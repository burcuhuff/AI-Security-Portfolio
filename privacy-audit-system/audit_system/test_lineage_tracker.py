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

