# Final Public-Interface Acceptance Validation

This is the final validation pass for the submission artifacts through public interfaces and integration boundaries.

## Public interfaces exercised

- Installed console scripts:
  - `loki-train --help`
  - `loki-eval --help`
- Module CLIs:
  - `python -m loki.agentic.sweep --help`
  - `python -m loki.agentic.gap --help`
  - `python -m loki.agentic.adaptive --help`
  - `python -m loki.judge_study --help`
  - `python -m loki.aggregate --help`
  - `python -m loki.label_sheet --help`
- Package boundary:
  - `uv build`
  - install built wheel into an isolated venv
  - import `loki` and `loki.agentic` from the wheel
- Paper acceptance path:
  - compile `paper/main.tex`
  - compile `paper/extended.tex`
  - read PDF page counts from generated PDFs
- RunPod integration boundary:
  - `python setup_runpod.py` dry run
  - verify output creates a **Pod**, not Serverless
  - verify output includes SSH startup via `--startSSH`
  - verify output emits current `loki` package commands

## Observed results

- Console scripts: passed.
- Module CLIs: passed.
- Wheel build/install/import: passed. Isolated wheel import reports 8 scenarios and 7 attacks.
- Short paper compile: passed, 4 pages.
- Extended paper compile: passed, 7 pages.
- RunPod dry-run: passed. It emits `runpodctl create pod`, `--startSSH`, `python -m loki.agentic.sweep`, `python -m loki.agentic.gap`, and `loki-train`.

## Acceptance constraint

Real `setup_runpod.py --create` was not run because it would create paid infrastructure. This is intentionally recorded as externally blocked rather than claimed as verified. The dry-run verifies the command shape and confirms the workflow uses RunPod Pods with SSH, which matches the project requirement for long-running GRPO/checkpoint workloads.
