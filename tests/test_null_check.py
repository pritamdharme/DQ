from src.validations.null_check import check_nulls


def test_passes_when_no_nulls(clean_orders_df, config):
    result = check_nulls(clean_orders_df, config["not_null_columns"])
    assert result["passed"] is True
    assert result["violations"] == {}


def test_fails_when_required_column_has_null(orders_with_nulls_df, config):
    result = check_nulls(orders_with_nulls_df, config["not_null_columns"])
    assert result["passed"] is False
    assert "order_amount" in result["violations"]
    assert result["violations"]["order_amount"] == 1
