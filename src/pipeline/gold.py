"""Gold layer: business-rule / reporting-ready aggregates.

Interview line: "Gold is a rollup, so the check here isn't nulls or
duplicates — it's reconciliation. I check gold's row count against the
number of distinct values of the *business key* I actually meant to
group by. That has to be a real, independent business key — not just
'whatever column I grouped by' — otherwise the check is tautological
and can never catch a bug like grouping on the wrong column."
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.validations.row_count_check import check_row_count


def build_gold(
    silver_df: DataFrame,
    group_by_col: str,
    agg_col: str,
    expected_key_col: str | None = None,
) -> tuple[DataFrame, list[dict]]:
    """expected_key_col defaults to group_by_col for normal use. Pass a
    different column explicitly when you want the reconciliation check
    to hold the aggregation accountable to a business key independent
    of whatever column the groupBy actually used (this is what makes
    the check able to catch a 'grouped by the wrong column' bug).
    """
    if expected_key_col is None:
        expected_key_col = group_by_col

    gold_df = silver_df.groupBy(group_by_col).agg(F.sum(agg_col).alias(f"total_{agg_col}"))

    expected_group_count_df = silver_df.select(expected_key_col).distinct()
    results = [
        check_row_count(expected_group_count_df, gold_df, tolerance_pct=0),
    ]
    return gold_df, results
