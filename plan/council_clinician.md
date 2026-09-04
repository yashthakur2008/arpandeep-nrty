# Council review: sleep medicine / PSG scorer (NSRR SHHS + MESA experience)

## 1. Tokenizer physiology

Sensible core (5 s bandpower x 5 bands, EMG RMS, previous-stage context). Fix these:

- **Slow-wave fraction, not delta power.** The N3 criterion is percent of epoch occupied by slow waves >75 uV peak-to-peak at 0.5-2 Hz. Add one symbol: SW-fraction quantized (0 / <20 / 20-50 / >50%). Delta power alone conflates sweat artifact, movement, and true slow waves.
- **EMG must be night-relative.** REM is atonia relative to the night's own floor, not an absolute level. Quantize per night (percentiles), not fixed levels. Absolute RMS is also incomparable across SHHS (125 Hz, Nyquist 62 Hz) and MESA (256 Hz): bandpass both to 10-50 Hz before RMS.
- **EOG SAX at 16 segments (1.9 s each) cannot see REMs** (<500 ms sharp deflections) and only weakly sees SEMs (0.2-0.6 Hz). Add: REM count per epoch, SEM flag, and L/R phase sign (out-of-phase = real eye movement, in-phase = EEG bleed-through). Without this, REM detection rests on EMG alone.
- **Spindle flag is fine (YASA detector). K-complex flag is weak on C4.** K-complexes are frontal-maximal. MESA has Fz-Cz, SHHS has no frontal channel, so the K symbol will be systematically sparser in SHHS. That is a cohort confound, not a finding.
- **Alpha:** wake alpha is occipital. C4 shows little; MESA Cz-Oz shows plenty, SHHS has none. Same confound. Use only C4 on both cohorts for the main result.
- **Redundant:** the 32-segment raw-envelope SAX (~32 chars) duplicates bandpower + EMG. Drop it. The 30 SpO2 digits are useless for staging (SpO2 lags 20-30 s and is unrelated to stage). Replace with min / mean / desaturation flag (3 chars).
- **Add:** hours-since-lights-off (N3 dominates early, REM late; the single most useful cheap feature).

## 2. Channels, sampling rates, labels

- **SHHS1 EDF labels:** `EEG` (C4-A1, 125 Hz), `EEG(sec)` (C3-A2, 125 Hz; label varies across records: `EEG 2`, `EEG(SEC)`, `EEG2`), `EOG(L)` / `EOG(R)` 50 Hz, `EMG` 125 Hz, `ECG` 125 Hz, `SaO2` 1 Hz, `H.R.` 1 Hz. Compumedics PS-2. Some SHHS2 records have EEG at 128 Hz.
- **MESA EDF labels:** `EEG1` (Fz-Cz), `EEG2` (Cz-Oz), `EEG3` (C4-M1), all 256 Hz; `EOG-L` / `EOG-R` 256 Hz; `EMG`, `EKG` 256 Hz; `SpO2` 1 Hz. Compumedics Somte. Not sure of the MESA EOG reference (Fpz?) versus SHHS EOG referenced to contralateral mastoid: verify in the NSRR montage documentation.
- A1/M1 are the same electrode, so C4-A1 (SHHS) and C4-M1 (MESA) are equivalent derivations. Good.
- **NSRR XML stage format:** `<ScoredEvent><EventType>Stages|Stages</EventType><EventConcept>...</EventConcept><Start>...</Start><Duration>...</Duration></ScoredEvent>` with concepts `Wake|0`, `Stage 1 sleep|1`, `Stage 2 sleep|2`, `Stage 3 sleep|3`, `Stage 4 sleep|4`, `REM sleep|5`, `Unscored|9`. Duration covers multi-epoch runs, so expand by Duration/30. SHHS (R&K, scored 1990s) contains 3 and 4; MESA (AASM 2007) contains only 3. Map 3+4 -> N3. Rare `Movement|6` in SHHS: drop those epochs.
- **Arousals are separate events**, not stage changes: `Arousal|Arousal ()`, `ASDA arousal|Arousal (ASDA)`, `Arousal resulting from respiratory effort|Arousal (ARO RES)`, `Spontaneous arousal|Arousal (ARO SPONT)`. Do not feed them to the stager (label leak: arousals cluster in N1/W transitions).
- **Gotchas:** XML epoch count is often less than EDF duration (trim to the minimum); leading and trailing `Unscored` epochs; `SaO2` dropouts (0 or <50 = artifact, mask them); SHHS records start before lights-off (long initial W runs); some MESA nights are near-all-W or mostly unscored (failed studies). Exclude nights with TST < 3 h.
- **Biggest systematic gap:** MESA participants are older (mean ~69 vs ~63) and were scored under AASM with a frontal derivation available, so N3 prevalence and N1 boundary rules differ. Report per-class confusion matrices. A raw MESA accuracy drop is mostly scoring-rule and cohort shift, not model fragility, and the paper must say so.
- YASA's staging classifier was trained on NSRR data that I believe includes both MESA and SHHS. Its spindle/SW detectors are fine to use for symbols, but do not present YASA staging as a leak-free baseline without checking its training manifest.

## 3. Physiologically plausible perturbation budget

- At most 10% of symbols edited; each edit at most ±1 quantization level; adjacent 5 s windows may differ by at most 1 level (continuity constraint).
- Hard vetoes (reward = 0, not just a penalty): spindle symbol in W or REM without elevated sigma in the same window; atonia outside REM; SpO2 fall >2%/s or rise >4%/s; a >=3% desaturation without a >=10 s respiratory event upstream; N3 edits must keep the SW-fraction symbol consistent with the delta symbol.
- **Second-scorer test.** An independent feature-based stager (or YASA) must still assign the edited epoch its original stage. If it does not, the attacker produced a legitimately ambiguous epoch, not an attack. Inter-scorer kappa is ~0.75 overall and N1 agreement is ~50%, so N1<->N2 and N2<->N3 flips from small edits are scorer noise, not exploits. Report attack success only on confident W / N2 / N3 / R epochs (for example where the second scorer's margin is high).
- Metadata attacks (age, BMI, AHI, "tech note") are fully plausible with zero signal edits, and they are the clinically alarming ones.

## 4. What this community would find interesting

- The stager flipped by metadata text more than by signal edits. That is shortcut learning and is publishable on its own.
- The attacker's learned edit loci mirroring AASM criteria (EMG symbol for R->W, sigma/spindle symbols for N2->N1, SW-fraction for N3->N2). That is an interpretability story clinicians will understand.
- Cross-cohort drop decomposed: how much vanishes with per-night normalization and N3-rule harmonization alone, versus what adversarial training recovers. Most "fragility" papers skip this and the community knows it.
- Honest N1 numbers with per-class F1, not just macro-F1.

## Flagged uncertainties

- Exact MESA EOG reference electrode.
- Whether YASA's staging training set included SHHS (MESA is likely).
- Exact SHHS `EEG(sec)` label variants across the release.
- SHHS2 sampling-rate variants (125 vs 128 Hz).
