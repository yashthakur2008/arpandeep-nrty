# Council: threat model critique (AI-control lens)

## 1. Is the distinction real?

Yes, but "belief poisoning" alone is not novel: PoisonedRAG, AgentPoison (Song, Li), CorruptRAG-AK, Poisoned Playbooks all do it. Cite all four early. The defensible claim is narrower: **the attack sits where two defense families both fail**.

- Hijack exploits the *control channel* (attacker text read as goals). Privilege separation (instruction hierarchy, CommandSans, spotlighting) fixes this if tool output is only data.
- Belief poisoning exploits the *evidence channel* (attacker text read as facts, which is what tool output is *for*). Goal never changes; a fact carries no privilege to strip. Failure is epistemic, not authorization.
- Poisoned Playbooks' **Verification Boundary** is the missing axis: poison succeeds iff the claim sits *outside* what the agent can refute with its tools/context. Prior work hand-writes claims; you make the attacker *learn* to stay outside the boundary.

So state the threat model as a tuple:
- **Attacker capability:** writes one tool result; no prompt access; no imperatives (stripper must return payload unchanged).
- **Trust assumption broken:** tool output is honest-but-possibly-irrelevant. Every hijack defense preserves this.
- **Success:** agent completes the *user's* task, reports success, final action equals attacker target.
- **Defender visibility:** transcript and tool outputs. No off-task action appears, so a Redwood-style trusted monitor scoring task deviation returns zero. That silent failure makes it a control problem.

Novelty sentence: "RL learns fabricated authority that is (i) instruction-free, so control-channel defenses pass it, and (ii) unverifiable, so evidence-channel defenses cannot refute it." Addendum (a)+(b)+(c) suffices for 4 pages only if (b) becomes **two** penalties: stripper flag and verifier refutation. CorruptRAG shows framing matters; you learn it under both penalties on action agents.

## 2. Which defenses catch it

| Defense | Mechanism | Hijack | Belief poison |
|---|---|---|---|
| Instruction stripping (CommandSans) | remove imperatives | kills | passes; none present |
| IH training (SecAlign, IH-Challenge) | deprivilege non-user text | kills | passes; fact needs no privilege |
| Spotlighting / delimiters | mark tool text as data | kills | passes; it *is* data |
| Injection classifiers (PromptGuard) | trained on command payloads | kills | mostly passes |
| Provenance / signing | reject unsigned sources | partial | partial; attacker writes to a trusted source |
| Fact-check vs user context / verifier | refute against evidence | weak | partial; catches contradictions (IBAN change), misses claims outside the Verification Boundary (fake regulation) |
| Task-deviation monitor (control) | flag off-task actions | kills | passes; action is on-task |

Each hijack-killing row passes poison for a *structural* reason, not a data gap.

## 3. Minimal proof experiment

One table, AgentDojo, three payload families:

- A: AgentDojo "important message" and PISmith-style RL hijack.
- B: Loki fabricated authority, instruction-free.
- B+: Loki with Verification-Boundary reward (a verifier with the user's context and tools must fail to refute).
- Defenses: none, stripping, IH target, PromptGuard, spotlighting, verifier.

Prediction: A collapses under 2-5. B flat under 2-5, drops under verifier. B+ flat under all six. That two-step separation is the paper. Add a hybrid (fact plus imperative) that strips to B and keeps B's ASR, and a no-injection baseline to rule out plain model error.

## 4. Metrics beyond ASR

- **Utility under attack:** user-task completion with poison present (stays high by design).
- **Silent-failure rate:** attacks succeeding with agent reporting success, no flag. Headline number.
- **Detection/refutation rate** per defense, plus **false-positive rate on benign tool outputs**.
- **Verifiability score:** fraction of learned claims a full-access verifier can refute; should fall over training for B+.
- **Attacker cost:** GRPO steps, params, transfer ASR.

## 5. What makes Bengio/Song/Bo Li reviewers care

- Structural taxonomy (control vs evidence channel, plus Verification Boundary) backed by the collapse-vs-flat table.
- Control framing: monitor-blind failure with on-task actions.
- Against AgentPoison: they backdoor memory with triggers; you need no trigger, no memory write, and evade defenses they never tested.
- One research-agent task where a poisoned search result flips a conclusion (Song's autonomous-research line).
- Defense probe with a security/utility curve.

Fail mode: payloads quietly containing imperatives, or no hijack baseline.
