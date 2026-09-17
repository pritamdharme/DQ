"""Silver layer: cleaned and deduplicated.

Interview line: "Silver is where I actually change the data — drop
duplicates, drop rows missing a required field — so it's also where the
heavier checks live. I check the *result* of cleaning, not just the
input, because a bad dedup rule can silently drop good rows too."
"""

from pyspark.sql import DataFrame

from src.validations.duplicate_check import check_duplicates
from src.validations.null_check import check_nulls


def build_silver(
    bronze_df: DataFrame, not_null_columns: list[str], primary_key: str
) -> tuple[DataFrame, list[dict]]:
    silver_df = bronze_df.dropDuplicates([primary_key]).na.drop(subset=not_null_columns)

    results = [
        check_nulls(silver_df, not_null_columns),
        check_duplicates(silver_df, primary_key),
    ]
    return silver_df, results
