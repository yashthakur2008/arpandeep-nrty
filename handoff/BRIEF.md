---
title: "Loki → two NeurIPS 2026 workshop papers: handoff brief"
date: "Sept 4, 2026 · deadline Sun Sep 6, 04:59 PDT (Sept 5 AoE)"
geometry: margin=0.55in
documentclass: extarticle
fontsize: 9pt
colorlinks: true
header-includes:
  - \usepackage{booktabs}
  - \usepackage{titlesec}
  - \titlespacing*{\section}{0pt}{8pt}{3pt}
  - \titlespacing*{\subsection}{0pt}{6pt}{2pt}
  - \setlength{\parskip}{3pt}
---

# TL;DR

The Loki repo (GRPO-trained "misdirection" red-teaming of LLMs) can ship **two** NeurIPS 2026 workshop submissions by **Sun Sep 6, 04:59 PDT**. All planning, citations, environment code, and a RunPod handoff package are pushed. Remaining work is: rent the box, run four scripts, implement two small files, and write the prose. Budget is not a constraint (~$1-2k available). Compute was never the bottleneck; **human writing (~8 h per paper) is.**

| | **AgentWild** (priority) | **BrainBodyFM** (stretch) |
|---|---|---|
| Workshop | Agents in the Wild: Safety, Security, and Beyond | Foundation Models for the Brain and Body |
| Track / length | Short, 4 pp | 5 pp, mandatory workshop style |
| Branch | `agentwild-pivot` (+ `aw-env`, `aw-paper`) | `sleep-pivot` (+ `sleep-paper`) |
| Loki reuse | ~95%: misdirection prompt used verbatim | ~90% infra, new data (NSRR SHHS/MESA) |
| P(submittable) | **~0.80** (→ ~0.88 with seeds + bigger targets) | **~0.50** (→ ~0.62 with parallel GPU) |
| P(accept \| submit) | ~0.55 | ~0.40 |
| Blocker | none (GPU + API keys) | NSRR token (validated, works) |

# The two papers in one paragraph each

**AgentWild: "Convincing, not Commanding."** Prompt-injection defenses (instruction strippers, spotlighting, PromptGuard, instruction-hierarchy training) all assume the attacker issues *commands*. Loki's attacker instead writes *fabricated authority* (fake statutes, reports, retractions) into a tool result, so the agent completes the user's task but with the attacker's wrong answer or action, and no monitor sees an off-task step. We frame this as *illusioning* (Wu et al.) vs *goal misdirection*, control channel vs evidence channel, plus the Verification Boundary (Poisoned Playbooks). One table: payload families (hijack / template fabricated-authority / GPT zero-shot / PoisonedRAG / Loki GRPO / Loki GRPO + verifiability reward) × six defenses. Prediction: hijack collapses under instruction defenses, fabricated authority stays flat until a refuter column. Must cite organizer papers AgentPoison and AdvWeb in paragraph one.

**BrainBodyFM: "Sleep as a language."** A symbolic tokenizer turns each 30 s polysomnography epoch into a ~40-char ASCII word (per-night-quantile bandpowers, slow-wave fraction, spindles, REM count, EMG tone, SpO2 min/desat, time-of-night) that the *unchanged* Qwen tokenizer reads. SFT a 0.5-1.5B Qwen stager on SHHS, evaluate zero-shot on MESA, with a mandatory logistic-regression / LightGBM / random-init ablation on identical words (the reviewer's "is the LLM decorative?" test). Then Loki's GRPO red-teamer edits words under a clinician-specified physiological budget with hard vetoes and a second-scorer test. Comparator: PFTSleep kappa 0.81 SHHS → 0.60 MESA zero-shot.

# What is already done (all pushed to `yashthakur2008/arpandeep-nrty`)

- **Plans**: `plan/PLAN.md` on each branch. Design, transfer map, agent DAG, hour-by-hour timeline, kill-switches, drop order, odds. Produced via 5-frame divergent ideation + a 3-seat critic council (hostile reviewer, ML engineer, domain expert) per paper.
- **Bibliographies**: `plan/BIBLIOGRAPHY.md` on each branch. AgentWild 36+11 papers / 50 BibTeX; sleep 30+19 / 49 BibTeX. Every entry has a Relevance line and Cite-in tag. All arXiv ids verified.
- **AgentWild environment** (`aw-env`): single-call research-agent env from HotpotQA, 10 declarative fabricated-authority templates, imperative stripper (all templates pass, hijack fails), resumable results table. Stub-tested end to end.
- **NSRR data access**: token validated against sleepdata.org (5,793 SHHS1 EDFs listed, download confirmed). Note: the `nsrr` gem needs a TTY; the scripts use the HTTP API instead.
- **Handoff package** (`handoff/`): `HANDOFF.md` (entry point), `RUNPOD.md`, `bootstrap.sh` (idempotent, dry-run tested), `run_agentwild.sh`, `run_sleep.sh`, `.env.example`, `CHAT_EXPORT.md`, `PROMPT_FOR_YASH.md`.
- **GitHub issues** #3-#7, each tied to a branch, each with the exact spec.

# What is left (issue map)

| # | Node | Branch | Needs | Est. |
|---|---|---|---|---|
| 3 | AgentWild 4-pp paper skeleton (NeurIPS style, related work from bib) | `aw-paper` | opus agent, no GPU | 1 h |
| 4 | GRPO attacker: copy `harmbench_trainer.py` → `illusion_trainer.py`, `reward_function.py` → `illusion_reward.py`, add detect + refute terms | `aw-env` | GPU | 1 h code + 4-6 h run ×2 |
| 5 | Real targets (`VLLMTarget`, `OpenAITarget` are 1-call shells) + defense table harness (6 defenses) + AgentDojo eval | `aw-env` | GPU + API keys | 3 h |
| 7 | Sleep: `nsrr_load.py` + `psg_words.py`, LR-on-words gate | `sleep-pivot` | CPU | 3 h |
| 6 | Compute plan / odds / go-order (reference) | both | | |
| | **Paper writing, both** | | **human** | **~8 h each** |

# RunPod setup (5 minutes)

1. `git clone https://github.com/yashthakur2008/arpandeep-nrty && cd arpandeep-nrty && git checkout agentwild-pivot`
2. Read `handoff/HANDOFF.md`.
3. RunPod: **4× H100 80GB** (was 2×; budget now allows parallel + seeds), image `runpod/pytorch:2.6-py3.12-cuda-12.1`, 200 GB volume at `/workspace`, expose 8000 + 22.
4. `cp handoff/.env.example handoff/.env`, fill `NSRR_TOKEN`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `WANDB_API_KEY`. Never commit `.env`.
5. `bash handoff/bootstrap.sh` → `bash handoff/run_agentwild.sh` (tmux pane 1) and `bash handoff/run_sleep.sh` (pane 2). Each script prints its next step and stops loudly at the issue number for any file not yet written.

# With the bigger budget, change these (ranked by value)

1. **Frontier targets.** Attack Qwen2.5-72B / Llama-3.1-70B locally and GPT-4o / Claude Sonnet 4.5 / Gemini 2.5 Pro via API. Moves the transfer table from appendix to headline. ~$300-500 API.
2. **3 GRPO seeds** per attacker variant. Entropy collapse is the top risk; seeds make it non-fatal and give mean ± std.
3. **4 GPUs, both papers in parallel.** GPU0-1 AgentWild target + attacker, GPU2 sleep, GPU3 seeds/spare. Sleep becomes a real attempt.
4. **Bigger sleep stager** (1.5-3B, 500 SHHS nights instead of 200).
5. **PromptArmor + Firewalls as real defense columns** (organizer paper and the paper most likely cited against us).
6. **A second human writer.** Highest-EV spend of all. Two papers need ~16 h of rewriting in ~30 h.

Do **not** go past 4 GPUs (idle), add experiments (scope creep), or touch the kill-switches.

# Rules

- **NeurIPS 2026 LLM policy: prose must be primarily human-authored.** Agents draft; a human rewrites every paragraph.
- Any coding agents: `claude-opus-4-8`. No fable-5-1 this week (owner instruction).
- AgentWild first. Sleep go/no-go at its hour-3 LR-on-words gate.
- Safe internal target: **Sat Sep 5, 23:00 PDT**. The last 6 h are for submission, not experiments.
- Double-blind: anonymize the paper *and* any linked code.

*Full history: `handoff/CHAT_EXPORT.md`. Questions: the plan files answer most of them; the council reviews (`plan/council_*.md`) answer the rest.*
