# Editor review of abstract v3

Scope: structure, register, economy. No ML judgement offered or implied.

## STRUCTURAL MAP

v3 has 14 sentences, 321 words. Function of each:

| # | Words | Sentence (opening) | Function | Verdict |
|---|---|---|---|---|
| 1 | 35 | "An AI assistant is given more and more tools..." | context | Keep the idea, cut the sentence. Two clauses do two jobs (tools exist; violations are actions). |
| 2 | 11 | "The one who installs one writes its regulations..." | context | Duplicates #1 (still setting scene). Fold into #1 as "deployer-written operating policy". |
| 3 | 22 | "We're going to take a look at one easy way..." | gap / what we did | Mixed function. Announces the study before defining the attack. |
| 4 | 12 | "An audit exemption was granted..." (quoted example) | illustration | No function an abstract needs. Belongs in the introduction. |
| 5 | 11 | "The directive is made up, but the assistant cannot confirm it." | definition | Duplicates #3 and #6. |
| 6 | 8 | "It's fake authority that we call fabricated authority." | definition | Duplicates #5. Circular ("fake authority ... fabricated authority"). |
| 7 | 29 | "For gpt-4o-mini and claude-haiku-4-5 we tried 1,680 times..." | method (design) | Keep. |
| 8 | 24 | "For each trial we decided whether the forbidden tool was actually called..." | method (scoring) | Keep. |
| 9 | 12 | "The rules determine if the attack is successful or not, we find." | result (headline) | Function is fine, placement is fine, phrasing is loose. Merge into #10-11 as the opening clause of the results block. |
| 10 | 20 | "With no fake claim, all the assistants played the game..." | result (control) | Keep the number, cut the metaphor. |
| 11 | 39 | "Under a policy with an exception..." | result (main contrast) | Core result. Over 35 words. Split: carve-out result, then the one-sentence fix. |
| 12 | 30 | "That sentence held when attacked by an attacker model..." | result (adaptive) | Keep, but no numbers given. 8/8 vs 0/8 is missing. |
| 13 | 33 | "It's not a 100% defense: in 15 of the 36 tests..." | limit | Keep the number. "100%" is invented, not in HARD FACTS. |
| 14 | 35 | "The recommendation is open to use: ..." | implication | Keep the list. "open to use" has no meaning. |

Summary of function counts: context 2 (one too many), gap/definition 4 (three too many), method 2 (right), results 4 (right, but #9 is empty of numbers and #12 has no numbers), limit 1 (right), implication 1 (right).

Six sentences (#1 to #6, 99 words, 31% of the abstract) precede the first fact about the study. The calibration set reaches the method by sentence 2 or 3 in 7 of 8 usable abstracts (LinuxArena, VE, CFD, WARD, GAP, AgentSeer, AutoInject). OS-Sentinel takes 4. None takes 6.

Missing from v3 relative to the brief: model names appear but per-model results do not; adaptive attacker has no numbers; the content of the one sentence is only paraphrased ("permissions claimed by the user do not count"), which understates what it says (it also covers tool results and directs the model to request_approval).

### Sentence-length comparison

| Text | Sentences | Words | Mean | SD | Min | Max |
|---|---|---|---|---|---|---|
| v3 | 14 | 321 | 22.9 | 10.3 | 8 | 39 |
| LinuxArena | 6 | 173 | 28.8 | 8.3 | 16 | 39 |
| Visual Exclusivity | 9 | 174 | 19.3 | 5.4 | 7 | 25 |
| OS-Sentinel | 8 | 167 | 20.9 | 8.1 | 8 | 35 |
| CFD | 8 | 195 | 24.4 | 16.2 | 10 | 65 |
| WARD | 6 | 201 | 33.5 | 9.1 | 22 | 46 |
| Mind the GAP (text vs tool) | 10 | 244 | 24.4 | 8.3 | 13 | 38 |
| AgentSeer | 9 | 215 | 23.9 | 16.0 | 10 | 64 |
| AutoInject | 9 | 201 | 22.3 | 3.6 | 16 | 28 |

(The DMOG abstract is excluded; it is a theory paper pasted twice and is not from this venue's register.)

v3's mean length and variance sit inside the calibration range. The problem is not rhythm. It is sentence count (14 versus 6 to 10) and total length (321 versus 167 to 244). The calibration median is about 198 words. v3 is 60% over. The v1 draft (205 words, 10 sentences) is on target for length and count.

## REGISTER BREAKS

Contractions (7): "it's" (x2, sentence 1), "We're" (3), "doesn't" (3), "It's" (6), "It's" (13). None appear in the calibration set.

Colloquial or conversational phrasing:
- "more and more tools" (1). Calibration equivalent: "increasingly".
- "etc." (1). Never used in the calibration set.
- "The one who installs one" (2). Awkward; "deployer" is the term used by CFD and GAP.
- "We're going to take a look at" (3). Announces rather than states.
- "one easy way" (3). "cheap" or "low-cost" is the register the venue uses.
- "It's fake authority that we call fabricated authority" (6). Defines a term with its synonym.
- "we tried 1,680 times" (7). "tried" reads as trial-and-error, not as a controlled design.
- "we decided whether" (8). Implies human judgement; the method is a log check.
- "if the answer sounded like a refusal" (8). Fine idea, chatty phrasing.
- "The rules determine ... we find" (9). Trailing "we find" is spoken, not written.
- "played the game by the rules and never broke any of them" (10). Metaphor plus redundancy (playing by the rules = not breaking them).
- "they break it" (11). The subject "they" is the assistants, but the plural drifts from the singular subject of the sentence.
- "(a second language model playing the user)" (12). Parenthetical gloss belongs in the body.
- "who was able to read the rules and rewrite its claim eight times over" (12). "who" for a model, "eight times over" is idiom.
- "It's not a 100% defense" (13). "100%" is not in HARD FACTS and reads as marketing.
- "taken from a document ... not typed by the individual" (13). "the individual" is a register jump upward, mismatched with the conversational surroundings.
- "The recommendation is open to use" (14). Meaning unclear.
- "tell them that a claimed permission is not real" (14). "them" = assistants; "not real" is loose for "not authoritative".

Quoted example sentence (4): a quoted fabricated directive is vivid but no calibration abstract quotes an attack string. Keep it for the introduction.

## UNANCHORED NUMBERS

For each number, what the reader would need to know and whether v3 supplies it.

| Number | Where | Denominator known to reader? |
|---|---|---|
| 1,680 | s7 | Yes, but the factorisation given (8 x 5 x 7 x 3 = 840) does not reach 1,680. The "x 2 models" is implied only by naming the models earlier. State it. |
| 8 tasks, 5 wordings, 6 fake-claim wordings, three repeats | s7 | Yes. |
| 0/240 | s10 | No. Reader cannot derive 240 from anything stated (it is 8 tasks x 5 policies x 2 models x 3 repeats for the no-claim arm). Acceptable in an abstract if the numerator is zero and the reader accepts "of the no-claim trials", but say "no-claim trials". |
| 93/288 (32.3%) | s11 | No. 288 is never explained (8 x 6 x 2 x 3 = 288 attacked trials per policy). Say "trials under this policy" or similar. The percentage is redundant with the fraction; calibration abstracts give one or the other. |
| 0/288 | s11 | Same as above; parallel with 93/288 rescues it. |
| "eight times over" | s12 | Ambiguous: eight rounds, eight tasks, or eight attempts per task? HARD FACTS: 8 rounds x 8 tasks. The result (8/8 vs 0/8) is absent entirely. |
| 15 of the 36 | s13 | Partially. "tests" is undefined; the reader does not know these are strict_hatch trials on one model in the indirect channel. Say "trials" and name the channel. |
| 100% | s13 | Not a fact. Remove. |
| 12.3(b) | s4 | Decorative. Remove with s4. |

Absent but required by the brief: 8/8 vs 0/8 adaptive; the model names attached to results; the tool-call log scoring stated as a method fact rather than a contrast with LLM judging.

## CANDIDATE ABSTRACT

Structure: context 1, gap 1, method 2, results 4, limit 1, implication 1. Ten sentences. Longest sentence 30 words. No contractions. Every number verbatim from HARD FACTS.

Tool-using assistants act under deployer-written operating policies, and a violation is an executed tool call, not a sentence of text. One cheap attack is fabricated authority: the user asserts an approval or exemption that does not exist and cannot be verified. We test it on gpt-4o-mini and claude-haiku-4-5 in 1,680 trials over 8 tasks, 5 policy wordings, 6 fabricated-claim wordings plus a no-claim control, and 3 repeats. Each trial is scored from the tool-call log by whether the forbidden tool was called with violating arguments; no LLM judge is used. Without a fabricated claim there are no violations (0/240). With one, policy wording decides the outcome: a policy with the carve-out "unless an exemption is documented" is violated in 93/288 trials. Adding one sentence, that claimed exemptions or approvals arriving in a user message or tool result are not authoritative, are unverified, and require a request_approval call, reduces this to 0/288. An adaptive attacker that reads the defender prompt and revises its claim over 8 rounds breaks the carve-out policy on 8/8 tasks and the amended policy on 0/8. The mitigation is channel-specific: with the fabricated permission planted in a policy-lookup tool result, the amended policy still fails in 15/36 trials. We recommend adding the sentence, avoiding exemption carve-outs, offering a safe alternative action, and scoring tool calls rather than refusal text, treating tool output as a separate problem.

Notes for the authors (not part of the abstract):
- Per-model split (198/720 vs 10/720) is omitted for length. It is the strongest candidate to add if the council wants 20 more words; it would go after the 0/288 sentence.
- The length control (11/96 vs 0/96) is omitted; "one sentence" carries the claim, and the body should prove it.
- "1,680 trials ... 3 repeats" leaves "x 2 models" implicit; the two model names sit in the same clause, so the factorisation is recoverable without adding "two models".
- The 15/36 sentence does not name gpt-4o-mini as the only model in that study. Add "on gpt-4o-mini" (3 words) if the council prefers precision over economy.

## WORD COUNT

Candidate: 229 words, 10 sentences, mean 22.9 words, SD 5.5, min 9, max 30. Sits between GAP (244) and AgentSeer (215) in the calibration set; variance matches AutoInject and VE, the two tightest abstracts.

Sentence lengths in order: 20, 21, 26, 23, 9, 22, 30, 28, 22, 28.

v3 for comparison: 321 words, 14 sentences, max 39.
