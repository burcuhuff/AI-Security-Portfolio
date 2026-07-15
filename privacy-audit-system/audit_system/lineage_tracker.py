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
        """Validates and records a transformation between registered artifacts.
        A failed transformation validation does not leave a partial transformation record in the JSONL log."""
        registered_artifact_ids = self._registered_artifact_ids()

        referenced_artifact_ids = {
            *event.input_artifact_ids,
            event.output_artifact_id,
        }

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
        pass

    def get_upstream_lineage(self, artifact_id: str) -> list:
        pass

    def get_downstream_lineage(self, artifact_id: str) -> list:
        pass

    def verify_integrity(self) -> bool:
        pass

    def export_lineage(self) -> dict:
        pass
