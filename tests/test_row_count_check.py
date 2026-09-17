from src.validations.row_count_check import check_row_count


def test_passes_when_counts_match(clean_orders_df):
    result = check_row_count(clean_orders_df, clean_orders_df, tolerance_pct=0)
    assert result["passed"] is True


def test_fails_when_target_missing_rows(spark, clean_orders_df):
    # simulate a target that lost one row during load
    target_df = clean_orders_df.limit(2)
    result = check_row_count(clean_orders_df, target_df, tolerance_pct=0)
    assert result["passed"] is False
    assert result["violations"]["source_count"] == 3
    assert result["violations"]["target_count"] == 2
