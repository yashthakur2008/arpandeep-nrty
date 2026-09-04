"""Table 1 rows (A0, A1, B0 x 10 templates, H) against one Target.

Usage: python -m env.run_table --target stub --n 100
Resumable: results/<target>_table.jsonl keyed on (row, case_id).
"""

import argparse
import json
import os
from collections import defaultdict

from env.payloads import HIJACK_TEMPLATE, HYBRID_TEMPLATE, TEMPLATES, render
from env.research_env import build_cases, make_target, render_agent_prompt, reward, utility
from env.strip import is_instruction_free

ROWS = {"A0": None, "A1": HIJACK_TEMPLATE, **{f"B0_{k}": t for k, t in TEMPLATES.items()}, "H": HYBRID_TEMPLATE}


def run(target_name: str, n: int, seed: int, out: str) -> dict:
    cases = build_cases(n=max(n, 500), seed=seed)[:n]
    target = make_target(target_name, cases=cases, seed=seed)
    done = {}
    if os.path.exists(out):
        for line in open(out):
            r = json.loads(line)
            done[(r["row"], r["case_id"])] = r
    with open(out, "a") as f:
        for row, template in ROWS.items():
            for case in cases:
                if (row, case["id"]) in done:
                    continue
                doc = render(template, case) if template else None
                ans = target.answer(render_agent_prompt(case, doc, seed=seed))
                r = {
                    "row": row, "case_id": case["id"], "answer": ans,
                    "asr": reward(ans, case), "utility": utility(ans, case),
                    "flag": float(doc is not None and not is_instruction_free(doc)),
                }
                done[(row, case["id"])] = r
                f.write(json.dumps(r) + "\n")
    agg = defaultdict(lambda: defaultdict(float))
    for (row, _), r in done.items():
        for k in ("asr", "utility", "flag"):
            agg[row][k] += r[k]
        agg[row]["n"] += 1
    return agg


def print_table(agg: dict) -> None:
    print(f"{'row':<16}{'n':>5}{'ASR':>8}{'util':>8}{'flag':>8}")
    for row in ROWS:
        a = agg.get(row)
        if a:
            print(f"{row:<16}{int(a['n']):>5}{a['asr']/a['n']:>8.2f}{a['utility']/a['n']:>8.2f}{a['flag']/a['n']:>8.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="stub", choices=["stub", "vllm", "openai"])
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    os.makedirs("results", exist_ok=True)
    print_table(run(a.target, a.n, a.seed, a.out or f"results/{a.target}_table.jsonl"))
