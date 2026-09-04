# Council: pragmatic ML engineer, 32-hour feasibility stress test

## Stage-by-stage

**1. NSRR download (`nsrr` gem).** SHHS1 EDF ~50-80MB/night; MESA ~250-400MB/night (256Hz, many channels). 200 SHHS + 60 MESA ≈ 15+20GB. Gem does ~5-15MB/s single-stream: **2-3h wall, runs in background.** Breaks: token not on box, gem picks whole dataset, RunPod disk 50GB default. Fix: request token first thing; `nsrr download shhs/polysomnography/edfs/shhs1 --file=shhs1-2000[0-9]*.edf` style subset plus `annotations-events-nsrr`; mount 150GB volume; start MESA download only after SHHS finishes.

**2. EDF parse + annotations.** pyedflib (faster than mne for this). **1.5h coding, 20 min runtime with 16 procs.** Breaks: channel names differ (SHHS `EEG`/`EEG(sec)`, MESA `EEG3`/`EOG-L`), sample rates, NSRR XML stage strings (`Stage 4`→N3, `SDO:...` in MESA), epoch count mismatch between EDF length and XML. Fix: per-dataset channel map dict; parse XML with `xml.etree` keyed on `EventConcept`; truncate to min(len). Skip nights that fail, log count.

**3. Symbolic tokenization.** Bandpower via `scipy.signal.welch`, SAX by hand (20 lines), SpO2 binning. **2h code + 15 min runtime.** Breaks: YASA spindle/K-complex detection is slow and fragile on 125Hz. Fix: YASA is optional; drop if not working in 30 min. Skip learned BPE (ablation is a luxury). Verify ~100 chars/epoch and <100 Qwen tokens.

**4. SFT warm start.** 200 nights × ~1000 epochs ≈ 200k samples, prompt ~150 tok. Qwen2.5-0.5B, bf16, seq 256, batch 64, lr 1e-5, 1 epoch ≈ 3k steps at ~3 it/s → **~20 min.** Breaks: stage labels `N1/N2/N3` tokenize to 2+ tokens, breaking 1-token completions. Fix: emit single letters `W A B C R` (or `0-4`), map back. Measure macro-F1 on SHHS held-out (20 nights) immediately: this is the hour-12 gate.

**5. GRPO stager (TRL 0.23).** `max_completion_length=1`, `num_generations=8`, `per_device_train_batch_size=64` (8 prompts × 8), `grad_accum=2`, lr 5e-6, `beta=0.02`, `temperature=1.3`. ~0.7 step/s → **1000 steps ≈ 30-45 min.** Breaks: after SFT the policy is confident, all 8 samples agree, advantage = 0, loss flat. Fix: temperature ≥1.3, and reward-shape with adjacent-stage partial credit (0.5). If reward std stays ~0 after 200 steps, stop: report GRPO as no-op over SFT (honest, still a finding).

**6. GRPO attacker.** Completion ≤128 tok, `num_generations=8`, batch 32 (4 prompts × 8), HF generate (do not spend >30 min on vLLM colocate). Reward = frozen stager batched forward (cheap) − λ·Levenshtein − physiology penalty. ~3s/step → **500 steps ≈ 30 min, budget 2h incl. debugging.** Breaks: attacker outputs malformed symbols (reward 0 everywhere), reward hacking by deleting the epoch. Fix: format gate reward −1, hard edit-budget check (≤20% chars), λ tuned so unedited = 0.

**7. MESA eval.** Forward pass over 60 nights ≈ 5 min. Also eval attacker transfer. Breaks: MESA channel differences shift symbol distribution. Fix: z-score bandpowers per night (not global) before quantizing.

**8. Paper.** 5 pages, **6h minimum.** Start template and related-work at hour 0.

## Schedule (h=0 now, deadline h=32)

- **0-1:** NSRR token, RunPod up, start SHHS download. Paper template, related work stubs.
- **1-4:** parse + tokenizer on 5 local test nights (download 5 to M4). Kill: no YASA by h3.
- **4-6:** full SHHS tokenization on GPU box; `scripts/nsrr.py` dataset builder. Start MESA download.
- **6-8:** SFT + held-out F1. **Gate at h8 (not h12): macro-F1 < 0.45 → pivot to CNN stager behind text interface (sklearn/1-layer CNN on bandpowers, 30 min).** LR baseline on same features regardless.
- **8-10:** GRPO stager. Kill at h10 whatever state.
- **10-14:** attacker. Kill at h14: if no attack success >20%, report attack-success curve and stop.
- **14-16:** MESA eval, transfer, symbol-edit histogram. Kill: adversarial-retraining experiment dropped unless h15 is clear.
- **16-18:** sleep 2h. Not optional.
- **18-26:** paper writing, figures on M4.
- **26-29:** buffer for one rerun.
- **29-31:** polish, anonymize, PDF check.
- **31-32:** submit. Target h30.

Drop order: BPE ablation → YASA symbols → adversarial retraining → GRPO stager (keep SFT) → MESA attack transfer.

P(submit something coherent) ≈ 0.6; most likely failure: download+parse eating 8h instead of 4.

## Summary numbers
- Nights: 200 SHHS train, 20 SHHS held-out, 60 MESA eval (~200k / 20k / 60k epochs).
- SFT: 1 epoch, batch 64, seq 256, lr 1e-5, ~3k steps, ~20 min.
- GRPO stager: 1000 steps, 8 prompts × 8 gens = batch 64, grad_accum 2, lr 5e-6, beta 0.02, temp 1.3, 1-token completions, ~45 min.
- GRPO attacker: 500 steps, 4 prompts × 8 gens = batch 32, ≤128-token completions, ~30 min run, 2h budget.
