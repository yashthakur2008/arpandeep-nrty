# START: paste this whole file into Claude (with the RunPod MCP) and say "go"

You are setting up one RunPod pod and launching a fully automated overnight research run. The human (Yash) will answer four questions, then you do everything else. Do not start any step until you have every key. Never print a key back. Never commit a key.

## Step 1. Ask Yash for exactly these, one message, all at once

1. **RUNPOD_API_KEY** (runpod.io > Settings > API Keys). Needed to create the pod via MCP/API.
2. **OPENAI_API_KEY** (platform.openai.com). Used for the gpt-4o target and the gpt-4o-mini guardrail. Expect ~$50-100 of usage.
3. **ANTHROPIC_API_KEY** (console.anthropic.com). Used for the claude-sonnet-4-5 target. Expect ~$50-100.
4. **NSRR_TOKEN** (sleepdata.org/token). Aayu already validated one; Yash pastes it or gets his own.
5. Optional: **WANDB_API_KEY** (wandb.ai) for training curves. Skip if he does not have one; the run works without it.
6. Optional: **HF_TOKEN** (huggingface.co) speeds model downloads. Skip if absent.

Wait for all four required values before continuing.

## Step 2. Create the pod (RunPod MCP, or console if MCP unavailable)

- GPU: **6x H100 80GB SXM** (8x also fine). Do not go below 6.
- Template image: `runpod/pytorch:2.6-py3.12-cuda-12.1`
- Container disk: 50 GB
- **Network volume: 1 TB**, mount path `/workspace`
- Expose: TCP 22, HTTP 8000
- Do not set `CUDA_VISIBLE_DEVICES` in the template; scripts set it per lane.
- Wait until the pod shows RUNNING and SSH is reachable. Record the SSH host/port.

## Step 3. On the pod, clone and place secrets

```bash
cd /workspace
git clone https://github.com/yashthakur2008/arpandeep-nrty loki && cd loki
git fetch origin && git checkout agentwild-pivot && git pull
cp handoff/.env.example handoff/.env
```
Write the keys into `handoff/.env` (one `KEY=value` per line). Confirm `git status` does NOT list `handoff/.env` (it is gitignored). If it does, stop and report.

## Step 4. Bootstrap (idempotent)

```bash
bash handoff/bootstrap.sh
```
Expect 6 green checks. It installs the venv + vllm + agentdojo + pyedflib/yasa, the nsrr gem, writes `~/.nsrr_token`, pre-downloads Qwen models, runs the env selfcheck. Any red line: paste it to Yash and stop.

## Step 5. Launch everything, one command

```bash
bash handoff/run_all.sh
```
Two tmux lanes start:
- `agentwild`: template experiment on GPT-4o + Claude under none/PromptArmor/refuter (API only, the headline number) -> gate -> 72B vLLM on GPU0-1 -> GRPO x3 seeds on GPU2. **It stops cleanly after the gate** with `illusion_trainer.py does not exist. Implement per issue #4`. That is expected; a human writes that file Saturday morning and reruns this same command.
- `sleep`: 630 GB NSRR download -> loader -> LR gate -> SFT x3 on GPU4-5.
- `summary`: rewrites `results/SUMMARY.md` every 10 min with STRONG / OK / WEAK.

Confirm with `tmux ls` (3 sessions) and `tail -5 /workspace/logs/agentwild.log /workspace/logs/sleep.log`.

## Step 6. Report to Yash and stop

Send him: the SSH host, `tmux ls` output, the last 5 lines of each log, and this line: "Read `/workspace/loki/results/SUMMARY.md` in the morning. Rerun `bash handoff/run_all.sh` to resume any lane. Nothing restarts from scratch."

## Rules
- Never echo secrets. Never `git add handoff/.env`.
- Do not modify any script. If one fails, report the exact error; do not patch around it.
- Do not launch any other GPU job on this pod.
- If you spawn sub-agents for anything: claude-opus-4-8 only.

## Reference
Full context: `handoff/HANDOFF.md`, `handoff/BRIEF.pdf`, pinned issue #8. Remaining human work: issue #4 (attacker trainer, Saturday morning), then paper writing.
