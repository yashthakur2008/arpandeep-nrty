# Paste this into a Claude agent that has the RunPod MCP (or SSH to a pod)

You are setting up a RunPod box and starting two ML runs for a NeurIPS 2026 workshop deadline (Sun Sep 6, 04:59 PDT). Do exactly this, in order, and stop at any red check.

## 1. Provision (RunPod MCP or console)
- GPU: 4x H100 80GB SXM (2x is the minimum; 4x lets both papers run in parallel).
- Image: `runpod/pytorch:2.6-py3.12-cuda-12.1`
- Container disk 50 GB. Network volume 200 GB mounted at `/workspace`.
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

## 4. Start the runs in two tmux panes
```bash
tmux new -d -s aw 'bash handoff/run_agentwild.sh 2>&1 | tee /workspace/logs/aw.log'
tmux new -d -s sl 'bash handoff/run_sleep.sh 2>&1 | tee /workspace/logs/sl.log'
```
- `run_agentwild.sh`: serves the target on GPU0, runs the H2 gate (prints PASS / LOW / HIGH with the next model size), then GRPO.
- `run_sleep.sh`: downloads 220 SHHS + 70 MESA nights (~25 GB) with resume.
- Both will STOP LOUDLY with `!! <file> does not exist. Implement per issue #N` for files not yet written. That is expected. Read the issue, implement, rerun. Before the GRPO step: `git pull` on `aw-env`, a hardening pass lands `handoff/HARDENING_AGENTWILD.md` with the reward v2 spec.

## 5. Report back
Paste the last 30 lines of each log and the H2 gate verdict.

## Rules
- Coding agents: claude-opus-4-8. Do not use fable-5-1.
- Never print secrets. Never commit `.env`.
- Do not start a >1h run without its 20-step smoke test having printed a non-flat reward.
