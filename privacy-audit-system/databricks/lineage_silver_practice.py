from pyspark.sql import functions as F


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

# Update for the Databricks environment/source being processed.
SOURCE_PATH = (
    "/Volumes/agent_nav_databricks/"
    "fde_practice/lineage_files/sample_lineage_with_invalid.jsonl"
)

SILVER_TABLE = (
    "agent_nav_databricks."
    "fde_practice."
    "lineage_silver"
)

QUARANTINE_TABLE = (
    "agent_nav_databricks."
    "fde_practice."
    "lineage_quarantine"
)

ALLOWED_ENTRY_TYPES = [
    "artifact",
    "transformation",
    "access",
]


# -------------------------------------------------------------------
# Raw / Bronze representation
# -------------------------------------------------------------------

lineage_raw = spark.read.json(SOURCE_PATH)

lineage_bronze = (
    lineage_raw
    .withColumn(
        "ingested_at",
        F.current_timestamp()
    )
    .withColumn(
        "source_file",
        F.expr("_metadata.file_path")
    )
)


# -------------------------------------------------------------------
# Silver validation and normalization
# -------------------------------------------------------------------

lineage_silver_staged = (
    lineage_bronze

    # Normalize source timestamps into one typed column.
    .withColumn(
        "event_timestamp",
        F.coalesce(
            F.try_to_timestamp(F.col("timestamp")),
            F.try_to_timestamp(F.col("created_at")),
        )
    )

    # Validate event type.
    .withColumn(
        "is_valid_entry_type",
        F.coalesce(
            F.col("entry_type").isin(ALLOWED_ENTRY_TYPES),
            F.lit(False),
        )
    )

    # Validate fields required by each event type.
    .withColumn(
        "has_required_fields",
        F.coalesce(
            F.when(
                F.col("entry_type") == "artifact",
                F.col("artifact_id").isNotNull()
            )
            .when(
                F.col("entry_type") == "transformation",
                (
                    F.col("event_id").isNotNull()
                    & F.col("operation").isNotNull()
                    & F.col("output_artifact_id").isNotNull()
                    & (
                        F.size(
                            F.col("input_artifact_ids")
                        ) > 0
                    )
                )
            )
            .when(
                F.col("entry_type") == "access",
                (
                    F.col("user_id").isNotNull()
                    & F.col("action").isNotNull()
                    & F.col("target_dataset").isNotNull()
                )
            )
            .otherwise(F.lit(False)),
            F.lit(False),
        )
    )

    # Validate timestamp.
    .withColumn(
        "has_valid_timestamp",
        F.col("event_timestamp").isNotNull()
    )

    # Overall Silver eligibility.
    .withColumn(
        "is_valid",
        (
            F.col("is_valid_entry_type")
            & F.col("has_required_fields")
            & F.col("has_valid_timestamp")
        )
    )
)


# -------------------------------------------------------------------
# Trusted Silver records
# -------------------------------------------------------------------

lineage_silver = (
    lineage_silver_staged
    .filter(F.col("is_valid"))
)


# -------------------------------------------------------------------
# Quarantine invalid records with failure reasons
# -------------------------------------------------------------------

lineage_quarantine = (
    lineage_silver_staged
    .filter(~F.col("is_valid"))
    .withColumn(
        "validation_error",
        F.concat_ws(
            "; ",
            F.when(
                ~F.col("is_valid_entry_type"),
                F.lit("invalid_entry_type")
            ),
            F.when(
                ~F.col("has_required_fields"),
                F.lit("missing_required_fields")
            ),
            F.when(
                ~F.col("has_valid_timestamp"),
                F.lit("invalid_timestamp")
            ),
        )
    )
)


# -------------------------------------------------------------------
# Persist trusted and rejected records
# -------------------------------------------------------------------

(
    lineage_silver
    .writeTo(SILVER_TABLE)
    .createOrReplace()
)

(
    lineage_quarantine
    .writeTo(QUARANTINE_TABLE)
    .createOrReplace()
)


# -------------------------------------------------------------------
# Verification
# -------------------------------------------------------------------

print("Input records:", lineage_bronze.count())
print("Silver records:", lineage_silver.count())
print("Quarantined records:", lineage_quarantine.count())

print("\nSilver event types:")
(
    lineage_silver
    .groupBy("entry_type")
    .agg(F.count("*").alias("records"))
    .orderBy(F.desc("records"))
    .show()
)

print("\nQuarantine failures:")
(
    lineage_quarantine
    .select(
        "entry_type",
        "event_id",
        "timestamp",
        "validation_error",
        "source_file",
    )
    .show(truncate=False)
)