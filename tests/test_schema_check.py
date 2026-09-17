from src.validations.schema_check import check_schema


def test_passes_when_schema_matches(clean_orders_df):
    expected = {
        "order_id": "string",
        "customer_id": "string",
        "order_amount": "double",
        "order_status": "string",
    }
    result = check_schema(clean_orders_df, expected)
    assert result["passed"] is True


def test_fails_when_column_missing(clean_orders_df):
    expected = {
        "order_id": "string",
        "shipping_country": "string",  # doesn't exist in the dataframe
    }
    result = check_schema(clean_orders_df, expected)
    assert result["passed"] is False
    assert "shipping_country" in result["violations"]["missing_columns"]


def test_fails_when_type_mismatch(clean_orders_df):
    expected = {"order_amount": "string"}  # actually a double
    result = check_schema(clean_orders_df, expected)
    assert result["passed"] is False
    assert "order_amount" in result["violations"]["type_mismatches"]
