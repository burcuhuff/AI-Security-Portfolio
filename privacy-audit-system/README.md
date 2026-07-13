# Audit Logging and Data Lineage System

The audit logging and data lineage system records structured metadata about
data access and transformation activity in the HR privacy pipeline.

Audit events capture:

- who accessed the data
- what operation was performed
- which dataset or fields were involved
- the stated purpose of the operation
- when the operation occurred

Lineage events capture how data artifacts change across privacy-preserving
operations. Together, these records are designed to answer questions such as:

> Which source artifact produced this anonymized dataset, what transformations
> were applied, and which audit event was associated with the operation?

## Lineage Tracker

The lineage tracker explains how a dataset or field reached its current state.

It records:

- input data artifacts
- output data artifacts
- the transformation performed
- fields that were read, modified, added, or removed
- transformation parameters
- artifact metadata, including version, record count, and checksum
- parent-child relationships between artifacts
- timestamps
- the related audit event ID from `audit_logger.py`

### Record Types

Each JSONL record includes an `entry_type` discriminator so that artifact,
access, and transformation records can be identified reliably.

```python
ENTRY_TYPE_ARTIFACT = "artifact"
ENTRY_TYPE_TRANSFORMATION = "transformation"
ENTRY_TYPE_ACCESS = "access"