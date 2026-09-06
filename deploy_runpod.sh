#!/usr/bin/env bash
# RunPod helper for Loki experiments.
#
# This script is intentionally non-interactive. It creates a pod and prints the
# exact commands for reproducing the current Loki package workflows. It does not
# reference the removed training/ directory.

set -euo pipefail

CONFIG_FILE=${CONFIG_FILE:-runpod_config.yaml}
POD_NAME=${POD_NAME:-loki-runpod-$(date +%s)}

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing $CONFIG_FILE" >&2
  exit 1
fi

if [[ -z "${RUNPOD_API_KEY:-}" ]]; then
  echo "RUNPOD_API_KEY is required" >&2
  exit 1
fi

require runpodctl
require python
require jq

GPU_TYPE=$(python - <<'PY'
import yaml
c=yaml.safe_load(open('runpod_config.yaml'))
print(c['runpod']['gpu_type'])
PY
)
IMAGE=$(python - <<'PY'
import yaml
c=yaml.safe_load(open('runpod_config.yaml'))
print(c['runpod']['docker_image'])
PY
)
MEMORY_GB=$(python - <<'PY'
import yaml
c=yaml.safe_load(open('runpod_config.yaml'))
print(c['runpod']['memory_gb'])
PY
)
STORAGE_GB=$(python - <<'PY'
import yaml
c=yaml.safe_load(open('runpod_config.yaml'))
print(c['runpod']['storage_gb'])
PY
)
CONTAINER_DISK_GB=$(python - <<'PY'
import yaml
c=yaml.safe_load(open('runpod_config.yaml'))
print(c['runpod']['container_disk_size'])
PY
)

ENV_ARGS=(
  --env "WANDB_PROJECT=loki-runpod"
  --env "CUDA_VISIBLE_DEVICES=0"
  --env "TOKENIZERS_PARALLELISM=false"
  --env "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512"
)
[[ -n "${OPENAI_API_KEY:-}" ]] && ENV_ARGS+=(--env "OPENAI_API_KEY=$OPENAI_API_KEY")
[[ -n "${ANTHROPIC_API_KEY:-}" ]] && ENV_ARGS+=(--env "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY")
[[ -n "${WANDB_API_KEY:-}" ]] && ENV_ARGS+=(--env "WANDB_API_KEY=$WANDB_API_KEY")

echo "Creating RunPod pod: $POD_NAME"
POD_JSON=$(runpodctl create pod \
  --gpuType "$GPU_TYPE" \
  --imageName "$IMAGE" \
  --name "$POD_NAME" \
  --ports "8888:http,22:tcp,6006:tcp" \
  --containerDiskSize "$CONTAINER_DISK_GB" \
  --volumeSize "$STORAGE_GB" \
  --mem "$MEMORY_GB" \
  --startSSH \
  "${ENV_ARGS[@]}" \
  --output json)

POD_ID=$(printf '%s' "$POD_JSON" | jq -r '.id // empty')
if [[ -z "$POD_ID" ]]; then
  echo "Pod creation did not return an id" >&2
  printf '%s\n' "$POD_JSON" >&2
  exit 1
fi

printf '%s\n' "$POD_ID" > .runpod_pod_id

echo "Pod created: $POD_ID"
echo
echo "Run on the pod after cloning this repo:"
cat <<'EOF'
cd /workspace/arpandeep-nrty
python -m pip install -U pip
python -m pip install -e ".[openai,anthropic,ollama]"
python -m pytest -q
python -m loki.agentic.sweep --targets gpt-4o-mini claude-haiku-4-5 \
  --policies strict_hatch strict exemption autonomous bare --trials 3
python -m loki.agentic.gap --targets gpt-4o-mini claude-haiku-4-5 \
  --policies strict autonomous exemption --attacks none combined superseded --trials 3
loki-train --reward-backend ollama --split train --num-samples 100
EOF

echo
echo "Stop the pod when finished: runpodctl stop pod $POD_ID"
