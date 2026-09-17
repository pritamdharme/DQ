from src.validations.duplicate_check import check_duplicates


def test_passes_when_keys_are_unique(clean_orders_df, config):
    result = check_duplicates(clean_orders_df, config["primary_key"])
    assert result["passed"] is True


def test_fails_when_key_repeats(orders_with_duplicates_df, config):
    result = check_duplicates(orders_with_duplicates_df, config["primary_key"])
    assert result["passed"] is False
    assert result["violations"]["duplicate_key_count"] == 1
