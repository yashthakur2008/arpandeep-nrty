# Design brief: Loki -> BrainBodyFM pivot (v0, for review)

Deadline: 2026-09-05 04:00 PST (~32h from now). Venue: NeurIPS 2026 Workshop on Foundation Models for the Brain and Body. 5 pages, anonymized, non-archival. OpenReview.

## What exists (Loki repo)
- TRL `GRPOTrainer` + a hand-rolled CPU GRPO loop, Qwen2.5-0.5B/1.5B-Instruct policy.
- Jinja system/user prompt templates that ask the policy to emit `<reasoning>..</reasoning><misdirection>..</misdirection>`.
- Reward functions: (a) heuristic format/length/keyword rewards, (b) "did the frozen target LLM get fooled" reward, (c) LLM-as-judge via Ollama.
- Dataset builders that turn FEVER/HotpotQA/HarmBench rows into `{prompt, answer, evidence}` HF Datasets.
- RunPod Dockerfile, deploy script, wandb logging.

## Data
NSRR SHHS1 (~5.8k nights, EEG C4-A1 125Hz, C3-A2, EOG L/R 50Hz, chin EMG 125Hz, ECG 125Hz, SaO2 1Hz, 30s R&K stages -> map to W/N1/N2/N3/R) and MESA (~2k nights, EEG C4-M1/Fz-Cz/Cz-Oz 256Hz, EOG, EMG, EKG, SpO2 1Hz, AASM stages). Both have NSRR XML annotations per night. Common channel set: one central EEG, one EOG, chin EMG, SpO2. User has NSRR access; token not yet on this machine. Local box: M4 Pro, no CUDA, 34GB free disk. Remote GPU available (RunPod-style).

## Converged design (proposal to critique)

Title-ish: "Sleep as a language: a drop-in symbolic tokenizer lets a text LLM stage PSG, and text-native GRPO red-teaming exposes its cross-cohort fragility."

Two contributions, one pipeline, every Loki component reused:

### C1. Symbolic PSG tokenizer ("PSG-SAX" / "sleep grammar")
Each 30s epoch -> a short ASCII "word" the *unchanged* Qwen tokenizer already handles. Per channel:
- EEG: bandpower in delta/theta/alpha/sigma/beta per 5s sub-window, quantized to 4 levels -> letters. Plus SAX of the raw envelope (32 PAA segments, 6-letter alphabet). Spindle/K-complex detector flags as single symbols (from YASA).
- EOG: SAX 16 segments, 4 letters.
- EMG: RMS quantized to 4 levels per 5s.
- SpO2: 30 x 1Hz samples binned to 8 levels -> digit string. Desaturation event flag.
Total ~80-120 chars per epoch, fits in 128-token completions with context of previous k epochs' stage labels. Optionally: learn a BPE on the corpus of symbolic epochs and register merges as added tokens ("sleep grammar"), ablate vs raw chars.

Reuses: Jinja templates (epoch word + demographics + previous stages replaces question + evidence), dataset builder pattern (`scripts/hotpotqa.py` -> `scripts/nsrr.py`), Qwen tokenizer/model, no architecture change.

### C2. Two GRPO roles, same loop
- **Stager (defender)**: policy emits a single stage token from {W,N1,N2,N3,R} (1-token action => contextual bandit, cheap rollouts). Reward = exact match (+ partial credit for adjacent-stage confusion). Train on SHHS subset, evaluate zero-shot on MESA => cross-cohort number. SFT warm start then GRPO. Baseline: same tokens -> logistic regression / small CNN on raw signals (upper bound reference).
- **Red-teamer (attacker)**: Loki's misdirection policy verbatim. Input: symbolic epoch + true stage. Output: `<misdirection>` = edited symbolic epoch (or appended metadata text: age/BMI/AHI/"tech note") under an edit budget. Reward = frozen stager flips label − λ·edit distance − physiology-violation penalty (e.g. SpO2 jumps >4%/s, spindles in W). This is literally the existing "did the target get fooled" reward with a plausibility term replacing keyword heuristics.
- Analysis: which symbols does the attacker learn to edit (interpretability of failure modes), does attack success transfer SHHS -> MESA, does adversarial fine-tuning of the stager on attacker outputs recover MESA accuracy.

### What is honestly NOT claimed
Not SOTA staging. OpenTSLM (2510.02410) reports fine-tuned text-only LLM at 9 F1 on their sleep task vs 70 with a native TS encoder, so raw-digit serialization is known to fail. Our bet is that *symbolic/spectral* serialization is a different regime. If stager macro-F1 < 0.45 on SHHS held-out by hour 12, pivot: keep C1 as "tokenizer + probing" and make the paper about the red-team result against a conventional CNN stager wrapped in the same text interface.

## Compute plan
1x A100/H100 on RunPod. Download 300 SHHS + 150 MESA nights there (not locally). Preprocess to per-epoch symbolic words (parquet, tiny). All GRPO on GPU; local M4 does eval/plots/paper.

## Questions for reviewers
1. Is the symbolic-tokenizer + red-team story in scope and credible for this workshop, or will it read as a gimmick?
2. Biggest technical risk you see in 32 hours.
3. What one experiment or ablation would you cut, and what one would you add?
4. Prior work we must cite or risk looking naive (OpenTSLM, SleepFM, LaBraM, BENDR, Chronos/LLMTime, SAX).
