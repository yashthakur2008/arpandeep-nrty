# Getting Started

The active project is the AIWILD agentic tool-call paper. These instructions replace the old pre-refactor workflow that referenced deleted `training/` scripts.

## Install

```bash
uv sync
python -m pip install -e ".[openai,anthropic,ollama]"
```

## Verify locally

```bash
python -m pytest -q
ruff check .
uv build
```

## Reproduce the short-paper results

Main hosted sweep:

```bash
python -m loki.agentic.sweep --targets gpt-4o-mini claude-haiku-4-5 \
  --policies strict_hatch strict exemption autonomous bare --trials 3
```

Text/tool gap:

```bash
python -m loki.agentic.gap --targets gpt-4o-mini claude-haiku-4-5 \
  --policies strict autonomous exemption --attacks none combined superseded --trials 3
```

Adaptive attacker:

```bash
python -m loki.agentic.adaptive --control-policy exemption --test-policy strict_hatch \
  --rounds 8 --trials 1
```

## Build the paper

```bash
cd paper
tectonic main.tex --reruns 2
tectonic extended.tex --reruns 2
```

## Optional RunPod

RunPod is only needed for larger follow-up work, such as RL-trained attackers or larger open models. See `RUNPOD_DEPLOYMENT.md`.
