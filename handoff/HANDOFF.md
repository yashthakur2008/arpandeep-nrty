# HANDOFF: two NeurIPS 2026 workshop runs on one RunPod box

## 0. TL;DR

1. Two papers, one deadline: **Sun Sep 6 04:59 PDT**. AgentWild first (P(submit) ~0.80), Sleep second (~0.50).
2. Box: 2x H100 80GB on RunPod. Settings in `handoff/RUNPOD.md`. ~15-20 GPU-hours total.
3. Setup: fill `handoff/.env`, then `bash handoff/bootstrap.sh`. Idempotent, rerun freely.
4. Run: `bash handoff/run_agentwild.sh` (GPUs) and `bash handoff/run_sleep.sh` (CPU download) in two tmux panes.
5. Two scripts will stop with `!! ... does not exist. Implement per issue #4` (and sleep N1/N3). That is on purpose. Code those, rerun.
6. **LLM policy (NeurIPS 2026): prose must be primarily human-authored. Agents draft, humans rewrite every paragraph.** Budget 8 h of human writing per paper. Compute is not the bottleneck, writing is.

## 1. Deadline

- Both workshops: **Sept 5 AoE = Sun Sep 6 04:59 PDT**. Safe target: **Sat Sep 5 23:00 PDT**.
- Hours left: `python3 -c "import datetime as d,zoneinfo as z; print((d.datetime(2026,9,6,4,59,tzinfo=z.ZoneInfo('America/Los_Angeles'))-d.datetime.now(z.ZoneInfo('America/Los_Angeles'))).total_seconds()/3600)"`
- Any agent Yash spawns for code: `claude-opus-4-8`. No fable (owner instruction 2026-09-04).

## 2. What exists, per branch

| Branch | Has | State |
|---|---|---|
| `agentwild-pivot` | `plan/PLAN.md`, `plan/BIBLIOGRAPHY.md` (50 BibTeX), council reviews, `handoff/` (this) | plan final |
| `aw-env` | `env/research_env.py`, `payloads.py`, `strip.py`, `run_table.py`. Cases rebuild into `data/research_cases_validation_0_500.jsonl` (gitignored) on first run, ~5 min HotpotQA download | stub-tested. `VLLMTarget`/`OpenAITarget` are `NotImplementedError` shells (issue #5) |
| `aw-paper` | nothing yet (branch exists) | paper skeleton not written (issue #3, opus) |
| `sleep-pivot` | `plan/PLAN.md`, `plan/BIBLIOGRAPHY.md` (49 BibTeX), clinician/engineer/reviewer council | plan final, zero code |
| `sleep-paper` | `paper/neurips_2026.sty` + `refs.bib` only, no main.tex | skeleton not written |
| `main` | original Loki: `training/harmbench_trainer.py`, `training/reward_function.py`, `scripts/hotpotqa.py`, `Dockerfile.runpod` | unchanged |

Missing and NOT stubbed: `training/illusion_trainer.py`, `training/illusion_reward.py` (issue #4), `nsrr_load.py`, `psg_words.py` (sleep-pivot PLAN.md N1/N3).

## 3. RunPod

See `handoff/RUNPOD.md` (10 lines). Summary: `2x H100 80GB SXM`, image `runpod/pytorch:2.6-py3.12-cuda-12.1`, 50 GB container, 200 GB volume at `/workspace`, ports 22 + 8000.

GPU map. Scripts set `CUDA_VISIBLE_DEVICES` per process. Never set it globally.

| GPU | Job |
|---|---|
| 0 | vLLM target Qwen2.5-7B-Instruct at 35% memory, then GRPO run B3 |
| 1 | GRPO run B4, then sleep SFT/GRPO after B4 finishes |

## 4. Commands, in order

```bash
git clone -b agentwild-pivot https://github.com/yashthakur2008/arpandeep-nrty.git /workspace/loki
cd /workspace/loki && cp handoff/.env.example handoff/.env && nano handoff/.env
bash handoff/bootstrap.sh
```
bootstrap: ~15 min first run (models ~18 GB). Ends with a green/red summary. Rerun until all green. Checks out `aw-env` and overlays `handoff/` from `agentwild-pivot`.

```bash
tmux new -s aw
cd /workspace/loki && bash handoff/run_agentwild.sh
```
| Stage | Wall | Kill switch |
|---|---|---|
| vLLM up + health | 3 min | `pkill -f "vllm serve"` |
| H2 gate: `env.run_table --target vllm --n 200` | 10 min | script exits itself. LOW: rerun with `TARGET_MODEL=Qwen/Qwen2.5-3B-Instruct`. HIGH: `Qwen/Qwen2.5-14B-Instruct` |
| GRPO smoke, 20 steps, B3 + B4 in parallel | 20-25 min | script kills itself if > 180 s/step. Fallback: `num_generations 4` or gpt-4o-mini reward target |
| GRPO full, 300 steps each | 4-6 h | `pkill -f illusion_trainer`, checkpoints in `/workspace/outputs/` |

Stops with `!! training/illusion_trainer.py does not exist` until issue #4 is done. Expected.

```bash
tmux new -s sleep
cd /workspace/loki && bash handoff/run_sleep.sh
```
| Stage | Wall | Kill switch |
|---|---|---|
| Download 220 SHHS1 (~9 GB) + 70 MESA (~15 GB) EDF + XML, 8 parallel | 1-3 h | `pkill -f "curl -sfL -C"`, rerun resumes |
| `nsrr_load.py`, `psg_words.py` | 30 min | stops with `!! nsrr_load.py does not exist` until written |

Both scripts log to `/workspace/logs/<script>.log` and print their own NEXT line.

## 5. Where results land, what "done" looks like

| Node | Output | Done when |
|---|---|---|
| H2 gate | `/workspace/logs/gate_Qwen2.5-7B-Instruct.txt`, `results/vllm_*_table.jsonl` | some `B0_*` row ASR in [0.15, 0.40], A1 flag ~1.0, B0 flag ~0 |
| GRPO B3/B4 | `/workspace/outputs/B3_300`, `B4_300`, wandb project `loki-agentwild` | reward curve rises, 500 sampled payloads in `results/`, B4 refuted-fraction falls over training |
| Table 1 | `results/*.csv` from `eval/defense_table.py` (issue #5) | A1 ASR under stripper < 5%; B rows flat under stripper/spotlight/PG; B4 flat under refuter |
| NSRR | `/workspace/nsrr/{shhs,mesa}/polysomnography/...` | `find /workspace/nsrr -name '*.edf' | wc -l` = 290 |
| Sleep words | `/workspace/outputs/words` | LR on words > 0.5 macro-F1 on one held-out night. This is the sleep go/no-go gate. Below it, sleep paper is dropped |

## 6. Issue map

| Issue | What | Closed by |
|---|---|---|
| #3 | AgentWild 4-page paper skeleton, `aw-paper` | human writing; `paper/main.tex` compiles with Table 1 placeholder |
| #4 | GRPO illusioning attacker: `cp training/reward_function.py training/illusion_reward.py`, `cp training/harmbench_trainer.py training/illusion_trainer.py`. Reward = 1[fooled] - 0.5 PG2 - 0.5 1[refuted] + format gate + 0.2 regulation-token bonus. Qwen2.5-1.5B, bf16, 8-bit Adam, lr 1e-6, beta 0.04, num_generations 8, 8 prompts/step, max_completion 128. CLI contract the script uses: `python -m training.illusion_trainer --run B3|B4 --max_steps N --output_dir DIR` | `run_agentwild.sh` passing the GRPO stages |
| #5 | `VLLMTarget.answer` / `OpenAITarget.answer` (one `chat.completions.create` each) + `eval/defense_table.py` | `run_agentwild.sh` passing the H2 gate, then a Table 1 CSV |
| #6 | compute, P-values, go-order | this file |

Env facts to respect (already built by N0): `StubTarget` takes `cases`; `make_target(name, cases, **kw)`; cases from HotpotQA validation split cached at `data/research_cases_validation_0_500.jsonl`; `render_agent_prompt(case, None)` is row A0.

## 7. Secrets

- `handoff/.env` only. Gitignored (`.env`, `handoff/.env`). Never commit, never paste into the RunPod UI, never echo in logs.
- `NSRR_TOKEN`: from sleepdata.org account page (Aayu's is validated). bootstrap writes it to `~/.nsrr_token` chmod 600.
- `OPENAI_API_KEY`: gpt-4o-mini targets and B1 payloads. Cap $200 total.
- `ANTHROPIC_API_KEY`: Haiku 4.5 transfer row (appendix, optional).
- `WANDB_API_KEY`: GRPO curves. `HF_TOKEN`: model download (Qwen is public, token only avoids rate limits).

## 8. If something fails

Drop order, AgentWild (PLAN.md sec 6): defense probe -> AgentDojo eval -> appendix histogram -> third API target -> RL rows. Template-only illusioning vs hijack under defenses is still a paper.

Drop order, Sleep (sleep-pivot PLAN.md): YASA symbols -> adversarial retraining -> attacker MESA transfer -> attacker entirely -> MESA (SHHS-only tokenizer study). Sleep drops entirely if LR-on-words gate fails or if AgentWild needs the human hours.

Specific failures:
- Gate LOW/HIGH twice: freeze on 7B anyway, report the ASR, RL becomes an upgrade row not the title.
- Step > 180 s after smoke: `num_generations 4`, or reward target gpt-4o-mini with 32 async calls.
- RL does not beat B0/B1 by H12: RL leaves the title. Paper = "templates suffice, defenses are structurally blind".
- NSRR download stalls: rerun `run_sleep.sh`, `curl -C -` resumes. Lower `N_SHHS=100 N_MESA=30` if past hour 3.
- vLLM OOM: `--gpu-memory-utilization 0.35` shares GPU0 with B3. If B3 OOMs, run B3 after B4 on GPU1 instead.

## 9. Links

- AgentWild plan: `plan/PLAN.md` (this branch). Bib: `plan/BIBLIOGRAPHY.md`. Council: `plan/council_reviewer.md`, `council_engineer.md`, `council_threat.md`.
- Sleep plan: `git show sleep-pivot:plan/PLAN.md`. Bib: `git show sleep-pivot:plan/BIBLIOGRAPHY.md`. Council: `council_clinician.md`, `council_engineer.md`, `council_reviewer.md` on `sleep-pivot`.
- Chat that produced all of this: `handoff/CHAT_EXPORT.md`.
- Issues: https://github.com/yashthakur2008/arpandeep-nrty/issues (3, 4, 5, 6).
- Venues: https://agentwild-workshop.github.io/neurips2026 (OpenReview `NeurIPS.cc/2026/Workshop/AIWILD`), BrainBodyFM CFP linked from sleep-pivot PLAN.md sec 0.
