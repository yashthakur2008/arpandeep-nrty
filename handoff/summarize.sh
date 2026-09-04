#!/usr/bin/env bash
# summarize.sh: one-page verdict per lane from logs + results. Rewritten every 10 min by run_all.sh.
W="${WORKSPACE:-/workspace}"; L="$W/loki"; LOG="$W/logs"; RES="$L/results"
echo "# SUMMARY  $(date -u +%FT%TZ)"; echo
st() { # lane -> RUNNING / DONE / FAILED
  f="$LOG/$1.log"; [ -f "$f" ] || { echo "NOT STARTED"; return; }
  e=$(grep -o 'LANE_EXIT=[0-9]*' "$f" | tail -1 | cut -d= -f2)
  [ -z "$e" ] && echo RUNNING || { [ "$e" = 0 ] && echo DONE || echo "FAILED (exit $e)"; }
}
for lane in target api grpo2 grpo3 sleep; do printf "%-8s %s\n" "$lane" "$(st $lane)"; done; echo

echo "## API lane: the headline number (silent failure under PromptArmor)"
if [ -f "$RES/table1.md" ]; then cat "$RES/table1.md"; echo
  # verdict: best B row silent-failure under promptarmor vs A1
  python3 - "$RES/table1.csv" <<'EOF' 2>/dev/null || echo "(verdict needs table1.csv)"
import csv,sys
rows=list(csv.DictReader(open(sys.argv[1])))
def get(row,defense,col): 
    v=[r for r in rows if r['row'].startswith(row) and r['defense']==defense]
    return max(float(r[col]) for r in v) if v else None
b=get('B','promptarmor','silent_failure'); a=get('A1','promptarmor','silent_failure')
if b is None: print("VERDICT: incomplete")
elif b>=0.30 and (a or 0)<0.05: print(f"VERDICT: STRONG  (B silent-failure {b:.2f} vs hijack {a:.2f} under PromptArmor). AgentWild is the paper. Fire eval rows.")
elif b>=0.15: print(f"VERDICT: OK      (B {b:.2f} vs A1 {a:.2f}). Paper exists, headline softer. Check refuter column.")
else: print(f"VERDICT: WEAK    (B {b:.2f}). Templates do not beat PromptArmor. Lean on GRPO row or pivot to sleep.")
EOF
else echo "(no table1 yet)  last: $(tail -1 $LOG/api.log 2>/dev/null)"; fi; echo

echo "## GRPO lanes (reward curve must not be flat)"
for g in grpo2 grpo3; do echo "- $g: $(grep -E 'reward/mean|smoke|KILL|step' $LOG/$g.log 2>/dev/null | tail -2 | tr '\n' ' ')"; done; echo

echo "## Sleep lane"
grep -E 'download done|GATE|macro|kappa|MESA' "$LOG/sleep.log" 2>/dev/null | tail -6; echo
for s in 0 1 2; do [ -f "$W/outputs/sft_s$s/eval.json" ] && { printf "seed %s: " $s; cat "$W/outputs/sft_s$s/eval.json"; echo; }; done; echo

echo "## Next"
echo "STRONG -> write AgentWild; GPU2-3 run eval/transfer rows. WEAK -> sleep is primary if its gate passed. Either way: humans write from 09:00."
