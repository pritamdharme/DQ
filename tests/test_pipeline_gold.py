from src.pipeline.bronze import load_bronze
from src.pipeline.gold import build_gold
from src.pipeline.silver import build_silver


def test_gold_reconciles_to_silver(raw_source_df, pipeline_schema, config):
    bronze_df, _ = load_bronze(raw_source_df, pipeline_schema)
    silver_df, _ = build_silver(bronze_df, config["not_null_columns"], config["primary_key"])

    gold_df, results = build_gold(silver_df, group_by_col="customer_id", agg_col="order_amount")

    # 2 clean rows in silver, 2 distinct customers -> gold should have 2 rows
    assert gold_df.count() == 2
    assert all(r["passed"] for r in results)


def test_gold_catches_a_bad_aggregation(spark, config):
    """Seed a defect on purpose: two rows share a customer_id but the
    aggregation groups by order_id instead, so gold ends up with more
    rows than there are distinct customers — this should fail
    reconciliation."""
    from src.pipeline.gold import build_gold

    data = [
        ("ORD001", "CUST01", 100.0, "SHIPPED"),
        ("ORD002", "CUST01", 50.0, "SHIPPED"),  # same customer, different order
    ]
    silver_df = spark.createDataFrame(
        data, ["order_id", "customer_id", "order_amount", "order_status"]
    )

    # deliberately group by the wrong column to simulate a bug, while the
    # reconciliation is still held to the real business key (customer_id)
    gold_df, results = build_gold(
        silver_df,
        group_by_col="order_id",
        agg_col="order_amount",
        expected_key_col="customer_id",
    )

    assert gold_df.count() == 2  # bug: should have been 1 (one customer)
    result = results[0]
    assert result["passed"] is False
    assert result["violations"]["source_count"] == 1  # 1 distinct customer expected
    assert result["violations"]["target_count"] == 2  # but gold produced 2 rows
