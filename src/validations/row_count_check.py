"""Reconciliation check: does the target have all the rows the source had.

Interview line: "Count matching isn't proof by itself — two datasets can
have the same count and still not match row for row — but it's the
cheap first check that catches the obvious break, like a truncated
load, before I run anything heavier like a hash comparison."
"""

from pyspark.sql import DataFrame


def check_row_count(
    source_df: DataFrame, target_df: DataFrame, tolerance_pct: float = 0
) -> dict:
    source_count = source_df.count()
    target_count = target_df.count()

    if source_count == 0:
        diff_pct = 0 if target_count == 0 else 100.0
    else:
        diff_pct = abs(source_count - target_count) / source_count * 100

    passed = diff_pct <= tolerance_pct
    return {
        "rule": "row_count_check",
        "passed": passed,
        "violations": {
            "source_count": source_count,
            "target_count": target_count,
            "diff_pct": round(diff_pct, 2),
        }
        if not passed
        else {},
    }
