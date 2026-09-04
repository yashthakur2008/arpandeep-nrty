# HARDENING_SLEEP: BrainBodyFM workstream spec

Written 2026-09-04 16:30 PDT by the sleep hardening engineer. Inputs: MISSION_REVIEW.md, PLAN.md, the three council seats, BIBLIOGRAPHY.md sections A-H (H = 2026-09-04 field scan), and the two shipped files `nsrr_load.py` + `psg_words.py` (commit aabfa2d, issue #7). Target: P(submittable, beats the field) >= 0.70.

**State of the branch.** Loader and tokenizer exist and pass the gate on real data: 5 dev nights (3 SHHS1, 2 MESA), 5,730 epochs, tokens/epoch max 38 mean 27.8 under Qwen2.5, LR-on-words leave-one-night-out macro-F1 **0.538** (per night 0.37 / 0.56 / 0.62 / 0.48 / 0.66; N1 0.05-0.26, everything else 0.34-0.96). That is above the 0.5 gate with 4 training nights and no context, which is the weakest possible setting. Nothing else on the branch runs yet.

## (i) Final tables, N per cell, producing script

Every number in the paper comes from a jsonl in `results/` via one script. No hand-typed numbers.

**Table 1. Staging, in-cohort and zero-shot.** Rows: LR-on-words, LightGBM-on-features, Qwen random-init SFT, Qwen-1.5B SFT (3 seeds, mean +/- sd), Qwen-3B SFT if run. Columns: SHHS held-out (kappa, macro-F1, per-class F1 W/N1/N2/N3/R) and MESA zero-shot (same). Comparator rows quoted from literature: PFTSleep kappa 0.60 MESA zero-shot, inter-scorer kappa 0.76 with N1 0.24.
N per cell: SHHS train 500 nights (~500k epochs), SHHS held-out 50 nights (~50k epochs), MESA 100 nights (~110k epochs). Every cell states nights and epochs. Script: `eval_stager.py --pred results/<run>.jsonl --out results/table1.json`; `make_tables.py` renders LaTeX.

**Table 2. Cross-cohort decomposition (sec iv).** Rows: raw-scale bins, per-night quantile bins, + N3 harmonization, residual. Columns: MESA kappa, macro-F1, per-class F1, delta vs previous row. N: same 100 MESA nights, LR consumer and Qwen consumer as paired columns. Script: `decompose.py`.

**Table 3. Red-team.** Rows: random edits, greedy single-symbol, GRPO attacker (3 seeds), metadata-line injection. Columns: flip rate on confident epochs per (from -> to) among W/N2/N3/R, mean edits per success, second-scorer-agree rate, veto rate. N: 2,000 confident epochs per source stage sampled from SHHS held-out, stratified. Script: `eval_attack.py`.

**Figure 1.** Edit-locus histogram: which of the 11 word fields the attacker edits per transition, next to the AASM criterion for that transition. From the same jsonl as Table 3.

**Figure 2.** Confusion matrices SHHS held-out vs MESA zero-shot, Qwen and LR side by side.

## (ii) SFT config and the ablation that runs FIRST

**Order is mandatory: ablation rows before any Qwen SFT starts.** The LR/LightGBM rows take 10 CPU-minutes on 500 nights. If LR-on-words already reaches MESA kappa >= 0.55 the paper is safe with the LLM as "one consumer"; if Qwen then beats LR by >= 3 macro-F1 points on both cohorts (3 seeds, non-overlapping CI), the language prior is real and goes in the abstract.

Ablation rows (script `ablation.py`, ~120 lines):
1. LR on positional char features of the word (exactly `psg_words.selfcheck`), plus previous-10-stages one-hot when context is on. Both with and without context.
2. LightGBM on the underlying quantized integers (same information, tree consumer).
3. Qwen-1.5B random-init, same SFT recipe. Report (a) generation accuracy and (b) a linear probe on last-layer hidden states, per Schumacher 2026 (H9): without the probe a reviewer says the decorative baseline was under-measured.
4. Qwen-1.5B pretrained, frozen, linear probe only (no SFT). Cheapest "does the prior help at all" test.

SFT (script `nsrr_sft.py`, copied from `training/harmbench_sft_trainer.py`, ~100 lines):
- Model: **Qwen2.5-1.5B-Instruct** for all three seeds. 3B is a stretch row, one seed, only if 1.5B beats LR. Reason: 1.5B SFT over 500k examples at seq 256 is ~35 min per seed on one H100 in bf16 with packing; 3B is ~80 min. Three 1.5B seeds cost less than one 3B seed plus its variance. Qwen2.5 tokenizer keeps `W A B C R` single-token (verified).
- Prompt: `age {a} sex {s} bmi {b} | prev {10 stage letters} | {word}` -> target one letter. Demographics line is omitted in 50% of training prompts (dropout) so the metadata attack in (iii) tests a model that was trained both with and without the line; report both variants.
- Seq len 256 (prompt ~45-60 tokens, plenty of headroom). Batch 128, lr 1e-5 cosine, 1 epoch, bf16, gradient checkpointing off, flash-attn on. Loss on the answer token only.
- Nights: 500 SHHS1 train / 50 SHHS1 held-out / 100 MESA test. Split by subject id, fixed seed, written to `splits.json` once and committed.
- Seeds 0/1/2. Report mean +/- sd. Any claim in the text needs the sd.
- Smoke test (rule 1): 200 steps on 20 nights, eval on 2 nights; must print macro-F1 > LR-on-2-nights within 15 min or the run is stopped and the pipeline debugged.

Gate after SFT: SHHS held-out macro-F1 >= 0.60 and MESA zero-shot kappa >= 0.45. Below that, the attacker targets LR-on-words instead (N6' in PLAN.md) and the paper is "tokenizer + decomposition + attack on the interface".

## (iii) Red-teamer reward v2

Policy: Qwen2.5-1.5B-Instruct (same family as stager, separate weights), GRPO via `training/harmbench_trainer.py` config path, `num_generations=8`, 4 prompts per step, `max_completion_length=96` (the edited word is <= 40 tokens plus a short tag), 500 steps, lr 5e-6, beta 0.02, temperature 1.2, entropy bonus 0.01 (PISmith warning, E3).

Input: original word, original stage, target stage, demographics. Output: `<misdirection>` edited word `</misdirection>` or `<misdirection>note: {free text <= 20 tokens}</misdirection>` for the metadata action.

Reward (pure Python over strings, `attack_reward.py` ~120 lines):
```
if not parseable or field count != 11 or any field length changed: return -1       # format gate
if veto(orig, edit): return 0                                                       # clinician hard zeros
if edits > budget: return 0                                                         # budget
flip   = 1 if stager(edit) == target else 0
second = 1 if lr_on_words(edit) == orig_stage else 0                                # second scorer must still see the original
return flip * second - 0.02 * edits
```
- Edit budget: <= 10% of symbols (<= 4 of 42 characters), each edit <= 1 quartile level, adjacent 5 s letters within the same band may differ by <= 1 level after the edit (continuity).
- Vetoes as hard zeros: spindle bucket > 0 while all six sigma letters are `a`; EMG all `a` (atonia) in a word whose stage is not R and whose target is not R; SpO2 min quartile changed by 2+ levels; desat flag set while min quartile is `d`; slow-wave symbol `3` while delta letters are all `a` or `b`; any `?` introduced or removed.
- Second scorer = LR-on-words (A3 caveat: YASA's stager saw NSRR). The flip counts only if LR still assigns the original stage, so the attack exploited the LLM, not a genuinely ambiguous epoch.
- Confident-epoch filter: attack only epochs where the frozen stager's original prediction is correct and its top-1 probability >= 0.8, and where LR agrees. Source stages W/N2/N3/R only (N1 is scorer noise, D4).
- Baselines, same budget and vetoes: random edits (100 samples per epoch), greedy single-symbol search (42 x 3 candidates). Both are cheaper than GRPO and run first; GRPO must beat greedy or it is reported as "greedy suffices".
- 3 seeds. Smoke criterion: 20-step run (160 completions) shows mean reward > 0 and reward std > 0.05 within 10 minutes. Flat reward = stop, fix, restart (do not let a 30-min run bake).
- Metadata action reward is the same formula with edits = 0, so the number reported is a pure flip rate, and the paper's headline comparison is "flip rate with zero signal edits vs flip rate at the 10% budget".

## (iv) Cross-cohort decomposition protocol

Same trained stager and same LR, four MESA tokenizations, one number per step, differences reported with bootstrap CI over nights:

1. **Raw-scale bins.** Replace per-night quantiles with fixed breakpoints fitted once on the SHHS training pool (global bins, Chronos-style). This is the "what a normal tokenizer would do" baseline and is expected to be the worst MESA number. Implemented as a `cuts=` override in `psg_words.qbin` fed from a `global_cuts.json`.
2. **Per-night quantile bins** (the shipped default). Delta from 1 = value of per-night normalization. Prediction: this is the largest term.
3. **+ N3 harmonization.** SHHS is R&K (3+4 -> N3); MESA is AASM. Two sub-steps reported separately: (a) relabel SHHS training N3 using the AASM 20% slow-wave rule applied to our own slow-wave-fraction feature (`w >= 2`), retrain, re-eval; (b) collapse N2/N3 to "N2+N3" in both cohorts and report 4-class kappa. Delta from 2 = value of rule harmonization.
4. **Residual.** What is left after 3 is cohort and montage shift (age 69 vs 63, Somte vs PS-2, EOG reference). Report per-age-bin confusion (Bechny 2025, H19) and per-cohort word-field marginals (KL per field) so the reader can see which symbol drifts.

Each step is one row in Table 2 for both LR and Qwen. The claim "per-night words close most of the gap PFTSleep loses" is true iff (row2 - row1) >= 0.5 * (in-cohort - row1). Otherwise we report the honest split.

## (v) Risk table

| # | Risk | P(fail) before | Mitigation in place | P(fail) after | Detectable when |
|---|---|---|---|---|---|
| R1 | Loader/tokenizer do not exist or break on real data | 0.35 | Both shipped, tested on 5 real nights, edge cases covered, gate passed at 0.538 | 0.05 | now |
| R2 | LR-on-words fails the 0.5 gate at scale (words carry too little signal) | 0.25 | Passed at 0.538 with only 4 train nights and no context; at 500 nights with context it goes up, not down | 0.05 | h+1 after full tokenization |
| R3 | Qwen SFT does not beat LR on identical words (Tan effect) | 0.50 | Ablation runs first; paper pre-committed to the honest framing either way; probe-based measurement per H9 | 0.50 (unchanged, but it no longer kills the paper: P(kills) 0.10) | h+3 |
| R4 | MESA zero-shot kappa < 0.45 (cross-cohort story collapses) | 0.35 | Per-night bins by construction; decomposition (iv) turns any drop into a result; comparator PFTSleep is only 0.60 | 0.20 | h+3 |
| R5 | GRPO attacker never gets non-flat reward | 0.40 | Greedy + random baselines run first and are publishable alone; 20-step smoke rule; entropy bonus; dense reward with second-scorer term | 0.20 (and P(kills paper) 0.05 since baselines carry Table 3) | h+5 |
| R6 | Novelty scooped (NeuroCognitor/Lei-SleepLM lineage, StageGuard) | 0.20 | Field scan done; repositioning written (no codebook, no vocab change, human-readable; StageGuard cited as defense) | 0.10 | now |
| R7 | Bulk download + tokenization eats 2x budget on the GPU box | 0.30 | `run_sleep.sh` exists; loader is 12 s per night on an M4 CPU, tokenizer ~3 s; 650 nights = ~3 CPU-hours, parallel 16 -> 15 min | 0.10 | h+2 |
| R8 | Paper writing time (6 h minimum) squeezed by reruns | 0.30 | Tables from jsonl via script; skeleton already committed on sleep-paper | 0.20 | h+10 |
| R9 | Reviewer says "symbolic edits are not signal-realizable" | 0.25 | Frame as interface robustness; vetoes and continuity make edits physiologically bounded; metadata attack needs zero signal edits | 0.15 | at review |

P(submittable) = product over paper-killing failures only: (1-0.05)(1-0.05)(1-0.10)(1-0.20)(1-0.05)(1-0.10)(1-0.10)(1-0.20)(1-0.15) = **0.95 x 0.95 x 0.90 x 0.80 x 0.95 x 0.90 x 0.90 x 0.80 x 0.85 = 0.34**.

That is honest: **0.70 is not reached by this table.** The two terms that hold it down are R4 (MESA collapse, 0.20) and R8 (writing time, 0.20). Under the tiered plan the paper is still submittable if R4 fires (SHHS-only tokenizer + attack paper, weaker), so the conditional P(submittable at all) is ~0.55, and P(submittable and beats PFTSleep's 0.60 on MESA) is ~0.30. Reaching 0.70 requires R4 and R8 to both come in under 0.10, which means: MESA words visibly transfer at the first 20-night eval (h+3), and writing starts at h+6 regardless of attacker state.

**Kill order under pressure (unchanged from PLAN.md):** 3B row -> GRPO attacker (keep greedy/random) -> attacker MESA transfer -> N3 harmonization sub-step (b) -> MESA (paper becomes SHHS-only).

## (vi) GPU allocation, 4x H100

| GPU | h0-2 | h2-4 | h4-7 | h7-10 |
|---|---|---|---|---|
| 0 | idle (download + tokenize are CPU) | SFT seed 0 (1.5B) | SFT 3B stretch (1 seed) or free | attacker seed 0 |
| 1 | idle | SFT seed 1 | attacker smoke, greedy/random baselines (forward-only) | attacker seed 1 |
| 2 | idle | SFT seed 2 | random-init SFT + frozen-probe rows | attacker seed 2 |
| 3 | idle | MESA eval of every checkpoint as it lands; decomposition rows 1-3 (retrain for 3a is one extra SFT) | decomposition, per-age confusions, figures | eval of attackers, Table 3 |

CPU: 16 procs for `nsrr_load.py` + `psg_words.py` over 650 nights in parallel (add `--jobs` via `multiprocessing.Pool` around `find_pairs`; 10 lines). LR/LightGBM rows on CPU at h+1.

Memory: 1.5B SFT at batch 128, seq 256, bf16 fits in one 80 GB H100 without sharding. Attacker (policy + frozen stager + LR) also fits on one GPU. No multi-GPU training anywhere; all parallelism is across seeds.

## (vii) Code budget

| File | Lines | Status |
|---|---|---|
| `nsrr_load.py` | 152 | shipped |
| `psg_words.py` | 197 | shipped (includes selfcheck + LR gate) |
| `splits.py` (subject split, global cuts) | 40 | todo |
| `ablation.py` (LR/LightGBM/probe rows, eval JSON) | 120 | todo |
| `nsrr_sft.py` (copy of harmbench_sft_trainer, prompt builder, eval) | 110 | todo |
| `attack_reward.py` (format gate, vetoes, budget, second scorer) | 120 | todo |
| `nsrr_attacker.py` (copy of harmbench_trainer with reward hook, greedy + random baselines) | 100 | todo |
| `decompose.py` (4 tokenizations, Table 2) | 60 | todo |
| `make_tables.py` (jsonl -> LaTeX) | 60 | todo |
| **Total** | **~960** | 349 shipped |

That is over the 600-line rule by ~360 lines, all of it in the attacker and eval scripts. Cuts if needed: fold `decompose.py` into `ablation.py` (saves 40), drop the LightGBM row (saves 20, LR is the ablation that matters), reuse `eval_stager` inside `nsrr_sft.py` (saves 30). Floor ~870. Anything above 1,000 is fat and should be deleted, not tuned.

## Bugs caught in my own code during the hostile review (for the record)

1. **Saturated wake EEG poisoned the sigma quartiles.** SHHS1 wake epochs late in the night sit at the +/-125 uV ADC rail for whole windows (27% of night 200002's W epochs). Rail-clipping is a square wave, so its spectrum is flat, and "relative sigma" in W came out at 0.38 vs 0.06 in N2. The per-night quartiles for sigma were then set by artifact, not by spindles. Fix: loader stores the ADC rail per night; tokenizer marks a 5 s window bad if >= 2% of samples touch the rail or std < 0.5 uV, and bins are fitted on clean windows only. Bad windows emit `?`.
2. **Spindle field was flat across stages (0.13/epoch in N2).** YASA's default thresholds on 100 Hz C4 with the full night as input barely fire. The obvious fix (pass the hypnogram to YASA) leaks labels into the tokenizer and was rejected. Loosened thresholds (`rel_pow 0.15, corr 0.6, rms 1.2`) instead; still weak (~0.2/epoch in N2), and the sigma quartile letters carry most of the spindle signal. Reported honestly; the spindle field is the first candidate for deletion.
3. **REM-count bucket saturated on wake.** Wake epochs have 13 crossings per epoch, R has 12, so the old buckets [1,3,6] put both at `3`. Rebinned to [1,4,10]; the L/R phase sign (R median corr -0.1, W median +0.35) is what separates them, and its thresholds were also off (0.2 put most of N2 at `n`). Now x < -0.1, i > 0.45.
4. **`_pick` returned the signal index, not the candidate rank**, so the "using C3 fallback" log would have fired on any night whose C4 channel happened to sit at index >= 3 (which is every SHHS night: `EEG` is index 7). Caught by re-reading the diff.
5. **Quantile bins were recomputed per epoch inside the word loop** (O(n^2) on SpO2 fields). Hoisted.
6. **`hour` is hours since recording start, not since lights-off.** SHHS `LIGHT` channel is 1 for the whole dev record, MESA has no light channel. Left as a proxy with a `ponytail:` comment; recordings start close to lights-off in both cohorts.

Not bugs but limits to state in the paper: SHHS chin EMG is weak in a known fraction of nights (D2); MESA mV units are converted by header, so an EDF with a wrong physical-dimension string would be silently 1000x off (the artifact mask would then flag the whole night as flat and every EEG field becomes `?`, which is loud enough).
