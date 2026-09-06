"""Build a human-labelling sheet for judge validation, and score judges against it.

The judge-validity result is only as strong as its ground truth. Our earlier
"manual labels" were a regex over refusal prefixes, which is itself a heuristic
and cannot be used to prove heuristics are good. This module exports a CSV for a
human to label, then scores every judge against those labels with accuracy,
precision, recall and Cohen's kappa.

    # 1. export a blind sheet (verdict column left empty, judge columns hidden)
    python -m loki.label_sheet export --inputs outputs/*.json --out labels/sheet.csv

    # 2. a human fills in the `human_verdict` column with COMPLIED / REFUSED

    # 3. score judges against it
    python -m loki.label_sheet score --sheet labels/sheet.csv --out results/judge_accuracy.json
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import logging
import os
import random
import sys
from dataclasses import asdict, dataclass

from loki.rewards.judges import build_judge
from loki.runtime import configure_logging

logger = logging.getLogger(__name__)

VALID_LABELS = {"COMPLIED", "REFUSED"}
FIELDNAMES = [
    "sample_id",
    "source_file",
    "behavior",
    "misdirection",
    "target_response",
    "human_verdict",
]


def export_sheet(
    input_globs: list[str],
    out_path: str,
    limit: int | None = None,
    seed: int = 0,
) -> int:
    """Write a blind labelling CSV.

    Judge verdicts are deliberately excluded so the human is not anchored by
    them, which would destroy the value of the ground truth.
    """
    rows = []
    for pattern in input_globs:
        for path in sorted(glob.glob(pattern)):
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
            for i, record in enumerate(payload.get("records", [])):
                if not record.get("target_response"):
                    continue
                rows.append(
                    {
                        "sample_id": f"{os.path.basename(path)}:{i}",
                        "source_file": os.path.basename(path),
                        "behavior": record["behavior"],
                        "misdirection": record.get("misdirection", ""),
                        "target_response": record["target_response"],
                        "human_verdict": "",
                    }
                )

    # Deduplicate identical (behavior, response) pairs: labelling the same text
    # twice adds cost without adding information.
    seen, unique = set(), []
    for row in rows:
        key = (row["behavior"], row["target_response"])
        if key not in seen:
            seen.add(key)
            unique.append(row)

    random.Random(seed).shuffle(unique)
    if limit:
        unique = unique[:limit]

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique)

    logger.info("Wrote %d rows to %s", len(unique), out_path)
    logger.info("Fill in 'human_verdict' with COMPLIED or REFUSED, then run 'score'.")
    return len(unique)


@dataclass
class JudgeAccuracy:
    judge: str
    n: int
    accuracy: float
    precision: float
    recall: float
    kappa: float
    false_positives: int
    false_negatives: int
    reported_asr: float
    human_asr: float


def _metrics(name: str, pred: list[int], truth: list[int]) -> JudgeAccuracy:
    tp = sum(1 for p, t in zip(pred, truth, strict=False) if p == 1 and t == 1)
    fp = sum(1 for p, t in zip(pred, truth, strict=False) if p == 1 and t == 0)
    tn = sum(1 for p, t in zip(pred, truth, strict=False) if p == 0 and t == 0)
    fn = sum(1 for p, t in zip(pred, truth, strict=False) if p == 0 and t == 1)
    n = len(truth)

    from loki.judge_study import cohens_kappa

    return JudgeAccuracy(
        judge=name,
        n=n,
        accuracy=(tp + tn) / n if n else 0.0,
        precision=tp / (tp + fp) if (tp + fp) else 0.0,
        recall=tp / (tp + fn) if (tp + fn) else 0.0,
        kappa=cohens_kappa(pred, truth),
        false_positives=fp,
        false_negatives=fn,
        reported_asr=sum(pred) / n if n else 0.0,
        human_asr=sum(truth) / n if n else 0.0,
    )


def score_sheet(
    sheet_path: str,
    judge_names: list[str],
    judge_models: dict[str, str] | None = None,
    out_path: str | None = None,
) -> dict:
    judge_models = judge_models or {}
    with open(sheet_path, encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if r.get("human_verdict")]

    bad = {r["human_verdict"].strip().upper() for r in rows} - VALID_LABELS
    if bad:
        raise ValueError(f"human_verdict must be COMPLIED or REFUSED; found {bad}")
    if not rows:
        raise ValueError(
            f"No labelled rows in {sheet_path}. Fill in the human_verdict column."
        )

    truth = [1 if r["human_verdict"].strip().upper() == "COMPLIED" else 0 for r in rows]
    logger.info("Scoring %d human-labelled samples", len(rows))

    results = []
    for name in judge_names:
        judge = build_judge(name, judge_models.get(name))
        pred = [
            0 if judge.judge(r["behavior"], r["target_response"]).refused else 1
            for r in rows
        ]
        accuracy = _metrics(name, pred, truth)
        results.append(accuracy)
        logger.info(
            "  %-18s acc=%.0f%% kappa=%.2f FP=%d ASR: reported %.0f%% vs human %.0f%%",
            name,
            100 * accuracy.accuracy,
            accuracy.kappa,
            accuracy.false_positives,
            100 * accuracy.reported_asr,
            100 * accuracy.human_asr,
        )

    payload = {
        "sheet": sheet_path,
        "n_labelled": len(rows),
        "human_asr": sum(truth) / len(truth),
        "judges": [asdict(r) for r in results],
    }
    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        logger.info("Wrote %s", out_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Human labelling for judge validation")
    sub = parser.add_subparsers(dest="command", required=True)

    exp = sub.add_parser("export", help="write a blind labelling CSV")
    exp.add_argument("--inputs", nargs="+", required=True)
    exp.add_argument("--out", default="labels/sheet.csv")
    exp.add_argument("--limit", type=int, default=200)
    exp.add_argument("--seed", type=int, default=0)

    sco = sub.add_parser("score", help="score judges against human labels")
    sco.add_argument("--sheet", required=True)
    sco.add_argument("--judges", nargs="+", default=["heuristic", "ollama", "openai"])
    sco.add_argument("--ollama-model", default="llama3.2")
    sco.add_argument("--openai-model", default="gpt-4o-mini")
    sco.add_argument("--out", default=None)

    args = parser.parse_args(argv)

    if args.command == "export":
        export_sheet(args.inputs, args.out, args.limit, args.seed)
    else:
        payload = score_sheet(
            args.sheet,
            args.judges,
            {"ollama": args.ollama_model, "openai": args.openai_model},
            args.out,
        )
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
