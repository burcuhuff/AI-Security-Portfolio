from __future__ import annotations

"""
Data lineage tracking for the privacy audit system.

This module defines immutable data-artifact and lineage-event models and
persists artifact registrations, access events, and transformation events
as JSON Lines records.

The lineage log supports tracing data artifacts across privacy-preserving
transformations and linking lineage records to corresponding audit events.
"""
from dataclasses import dataclass, asdict
from types import MappingProxyType
from typing import Any
from datetime import datetime, timezone
import json


ENTRY_TYPE_ARTIFACT = "artifact"
ENTRY_TYPE_TRANSFORMATION = "transformation"
ENTRY_TYPE_ACCESS = "access"


@dataclass (frozen=True)
class DataArtifact:
    artifact_id: str
    name: str
    version: int
    record_count: int
    fields: tuple[str,...]
    checksum: str
    created_at: str

@dataclass (frozen=True)
class LineageEvent:
    event_id: str
    operation: str
    input_artifact_ids: tuple[str]
    output_artifact_id: str
    fields_read: tuple[str,...]
    fields_modified: tuple[str,...]
    fields_added: tuple[str,...]
    fields_removed: tuple[str,...]
    parameters: MappingProxyType[str, Any]
    audit_event_id: str | None
    timestamp: str

class LineageTracker:
    def __init__(self, log_path="audit_log.jsonl"):
        self.log_path = log_path
    
    def _read_entries(self) -> list[dict[str, Any]]:
        """Reads all structured records from the lineage JSONL file."""
        try:
            with open(self.log_path, "r", encoding="utf-8") as log_file:
                return [
                    json.loads(line)
                    for line in log_file
                    if line.strip()
                ]
        except FileNotFoundError:
            return []


    def _registered_artifact_ids(self) -> set[str]:
        """Returns all artifact IDs registered in the lineage log."""
        return {
            entry["artifact_id"]
            for entry in self._read_entries()
            if entry.get("entry_type") == ENTRY_TYPE_ARTIFACT
        }

    def log_lineage_event(self, event: LineageEvent) -> None:
        """Records a single immutable lineage transaction to disk.
        asdict unpacks immutable structures into JSON ready dictionaries
        instead of write function to JSON, manually unpacking fields
        due to python limitation in standard library interoperability
        while asdict() hits MappingProxyType, deepcopy() tries to duplicate it, 
        because a MappingProxyType is an engineered read-only wrapper directly linked to a hidden internal dictionary, 
        python's memory allocator forbids copying, resulting "TypeError: cannot pickle 'mappingproxy' object"
        cast MappingProxy directly into a raw dictionary for JSON serialization """
        event_dict = {
            "entry_type": ENTRY_TYPE_TRANSFORMATION,
            "event_id": event.event_id,
            "operation": event.operation,
            "input_artifact_ids": list(event.input_artifact_ids),
            "output_artifact_id": event.output_artifact_id,
            "fields_read": list(event.fields_read),
            "fields_modified": list(event.fields_modified),
            "fields_added": list(event.fields_added),
            "fields_removed": list(event.fields_removed),
            "parameters": dict(event.parameters), 
            "audit_event_id": event.audit_event_id,
            "timestamp": event.timestamp
        }
    
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(event_dict) + "\n")



    def log_access(
            self, 
            user_id: str, 
            action: str, 
            target_dataset: str
        ) -> dict [str,str]:
        """Records a single structured data-access event."""
        event = {
            "entry_type": ENTRY_TYPE_ACCESS,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "action": action,
            "target_dataset": target_dataset
        }
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(event) + "\n")

        return event
    
    def register_artifact(self, artifact: DataArtifact) -> None:
        """Registers a data asset version snapshot to the lineage logs.
        Unpack the dataclass into a dictionary **asdict(artifact) and add an entry_type for clarity in the log.
        This allows establishing the correct workflow and API, but it does not yet enforce that the artifact IDs are registered"""
        # DataArtifact types: strings, ints, standard tuples
        artifact_dict = {
            "entry_type": ENTRY_TYPE_ARTIFACT,
            **asdict(artifact)  
        }
        
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(artifact_dict) + "\n")
        
    def record_transformation(self, event: LineageEvent) -> None:
        """Validates and records a transformation between every registered artifacts referenced 
        by one transformation, both inputs and output, so they can all be validated against the registered artifacts
        A failed transformation validation does not leave a partial transformation record in the JSONL log."""

        registered_artifact_ids = self._registered_artifact_ids()

        # unpack every input ID into the set and add the output ID to the set
        # referenced_artifact_ids = set(event.input_artifact_ids)
        # referenced_artifact_ids.add(event.output_artifact_id)
        referenced_artifact_ids = {
            *event.input_artifact_ids,
            event.output_artifact_id,
        }

        # artifact IDs referenced by the transformation have not been registered
        missing_artifact_ids = (
            referenced_artifact_ids - registered_artifact_ids
        )

        if missing_artifact_ids:
            raise ValueError(
                "Transformation references unregistered artifact IDs: "
                f"{sorted(missing_artifact_ids)}"
            )

        self.log_lineage_event(event)

    
    def get_artifact_history(self, artifact_id: str) -> list:
        """Returns log entries directly involving an artifact in append order.
        Not Recursive, only returns the entries that directly reference the artifact ID.
        Read every lineage record -> is this the artifact itself? YES → include it
                                        OR
        Is this a transformation? -> does the artifact appear as input or output? YES → include it"""
        history = []

        for entry in self._read_entries():
            entry_type = entry.get("entry_type")

            if (
                entry_type == ENTRY_TYPE_ARTIFACT
                and entry.get("artifact_id") == artifact_id
            ):
                history.append(entry)

            elif entry_type == ENTRY_TYPE_TRANSFORMATION:
                is_output = (
                    entry.get("output_artifact_id") == artifact_id
                )

                is_input = (
                    artifact_id
                    in entry.get("input_artifact_ids", [])
                )

                if is_output or is_input:
                    history.append(entry)

        return history

    def get_upstream_lineage(self, artifact_id: str) -> list:
        """Return all ancestor artifacts, nearest ancestor first.
        current artifact → who produced me? → walk to inputs
        Recursive: find transformation that produced current artifact → find its inputs 
        → add those artifacts → repeat backward recursively
        """
        entries = self._read_entries()

        artifacts = {
            entry["artifact_id"]: entry
            for entry in entries
            if entry.get("entry_type") == ENTRY_TYPE_ARTIFACT
        }

        transformations = [
            entry
            for entry in entries
            if entry.get("entry_type") == ENTRY_TYPE_TRANSFORMATION
        ]

        upstream = []
        visited = set()

        def walk(current_artifact_id: str) -> None:
            if current_artifact_id in visited:
                return

            visited.add(current_artifact_id)

            for transformation in transformations:
                if (
                    transformation.get("output_artifact_id")
                    == current_artifact_id
                ):
                    for input_artifact_id in transformation.get(
                        "input_artifact_ids", []
                    ):
                        if input_artifact_id in visited:
                            continue

                        artifact = artifacts.get(input_artifact_id)

                        if artifact is not None:
                            upstream.append(artifact)

                        walk(input_artifact_id)

        walk(artifact_id)

        return upstream

    def get_downstream_lineage(self, artifact_id: str) -> list:
        """Return all descendant artifacts, nearest descendant first.
        current artifact → who consumed me? → walk to outputs
        """
        entries = self._read_entries()

        artifacts = {
            entry["artifact_id"]: entry
            for entry in entries
            if entry.get("entry_type") == ENTRY_TYPE_ARTIFACT
        }

        transformations = [
            entry
            for entry in entries
            if entry.get("entry_type") == ENTRY_TYPE_TRANSFORMATION
        ]

        downstream = []
        visited = set()

        def walk(current_artifact_id: str) -> None:
            if current_artifact_id in visited:
                return

            visited.add(current_artifact_id)

            for transformation in transformations:
                input_artifact_ids = transformation.get(
                    "input_artifact_ids", []
                )

                if current_artifact_id in input_artifact_ids:
                    output_artifact_id = transformation.get(
                        "output_artifact_id"
                    )

                    if output_artifact_id in visited:
                        continue

                    artifact = artifacts.get(output_artifact_id)

                    if artifact is not None:
                        downstream.append(artifact)

                    walk(output_artifact_id)

        walk(artifact_id)

        return downstream

    def verify_integrity(self) -> bool:
        pass

    def verify_integrity(self) -> bool:
        """Verify that the stored lineage graph is structurally valid.
        Integrity checks whether the lineage graph is trustworthy before we query or analyze it.
        1. All artifact IDs referenced in transformations must be registered.
        2. No duplicate artifact IDs or transformation event IDs.
        3. The lineage graph must be acyclic (no circular dependencies A->B->C->A)."""
        entries = self._read_entries()

        artifact_ids = set()
        event_ids = set()
        transformations = []

        # First pass: collect artifacts and transformations.
        for entry in entries:
            entry_type = entry.get("entry_type")

            if entry_type == ENTRY_TYPE_ARTIFACT:
                artifact_id = entry.get("artifact_id")

                if not artifact_id or artifact_id in artifact_ids:
                    return False

                artifact_ids.add(artifact_id)

            elif entry_type == ENTRY_TYPE_TRANSFORMATION:
                event_id = entry.get("event_id")

                if not event_id or event_id in event_ids:
                    return False

                event_ids.add(event_id)
                transformations.append(entry)

        # Second pass: validate artifact references.
        for transformation in transformations:
            input_artifact_ids = transformation.get(
                "input_artifact_ids", []
            )
            output_artifact_id = transformation.get(
                "output_artifact_id"
            )

            if output_artifact_id not in artifact_ids:
                return False

            for input_artifact_id in input_artifact_ids:
                if input_artifact_id not in artifact_ids:
                    return False

        # Build directed graph:
        # input artifact -> output artifact
        adjacency = {
            artifact_id: []
            for artifact_id in artifact_ids
        }

        for transformation in transformations:
            output_artifact_id = transformation[
                "output_artifact_id"
            ]

            for input_artifact_id in transformation.get(
                "input_artifact_ids", []
            ):
                adjacency[input_artifact_id].append(
                    output_artifact_id
                )

        # Cycle detection using DFS.
        # 0 = unseen
        # 1 = currently visiting
        # 2 = fully processed
        state = {
            artifact_id: 0
            for artifact_id in artifact_ids
        }

        def has_cycle(artifact_id: str) -> bool:
            if state[artifact_id] == 1:
                return True

            if state[artifact_id] == 2:
                return False

            state[artifact_id] = 1

            for downstream_id in adjacency[artifact_id]:
                if has_cycle(downstream_id):
                    return True

            state[artifact_id] = 2
            return False

        for artifact_id in artifact_ids:
            if state[artifact_id] == 0:
                if has_cycle(artifact_id):
                    return False

        return True

    def export_lineage(self) -> dict:
        pass
