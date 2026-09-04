# Council review: Loki -> AgentWild short paper (post-addendum)

Reviewer stance: Berkeley RDI / prompt-injection benchmark lineage. Bias disclosed: I desk-reject "GRPO attacker, ASR up" papers weekly. Novelty must sit in the threat model and the evidence, not the trainer.

## Predicted score: 5/10 (range 4-6)

Borderline as written. Threat model interesting, RL not. With the matched-defense table plus a non-RL baseline: 6-7, plausible poster. Without: 4.

## One-sentence reject

"Knowledge corruption of retrieval-fed agents is established (PoisonedRAG, AgentPoison, CorruptRAG-AK, Poisoned Playbooks, illusioning attacks of Wu et al.), and the paper's addition is an RL attacker whose gain over hand-written fabricated authority is never measured."

## Does prior work already do exactly this? Partially, yes.

Your addendum is right and incomplete. Confident ids you still miss:
- **Wu et al. 2406.12814** (ICLR 2025, multimodal agents): names *illusioning* (agent believes false state, does user's task wrong) vs *goal misdirection* (hijack). Your Q1 distinction already has a name. Adopt or contrast it, or a reviewer from that lab will.
- **AdvWeb 2410.17401** (Bo Li lab): DPO-trained attacker producing injections that flip web-agent actions, e.g. wrong recipient, user task unchanged. Closest "learned attacker, wrong action" paper. Ignoring an organizer's closest paper is a self-inflicted wound.
- **Greshake 2302.12173**: indirect PI taxonomy already lists misinformation as a goal class.
- **Pan et al. 2305.13661**: LLM misinformation pollution of ODQA. Your HotpotQA env is a cousin.
- **RobustRAG 2405.15556**: the natural defense baseline.

Less confident, verify: BadRAG 2406.00083; DarkCite 2411.11407 (fake-authority citations for jailbreaks; undercuts your JailbreakBench template's novelty); MINJA 2503.03704.

Nobody I know of does: RL-learned *framing* + explicit detectability penalty against instruction-detectors + matched hijack-vs-fact comparison under one defense suite on AgentDojo. That triple is the paper.

## Q1, re-answered against the addendum

(a)+(b)+(c) is enough for 4 pages only if (b) is proven, not asserted. (a) alone is CorruptRAG-AK with a trainer; (c) alone is AgentPoison on a different benchmark; (d) is a table, not a contribution. Cut (d) from the pitch.

The sharper angle is the Verification-Boundary one, and it is what I would fund. Reframe the attacker as *learning to stay inside the unverifiable zone*: reward = attacker-goal success minus (instruction-detector flag) minus (fact-checker refutation given the agent's actual tool access). Then the headline is a mechanism, not an ASR: "ASR tracks the verification boundary; widening it (give the agent a lookup tool) kills the attack, instruction defenses do not." This positions against Poisoned Playbooks (they name the boundary, you weaponize it) and CorruptRAG-AK (they hand-write framing, you learn it and show which cues survive a refuter). That is a workshop talk. Measuring "which fabricated-authority features transfer" is a histogram, not a paper.

The one experiment: matched pairs on AgentDojo. Same task, same wrong final action (same IBAN), one hijack payload, one fabricated-fact payload. Same defense stack: PromptGuard-class classifier, CommandSans stripping, spotlighting/tool-filter, one IH-trained model, plus one fact-check/refute step. Report ASR-under-defense. Hijack collapses, fact holds, refuter kills fact: paper. Both hold: the Firewalls 2510.05244 critique eats you.

Mandatory control: non-RL fabricated-authority baseline (templates or one GPT-4o-mini prompt). If RL does not clearly beat it, drop RL from the title.

## Q2. Biggest 34h risk

Goodhart on the detectability term: the 1.5B policy learns bland text that fools the classifier and the LLM judge but changes no action. Second: AgentDojo plus judge-reward latency means 200 steps of noise. Mitigation: freeze a template attacker at hour 0, produce the matched-defense table with it, treat RL as an upgrade row.

## Q3. Cut one, add one

Cut: 4-target transfer table and interpretability histogram. Add: the non-RL baseline and the matched hijack-vs-fact defense table with a refuter column.

## Q4. Must-cite

Everything confident above, plus your addendum list, PISmith 2603.13026, AgentDojo, InjecAgent, WASP, Firewalls 2510.05244, your chosen CommandSans / IH paper. AgentPoison and AdvWeb in the first paragraph of related work.

## Q5. Short or regular

Short. One table of evidence, 34 hours. Transfer, if any, goes in the appendix.

## What moves me to 7

Matched-defense table with non-RL baseline, 30+ point ASR-under-defense gap between hijack and fact, refuter column showing the boundary mechanism, illusioning terminology acknowledged, one honest paragraph on why Firewalls does not already cover this.
