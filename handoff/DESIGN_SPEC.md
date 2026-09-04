# Handoff design spec (written by coordinator, fable-5-1). Opus builds from this.

## Audience
Yash. Has repo write access, will spin up RunPod with 2x H100 80GB. Wants to type as few commands as possible. Has NOT read any of the plans. Assume 5 minutes of attention before he starts copying commands.

## Deliverables (all on branch `agentwild-pivot`, dir `handoff/`, then merged into `sleep-pivot` too)
1. `handoff/HANDOFF.md`: the single entry point. Order: (0) TL;DR 6 lines, (1) deadline in PDT with countdown formula, (2) what exists per branch (table), (3) RunPod setup: exact template/image, disk, ports, env vars, which 2 GPUs do what, (4) `bash handoff/bootstrap.sh` then the 4 run commands in order with expected wall-clock and the kill-switch for each, (5) where results land and what "done" looks like per node, (6) issue map (#3-#6) with which command closes which issue, (7) secrets: what to set and where (NEVER commit; `.env` is gitignored), (8) fallback if anything fails (drop order from PLAN.md sec 6), (9) links: both PLAN.md, both BIBLIOGRAPHY.md, council reviews, chat export.
2. `handoff/bootstrap.sh`: idempotent. Clones/updates repo, checks out `aw-env` into `/workspace/loki`, creates venv with `uv`, installs `requirements_runpod.txt` + `vllm` + `agentdojo` + `pyedflib mne yasa`, installs `nsrr` gem, reads `.env`, writes `~/.nsrr_token` from `NSRR_TOKEN`, pre-downloads Qwen2.5-7B-Instruct and Qwen2.5-1.5B-Instruct to HF cache, runs `python -m env.strip` and `python -m env.run_table --target stub --n 20` as a smoke test, prints a green/red summary. Must be safe to re-run.
3. `handoff/run_agentwild.sh`: GPU0 = `vllm serve Qwen/Qwen2.5-7B-Instruct --gpu-memory-utilization 0.35 --port 8000` in background + wait for /health; then `python -m env.run_table --target vllm --n 200` (this is the H2 gate: prints template ASR; script prints PASS if any B0 template ASR in [0.15,0.40], else prints which target size to try next). Then, gated on PASS, GRPO smoke `--max_steps 20` for run B3 on GPU0 and B4 on GPU1, then full 300-step runs. Note: `training/illusion_trainer.py` and `training/illusion_reward.py` DO NOT EXIST YET (issue #4). The script must call them and fail loudly with "implement per issue #4" if missing. Do not stub them.
4. `handoff/run_sleep.sh`: NSRR download via HTTP API (gem needs TTY): loop over `https://sleepdata.org/datasets/{ds}/files/m/browser/{path}?auth_token=$NSRR_TOKEN` for SHHS1 edfs matching `shhs1-20[0-1][0-9]{3}\.edf` (~220) + `annotations-events-nsrr/shhs1` XMLs, and MESA `mesa-sleep-00[0-6][0-9]{2}\.edf` (~70) + XMLs, with `curl -C -` resume, 8 parallel via xargs, to `/workspace/nsrr/`. Then note that `nsrr_load.py` and `psg_words.py` do not exist yet (sleep-pivot PLAN.md nodes N1/N3) and fail loudly. Listing endpoint that works: `https://sleepdata.org/api/v1/datasets/{ds}/files.json?auth_token=TOKEN&path=polysomnography/edfs/shhs1` (verified 5793 entries). Download endpoint verified: `https://sleepdata.org/datasets/shhs/files/m/browser/{full_path}?auth_token=TOKEN` returns 200 + bytes.
5. `handoff/.env.example`: NSRR_TOKEN=, OPENAI_API_KEY=, ANTHROPIC_API_KEY=, WANDB_API_KEY=, HF_TOKEN=. Add `.env` and `handoff/.env` to `.gitignore`.
6. `handoff/CHAT_EXPORT.md`: coordinator will paste this in; leave a placeholder header.
7. `handoff/RUNPOD.md`: 10 lines: pick "2x H100 80GB SXM", image `runpod/pytorch:2.6-py3.12-cuda-12.1` (matches Dockerfile.runpod), container disk 50GB, volume 200GB mounted at /workspace, expose 8000 (vllm) + 22, env vars from .env, set `CUDA_VISIBLE_DEVICES` per script not globally.

## Hard facts to embed (do not re-derive)
- Deadline both workshops: Sept 5 AoE = Sun Sep 6 04:59 PDT. Safe target Sat Sep 5 23:00 PDT.
- Compute: ~15-20 GPU-hours real work; 2 GPUs is right-sized; GPU0 AgentWild B3 + target, GPU1 AgentWild B4; sleep SFT/GRPO share GPU1 after B4 or wait.
- P(submittable): AgentWild ~0.80, Sleep ~0.50. Go-order: AgentWild first. Sleep go/no-go at LR-on-words gate.
- GRPO numbers (from plan): Qwen2.5-1.5B, bf16, 8-bit Adam, lr 1e-6, beta 0.04, num_generations 8, 8 prompts/step, max_completion 128, 300 steps, ~50-70s/step. Kill if step > 3 min after 20-step smoke.
- Env spec changes already made by N0 (respect them): StubTarget takes cases; `make_target(name, cases, **kw)`; cases from HotpotQA validation split, cached at `data/research_cases_validation_0_500.jsonl`; `render_agent_prompt(case, None)` = A0.
- Existing Loki files to copy for issue #4: `training/reward_function.py` -> `training/illusion_reward.py`, `training/harmbench_trainer.py` -> `training/illusion_trainer.py`.
- LLM policy: prose must be primarily human-authored. Agents draft, humans rewrite. Say this once, prominently.
- Model routing for any agents Yash spawns: opus-4-8 for code, no fable (owner instruction 2026-09-04).

## Style
Caveman-terse in HANDOFF.md headers and bullets, full sentences in any warning. No em dashes. Every command copy-pasteable as-is. Every script `set -euo pipefail`, logs to `/workspace/logs/<script>.log`, prints its own next step at the end.
