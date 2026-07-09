# Audit Logging and Data Lineage System

Every time data is accessed, transformed, or queried in the HR pipeline, the system automatically records:
-  who accessed it, 
- what operation was performed, 
- what data was touched, 
- why (purpose), 
- and when. 

It also tracks the lineage of every transformation, so we can answer "where did this anonymized record come from and what happened to it?"