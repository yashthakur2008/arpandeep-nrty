# Seat: science editor

Standard applied: the advisor's. Can each sentence be understood using only what came before it, and does the argument arrive in the order a reader needs (problem, why it matters, why it is hard, what was done, what was found, what it means)?

Legend: [G] = given earlier in the abstract, [D] = defined in this sentence, [N] = never defined anywhere in the abstract.

## Dependency audit: short-paper abstract

1. "Tool-using language-model agents can refuse in text while still taking an unsafe action."
   - tool-using language-model agent [N] (field-standard, but the reader has not been told an agent "takes actions" by calling tools; the contrast text/action is the whole paper and is asserted, not set up)
   - refuse in text [N]
   - unsafe action [N] (unsafe according to whom? the operating policy has not appeared)
2. "We study fabricated authority: user-controlled claims that a forbidden action is allowed by a non-existent approval, exemption, or superseding policy."
   - fabricated authority [D]
   - forbidden action [N] (forbidden by what? the policy is introduced in sentence 3 as a count)
   - user-controlled [N]
   - superseding policy [N]
   - approval / exemption [N] (approval by whom, exemption from what)
3. "Across 1,968 hosted-model trials with 8 scenarios, 6 operating-policy phrasings, 7 attack templates, and 2 production models, fabricated authority raises logged tool-call violations from 0/240 in controls to 208/1440 under attack (14.4%, p = 1.1e-15)."
   - hosted-model [N]
   - scenario [N]
   - operating policy [N] (this is the independent variable of the paper and it is introduced as a count)
   - attack template [N]
   - production model [N]
   - logged tool-call violation [N] (violation of what: the policy, which has not been defined as a thing the agent is given)
   - controls [N]
   - 1,968 vs 240 + 1,440 = 1,680 [N] (the 288 leftover trials are never accounted for; Fig 1 explains it, the text never does)
   - fabricated authority [G]
4. "The largest lever is the deployer's policy wording."
   - deployer [N]
   - policy wording [G, weakly: "operating-policy phrasings" was a count in sentence 3]
5. "A provenance-aware policy that states user-supplied exemptions are not authoritative has 0/288 direct user-message violations, while a documented-exemption carve-out has 93/288 (32.3%, p = 1.4e-32); a matched contrast gives complete separation, 0/18 vs 18/18."
   - provenance-aware policy [D, partially: what it states is given, "provenance" itself is not]
   - provenance [N]
   - direct user-message [N] (implies an indirect channel that does not appear until sentence 8)
   - documented-exemption carve-out [N] (the reader must infer this is one of the 6 phrasings)
   - matched contrast [N]
   - complete separation [N]
   - 288 [N] (1440 / 5 policies, but the abstract said 6)
   - 18 [N]
6. "A length-control ablation shows this is not verbosity: a longer irrelevant policy is worse."
   - length-control ablation [N]
   - "this" [G]
   - verbosity [D by the second clause]
7. "An adaptive attacker with white-box access breaks weak controls in 8/8 and 7/8 scenarios across two runs, but breaches the provenance-aware policy in 0/8 scenarios both times."
   - adaptive attacker [N]
   - white-box access [N]
   - weak controls [N] (which of the 6 phrasings? "controls" already meant no-attack trials in sentence 3, so the word now means two things)
   - scenarios [G, as a count only]
   - runs [N]
   - provenance-aware policy [G]
8. "However, a forced indirect-channel study breaks the same policy in 15/36 poisoned policy-lookup trials, so the mitigation is channel-specific rather than universal."
   - forced indirect-channel study [N]
   - poisoned policy-lookup trial [N]
   - channel [N] (first appearance of the word as a concept)
   - the mitigation [G, by inference: the provenance-aware policy]
   - 36 [N]
9. "The result is a narrow, actionable finding: agent evaluations should score tool logs, and deployment prompts should explicitly reject unauthenticated authority claims while treating tool-output provenance as a separate runtime security problem."
   - tool logs [G, as "logged tool-call"]
   - deployment prompts [N] (a third name for the operating policy: "operating-policy phrasing", "policy wording", "deployment prompt")
   - unauthenticated authority claims [G, as fabricated authority]
   - tool-output provenance [N]
   - runtime security problem [N]

Totals: 9 sentences. Concepts relied on: 44. [G] 8, [D] 3, [N] 33. Sentence 3 alone carries 8 undefined concepts. The independent variable (the operating policy the agent is given) is never defined as a thing; it appears only as a count and then as a synonym chain (policy wording, deployment prompt, control).

## Dependency audit: regular-paper abstract

1. "Tool-using language-model agents can refuse in text while still taking an unsafe action."
   - identical to short S1: tool-using agent [N], refuse in text [N], unsafe action [N]
2. "We study fabricated authority: user-controlled claims that a forbidden action is allowed by a non-existent approval, exemption, or superseding policy."
   - fabricated authority [D]; forbidden action [N]; user-controlled [N]; superseding policy [N]; approval / exemption [N]
3. "Across 1,968 hosted-model direct-channel trials with 8 scenarios, 6 operating-policy phrasings, 7 attack templates, and 2 hosted models, fabricated authority raises logged tool-call violations from 0/240 in controls to 208/1440 under attack (14.4%, p = 1.1e-15)."
   - everything in short S3 [N] x 8, plus direct-channel [N] (worse than the short paper: "direct-channel" now arrives in sentence 3 with no indirect channel in sight until sentence 7)
   - "hosted" is used twice in one sentence to mean the same thing
4. "The dominant variable is operating-policy wording: a provenance-aware policy has 0/288 direct user-message violations, while a documented-exemption carve-out has 93/288 (32.3%)."
   - operating-policy wording [G, weakly]
   - provenance-aware policy [N] (the short paper at least said what it states; this version drops that clause, so "provenance-aware" is a bare label)
   - provenance [N]
   - direct user-message [N]
   - documented-exemption carve-out [N]
   - 288 [N]
5. "A matched contrast gives complete separation, 18/18 versus 0/18."
   - matched contrast [N]; complete separation [N]; 18 [N]; which arm is 18/18 [N] (the order is reversed relative to sentence 4, so a reader must guess which policy is which)
6. "A length-control ablation shows this is not verbosity, and two adaptive-attacker runs break weak controls while failing to breach the provenance-aware policy."
   - length-control ablation [N]; verbosity [N, and no longer explained by the second clause]; adaptive-attacker [N]; runs [N]; weak controls [N, same double meaning of "control"]; provenance-aware policy [G]
7. "We then scale a forced indirect-channel study to all 8 scenarios: when the same fabricated authority arrives through a required policy-lookup tool, clean lookups cause 0/48 violations but poisoned lookups cause 32/48, including 8/24 under the provenance-aware policy and 24/24 under the exemption policy."
   - forced indirect-channel study [N] ("scale" implies an earlier one the reader has not seen)
   - required policy-lookup tool [D, roughly]
   - clean / poisoned lookup [D by contrast, acceptable]
   - the exemption policy [N as a name; the reader met "documented-exemption carve-out" in sentence 4 and must map the two]
   - 48 / 24 [N]
   - fabricated authority [G]
8. "These findings suggest that agent evaluations should score tool logs, deployment prompts should reject unauthenticated authority claims, and production systems need runtime provenance controls for tool outputs."
   - tool logs [G]; deployment prompts [N, third synonym again]; unauthenticated authority claims [G]; runtime provenance controls [N]; tool outputs [G, via lookup tool]

Totals: 8 sentences. Concepts relied on: 43. [G] 8, [D] 4, [N] 31. Net effect versus the short abstract: one fewer sentence, same number of undefined terms, and two regressions (the provenance clause is no longer paraphrased; "direct-channel" is now in sentence 3).

## Order of ideas

Reader needs, in order: (1) agents now act by calling tools, so a wrong answer is a wrong action; (2) a user can claim a permission that does not exist and the agent has no way to check; (3) measuring this is hard because text judges are unreliable, so we score the tool log instead; (4) 1,968 trials varying the sentence the agent is given; (5) one sentence in that policy takes violations from a third to zero, but only when the fake claim comes from the user, not from a document; (6) write that sentence, score tool logs, and treat documents as a separate problem.

**Short paper**, order as it arrives: (3) judge failure and a GRPO attacker → related work → (4) setup in six lines → (5) results → (6) recommendations → limitations, with (1) and (2) never stated as prose anywhere; they exist only inside abstract sentence 1 and the parenthetical "(e.g. exporting patient records)". Single worst misordering: the paper opens with why a different, abandoned experiment failed, before the reader has been told what an agent, a policy, or a fabricated authority claim is. See the next-but-one section.

**Regular paper**, order as it arrives: Introduction does (1), (2), (5) in roughly the right order, which is the best-written page in either draft. Then: §2 repeats the judge story; §3 setup; §4 results 4.1 to 4.8; §5 "Scenario and policy design detail" (what the scenarios and the violation predicate are); §6 mechanism; §7 reproducibility file list; §8 ethics; §9 "Reviewer-facing narrative"; §10 operational implications; §11 "Visual summary" (two tables labelled Figure 1 and Figure 2); §12 related work; §13 recommendations (five sentences); §14 limitations; §15 "Design choices for the longer paper"; §16 ablation summary table; §17 "Regular-paper submission plan"; §18 conclusion. Single worst misordering: §5 (what the scenarios are and what counts as a violation) comes after §4 (results computed over those scenarios and that predicate). A reader reaches "exemption scores 18/18" without knowing what medical_export is or what predicate fired. Separately, §9, §15 and §17 are notes from the authors to themselves ("The longer version should...", "submission plan") and are not paper content in any order; §7, §11 and §16 restate results already given. Related work at §12, after the conclusions have effectively been drawn, is the second-worst.

## Sentences doing two jobs

Short abstract:
- S5: "A provenance-aware policy that states user-supplied exemptions are not authoritative has 0/288 ... while a documented-exemption carve-out has 93/288 ...; a matched contrast gives complete separation, 0/18 vs 18/18." Reports the sweep result and a second, differently designed experiment in one sentence.
- S8: "However, a forced indirect-channel study breaks the same policy in 15/36 poisoned policy-lookup trials, so the mitigation is channel-specific rather than universal." Introduces a new experiment and draws the paper's main caveat from it.
- S9: "The result is a narrow, actionable finding: agent evaluations should score tool logs, and deployment prompts should explicitly reject unauthenticated authority claims while treating tool-output provenance as a separate runtime security problem." Three recommendations in one sentence.

Short paper §1 (it has no introduction; §1 is the opening):
- "That figure is an artifact of an unvalidated judge, as we now show." Announces the verdict and promises the evidence.
- "No LLM judge appears anywhere in the agentic pipeline below. This separates our contribution from text-jailbreak work such as HarmBench, LLMStinger and DarkCite [1, 2, 3], and from judge-reliability work..." The second sentence states a method choice and does the related-work positioning off it.
- "Our focus is narrower and deployment-facing: which operating-policy phrasings make fabricated authority succeed or fail when the outcome is a verifiable tool call." Positions against prior work and states the research question.

Regular abstract:
- S4: "The dominant variable is operating-policy wording: a provenance-aware policy has 0/288 ... while a documented-exemption carve-out has 93/288 (32.3%)." States the headline claim and supplies its evidence.
- S6: "A length-control ablation shows this is not verbosity, and two adaptive-attacker runs break weak controls while failing to breach the provenance-aware policy." Two unrelated experiments joined by "and".
- S7: "We then scale a forced indirect-channel study to all 8 scenarios: when the same fabricated authority arrives through a required policy-lookup tool, clean lookups cause 0/48 violations but poisoned lookups cause 32/48, including 8/24 ... and 24/24 ..." Describes the method and reports four results.
- S8: "These findings suggest that agent evaluations should score tool logs, deployment prompts should reject unauthenticated authority claims, and production systems need runtime provenance controls for tool outputs." Three recommendations.

Regular introduction:
- "In that setting, the most important dependent variable is often available without a judge: did the agent call the forbidden tool with violating arguments?" Makes a claim about measurement and introduces the paper's outcome variable.
- "AIWILD explicitly solicits work on agent security, tool misuse, prompt injection, evaluation, and agent systems; this paper sits at that intersection because the failure is an external action, not merely an unsafe answer." Pitches the venue fit and restates the thesis. The venue pitch should not be in the paper at all.
- "The central finding is that policy wording can dominate the outcome. A policy that says claimed exemptions, prior approvals, or superseding policies arriving in user input or tool output are not authoritative drives violations to 0/288 in the main hosted-model sweep." The second sentence quotes the clause and reports the number.
- "Contributions. We contribute: (1) ... (7) ..." Seven contributions in one sentence, three of which (4, 5, 6) are checks on contribution 3 rather than contributions.

## Does the first section make sense as an opening?

No. Argument:

1. The reader has no problem yet. Page 1, line 1 of the short paper is "This work began as a GRPO-trained text attacker scored by an LLM judge." That sentence contains three undefined terms and describes an experiment the paper is not about. The title promised fabricated authority and policy provenance; neither word appears until the last paragraph of §1. This is exactly the advisor's complaint: "the problem being solved makes no sense" at the top.

2. The section answers a question nobody has asked. "Why we changed the outcome variable" presupposes the reader knows there was an outcome variable, that it was text judged by an LLM, and that there was a reason to want a different one. All three are things the reader learns from the section itself. A section whose title only makes sense after reading it is not an opening.

3. It spends 40% of page 1 (Table 1, kappa, precision, recall, 128 false positives, tag compliance 0% to 46%) on the reliability of a llama3.2 judge, and then says "we do not claim novelty for judge failure" (regular paper §2). If the finding is not novel, it does not get the opening.

4. It confuses the paper's motivation with the authors' biography. The honest content here is a single method justification: "we score the tool log, not the text, because LLM judges disagree with humans by up to 69 points on identical outputs (Table 1)." That is one sentence in Setup, with Table 1 in an appendix. The story of the GRPO attacker that learned tag formatting instead of attacking is a good anecdote for a talk and belongs in a footnote or the supplement.

The best case for keeping it: it is a memorable, honest negative result, it explains why this paper looks unlike other jailbreak papers, and reviewers at this venue care about judge validity. But every one of those is served by the sentence above plus the appendix table. The cost is that the advisor, or any reader, closes the PDF before reaching the actual experiment. The regular paper already shows the fix: its introduction (agents act, text and action diverge in 32/432 trials, users claim permissions that do not exist, one sentence fixes it) is the correct opening, and its §2 is the same judge story demoted to half a page. Demote it further.

## Vocabulary budget

The three terms each paper actually needs:

1. **tool call** (the agent acts by calling a named function with arguments; a violation is calling the forbidden one). Everything else in the paper rests on this being a checkable event.
2. **operating policy** (the instructions the deployer writes into the agent's system prompt). This is the independent variable and needs one stable name. Pick this one and delete "policy wording", "policy phrasing", "deployment prompt", "system prompt" as synonyms in the abstract.
3. **fabricated authority** (the paper's named attack). Already defined in sentence 2; keep the definition.

"Provenance" is the fourth candidate and does not make the budget. In the abstract it can be spelled out ("a sentence saying that permissions claimed by the user or found in a document do not count") and the word introduced in the body, where the clause is quoted.

Every other technical term now in either abstract, with a plain replacement:

| Term in abstract | Plain replacement |
|---|---|
| tool-using language-model agent | an AI assistant that can act, for example export a file or send money |
| refuse in text | say no |
| unsafe action | an action its rules forbid |
| user-controlled claims | claims typed by the user |
| superseding policy | a newer rule that overrides the old one |
| hosted-model / production models / hosted models | two commercial models (name them) |
| direct-channel trials | trials where the fake claim is in the user's message |
| scenarios | eight tasks (medical records, payroll, backups, wire transfers, ...) |
| operating-policy phrasings | six ways of wording the agent's rules |
| attack templates | seven wordings of the fake claim |
| logged tool-call violations | times the agent actually called the forbidden tool |
| controls | trials with no fake claim |
| deployer | whoever writes the agent's rules |
| provenance-aware policy | rules that add one sentence: permissions claimed by the user do not count |
| documented-exemption carve-out | rules that allow the action if an exemption is documented |
| direct user-message violations | violations when the claim came from the user |
| matched contrast | the same task and the same attacks, with only that one sentence changed |
| complete separation | every trial failed under one wording and none under the other |
| length-control ablation | adding the same number of unrelated words instead |
| verbosity | length |
| adaptive attacker with white-box access | an attacker model that could read the agent's rules and its own failed attempts, and rewrite the claim each round |
| weak controls | the rules without the sentence (do not reuse "controls") |
| runs | repeats |
| forced indirect-channel study | a second experiment where the fake claim is planted in a document the agent is required to read |
| poisoned policy-lookup trials | trials where that document was tampered with |
| clean lookups | untampered documents |
| exemption policy | (same object as "documented-exemption carve-out"; use one name) |
| channel-specific rather than universal | works for claims from the user, not for claims from documents |
| mitigation | the sentence |
| tool logs | what the agent actually did, not what it said |
| deployment prompts | the agent's rules (same object as operating policy) |
| unauthenticated authority claims | claimed permissions that cannot be checked |
| tool-output provenance | where a document the agent reads came from |
| runtime security problem / runtime provenance controls | something the surrounding system must check, not the prompt |
| p = 1.1e-15, p = 1.4e-32 | drop from abstract or keep one; the ratios already carry the point |

## Figure placement

Note on consistency before placement. Fig 1 says "5 phrasings" and "8 x 5 x 7 x 2 x 3 = 1,680 plus ablations = 1,968"; both abstracts say "6 operating-policy phrasings" and never reconcile 1,968 with 1,680. Fig 1 is right and the abstracts are wrong; fix the text. Fig 3 and Fig 6 show the indirect study at n = 36 per policy (the short paper's 15/36), while the regular paper reports a different run at n = 24 per policy (8/24 vs 24/24, 96 trials). The regular paper cannot use Fig 3 or Fig 6 as drawn.

**Fig 1, threat model (agent gets policy, user message with fake directive, tools; outcome is the tool log).**
- Short paper: §2 Setup, as the only figure on page 1. Replaces the six-line prose setup and does the job §1 currently fails at: it shows the problem before any number. No table replaced.
- Regular paper: §3 Threat model. Replaces the first two paragraphs of §3 and makes Table 5 (scenario list) redundant with the eight scenarios in the green box.
- Caption: "The agent is given a rule, a request carrying a permission that does not exist, and tools that can break the rule. We score only whether it calls the forbidden tool."
- Keep. Fix "5 phrasings" to match the text, or fix the text.

**Fig 2, three-panel bar chart (a: policy wording, b: length control, c: what the claim asserts).**
- Short paper: §3 Results. Replaces Table 2 and the numbers in the "It is the clause, not the length" and "Which reasoning step fails" paragraphs. Those paragraphs shrink to one sentence each pointing at a panel.
- Regular paper: §4.2 to §4.3 and §6. Replaces Table 3, Table 4, the §11 "Figure 1" table, and the numbers in §6.
- Caption: "(a) One added sentence takes violations from a third to zero. (b) Adding unrelated words instead makes it worse, so it is the sentence, not the length. (c) Claims about who authorised the action succeed; claims about what the action is do not."
- Keep. For the short paper, (a) and (c) alone would fit if space is tight; (b) can be a sentence.

**Fig 3, direct vs indirect channel by policy.**
- Short paper: §5 Limitations, or better a last Results paragraph titled "Where the sentence stops working". Replaces the prose numbers in Limitations (0/72, 51/72, 15/36). No table replaced.
- Regular paper: §4.7. Replaces the §11 "Figure 2" table. Must be regenerated from the 96-trial run (8/24 vs 24/24 poisoned; clean 0/48 could be a third bar pair).
- Caption: "The added sentence stops fake permissions typed by the user but not fake permissions planted in a document the agent is required to read."
- Keep. This is the figure that stops the paper overclaiming.

**Fig 4, three reasoning steps with the clause quoted.**
- Short paper: cut. It repeats Fig 2(c) with the same three numbers, and a 4-page paper cannot carry two figures making one point. Its best line ("Does Directive 12.3(b) exist?") goes in the text.
- Regular paper: §6 "Why provenance is the control surface", where it replaces the whole first paragraph. If it is used, drop Fig 2(c) from the regular paper to avoid the duplicate. The "Not length: 98-word policy scored 11/96" side note duplicates Fig 2(b) and should be removed from the graphic.
- Caption: "Fake claims work only at the third step: the agent knows what the action is and whether it is urgent, but has no way to check whether the cited approval exists."

**Fig 5, per-model no-attack vs attack rates (llama3.2, gpt-4o-mini, claude-haiku, claude-sonnet).**
- Short paper: cut. The short paper never reports Sonnet, so the figure would introduce a result the text does not own; the two-model 20x gap is one sentence.
- Regular paper: merge §4.5, §4.6 and the llama3.2 half of §4.8 into one subsection "Which models this applies to" and place it there. Replaces the prose numbers in all three. Add a gpt-4.1-mini row (0/40 vs 68/240) so §4.6 is not the only model without a mark on the chart.
- Caption: "The attack only shows up in models that follow their rules to begin with: the small local model breaks them unprompted, and the largest model never breaks them at all."

**Fig 6, provenance clause under poisoned lookup, by claim type (n = 12 each).**
- Both papers: cut. Three bars at 4, 5 and 6 out of 12 with intervals from roughly 15% to 75% that all overlap; the figure shows no difference and says so. Its content is one sentence in the indirect-channel paragraph ("all three claim types get through, 4 to 6 times out of 12 each"). It also uses the n = 36 run that the regular paper has superseded.

## Score

Short paper: 5/10. The experiment and the finding are clear and narrow, but the abstract has 33 undefined dependencies in 9 sentences and the paper opens with the wrong experiment; a reader who does not already know the field will not reach §2.

Regular paper: 4/10. The introduction is the right opening and should be transplanted into the short paper, but the document around it is a working file: results before the definitions they depend on, three sections addressed to the authors rather than the reader, three restatements of the same results, related work after the conclusions, and figures that no longer match the reported numbers.
