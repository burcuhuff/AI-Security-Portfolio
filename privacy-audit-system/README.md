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

The current implementation provides artifact-level lineage. A `DataArtifact`<br>
represents an immutable, versioned snapshot of a dataset, while a<br>
`LineageEvent` records the transformation connecting one or more input<br>
artifacts to an output artifact.


### Record Types

Each JSONL record includes an `entry_type` discriminator so that artifact,
access, and transformation records can be identified reliably.

```python
ENTRY_TYPE_ARTIFACT = "artifact"
ENTRY_TYPE_TRANSFORMATION = "transformation"
ENTRY_TYPE_ACCESS = "access"
```
This design supports dataset-level provenance, transformation history, field
impact tracking, and audit-event linkage. It does not currently retain
row-level mappings between original and anonymized records or continuously
observe operations performed outside the instrumented pipeline.

## Lineage Graph

| Concept        | Meaning                                                 |
| -------------- | ------------------------------------------------------- |
| `DataArtifact` | A versioned state or snapshot of data                   |
| `LineageEvent` | The transformation relationship between artifact states |

```
Artifact A: raw HR data
        |
        | GENERALIZE age
        v
Artifact B: generalized HR data
        |
        | SUPPRESS groups smaller than k=5
        v
Artifact C: k-anonymous HR data
```
- The rtifacts are nodes

- The transformation events are the edges

- Therefore the LineageEvent identified in the project doesn't represent the data itseld. It represents the operation that caused one artifact state to become another.

```pyton
LineageEvent(
    operation="GENERALIZE",
    input_artifact_ids=("artifact-a",),
    output_artifact_id="artifact-b",
    fields_read=("age",),
    fields_modified=("age",),
    parameters=MappingProxyType({
        "age_range": 10,
    }),
)
```


- Artifact lets us distinguish between different states of a dataset and verify that a particular transformation used the expected version:
```
version
record_count
fields
checksum
created_at
``` 

```
artifact
{
  "entry_type": "artifact",
  "artifact_id": "de0d77d3-2620-4810-b1a1-49d6d65ce58a",
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
  "checksum": "7bbcbff5802cab6e7055e6a47d23e779b70b0fbb5bfabebf68177931953c13fe",
  "created_at": "2026-07-13T19:32:57.543387+00:00"
}
```

Milestone 1 — Typed JSONL records

-> artifact
-> access
-> transformation

Milestone 2 — Validated transformation relationships towards graph compatibility
```
register_artifact()
        ↓
artifact IDs become valid lineage nodes
        ↓
record_transformation()
        ↓
validate all references
        ↓
log_lineage_event()
        ↓
persist the relationship as JSONL
```

Milestone 3 — Lineage queries
- get_artifact_history()
- get_upstream_lineage()
- get_downstream_lineage()

Milestone 4 — Integrity validation
- unknown references
- duplicate identifiers
- malformed records
- cycles
- orphan artifacts, where relevant

Milestone 5 — Export and visualization
- export_lineage()
- nodes-and-relationships JSON
- optional Mermaid or Graphviz visualization
