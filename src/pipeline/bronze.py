"""Bronze layer: raw, unvalidated landing zone.

Interview line: "Bronze doesn't clean anything — it just has to prove
nothing was lost or silently changed shape on the way in. That's why the
checks here are schema and row count, not nulls or duplicates."
"""

from pyspark.sql import DataFrame

from src.validations.row_count_check import check_row_count
from src.validations.schema_check import check_schema


def load_bronze(source_df: DataFrame, expected_schema: dict[str, str]) -> tuple[DataFrame, list[dict]]:
    """In a real pipeline this would read from S3/a raw landing path.
    Here, the "load" is a pass-through so the check logic is what's on
    display, not I/O plumbing.
    """
    bronze_df = source_df

    results = [
        check_schema(bronze_df, expected_schema),
        check_row_count(source_df, bronze_df, tolerance_pct=0),
    ]
    return bronze_df, results
