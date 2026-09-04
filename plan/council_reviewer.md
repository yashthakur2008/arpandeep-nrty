# Review: "Sleep as a language" (Loki -> BrainBodyFM pivot)

Reviewer persona: senior NeurIPS reviewer, biosignal foundation models (SleepFM / LaBraM / BENDR lineage).

**Predicted score: 4/10** (workshop scale; 5 is borderline accept). Fixable to 6 with the ablation below.

**Reject sentence:** "The paper's central claim rests on an LLM staging sleep from serialized text, but never shows the LLM contributes anything over a logistic regression on the same symbols, so the 'language' framing is decorative and the red-team result characterizes the tokenizer, not the model."

## Q1. Scope / gimmick

Half in scope. A discrete symbolic PSG tokenizer is a legitimate representation question for this workshop. "A text LLM can consume it" is the gimmick, and this community has already been burned: Tan et al. "Are Language Models Actually Useful for Time Series Forecasting?" (2406.16964) showed that removing or randomizing the LLM in Time-LLM (2310.01728) / LLMTime (2310.07820) pipelines doesn't hurt. Your own brief concedes OpenTSLM (2510.02410) got 9 F1 with text serialization. Reframe: the tokenizer is the object of study, the LLM is one consumer among several.

The red-team contribution is more novel, but as written the attacker edits *symbols*, and symbolic edits are not invertible to signals. So "cross-cohort fragility" is fragility of the interface, and a reviewer will say so unless you either (a) constrain edits to ones realizable by a signal perturbation, or (b) frame it explicitly as an interface robustness study.

## Q2. Biggest 32h risk

Two, in order:

1. **Method collapse.** A 1-token action with 0/1 exact-match reward makes GRPO a high-variance REINFORCE approximation of cross-entropy. A reviewer will write "this is SFT with extra steps." Don't train the stager with GRPO. SFT it, save the GPU hours.
2. **Engineering.** NSRR token not on the machine, EDF+XML parsing for two cohorts with different montages/sampling rates, YASA feature extraction, all before any training starts. Budget 10 of 32 hours for this or you will not have a stager by hour 12 and the pivot clause triggers by default. The attacker (Qwen-0.5B rewriting 100-char strings under an edit budget with a plausibility penalty) is the least certain to converge in one night of GPU.

## Q3. Cut one, add one

**Cut:** the learned BPE "sleep grammar" ablation. Zero chance it changes the story in 32h and it invites tokenizer-noise confounds.

**Add:** the Tan-style "LLM removed" ablation. Same symbolic words -> logistic regression / LightGBM, and Qwen with shuffled or randomly initialized weights. If the LLM does not beat LR on identical inputs, say it in the abstract and pivot the paper to "a symbolic tokenizer that is attackable and interpretable," which is a fine workshop paper. Also run attack transfer against a small CNN on raw signals through the same interface, which tells you whether the attacker found tokenizer holes or LLM holes.

## Q4. Must-cite

- SleepFM, Thapa et al. 2405.17766 (multimodal PSG FM, SHHS/MESA-style cohorts). Direct baseline; reviewers from this lineage will ask why not probe it.
- LaBraM, Jiang et al. ICLR 2024 (VQ neural tokenizer for EEG). Arxiv id: unsure, cite OpenReview.
- NeuroLM, Jiang et al. 2409.00101 (EEG tokens fed to an LLM, multi-task). Closest prior work to C1; omission would look naive. Moderately confident on id.
- BENDR, Kostas et al. 2101.12037. BIOT, Yang et al. 2305.10351.
- U-Sleep, Perslev et al. npj Digit. Med. 2021 (SHHS->MESA cross-cohort staging numbers you will be compared to).
- Chronos 2403.07815, LLMTime 2310.07820, Time-LLM 2310.01728, Tan et al. 2406.16964.
- SAX: Lin, Keogh, Lonardi, Chiu, DMKD 2007 (no arxiv). YASA: Vallat & Walker, eLife 2021.
- Health-signal-as-text: Liu et al. "LLMs are Few-Shot Health Learners" 2305.15525.
- EEG adversarial robustness: Zhang & Wu 2019 on CNN BCI vulnerability. Not confident of the arxiv id, verify before citing.

## Overall

Probability this lands as an accept if you add the ablation and drop GRPO-for-stager: ~50%. Most likely way I'm wrong: the workshop is small and lenient, and the red-team interpretability plots carry it regardless.
