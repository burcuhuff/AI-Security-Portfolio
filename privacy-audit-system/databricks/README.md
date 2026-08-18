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