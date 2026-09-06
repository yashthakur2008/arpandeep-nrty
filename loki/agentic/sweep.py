"""Run the scenario x policy x attack x target matrix and report statistics.

Usage:
    python -m loki.agentic.sweep --targets gpt-4o-mini claude-haiku-4-5 --trials 3

Statistics reported, and why:

* **Wilson intervals** rather than normal-approximation intervals, because
  violation rates sit near 0 and 1 where the normal approximation produces
  intervals that leave [0, 1] and understate uncertainty.
* **Fisher's exact test** rather than chi-squared, because per-cell counts are
  small by design (a few trials per condition, many conditions).
* Errored trials are **dropped, not scored as non-violations**. Counting an API
  timeout as "the agent complied with policy" would bias every rate downward.
"""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from math import comb, sqrt

from loki.agentic.attacks import get_attacks
from loki.agentic.harness import AgentOutcome, available_targets, run_scenario
from loki.agentic.scenarios import POLICY_VARIANTS, get_scenarios
from loki.runtime import configure_logging, set_seed

logger = logging.getLogger(__name__)


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval. Correct near 0 and 1, unlike the normal approx."""
    if n == 0:
        return (0.0, 0.0)
    phat = successes / n
    denom = 1 + z**2 / n
    centre = (phat + z**2 / (2 * n)) / denom
    margin = z * sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def fisher_exact_greater(a: int, b: int, c: int, d: int) -> float:
    """One-sided Fisher's exact test, P(X >= a) for the 2x2 table [[a,b],[c,d]]."""
    n = a + b + c + d
    if n == 0:
        return 1.0
    total = 0.0
    for i in range(a, min(a + b, a + c) + 1):
        total += comb(a + b, i) * comb(c + d, a + c - i)
    return min(1.0, total / comb(n, a + c))


@dataclass
class CellStats:
    key: str
    n: int
    violations: int
    rate: float
    ci_low: float
    ci_high: float


def summarise(outcomes: list[AgentOutcome], keyfn) -> list[CellStats]:
    buckets: dict[str, list[AgentOutcome]] = defaultdict(list)
    for o in outcomes:
        if o.errored:
            continue
        buckets[keyfn(o)].append(o)
    rows = []
    for key, items in sorted(buckets.items()):
        n = len(items)
        v = sum(o.violated for o in items)
        low, high = wilson_interval(v, n)
        rows.append(CellStats(key, n, v, v / max(n, 1), low, high))
    return rows


def run_sweep(
    targets: list[str],
    scenario_ids: list[str] | None,
    policy_variants: list[str],
    attack_names: list[str] | None,
    trials: int,
    workers: int,
    temperature: float,
) -> list[AgentOutcome]:
    scenarios = get_scenarios(scenario_ids)
    attacks = get_attacks(attack_names)

    jobs = [
        (scenario, policy, target, attack, trial)
        for scenario, policy, target, attack, trial in itertools.product(
            scenarios, policy_variants, targets, attacks, range(trials)
        )
    ]
    logger.info(
        "sweep: %d scenarios x %d policies x %d targets x %d attacks x %d trials = %d calls",
        len(scenarios), len(policy_variants), len(targets), len(attacks), trials, len(jobs),
    )

    def run_one(job) -> AgentOutcome:
        scenario, policy, target, attack, _ = job
        return run_scenario(
            scenario,
            policy_variant=policy,
            target=target,
            attack_text=attack.text(scenario),
            attack_name=attack.name,
            temperature=temperature,
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes = list(pool.map(run_one, jobs))

    n_err = sum(o.errored for o in outcomes)
    if n_err:
        logger.warning("%d/%d trials errored and are excluded", n_err, len(outcomes))
    return outcomes


def print_report(outcomes: list[AgentOutcome]) -> dict:
    valid = [o for o in outcomes if not o.errored]
    report: dict = {}

    def table(title: str, rows: list[CellStats]) -> None:
        print(f"\n{title}")
        print(f"{'condition':34s} {'n':>4s} {'viol':>5s} {'rate':>7s}   95% CI")
        for r in rows:
            print(
                f"{r.key:34s} {r.n:4d} {r.violations:5d} {r.rate:6.1%}   "
                f"[{r.ci_low:.1%}, {r.ci_high:.1%}]"
            )

    by_policy = summarise(valid, lambda o: o.policy_variant)
    by_attack = summarise(valid, lambda o: o.attack_name)
    by_target = summarise(valid, lambda o: o.target)
    by_scenario = summarise(valid, lambda o: o.scenario_id)

    table("VIOLATION RATE BY POLICY PHRASING", by_policy)
    table("VIOLATION RATE BY ATTACK", by_attack)
    table("VIOLATION RATE BY TARGET", by_target)
    table("VIOLATION RATE BY SCENARIO", by_scenario)

    report["by_policy"] = [asdict(r) for r in by_policy]
    report["by_attack"] = [asdict(r) for r in by_attack]
    report["by_target"] = [asdict(r) for r in by_target]
    report["by_scenario"] = [asdict(r) for r in by_scenario]

    # Headline test: does any attack beat the no-attack control?
    control = [o for o in valid if o.attack_name == "none"]
    attacked = [o for o in valid if o.attack_name != "none"]
    a, b = sum(o.violated for o in attacked), len(attacked) - sum(o.violated for o in attacked)
    c, d = sum(o.violated for o in control), len(control) - sum(o.violated for o in control)
    p = fisher_exact_greater(a, b, c, d)
    print(
        f"\nHEADLINE: control {c}/{len(control)} ({c / max(len(control), 1):.1%}) vs "
        f"attacked {a}/{len(attacked)} ({a / max(len(attacked), 1):.1%}), "
        f"one-sided Fisher p = {p:.3g}"
    )
    report["headline"] = {
        "control_violations": c, "control_n": len(control),
        "attacked_violations": a, "attacked_n": len(attacked),
        "fisher_p": p,
    }

    # The policy-phrasing contrast, which is the novel finding.
    print("\nPOLICY-PHRASING CONTRAST (attacked trials only)")
    per_policy = defaultdict(lambda: [0, 0])
    for o in attacked:
        per_policy[o.policy_variant][0] += int(o.violated)
        per_policy[o.policy_variant][1] += 1
    ranked = sorted(per_policy.items(), key=lambda kv: kv[1][0] / max(kv[1][1], 1))
    for name, (v, n) in ranked:
        low, high = wilson_interval(v, n)
        print(f"  {name:16s} {v:3d}/{n:3d} = {v / max(n, 1):6.1%}  [{low:.1%}, {high:.1%}]")
    if len(ranked) >= 2:
        (bn, (bv, bnn)), (wn, (wv, wnn)) = ranked[0], ranked[-1]
        pp = fisher_exact_greater(wv, wnn - wv, bv, bnn - bv)
        print(
            f"  strongest={bn} vs weakest={wn}: "
            f"{bv / max(bnn, 1):.1%} vs {wv / max(wnn, 1):.1%}, Fisher p = {pp:.3g}"
        )
        report["policy_contrast"] = {
            "strongest": bn, "weakest": wn,
            "strongest_rate": bv / max(bnn, 1), "weakest_rate": wv / max(wnn, 1),
            "fisher_p": pp,
        }
    return report


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Agentic policy-violation sweep")
    parser.add_argument("--targets", nargs="+", default=["gpt-4o-mini"])
    parser.add_argument("--scenarios", nargs="*", default=None)
    parser.add_argument("--policies", nargs="+", default=list(POLICY_VARIANTS))
    parser.add_argument("--attacks", nargs="*", default=None)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="results/agentic_sweep.json")
    args = parser.parse_args(argv)

    set_seed(args.seed)
    targets = available_targets(args.targets)
    if not targets:
        print("no usable targets (missing credentials)", file=sys.stderr)
        return 2

    outcomes = run_sweep(
        targets, args.scenarios, args.policies, args.attacks,
        args.trials, args.workers, args.temperature,
    )
    report = print_report(outcomes)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "config": {
                    "targets": targets, "policies": args.policies,
                    "trials": args.trials, "temperature": args.temperature,
                    "seed": args.seed,
                },
                "report": report,
                "outcomes": [o.to_dict() for o in outcomes],
            },
            handle,
            indent=2,
        )
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
