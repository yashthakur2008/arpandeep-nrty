# Paste this into a Claude agent that has the RunPod MCP (or SSH to a pod)

You are setting up a RunPod box and starting two ML runs for a NeurIPS 2026 workshop deadline (Sun Sep 6, 04:59 PDT). Do exactly this, in order, and stop at any red check.

## 1. Provision (RunPod MCP or console)
- GPU: 6x H100 80GB SXM (8x also fine). Lanes: GPU0-1 target, GPU2-3 attacker seeds, GPU4-5 sleep.
- Image: `runpod/pytorch:2.6-py3.12-cuda-12.1`
- Container disk 50 GB. Network volume **1 TB** mounted at `/workspace`. Sleep data is 630 GB at defaults (full SHHS1 + MESA cohorts).
- Expose TCP 22 (ssh) and HTTP 8000 (vllm).
- Do not set CUDA_VISIBLE_DEVICES globally; the scripts set it per process.

## 2. On the pod
```bash
cd /workspace
git clone https://github.com/yashthakur2008/arpandeep-nrty loki && cd loki
git checkout agentwild-pivot && git pull
cp handoff/.env.example handoff/.env
```
Fill `handoff/.env` with: `NSRR_TOKEN`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `WANDB_API_KEY` (HF_TOKEN optional). Never commit this file; it is gitignored.

## 3. Bootstrap (idempotent, rerun freely)
```bash
bash handoff/bootstrap.sh
```
Expect 6 green checks. It creates the venv, installs deps + vllm + agentdojo + pyedflib/yasa, installs the nsrr gem, writes `~/.nsrr_token`, pre-downloads Qwen2.5-7B and 1.5B, and runs the env smoke test. Red = stop and report the line.

## 4. Launch everything (one command, then sleep)
```bash
bash handoff/run_all.sh
```
This launches five tmux lanes: `target` (72B vLLM on GPU0-1), `api` (the headline experiment, API only), `grpo2`/`grpo3` (attacker seeds), `sleep` (630 GB download, loader, LR gate, then SFT x3). Every lane is gated and resumable. A `summary` lane rewrites `results/SUMMARY.md` every 10 min with a STRONG / OK / WEAK verdict.

If `run_all.sh` says a file is missing on `aw-env` or `sleep-paper`, a hardening commit has not landed yet: wait 10 min, `git fetch`, rerun. Rerunning never restarts finished work.

## 5. Report back
Paste `results/SUMMARY.md` and `tmux ls`.

## Rules
- Coding agents: claude-opus-4-8. Do not use fable-5-1.
- Never print secrets. Never commit `.env`.
- Do not start a >1h run without its 20-step smoke test having printed a non-flat reward.
