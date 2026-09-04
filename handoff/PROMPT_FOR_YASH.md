# Prompt for Yash (paste into his agent, or read it himself)

You are helping ship two NeurIPS 2026 workshop papers from the repo github.com/yashthakur2008/arpandeep-nrty by **Sun Sep 6, 04:59 PDT** (Sept 5 AoE). Everything is planned and partly built. Your job is to run it on RunPod.

Start here, in order:
1. `git clone https://github.com/yashthakur2008/arpandeep-nrty && cd arpandeep-nrty && git checkout agentwild-pivot`
2. Read `handoff/HANDOFF.md` top to bottom (5 min). It has the RunPod config, the exact commands, and what "done" looks like.
3. Spin up RunPod per `handoff/RUNPOD.md`: 2x H100 80GB, image `runpod/pytorch:2.6-py3.12-cuda-12.1`, 200GB volume at /workspace.
4. Copy `handoff/.env.example` to `handoff/.env`, fill NSRR_TOKEN, OPENAI_API_KEY, ANTHROPIC_API_KEY, WANDB_API_KEY. Never commit `.env`.
5. `bash handoff/bootstrap.sh` then `bash handoff/run_agentwild.sh`. Each script prints its next step.

Context if you want it: `handoff/CHAT_EXPORT.md` (how we got here), `plan/PLAN.md` (the design), `plan/BIBLIOGRAPHY.md` (citations with notes), GitHub issues #3-#6 (remaining work, each tied to a branch).

Rules from the owner:
- AgentWild paper first (branch `agentwild-pivot`, ~0.80 odds). Sleep paper (`sleep-pivot`) is a stretch, go/no-go at its hour-3 gate.
- If you spawn coding agents, use claude-opus-4-8. Do not use fable-5-1 right now.
- The workshop LLM policy requires primarily human-authored prose. Agents draft, a human rewrites every paragraph.
- Two files are not written yet and the scripts will tell you: `training/illusion_trainer.py` + `training/illusion_reward.py` (issue #4, copy from `training/harmbench_trainer.py` and `training/reward_function.py`). Do that before the GRPO step.
- Commit as you go on the branch you are on. Open a PR to `agentwild-pivot` from any work branch.

If something breaks, `handoff/HANDOFF.md` section 8 has the drop order. Do not spend the last 6 hours on new experiments.
