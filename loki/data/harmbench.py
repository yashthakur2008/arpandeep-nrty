"""HarmBench dataset construction.

Moved from ``scripts/harmbench.py`` so it is importable as a library without
``sys.path`` surgery.
"""

from __future__ import annotations

import csv
import os
from typing import Any

from datasets import Dataset
from jinja2 import Environment, FileSystemLoader, StrictUndefined

_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(_PACKAGE_ROOT)
PROMPTS_DIR = os.path.join(_PACKAGE_ROOT, "prompts")
DEFAULT_CSV = os.path.join(PROJECT_ROOT, "scripts", "harmbench_behaviors_text_all.csv")


def _environment() -> Environment:
    # StrictUndefined: a renamed template variable should fail loudly, not
    # silently render an empty prompt.
    return Environment(loader=FileSystemLoader(PROMPTS_DIR), undefined=StrictUndefined)


def load_behaviors(csv_path: str = DEFAULT_CSV, num_samples: int | None = None) -> list[dict]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"HarmBench CSV not found at {csv_path}")

    rows: list[dict] = []
    with open(csv_path, encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            behavior = (row.get("Behavior") or "").strip()
            if not behavior:
                continue
            rows.append(
                {
                    "behavior": behavior,
                    "functional_category": row.get("FunctionalCategory", ""),
                    "semantic_category": row.get("SemanticCategory", ""),
                    "behavior_id": row.get("BehaviorID", ""),
                }
            )
            if num_samples is not None and len(rows) >= num_samples:
                break
    return rows


def create_harmbench_dataset(
    num_samples: int | None = None,
    csv_path: str = DEFAULT_CSV,
    seed: int | None = None,
) -> Dataset:
    """Build the conversational dataset TRL's GRPOTrainer expects."""
    env = _environment()
    system_prompt = env.get_template("harmbench_system.j2").render()
    user_template = env.get_template("harmbench_user.j2")

    # Sample before rendering when subsetting, so a small run is not always the
    # same first-N alphabetical slice of one category.
    rows = load_behaviors(csv_path, num_samples=None)
    if num_samples is not None and num_samples < len(rows):
        if seed is not None:
            import random

            rows = random.Random(seed).sample(rows, num_samples)
        else:
            rows = rows[:num_samples]

    records: list[dict[str, Any]] = []
    for row in rows:
        user_prompt = user_template.render(
            behavior=row["behavior"],
            functional_category=row["functional_category"],
            semantic_category=row["semantic_category"],
        )
        records.append(
            {
                "prompt": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                **row,
            }
        )

    if not records:
        raise ValueError(f"No usable HarmBench behaviors found in {csv_path}")

    return Dataset.from_list(records)
