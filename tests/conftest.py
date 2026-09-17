import sys
from pathlib import Path

import pytest

# so `from src...` works when pytest is run from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import load_config
from src.spark_utils import get_spark


@pytest.fixture(scope="session")
def spark():
    """One SparkSession for the whole test run — building it is expensive,
    and tests don't need isolation from each other at the session level."""
    s = get_spark(app_name="dq-framework-tests")
    yield s
    s.stop()


@pytest.fixture(scope="session")
def config():
    """Config is read-only and cheap — session scope is fine here."""
    return load_config()


@pytest.fixture
def clean_orders_df(spark):
    """A batch with no data quality problems — the control case."""
    data = [
        ("ORD001", "CUST01", 120.50, "SHIPPED"),
        ("ORD002", "CUST02", 45.00, "PENDING"),
        ("ORD003", "CUST03", 300.75, "SHIPPED"),
    ]
    return spark.createDataFrame(data, ["order_id", "customer_id", "order_amount", "order_status"])


@pytest.fixture
def orders_with_nulls_df(spark):
    """order_amount is null on one row — should fail the null check."""
    data = [
        ("ORD001", "CUST01", 120.50, "SHIPPED"),
        ("ORD002", "CUST02", None, "PENDING"),
    ]
    return spark.createDataFrame(data, ["order_id", "customer_id", "order_amount", "order_status"])


@pytest.fixture
def orders_with_duplicates_df(spark):
    """ORD001 appears twice — should fail the duplicate check."""
    data = [
        ("ORD001", "CUST01", 120.50, "SHIPPED"),
        ("ORD001", "CUST01", 120.50, "SHIPPED"),
        ("ORD002", "CUST02", 45.00, "PENDING"),
    ]
    return spark.createDataFrame(data, ["order_id", "customer_id", "order_amount", "order_status"])


# ---- Pipeline (bronze -> silver -> gold) fixtures ----

@pytest.fixture
def raw_source_df(spark):
    """The source system's raw feed: has a duplicate row (ORD001 landed
    twice, a common real-world symptom of an upstream retry) and one row
    missing order_amount. Bronze should let both through unchanged —
    that's Silver's job to fix."""
    data = [
        ("ORD001", "CUST01", 120.50, "SHIPPED"),
        ("ORD001", "CUST01", 120.50, "SHIPPED"),  # duplicate landing
        ("ORD002", "CUST02", 45.00, "PENDING"),
        ("ORD003", "CUST03", None, "SHIPPED"),  # missing amount
    ]
    return spark.createDataFrame(data, ["order_id", "customer_id", "order_amount", "order_status"])


@pytest.fixture
def pipeline_schema():
    return {
        "order_id": "string",
        "customer_id": "string",
        "order_amount": "double",
        "order_status": "string",
    }
