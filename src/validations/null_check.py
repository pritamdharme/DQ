"""Completeness check: required columns should never be null.

Interview line: "I don't hardcode which columns to check — the list
comes from config, so the same function runs against any table."
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def check_nulls(df: DataFrame, not_null_columns: list[str]) -> dict:
    """Returns a result dict: which columns had nulls, and how many rows.

    Design note: this returns a structured result instead of raising —
    the caller (a test, or a pipeline gate) decides whether a null here
    is a warning or a hard failure. The check itself stays dumb and
    reusable.
    """
    violations = {}
    for column in not_null_columns:
        null_count = df.filter(col(column).isNull()).count()
        if null_count > 0:
            violations[column] = null_count

    return {
        "rule": "null_check",
        "passed": len(violations) == 0,
        "violations": violations,
    }
