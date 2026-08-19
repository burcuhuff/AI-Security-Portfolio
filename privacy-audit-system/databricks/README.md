# Databricks Lineage Practice

This folder explores a downstream Databricks analytics layer for the
platform-independent lineage events produced by the Privacy Audit System.

Current flow:

Python audit/lineage components
        ↓
append-only JSONL lineage events
        ↓
Databricks Bronze ingestion
        ↓
validated / normalized Silver events
        ↓
future lineage, integrity, and impact analytics

The application remains independent of Databricks. Databricks is used
as a downstream processing and analytics layer.


Current implementation:

- Bronze preserves heterogeneous lineage events and adds ingestion metadata.
- Silver normalizes timestamps and validates event types and required fields.
- Valid records are persisted to a managed Delta table.
- Invalid records are persisted separately with validation failure reasons.

Input records: 5
Silver records: 4
Quarantined records: 1

### Silver Event Types

| entry_type | records |
|---|---:|
| artifact | 2 |
| access | 1 |
| transformation | 1 |

### Quarantine Failures

| entry_type | event_id | timestamp | validation_error | source_file |
|---|---|---|---|---|
| transformation | NULL | not-a-date | missing_required_fields; invalid_timestamp | `dbfs:/Volumes/agent_nav_databricks/fde_practice/lineage_files/sample_lineage_with_invalid.jsonl` |