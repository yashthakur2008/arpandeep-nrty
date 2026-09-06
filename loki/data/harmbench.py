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


def split_behaviors(
    csv_path: str = DEFAULT_CSV,
    test_fraction: float = 0.3,
    seed: int = 0,
) -> tuple[list[dict], list[dict]]:
    """Deterministic train/test split over the behavior list.

    Without this, training and evaluation both sampled ``seed=0`` from the same
    list, so the eval behaviors were a subset of the training behaviors and the
    reported numbers were not held out.
    """
    import random

    rows = load_behaviors(csv_path, num_samples=None)
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    n_test = max(1, int(len(shuffled) * test_fraction))
    return shuffled[n_test:], shuffled[:n_test]


def create_harmbench_dataset(
    num_samples: int | None = None,
    csv_path: str = DEFAULT_CSV,
    seed: int | None = None,
    split: str = "all",
    test_fraction: float = 0.3,
) -> Dataset:
    """Build the conversational dataset TRL's GRPOTrainer expects.

    ``split`` is one of ``"train"``, ``"test"`` or ``"all"``. Use ``train`` for
    training and ``test`` for evaluation so that reported metrics are held out.
    """
    env = _environment()
    system_prompt = env.get_template("harmbench_system.j2").render()
    user_template = env.get_template("harmbench_user.j2")

    if split not in {"all", "train", "test"}:
        raise ValueError(f"split must be 'all', 'train' or 'test', got {split!r}")

    if split == "all":
        rows = load_behaviors(csv_path, num_samples=None)
    else:
        train_rows, test_rows = split_behaviors(
            csv_path, test_fraction=test_fraction, seed=seed if seed is not None else 0
        )
        rows = train_rows if split == "train" else test_rows

    # Sample before rendering when subsetting, so a small run is not always the
    # same first-N alphabetical slice of one category.
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
