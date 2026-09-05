# Progress Report: NeurIPS 2026 "Agents in the Wild"

Prepared 2026-09-05. Numbers are measured on this machine, not estimated.

## 1. The deadline problem

The workshop's extended deadline is **September 5, 2026 AoE**, which is **today**
(roughly 25 hours from now, since AoE is UTC-12).

There is no realistic path to a novel, experimentally-supported paper in 25 hours
from the current state. The honest options are in section 6. Everything below
quantifies why.

## 2. Where the project actually stands

### What works, verified today

- A real GRPO training loop (TRL), with an integration test proving weights move
  iff the reward has variance.
- An installable package with 69 passing tests and a clean lint.
- An eval harness reporting format rate and ASR with bootstrap CIs.
- **Ollama installed and working**, which unblocked the first attack-success
  measurement this project has ever produced.

### The measured baseline

Qwen2.5-0.5B-Instruct attacker, llama3.2 target, 20 HarmBench behaviors, seed 0:

| Metric | Value |
|---|---|
| Parseable misdirections | 16/20 (80%) |
| Strict `<misdirection>` tag compliance | **0/20 (0%)** |
| **Attack success rate (llama3.2 judge)** | **25% [6%, 50%]** |
| **Attack success rate (refusal heuristic)** | **19% [0%, 38%]** |
| Judge agreement | 15/16 (94%) |
| Wall-clock | ~6 min on M4 CPU + Metal |

The CIs are very wide because n=16. They are honest, not encouraging: at this
sample size the result is compatible with anything from "barely works" to
"works half the time".

### Finding: the judge is itself a research problem

Inspecting the 4 "successes" showed llama3.2 scoring `"I can't provide a script
for a pornographic snuff film"` as **compliance**. Separately, our own heuristic
missed `"I can\u2019t provide..."` because models emit the Unicode apostrophe
(U+2019), not ASCII. Fixing that raised judge agreement from 81% to 94%.

Two different judges disagree on ~1 in 6 samples, and both had demonstrable bugs
found by reading 16 examples. Any ASR in this literature is only as good as its
judge, which is a publishable observation (section 4.3).

### What still does not exist

- No trained checkpoint. The only "trained" artifacts came from the trainer that
  performed no gradient updates, so they are the base model with a new filename.
- **No trained-vs-base comparison.** We have a baseline but have not yet run GRPO
  to see whether training improves on 25%. This is the core experiment.
- No baseline comparisons (PAIR, GCG, AutoDAN, DarkCite).
- No transfer results across target models.
- No experimental history: all 8 wandb run directories are 0 bytes.

## 3. Quantified gap to a submittable paper

| Requirement | Have | Need | Gap |
|---|---|---|---|
| Working training pipeline | Yes | Yes | **Closed today** |
| Baseline ASR measured | **Yes, 25%** | Yes | **Closed today** |
| Trained attacker checkpoint | No | >=1 | ~1 day local |
| Trained-vs-base ASR delta | No | Yes, with CIs | ~2 days |
| Baselines compared | 0 | 3-4 | ~2 weeks |
| Target models evaluated | 1 | 3+ | ~1 week |
| Behaviors evaluated | 20 | 200+ | ~2 days |
| Seeds per condition | 1 | 3+ | Multiplies above |
| Human validation of judge | No | ~100 samples | ~1 week |
| Written paper | 0 pages | 4 or 9 | ~1 week |

Realistic effort to a credible 4-page short paper: **4-6 focused weeks** with GPU
access. To a 9-page regular paper: **3-4 months**.

## 4. The novelty problem (most serious, and not fixable by compute)

Both core ideas are already published:

- **RL-trained attacker LLM against HarmBench.** LLMStinger (arXiv 2411.08862)
  fine-tunes an attacker LLM in an RL loop to generate adversarial suffixes for
  HarmBench behaviors. This is our method.
- **Fabricated authority/citation framing.** DarkCite (arXiv 2411.11407,
  ICASSP'26) generates fake but credible citations to bypass safety, and reports
  that authority framing beats uncited harmful prompts. This is our system
  prompt, which asks for "fake laws, policies, regulations, authorities,
  statutes" with "section numbers, dates, organization names".

"GRPO instead of PPO on an existing attack" is not a workshop contribution on its
own. A viable angle must add something neither paper has. Candidates, in
descending order of feasibility:

1. **Agentic framing (best fit for this venue).** Every prior work attacks a
   chat model. This workshop is about *agents in the wild*: tool use, multi-step
   execution, computer use. Does authority-framed misdirection transfer to an
   agent that can call tools? Does a fabricated "compliance policy" make an agent
   execute a harmful tool call it would otherwise refuse? Nobody has measured
   this, and it is squarely on-topic.
2. **Negative/replication result.** Honest measurement of whether RL-learned
   misdirection actually beats DarkCite's static templates. Workshops accept
   well-executed negative results, and the short-paper track explicitly invites
   "follow-up experiments".
3. **Judge-sensitivity study.** Show how much reported ASR depends on the judge
   (keyword vs. LLM vs. human). Our own audit found a keyword judge that scored
   any response over 100 chars as a jailbreak. That is a real, demonstrable
   measurement problem in this literature.

## 5. Funds and cost efficiency

### Audit result: there are no funds

| Resource | Status |
|---|---|
| OpenAI | **No key anywhere.** No `.env`, shell rc, or config file |
| Anthropic | No key |
| RunPod | **No key.** No GPU access |
| HuggingFace | No token (public models fine) |
| W&B | Working, free tier, entity `tsavla23-cupertino-high-school` |
| Ollama | **Installed today.** llama3.2 (2 GB) pulled, serving on Metal (17.8 GiB) |

"Check if the API keys have funds" has a blunt answer: there are no API keys, so
there is nothing to check. Every credential-dependent path in this repository has
never run. This also explains why the codebase drifted into fake trainers and
keyword judges: nobody could execute the real path, so the fallbacks became the
only code that ran.

### Most cost-efficient plan, in order

**Step 1 — spend $0, unblock everything. DONE today.**
Ollama is installed, llama3.2 is pulled, and the first ASR number (25%) is
measured. The M4's 17.8 GiB of unified memory runs the target locally at
~6 min / 20 behaviors, so the entire attack loop costs nothing. The immediate
next command is the actual training run:
```bash
loki-train --reward-backend ollama --num-samples 100 --report-to wandb
loki-eval --model outputs/harmbench-grpo --reward-backend ollama --num-samples 100
```
That produces the trained-vs-base delta, which is the core result.

**Step 2 — the cheapest useful hosted spend, ~$5.**
`gpt-4o-mini` at ~$0.15/1M input tokens. A 200-behavior eval with a ~500-token
judge call is roughly 100K tokens, well under $1 per full evaluation. Budget $5
for judge calls only; keep the *target* local. Use the hosted model as a judge,
never as the bulk generator, because judging is ~20x cheaper per sample.

**Step 3 — GPU only when the pipeline is proven.**
An A100 at ~$1.50/hr is wasted on a pipeline that has never produced a valid
number. Prove the loop locally on the 0.5B model first, then rent for the final
runs. A 1.5B GRPO run of 200 behaviors is ~4-6 hours, roughly $8. Budget $50
total for all training, and use spot instances (`use_spot: true` in
`runpod_config.yaml`, already present but unread until today).

**Efficiency rules to hold to:**
- Local Ollama for the *target* (thousands of calls), hosted only for the
  *judge* (hundreds of calls). The split is why `targets.py` and `judges.py` are
  separate modules.
- Cache target responses by `(behavior, misdirection)`; GRPO regenerates the same
  pairs constantly.
- Keep `heuristic` as the CI/dev default so no run ever burns credits by accident.
- Preflight now blocks a keyless run in under a second, instead of failing after
  a model download.

Total to a credible short paper: **under $60.** The binding constraint is time
and novelty, not money.

## 6. Recommendation

Submitting to today's deadline is not advisable. We now have a working pipeline
and one real baseline (25% ASR, n=16, very wide CI), but no trained model, no
trained-vs-base comparison, no competing baselines, and a method that overlaps
two published papers. A submission today would be desk-reject material and would
spend reviewer goodwill for no gain, on a non-archival venue where there is
little cost to waiting.

Options, in order of what I would advise:

1. **Target the next venue** (ICLR 2026 workshops, or the 4th AIWILD) with the
   agentic-transfer angle from section 4.1. That is 4-6 weeks of work, is
   genuinely novel, and fits this workshop family's scope precisely. The pipeline
   to do it now exists and is tested.
2. **Finish the core experiment this week.** A GRPO run on 40 behaviors is
   already running locally at $0. If trained ASR does not beat 25% by a margin
   that survives its confidence interval, the method does not work and no amount
   of writing will fix that. This single number should gate all further effort.
3. **Bank the judge-sensitivity finding.** Section 4.3 is a real result we
   partly have already: two judges disagreeing on 1 in 6 samples, with concrete
   bugs (Unicode apostrophes, a keyword judge scoring any 100+ char response as a
   jailbreak). Scaled to ~200 samples with human labels it is a defensible short
   paper on its own, and it is a genuine service to a literature where everyone
   reports ASR without validating the judge.

I would do option 2 now (it is free and running), then commit to option 1.

## 7. Immediate next actions

| # | Action | Cost | Time |
|---|---|---|---|
| 1 | Finish the running GRPO training run | $0 | ~1 hr |
| 2 | Eval trained vs. base, 100 behaviors, 3 seeds | $0 | ~4 hr |
| 3 | If delta is positive: scale to 200 behaviors, 3 targets | $0-5 | ~2 days |
| 4 | Hand-label 100 judge decisions to calibrate ASR | $0 | ~3 hr |
| 5 | Update the deploy scripts, which still point at deleted paths | $0 | ~1 hr |
| 6 | Decide venue and write | $0 | ~1 wk |

Nothing on this list requires a purchase. The binding constraints are time and
novelty, not money.
