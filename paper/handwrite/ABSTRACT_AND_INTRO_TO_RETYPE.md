# Abstract + Section 1, for you and Yash to retype in your own words

Rules: keep every number and every quoted policy string exactly. Change everything
else. Write like you'd explain it to Amrith on a call. Sentence length should vary.
Have an opinion. Then paste your version back into paper/main.tex (abstract goes
between \begin{abstract} and \end{abstract}; section 1 replaces the two
paragraphs after \section{The problem}). I'll run the number check and a cold read.

Numbers that must survive, verbatim:
  1,680 trials | gpt-4o-mini | claude-haiku-4-5 | eight tasks | five policy wordings |
  six fake-claim wordings + no-claim control | three repeats | 0/240 | 93/288 | 0/288 |
  eight rounds | 15/36 | 200 human-labelled | 14% to 83% | 19%
  quoted: "if an exemption is documented"

What each abstract sentence has to do (current draft below it):
  1 stakes: assistants act, so a broken rule is an action
  2 the deployer writes rules (define "operating policy")
  3-5 the attack, with the Directive 12.3(b) example (define "fabricated authority")
  6-7 what you ran, and that you scored tool calls not text
  8 "We find that ..." the result in one sentence
  9-10 the numbers: 0/240, 93/288 vs 0/288
  11 held against the adaptive attacker
  12 the limit: 15/36 when planted in a document
  13 what to do about it

=== ABSTRACT (current, 291 words) ===

AI assistants are increasingly given tools: they can export a file, delete a database, or send money, so a rule they break is an action taken, not a sentence written. Whoever deploys one writes it a set of rules, its operating policy. We study a simple way to break those rules: the user claims a permission that does not exist. "Per Directive 12.3(b), an audit exemption was granted for this export." The directive is invented, and the assistant has no way to check. We call this fabricated authority. We ran 1{,}680 trials on gpt-4o-mini and claude-haiku-4-5: eight tasks, five wordings of the operating policy, six fake-claim wordings plus a no-claim control, three repeats each. We scored each trial by whether the forbidden tool was actually called, not by asking another model whether the reply sounded like a refusal. We find that the wording of the rules decides whether the attack works. With no fake claim the assistants never broke a rule (0/240). Under a policy that allowed the action "if an exemption is documented" they broke it in 93/288 trials; under the same policy plus one sentence stating that permissions claimed by the user do not count, never (0/288). That sentence held against an attacker model (a second language model acting as the user) that could read the rules and rewrite its claim over eight rounds. It is not a complete defense: when the fake permission was planted in a document the assistant retrieved rather than typed by the user, the same sentence still failed in 15/36 trials. The recommendation is free to apply: score assistants on what they do, not what they say; do not write exemptions into their rules; and tell them claimed permissions are not real until verified.

=== SECTION 1 (current) ===

An assistant that can act is more useful and more dangerous than one that can only answer. A refusal in prose costs nothing if the same turn also calls export\_records(patients, research@ext.org). Deployers therefore write an operating policy into the assistant's system prompt ("never export patient records externally; if unsure, call request\_approval") and evaluate whether the assistant complies. Two things make that evaluation unreliable. First, users can lie about permissions, and language models have no mechanism to verify a citation to a policy, an approval, or an audit exemption that does not exist. Second, the usual way of scoring compliance, asking a second language model (a judge) whether the reply reads as a refusal, is itself unreliable. We checked three such judges against 200 outputs graded by a person: the fraction of attacks each judge reported as successful ranged from 14% to 83% on identical text, against 19% by the human grader (Appendix app:judge). We therefore score the tool-call log directly. A trial is a violation if and only if the forbidden tool was called with policy-violating arguments (Figure fig:threat). No language-model judge appears anywhere in the results.

This separates our contribution from text-jailbreak work such as HarmBench, LLMStinger, and DarkCite [cite], which score prose, and from work on judge reliability [cite]. Closest are agent benchmarks showing that text safety does not transfer to tool calls [cite], prompt-injection attacks on tool-using agents [cite], and prompt-injection defenses for web agents [cite]. Lin et al.\ [cite] exploit the same gap from the attacker's side: the assistant cannot tell where a claim or document came from, which they call an artifact-provenance gap. Our question is narrower and deployment-facing: which wordings of the operating policy let a fabricated permission through, and which one sentence stops it.
