# test_audit_logger.py
from audit_logger import AuditLogger

logger = AuditLogger()

# Log a few operations
logger.log(
    operation="READ",
    dataset="raw",
    fields_accessed=["age", "gender", "department", "salary"],
    purpose="exploratory_analysis",
    actor="data_scientist",
    row_count=5000
)

logger.log(
    operation="GENERALIZE",
    dataset="raw",
    fields_accessed=["age"],
    purpose="k_anonymity_preparation",
    actor="privacy_pipeline",
    row_count=5000,
    additional_context={"method": "10_year_ranges"}
)

logger.log(
    operation="SUPPRESS",
    dataset="anonymized",
    fields_accessed=["age", "gender", "department"],
    purpose="k_anonymity_enforcement",
    actor="privacy_pipeline",
    row_count=26,
    additional_context={"k": 5, "reason": "group_size_below_k"}
)

# Verify integrity
logger.verify_integrity()

# Print report
import json
print(json.dumps(logger.get_access_report(), indent=2))