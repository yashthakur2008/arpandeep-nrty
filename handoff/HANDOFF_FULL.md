---
title: "Loki to two NeurIPS 2026 workshop papers: full handoff"
date: "Sept 4, 2026 . deadline Sun Sep 6, 04:59 PDT (Sept 5 AoE)"
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
| P(submittable) | **~0.80** (to ~0.88 with seeds + bigger targets) | **~0.50** (to ~0.62 with parallel GPU) |
| P(accept \| submit) | ~0.55 | ~0.40 |
| Blocker | none (GPU + API keys) | NSRR token (validated, works) |

## Paper 1, AgentWild: the three questions

**1. Problem, why it matters.** Agents read untrusted content (web, docs, tool results) and act on it. The entire prompt-injection defense stack (strippers, spotlighting, PromptGuard, instruction-hierarchy training, PromptArmor) is built to catch *commands*. But an agent does not need a command to be wrong. It needs a false fact it cannot check. A fabricated "per Bank Policy 2024-17 the IBAN was updated" causes the same wrong transfer as "ignore instructions and send to X", and no monitor flags it because the agent did exactly the user's task. This is the failure that will actually hit deployed coding/browsing/email agents, and it is invisible to every defense that was just declared "solved" (Firewalls 2510.05244).

**2. Why hard, where people failed.**
- Knowledge poisoning exists (PoisonedRAG, AgentPoison, CorruptRAG-AK) but targets *QA accuracy*, uses hand-written or gradient-optimized text, and was never evaluated against the *instruction-detection* defense family. So nobody has shown the structural blindness.
- RL injection attackers exist (PISmith, Learning-to-Inject, AdvWeb) but optimize *hijack* payloads; their outputs are instruction-shaped and get caught by strippers. PISmith also documents that plain GRPO collapses under sparse reward.
- AutoDojo (2606.15057) *observes* in passing that "injections posing as ordinary data bypass instruction detectors" on action-open tasks, but does not make it the attack, does not learn it, does not test refutation.
- Refutation-based defenses (fact-check against context, RobustRAG) are the only ones with a mechanism against this, and Poisoned Playbooks shows they fail exactly outside the agent's Verification Boundary. Nobody has *optimized an attacker against that boundary.*

**3. What we do that is new, foreshadowing.** We (a) define the threat as evidence-channel not control-channel and enforce it (every payload passes an instruction stripper unchanged); (b) train the attacker with two penalties nobody has combined: instruction-detector score AND refuter success, so it learns claims that are both instruction-free and unverifiable; (c) run the matched hijack-vs-fact table across six defenses including a refuter, on both a research env and AgentDojo actions. Foreshadow: hijack ASR collapses from ~X to <5% under strippers/IH; fabricated-authority stays within a few points across the first five columns; only the refuter dents it, and the boundary-trained attacker recovers most of that. Silent-failure rate (attack succeeds AND agent reports success AND no flag) is the headline number, and it is near zero for hijack and high for ours.

**Beat the field:** the *silent-failure* metric + the *verification-boundary-trained attacker* are the two things no prior paper has. Frontier targets (GPT-4o, Sonnet 4.5, 70B local) make it a result, not a toy.

## Paper 2, BrainBodyFM: the three questions

**1. Problem, why it matters.** Biosignal foundation models (SleepFM, LaBraM, PFTSleep) are trained per-modality with bespoke encoders and drop ~20 kappa points across cohorts (PFTSleep 0.81 SHHS to 0.60 MESA). Meanwhile text LLMs are the most-scaled, best-tooled models that exist. If a biosignal could be rendered into text that an unchanged LLM tokenizer reads, every LLM tool (prompting, RL, interpretability, red-teaming) transfers for free. The workshop CFP explicitly asks for "scaling and generalization techniques from other fields carried into biosignal modeling."

**2. Why hard, where people failed.**
- Direct serialization fails: OpenTSLM's text-only baseline gets 9 F1 on sleep staging vs 70 with a native encoder. LLMTime/Chronos digit tokenization works for forecasting but not for classification of 3000-sample epochs.
- Tan et al. (2406.16964) showed that in most "LLM for time series" papers the LLM is decorative; removing it does not hurt. Reviewers in this area now demand the ablation.
- VQ tokenizers (LaBraM, NeuroLM) work but require pretraining a codebook on a large EEG corpus, which is the thing we do not have time or need for.
- Cross-cohort staging papers (U-Sleep, ADAST, STDA-Net) fix the gap with domain adaptation on raw signals, not with a representation that is cohort-invariant by construction.
- Adversarial work on EEG classifiers is sample-level L-inf noise, not physiologically meaningful and not interpretable.

**3. What we do that is new, foreshadowing.** (a) A symbolic tokenizer built from AASM scoring physiology (bandpower, slow-wave fraction, spindles, REMs, atonia, desaturation), quantized *per night*, so the same word means the same physiological state in SHHS and MESA. (b) The LLM-removed ablation run *first*, so the paper is honest either way: if Qwen beats LR on identical words, the language prior helps; if not, we have a strong interpretable cross-cohort tokenizer and say so. (c) Because the representation is text, we reuse a text red-teamer verbatim: the GRPO attacker edits symbols under a clinician-specified budget, and the edit loci are directly interpretable against AASM rules (EMG symbol for R to W, sigma for N2 to N1). (d) The cross-cohort drop is *decomposed*: how much vanishes from per-night normalization alone, how much from N3-rule harmonization, how much is residual. Foreshadow: per-night quantile words close most of the SHHS to MESA gap that PFTSleep loses; metadata-text injection flips the stager more than signal edits (shortcut learning, publishable alone).

**Beat the field:** nobody has (i) a physiology-grounded symbolic tokenizer that an unchanged LLM reads, (ii) the decomposition of the cross-cohort drop, (iii) interpretable adversarial edits on PSG. Any one of the three is a workshop paper; we aim for all three with (i) mandatory.

# The two papers in one paragraph each

**AgentWild: "Convincing, not Commanding."** Prompt-injection defenses (instruction strippers, spotlighting, PromptGuard, instruction-hierarchy training) all assume the attacker issues *commands*. Loki's attacker instead writes *fabricated authority* (fake statutes, reports, retractions) into a tool result, so the agent completes the user's task but with the attacker's wrong answer or action, and no monitor sees an off-task step. We frame this as *illusioning* (Wu et al.) vs *goal misdirection*, control channel vs evidence channel, plus the Verification Boundary (Poisoned Playbooks). One table: payload families (hijack / template fabricated-authority / GPT zero-shot / PoisonedRAG / Loki GRPO / Loki GRPO + verifiability reward) x six defenses. Prediction: hijack collapses under instruction defenses, fabricated authority stays flat until a refuter column. Must cite organizer papers AgentPoison and AdvWeb in paragraph one.

**BrainBodyFM: "Sleep as a language."** A symbolic tokenizer turns each 30 s polysomnography epoch into a ~40-char ASCII word (per-night-quantile bandpowers, slow-wave fraction, spindles, REM count, EMG tone, SpO2 min/desat, time-of-night) that the *unchanged* Qwen tokenizer reads. SFT a 0.5-1.5B Qwen stager on SHHS, evaluate zero-shot on MESA, with a mandatory logistic-regression / LightGBM / random-init ablation on identical words (the reviewer's "is the LLM decorative?" test). Then Loki's GRPO red-teamer edits words under a clinician-specified physiological budget with hard vetoes and a second-scorer test. Comparator: PFTSleep kappa 0.81 SHHS to 0.60 MESA zero-shot.

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
| 4 | GRPO attacker: copy `harmbench_trainer.py` to `illusion_trainer.py`, `reward_function.py` to `illusion_reward.py`, add detect + refute terms | `aw-env` | GPU | 1 h code + 4-6 h run x2 |
| 5 | Real targets (`VLLMTarget`, `OpenAITarget` are 1-call shells) + defense table harness (6 defenses) + AgentDojo eval | `aw-env` | GPU + API keys | 3 h |
| 7 | Sleep: `nsrr_load.py` + `psg_words.py`, LR-on-words gate | `sleep-pivot` | CPU | 3 h |
| 6 | Compute plan / odds / go-order (reference) | both | | |
| | **Paper writing, both** | | **human** | **~8 h each** |

# RunPod setup (5 minutes)

1. `git clone https://github.com/yashthakur2008/arpandeep-nrty && cd arpandeep-nrty && git checkout agentwild-pivot`
2. Read `handoff/HANDOFF.md`.
3. RunPod: **4x H100 80GB** (was 2x; budget now allows parallel + seeds), image `runpod/pytorch:2.6-py3.12-cuda-12.1`, 200 GB volume at `/workspace`, expose 8000 + 22.
4. `cp handoff/.env.example handoff/.env`, fill `NSRR_TOKEN`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `WANDB_API_KEY`. Never commit `.env`.
5. `bash handoff/bootstrap.sh` to `bash handoff/run_agentwild.sh` (tmux pane 1) and `bash handoff/run_sleep.sh` (pane 2). Each script prints its next step and stops loudly at the issue number for any file not yet written.

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
