# DQ Automation Framework (hands-on practice build)

A small, real, runnable data quality framework — PySpark validation
checks tested with PyTest, config-driven, structured to map cleanly onto
a Databricks Workflow. Built to practice, not just describe.

## What's in here

```
dq-automation-framework/
├── src/
│   ├── config.py                  # loads config/settings.yaml
│   ├── spark_utils.py             # get_spark() — reuses an active session (Databricks) or builds a local one
│   ├── pipeline/
│   │   ├── bronze.py              # raw landing: schema + row count checks only
│   │   ├── silver.py              # cleaned/deduped: null + duplicate checks on the *output*
│   │   └── gold.py                # aggregated: reconciliation against the real business key
│   └── validations/
│       ├── null_check.py          # completeness
│       ├── duplicate_check.py     # uniqueness
│       ├── schema_check.py        # shape/type check
│       └── row_count_check.py     # source vs target reconciliation
├── tests/
│   ├── conftest.py                 # spark fixture (session-scoped) + sample data (function-scoped)
│   ├── test_null_check.py
│   ├── test_duplicate_check.py
│   ├── test_schema_check.py
│   ├── test_row_count_check.py
│   ├── test_pipeline_bronze.py
│   ├── test_pipeline_silver.py
│   └── test_pipeline_gold.py
├── config/
│   └── settings.yaml               # expected schema, not-null columns, primary key, tolerance
├── INTERVIEW_QUESTIONS.md          # Q&A grounded in this project's actual code
├── requirements.txt
└── pytest.ini
```

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```

You should see 15 tests pass (9 on the individual checks, 6 on the
bronze/silver/gold pipeline). Java 17+ needs to be installed for PySpark
to run locally. On Databricks, see the note in `spark_utils.py` — it
reuses the notebook's already-active session instead of building a new
one, and run tests with `pytest.main()` in a notebook cell rather than
via `%sh`, since a shell subprocess doesn't have access to the
notebook's Spark Connect session.

## How to practice with this

1. **Run it once as-is** so you have a working baseline and the muscle
   memory of `pytest -v` output.
2. **Break something on purpose.** Edit `conftest.py` and add a null to
   `clean_orders_df`, or change `config/settings.yaml`'s `primary_key` to
   a column that isn't unique. Re-run and watch a specific test go red —
   that's the "how do you know it caught a real problem" story for an
   interview.
3. **Add a 5th check.** A good next one: a `value_range_check.py` that
   flags `order_amount < 0`. Copy the shape of `null_check.py` — a
   function that takes a DataFrame and config, returns a
   `{rule, passed, violations}` dict — then write `test_value_range_check.py`
   the same way the others are written. Doing this once yourself is worth
   more for interview readiness than reading ten more examples.
4. **Say it out loud while you run it.** Talk through what each check
   does and why the fixtures are scoped the way they are (session-scoped
   Spark because it's expensive to build, function-scoped data so tests
   don't leak into each other) — that's the exact material from your
   spoken-answer prep, now backed by code you've actually run.

## Bronze / Silver / Gold pipeline

`src/pipeline/` wires the same four checks into the three medallion
layers, each with a different job:

- **Bronze** (`bronze.py`) — raw pass-through. Only schema + row count
  checks run here, since Bronze isn't supposed to be clean yet.
- **Silver** (`silver.py`) — dedupes and drops nulls, then checks its
  *own output* for nulls and duplicates, proving the cleaning actually
  worked.
- **Gold** (`gold.py`) — aggregates, then reconciles the result against
  the distinct count of the real business key — deliberately kept
  separate from whatever column the aggregation grouped by, so the
  check can't be tautological (see `INTERVIEW_QUESTIONS.md` Q3 for the
  actual bug this caught while building it).

`tests/conftest.py`'s `raw_source_df` fixture seeds two realistic
defects — a duplicate landing and a missing required field — so the
pipeline tests prove each layer actually fixes what it's supposed to,
not just that the code runs.

## How each check maps to an interview answer

- `null_check.py` → completeness pillar. "Required columns should never
  be null — the column list comes from config, not hardcoded, so the
  same function runs against any table."
- `duplicate_check.py` → accuracy/uniqueness. "I group by the key and
  count — any group bigger than one is a duplicate."
- `schema_check.py` → schema pillar. "This runs before value checks,
  because a column that silently changed type breaks everything
  downstream."
- `row_count_check.py` → reconciliation. "Matching counts isn't proof by
  itself, but it's the cheap first check before something heavier like a
  hash comparison."

## Where this goes next (the fuller design, if they push deeper)

This build intentionally stays flat and simple — one file per check,
one test per check. If an interviewer asks "how would this scale on a
real team," that's your cue to bring in the fuller design already in
your prep notes: severity tiers (`expect` / `expect_or_drop` /
`expect_or_fail`) instead of a flat pass/fail, a reporting layer that
persists results to Postgres so failures trend over time, and running
the same check logic as native `@dlt.expect_or_fail(...)` decorators
inside a Databricks Lakeflow pipeline instead of a separate Workflow
task.
