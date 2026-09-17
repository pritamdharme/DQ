"""One place that builds the SparkSession — every test and every check
gets it from here so there's a single, consistent config.

Reuses an already-active session when one exists (Databricks notebooks,
whether classic cluster or Spark Connect, always have one already running)
and only builds a fresh local one when there isn't — e.g. on your own
machine or a plain CI runner.
"""

from pyspark.sql import SparkSession


def get_spark(app_name: str = "dq-automation-framework") -> SparkSession:
    existing = SparkSession.getActiveSession()
    if existing is not None:
        return existing

    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
