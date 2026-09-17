"""Loads config/settings.yaml — thresholds, expected schema, and the
primary key all live in config, not hardcoded inside check functions.
That's what makes a check reusable across tables: point it at a
different config, not different code."""

from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)
