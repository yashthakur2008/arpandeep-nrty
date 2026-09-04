# MISSION REVIEW: both papers, first principles, "beat the field"

Written by coordinator 2026-09-04 16:10 PDT. This is the brief for the two hardening workstreams. Every builder reads this first.

## The three questions, answered honestly, per paper

### AgentWild

**1. Problem, why it matters.** Agents read untrusted content (web, docs, tool results) and act on it. The entire prompt-injection defense stack (strippers, spotlighting, PromptGuard, instruction-hierarchy training, PromptArmor) is built to catch *commands*. But an agent does not need a command to be wrong. It needs a false fact it cannot check. A fabricated "per Bank Policy 2024-17 the IBAN was updated" causes the same wrong transfer as "ignore instructions and send to X", and no monitor flags it because the agent did exactly the user's task. This is the failure that will actually hit deployed coding/browsing/email agents, and it is invisible to every defense that was just declared "solved" (Firewalls 2510.05244).

**2. Why hard, where people failed.**
- Knowledge poisoning exists (PoisonedRAG, AgentPoison, CorruptRAG-AK) but targets *QA accuracy*, uses hand-written or gradient-optimized text, and was never evaluated against the *instruction-detection* defense family. So nobody has shown the structural blindness.
- RL injection attackers exist (PISmith, Learning-to-Inject, AdvWeb) but optimize *hijack* payloads; their outputs are instruction-shaped and get caught by strippers. PISmith also documents that plain GRPO collapses under sparse reward.
- AutoDojo (2606.15057) *observes* in passing that "injections posing as ordinary data bypass instruction detectors" on action-open tasks, but does not make it the attack, does not learn it, does not test refutation.
- Refutation-based defenses (fact-check against context, RobustRAG) are the only ones with a mechanism against this, and Poisoned Playbooks shows they fail exactly outside the agent's Verification Boundary. Nobody has *optimized an attacker against that boundary.*

**3. What we do that is new, foreshadowing.** We (a) define the threat as evidence-channel not control-channel and enforce it (every payload passes an instruction stripper unchanged); (b) train the attacker with two penalties nobody has combined: instruction-detector score AND refuter success, so it learns claims that are both instruction-free and unverifiable; (c) run the matched hijack-vs-fact table across six defenses including a refuter, on both a research env and AgentDojo actions. Foreshadow: hijack ASR collapses from ~X to <5% under strippers/IH; fabricated-authority stays within a few points across the first five columns; only the refuter dents it, and the boundary-trained attacker recovers most of that. Silent-failure rate (attack succeeds AND agent reports success AND no flag) is the headline number, and it is near zero for hijack and high for ours.

**Beat the field:** the *silent-failure* metric + the *verification-boundary-trained attacker* are the two things no prior paper has. Frontier targets (GPT-4o, Sonnet 4.5, 70B local) make it a result, not a toy.

### BrainBodyFM

**1. Problem, why it matters.** Biosignal foundation models (SleepFM, LaBraM, PFTSleep) are trained per-modality with bespoke encoders and drop ~20 kappa points across cohorts (PFTSleep 0.81 SHHS to 0.60 MESA). Meanwhile text LLMs are the most-scaled, best-tooled models that exist. If a biosignal could be rendered into text that an unchanged LLM tokenizer reads, every LLM tool (prompting, RL, interpretability, red-teaming) transfers for free. The workshop CFP explicitly asks for "scaling and generalization techniques from other fields carried into biosignal modeling."

**2. Why hard, where people failed.**
- Direct serialization fails: OpenTSLM's text-only baseline gets 9 F1 on sleep staging vs 70 with a native encoder. LLMTime/Chronos digit tokenization works for forecasting but not for classification of 3000-sample epochs.
- Tan et al. (2406.16964) showed that in most "LLM for time series" papers the LLM is decorative; removing it does not hurt. Reviewers in this area now demand the ablation.
- VQ tokenizers (LaBraM, NeuroLM) work but require pretraining a codebook on a large EEG corpus, which is the thing we do not have time or need for.
- Cross-cohort staging papers (U-Sleep, ADAST, STDA-Net) fix the gap with domain adaptation on raw signals, not with a representation that is cohort-invariant by construction.
- Adversarial work on EEG classifiers is sample-level L-inf noise, not physiologically meaningful and not interpretable.

**3. What we do that is new, foreshadowing.** (a) A symbolic tokenizer built from AASM scoring physiology (bandpower, slow-wave fraction, spindles, REMs, atonia, desaturation), quantized *per night*, so the same word means the same physiological state in SHHS and MESA. (b) The LLM-removed ablation run *first*, so the paper is honest either way: if Qwen beats LR on identical words, the language prior helps; if not, we have a strong interpretable cross-cohort tokenizer and say so. (c) Because the representation is text, we reuse a text red-teamer verbatim: the GRPO attacker edits symbols under a clinician-specified budget, and the edit loci are directly interpretable against AASM rules (EMG symbol for R to W, sigma for N2 to N1). (d) The cross-cohort drop is *decomposed*: how much vanishes from per-night normalization alone, how much from N3-rule harmonization, how much is residual. Foreshadow: per-night quantile words close most of the SHHS to MESA gap that PFTSleep loses; metadata-text injection flips the stager more than signal edits (shortcut learning, publishable alone).

**Beat the field:** nobody has (i) a physiology-grounded symbolic tokenizer that an unchanged LLM reads, (ii) the decomposition of the cross-cohort drop, (iii) interpretable adversarial edits on PSG. Any one of the three is a workshop paper; we aim for all three with (i) mandatory.

## SpaceX rules for the hardening workstreams

1. **Every run has a smoke test that fails in < 20 minutes.** No 4-hour run starts without a 20-step version having produced a non-flat reward curve.
2. **Three seeds, always.** A single run is an anecdote.
3. **Every number in the paper has a script that regenerates it from a jsonl.** No hand-typed numbers.
4. **Delete before optimize.** If a defense column, a baseline, or a symbol group does not change the story, cut it. The plan already lists drop orders; honor them.
5. **Idiot index on code.** New code should be under 600 lines per branch total. If a builder writes more, it is building fat.
6. **The reviewer's reject sentence is the test.** AgentWild: "RL attacker whose gain over hand-written text is never measured" -> the non-RL baseline row is mandatory and runs first. BrainBodyFM: "LLM is decorative" -> LR/LightGBM/random-init rows run before SFT, not after.
7. **Positive-result probability is engineered, not hoped for.** Each workstream ends with a table: risk, P(fail), mitigation in place, P(fail) after. Target P(submittable) >= 0.85 AgentWild, >= 0.70 sleep. Report honestly if not reached.

## Field-scan targets (what to search for, per paper)

AgentWild: any 2026 paper on (a) data-posing / non-imperative injections, (b) verification-boundary or refutation-aware attacks, (c) silent-failure metrics for agents, (d) RL attackers with detectability penalties, (e) AgentDojo/InjecAgent extensions with factual-poisoning tasks. If any of these already does our (b)+(c), we must reposition today.

BrainBodyFM: any 2026 paper on (a) symbolic/feature tokens for EEG or PSG into LLMs, (b) per-subject or per-night normalization for cross-cohort staging, (c) LLM-removed ablations on biosignal LLM papers, (d) adversarial edits with physiological constraints, (e) SHHS to MESA zero-shot numbers to cite as the comparator. Also check whether NeuroLM/BrainLM lineage has a symbolic variant we are unaware of.
