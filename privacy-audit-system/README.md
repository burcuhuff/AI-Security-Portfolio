# Audit Logging and Data Lineage System

Every time data is accessed, transformed, or queried in the HR pipeline, the system automatically records:
-  who accessed it, 
- what operation was performed, 
- what data was touched, 
- why (purpose), 
- and when

It also tracks the lineage of every transformation, so we can answer "where did this anonymized record come from and what happened to it?"

## Lineage Tracker

Explains how a dataset or field reached to its current state.

It tracks: 
- the input dataset or artifact
- the transformation performed
- the output dataset or artifact
- which fields were read, modified, added, or removed
- the parent–child relationship between transformations
- basic metadata such as timestamp, record count, and parameters
- the related audit-event ID from audit_logger.py

Tracking is done seperately on artifacts and transformation events. This is because one artifact may pass through several operations, and one operation may eventually have multiple inputs.

