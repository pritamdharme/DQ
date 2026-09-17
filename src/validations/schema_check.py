"""Schema check: are the columns and types what we expect.

Interview line: "Before I even check the data's values, I check the
data's shape — missing columns or a type that silently changed
upstream (like an int becoming a string) breaks everything
downstream, so this runs first."
"""

from pyspark.sql import DataFrame

# Maps our plain config names to Spark's internal type names
_TYPE_ALIASES = {
    "string": "string",
    "double": "double",
    "int": "int",
    "integer": "int",
    "timestamp": "timestamp",
    "boolean": "boolean",
}


def check_schema(df: DataFrame, expected_schema: dict[str, str]) -> dict:
    actual_types = {f.name: f.dataType.typeName() for f in df.schema.fields}

    missing_columns = [c for c in expected_schema if c not in actual_types]
    type_mismatches = {}
    for column, expected_type in expected_schema.items():
        if column in actual_types:
            expected_normalized = _TYPE_ALIASES.get(expected_type, expected_type)
            if actual_types[column] != expected_normalized:
                type_mismatches[column] = {
                    "expected": expected_normalized,
                    "actual": actual_types[column],
                }

    passed = not missing_columns and not type_mismatches
    return {
        "rule": "schema_check",
        "passed": passed,
        "violations": {
            "missing_columns": missing_columns,
            "type_mismatches": type_mismatches,
        }
        if not passed
        else {},
    }
