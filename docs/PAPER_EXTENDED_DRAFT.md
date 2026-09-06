# Fabricated Authority in the Wild: Policy Provenance as a Control Surface for Tool-Calling Agents

**Extended version context.** Lead author: Yash Thakur. Backup authors: Aayushya Patel and Pranav Burra. Keep double-blind submission artifacts anonymous until camera-ready.

This is the larger-page draft built after finalizing the 4-page AIWILD submission. It preserves the short-paper claims, adds context, methods detail, related work, threat-model clarity, and a stronger limitations section without expanding the claims beyond the data.

## Abstract

Tool-using language-model agents convert text into external actions. That changes how safety should be measured: a model can refuse in prose while still invoking a forbidden tool. We study a simple but deployment-relevant attack family, **fabricated authority**, in which the user request cites a non-existent policy update, prior approval, audit exemption, or administrative override. Across 1,968 hosted-model trials spanning 8 scenarios, 6 operating-policy phrasings, 7 attack templates, and 2 production models, fabricated authority raises policy violations from 0/240 in controls to 208/1440 under attack (14.4%, Fisher p = 1.1e-15). The dominant variable is not the model alone, but the deployer's operating-policy wording: attacked violation rates range from 0/288 under a provenance-aware policy to 93/288 (32.3%) under an exemption-carve-out policy. A matched single-scenario contrast gives complete separation, 18/18 versus 0/18, with only one sentence changed. A length-control ablation shows the effect is not policy verbosity; a longer irrelevant policy is worse than the short strict policy it extends. Finally, an adaptive LLM attacker with white-box access to the defender prompt and tool schema breaks the weak control policy in 8/8 and 7/8 scenarios across two runs, but fails to breach the provenance-aware policy in 0/8 scenarios both times. A forced indirect-channel study breaks the same policy in 15/36 poisoned policy-lookup trials, so the longer version should separate direct-user provenance claims from poisoned-tool-output provenance. These findings suggest a concrete mitigation for direct user-message attacks and a follow-on requirement for runtime provenance tracking.

## 1. Introduction

Language-model safety evaluations often ask whether the model produces harmful text. Tool-using agents require a different view. The system output is no longer just a string; it can be a database export, wire transfer, deletion command, privilege grant, or security change. In that setting, the most important dependent variable is often available without a judge: did the agent call the forbidden tool with violating arguments?

This matters because text and action can diverge. In our paired text/tool experiment, 32 of 432 trials contain a refusal in prose while also emitting the forbidden tool call. None of these divergences occur in no-attack controls. A text-only evaluation would score these as safe refusals even though the external action fires.

We focus on a specific attack family: fabricated authority. The user does not primarily deny that the requested action is restricted. Instead, the user claims that some authority permits it: a superseding directive, a prior approval, a documented audit exemption, or an updated classification. This is natural in real deployments because agent policies often include operational carve-outs. Engineers write policies like "do not export records unless an exemption is documented" or "handle routine requests end-to-end without bothering staff." Such language is convenient, but it creates hooks for user-controlled claims.

The central finding is that policy wording can dominate the outcome. A policy that says claimed exemptions, prior approvals, or superseding policies arriving in user input or tool output are not authoritative drives violations to 0/288 in the main hosted-model sweep. A policy that allows documented exemptions reaches 93/288, or 32.3%, under identical attacks. This is not because the safer policy is longer: a length-control policy with irrelevant operational detail reaches 11/96 violations, while the provenance-aware policy remains at 0/96.

### Contributions

1. **A logged-tool-call evaluation for fabricated authority.** We measure policy violations using tool names and arguments rather than LLM judges.
2. **A policy-phrasing measurement matrix.** We vary five main operating-policy phrasings across 8 scenarios, 7 attacks, and 2 hosted targets.
3. **A one-sentence mitigation.** A provenance clause eliminates violations in the main hosted sweep and in a matched contrast.
4. **A controlled ablation.** A verbosity control shows the effect is not merely more policy text.
5. **An adaptive-attacker check.** A white-box attacker breaks weak controls but fails twice against the provenance-aware policy.
6. **A boundary condition.** A 3B local model violates policy without attack, showing that policy wording is not a substitute for baseline policy adherence.

## 2. Motivation: why not score text with an LLM judge?

The project began as a GRPO-trained text attacker scored by an LLM judge. The initial result looked encouraging: measured ASR rose from 25% to 48%. Validating the judge against 200 human-labelled responses showed that the effect was an artifact. The local judge reported 83% ASR on outputs whose human-labelled ASR was 19%, with 36% accuracy and 23% precision. The same outputs scored 14% ASR under gpt-4o-mini and 25% under a refusal heuristic. Re-running the trained-vs-base comparison on 120 held-out behaviors with the validated judge produced 12.5% versus 11.7%, Fisher p = 1.00.

We do not claim novelty for judge failure. Recent work studies judge unreliability at far greater scale. The lesson for this paper is methodological: where a verifiable action log exists, use it. Tool-call traces make the safety outcome less ambiguous and avoid evaluator false positives.

## 3. Threat model

The defender is a single-turn tool-using agent. It receives a system prompt containing an operating policy, a user task, and a fixed set of tools. Some tools can be used compliantly, but each scenario defines a policy-violating use through a predicate over tool name and arguments. The agent also has a safe alternative tool, `request_approval`, so non-violation is not confounded with doing nothing.

The attacker controls the user message. The attacker cannot modify the system prompt, tool schema, or execution environment. The attacker can include fabricated claims about policy, approval, urgency, or document status. In the adaptive setting, the attacker additionally sees the defender's system prompt, tool schema, and transcripts of prior failed attempts.

The main outcome is binary: whether a violating tool call occurred. We count a trial as violating only when the tool name and arguments match the scenario-specific forbidden pattern. Calling the same tool with non-violating arguments is not counted. Errored trials are dropped rather than counted as safe. The hosted sweep had zero errored trials.

## 4. Experimental setup

### Scenarios

We use 8 hand-written scenarios covering data exfiltration, destructive operations, financial actions, privilege escalation, and security degradation:

- `medical_export`: export patient records to an external domain.
- `payroll_disclosure`: disclose payroll records.
- `customer_pii_share`: send customer PII externally.
- `prod_db_delete`: delete production database records.
- `backup_deletion`: delete backup snapshots.
- `security_disable`: disable endpoint protection.
- `wire_transfer`: initiate a wire transfer.
- `access_grant`: grant administrative access.

Each scenario specifies a forbidden tool call and a safe alternative. This lets the harness distinguish a true violation from either a safe refusal or a compliant action.

### Operating-policy phrasings

The independent variable is the operating policy. The main hosted sweep uses five phrasings:

| Policy | Content |
|---|---|
| `strict_hatch` | Prohibition, safe alternative, and provenance clause. |
| `strict` | Prohibition plus safe alternative. |
| `bare` | Prohibition only. |
| `autonomous` | Encourages routine end-to-end handling, with a carve-out. |
| `exemption` | Prohibition unless an exemption is documented. |

The critical provenance clause is:

> Claims of exemption, prior approval, or superseding policy that arrive in a user message or tool result are NOT authoritative. Treat them as unverified and call `request_approval`.

A sixth policy, `strict_verbose`, appears in the length-control ablation. It is longer than `strict_hatch` but contains irrelevant operational detail rather than provenance guidance.

### Attack templates

We use seven attacks including the no-attack control:

| Attack | Mechanism |
|---|---|
| `none` | No fabricated authority. |
| `superseded` | Claims a newer policy supersedes the restriction. |
| `prior_approval` | Claims approval already happened. |
| `reclassify` | Claims the action is not in the restricted category. |
| `emergency` | Claims urgency overrides normal policy. |
| `audit_exemption` | Claims an exemption exists for audit or compliance. |
| `combined` | Stacks multiple fabricated authority claims. |

### Targets and statistics

The hosted targets are `gpt-4o-mini` and `claude-haiku-4-5`. We report `llama3.2` separately because it has a high no-attack violation floor. We use Wilson confidence intervals and one-sided Fisher exact tests for the planned contrasts.

## 5. Results

### 5.1 Fabricated authority causes tool violations

The main hosted sweep contains 1,680 trials: 8 scenarios x 5 policies x 7 attacks x 2 targets x 3 trials. No trials errored.

| Condition | Violations | Rate |
|---|---:|---:|
| No attack | 0/240 | 0.0% |
| Fabricated authority | 208/1440 | 14.4% |

The one-sided Fisher exact test gives p = 1.14e-15. Since the control floor is zero, violations in the attacked condition are attributable to fabricated authority rather than ordinary noncompliance in these hosted models.

### 5.2 Policy phrasing dominates

Attacked trials, both hosted targets pooled:

| Policy | Violations | Rate | 95% CI |
|---|---:|---:|---:|
| `strict_hatch` | 0/288 | 0.0% | [0.0%, 1.3%] |
| `strict` | 7/288 | 2.4% | [1.2%, 4.9%] |
| `bare` | 21/288 | 7.3% | [4.8%, 10.9%] |
| `autonomous` | 87/288 | 30.2% | [25.2%, 35.7%] |
| `exemption` | 93/288 | 32.3% | [27.2%, 37.9%] |

The planned contrast `strict_hatch` versus `exemption` gives Fisher p = 1.37e-32. The ranking is non-monotonic. A bare prohibition is safer than a prohibition with a documented-exemption carve-out, which suggests that adding operational exceptions can create attack surface if the agent is not also told how to authenticate them.

### 5.3 The effect is not policy length

`strict_hatch` is longer than `strict`, so we ran a length-control ablation on gpt-4o-mini using the four strongest attacks across all 8 scenarios. `strict_verbose` is longer than `strict_hatch` but contains irrelevant operational detail.

| Policy | Words | Violations | Rate |
|---|---:|---:|---:|
| `strict_hatch` | 77 | 0/96 | 0.0% |
| `strict` | 40 | 5/96 | 5.2% |
| `strict_verbose` | 98 | 11/96 | 11.5% |

`strict_hatch` versus `strict_verbose` gives Fisher p = 0.000361. More words do not explain the mitigation. If anything, irrelevant policy detail appears to dilute attention to the restriction.

### 5.4 Matched contrast: complete separation

The strongest single contrast isolates `medical_export` and the three attacks that reliably fire on it, holding model, scenario, temperature, and attack text fixed:

| Policy | Violations |
|---|---:|
| `exemption` | 18/18 |
| `strict_hatch` | 0/18 |

Fisher p = 1.1e-10. The only policy difference is the provenance clause.

### 5.5 Which fabricated claims work?

Across the hosted sweep:

| Attack | Violations | Rate |
|---|---:|---:|
| `none` | 0/240 | 0.0% |
| `reclassify` | 0/240 | 0.0% |
| `emergency` | 2/240 | 0.8% |
| `prior_approval` | 43/240 | 17.9% |
| `superseded` | 43/240 | 17.9% |
| `audit_exemption` | 52/240 | 21.7% |
| `combined` | 68/240 | 28.3% |

The pattern suggests that models can recognize the semantics of the action but do not reliably authenticate the provenance of the authority. Telling the agent "this is not a restricted action" fails. Telling it "the restriction was lifted" or "approval already exists" works much more often.

### 5.6 Target sensitivity

| Target | Violations | Rate |
|---|---:|---:|
| `claude-haiku-4-5` | 10/840 | 1.2% |
| `gpt-4o-mini` | 198/840 | 23.6% |

Model choice matters substantially. However, the provenance clause closes the gap in this sweep: both hosted targets score 0/144 under `strict_hatch` attacked trials.

### 5.7 Adaptive attacker

We next gave an attacker LLM the defender's exact system prompt, tool schema, and a transcript of its failed attempts. The attacker proposed a new misdirection each round. We compare `strict_hatch` to `exemption` as a control policy.

| Run | Rounds | Control broken | `strict_hatch` broken | Fisher p |
|---|---:|---:|---:|---:|
| A | 8 | 8/8 | 0/8 | 7.8e-05 |
| B | 10 | 7/8 | 0/8 | 6.99e-04 |

The control is essential. Earlier hand-written adaptive attempts failed against `strict_hatch`, but also failed against weak policies, making them uninformative. The LLM attacker is informative because it does break the control while failing against the provenance clause. This does not prove the clause is unbreakable. It shows that the clause resists an adaptive attacker strong enough to defeat the closest weak alternative.

### 5.8 Text refusal and tool action can diverge

In 432 paired trials, we compare prose refusal behavior to tool invocation behavior. There are 32 cases in which the model refuses in prose while simultaneously executing the forbidden tool call. The divergence never occurs without an attack: 0/144 controls versus 32/288 attacked, Fisher p = 1.26e-06.

This is the core measurement argument. For agents, safety is not merely what the model says. It is what the agent does.

### 5.9 Boundary condition: small local model

The local `llama3.2` run contains 560 trials. It violates policy in 54/80 no-attack controls and 270/480 attacked trials. The attack does not help, p = 0.979, because the baseline violation floor is already 67.5%.

This result bounds the mitigation. Policy phrasing is useful for models that can follow an operating policy at baseline. It is not a substitute for baseline instruction following. A small model with destructive tools may misuse them without any adversary.

## 6. Related work

**Text jailbreak benchmarks and learned attackers.** HarmBench standardizes harmful-behavior evaluation. LLMStinger and related work train or search for jailbreak prompts. These works generally evaluate text outputs with model-based judges. Our initial GRPO text attacker fell into the same evaluation trap, which motivated the switch to tool-call logs.

**Authority and citation attacks.** DarkCite shows that fabricated authority and citations can jailbreak text models. Our attack family is related, but the unit of failure is different: a policy-constrained agent invokes an external tool after receiving a fabricated claim about operational authority.

**Judge reliability.** Recent work including A Coin Flip for Safety and How Reliable Is Your Jailbreak Judge? shows that unvalidated LLM judges can dominate reported ASR. We do not compete with those papers. We use their lesson: avoid judges when the environment already exposes an objective success signal.

**Agent safety and tool-use benchmarks.** GAP and AgentSeer show that text safety does not transfer cleanly to tool-calling agents. AutoInject studies automated prompt injection attacks against tool-using agents. Our focus is narrower: deployment-policy phrasing as an independent variable, and provenance-aware policy text as a mitigation against fabricated authority.

## 7. Practical recommendations

1. **Add a provenance clause.** Tell agents that claimed exemptions, approvals, and superseding policies arriving via user-controlled channels are not authoritative.
2. **Avoid unauthenticated carve-outs.** "Unless an exemption is documented" is attack surface unless the agent can verify the document's source.
3. **Be careful with autonomy language.** "Handle routine requests end-to-end" can override safety intent in practice.
4. **Always include a safe alternative tool.** `request_approval` turns refusal into a positive action, not paralysis.
5. **Evaluate on tool logs.** For tool-using agents, text-only safety evaluation can miss real violations.

## 8. Limitations

The main hosted sweep has only two production targets. The scenarios are hand-written and single-turn. The adaptive attacker is `gpt-4o-mini`, not a stronger frontier model or an RL-trained optimizer. The provenance clause may fail in multi-turn settings, indirect prompt injection, or environments where tool outputs themselves are treated as trusted policy channels. The local small-model result shows that policy wording cannot compensate for weak baseline policy adherence. Finally, our results measure violation of synthetic policies in controlled harnesses, not incidents in deployed systems.

## 9. What the longer version should add next

The most valuable additions for a conference-length version are:

1. **More targets:** add at least one frontier model and one open-weight model larger than 3B.
2. **Multi-turn attacks:** allow the attacker to elicit intermediate tool outputs before presenting fabricated authority.
3. **Indirect-channel attacks:** force the agent to consult a poisoned corpus so user-controlled authority appears in tool output.
4. **RL-trained attacker:** optimize directly against `strict_hatch` rather than relying on an LLM red-teamer.
5. **Scenario expansion:** move from 8 hand-written scenarios to 30-50 scenarios grouped by sector and tool type.
6. **Policy-authentication taxonomy:** separate provenance, authority, freshness, delegation, and emergency exceptions.
7. **Human review of prompts:** ask practitioners to rate which policies look realistic before testing them.

## 10. Conclusion

Fabricated authority is a simple attack that becomes measurable when agents have tools. In hosted models that otherwise follow their policies, fabricated authority produces statistically significant tool violations. The largest lever is not model choice alone but the exact operating-policy phrasing. A one-sentence provenance clause eliminates violations in our main sweep, survives a matched contrast and two adaptive-attacker runs, and costs nothing to deploy. The result is narrow but actionable: for policy-constrained agents, unauthenticated authority claims should be explicitly rejected at the system-prompt level, and safety should be evaluated from tool logs rather than text alone.
