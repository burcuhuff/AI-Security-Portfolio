# TEST RESULTS

- 5,000 input records
- 26 suppressed records
- 4,974 output records

> employee_id appears in fields_removed 

> employee_id is absent from the output artifact


```
(venv) burcu@Burcus-MacBook-Pro audit_system % pytest -s -vv test_lineage_tracker.py
============================= test session starts =============================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- /Users/burcu/github/ai-security-portfolio/privacy-audit-system/venv/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/burcu/github/ai-security-portfolio/privacy-audit-system/audit_system
plugins: Faker-40.28.1
collected 5 items                                                             

test_lineage_tracker.py::test_register_artifact_stores_metadata 
--- REGISTERED ARTIFACT ---
Entry 1:
{
  "entry_type": "artifact",
  "artifact_id": "8120bd5f-13a8-41c9-ad6b-d1a71e041a5c",
  "name": "hr_dataset.csv",
  "version": 1,
  "record_count": 5000,
  "fields": [
    "employee_id",
    "age",
    "gender",
    "zip_code",
    "salary"
  ],
  "checksum": "f1f8745a1feff8d238604ad272806033f15a9e50d0cd5d354ad1f6ad98e99518",
  "created_at": "2026-07-14T22:00:56.426796+00:00"
}
---------------------------
PASSED
test_lineage_tracker.py::test_log_access_writes_access_entry 
--- ACCESS EVENT ---
Entry 1:
{
  "entry_type": "access",
  "timestamp": "2026-07-14T22:00:56.428791+00:00",
  "user_id": "privacy_analyst_01",
  "action": "READ",
  "target_dataset": "hr_dataset.csv"
}
--------------------
PASSED
test_lineage_tracker.py::test_log_lineage_event_writes_transformation_entry 
--- TRANSFORMATION EVENT ---
Entry 1:
{
  "entry_type": "transformation",
  "event_id": "2d6e9f9b-eb3c-4288-8181-e904c54b542f",
  "operation": "ANONYMIZATION_RUN",
  "input_artifact_ids": [
    "a2848f66-fe3e-4b60-942c-4304f1424267"
  ],
  "output_artifact_id": "1857b692-90f5-45da-8e20-c1c568a44cb7",
  "fields_read": [
    "age",
    "zip_code",
    "salary"
  ],
  "fields_modified": [
    "zip_code",
    "salary"
  ],
  "fields_added": [],
  "fields_removed": [
    "employee_id"
  ],
  "parameters": {
    "privacy_budget_epsilon": 0.1
  },
  "audit_event_id": "980309d2-dc2a-4171-96c7-f50510de4748",
  "timestamp": "2026-07-14T22:00:56.430092+00:00"
}
----------------------------
PASSED
test_lineage_tracker.py::test_record_transformation_links_registered_artifacts 
--- VALIDATED ARTIFACT TRANSFORMATION ---
Entry 1:
{
  "entry_type": "artifact",
  "artifact_id": "8fe9dd59-5ccf-42a6-b9e8-f55230b00830",
  "name": "raw_hr_dataset.csv",
  "version": 1,
  "record_count": 5000,
  "fields": [
    "employee_id",
    "age",
    "gender",
    "zip_code",
    "salary"
  ],
  "checksum": "4906b939bb000d94ba5ab6c6d5de4ed98d4aab3044376755f4859a14c34bab58",
  "created_at": "2026-07-14T22:00:56.431610+00:00"
}
Entry 2:
{
  "entry_type": "artifact",
  "artifact_id": "9d790383-e181-45ac-a58e-8e8df27d3ebe",
  "name": "anonymized_hr_dataset.csv",
  "version": 2,
  "record_count": 4974,
  "fields": [
    "age",
    "gender",
    "zip_code",
    "salary"
  ],
  "checksum": "7ffadbe20be7235b5d12cb2b16aa84ef9887343769aafda640656136940df230",
  "created_at": "2026-07-14T22:00:56.431610+00:00"
}
Entry 3:
{
  "entry_type": "transformation",
  "event_id": "952a31be-2a21-4768-a20c-91674d003128",
  "operation": "ANONYMIZATION_RUN",
  "input_artifact_ids": [
    "8fe9dd59-5ccf-42a6-b9e8-f55230b00830"
  ],
  "output_artifact_id": "9d790383-e181-45ac-a58e-8e8df27d3ebe",
  "fields_read": [
    "employee_id",
    "age",
    "gender",
    "zip_code",
    "salary"
  ],
  "fields_modified": [
    "age",
    "zip_code",
    "salary"
  ],
  "fields_added": [],
  "fields_removed": [
    "employee_id"
  ],
  "parameters": {
    "k": 5,
    "age_range": 10,
    "suppressed_records": 26
  },
  "audit_event_id": "22e569fd-df94-4bd1-bbbc-4220ac767044",
  "timestamp": "2026-07-14T22:00:56.432056+00:00"
}
-----------------------------------------
PASSED
test_lineage_tracker.py::test_record_transformation_rejects_unregistered_input_artifact PASSED

============================== 5 passed in 0.13s ==============================
(venv) burcu@Burcus-MacBook-Pro audit_system % 
```