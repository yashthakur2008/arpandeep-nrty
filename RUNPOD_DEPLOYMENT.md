# RunPod Deployment Notes

This file replaces the stale pre-refactor instructions that referenced the removed `training/` directory.

## Current status
RunPod is optional for the AIWILD submission. The hosted-agentic experiments use OpenAI/Anthropic APIs and the local text-validation path can run on a laptop. Use RunPod only for larger follow-up experiments, such as RL-trained attackers or larger open models.

## Prerequisites

```bash
export RUNPOD_API_KEY=...
export OPENAI_API_KEY=...        # only if running hosted targets
export ANTHROPIC_API_KEY=...     # only if running Claude target
export WANDB_API_KEY=...         # optional
```

Install `runpodctl` and `jq` locally before using `deploy_runpod.sh`.

## Create a pod

Dry-run and inspect commands:

```bash
python setup_runpod.py
```

Create via Python helper:

```bash
python setup_runpod.py --create
```

Or create via shell helper:

```bash
./deploy_runpod.sh
```

## Run the current package workflow on the pod

```bash
cd /workspace/arpandeep-nrty
python -m pip install -U pip
python -m pip install -e ".[openai,anthropic,ollama]"
python -m pytest -q
```

Main agentic sweep:

```bash
python -m loki.agentic.sweep --targets gpt-4o-mini claude-haiku-4-5 \
  --policies strict_hatch strict exemption autonomous bare --trials 3
```

Text/tool gap:

```bash
python -m loki.agentic.gap --targets gpt-4o-mini claude-haiku-4-5 \
  --policies strict autonomous exemption --attacks none combined superseded --trials 3
```

Legacy text-attack training, retained as supporting negative-control infrastructure:

```bash
loki-train --reward-backend ollama --split train --num-samples 100
```

## Cost note
Stop pods when done:

```bash
runpodctl stop pod <pod-id>
```
