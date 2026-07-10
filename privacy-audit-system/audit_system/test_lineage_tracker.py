import os
import json
import pytest
from faker import Faker
from types import MappingProxyType
from lineage_tracker import LineageTracker, DataArtifact, LineageEvent

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

def test_log_creation_on_data_access():
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
        timestamp=fake.iso8601()
    )

    #  log the lineage event
    tracker.log_lineage_event(event)

    # assert that the log file was created and contains the expected data
    assert os.path.exists(TEST_LOG_PATH), "Lineage file was not created."
    
    with open(TEST_LOG_PATH, "r") as f:
        log_lines = f.readlines()
        
    assert len(log_lines) == 1
    
    logged_data = json.loads(log_lines[0])
    assert logged_data["event_id"] == mock_event_id
    assert logged_data["operation"] == "ANONYMIZATION_RUN"
    assert logged_data["fields_read"] == ["age", "zip_code", "salary"]
    # MappingProxyType serializes natively into standard JSON dicts
    assert logged_data["parameters"]["privacy_budget_epsilon"] == 0.1
