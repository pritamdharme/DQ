from src.pipeline.bronze import load_bronze
from src.pipeline.silver import build_silver


def test_silver_removes_duplicates_and_nulls(raw_source_df, pipeline_schema, config):
    bronze_df, _ = load_bronze(raw_source_df, pipeline_schema)
    silver_df, results = build_silver(
        bronze_df, config["not_null_columns"], config["primary_key"]
    )

    # raw had 4 rows: one exact duplicate + one null amount -> silver should have 2 clean rows
    assert silver_df.count() == 2
    assert all(r["passed"] for r in results)


def test_silver_checks_would_fail_on_uncleaned_data(raw_source_df, pipeline_schema, config):
    """Proves the checks are actually doing something — run them against
    the raw (uncleaned) data and confirm they correctly report problems."""
    from src.validations.duplicate_check import check_duplicates
    from src.validations.null_check import check_nulls

    bronze_df, _ = load_bronze(raw_source_df, pipeline_schema)

    dup_result = check_duplicates(bronze_df, config["primary_key"])
    null_result = check_nulls(bronze_df, config["not_null_columns"])

    assert dup_result["passed"] is False
    assert null_result["passed"] is False
