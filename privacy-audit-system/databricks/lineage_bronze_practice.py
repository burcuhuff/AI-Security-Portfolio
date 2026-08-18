from pyspark.sql import functions as F

SOURCE_PATH = (
    "/Volumes/agent_nav_databricks/"
    "fde_practice/lineage_files/sample_lineage.jsonl"
)

lineage_raw = spark.read.json(SOURCE_PATH)

lineage_bronze = (
    lineage_raw
    .withColumn("ingested_at", F.current_timestamp())
    .withColumn("source_file", F.expr("_metadata.file_path"))
)

entry_type_summary = (
    lineage_bronze
    .groupBy("entry_type")
    .agg(
        F.count("*").alias("records")
    )
    .orderBy(F.desc("records"))
)

print("Bronze row count:", lineage_bronze.count())
entry_type_summary.show()