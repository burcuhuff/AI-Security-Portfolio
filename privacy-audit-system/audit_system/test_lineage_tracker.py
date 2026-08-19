from lineage_tracker import DataArtifact
from datetime import datetime, timezone as datetime_timezone
import os
import json
from time import timezone
import pytest
import re
from faker import Faker
from types import MappingProxyType
from lineage_tracker import LineageTracker, DataArtifact, LineageEvent

"""
Tests:
    1. Register the data artifact
    2. Record access to the artifact
    3. Record a transformation involving artifacts

Each Test:
    1. Call the method under test
    2. Assert that the log file exists
    3. Print the JSONL readout
    4. Parse the file
    5. Perform detailed assertions
"""

fake = Faker()
TEST_LOG_PATH = "test_audit_log.jsonl"

@pytest.fixture(autouse=True)
def cleanup_logs():
    """Ensure a clean log file for every isolated test run."""
    if os.path.exists(TEST_LOG_PATH):
        os.remove(TEST_LOG_PATH)
    yield
    if os.path.exists(TEST_LOG_PATH):
        os.remove(TEST_LOG_PATH)

def print_jsonl_log(log_path: str, label: str) -> None:
    """Pretty print JSON objects currently stored in a JSONL file."""
    print(f"\n--- {label} ---")

    with open(log_path, "r", encoding="utf-8") as log_file:
        for line_number, line in enumerate(log_file, start=1):
            entry = json.loads(line)

            print(f"Entry {line_number}:")
            print(json.dumps(entry, indent=2))

    print("-" * (len(label) + 8))

def test_register_artifact_stores_metadata():
    """Verify that registering a data asset version correctly writes its metadata to the log."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)
    
    # build a mock snapshot of a dataset version
    mock_artifact_id = fake.uuid4()
    mock_name = "hr_dataset.csv"
    
    artifact = DataArtifact(
        artifact_id=mock_artifact_id,
        name=mock_name,
        version=1,
        record_count=5000,
        fields=("employee_id", "age", "gender", "zip_code", "salary"),
        checksum=fake.sha256(),
        created_at=datetime.now(datetime_timezone.utc).isoformat()
    )

    # run registration method
    tracker.register_artifact(artifact)

    # confirm the log entry captures the structural metadata
    assert os.path.exists(TEST_LOG_PATH), "Artifact registration file was not created."
    with open(TEST_LOG_PATH, "r") as f:
        log_lines = f.readlines()

    # Display the persisted JSON structure.
    print_jsonl_log(
        TEST_LOG_PATH,
        "REGISTERED ARTIFACT",
    ) 

    assert len(log_lines) == 1
    logged_data = json.loads(log_lines[0])
    
    assert logged_data["artifact_id"] == mock_artifact_id
    assert logged_data["name"] == mock_name
    assert logged_data["record_count"] == 5000
    assert logged_data["fields"] == ["employee_id", "age", "gender", "zip_code", "salary"]
    assert logged_data["entry_type"] == "artifact"
    


def test_log_access_writes_access_entry():
    """Verify that a data-access event is written with the correct record type."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    returned_event = tracker.log_access(
        user_id="privacy_analyst_01",
        action="READ",
        target_dataset="hr_dataset.csv",
    )

    assert os.path.exists(TEST_LOG_PATH), "Lineage log file was not created."

    # Display the persisted JSON structure.
    print_jsonl_log(
        TEST_LOG_PATH,
        "ACCESS EVENT",
    ) 
    with open(TEST_LOG_PATH, "r", encoding="utf-8") as log_file:
        log_lines = log_file.readlines()

    assert len(log_lines) == 1

    logged_data = json.loads(log_lines[0])

    assert logged_data["entry_type"] == "access"
    assert logged_data["user_id"] == "privacy_analyst_01"
    assert logged_data["action"] == "READ"
    assert logged_data["target_dataset"] == "hr_dataset.csv"

    # Confirm the method returns the same event that was persisted.
    assert logged_data == returned_event

    # Confirm the timestamp is valid ISO 8601 and timezone-aware.
    parsed_timestamp = datetime.fromisoformat(logged_data["timestamp"])
    assert parsed_timestamp.tzinfo is not None

def test_log_lineage_event_writes_transformation_entry():
    """Verify that logging a lineage event correctly writes a structured JSONL entry."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)
    
    # create mock data for the lineage event
    mock_event_id = fake.uuid4()
    mock_input_id = fake.uuid4()
    
    # immutable parameters for the lineage event
    params = MappingProxyType({"privacy_budget_epsilon": 0.1})
    
    # instantiate a LineageEvent with the mock data
    event = LineageEvent(
        event_id=mock_event_id,
        operation="ANONYMIZATION_RUN",
        input_artifact_ids=(mock_input_id,),
        output_artifact_id=fake.uuid4(),
        fields_read=("age", "zip_code", "salary"),
        fields_modified=("zip_code", "salary"),
        fields_added=(),
        fields_removed=("employee_id",),
        parameters=params,
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat()
    )

    #  log the lineage event
    tracker.log_lineage_event(event)

    # assert that the log file was created and contains the expected data
    assert os.path.exists(TEST_LOG_PATH), "Lineage file was not created."
    
    # Display the persisted JSON structure.
    print_jsonl_log(
        TEST_LOG_PATH,
        "TRANSFORMATION EVENT",
    ) 

    with open(TEST_LOG_PATH, "r") as f:
        log_lines = f.readlines()
        
    assert len(log_lines) == 1
    
    logged_data = json.loads(log_lines[0])

    assert logged_data["event_id"] == mock_event_id
    assert logged_data["operation"] == "ANONYMIZATION_RUN"
    assert logged_data["fields_read"] == ["age", "zip_code", "salary"]
    # MappingProxyType serializes natively into standard JSON dicts
    assert logged_data["parameters"]["privacy_budget_epsilon"] == 0.1
    # Assert: Instead of checking a fake match, verify it is a valid ISO timestamp format
    assert "timestamp" in logged_data
    iso_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    assert re.match(iso_regex, logged_data["timestamp"]), "Timestamp is not in valid ISO 8601 format"
    assert logged_data["entry_type"] == "transformation"

"""
Milestone II: Validated Artifact Relationships
    1. Register input and output artifacts
    2. Rejects unregistered artifacts
    3. Assert that the transformation entry correctly references the registered artifacts
"""

def test_record_transformation_links_registered_artifacts():
    """Verify that a transformation links registered input and output artifacts."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    created_at = datetime.now(datetime_timezone.utc).isoformat()

    input_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="raw_hr_dataset.csv",
        version=1,
        record_count=5000,
        fields=(
            "employee_id",
            "age",
            "gender",
            "zip_code",
            "salary",
        ),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    output_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="anonymized_hr_dataset.csv",
        version=2,
        record_count=4974,
        fields=(
            "age",
            "gender",
            "zip_code",
            "salary",
        ),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    tracker.register_artifact(input_artifact)
    tracker.register_artifact(output_artifact)

    event = LineageEvent(
        event_id=fake.uuid4(),
        operation="ANONYMIZATION_RUN",
        input_artifact_ids=(input_artifact.artifact_id,),
        output_artifact_id=output_artifact.artifact_id,
        fields_read=(
            "employee_id",
            "age",
            "gender",
            "zip_code",
            "salary",
        ),
        fields_modified=(
            "age",
            "zip_code",
            "salary",
        ),
        fields_added=(),
        fields_removed=("employee_id",),
        parameters=MappingProxyType(
            {
                "k": 5,
                "age_range": 10,
                "suppressed_records": 26,
            }
        ),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    tracker.record_transformation(event)

    assert os.path.exists(
        TEST_LOG_PATH
    ), "Lineage log file was not created."

    print_jsonl_log(
        TEST_LOG_PATH,
        "VALIDATED ARTIFACT TRANSFORMATION",
    )

    with open(TEST_LOG_PATH, "r", encoding="utf-8") as log_file:
        entries = [
            json.loads(line)
            for line in log_file
            if line.strip()
        ]

    assert len(entries) == 3

    assert [entry["entry_type"] for entry in entries] == [
        "artifact",
        "artifact",
        "transformation",
    ]

    transformation_entry = entries[-1]

    assert transformation_entry["event_id"] == event.event_id
    assert transformation_entry["operation"] == "ANONYMIZATION_RUN"
    assert transformation_entry["input_artifact_ids"] == [
        input_artifact.artifact_id
    ]
    assert (
        transformation_entry["output_artifact_id"]
        == output_artifact.artifact_id
    )
    assert transformation_entry["parameters"]["k"] == 5
    assert transformation_entry["parameters"]["suppressed_records"] == 26

def test_record_transformation_rejects_unregistered_input_artifact():
    """Verify that a transformation cannot reference an unknown input artifact."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    output_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="anonymized_hr_dataset.csv",
        version=2,
        record_count=4974,
        fields=(
            "age",
            "gender",
            "zip_code",
            "salary",
        ),
        checksum=fake.sha256(),
        created_at=datetime.now(datetime_timezone.utc).isoformat(),
    )

    # Register only the output artifact.
    tracker.register_artifact(output_artifact)

    unknown_input_id = fake.uuid4()

    event = LineageEvent(
        event_id=fake.uuid4(),
        operation="ANONYMIZATION_RUN",
        input_artifact_ids=(unknown_input_id,),
        output_artifact_id=output_artifact.artifact_id,
        fields_read=("age", "zip_code", "salary"),
        fields_modified=("age", "zip_code", "salary"),
        fields_added=(),
        fields_removed=(),
        parameters=MappingProxyType(
            {
                "k": 5,
                "age_range": 10,
            }
        ),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    with pytest.raises(
        ValueError,
        match="unregistered artifact",
    ):
        tracker.record_transformation(event)

    # The rejected transformation must not be written.
    with open(TEST_LOG_PATH, "r", encoding="utf-8") as log_file:
        entries = [
            json.loads(line)
            for line in log_file
            if line.strip()
        ]

    assert len(entries) == 1
    assert entries[0]["entry_type"] == "artifact"

"""
Milestone III: Lineage Queries
    1. Get direct history for an artifact
    2. Get upstream lineage
    3. Get downstream lineage
    4. Verify integrity of the lineage graph Happy Path
"""

def test_get_artifact_history_returns_directly_related_entries():
    """Verify that artifact history returns the artifact and transformations directly involving it."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    created_at = datetime.now(datetime_timezone.utc).isoformat()

    input_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="raw_hr_dataset.csv",
        version=1,
        record_count=5000,
        fields=(
            "employee_id",
            "age",
            "gender",
            "zip_code",
            "salary",
        ),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    output_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="anonymized_hr_dataset.csv",
        version=2,
        record_count=4974,
        fields=(
            "age",
            "gender",
            "zip_code",
            "salary",
        ),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    tracker.register_artifact(input_artifact)
    tracker.register_artifact(output_artifact)

    event = LineageEvent(
        event_id=fake.uuid4(),
        operation="ANONYMIZATION_RUN",
        input_artifact_ids=(input_artifact.artifact_id,),
        output_artifact_id=output_artifact.artifact_id,
        fields_read=(
            "employee_id",
            "age",
            "gender",
            "zip_code",
            "salary",
        ),
        fields_modified=(
            "age",
            "zip_code",
            "salary",
        ),
        fields_added=(),
        fields_removed=("employee_id",),
        parameters=MappingProxyType({"k": 5}),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    tracker.record_transformation(event)

    history = tracker.get_artifact_history(
        output_artifact.artifact_id
    )

    assert len(history) == 2

    assert [entry["entry_type"] for entry in history] == [
        "artifact",
        "transformation",
    ]

    assert history[0]["artifact_id"] == output_artifact.artifact_id
    assert (
        history[1]["output_artifact_id"]
        == output_artifact.artifact_id
    )

def test_get_artifact_history_includes_transformation_where_artifact_is_input():
        """Verify that history includes transformations that consume the artifact."""
        tracker = LineageTracker(log_path=TEST_LOG_PATH)

        created_at = datetime.now(datetime_timezone.utc).isoformat()

        input_artifact = DataArtifact(
            artifact_id=fake.uuid4(),
            name="raw_hr_dataset.csv",
            version=1,
            record_count=5000,
            fields=("employee_id", "age", "salary"),
            checksum=fake.sha256(),
            created_at=created_at,
        )

        output_artifact = DataArtifact(
            artifact_id=fake.uuid4(),
            name="anonymized_hr_dataset.csv",
            version=2,
            record_count=4974,
            fields=("age", "salary"),
            checksum=fake.sha256(),
            created_at=created_at,
        )

        tracker.register_artifact(input_artifact)
        tracker.register_artifact(output_artifact)

        event = LineageEvent(
            event_id=fake.uuid4(),
            operation="ANONYMIZATION_RUN",
            input_artifact_ids=(input_artifact.artifact_id,),
            output_artifact_id=output_artifact.artifact_id,
            fields_read=("employee_id", "age", "salary"),
            fields_modified=("age", "salary"),
            fields_added=(),
            fields_removed=("employee_id",),
            parameters=MappingProxyType({"k": 5}),
            audit_event_id=fake.uuid4(),
            timestamp=datetime.now(datetime_timezone.utc).isoformat(),
        )

        tracker.record_transformation(event)

        history = tracker.get_artifact_history(
            input_artifact.artifact_id
        )

        assert len(history) == 2

        assert [entry["entry_type"] for entry in history] == [
            "artifact",
            "transformation",
        ]

        assert history[0]["artifact_id"] == input_artifact.artifact_id
        assert (
            input_artifact.artifact_id
            in history[1]["input_artifact_ids"]
)

def test_get_upstream_lineage_returns_recursive_ancestor_artifacts():
    """Verify that upstream lineage recursively returns ancestor artifacts."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    created_at = datetime.now(datetime_timezone.utc).isoformat()

    raw_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="raw_hr_dataset.csv",
        version=1,
        record_count=5000,
        fields=("employee_id", "age", "salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    anonymized_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="anonymized_hr_dataset.csv",
        version=2,
        record_count=4974,
        fields=("age", "salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    aggregated_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="aggregated_hr_dataset.csv",
        version=3,
        record_count=100,
        fields=("age_group", "avg_salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    tracker.register_artifact(raw_artifact)
    tracker.register_artifact(anonymized_artifact)
    tracker.register_artifact(aggregated_artifact)

    anonymization_event = LineageEvent(
        event_id=fake.uuid4(),
        operation="ANONYMIZATION_RUN",
        input_artifact_ids=(raw_artifact.artifact_id,),
        output_artifact_id=anonymized_artifact.artifact_id,
        fields_read=("employee_id", "age", "salary"),
        fields_modified=("age", "salary"),
        fields_added=(),
        fields_removed=("employee_id",),
        parameters=MappingProxyType({"k": 5}),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    aggregation_event = LineageEvent(
        event_id=fake.uuid4(),
        operation="AGGREGATION",
        input_artifact_ids=(anonymized_artifact.artifact_id,),
        output_artifact_id=aggregated_artifact.artifact_id,
        fields_read=("age", "salary"),
        fields_modified=(),
        fields_added=("age_group", "avg_salary"),
        fields_removed=("age", "salary"),
        parameters=MappingProxyType({"group_by": "age_group"}),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    tracker.record_transformation(anonymization_event)
    tracker.record_transformation(aggregation_event)

    upstream = tracker.get_upstream_lineage(
        aggregated_artifact.artifact_id
    )

    assert len(upstream) == 2

    assert [artifact["artifact_id"] for artifact in upstream] == [
        anonymized_artifact.artifact_id,
        raw_artifact.artifact_id,
    ]

def test_get_downstream_lineage_returns_recursive_descendant_artifacts():
    """Verify that downstream lineage recursively returns descendant artifacts."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    created_at = datetime.now(datetime_timezone.utc).isoformat()

    raw_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="raw_hr_dataset.csv",
        version=1,
        record_count=5000,
        fields=("employee_id", "age", "salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    anonymized_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="anonymized_hr_dataset.csv",
        version=2,
        record_count=4974,
        fields=("age", "salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    aggregated_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="aggregated_hr_dataset.csv",
        version=3,
        record_count=100,
        fields=("age_group", "avg_salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    tracker.register_artifact(raw_artifact)
    tracker.register_artifact(anonymized_artifact)
    tracker.register_artifact(aggregated_artifact)

    anonymization_event = LineageEvent(
        event_id=fake.uuid4(),
        operation="ANONYMIZATION_RUN",
        input_artifact_ids=(raw_artifact.artifact_id,),
        output_artifact_id=anonymized_artifact.artifact_id,
        fields_read=("employee_id", "age", "salary"),
        fields_modified=("age", "salary"),
        fields_added=(),
        fields_removed=("employee_id",),
        parameters=MappingProxyType({"k": 5}),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    aggregation_event = LineageEvent(
        event_id=fake.uuid4(),
        operation="AGGREGATION",
        input_artifact_ids=(anonymized_artifact.artifact_id,),
        output_artifact_id=aggregated_artifact.artifact_id,
        fields_read=("age", "salary"),
        fields_modified=(),
        fields_added=("age_group", "avg_salary"),
        fields_removed=("age", "salary"),
        parameters=MappingProxyType({"group_by": "age_group"}),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    tracker.record_transformation(anonymization_event)
    tracker.record_transformation(aggregation_event)

    downstream = tracker.get_downstream_lineage(
        raw_artifact.artifact_id
    )

    assert len(downstream) == 2

    assert [artifact["artifact_id"] for artifact in downstream] == [
        anonymized_artifact.artifact_id,
        aggregated_artifact.artifact_id,
    ]

def test_verify_integrity_returns_true_for_valid_lineage():
    """Verify that a valid lineage graph passes integrity validation.
    This is a ** HAPPY PATH ** proving valid lieage returns True"""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    created_at = datetime.now(datetime_timezone.utc).isoformat()

    raw_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="raw_hr_dataset.csv",
        version=1,
        record_count=5000,
        fields=("employee_id", "age", "salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    anonymized_artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="anonymized_hr_dataset.csv",
        version=2,
        record_count=4974,
        fields=("age", "salary"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    tracker.register_artifact(raw_artifact)
    tracker.register_artifact(anonymized_artifact)

    event = LineageEvent(
        event_id=fake.uuid4(),
        operation="ANONYMIZATION_RUN",
        input_artifact_ids=(raw_artifact.artifact_id,),
        output_artifact_id=anonymized_artifact.artifact_id,
        fields_read=("employee_id", "age", "salary"),
        fields_modified=("age", "salary"),
        fields_added=(),
        fields_removed=("employee_id",),
        parameters=MappingProxyType({"k": 5}),
        audit_event_id=fake.uuid4(),
        timestamp=datetime.now(datetime_timezone.utc).isoformat(),
    )

    tracker.record_transformation(event)

    assert tracker.verify_integrity() is True


"""
Milestone IV: Lineage Integrity
    1. Valid lineage passes integrity validation
    2. Unknown artifact references fail integrity validation
    3. Cycles fail integrity validation
"""

def test_verify_integrity_returns_false_for_unknown_artifact_reference():
    """Verify that lineage referencing an unknown artifact fails integrity validation."""
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    artifact = DataArtifact(
        artifact_id=fake.uuid4(),
        name="raw_hr_dataset.csv",
        version=1,
        record_count=5000,
        fields=("employee_id", "age", "salary"),
        checksum=fake.sha256(),
        created_at=datetime.now(datetime_timezone.utc).isoformat(),
    )

    tracker.register_artifact(artifact)

    corrupted_transformation = {
        "entry_type": "transformation",
        "event_id": fake.uuid4(),
        "operation": "ANONYMIZATION_RUN",
        "input_artifact_ids": [artifact.artifact_id],
        "output_artifact_id": fake.uuid4(),  # never registered
    }

    # Bypass record_transformation() deliberately to simulate
    # malformed or externally corrupted persisted lineage.
    with open(TEST_LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(
            json.dumps(corrupted_transformation) + "\n"
        )

    assert tracker.verify_integrity() is False

def test_verify_integrity_returns_false_for_cycle():
    """Verify that cyclic lineage fails integrity validation.
    A->B->A
    """
    tracker = LineageTracker(log_path=TEST_LOG_PATH)

    created_at = datetime.now(datetime_timezone.utc).isoformat()

    artifact_a = DataArtifact(
        artifact_id=fake.uuid4(),
        name="artifact_a.csv",
        version=1,
        record_count=100,
        fields=("id", "value"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    artifact_b = DataArtifact(
        artifact_id=fake.uuid4(),
        name="artifact_b.csv",
        version=1,
        record_count=100,
        fields=("id", "value"),
        checksum=fake.sha256(),
        created_at=created_at,
    )

    tracker.register_artifact(artifact_a)
    tracker.register_artifact(artifact_b)

    transformation_a_to_b = {
        "entry_type": "transformation",
        "event_id": fake.uuid4(),
        "operation": "STEP_A_TO_B",
        "input_artifact_ids": [artifact_a.artifact_id],
        "output_artifact_id": artifact_b.artifact_id,
    }

    transformation_b_to_a = {
        "entry_type": "transformation",
        "event_id": fake.uuid4(),
        "operation": "STEP_B_TO_A",
        "input_artifact_ids": [artifact_b.artifact_id],
        "output_artifact_id": artifact_a.artifact_id,
    }

    # Write directly to simulate corrupted persisted lineage.
    with open(TEST_LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(
            json.dumps(transformation_a_to_b) + "\n"
        )
        log_file.write(
            json.dumps(transformation_b_to_a) + "\n"
        )

    assert tracker.verify_integrity() is False