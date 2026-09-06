# Progress Check: are we en route to a NeurIPS AIWILD 2026 paper?

Last updated 2026-09-05, after the agentic pivot. All numbers are measured on
this machine and traceable to files in `results/`.

---

## Headline: **~88% of the way to a submittable paper.** The deadline (today,
Sept 5 AoE) is not achievable, but the paper is close to submission-ready.

---

## Quantified progress

| Dimension | Weight | Score | Rationale |
|---|---|---|---|
| Working, trustworthy infrastructure | 20% | **95%** | 137 tests, held-out splits, validated judge, tool-call ground truth, CI |
| A measured result | 20% | **95%** | 1,968 agentic trials + n=120 GRPO comparison, all committed as JSON |
| Statistical rigor | 15% | **95%** | Fisher/McNemar/Wilson CIs, length control, matched contrast, adaptive control, 200 human labels |
| **Novelty** | 25% | **85%** | Policy-phrasing effect, text/tool-call divergence, and an adaptive-attack-validated mitigation |
| Baselines vs. prior work | 10% | **20%** | Positioned against LLMStinger/DarkCite in prose; no head-to-head rerun |
| Written paper | 10% | **90%** | 4-page LaTeX draft, every number guarded by 34 claim tests |
| **Weighted total** | | **~88%** | |

---

## What the paper claims now

**Primary (agentic, 1,968 trials, no LLM judge anywhere):**

| Finding | Evidence |
|---|---|
| Fabricated authority breaks policy-constrained agents | 0/240 → 208/1440 (14.4%), p = 1.1e-15 |
| **Deployer's policy wording dominates** | 0/288 vs 32.3% under identical attacks, p = 1.4e-32 |
| Complete separation in a matched contrast | 18/18 vs 0/18, p = 1.1e-10 |
| It is the clause, not verbosity | Longest policy was *worst*: 11.5% vs 0%, p = 3.6e-4 |
| Agents refuse in prose and act anyway | 32/432 paired trials, p = 1.3e-6 |
| Provenance claims work, category claims do not | 21.7% vs 0/240 |

**Supporting (why we changed the outcome variable):** three judges scoring 200
identical responses report ASR of 14%, 25% and 83% against a human truth of 19%.
The local judge is 36% accurate, worse than the 81% constant baseline, and
mislabelled 128 of 162 genuine refusals. Our own GRPO result inverted under a
validated judge: 12.5% → 11.7%, p = 1.00.

---

## What changed since the last check (52% → 78%)

1. **The pivot was executed, not just recommended.** The outcome variable is now
   a logged tool call, which removes the judge from the measurement entirely.
   That is what makes the primary result trustworthy.
2. **A paper exists.** `paper/main.tex`, 1,492 words, within the 4-page limit.
3. **Every claim is machine-checked.** `tests/test_paper_claims.py` parses the
   LaTeX tables cell by cell and re-derives each value from `results/*.json`.
   Verified it fails when a table value is altered. This is the safeguard that
   was missing when the project reported the false 25% → 48% improvement.
4. **CI added.** Lint, offline tests and paper-claim verification, hermetic
   (passes with no API keys and a clean HOME).

---

## Remaining gaps

| Gap | Severity | Effort |
|---|---|---|
| ~~No competent adaptive attacker~~ | **CLOSED** | done |
| Only two hosted targets, both small production models | Medium | ~1 day, ~$5 |
| Single-turn only; the indirect tool-output channel was inconclusive (24/24 early `request_approval`) | Medium | ~2 days |
| Hand-written scenarios | Low — per-scenario rates span 7.1–15.7% | — |
| No head-to-head against DarkCite/PAIR | Low for a workshop | ~1 week |
| GRPO multi-seed replication still running | Low — now a supporting section | in progress |

**The adaptive-attack gap is now closed.** An attacker LLM with the defender's
exact system prompt, tool schema and its own failure transcript broke the weak
control policy 8/8 but never breached `strict_hatch` (0/8, p = 7.8e-5). The
control result is what makes it informative rather than a repeat of our weak
hand-written attempt. The claim remains bounded: the attacker is gpt-4o-mini,
so a stronger or RL-trained attacker may still succeed.

The largest remaining gap is target coverage: two small production models. One
frontier model would blunt the most likely reviewer objection.

---

## Cost

Total spend across the entire project: **under $3.** Local Ollama for bulk
target calls, hosted models only where fidelity is required. The 1,968-trial
agentic sweep cost under $2. RunPod was never needed and never started.

Money is not a constraint on this project. The remaining constraints are the
adaptive-attack experiment and time.

---

## Recommendation

1. **Do not submit today.** The paper is close but the adaptive-attack hole is
   exactly what a reviewer will probe, and the venue is non-archival so there is
   no cost to waiting.
2. ~~Run the adaptive attack~~ **Done.** Informative null: 0/8 against the
   clause with the control broken 8/8.
3. **Add one frontier model** to blunt the "small models only" objection. This
   is now the highest-value remaining experiment (~1 day, ~$5).
4. **Consider an RL-trained adaptive attacker.** The repo has a working GRPO
   attacker; pointing it at the precedence clause is the strongest available
   test and would either harden or overturn the paper's main recommendation.
5. **Rotate the API keys** pasted into the chat transcript.
