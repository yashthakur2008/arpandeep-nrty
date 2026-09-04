#!/usr/bin/env bash
# run_all.sh: ONE command. Launches every lane in tmux on a 6-8 GPU pod, gated and resumable, writes results/SUMMARY.md.
# Usage: bash handoff/run_all.sh        (after bootstrap.sh; needs handoff/.env filled)
# Re-running is safe: every lane resumes from its own state.
set -euo pipefail
W="${WORKSPACE:-/workspace}"; L="$W/loki"; LOG="$W/logs"; RES="$L/results"; mkdir -p "$LOG" "$RES"
cd "$L"
[ -f handoff/.env ] || { echo "!! handoff/.env missing. cp handoff/.env.example handoff/.env and fill keys."; exit 1; }
set -a; . handoff/.env; set +a
for k in OPENAI_API_KEY ANTHROPIC_API_KEY NSRR_TOKEN; do [ -n "${!k:-}" ] || { echo "!! $k empty in handoff/.env"; exit 1; }; done
NGPU=$(nvidia-smi -L | wc -l); echo "== run_all $(date -u +%FT%TZ) gpus=$NGPU"
[ "$NGPU" -ge 6 ] || echo "WARN: $NGPU GPUs, lanes assume 6+. Attacker seeds will serialize."
git fetch -q origin; git checkout -q aw-env; git pull -q; git checkout -q origin/agentwild-pivot -- handoff 2>/dev/null || true
git show origin/sleep-paper:nsrr_load.py > nsrr_load.py; git show origin/sleep-paper:psg_words.py > psg_words.py
git show origin/sleep-paper:nsrr_sft.py > nsrr_sft.py 2>/dev/null || echo "WARN: nsrr_sft.py not on sleep-paper yet, sleep lane stops at the LR gate."

lane() { # name, gpus, cmd
  tmux kill-session -t "$1" 2>/dev/null || true
  tmux new -d -s "$1" "cd $L && CUDA_VISIBLE_DEVICES=$2 bash -c '$3' 2>&1 | tee -a $LOG/$1.log; echo LANE_EXIT=\$? >> $LOG/$1.log"
  echo "  launched $1 on gpu[$2]  -> tail -f $LOG/$1.log"
}

# Lane A+B+C: AgentWild, one sequential lane (giraffe's script owns the order):
#   templates on API targets (no GPU, headline number) -> gate -> vLLM 72B on GPU0-1 -> GRPO B4 x3 seeds on GPU2
lane agentwild 0,1,2,3 "bash handoff/run_agentwild.sh"

# Lane D: sleep, GPU4-5: download -> loader -> LR gate -> SFT x3 seeds ------
lane sleep 4,5 "bash handoff/run_sleep.sh && \
  for s in 0 1 2; do CUDA_VISIBLE_DEVICES=\$((4 + s % 2)) $L/.venv/bin/python nsrr_sft.py --seed \$s --words $W/outputs/words --out $W/outputs/sft_s\$s & done; wait"

# Summary writer: polls every 10 min, rewrites results/SUMMARY.md -----------
tmux kill-session -t summary 2>/dev/null || true
tmux new -d -s summary "while true; do bash handoff/summarize.sh > $RES/SUMMARY.md 2>/dev/null; sleep 600; done"

echo
echo "All lanes launched. Sleep. In the morning:"
echo "  cat $RES/SUMMARY.md          # one-page verdict per lane: STRONG / WEAK / FAILED + the numbers"
echo "  tmux ls; tail -50 $LOG/<lane>.log"
echo "Rerun this script to resume any lane that died. Nothing restarts from scratch."
