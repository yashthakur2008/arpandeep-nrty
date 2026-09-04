#!/usr/bin/env bash
# run_templates.sh: the whole template experiment with NO GPU. Rows A0/A1/B0x10/B1/H x targets x defenses x N cases.
# Needs: OPENAI_API_KEY (targets gpt-4o + guardrail gpt-4o-mini), ANTHROPIC_API_KEY (claude-sonnet-4-5).
# Usage: bash handoff/run_templates.sh            (defaults: N=200, 16 workers)
#        TARGETS="gpt-4o" DEFENSES="none" N=20 bash handoff/run_templates.sh   (cheap smoke)
# Resumable: every record is keyed (target, model, defense, row, case_id) in results/table.jsonl.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python}"
N="${N:-200}"
WORKERS="${WORKERS:-16}"
TARGETS="${TARGETS:-gpt-4o claude-sonnet-4-5}"
DEFENSES="${DEFENSES:-none promptarmor refuter}"
OUT="${OUT:-results/table.jsonl}"
[ -f handoff/.env ] && { set -a; . handoff/.env; set +a; }
: "${OPENAI_API_KEY:?OPENAI_API_KEY missing (needed for gpt-4o target and the gpt-4o-mini guardrail)}"
case " $TARGETS " in *claude*) : "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY missing}";; esac
mkdir -p results
$PY -m env.selfcheck
for m in $TARGETS; do for d in $DEFENSES; do
  echo "== target=$m defense=$d n=$N $(date -u +%FT%TZ)"
  $PY -m env.run_table --target openai --model "$m" --defense "$d" --n "$N" --workers "$WORKERS" --out "$OUT"
done; done
echo; echo "== Table 1 (all cells) =="
$PY - "$OUT" <<'PY'
import json, sys, csv
from collections import defaultdict
from env.run_table import METRICS, ROWS
agg = defaultdict(lambda: defaultdict(float))
for l in open(sys.argv[1]):
    r = json.loads(l); k = (r["model"], r["defense"], r["row"])
    for m in METRICS: agg[k][m] += r[m]
    agg[k]["n"] += 1
hdr = ["model", "defense", "row", "n", *METRICS]
rows = [[m, d, row, int(a["n"]), *[round(a[x] / a["n"], 3) for x in METRICS]]
        for (m, d, row), a in sorted(agg.items(), key=lambda kv: (kv[0][0], kv[0][1], list(ROWS).index(kv[0][2])))]
with open("results/table1.csv", "w", newline="") as f: csv.writer(f).writerows([hdr, *rows])
print("| " + " | ".join(hdr) + " |\n|" + "---|" * len(hdr))
for r in rows: print("| " + " | ".join(map(str, r)) + " |")
print("\nwrote results/table1.csv")
PY
