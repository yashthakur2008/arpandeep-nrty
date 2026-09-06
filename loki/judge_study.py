"""Judge agreement study: how much does reported ASR depend on the judge?

Attack-success rate is the headline metric of every jailbreak paper, but it is
produced by a judge that is rarely validated. Our own audit found two concrete
judge bugs in this repository:

  * a keyword judge that scored *any* response over 100 characters as a
    successful jailbreak, and
  * a refusal regex that missed "I can<U+2019>t ..." because models emit the Unicode
    right single quote rather than the ASCII apostrophe.

This script re-judges an existing eval file with several judges and reports
pairwise agreement, Cohen's kappa, and the ASR each judge would have reported
from identical model outputs. Because it re-judges cached responses, it costs
one cheap API call per sample and no GPU time.

Usage:
    python -m loki.judge_study --input outputs/trained_v1_heldout.json \
        --judges heuristic ollama openai --out results/judge_study.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass

import numpy as np

from loki.eval import bootstrap_ci
from loki.rewards.judges import build_judge
from loki.runtime import configure_logging

logger = logging.getLogger(__name__)


@dataclass
class JudgeSummary:
    judge: str
    n: int
    n_complied: int
    asr: float
    ci_low: float
    ci_high: float
    n_errors: int


def cohens_kappa(a: list[int], b: list[int]) -> float:
    """Chance-corrected agreement between two binary raters."""
    if not a:
        return float("nan")
    n = len(a)
    observed = sum(1 for x, y in zip(a, b, strict=False) if x == y) / n
    pa1, pb1 = sum(a) / n, sum(b) / n
    expected = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)


def load_responses(path: str) -> list[dict]:
    """Pull the cached (behavior, target_response) pairs from an eval file."""
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    return [
        r
        for r in payload["records"]
        if r.get("target_response")  # only samples with a real measurement
    ]


def run_study(
    input_path: str,
    judge_names: list[str],
    judge_models: dict[str, str] | None = None,
    out_path: str | None = None,
) -> dict:
    judge_models = judge_models or {}
    records = load_responses(input_path)
    if not records:
        raise ValueError(f"No judged responses with target_response in {input_path}")

    logger.info("Re-judging %d cached responses with: %s", len(records), judge_names)

    verdicts: dict[str, list[int]] = {}
    errors: dict[str, int] = {}

    for name in judge_names:
        judge = build_judge(name, judge_models.get(name))
        column, n_err = [], 0
        for record in records:
            judgement = judge.judge(record["behavior"], record["target_response"])
            if judgement.errored:
                n_err += 1
                column.append(0)
            else:
                column.append(0 if judgement.refused else 1)
        verdicts[name] = column
        errors[name] = n_err
        logger.info("  %-18s ASR=%.0f%% (%d errors)", name, 100 * np.mean(column), n_err)

    summaries = []
    for name, column in verdicts.items():
        low, high = bootstrap_ci([float(v) for v in column])
        summaries.append(
            JudgeSummary(
                judge=name,
                n=len(column),
                n_complied=int(sum(column)),
                asr=float(np.mean(column)),
                ci_low=low,
                ci_high=high,
                n_errors=errors[name],
            )
        )

    pairwise = {}
    for a, b in itertools.combinations(judge_names, 2):
        agree = sum(1 for x, y in zip(verdicts[a], verdicts[b], strict=False) if x == y)
        pairwise[f"{a}__vs__{b}"] = {
            "agreement": agree / len(records),
            "kappa": cohens_kappa(verdicts[a], verdicts[b]),
            "n_disagree": len(records) - agree,
        }

    asrs = [s.asr for s in summaries]
    result = {
        "input": input_path,
        "n": len(records),
        "summaries": [asdict(s) for s in summaries],
        "pairwise": pairwise,
        "asr_spread": max(asrs) - min(asrs) if asrs else 0.0,
        "disagreements": [
            {
                "behavior": records[i]["behavior"][:200],
                "response": records[i]["target_response"][:300],
                "verdicts": {name: verdicts[name][i] for name in judge_names},
            }
            for i in range(len(records))
            if len({verdicts[name][i] for name in judge_names}) > 1
        ][:25],
    }

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
        logger.info("Wrote %s", out_path)

    return result


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Judge agreement study")
    parser.add_argument("--input", required=True, help="an eval .json with records")
    parser.add_argument(
        "--judges", nargs="+", default=["heuristic", "ollama", "openai"]
    )
    parser.add_argument("--ollama-model", default="llama3.2")
    parser.add_argument("--openai-model", default="gpt-4o-mini")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    result = run_study(
        args.input,
        args.judges,
        {"ollama": args.ollama_model, "openai": args.openai_model},
        args.out,
    )

    print(json.dumps({k: v for k, v in result.items() if k != "disagreements"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
