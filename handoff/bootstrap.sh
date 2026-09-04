#!/usr/bin/env bash
# bootstrap.sh: one-shot, idempotent RunPod setup for both workshop runs.
# Usage: bash handoff/bootstrap.sh            (real)
#        DRY_RUN=1 WORKSPACE=/tmp/ws bash handoff/bootstrap.sh   (echo pip/curl/git/apt instead of running)
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
LOKI="$WORKSPACE/loki"
VENV="$WORKSPACE/venv"
REPO="${REPO:-https://github.com/yashthakur2008/arpandeep-nrty.git}"
ENV_BRANCH="${ENV_BRANCH:-aw-env}"          # env/ code lives here; switch to aw-attacker once issue #4 lands
HANDOFF_BRANCH="${HANDOFF_BRANCH:-agentwild-pivot}"  # handoff/ scripts live here
export HF_HOME="$WORKSPACE/hf"                # model cache on the persistent volume
mkdir -p "$WORKSPACE/logs" "$HF_HOME" "$WORKSPACE/nsrr" "$WORKSPACE/outputs"
exec > >(tee -a "$WORKSPACE/logs/bootstrap.sh.log") 2>&1
echo "== bootstrap $(date -u +%FT%TZ) WORKSPACE=$WORKSPACE DRY_RUN=${DRY_RUN:-0}"

run() { if [ "${DRY_RUN:-0}" = 1 ]; then echo "[dry] $*"; else "$@"; fi; }
declare -a OK=() BAD=()
check() { if "$@"; then OK+=("$1"); else BAD+=("$1"); fi; }  # never aborts; feeds the summary

# 1. repo -------------------------------------------------------------------
repo() {
  if [ -d "$LOKI/.git" ]; then
    run git -C "$LOKI" fetch -q origin
  else
    run git clone -q "$REPO" "$LOKI"
  fi
  run git -C "$LOKI" checkout -q "$ENV_BRANCH"
  run git -C "$LOKI" reset -q --hard "origin/$ENV_BRANCH"
  # handoff/ is on $HANDOFF_BRANCH, not $ENV_BRANCH: overlay it, unstaged, so `bash handoff/run_*.sh` keeps working
  run git -C "$LOKI" checkout -q "origin/$HANDOFF_BRANCH" -- handoff
  run git -C "$LOKI" reset -q -- handoff
  [ "${DRY_RUN:-0}" = 1 ] || [ -f "$LOKI/env/research_env.py" ]
}
check repo

# 2. secrets ----------------------------------------------------------------
secrets() {
  local envf="$LOKI/handoff/.env"
  [ -f "$envf" ] || envf="$(dirname "${BASH_SOURCE[0]}")/.env"
  if [ ! -f "$envf" ]; then echo "!! no handoff/.env. cp handoff/.env.example handoff/.env and fill it."; return 1; fi
  set -a; . "$envf"; set +a
  local missing=0
  for k in NSRR_TOKEN OPENAI_API_KEY WANDB_API_KEY; do
    [ -n "${!k:-}" ] || { echo "!! $k empty in $envf"; missing=1; }
  done
  [ -n "${HF_TOKEN:-}" ] || echo "warn: HF_TOKEN empty (fine, Qwen is public, downloads may be rate limited)"
  if [ -n "${NSRR_TOKEN:-}" ]; then
    printf '%s\n' "$NSRR_TOKEN" > "$HOME/.nsrr_token"; chmod 600 "$HOME/.nsrr_token"
  fi
  return $missing
}
check secrets

# 3. python -----------------------------------------------------------------
python_env() {
  command -v uv >/dev/null || run bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  [ -x "$VENV/bin/python" ] || run uv venv -q "$VENV" --python 3.12
  # torch and flash-attn pins come from vllm's resolver instead of requirements_runpod.txt (they conflict otherwise)
  local req="$WORKSPACE/logs/requirements.resolved.txt"
  if [ -f "$LOKI/requirements_runpod.txt" ]; then grep -Ev '^(torch|flash-attn)' "$LOKI/requirements_runpod.txt" > "$req"; else : > "$req"; fi
  run uv pip install -q --python "$VENV/bin/python" -r "$req" vllm agentdojo pyedflib mne yasa huggingface_hub
  [ "${DRY_RUN:-0}" = 1 ] || "$VENV/bin/python" -c "import trl, vllm, agentdojo, pyedflib, mne, yasa"
}
check python_env

# 4. nsrr gem (optional: downloads go over HTTP in run_sleep.sh, gem needs a TTY) --
nsrr_gem() {
  command -v gem >/dev/null || run bash -c 'apt-get update -qq && apt-get install -y -qq ruby-full'
  gem list -i nsrr >/dev/null 2>&1 || run gem install -q nsrr
}
check nsrr_gem

# 5. models -----------------------------------------------------------------
models() {
  for m in Qwen/Qwen2.5-7B-Instruct Qwen/Qwen2.5-1.5B-Instruct; do
    run "$VENV/bin/python" -c "from huggingface_hub import snapshot_download; snapshot_download('$m')"
  done
}
check models

# 6. smoke test (env code on $ENV_BRANCH, StubTarget, no GPU) ----------------
smoke() {
  cd "$LOKI" 2>/dev/null || [ "${DRY_RUN:-0}" = 1 ]
  run "$VENV/bin/python" -m env.strip
  run "$VENV/bin/python" -m env.run_table --target stub --n 20
}
check smoke

# summary -------------------------------------------------------------------
G=$'\e[32m'; R=$'\e[31m'; N=$'\e[0m'
echo; echo "== bootstrap summary"
for s in "${OK[@]}";  do echo "${G}OK ${N} $s"; done
for s in "${BAD[@]-}"; do [ -n "$s" ] && echo "${R}FAIL${N} $s (see $WORKSPACE/logs/bootstrap.sh.log)"; done
echo
echo "NEXT: cd $LOKI && bash handoff/run_agentwild.sh     (GPU0+GPU1, AgentWild first)"
echo "      cd $LOKI && bash handoff/run_sleep.sh         (CPU download, safe to start in a 2nd tmux now)"
[ "${#BAD[@]}" -eq 0 ]
