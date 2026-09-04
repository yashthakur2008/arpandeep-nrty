# Annotated bibliography: "Sleep as a Language" (BrainBodyFM @ NeurIPS 2026)

Built 2026-09-04 from 25 Consensus queries (22 required + 3 gap) and arXiv API checks. Every id below was returned by Consensus or arXiv; entries with an unverifiable *claim* (not id) carry ⚠️ on that claim. Citation counts are Consensus/Semantic Scholar snapshots and will drift.

Design being positioned (from `PLAN.md`): C1 per-night-quantile symbolic PSG tokenizer (one ASCII word per 30 s epoch, ~25 Qwen tokens), C2 SFT Qwen-0.5B stager trained on SHHS1, zero-shot on MESA, C3 mandatory LR/LightGBM/random-init ablation on identical words, C4 GRPO red-teamer editing words under a physiological budget plus metadata-line injection, with a second-scorer test.

---

## (A) Direct baselines we must compare or probe against

### A1. SleepFM: Multi-modal Representation Learning for Sleep Across Brain Activity, ECG and Respiratory Signals
Thapa et al., 2024. arXiv:2405.17766 (ICML 2024). ~59 cit. Journal version: *A multimodal sleep foundation model for disease prediction*, Nature Medicine 2026, DOI 10.1038/s41591-025-04133-4, ~52 cit.
Leave-one-out contrastive pretraining over EEG/ECG/respiratory PSG. arXiv version: 14k participants, LR on embeddings beats end-to-end CNN for staging (macro AUROC 0.88 vs 0.72). Nat Med version: 585k hours / 65k participants, SHHS held out of pretraining, staging mean F1 0.70-0.78, "competitive with U-Sleep and YASA", predicts 130 future diseases. Open source.
**Relevance.** The reviewer seat's first must-cite and the number we will be compared to: F1 0.70-0.78 on staging with a *frozen* encoder plus linear head. Our LR-on-words ablation is the symbolic analogue of their "LR on embeddings" result, so cite it as precedent that a cheap head on a good representation is a legitimate contribution. SHHS was excluded from their pretraining, so their SHHS transfer number is the honest external-cohort comparator. We do not probe SleepFM (no time), say so in limitations.
**Cite in:** intro, related work, results (comparison row), discussion.

### A2. U-Sleep: resilient high-frequency sleep staging
Perslev et al., 2021. npj Digital Medicine, DOI 10.1038/s41746-021-00440-5. ~386 cit.
Fully convolutional U-Net staged on 15,660 PSGs from 16 studies (SHHS and MESA included), arbitrary EEG+EOG channel combinations, matches best human expert on an unseen clinic. Public weights at sleep.ai.ku.dk.
**Relevance.** The canonical cross-cohort staging number. ⚠️ The specific SHHS→MESA per-cohort F1 values are in their supplementary tables, not the abstract; pull them before writing the results table. Because U-Sleep trained on both SHHS and MESA, it is *not* a zero-shot MESA baseline; our MESA number is zero-shot from 200 SHHS nights and must be framed as such. Also cite Fiorillo et al. 2023 (*U-Sleep's resilience to AASM guidelines*, npj Digit Med, DOI 10.1038/s41746-023-00784-0): U-Sleep needs neither recommended derivations nor subject age, which is the opposite of our metadata-injection hypothesis and makes a good foil.
**Cite in:** related work, results, discussion.

### A3. An open-source, high-performance tool for automated sleep staging (YASA)
Vallat & Walker, 2021. eLife, DOI 10.7554/elife.70092. ~327 cit.
LightGBM on hand-crafted per-epoch features (bandpowers, entropy, EOG/EMG stats) trained on 30k+ hours of NSRR data, matches inter-scorer agreement. Also ships spindle and slow-wave detectors.
**Relevance.** Three roles. (1) We use YASA's spindle detector to emit the spindle symbol in C1. (2) YASA *is* the natural non-LLM comparator: feature-based LightGBM. Our C3 LightGBM-on-words row is essentially YASA with a coarser, per-night-quantile feature set. (3) Clinician seat flags YASA's staging classifier was trained on NSRR (likely MESA, possibly SHHS), so it cannot serve as a leak-free second scorer for C4 without checking its training manifest. Use LR-on-words as second scorer instead, cite YASA as the reason.
**Cite in:** method (tokenizer), results (baseline), discussion (leakage caveat).

### A4. A foundational transformer leveraging full night, multichannel sleep study data accurately classifies sleep stages (PFTSleep)
Fox et al., 2025. Sleep, DOI 10.1093/sleep/zsaf061. ~5 cit. (medRxiv 2024, DOI 10.1101/2024.08.02.24311417, ~25 cit.)
Self-supervised transformer over 8 h, 7-signal PSG at 125 Hz; trained on SHHS, WSC, MrOS; tested on MESA, APPLES, MrOS2. Cohen's κ 0.81 held-out, **0.60 on MESA zero-shot**, 0.76 when MESA enters the head's training set. MESA per-class AUPRC W/N1/N2/N3/R = 0.56/0.16/0.40/0.45/0.65 (medRxiv version).
**Relevance.** This is the exact number to beat or match: a 13,888-study foundation transformer trained on SHHS drops from κ 0.81 to 0.60 on MESA. If our 200-night symbolic pipeline lands anywhere near κ 0.55-0.60 on MESA the story is "the cross-cohort gap is mostly cohort/rule shift, not model capacity", which is the clinician seat's decomposition claim. Their MESA N1 AUPRC 0.16 licenses us to report honest N1 numbers without apology.
**Cite in:** related work, results (headline comparator), discussion.

### A5. SLEEPYLAND: trust begins with fair evaluation of automatic sleep staging models
Rossi et al., 2025. npj Digital Medicine, DOI 10.1038/s41746-025-02237-2. ~9 cit.
Open framework, 220k h in-domain + 84k h out-of-domain PSG; SOMNUS soft-vote ensemble reaches macro-F1 68.7-87.2% across 24 datasets, beats best human scorer on DOD-H/DOD-O. No architecture minimizes demographic bias. **Ensemble disagreement predicts scorer ambiguity (AUC 0.83).**
**Relevance.** Two things. Their macro-F1 range 68.7-87.2 is the spread we should place our SHHS/MESA numbers within. Their finding that model disagreement predicts human ambiguity is the justification for the C4 second-scorer test and for reporting attack success only on high-margin epochs.
**Cite in:** results, method (second-scorer rationale).

### A6. Large Brain Model for Learning Generic Representations with Tremendous EEG Data in BCI (LaBraM)
Jiang et al., 2024. ICLR 2024; arXiv:2405.18765. ~455 cit.
VQ neural-spectrum-prediction tokenizer turns EEG channel patches into discrete codes; masked code prediction pretraining on 2,500 h across 20 datasets. Beats task-specific SOTA on abnormal detection, event classification, emotion, gait.
**Relevance.** The learned-tokenizer alternative to our hand-designed symbolic tokenizer. Position: LaBraM's codes are opaque and non-editable; ours are physiologically named and edit-constrained, which is what makes the red-team interpretable. Also cite BENDR (Kostas et al. 2021, Front Hum Neurosci, arXiv:2101.12037, ~392 cit., wav2vec-style contrastive EEG pretraining evaluated on sleep staging) as the earlier "EEG as language modeling" precedent.
**Cite in:** related work.

### A7. BIOT: Cross-data Biosignal Learning in the Wild
Yang et al., 2023. NeurIPS 2023; arXiv:2305.10351. ~296 cit. (NeurIPS DOI 10.52202/075280-3420)
Tokenizes each channel into fixed-length segments, flattens to a "biosignal sentence" with channel and relative position embeddings; handles mismatched channels, variable lengths, missing values; joint pretraining across EEG/ECG/HAR.
**Relevance.** BIOT already framed biosignals as "sentences", so we cannot claim that metaphor. Our difference: BIOT's tokens are continuous patch embeddings consumed by a from-scratch transformer; ours are literal ASCII consumed by an unchanged text LLM. Cite to pre-empt "this is just BIOT".
**Cite in:** related work.

---

## (B) LLM-on-biosignal and time-series-as-text (closest methodology)

### B1. NeuroLM: A Universal Multi-task Foundation Model for Bridging the Gap between Language and EEG Signals
Jiang et al., 2024. arXiv:2409.00101 (ICLR 2025). ~115 cit.
Text-aligned VQ tokenizer (temporal-frequency prediction) turns EEG into discrete tokens fed to a GPT-2-family LLM by multi-channel autoregression; multi-task instruction tuning; 1.7B NeuroLM-XL on 25k h.
**Relevance.** Closest prior work to C1+C2. The reviewer says omitting it "would look naive". Our contrast is sharp: NeuroLM extends the LLM vocabulary with learned neural tokens; we change *nothing* in the LLM and feed ASCII. That is the whole "unchanged text LLM" claim. NeuroLM also reports that its multi-task numbers trail single-task fine-tuning, which supports our "the LLM is one consumer among several" framing.
**Cite in:** intro, related work.

### B2. OpenTSLM: Time-Series Language Models for Reasoning over Multivariate Medical Text- and Time-Series Data
Langer et al., 2025. arXiv:2510.02410. ~23 cit.
Soft-prompt and Flamingo-style cross-attention variants that add time series as a native modality to Llama/Gemma. Introduces Sleep-CoT. **Sleep staging F1: 69.9 (OpenTSLM) vs 9.05 for fine-tuned text-only serialization vs 15.47 GPT-4o.**
**Relevance.** The single most dangerous number for us. OpenTSLM's text-serialized baseline got 9 F1 on sleep staging. Our entire bet is that *their* serialization (raw numbers) is the wrong text, and per-night-quantile symbolic words are the right text. If we clear ~50 macro-F1 on SHHS with pure text we have directly refuted their baseline; if we do not, we must say so. Put their 9.05 in the intro as the motivating gap.
**Cite in:** intro, related work, results, discussion.

### B3. Large Language Models Are Zero-Shot Time Series Forecasters (LLMTime)
Gruver et al., 2023. arXiv:2310.07820 (NeurIPS 2023). ~842 cit.
Encodes series as digit strings, frames forecasting as next-token prediction; GPT-3/LLaMA-2 zero-shot match purpose-built forecasters. Shows tokenization of numbers matters (GPT-4 worse than GPT-3 because of BPE on digits).
**Relevance.** Precedent for "time series as text with no architecture change". Their finding that digit tokenization dominates is exactly why we use single letters per symbol and a single-letter stage vocabulary (`W A B C R`), so `N1` is not two tokens.
**Cite in:** related work, method (token design).

### B4. Chronos: Learning the Language of Time Series
Ansari et al., 2024. arXiv:2403.07815. ~971 cit.
Scale-and-quantize values into a fixed vocabulary, train T5 with cross-entropy on tokenized series; strong zero-shot forecasting across 42 datasets.
**Relevance.** Chronos's tokenizer is *global* mean-scaling plus uniform binning; ours is per-night quantile binning. Cite to name the design axis (what you normalize over) and to argue that per-recording quantiles are the right choice when cohorts differ in amplifier gain and age.
**Cite in:** related work, method.

### B5. Time-LLM: Time Series Forecasting by Reprogramming Large Language Models
Jin et al., 2023. arXiv:2310.01728 (ICLR 2024). ~1139 cit.
Reprograms series patches into text-prototype embeddings for a frozen LLM, prompt-as-prefix.
**Relevance.** The paper Tan et al. (B6) ablated. Cite together with B6 as the pair that made this community suspicious of "LLM for time series" claims.
**Cite in:** related work.

### B6. Are Language Models Actually Useful for Time Series Forecasting?
Tan et al., 2024. arXiv:2406.16964 (NeurIPS 2024). ~294 cit.
Ablates three LLM-for-TS methods: removing the LLM or replacing it with one attention layer does not hurt and often helps; pretrained LLMs no better than from-scratch; no few-shot benefit.
**Relevance.** This is the reviewer's reject sentence in paper form. C3 exists because of it: same words → LR, LightGBM, random-init Qwen. If the LLM does not beat LR on identical inputs we say so in the abstract. Put this in the intro as the standard we hold ourselves to, not as a threat to hide from.
**Cite in:** intro, related work, method (ablation design), discussion.

### B7. Large Language Models are Few-Shot Health Learners
Liu et al., 2023. arXiv:2305.15525. ~180 cit.
Few-shot tuning lets PaLM ground numerical physiological series (HR, HRV, steps) rendered as text for cardiac, activity, calorie, and mental-health tasks.
**Relevance.** Earliest "physiology as prompt text" precedent in health; they serialized aggregate statistics, not raw signals, which is closer to our per-epoch feature words than LLMTime's digit dumps. Cite as the lineage we sit in.
**Cite in:** related work.

### B8. SleepLM: Natural-Language Intelligence for Human Sleep
Xu et al., 2026. arXiv:2602.23605. ~10 cit.
Sleep-language foundation model: 100k h PSG paired with generated multilevel captions from 10k subjects; contrastive + captioning + reconstruction pretraining; zero/few-shot, retrieval, captioning, event localization.
**Relevance.** Most recent "sleep + language" system and a reviewer will ask why ours is not a subset of it. Answer: SleepLM aligns a *signal encoder* to text and needs 100k h; we require no encoder, no paired captions, and 200 nights. Also, SleepLM has no adversarial or shortcut analysis.
**Cite in:** related work, discussion.

### B9. Language Models Still Struggle to Zero-shot Reason about Time Series
Merrill et al., 2024. arXiv:2404.11757. ~110 cit.
Formal benchmark of etiological reasoning, QA, and context-aided forecasting over series+captions; strong LLMs score barely above chance on the first two.
**Relevance.** Supports the decision to SFT rather than prompt. Also frames why a zero-shot LLM baseline (Honnavalli et al. 2025, ICEENG, DOI 10.1109/iceeng64546.2025.11031373, report **44.4% accuracy** for the best of four open LLMs on staging) is not a meaningful comparator; we can quote that 44% as the prompting floor.
**Cite in:** related work, discussion.

---

## (C) Tokenization and discretization

### C1. Experiencing SAX: a novel symbolic representation of time series
Lin, Keogh, Wei, Lonardi, 2007. Data Mining and Knowledge Discovery, DOI 10.1007/s10618-007-0064-z. ~1737 cit.
PAA segment means mapped to equiprobable symbols under a Gaussian assumption, with a lower-bounding distance. Enables text-mining and bioinformatics algorithms on series.
**Relevance.** Our tokenizer is SAX-flavored (segment → symbol), so cite as the root. Our two deviations are (a) symbols are derived features (bandpower ratios, RMS, counts), not raw means, and (b) breakpoints are empirical per-night quantiles, not Gaussian. For (b) cite Butler & Kazakov 2015 (*SAX Discretization Does Not Guarantee Equiprobable Symbols*, IEEE TKDE, DOI 10.1109/tkde.2014.2382882) which shows PAA shrinks variance so Gaussian breakpoints are not equiprobable; per-night quantiles sidestep this and, more importantly, are the cross-cohort normalization bet.
**Cite in:** method, related work.

### C2. Neural Codecs as Biosignal Tokenizers (BioCodec)
Avramidis et al., 2025. arXiv:2510.09095. ~9 cit.
Neural-codec-style discrete tokenizer for EEG pretrained on thousands of hours; downstream includes sleep physiology; analyzes codebook usage and spatial coherence; extends to EMG.
**Relevance.** The learned-discrete-token alternative. Also cite Hypnos (Carter et al. 2026, *Next-Token Prediction Learns Generalisable Representations of Sleep Physiology*, arXiv:2606.09605) which RVQ-tokenizes eight PSG modalities and trains an autoregressive RQ-Transformer, matching supervised staging with 100× fewer labels. Both show discrete tokens are viable for PSG; neither token is human-readable or editable, which is our lever for the red-team and interpretability sections.
**Cite in:** related work, discussion.

### C3. From Values to Tokens: An LLM-Driven Framework for Context-aware Time Series Forecasting via Symbolic Discretization (TokenCast)
Tao et al., 2025. arXiv:2508.09191. ~18 cit.
Discrete tokenizer turns series into temporal tokens embedded alongside text in a pretrained LLM, then supervised fine-tuning to predict future tokens.
**Relevance.** Recent evidence that symbolic discretization is the right bridge into an LLM when text context (for us: demographics, previous stages) must be fused. Their tokens are learned; ours are fixed. Minor cite.
**Cite in:** related work.

---

## (D) Cross-cohort sleep staging and datasets

### D1. The National Sleep Research Resource: towards a sleep data commons
Zhang et al., 2018. JAMIA, DOI 10.1093/jamia/ocy064. ~911 cit.
NSRR: 10 NIH cohorts, 26,808 subjects, 31,166 EDFs, harmonized terminology, XML annotations.
**Relevance.** Data source citation. Also cite the 2024 update (Zhang et al., *Sleep*, DOI 10.1093/sleep/zsae088) for FAIR harmonization. Note for methods: Ahn/Lim et al. 2025-26 (AJRCCM abstract / Sleep Medicine DOI 10.1016/j.sleep.2025.108174) found NSRR respiratory annotations in SHHS/MESA are not AASM-consistent; we do not use respiratory events so this does not bite us, but do not feed arousals (clinician seat).
**Cite in:** method (data).

### D2. The Sleep Heart Health Study: design, rationale, and methods
Quan et al., 1997. Sleep, DOI 10.1093/sleep/20.12.1077. ~1457 cit.
Home PSG on 6,600 adults ≥40 from six parent cardiovascular cohorts. Companion: Redline et al. 1998 (Sleep, DOI 10.1093/sleep/21.7.759) on unattended PSG methods; 75% of studies of sufficient quality for staging, submental EMG the weakest channel.
**Relevance.** Cohort citation. Redline 1998's EMG-quality finding matters for C1: our chin-EMG symbol will be missing or noisy in a meaningful fraction of SHHS nights, so the tokenizer must handle a masked EMG field and we should report the fraction.
**Cite in:** method (data).

### D3. Racial/Ethnic Differences in Sleep Disturbances: The Multi-Ethnic Study of Atherosclerosis (MESA)
Chen et al., 2015. Sleep, DOI 10.5665/sleep.4732. ~886 cit.
MESA Sleep: 2,230 adults aged 54-93, in-home PSG 2010-13, actigraphy, questionnaires; large racial/ethnic variation in SDB, short sleep, sleepiness.
**Relevance.** Cohort citation and the source of the "MESA is older and more diverse than SHHS" statement the clinician seat wants in the discussion. Also cite Saha et al. 2025 (AJRCCM abstract, DOI 10.1164/ajrccm.2025.211.abstracts.a3387) which shows 11 sleep variables differ by race in MESA but not SHHS, a direct warning about attribute bias when our metadata line includes race.
**Cite in:** method (data), discussion.

### D4. Interrater reliability of sleep stage scoring: a meta-analysis
Lee et al., 2022. J Clin Sleep Med, DOI 10.5664/jcsm.9538. ~157 cit.
11 studies: overall κ 0.76; per stage W 0.70, **N1 0.24**, N2 0.57, N3 0.57, R 0.69.
**Relevance.** The ceiling. Any staging number must be read against κ 0.76, and N1 at 0.24 means our N1 F1 will be low for reasons that are not ours. Cite in the same sentence as Bakker et al. 2022 (*Sleep*, DOI 10.1093/sleep/zsac154): only 32-46% of epochs get 100% agreement across 6-12 scorers, "ambiguity is the rule". This is the empirical basis for the C4 rule "report attack success only on confident W/N2/N3/R epochs".
**Cite in:** results, method (second-scorer test), discussion.

### D5. Inter-database validation of a deep learning approach for automatic sleep scoring
Álvarez-Estévez & Rijsman, 2021. PLoS ONE, DOI 10.1371/journal.pone.0256111. ~89 cit.
CNN-LSTM across six public databases: local κ 0.80, **external κ 0.54**, ensemble of local models 0.62.
**Relevance.** Independent evidence that a raw external-cohort drop of ~0.25 κ is normal for well-built models. Together with PFTSleep (A4) it sets the expectation for our SHHS→MESA gap and supports the decomposition (normalization vs rule shift vs residual) rather than "our model is fragile".
**Cite in:** related work, discussion.

---

## (E) Adversarial robustness and red-teaming of biosignal models

### E1. On the Vulnerability of CNN Classifiers in EEG-Based BCIs
Zhang & Wu, 2019. IEEE TNSRE, DOI 10.1109/tnsre.2019.2908955; arXiv:1904.01002. ~99 cit.
Unsupervised FGSM fools EEGNet, DeepConvNet, ShallowConvNet; adversarial examples transfer across architectures and datasets. First adversarial-EEG paper.
**Relevance.** The reviewer flagged this as "verify id before citing": id confirmed (arXiv 1904.01002). Cite as the origin of EEG adversarial work and to make the contrast: gradient perturbations on raw signals vs our symbol-level, physiologically bounded edits. Also cite Meng et al. 2023 (*Adversarial robustness benchmark for EEG-based BCIs*, FGCS, DOI 10.1016/j.future.2023.01.028) for the defense benchmark.
**Cite in:** related work.

### E2. REST: Robust and Efficient Neural Networks for Sleep Monitoring in the Wild
Duggal et al., 2020. WWW 2020, DOI 10.1145/3366423.3380241; arXiv:2001.11363. ~24 cit.
Adversarial training plus Lipschitz (spectral) regularization for single-channel EEG staging: **macro-F1 0.67 vs 0.39** for SOTA under Gaussian noise, 19× fewer params.
**Relevance.** The only prior paper that adversarially trains a *sleep stager*, and it is noise-robustness, not targeted attack. Their 0.39 collapse under noise is a useful anchor: our symbolic tokenizer quantizes away small-amplitude noise by construction, which we can test cheaply. Also cite Yoo et al. 2022 (*Noise-Robust Sleep Staging via Adversarial Training With an Auxiliary Model*, IEEE TBME, DOI 10.1109/tbme.2022.3214269) for class-wise robustness patterns.
**Cite in:** related work, discussion.

### E3. PISmith: Reinforcement Learning-based Red Teaming for Prompt Injection Defenses
Yin et al., 2026. arXiv:2603.13026. ~13 cit.
GRPO-trained black-box attacker against 13 prompt-injection defenses. Finds vanilla GRPO collapses under extreme reward sparsity (most attacks blocked, entropy collapses before success); fixes with adaptive entropy regularization and dynamic advantage weighting.
**Relevance.** Methodological template for C4 and a warning. Our reward (flip − λ·edits, hard-zero on veto) is sparse in exactly PISmith's sense: most edited words will not flip a confident stager. Plan for entropy regularization and advantage re-weighting from step 0; cite PISmith as the reason. Also cite Beutel et al. 2024 (*Diverse and Effective Red Teaming with Auto-generated Rewards and Multi-step RL*, arXiv:2412.18693) for rule-based rewards and a diversity term, which maps onto our per-transition (from→to) attack goals.
**Cite in:** method (attacker), related work.

### E4. Learning to Attack and Defend: Adaptive Red Teaming of Language Models via GRPO (AdvGRPO)
Bullwinkel et al., 2026. arXiv:2606.09701. ~1 cit.
Makes GRPO viable for attacker-defender co-training using dense multi-channel rewards and decoupled advantage normalization; single-turn → multi-turn curriculum.
**Relevance.** Supports the engineer seat's advice that the reward must be dense and multi-term (format gate, edit budget, flip). If time permits for adversarial retraining of the stager (`[T40]`), this is the citation for the co-training loop.
**Cite in:** method (attacker), discussion.

---

## (F) Shortcut learning and clinical validity

### F1. Shortcut learning in deep neural networks
Geirhos et al., 2020. Nature Machine Intelligence, DOI 10.1038/s42256-020-00257-z. ~3389 cit.
Unifying perspective: models adopt decision rules that work on the benchmark and fail on distribution shift; recommendations for OOD testing.
**Relevance.** The canonical citation for the metadata-injection result. If a `tech note: AHI 45` line flips the stager more than any signal edit, that is shortcut learning by definition.
**Cite in:** intro, discussion.

### F2. Shortcut learning in medical AI hinders generalization: method for estimating AI model generalization without external data
Ong Ly et al., 2024. npj Digital Medicine, DOI 10.1038/s41746-024-01118-4. ~100 cit.
Across 13 datasets (X-ray, CT, ECG, notes, auscultation), performance overestimated by up to 20% on average due to hidden data-acquisition bias; proposes a bias-corrected external-accuracy estimate.
**Relevance.** Their ~20% overestimate is the same order as the SHHS→MESA drop in A4/D5. Cite to argue that some of "cross-cohort fragility" is acquisition-bias shortcutting (Compumedics PS-2 vs Somte, 125 vs 256 Hz), which per-night quantile binning is designed to remove.
**Cite in:** discussion.

### F3. The Identity Trap in EEG Foundation Models: A Diagnostic Audit
Lin et al., 2026. arXiv:2606.06647. ~2 cit.
Frozen-representation audit of LaBraM, CBraMod, REVE: subject-identity variance is 13-89× a random null in 12/12 dataset pairs and grows under fine-tuning; aperiodic 1/f is one identity carrier; erasing the identity axis improves within-subject label decoding by +6 to +27 pp.
**Relevance.** Shows EEG foundation models shortcut on *who* the subject is. Per-night quantile normalization is a crude identity-erasure step (it removes per-recording scale and 1/f offset), which gives a mechanistic reason it might help cross-cohort. Cite alongside SleepMaMi (Park et al. 2026, arXiv:2602.07628), which deliberately uses age/sex/BMI as contrastive supervision, as the two poles of "metadata is signal vs metadata is shortcut".
**Cite in:** related work, discussion.

---

## (G) Similar motivation, different method

### G1. SleepVLM: A Rule-Grounded Vision-Language Model for Auditable Sleep Staging
Deng et al., 2026. arXiv:2603.26738. ~0 cit.
Casts staging as visual reasoning over rendered PSG images; outputs stage plus applicable AASM rules plus rationale; releases MASS-EX with expert rule annotations.
**Relevance.** Same goal (auditable, rule-aligned staging), opposite modality (image). Our edit-locus histogram vs AASM criteria is the text-side analogue of their rule audit. Position as complementary, and note ours needs no VLM and no rendered images.
**Cite in:** related work, discussion.

### G2. Staging by the Book: Automatic Sleep Stage Classification Using Scoring Rules
Hardarson et al., 2026. arXiv:2605.22859. ~1 cit.
Deterministic executable-code implementation of AASM logic with natural-language justifications; **κ 0.42** vs 10-scorer majority (0.61 on development set); high N2 recall, low W/N1.
**Relevance.** The floor for "AASM rules as code". If an SFT LLM on symbolic words lands at κ 0.6+ it is well above pure rules while keeping rule-level auditability via edit loci. Also EEG-VLM (Qiu et al. 2025, arXiv:2511.19155) is the CoT-VLM variant of the same idea.
**Cite in:** related work, results.

### G3. Mechanistic Interpretability of EEG Foundation Models via Sparse Autoencoders
Lehn-Schiøler et al., 2026. arXiv:2605.13930. ~3 cit.
TopK SAEs on SleepFM, REVE, LaBraM embeddings; grounds features in abnormality/age/sex/medication; concept steering reveals "encoded but entangled" regimes, e.g. age-pathology confounding where one cannot suppress one concept without corrupting the other; spectral decoder maps latent edits to band signatures.
**Relevance.** Post-hoc interpretability for opaque sleep FMs. Our claim: a symbolic interface makes the same questions (which band drives R→W?) answerable by direct edit rather than by SAE. Their age-pathology entanglement finding is prior evidence that metadata leaks into SleepFM embeddings, which motivates our metadata attack. Note Korznikov et al. 2026 (arXiv:2602.14111) show random-baseline SAEs match trained ones on interpretability metrics, so "SAE-interpretable" is a weaker claim than "editable".
**Cite in:** related work, discussion.

---

## Reading notes: 10 insights that change how we write the paper

1. **OpenTSLM's 9.05 F1 text baseline is the paper's opening line.** The community already believes "PSG as text fails". We are claiming the failure is in *what text*, not *that text*. Lead with that number, then ours.
2. **PFTSleep κ 0.81 → 0.60 (SHHS→MESA) is the comparator, not U-Sleep.** U-Sleep trained on MESA. PFTSleep is the only large model with a clean SHHS-train/MESA-test number and per-class AUPRC (N1 = 0.16). Frame our MESA drop relative to theirs.
3. **Tan et al. is a design constraint, not a threat.** Put the LR/LightGBM/random-init ablation in the abstract regardless of outcome. Reviewers in this lineage reward the honest version; SleepFM itself made its headline with LR on embeddings.
4. **Inter-scorer κ 0.76 with N1 at 0.24 caps everything.** Report per-class F1 and confusion matrices; treat N1 and N2↔N3 flips as scorer noise, not attacks. Bakker's "ambiguity is the rule" plus SLEEPYLAND's disagreement-predicts-ambiguity result justify the confident-epoch filter.
5. **Per-night quantile binning has three independent justifications now**: SAX's equiprobability assumption fails after PAA (Butler & Kazakov), Chronos's global scaling is the wrong axis for cohort shift, and the Identity Trap shows EEG FMs encode per-subject scale/1-f offsets. Say all three in one paragraph; it turns a preprocessing choice into a contribution.
6. **GRPO reward sparsity is a known failure mode with a known fix.** PISmith and AdvGRPO both report vanilla GRPO collapsing on sparse attack rewards. Budget entropy regularization and advantage re-weighting from the first smoke run, and cite them so the reviewer knows we knew.
7. **The metadata-injection attack has prior art on both sides.** SleepMaMi trains *on* age/sex/BMI as supervision; SAE audits of SleepFM find age-pathology entanglement; MESA vs SHHS attribute bias is documented. Our result is not "metadata matters", it is "a stager that never saw the metadata during signal-feature extraction still flips on a text line". Word it that way.
8. **"Biosignal sentence" and "sleep language" are taken** (BIOT, NeuroLingua, Chronos's title, SleepLM). Do not use them as if novel. Our novel object is the *human-readable, edit-constrained* word; lean on that adjective pair.
9. **Two adversarial-sleep papers exist and both are noise-robustness** (REST, Yoo). No prior targeted, physiologically bounded attack on a sleep stager, and none via an LLM policy. That gap sentence can be stated flatly.
10. **Interpretability by editing beats interpretability by SAE right now.** Korznikov et al. show random SAEs match trained SAEs on standard metrics. A histogram of which *named* symbol the attacker edits per (from→to) transition, compared to AASM criteria, is a causal claim SAE papers cannot make. This is the discussion paragraph that earns the "interpretability" word in the title.

---

## BibTeX

```bibtex
@article{thapa2024sleepfm,
  title={SleepFM: Multi-modal Representation Learning for Sleep Across Brain Activity, ECG and Respiratory Signals},
  author={Thapa, Rahul and others},
  journal={arXiv preprint arXiv:2405.17766},
  year={2024}
}
@article{thapa2026sleepfm,
  title={A multimodal sleep foundation model for disease prediction},
  author={Thapa, Rahul and others},
  journal={Nature Medicine},
  year={2026},
  doi={10.1038/s41591-025-04133-4}
}
@article{perslev2021usleep,
  title={U-Sleep: resilient high-frequency sleep staging},
  author={Perslev, Mathias and others},
  journal={npj Digital Medicine},
  volume={4},
  year={2021},
  doi={10.1038/s41746-021-00440-5}
}
@article{fiorillo2023usleep,
  title={U-Sleep's resilience to AASM guidelines},
  author={Fiorillo, Luigi and others},
  journal={npj Digital Medicine},
  year={2023},
  doi={10.1038/s41746-023-00784-0}
}
@article{vallat2021yasa,
  title={An open-source, high-performance tool for automated sleep staging},
  author={Vallat, Raphael and Walker, Matthew P},
  journal={eLife},
  volume={10},
  pages={e70092},
  year={2021},
  doi={10.7554/eLife.70092}
}
@article{fox2025pftsleep,
  title={A foundational transformer leveraging full night, multichannel sleep study data accurately classifies sleep stages},
  author={Fox, Benjamin and others},
  journal={Sleep},
  year={2025},
  doi={10.1093/sleep/zsaf061}
}
@article{rossi2025sleepyland,
  title={SLEEPYLAND: trust begins with fair evaluation of automatic sleep staging models},
  author={Rossi, Alessandro D and others},
  journal={npj Digital Medicine},
  year={2025},
  doi={10.1038/s41746-025-02237-2}
}
@inproceedings{jiang2024labram,
  title={Large Brain Model for Learning Generic Representations with Tremendous EEG Data in BCI},
  author={Jiang, Wei-Bang and Zhao, Li-Ming and Lu, Bao-Liang},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2024},
  note={arXiv:2405.18765}
}
@article{kostas2021bendr,
  title={BENDR: Using Transformers and a Contrastive Self-Supervised Learning Task to Learn From Massive Amounts of EEG Data},
  author={Kostas, Demetres and Aroca-Ouellette, Stephane and Rudzicz, Frank},
  journal={Frontiers in Human Neuroscience},
  volume={15},
  year={2021},
  doi={10.3389/fnhum.2021.653659},
  note={arXiv:2101.12037}
}
@inproceedings{yang2023biot,
  title={BIOT: Biosignal Transformer for Cross-data Learning in the Wild},
  author={Yang, Chaoqi and Westover, M Brandon and Sun, Jimeng},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  volume={36},
  year={2023},
  note={arXiv:2305.10351}
}
@article{jiang2024neurolm,
  title={NeuroLM: A Universal Multi-task Foundation Model for Bridging the Gap between Language and EEG Signals},
  author={Jiang, Wei-Bang and others},
  journal={arXiv preprint arXiv:2409.00101},
  year={2024}
}
@article{langer2025opentslm,
  title={OpenTSLM: Time-Series Language Models for Reasoning over Multivariate Medical Text- and Time-Series Data},
  author={Langer, Patrick and others},
  journal={arXiv preprint arXiv:2510.02410},
  year={2025}
}
@inproceedings{gruver2023llmtime,
  title={Large Language Models Are Zero-Shot Time Series Forecasters},
  author={Gruver, Nate and Finzi, Marc and Qiu, Shikai and Wilson, Andrew Gordon},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2023},
  note={arXiv:2310.07820}
}
@article{ansari2024chronos,
  title={Chronos: Learning the Language of Time Series},
  author={Ansari, Abdul Fatir and others},
  journal={arXiv preprint arXiv:2403.07815},
  year={2024}
}
@inproceedings{jin2024timellm,
  title={Time-LLM: Time Series Forecasting by Reprogramming Large Language Models},
  author={Jin, Ming and others},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2024},
  note={arXiv:2310.01728}
}
@inproceedings{tan2024useful,
  title={Are Language Models Actually Useful for Time Series Forecasting?},
  author={Tan, Mingtian and Merrill, Mike A and Gupta, Vinayak and Althoff, Tim and Hartvigsen, Thomas},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2024},
  note={arXiv:2406.16964}
}
@article{liu2023fewshot,
  title={Large Language Models are Few-Shot Health Learners},
  author={Liu, Xin and others},
  journal={arXiv preprint arXiv:2305.15525},
  year={2023}
}
@article{xu2026sleeplm,
  title={SleepLM: Natural-Language Intelligence for Human Sleep},
  author={Xu, Zongzhe and others},
  journal={arXiv preprint arXiv:2602.23605},
  year={2026}
}
@article{merrill2024struggle,
  title={Language Models Still Struggle to Zero-shot Reason about Time Series},
  author={Merrill, Mike A and others},
  journal={arXiv preprint arXiv:2404.11757},
  year={2024}
}
@inproceedings{honnavalli2025llmsleep,
  title={Large language models for automated sleep staging},
  author={Honnavalli, Akshay and others},
  booktitle={2025 15th International Conference on Electrical Engineering (ICEENG)},
  year={2025},
  doi={10.1109/iceeng64546.2025.11031373}
}
@article{lin2007sax,
  title={Experiencing SAX: a novel symbolic representation of time series},
  author={Lin, Jessica and Keogh, Eamonn and Wei, Li and Lonardi, Stefano},
  journal={Data Mining and Knowledge Discovery},
  volume={15},
  number={2},
  pages={107--144},
  year={2007},
  doi={10.1007/s10618-007-0064-z}
}
@article{butler2015sax,
  title={SAX Discretization Does Not Guarantee Equiprobable Symbols},
  author={Butler, Matthew and Kazakov, Dimitar},
  journal={IEEE Transactions on Knowledge and Data Engineering},
  volume={27},
  number={4},
  year={2015},
  doi={10.1109/TKDE.2014.2382882}
}
@article{avramidis2025biocodec,
  title={Neural Codecs as Biosignal Tokenizers},
  author={Avramidis, Kleanthis and others},
  journal={arXiv preprint arXiv:2510.09095},
  year={2025}
}
@article{carter2026hypnos,
  title={Next-Token Prediction Learns Generalisable Representations of Sleep Physiology},
  author={Carter, Jonathan and others},
  journal={arXiv preprint arXiv:2606.09605},
  year={2026}
}
@article{tao2025tokencast,
  title={From Values to Tokens: An LLM-Driven Framework for Context-aware Time Series Forecasting via Symbolic Discretization},
  author={Tao, Xiaoyu and others},
  journal={arXiv preprint arXiv:2508.09191},
  year={2025}
}
@article{zhang2018nsrr,
  title={The National Sleep Research Resource: towards a sleep data commons},
  author={Zhang, Guo-Qiang and others},
  journal={Journal of the American Medical Informatics Association},
  volume={25},
  number={10},
  pages={1351--1358},
  year={2018},
  doi={10.1093/jamia/ocy064}
}
@article{zhang2024nsrr,
  title={The National Sleep Research Resource: making data findable, accessible, interoperable, reusable and promoting sleep science},
  author={Zhang, Ying and others},
  journal={Sleep},
  year={2024},
  doi={10.1093/sleep/zsae088}
}
@article{quan1997shhs,
  title={The Sleep Heart Health Study: design, rationale, and methods},
  author={Quan, Stuart F and others},
  journal={Sleep},
  volume={20},
  number={12},
  pages={1077--1085},
  year={1997},
  doi={10.1093/sleep/20.12.1077}
}
@article{redline1998shhs,
  title={Methods for obtaining and analyzing unattended polysomnography data for a multicenter study},
  author={Redline, Susan and others},
  journal={Sleep},
  volume={21},
  number={7},
  pages={759--767},
  year={1998},
  doi={10.1093/sleep/21.7.759}
}
@article{chen2015mesa,
  title={Racial/Ethnic Differences in Sleep Disturbances: The Multi-Ethnic Study of Atherosclerosis (MESA)},
  author={Chen, Xiaoli and others},
  journal={Sleep},
  volume={38},
  number={6},
  pages={877--888},
  year={2015},
  doi={10.5665/sleep.4732}
}
@article{lee2022interrater,
  title={Interrater reliability of sleep stage scoring: a meta-analysis},
  author={Lee, Yun Ji and Lee, Jae Yong and Cho, Jae Hoon and Choi, Ji Ho},
  journal={Journal of Clinical Sleep Medicine},
  volume={18},
  number={1},
  pages={193--202},
  year={2022},
  doi={10.5664/jcsm.9538}
}
@article{bakker2022hypnodensity,
  title={Scoring sleep with artificial intelligence enables quantification of sleep stage ambiguity: hypnodensity based on multiple expert scorers and auto-scoring},
  author={Bakker, Jessie P and others},
  journal={Sleep},
  volume={46},
  number={2},
  year={2023},
  doi={10.1093/sleep/zsac154}
}
@article{alvarez2021interdatabase,
  title={Inter-database validation of a deep learning approach for automatic sleep scoring},
  author={{\'A}lvarez-Est{\'e}vez, Diego and Rijsman, Roselyne M},
  journal={PLoS ONE},
  volume={16},
  number={8},
  pages={e0256111},
  year={2021},
  doi={10.1371/journal.pone.0256111}
}
@article{zhang2019vulnerability,
  title={On the Vulnerability of CNN Classifiers in EEG-Based BCIs},
  author={Zhang, Xiao and Wu, Dongrui},
  journal={IEEE Transactions on Neural Systems and Rehabilitation Engineering},
  volume={27},
  number={5},
  pages={814--825},
  year={2019},
  doi={10.1109/TNSRE.2019.2908955},
  note={arXiv:1904.01002}
}
@article{meng2023benchmark,
  title={Adversarial robustness benchmark for EEG-based brain-computer interfaces},
  author={Meng, Lubin and others},
  journal={Future Generation Computer Systems},
  year={2023},
  doi={10.1016/j.future.2023.01.028}
}
@inproceedings{duggal2020rest,
  title={REST: Robust and Efficient Neural Networks for Sleep Monitoring in the Wild},
  author={Duggal, Rahul and Freitas, Scott and Xiao, Cao and Chau, Duen Horng and Sun, Jimeng},
  booktitle={Proceedings of The Web Conference 2020},
  year={2020},
  doi={10.1145/3366423.3380241},
  note={arXiv:2001.11363}
}
@article{yoo2022noiserobust,
  title={Noise-Robust Sleep Staging via Adversarial Training With an Auxiliary Model},
  author={Yoo, Chaehwa and others},
  journal={IEEE Transactions on Biomedical Engineering},
  year={2022},
  doi={10.1109/TBME.2022.3214269}
}
@article{yin2026pismith,
  title={PISmith: Reinforcement Learning-based Red Teaming for Prompt Injection Defenses},
  author={Yin, Chenlong and others},
  journal={arXiv preprint arXiv:2603.13026},
  year={2026}
}
@article{beutel2024redteam,
  title={Diverse and Effective Red Teaming with Auto-generated Rewards and Multi-step Reinforcement Learning},
  author={Beutel, Alex and others},
  journal={arXiv preprint arXiv:2412.18693},
  year={2024}
}
@article{bullwinkel2026advgrpo,
  title={Learning to Attack and Defend: Adaptive Red Teaming of Language Models via GRPO},
  author={Bullwinkel, Blake and others},
  journal={arXiv preprint arXiv:2606.09701},
  year={2026}
}
@article{geirhos2020shortcut,
  title={Shortcut learning in deep neural networks},
  author={Geirhos, Robert and others},
  journal={Nature Machine Intelligence},
  volume={2},
  pages={665--673},
  year={2020},
  doi={10.1038/s42256-020-00257-z}
}
@article{ongly2024shortcut,
  title={Shortcut learning in medical AI hinders generalization: method for estimating AI model generalization without external data},
  author={Ong Ly, Cathy and others},
  journal={npj Digital Medicine},
  volume={7},
  year={2024},
  doi={10.1038/s41746-024-01118-4}
}
@article{lin2026identitytrap,
  title={The Identity Trap in EEG Foundation Models: A Diagnostic Audit},
  author={Lin, Junye and others},
  journal={arXiv preprint arXiv:2606.06647},
  year={2026}
}
@article{park2026sleepmami,
  title={SleepMaMi: A Universal Sleep Foundation Model for Integrating Macro- and Micro-structures},
  author={Park, Keondo and others},
  journal={arXiv preprint arXiv:2602.07628},
  year={2026}
}
@article{deng2026sleepvlm,
  title={SleepVLM: A Rule-Grounded Vision-Language Model for Auditable Sleep Staging},
  author={Deng, Guifeng and others},
  journal={arXiv preprint arXiv:2603.26738},
  year={2026}
}
@article{hardarson2026bythebook,
  title={Staging by the Book: Automatic Sleep Stage Classification Using Scoring Rules},
  author={Hardarson, Emil and others},
  journal={arXiv preprint arXiv:2605.22859},
  year={2026}
}
@article{qiu2025eegvlm,
  title={EEG-VLM: A Hierarchical Vision-Language Model with Multi-Level Feature Alignment and Visually Enhanced Language-Guided Reasoning for EEG Image-Based Sleep Stage Prediction},
  author={Qiu, Xihe and others},
  journal={arXiv preprint arXiv:2511.19155},
  year={2025}
}
@article{lehnschioler2026sae,
  title={Mechanistic Interpretability of EEG Foundation Models via Sparse Autoencoders},
  author={Lehn-Schi{\o}ler, William and others},
  journal={arXiv preprint arXiv:2605.13930},
  year={2026}
}
@article{korznikov2026sanity,
  title={Sanity Checks for Sparse Autoencoders: Do SAEs Beat Random Baselines?},
  author={Korznikov, Anton and others},
  journal={arXiv preprint arXiv:2602.14111},
  year={2026}
}
```

---

## Field scan 2026-09-04 (hardening pass)

Run 16:10-16:25 PDT via Consensus (year_min 2025/2026) and arXiv API (sortBy=submittedDate) on MISSION_REVIEW targets (a)-(e) plus the seven extra queries. Every id below came back from Consensus or the arXiv API; claims are from abstracts only. None of these were in sections A-G.

### (a) Symbolic / feature tokens for EEG or PSG into an LLM

**H1. NeuroCognitor** (Cong, IEEE Access 2025, DOI 10.1109/access.2025.3637315). VQ tokenization of time-frequency EEG segments, adversarial EEG-text distribution alignment without paired data, instruction-tuned causal LLM, sleep staging as one task. Tokens are *learned* codes (codebook ~8k). Closest new threat to "EEG as discrete tokens in a shared vocabulary with a text LLM". Our difference stays: their tokens are opaque codebook ids; ours are named physiological symbols with no codebook training. Cite next to NeuroLM.

**H2. SleepLM (Lei et al., AINIT 2025, DOI 10.1109/ainit65432.2025.11035684)**, not the Xu 2026 SleepLM. VQVAE EEG tokens + text, autoregressive LLM pretraining, fine-tune for staging and seizure. Same lineage as H1. Two unrelated papers now share the name SleepLM; cite both with year to avoid confusion.

**H3. HSQP** (Abdullahi et al., IEEE Access 2026, DOI 10.1109/access.2026.3674765). Plug-and-play symbolic-quantized patching (ABBA symbolic aggregation + affine quantization) for frozen LLMs, forecasting only. Shows symbolic discretization into a frozen LLM is an active 2026 direction; not applied to biosignals or classification. Cite in tokenization paragraph with SAX and TokenCast.

**H4. BLPM** (Cho et al., arXiv:2608.11656, Aug 2026). Argues the opposite bet: "autoregressive modeling creates a mismatch between continuous neural dynamics and discrete token spaces", so they predict continuous latents. Use as the foil that names the design axis we sit on the other side of.

**H5. eNeuroLingua** (Samaee et al., BSPC 2026, DOI 10.1016/j.bspc.2026.110333). "Language-inspired" staging with CNN-tokenized 3 s subwindows and hierarchical transformers, Sleep-EDF/ISRUC only. Not an LLM, not text; confirms "language-inspired" framing is saturated. Do not lean on the metaphor.

### (b) Per-subject / per-night normalization for cross-cohort staging

**H6. Köksal 2026** (Düzce Univ. J. Sci. Tech., DOI 10.29130/dubited.1773372). Direct evidence: subject-aware normalization plus test-time adaptation raised ISRUC macro-F1 by 0.08 and kappa by 0.10 over fold-aware normalization, and record-wise CV overstates macro-F1 by 7-9 points. Small venue, but it is the cleanest "normalization competes with model choice" statement we found. Cite in the per-night-quantile paragraph and in the eval protocol (LONO, never record-wise).

**H7. PSDNorm** (Gnassounou et al., arXiv:2503.04582). Test-time temporal normalization via Monge mapping inside U-Net/transformer stagers, 10k subjects, 10 datasets, SOTA on left-out datasets. The learned-normalization analogue of our per-night quantile bins. Cite as the strong baseline in spirit; note that theirs lives inside the network, ours lives in the tokenizer and so transfers to any consumer (LR, LightGBM, LLM).

**H8. STDA-Net** (Tallal et al., arXiv:2605.06736). Spectrogram CNN-BiLSTM-DANN, six cross-dataset settings among Sleep-EDF/SHHS1/SHHS2, avg macro-F1 87.6. Adds to the "domain adaptation on raw signals" family (ADAST, DDAST). Does not test MESA.

### (c) LLM-removed ablations on time-series / biosignal LLM papers

**H9. Schumacher et al. 2026** (arXiv:2601.03464, *Prompting Underestimates LLM Capability for Time Series Classification*). Zero-shot prompting near chance; linear probes on the same LLM internals reach F1 0.61-0.67. Cuts both ways for us: it licenses SFT over prompting, and it means our "random-init Qwen" row must be reported with a probe, not just with generation, otherwise a reviewer will say we under-measured the decorative baseline.

**H10. He et al. 2026** (arXiv:2601.09971). Hybrid encoder + frozen LLM for TSC; only Inception encoders give consistent gains. Reinforces Tan et al. for classification specifically.

**H11. Zhao et al. 2025** (arXiv:2505.24030, *Are Large Vision Models Useful for Time Series Analysis?*). Same question for LVMs; useful for classification, weak for forecasting. Cite with Tan as the "prove the backbone matters" norm.

### (d) Adversarial edits with physiological constraints

**H12. StageGuard** (Wang et al., KDD 2026, DOI 10.1145/3770855.3818916). Physiology-constrained *decoding* (soft transition penalty + semi-Markov min-bout decoder) that cuts transition-violation rate and fragmentation 56-62% across six backbones. Not an attack, but it is the first paper to formalize "physiologically plausible hypnogram" as a checkable constraint. Our clinician vetoes are the epoch-level analogue; a StageGuard-style decoder is also a natural *defense* against our attacker and should be in the discussion. No prior physiologically bounded *attack* on a stager found (still true after this scan).

### (e) SHHS -> MESA comparator numbers

**H13. Serrano Alarcón et al. 2025** (J Sleep Res, DOI 10.1111/jsr.70266). U-Net on SpO2+HR+abdominal effort, trained SHHS2, external MESA: SHHS2 kappa 0.61 (5-class), "consistent performance on MESA" (exact MESA number not in abstract). EEG-free, so a floor, not a comparator.

**H14. NeuroSleepNet** (Dip et al., IEEE Access 2025, arXiv:2501.00557). In-domain (not zero-shot): MESA acc 82.0 / macro-F1 76.3 / kappa 0.753; SHHS acc 86.7 / macro-F1 80.9 / kappa 0.804. Useful as the in-domain ceiling on each cohort.

**H15. SleepVST** (Carter et al., CVPR 2024, arXiv:2404.03831). Cardio-respiratory only; in-domain kappa 0.75 SHHS, 0.77 MESA. Another in-domain ceiling for non-EEG channels.

**H16. DCA-Sleep** (Li et al., Diagnostics 2026, DOI 10.3390/diagnostics16050802). PPG-only, MESA F1 0.731, kappa 0.652 (mixed-cohort training). Floor for single non-EEG channel.

### Other

**H17. Omni-Sleep** (Hou et al., arXiv:2607.07720) and **sleep2vec** (Yuan et al., arXiv:2602.13857). Two more 100k-hour PSG foundation models (Jul 2026, Feb 2026). sleep2vec explicitly uses age/site metadata in its InfoNCE to "mitigate cohort-specific shortcuts", which is direct prior art that metadata shortcuts exist in PSG FMs. Cite with SleepMaMi and the Identity Trap.

**H18. Hossain et al. 2026** (arXiv:2605.02245). Demographic-stratified fine-tuning improves kappa 0.9-12.9% on DREAMT. Evidence that demographics carry stage information, which is why a metadata line can be a legitimate feature *and* a shortcut; cite when framing the metadata attack.

**H19. Bechný et al. 2025** (Sci Rep, DOI 10.1038/s41598-025-06019-4). Bias framework applied to U-Sleep and YASA finds age-related error shifts. Supports reporting per-age-bin confusion on MESA.

### Comparator table: SHHS-trained, MESA-tested, EEG-based (the row we are compared to)

| Model | Train | Test | kappa | macro-F1 | per-class | Zero-shot? | Source |
|---|---|---|---|---|---|---|---|
| PFTSleep (transformer, 7 ch, 8 h) | SHHS1+2, WSC, MrOS (13,888) | MESA | **0.60** | n/r | AUPRC W/N1/N2/N3/R 0.56/0.16/0.40/0.45/0.65 (medRxiv) | yes | A4, Fox 2025 |
| PFTSleep, MESA in head | + MESA head | MESA held-out | 0.76 | n/r | n/r | no | A4 |
| PFTSleep in-domain | same | SHHS held-out | 0.81 | n/r | AUPRC 0.82/0.40/0.53/0.75/0.82 | n/a | A4 |
| Álvarez-Estévez CNN-LSTM | one DB | other 5 DBs | 0.54 (ext), 0.80 (local) | n/r | n/r | yes (not MESA) | D5 |
| SleepFM Nat Med (frozen + LR) | 65k pts, SHHS excluded | SHHS | n/r | 0.70-0.78 | n/r | yes (reverse direction) | A1 |
| U-Sleep | 16 cohorts incl. SHHS+MESA | MESA | n/r (supp.) | n/r | n/r | no | A2 |
| NeuroSleepNet | MESA | MESA | 0.753 | 0.763 | n/r | no (ceiling) | H14 |
| Serrano U-Net (no EEG) | SHHS2 | MESA | ~0.61 (SHHS2) | wF1 0.68 | n/r | yes | H13 |
| Inter-scorer (meta) | humans | humans | 0.76 | n/r | W/N1/N2/N3/R 0.70/0.24/0.57/0.57/0.69 | n/a | D4 |

Read: the only clean EEG-based SHHS->MESA zero-shot number in print is PFTSleep kappa 0.60 (N1 AUPRC 0.16). In-domain MESA ceilings are kappa 0.75-0.80. Our target band: MESA zero-shot kappa 0.50-0.60 from 500 SHHS nights would tie a 13,888-study foundation transformer; anything above 0.60 beats it. macro-F1 comparators are scarce for this exact split; we report both kappa and macro-F1 so either can be compared.

### Repositioning (after this scan)

Nothing found does (i) named-symbol tokenization that an unchanged text LLM reads, (ii) the cross-cohort drop decomposition, or (iii) a physiologically bounded attack on a stager. Three threats moved closer since the first bibliography: NeuroCognitor and Lei-SleepLM (H1, H2) now make "EEG as discrete tokens in an LLM vocabulary" a crowded 2025 lineage, so the abstract must say *no codebook, no vocabulary change, human-readable* in the first sentence, not the third. Schumacher (H9) means the random-init / frozen-LLM ablation must include a linear probe on hidden states, or the "decorative" test is itself under-measured. StageGuard (H12) means "physiologically plausible" now has a published operationalization; our vetoes should cite it and our discussion should name a StageGuard-style constrained decoder as the obvious defense. Per-night normalization got stronger support (H6, H7): frame it as "test-time normalization moved into the tokenizer so it transfers to every consumer", which is the sentence that separates us from PSDNorm. The comparator is unchanged: PFTSleep kappa 0.60 on MESA.
