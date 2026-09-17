"""Accuracy/uniqueness check: no key should appear more than once.

Interview line: "I group by the key column and count — any group bigger
than one is a duplicate. On a real dataset I'd do this in Spark SQL
rather than collecting to the driver, so it scales past what fits in
memory."
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count


def check_duplicates(df: DataFrame, primary_key: str) -> dict:
    dup_rows = (
        df.groupBy(col(primary_key))
        .agg(count("*").alias("row_count"))
        .filter(col("row_count") > 1)
    )
    dup_count = dup_rows.count()

    return {
        "rule": "duplicate_check",
        "passed": dup_count == 0,
        "violations": {"duplicate_key_count": dup_count} if dup_count else {},
    }
