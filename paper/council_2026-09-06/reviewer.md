# Reviewer report: abstract only (AIWILD calibration)

Calibration set stats (excluding the duplicated "Mind the Gap" DMOG entry, which is off-topic and appears to be a paste error): 167, 173, 174, 195, 201, 201, 215, 244 words. Median 198. Every abstract opens with the threat or gap, names the artifact or finding in one sentence, and puts 2 to 5 numbers in plain "X% / X of Y" form. All use "we". None use contractions, "etc.", or future tense.

## SCORES

| Criterion | v3 (321 w) | v1 (205 w) |
|---|---|---|
| (a) First sentence states a problem a reviewer cares about | 3 | 7 |
| (b) Contribution stated in one sentence | 3 | 8 |
| (c) Key numbers present and legible | 5 | 6 |
| (d) Register (calibration set vs blog) | 2 | 8 |
| (e) Length relative to calibration set | 3 | 9 |
| **Mean** | **3.2** | **7.6** |

Notes.

v3 (a): the first sentence contains "etc.", two contractions, and a slogan ("it's not a sentence being written, it's something that is being done") in place of a named problem. A reviewer skimming 30 abstracts does not learn what is attacked or why until sentence three.
v3 (b): the contribution is spread over sentences 3 to 6 and introduced with "We're going to take a look at". No single sentence a reviewer could copy into a summary.
v3 (c): 1,680, 0/240, 93/288 (32.3%), 0/288, 15/36 are present. Missing: adaptive attacker 8/8 vs 0/8, per-model split, length control. The numbers that are present sit inside 40-plus-word sentences, so they do not scan.
v3 (d): "played the game by the rules", "It's not a 100% defense", "The recommendation is open to use", "We're going to take a look". Reads as a translated blog post. The one sentence that would land ("one added sentence takes violations from 93/288 to 0/288") is never written as a single sentence.
v3 (e): 321 words is 60% over the calibration median and longer than the longest on-topic calibration abstract (244).

v1 (a): "Tool-using language-model agents can refuse in text while still taking an unsafe action" is a strong opener but it is the GAP paper's headline, not ours. The paper is about fabricated authority; the text/action gap is a secondary finding (32/432). Slightly mis-aimed.
v1 (b): "We study fabricated authority: ..." is exactly right.
v1 (c): numbers are legible but overloaded (two p-values, two adaptive-attacker runs, 1,968 trials which now contradicts the 1,680 hard fact). Stale numbers cost points.
v1 (d): matches the set. Minor: "$p = 1.1\times10^{-15}$" in an abstract is unusual for this workshop; none of the calibration abstracts carry p-values.
v1 (e): 205 words, right at the median.

Verdict on the 20-second test: v1 I keep reading. v3 I stop at "etc.".

## WORST SENTENCES (v3)

1. "An AI assistant is given more and more tools: export a file, delete a database, etc., and when a rule is not observed, it's not a sentence being written, it's something that is being done."
   "etc." and two contractions in the opening sentence; "when a rule is not observed" is passive and vague; the second half is an aphorism, not a claim. The threat (users faking permission to trigger irreversible tool calls) is absent.

2. "The one who installs one writes its regulations, its operating policy."
   Two unresolved "one"s; "regulations" is the wrong word (the paper's term is operating policy); the apposition reads like a translation. This sentence exists only to introduce a term and does it badly.

3. "We're going to take a look at one easy way to break those rules: the user claims a permission that doesn't exist."
   Future tense and two contractions; "take a look" and "easy way" are conversational and undersell the attack. Calibration abstracts say "We study X: ...".

4. "It's fake authority that we call fabricated authority."
   Circular definition. Defines the term with its own synonym and adds no content (who makes the claim, what it asserts, why it cannot be verified). v1's definition sentence is strictly better.

5. "The rules determine if the attack is successful or not, we find."
   The main finding, delivered with a trailing "we find", no number, and "the rules" instead of "policy wording". This should be the most quotable sentence in the abstract and it is the least.

Honourable mentions: "all the assistants played the game by the rules and never broke any of them (0/240)" (idiom, "assistants" plural conflicts with two named models); "That sentence held when attacked by an attacker model (a second language model playing the user) who was able to read the rules and rewrite its claim eight times over" (no 8/8 vs 0/8 figure, "who" for a model, parenthetical explains what "attacker model" already says); "The recommendation is open to use" (no meaning).

## CANDIDATE ABSTRACT

Tool-using language-model agents act under a deployer-written operating policy, and a policy violation is an executed action, not a sentence. We study fabricated authority: a user claim that a forbidden action is permitted by an approval, exemption, or superseding policy that does not exist. We run 1,680 trials on gpt-4o-mini and claude-haiku-4-5, crossing 8 tasks, 5 operating-policy wordings, 6 fabricated-claim wordings, and a no-claim control, scoring each trial from the tool-call log by whether the forbidden tool was called with violating arguments, not by an LLM judge. Without a fabricated claim, no trial violates (0/240). With one, policy wording decides the outcome: a policy permitting the action "unless an exemption is documented" is violated in 93/288 trials; the same policy plus one sentence declaring that exemptions, approvals, or superseding policies arriving in a user message or tool result are not authoritative and must be treated as unverified is violated in 0/288. A length control rules out verbosity as the cause. An adaptive attacker that reads the policy and revises its claim over 8 rounds breaks the exemption policy on 8/8 tasks and the hardened policy on 0/8. The defense is channel-specific: when the fabricated permission arrives via a policy-lookup tool result, the hardened policy fails in 15/36 trials. We recommend adding the sentence, never writing exemption carve-outs, always providing a safe alternative action, and scoring tool calls rather than text.

## WORD COUNT

Candidate abstract: 230 words (target 170-230).

Numbers used, each traced to HARD FACTS: 1,680; gpt-4o-mini; claude-haiku-4-5; 8 tasks; 5 operating-policy wordings; 6 fabricated-claim wordings; 1 no-claim control; 0/240; 93/288; 0/288; 8 rounds; 8/8; 0/8; 15/36. Nothing added. Omitted deliberately for length: 32.3%, per-model split (198/720 vs 10/720), length-control counts (11/96 vs 0/96), judge-disagreement range, text/action mismatch (32/432), matched contrast (18/18 vs 0/18), CI bound. If one more number is wanted, the matched contrast 18/18 vs 0/18 is the most legible addition (about 12 words).
