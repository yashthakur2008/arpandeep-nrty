"""Aggregate multi-seed base-vs-trained runs into one publishable table.

A single seed cannot distinguish a real effect from seed luck, so the headline
claim ("GRPO teaches format, not attack") needs replication. This pools the
paired per-behavior outcomes across seeds and reports:

  * per-seed and pooled attack success rate with bootstrap CIs
  * a paired McNemar test per seed and pooled
  * the format and tag-compliance deltas, which are the positive result

Usage:
    python -m loki.aggregate --base 'outputs/base_seed*.json' \
        --trained 'outputs/trained_seed*.json' --out results/multiseed.json
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import os
import re
import sys

import numpy as np

from loki.eval import bootstrap_ci
from loki.runtime import configure_logging

logger = logging.getLogger(__name__)

_SEED_RE = re.compile(r"seed(\d+)")


def _seed_of(path: str) -> str:
    match = _SEED_RE.search(os.path.basename(path))
    return match.group(1) if match else os.path.basename(path)


def _load(path: str) -> tuple[dict, dict]:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["summary"], {r["behavior_id"]: r for r in payload["records"]}


def mcnemar(base: list[float], trained: list[float]) -> tuple[int, int, float]:
    """Exact paired test. Returns (wins, losses, p)."""
    wins = sum(1 for b, t in zip(base, trained, strict=False) if b == 0 and t == 1)
    losses = sum(1 for b, t in zip(base, trained, strict=False) if b == 1 and t == 0)
    if wins + losses == 0:
        return wins, losses, 1.0
    from scipy.stats import binomtest

    return wins, losses, float(binomtest(wins, wins + losses, 0.5).pvalue)


def aggregate(base_glob: str, trained_glob: str, out_path: str | None = None) -> dict:
    base_files = {_seed_of(p): p for p in sorted(glob.glob(base_glob))}
    trained_files = {_seed_of(p): p for p in sorted(glob.glob(trained_glob))}
    seeds = sorted(set(base_files) & set(trained_files))
    if not seeds:
        raise ValueError(
            f"No matching seeds between {base_glob!r} and {trained_glob!r}. "
            f"base={list(base_files)} trained={list(trained_files)}"
        )

    per_seed = []
    pooled_base: list[float] = []
    pooled_trained: list[float] = []

    for seed in seeds:
        b_sum, b_rec = _load(base_files[seed])
        t_sum, t_rec = _load(trained_files[seed])
        ids = sorted(set(b_rec) & set(t_rec))
        # Unparseable output is a failed attack end to end, so score it 0 rather
        # than dropping it; dropping would flatter whichever model is worse at
        # producing well-formed attacks.
        pb = [b_rec[i].get("score", 0.0) for i in ids]
        pt = [t_rec[i].get("score", 0.0) for i in ids]
        wins, losses, p = mcnemar(pb, pt)
        pooled_base += pb
        pooled_trained += pt

        per_seed.append(
            {
                "seed": seed,
                "n": len(ids),
                "base_asr": float(np.mean(pb)) if pb else 0.0,
                "trained_asr": float(np.mean(pt)) if pt else 0.0,
                "delta": float(np.mean(pt) - np.mean(pb)) if pb else 0.0,
                "mcnemar_wins": wins,
                "mcnemar_losses": losses,
                "mcnemar_p": p,
                "base_format_rate": b_sum.get("format_rate"),
                "trained_format_rate": t_sum.get("format_rate"),
                "base_tag_rate": b_sum.get("tag_compliance_rate"),
                "trained_tag_rate": t_sum.get("tag_compliance_rate"),
            }
        )
        logger.info(
            "seed %s: ASR %.1f%% -> %.1f%% (p=%.3f) | tags %.0f%% -> %.0f%%",
            seed,
            100 * per_seed[-1]["base_asr"],
            100 * per_seed[-1]["trained_asr"],
            p,
            100 * (per_seed[-1]["base_tag_rate"] or 0),
            100 * (per_seed[-1]["trained_tag_rate"] or 0),
        )

    wins, losses, p = mcnemar(pooled_base, pooled_trained)
    b_low, b_high = bootstrap_ci(pooled_base)
    t_low, t_high = bootstrap_ci(pooled_trained)

    result = {
        "seeds": seeds,
        "per_seed": per_seed,
        "pooled": {
            "n": len(pooled_base),
            "base_asr": float(np.mean(pooled_base)),
            "base_ci": [b_low, b_high],
            "trained_asr": float(np.mean(pooled_trained)),
            "trained_ci": [t_low, t_high],
            "delta": float(np.mean(pooled_trained) - np.mean(pooled_base)),
            "mcnemar_wins": wins,
            "mcnemar_losses": losses,
            "mcnemar_p": p,
            "significant_at_05": p < 0.05,
        },
        "format": {
            "base_mean": float(
                np.mean([s["base_format_rate"] or 0 for s in per_seed])
            ),
            "trained_mean": float(
                np.mean([s["trained_format_rate"] or 0 for s in per_seed])
            ),
            "base_tag_mean": float(np.mean([s["base_tag_rate"] or 0 for s in per_seed])),
            "trained_tag_mean": float(
                np.mean([s["trained_tag_rate"] or 0 for s in per_seed])
            ),
        },
    }

    logger.info(
        "POOLED n=%d: ASR %.1f%% -> %.1f%% (delta %+.1f pts, McNemar p=%.3f) -> %s",
        result["pooled"]["n"],
        100 * result["pooled"]["base_asr"],
        100 * result["pooled"]["trained_asr"],
        100 * result["pooled"]["delta"],
        p,
        "SIGNIFICANT" if p < 0.05 else "no significant effect",
    )

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
        logger.info("Wrote %s", out_path)
    return result


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Aggregate multi-seed runs")
    parser.add_argument("--base", default="outputs/base_seed*.json")
    parser.add_argument("--trained", default="outputs/trained_seed*.json")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    result = aggregate(args.base, args.trained, args.out)
    print(json.dumps(result["pooled"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
