#!/usr/bin/env bash
# run_sleep.sh: NSRR SHHS1 + MESA download over HTTP (nsrr gem needs a TTY), then the loader/tokenizer nodes.
# Usage: cd /workspace/loki && bash handoff/run_sleep.sh      (CPU only, safe alongside run_agentwild.sh)
# Kill:  pkill -f "curl -sfL -C"   (rerun resumes, curl -C - picks up partial files)
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
LOKI="${LOKI:-$WORKSPACE/loki}"
PY="${PY:-$WORKSPACE/venv/bin/python}"
NSRR="$WORKSPACE/nsrr"
N_SHHS="${N_SHHS:-5793}"  # full SHHS1 cohort, ~39 MB each, 228 GB. Override to subset if needed.
N_MESA="${N_MESA:-2056}"  # full MESA cohort, ~196 MB each, 402 GB. Override to subset if needed.
PAR="${PAR:-16}"
mkdir -p "$WORKSPACE/logs" "$NSRR"
exec > >(tee -a "$WORKSPACE/logs/run_sleep.sh.log") 2>&1
echo "== run_sleep $(date -u +%FT%TZ) N_SHHS=$N_SHHS N_MESA=$N_MESA"

cd "$LOKI"
set -a; . handoff/.env; set +a
[ -n "${NSRR_TOKEN:-}" ] || { echo "!! NSRR_TOKEN empty in handoff/.env"; exit 1; }
die() { echo; echo "!! $*"; exit 1; }

# 1. list -------------------------------------------------------------------
# listing endpoint (verified): api/v1/datasets/{ds}/files.json?path=...  -> [{full_path, file_name, file_size, ...}]
list() {  # ds path regex n  -> full_path lines, sorted by id, first n
  curl -sf --retry 3 "https://sleepdata.org/api/v1/datasets/$1/files.json?auth_token=$NSRR_TOKEN&path=$2" \
    | "$PY" -c "import json,sys,re; print('\n'.join(sorted(x['full_path'] for x in json.load(sys.stdin) if re.fullmatch(r'$3', x['file_name']))[:$4]))"
}
Q="$WORKSPACE/logs/nsrr_queue.txt"
{
  list shhs polysomnography/edfs/shhs1 'shhs1-\d{6}\.edf' "$N_SHHS" | sed 's|^|shhs |'
  list shhs polysomnography/annotations-events-nsrr/shhs1 'shhs1-\d{6}-nsrr\.xml' "$N_SHHS" | sed 's|^|shhs |'
  list mesa polysomnography/edfs 'mesa-sleep-\d{4}\.edf' "$N_MESA" | sed 's|^|mesa |'
  list mesa polysomnography/annotations-events-nsrr 'mesa-sleep-\d{4}-nsrr\.xml' "$N_MESA" | sed 's|^|mesa |'
} > "$Q"
echo "queued $(wc -l < "$Q") files -> $NSRR (ds/full_path)"

# 2. download, 8 parallel, resumable ------------------------------------------
# download endpoint (verified 200 + bytes): datasets/{ds}/files/m/browser/{full_path}?auth_token=TOKEN
export NSRR NSRR_TOKEN
xargs -P "$PAR" -n 2 sh -c '
  out="$NSRR/$0/$1"; mkdir -p "$(dirname "$out")"
  curl -sfL -C - --retry 3 -o "$out" "https://sleepdata.org/datasets/$0/files/m/browser/$1?auth_token=$NSRR_TOKEN" \
    && echo "ok  $1" || echo "ERR $1"' < "$Q"
n_err=$(grep -c '^ERR' "$WORKSPACE/logs/run_sleep.sh.log" || true)
echo "download done: $(find "$NSRR" -name '*.edf' | wc -l) edf, $(find "$NSRR" -name '*.xml' | wc -l) xml, $(du -sh "$NSRR" | cut -f1). errors this+past runs: $n_err (rerun to resume)"

# 3. loader + tokenizer (sleep-pivot PLAN.md nodes N1, N3) -------------------
for f in nsrr_load.py psg_words.py; do
  [ -f "$f" ] || die "$f does not exist. Implement per sleep-pivot plan/PLAN.md node $([ "$f" = nsrr_load.py ] && echo N1 || echo N3) (git show sleep-pivot:plan/PLAN.md). No GitHub issue filed yet; file one under the workshop-sleep label. Not stubbing."
done
"$PY" nsrr_load.py --nsrr "$NSRR" --out "$WORKSPACE/outputs/nights"
"$PY" psg_words.py --nights "$WORKSPACE/outputs/nights" --out "$WORKSPACE/outputs/words"

echo
echo "DONE. Words in $WORKSPACE/outputs/words."
echo "NEXT (go/no-go gate): LR on the words must reach > 0.5 macro-F1 on one held-out night (PLAN.md N3 check). If not, tokenizer bug: fix before SFT. Then SFT stager on GPU1 once run_agentwild.sh prints DONE."
