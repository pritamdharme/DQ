from src.pipeline.bronze import load_bronze


def test_bronze_passes_schema_and_count(raw_source_df, pipeline_schema):
    bronze_df, results = load_bronze(raw_source_df, pipeline_schema)

    assert bronze_df.count() == raw_source_df.count()  # bronze is a pass-through, nothing dropped
    assert all(r["passed"] for r in results)


def test_bronze_catches_missing_column(raw_source_df):
    broken_schema = {
        "order_id": "string",
        "shipping_country": "string",  # doesn't exist upstream
    }
    _, results = load_bronze(raw_source_df, broken_schema)

    schema_result = next(r for r in results if r["rule"] == "schema_check")
    assert schema_result["passed"] is False
    assert "shipping_country" in schema_result["violations"]["missing_columns"]
