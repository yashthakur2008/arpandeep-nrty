# Seat: ML safety reviewer (NeurIPS / AIWILD repeat reviewer)

## The claim, reconstructed

When a user fabricates an approval, exemption, or superseding policy, small production models call a forbidden tool 14% of the time, and a single system-prompt sentence declaring user- or tool-supplied exemptions non-authoritative drives that to 0/288 for user-message attacks but only halves it when the same claim arrives via a poisoned tool result.

The short paper never states this in one place. The abstract comes closest but spreads it over four sentences ("fabricated authority raises logged tool-call violations from 0/240 ... to 208/1440", "A provenance-aware policy ... has 0/288 direct user-message violations", "a forced indirect-channel study breaks the same policy in 15/36"). The nearest single sentence is the last one of the abstract, and it is a recommendation, not the claim: "agent evaluations should score tool logs, and deployment prompts should explicitly reject unauthenticated authority claims while treating tool-output provenance as a separate run-time security problem." The regular paper does better: "The central finding is that policy wording can dominate the outcome" (Intro, para 4), followed by the 0/288 vs 93/288 numbers. Port that sentence into the short paper's Section 1 or 3 opener.

## Reasons to reject

1. **The mitigation is never shown.** The short paper's deliverable is "one sentence" that takes violations from 32% to 0%, and the sentence does not appear in the short paper. It appears only in Fig 4 (unplaced) and the regular paper Section 3. Table 2's caption paraphrases it. A reviewer cannot evaluate a one-sentence defense they cannot read. Fixable: yes, 40 words. Quote it verbatim in Section 2.

2. **The headline policy effect is pooled across two models when it is almost entirely one model.** claude-haiku-4-5 has 10 violations total across 720 attacked trials; gpt-4o-mini has 198. Table 2's 93/288 for `exemption` is therefore roughly 85 to 93 out of 144 gpt-4o-mini trials plus a handful of haiku. "Policy phrasing dominates" is a gpt-4o-mini result presented as a two-model result. The regular paper's gpt-4.1-mini replication (0/48 vs 30/48) is exactly what the short paper needs and it is absent from it. Fixable: yes. Add a per-model column to Table 2 (or Fig 2a split bars) and one sentence on gpt-4.1-mini.

3. **Independence assumption in every Fisher test is violated.** Each 288-trial cell is 8 scenarios × 6 attacks × 2 models × 3 repeats. Temperature is never stated in either paper. If temperature is 0 or low, the 3 repeats are near-duplicates and the effective n is 96, not 288; the scenario × attack structure further clusters outcomes. The p-values of 1e-32 will survive any correction, but the paper reports them as if trials were iid, and the length-control p = 0.000361 (11/96 vs 0/96, i.e. 32 cells × 3) is the one that could soften. Fixable: partially. State temperature; report per-cell (any-of-3) rates alongside per-trial rates, or a permutation test over cells. One evening.

4. **Missing prior work that a hostile reviewer will hit immediately.** No AgentDojo (Debenedetti et al. 2024), no InjecAgent (Zhan et al. 2024), no AgentHarm (Andriushchenko et al. 2024), no Instruction Hierarchy (Wallace et al. 2024), no spotlighting (Hines et al. 2024), no PAP / "How Johnny can persuade LLMs" (Zeng et al. 2024) whose persuasion taxonomy includes authority endorsement. The forced-lookup study is AgentDojo-lite; the provenance clause is a prompt-level instruction-hierarchy defense; the attack templates overlap PAP's authority category. Section 1's "This separates our contribution from ..." lists three text-jailbreak papers and two judge papers, which is the wrong comparison set. Fixable: yes, one paragraph and 6 citations. Must be done or the novelty section reads as unaware.

5. **The adaptive-attacker language outruns n = 8.** "The clause survives an adaptive attacker" and "never breached" rest on 8 scenarios × 8 rounds with a gpt-4o-mini attacker against (presumably, not stated) a gpt-4o-mini defender, 64 attempts total. The 0/8 upper Wilson bound is 32%; pooled 0/16 is 19%. No GCG, no PAIR/TAP tree search, no best-of-n sampling, no attacker from a different family. AutoInject [8], which the paper cites, is a stronger adaptive baseline and was not run. Fixable: partially. Soften to "resists a single-stream 8-round LLM attacker that breaks the control"; state defender model; if time, run PAIR-style 20 × 3 streams on 4 scenarios.

6. **Count inconsistencies across abstract, figures, and drafts.** (a) Abstract says "6 operating-policy phrasings"; Table 2 and Fig 1 show 5; the sixth is `strict_verbose`, run on one model only. (b) "7 attack templates" is 6 attacks plus the no-attack control (1440/240 = 6; Fig 2c shows 6 bars). (c) Short paper per-model rates use denominator 840 (controls included); Fig 5 uses 720. 198/840 = 23.6% in text vs ~27.5% in the figure. (d) Indirect study: short paper 15/36 and 51/72; regular paper 8/24 and 32/48; Fig 3 and Fig 6 use 36. These are different runs and the drafts do not say so. (e) Fig 4 says provenance attacks score "43–52/240"; regular paper says "43/240 to 68/240". Fixable: yes, an hour with the JSON files. Must be done; a reviewer who finds two of these stops trusting the rest.

7. **Section 1 is a different paper.** One quarter of a 4-page paper, and its only table, are about a judge-validation result the regular paper itself says is "not novel". See "The opening section" below. Fixable: yes, cut to three sentences.

8. **Setup is too thin to reproduce or to satisfy the advisor's standard.** Section 2 is five lines. The five policies are named but never described in the short paper (`bare`, `autonomous`, `strict_hatch` are opaque; "hatch" is never explained). The "paired trials" design behind 32/432 is never described. The violation predicate is never defined. The judge validation's human labelling protocol (how many annotators, agreement) is absent. Fixable: yes, if space is freed by cutting Section 1. Add a 5-row policy table (regular paper Table 1) and one sentence per experiment on what "paired" means.

9. **"Largest lever is the deployer's policy wording" is asserted, not shown.** Model choice is a 20× lever in the same data (10 vs 198). Policy is 0 vs 93. Both are large; neither is compared in a common effect size. Fixable: yes. Say "policy wording is a lever comparable in size to model choice, and unlike model choice it is free."

10. **Attacker/defender family confound.** Attacker is gpt-4o-mini, and the models that fail are OpenAI minis. Haiku barely fails at all. The "adaptive attacker" result may partly reflect that gpt-4o-mini cannot write attacks that beat its own refusal training. Fixable: no by deadline; state as limitation (regular paper already lists it as a next step).

## Novelty check

- **DarkCite** (Yang et al. 2024): fabricated citations and authority to jailbreak text output. Overlap: attack ingredient is fabricated authority. Difference: DarkCite's authority is epistemic ("a paper says X is fine"); here it is procedural ("an approval exists"). DarkCite has no defender-side variable and no tool outcome.
- **PAP / Zeng et al. 2024** (uncited): persuasion taxonomy including "authority endorsement". Same gap: text, no policy variable.
- **AutoInject** [8]: automated prompt injection against tool agents. It is a stronger attacker than what this paper runs; this paper does not compare against it despite citing it.
- **AgentDojo / InjecAgent** (uncited): injection through tool outputs with tool-call outcomes and defense baselines. The forced-lookup experiment is a subset of AgentDojo's threat model, at 1/50 the scale.
- **Instruction Hierarchy / spotlighting** (uncited): the provenance clause is a prompt-level instruction-hierarchy defense. Both papers report that prompt-only defenses are partial. This paper agrees (channel-specific).
- **GAP / AgentSeer** [6, 7]: policy-following benchmarks; establish that text safety does not transfer to tools. This paper's 32/432 refusal-while-calling result is a small replication.

What a hostile reviewer says: "DarkCite on tools, with an instruction-hierarchy sentence as defense, evaluated on eight hand-written scenarios and one weak model. AgentDojo already showed prompt defenses are partial."

What is actually new: the independent variable is the deployer's policy phrasing, held fixed across identical attacks, and the finding is non-monotonic: a documented-exemption carve-out (a realistic thing engineers write) is worse than no mention of exemptions at all, and the fix is not length. Nobody in the list above manipulates the operator's policy text as a variable or reports that the carve-out itself is the attack surface.

One-sentence answer: "DarkCite varies the attack; we hold the attack fixed and vary the operator's policy contract, and show the carve-out clause, not the attacker's creativity, determines whether the tool fires."

## Statistics

- **n per cell.** Main sweep: 8 × 5 × 7 × 2 × 3 = 1,680; attacked 1,440 (6 attacks), control 240. Per policy: 288 attacked (144 per model, 48 per model-attack, 6 per scenario-attack-model, 3 per cell). Length ablation: 96 per policy on gpt-4o-mini. Matched contrast: 18 = 3 attacks × 6 repeats, one scenario, one model. Adaptive: 8 scenarios, 8 or 10 rounds. Indirect: 36 or 24 per policy depending on which draft you read. Paired gap: 432 (144 control, 288 attacked).
- **Test.** One-sided Fisher exact everywhere. Direction is never justified as pre-specified; one-sided is defensible for "attack increases violations" but should be stated once as a design choice. Arithmetic spot-checks pass: 0/8 vs 8/8 gives 1/C(16,8) = 7.8e-5; 0/8 vs 7/8 gives 9/12870 = 7.0e-4; Wilson upper for 0/288 is z²/(n+z²) = 1.32%.
- **Multiple comparisons.** None applied. At least nine Fisher tests are reported in the short paper. Bonferroni at 9 leaves every reported p below 0.004 significant, so this is a presentation issue, not an outcome issue. Say so in one clause.
- **Independence.** The real problem (Reason 3). 3 repeats per cell at unstated temperature, plus scenario × attack clustering. Report temperature. Report a cell-level analysis: 96 cells per policy, "any violation in 3" or a permutation test over cells. If the 0/288 becomes 0/96 cells vs 31+/96 cells the story is unchanged and the stats become defensible.
- **0/288 with Wilson.** Presented honestly in Table 2 and Fig 2a; the CI is shown and "0/288" is not called "eliminates" in the short paper. The regular paper's conclusion says "eliminates direct user-message violations", which the CI does not support; change to "drives to zero in our sweep (upper bound 1.3%)".
- **Adaptive n = 8.** "Survives", "never breached", "informative null" are too strong. The informative-null argument (attacker beats control 8/8) is valid and should be kept, but the wording should carry the 32% upper bound. The replication at 10 rounds helps and is correctly reported.
- **Per-model rates.** 198/840 and 10/840 in the text pool controls into the denominator; Fig 5 uses 720. Pick 720.
- **"6 of 10 attacked trials"** (Section 3, models paragraph) is not a count from any cell in the design (cells are 144 per model-policy). Replace with the actual fraction.
- **Judge validation.** 200 human labels, κ reported for judges vs human but no inter-annotator agreement, no annotator count. If one author labelled, say so.

## The opening section

**Case that it is a strength.** It is honest, it is the actual origin of the design, and it makes the methodological point concrete: an LLM judge produced a 69-point ASR swing on identical outputs, so the paper measures a predicate on tool logs instead. Reviewers at this workshop have seen many ASR-inflation papers and will respect the confession. It also pre-empts "why no LLM judge?".

**Case that it is a weakness.** It is 25% of a 4-page paper and its only numbered table, about an experiment that the regular paper explicitly calls "not novel" and that uses a 3B judge nobody would defend as a baseline (HarmBench's classifier and gpt-4o existed). The reader finishes page 1 knowing about GRPO, tag compliance, and llama3.2 judge precision, and still does not know what "fabricated authority" attacks look like, what the five policies say, or what the provenance clause is. The title says "Policy Provenance"; page 1 says "judge error". It reads as two papers, and the advisor's standing complaint ("more and more terms not previously defined, not clear what the result is at any point") applies exactly to page 1: GRPO, ASR, κ, tag compliance, held-out behaviors, all before the first sentence about agents.

**Decision.** Weakness, as currently placed. Cut Section 1 to three sentences at the top of Setup: "We first built a GRPO text attacker scored by an LLM judge; validating the judge on 200 human-labelled outputs showed the 25→48% gain was judge error (the judge reported 83% ASR where humans found 19%; with a validated judge the attacker showed no effect, p = 1.00). We therefore measure a predicate on the tool-call log and use no LLM judge. Details in Appendix A." Move Table 1 to the appendix. Spend the recovered half page on the policy table, the quoted clause, and a per-model split. The honesty survives; the lede does not get buried.

## What is strong and must be protected

- **The non-monotonic ordering, `bare` 21/288 < `exemption` 93/288.** A prohibition with a documented-exemption carve-out is worse than a prohibition alone. This is the one result that is a deployment finding rather than a benchmark number, and it survives the matched contrast (0/18 vs 18/18) and the length control (98-word irrelevant policy: 11/96). Keep all three together.
- **Zero control floor, and the refusal-in-prose/violation-in-action count (0/144 vs 32/288).** Every violation is attributable to the attack, and 32 cases where a text scorer would say "refused" while the tool fired is a concrete, quotable argument for scoring logs.
- **The indirect-channel caveat stated in the abstract.** 15/36 under the provenance clause when the same claim arrives via a poisoned lookup is the paper's own bound on its own mitigation, placed in the abstract rather than the last paragraph. That is rare and reviewers notice. Do not let a co-author talk it out of the abstract.

## Figures

Keep for the 4-page paper:
- **Fig 2 (a, b, c).** Replaces Table 2 and the prose numbers in "It is the clause, not the length" and "Which reasoning step fails". One half-column figure carrying three results with Wilson bars. Best figure in the set. Split panel (a) bars by model or add a per-model annotation (Reason 2).
- **Fig 3 (channel).** Replaces the numbers in Limitations. It is the honesty figure and it should sit next to the recommendations, not in Limitations. Reconcile n = 36 with the regular paper's n = 24 before placing.
- **Fig 1 (threat model), only if Section 1 is cut.** It does more for the advisor's "what problem is being solved" standard than any paragraph in the draft. Fix "7 templates" (6 + control) and "5 phrasings" vs abstract "6".

Filler for the short paper:
- **Fig 4.** A slide, not a figure. Its content is Fig 2c plus the quoted clause. Quote the clause in the text instead. Its caption "models cannot check" is a mechanism claim the data do not test (no probe of whether the model believed the directive existed); the text's "they have no mechanism to check" is likewise speculation dressed as finding.
- **Fig 5.** Includes claude-sonnet-4-5 (0/36), which the short paper never mentions and whose Limitations say "no frontier-model claim". Placing it in the short paper creates a claim the text disowns. Also uses 720 denominators where the text uses 840. Good for the regular paper.
- **Fig 6.** n = 12 per bar, all three CIs overlap completely; it shows nothing beyond "about 40% with wide error". Regular paper appendix at most.

Overclaim check: Fig 2a's green "0/288" and Fig 4's "0/288 violations under attack" are fine because the bar is drawn with its CI. Fig 4's three green/red boxes imply a causal decomposition of "reasoning steps" that the design (six attack templates) does not license.

## Verdict

**Borderline, leaning accept for a workshop short paper. P(accept) = 0.55** as submitted; **0.75** if Reasons 1, 2, 4, 6, and 7 are fixed, which is one to two days of work and no new experiments. As a hostile reviewer I would score it 5/10 today: clean design, honest bound, but a missing defense sentence, a pooled headline that is one model, an unaware related-work section, and count mismatches between the figures and the text.

Most likely way I am wrong: workshop reviewers weigh the clean 0 vs 32% effect and the self-imposed indirect-channel bound heavily, ignore the iid issue and the missing AgentDojo/PAP citations, and accept with minor comments. Second most likely: the per-model split shows haiku's `exemption` cell is 8 to 10 of 144, which is a real if small effect in the same direction, and Reason 2 collapses into a presentation note.
