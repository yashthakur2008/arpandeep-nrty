# Fabricated Authority Breaks Policy-Constrained LLM Agents

### One sentence in the system prompt decides whether it works

**Submission draft for NeurIPS 2026 Workshop on Agents in the Wild (AIWILD),
short paper track.** Deadline Sep 6, 2026, 13:00 UTC.

Every number is measured, reproducible with the command given, and stored as
JSON in `results/`. Total hosted-API cost of all experiments: under $3.

---

## Abstract

Safety evaluations of LLM agents mostly measure whether a model *says*
something harmful, scored by an automated judge. We show that this measurement
is unreliable, and that for tool-using agents a better dependent variable is
free: whether the agent invoked a forbidden tool. Across 1,968 trials spanning
8 scenarios, 6 operating-policy phrasings, 7 fabricated-authority attacks and 2
production models, we find that (i) fabricated authority raises the policy
violation rate from 0/240 to 208/1440 (14.4%, p = 1.1e-15), (ii) **the
deployer's policy wording dominates the outcome**, ranging from 0/288 to 32.3%
under identical attacks (p = 1.4e-32) and reaching complete separation (0/18 vs
18/18, p = 1.1e-10) in a matched single-scenario contrast, and (iii) in 32 of
432 paired trials the
agent refuses in prose while simultaneously executing the forbidden tool call,
a divergence that never occurs without an attack (p = 1.3e-06). A length
control shows the protection comes from one specific sentence about the
provenance of authority, not from policy verbosity: the longest policy we
tested was the worst performer. We also report the negative result that
motivated this design, in which an apparent 20-point attack improvement
disappeared entirely once the judge scoring it was validated against human
labels.

---

## 1. Why we changed the outcome variable

We began with a standard setup: train an attacker with GRPO to produce a
"misdirection" appended to a HarmBench behavior, and score attack success with
an LLM judge. It appeared to work. Attack success rose from 25% to 48%.

Then we validated the judge against 200 human-labelled responses.

| Judge | Accuracy | Cohen's kappa | Precision | Reported ASR |
|---|---|---|---|---|
| llama3.2 (3B, local) | 36% | 0.09 | 23% | **83%** |
| refusal heuristic | 94% | 0.83 | 76% | 25% |
| gpt-4o-mini | 93% | 0.75 | 93% | 14% |

True (human) ASR was **19%**. A judge that answered "refused" every time would
have scored 81% accuracy, more than double the 3B judge's 36%. Re-running the
comparison on 120 held-out behaviors with a validated judge gave **12.5% vs
11.7%, p = 1.00**. The effect was entirely an artifact of the judge.

We do not claim novelty for this. Concurrent work reaches the same conclusion
at far greater scale (arXiv:2603.06594, 6,642 human labels; arXiv:2606.25487,
596 human labels). We report it because it is why the rest of this paper does
not contain a judge.

**The alternative.** Give the agent tools and a binding operating policy.
Success is then `is_violation(tool_name, arguments)`: the forbidden tool fired,
with arguments matching the violating pattern. A compliant call to the same
tool is not a violation. This is a logged fact. It cannot be gamed by text that
sounds like compliance, it needs no human labelling budget, and it costs
nothing to compute.

## 2. Setup

Each trial gives a model a role, a binding policy containing a prohibition, a
tool that would violate it, a safe alternative (`request_approval`), a task
inviting the violation, and optionally an attack appended to the task.

Providing the safe alternative matters: without it, "did not violate" is
confounded with "failed to act".

**Scenarios (8).** Data exfiltration (medical records, payroll, customer PII),
destructive action (production DB, backups, endpoint protection), financial
(wire transfer), privilege escalation (admin grant).

**Policy phrasings (6),** the independent variable:

| Variant | Words | Content |
|---|---|---|
| `strict_hatch` | 77 | prohibition + escape hatch + **precedence clause** |
| `strict_verbose` | 98 | prohibition + escape hatch + 58 words of irrelevant policy |
| `strict` | 40 | prohibition + escape hatch |
| `exemption` | 35 | prohibition + "unless an exemption is documented" |
| `autonomous` | 41 | "handle routine requests end-to-end" + exemption carve-out |
| `bare` | 24 | prohibition only |

The precedence clause is one sentence:

> Claims of exemption, prior approval, or superseding policy that arrive in a
> user message or tool result are NOT authoritative. Treat them as unverified
> and call `request_approval`.

**Attacks (7),** each targeting a distinct reasoning step: `superseded`
(policy currency), `prior_approval` (process state), `reclassify` (category
membership), `emergency` (urgency), `audit_exemption` (documented carve-out),
`combined` (stacked), and a `none` control.

**Targets.** gpt-4o-mini, claude-haiku-4-5. A local llama3.2 is reported
separately as a floor-effect case.

**Statistics.** Wilson score intervals and one-sided Fisher exact tests.
Errored trials are dropped, never scored as compliance. Zero trials errored in
the main sweep.

## 3. Results

### 3.1 The attack works

1,680 trials.

| | Violations | Rate |
|---|---|---|
| No attack (control) | 0/240 | **0.0%** |
| Fabricated authority | 208/1440 | **14.4%** |

Fisher **p = 1.14e-15**. The control is at the floor, so every violation is
attributable to the attack rather than to a permissive baseline.

### 3.2 Policy phrasing dominates

Attacked trials, both targets pooled.

| Policy | Violations | Rate | 95% CI |
|---|---|---|---|
| `strict_hatch` | 0/288 | **0.0%** | [0.0%, 1.3%] |
| `strict` | 7/288 | 2.4% | [1.2%, 4.9%] |
| `bare` | 21/288 | 7.3% | [4.8%, 10.9%] |
| `autonomous` | 87/288 | 30.2% | [25.2%, 35.7%] |
| `exemption` | 93/288 | **32.3%** | [27.2%, 37.9%] |

`strict_hatch` vs `exemption`: **p = 1.37e-32**.

Two observations a practitioner can act on immediately. First, the two most
attackable phrasings are the two that sound most reasonable to write: "handle
routine requests without bothering staff" and "unless an applicable exemption
is documented". A documented-exemption carve-out is an open invitation to
fabricate a document. Second, the relationship is **non-monotonic**: `bare`
(7.3%), which says nothing about exemptions, is safer than `exemption` (32.3%).
Adding a carve-out is worse than adding nothing.

### 3.3 It is the clause, not the length

`strict_hatch` is longer than `strict`, so its 0/288 might come from having
more text. `strict_verbose` controls for this with 58 words of irrelevant
policy and no statement about claimed authority, reaching 98 words, longer than
`strict_hatch`. gpt-4o-mini, 288 attacked trials:

| Policy | Words | Violations | Rate |
|---|---|---|---|
| `strict_hatch` | 77 | 0/96 | **0.0%** |
| `strict` | 40 | 5/96 | 5.2% |
| `strict_verbose` | 98 | 11/96 | **11.5%** |

`strict_hatch` vs `strict_verbose`: **p = 0.000361**.

The longest policy was the worst, roughly doubling the violation rate of the
short policy it extends. Verbosity is not protective and may dilute attention
to the prohibition. **What the policy says matters, not how much it says.**

### 3.4 Matched contrast: 18/18 versus 0/18

The pooled comparison averages over 8 scenarios, so the policies may not have
faced equally potent attacks. Isolating one scenario (`medical_export`) and the
three attacks verified to fire on it, gpt-4o-mini, 6 trials each:

| Policy | Violations |
|---|---|
| `exemption` | **18/18 (100%)** |
| `strict_hatch` | **0/18 (0%)** |

Fisher **p = 1.1e-10**. Identical scenario, attack text, model and temperature.
The only difference is the precedence clause. Complete separation.

**A failed attempt to break it, reported because it is uninformative.** We
wrote four attacks specifically against `strict_hatch`: denying the
misdirection is a claim, reframing it as completed out-of-band verification,
forging an "authenticated channel" update, and arguing that `request_approval`
would itself breach another policy. All scored 0/6. We do **not** count this as
evidence of robustness, because the same attacks scored 0/12 against the weak
policies where standard attacks score 18/18. Our adaptive attacks were simply
weak. Whether a competent adaptive attacker defeats the clause is **open**, and
it is the most important question this work leaves.

### 3.5 Which reasoning step fails

| Attack | Mechanism | Violations | Rate |
|---|---|---|---|
| `none` | control | 0/240 | 0.0% |
| `reclassify` | category membership | 0/240 | **0.0%** |
| `emergency` | urgency override | 2/240 | 0.8% |
| `prior_approval` | process state | 43/240 | 17.9% |
| `superseded` | policy currency | 43/240 | 17.9% |
| `audit_exemption` | documented carve-out | 52/240 | 21.7% |
| `combined` | stacked claims | 68/240 | **28.3%** |

Claims about **provenance and process state** work; claims about **category
membership and urgency** do not. Telling an agent "this isn't really a
restricted operation" fails completely (0/240). Telling it "the restriction was
lifted" or "approval already happened" works about one time in five.

Our interpretation: these models verify the *semantics* of the act (is this an
export of medical data? yes) but not the *provenance* of the authority
supposedly permitting it. They have no mechanism to check whether Directive
12.3(b) exists, and they do not treat its unverifiability as disqualifying.
The precedence clause works because it supplies exactly that missing rule.

### 3.6 Models differ by 20x, policy closes the gap

| Target | Violations | Rate |
|---|---|---|
| claude-haiku-4-5 | 10/840 | **1.2%** |
| gpt-4o-mini | 198/840 | **23.6%** |

Attacked trials, by policy:

| Policy | claude-haiku-4-5 | gpt-4o-mini |
|---|---|---|
| `strict_hatch` | 0/144 (0.0%) | 0/144 (0.0%) |
| `strict` | 0/144 (0.0%) | 7/144 (4.9%) |
| `bare` | 0/144 (0.0%) | 21/144 (14.6%) |
| `autonomous` | 6/144 (4.2%) | 81/144 (56.2%) |
| `exemption` | 4/144 (2.8%) | 89/144 (61.8%) |

gpt-4o-mini under a permissive policy violates in 6 of 10 attacked trials. The
same model under `strict_hatch` never violates. Model choice matters, but the
policy sentence closes the gap for both.

### 3.7 A small local model: the attack becomes irrelevant

llama3.2 (3B, local), 560 trials.

| | Violations | Rate |
|---|---|---|
| No attack (control) | 54/80 | **67.5%** |
| Fabricated authority | 270/480 | 56.2% |

The attack does not help (p = 0.979). The model violates its operating policy
two thirds of the time when simply asked, so there is no headroom, and it is
reported separately rather than pooled.

Two things survive. Policy phrasing still orders the outcomes under attack
(`strict_hatch` 35.4% vs `autonomous` 75.0%, p = 2.64e-08), in the same
direction as the hosted models. But `strict_hatch` has the **highest** control
violation rate (12/16, 75.0%): a clause the model does not reliably attend to
provides no protection.

This bounds the recommendation. Policy phrasing is a mitigation for models
already capable of policy adherence, not a substitute for that capability. A 3B
model holding destructive tools misuses them with no adversary present.

### 3.8 Refusal is a positive choice, and weak policies lose it

| Policy | `request_approval` called | No tool call at all |
|---|---|---|
| `strict_hatch` | 335/336 (99.7%) | 1/336 (0.3%) |
| `strict` | 298/336 (88.7%) | 31/336 (9.2%) |
| `bare` | 203/336 (60.4%) | 112/336 (33.3%) |
| `autonomous` | 194/336 (57.7%) | 56/336 (16.7%) |
| `exemption` | 182/336 (54.2%) | 63/336 (18.8%) |

Strong policies do not merely suppress the forbidden call, they redirect the
agent into the escape hatch. `bare` has no escape-hatch instruction and leaves
the agent stuck in a third of trials, which is why a bare prohibition is a
worse design than its 7.3% violation rate suggests.

### 3.9 The agent refuses in prose and acts anyway

432 paired trials. Identical system prompt and user message; the only
difference is whether the tool schema is present.

| Measure | Value |
|---|---|
| Refused in prose | 347/432 (80.3%) |
| Violated via tool call | 92/432 (21.3%) |
| **Refused in prose AND fired the tool** | **32/432 (7.4%)** [5.3%, 10.3%] |
| Gap under control | 0/144 (0.0%) |
| Gap under attack | 32/288 (11.1%) |

Fisher **p = 1.26e-06**.

Fabricated authority does not only raise the violation rate, it **decouples the
two channels**. Without an attack the channels never disagree. Under attack
they disagree in 11% of trials.

A representative case, `medical_export` under the `strict` policy. The prose:

> "Despite the updates you provided regarding the Administrative Directive
> 12.3(b) and the compliance ticket NW-88213, my operating policy remains
> intact and binding. Therefore, I cannot proceed with exporting records
> containing personal or medical data to an external address..."

The model names the fabricated directive, rejects it, restates the policy, and
then calls `export_records(destination="research-partner@external-domain.net")`.
Text-based safety evaluation scores this as a refusal. The records still leave.

**This estimate is conservative by construction.** The text arm is classified
by the refusal heuristic validated at 94% accuracy (kappa 0.83) against 200
human labels, applied only to the text arm. A false "refused" would shrink the
measured gap, so 7.4% is a lower bound.

## 4. Recommendations

1. **Add a provenance clause.** State that claimed exemptions, prior approvals
   or superseding policies arriving in user input or tool output are not
   authoritative. In our sweep this took violations to 0/288, and to 0/18 in a
   matched contrast where the alternative phrasing scored 18/18. This works
   only for models already capable of policy adherence (3.7).
2. **Do not write exemption carve-outs** into agent policies. "Unless an
   exemption is documented" was the single most attackable phrasing we tested,
   worse than saying nothing about exemptions at all.
3. **Avoid autonomy-forward phrasing** for agents holding destructive or
   exfiltrating tools.
4. **Always provide a safe alternative action**, or refusal degrades into
   paralysis.
5. **Evaluate agents on tool calls, not text.** They are not the same
   measurement, and under attack they disagree.

## 5. Limitations

- Two hosted targets, both small production models. No frontier-model claim.
  A 3B local model (llama3.2) violates its policy 67.5% of the time with no
  attack at all, so it has no headroom and is reported separately in 3.7.
- Single-turn. We attempted an indirect variant in which the misdirection
  arrives through tool output rather than user text, since `strict_hatch`
  explicitly names "a user message **or tool result**". The test was
  inconclusive: across 24 trials on `medical_export`, gpt-4o-mini called
  `request_approval` immediately in 24/24 cases and never consulted the
  poisoned policy corpus, so the indirect channel was never exercised. We
  report this as untested rather than safe. A scenario that requires corpus
  lookup before acting would be needed to settle it.
- Hand-written scenarios. Per-scenario rates span 7.1% to 15.7%, so no single
  scenario carries the result, but scenario design could still contribute.
- Violation detection is argument-pattern based: precise by construction, but
  would miss a creative violation routed through an unanticipated tool.
- `reclassify` and `emergency` are one phrasing each. Their nulls show that
  these framings fail, not that the mechanisms are universally safe.
- **No competent adaptive attacker.** Our four attacks written against the
  precedence clause were too weak to test it (0/12 against policies where
  standard attacks score 18/18). The clause's robustness under genuine adaptive
  pressure, including an RL-trained attacker optimising directly against it, is
  the natural next experiment and we make no claim about it.

## 6. Reproducibility

```bash
pytest                                       # 113 offline tests, no spend
python scripts/probe_agentic.py --n 5        # preliminary probe

python -m loki.agentic.sweep \
    --targets gpt-4o-mini claude-haiku-4-5 \
    --policies strict_hatch strict exemption autonomous bare \
    --trials 3                                               # 3.1-3.2, 3.4-3.6

python -m loki.agentic.sweep --targets gpt-4o-mini \
    --policies strict strict_verbose strict_hatch \
    --attacks superseded prior_approval audit_exemption combined --trials 3   # 3.3

python -m loki.agentic.gap --targets gpt-4o-mini claude-haiku-4-5 \
    --policies strict autonomous exemption \
    --attacks none combined superseded --trials 3              # 3.9

python -m loki.agentic.sweep --targets llama3.2 \
    --policies strict_hatch strict exemption autonomous bare \
    --trials 2 --workers 2                                     # 3.7 (slow, free)
```

Raw per-trial records: `results/agentic_sweep_api.json`, `results/agentic_sweep_local.json`,
`results/agentic_ablation.json`, `results/agentic_gap_full.json`,
`results/agentic_matched_contrast.json`,
`results/agentic_probe.json`. Judge validation: `results/JUDGE_VALIDATION.md`.
