# Longer Paper Ground Check

Date: 2026-09-06

## Current submission readiness

- Regular-paper draft: `paper/extended.tex`, currently compiles to **9/9 pages**.
- Short paper has been handed off. The longer paper is now the active target.
- Repo-side baseline from prior/follow-up passes: tests, lint, package build, CLI smoke tests, LaTeX compile, and page-count checks have passed.
- Honest readiness before further new experiments: **65-70% submit-ready**, **50-55% A+ ready**.
- Time to best possible today: **3-5 focused hours** for polishing + one targeted data/figure pass. More broad data is not worth it today.

## Defensible thesis

The strongest defensible thesis is:

> Fabricated authority is a policy-provenance failure mode for tool-calling agents. In hosted models with low baseline policy violations, direct user-channel fabricated authority causes statistically significant forbidden tool calls. A prompt-level provenance clause eliminates the direct-channel failures we tested, but poisoned tool-output authority still breaks it, so runtime provenance controls are required for indirect channels.

This is stronger and more novel than saying “authority jailbreaks work,” because the object of study is the **deployment policy contract** and the dependent variable is a **logged external action**.

## What must not be claimed

- Fabricated authority is new in all LLM settings.
- The prompt clause is a universal defense.
- Prompt wording replaces runtime provenance enforcement.
- The result generalizes to all frontier models.
- Judge unreliability is the paper’s primary novelty.
- Text refusal is sufficient evidence of agent safety.

## Abstract check

The current abstract is fendable because it states:

- exact direct-channel scale: 1,968 hosted-model trials,
- exact control and attack rates,
- policy wording as the independent variable,
- matched contrast and length-control ablation,
- adaptive attacker check,
- Sonnet negative result,
- forced indirect-channel failure that bounds the mitigation.

The abstract is now appropriately narrow: it says policy provenance is a control surface, not that a prompt sentence solves tool safety.

## Novelty check against closest work

### DarkCite / authority-citation jailbreaks

Overlap: fabricated authority/citation as an attack pattern against chat LLMs.

Difference: this paper measures external **tool-call violations**, varies **operating-policy phrasing**, and studies whether a deployer-provided provenance rule changes agent behavior. The outcome is not harmful text generation.

Novelty impact: DarkCite weakens any claim that authority framing is new. It does not kill the agentic policy-provenance/tool-log contribution.

### Context-Fractured Decomposition Attacks

Overlap: provenance gaps in tool-using agents and artifact-mediated failures.

Difference: their object is cross-context multi-step artifact composition and provenance lineage tagging. This paper's strongest core is single-turn operating-policy phrasing as a controlled variable, plus direct-vs-indirect channel separation.

Novelty impact: high-risk close prior. The longer paper now cites it and frames indirect-channel results as complementary evidence that prompt-level provenance is insufficient for tool-output channels.

### AutoInject / WARD / prompt injection defenses

Overlap: prompt injection and binary tool-call success.

Difference: those works focus on generic injection/defense mechanics in web or agent environments. Our main variable is deployment policy semantics: which kinds of exceptions and authority provenance rules make the same model fail.

Novelty impact: raises empirical bar but improves venue fit.

### GAP / AgentSeer

Overlap: text/tool safety gap and agent safety benchmarks.

Difference: we do not only benchmark the gap. We isolate a deployer-controlled variable, policy provenance wording, and show direct-channel mitigation plus indirect-channel failure.

Novelty impact: strong venue fit.

## Comparison to prior AIWILD-style accepted work

The ICML 2026 AIWILD program included action-level agent-security papers and talks such as LinuxArena, WARD, and command-line agent risk work. Common traits:

- concrete agentic environment,
- action-level measurement rather than chat-only scoring,
- realistic staged tasks,
- security/safety failure mode with deployment relevance,
- honest negative or boundary results.

Our longer paper matches those traits. Its weaker points are breadth, figure polish, and limited model coverage.

## Estimated acceptance odds

These are educated estimates, not guarantees.

- **If submitted as-is after compile/package only:** 50-55%.
- **After polish of thesis, related work, figures/tables, and final validation:** 60-65%.
- **Best plausible by today with no broad new data:** 65-70%.
- **True A+ / main-conference-ready:** not today. Needs more models, more scenarios, stronger adaptive/RL attacker, and runtime provenance defense evaluation.

## Highest-return next moves

1. Tighten the longer paper around the direct-vs-indirect provenance thesis.
2. Improve figure/table readability without changing claims.
3. Re-run claim guards and compile to exactly 9 pages.
4. Refresh the regular-paper submission bundle.
5. Only collect new data if it directly addresses a named weakness. Broad random data is not cost-effective now.

## Decision

Proceed with writing/presentation polish and validation first. The existing data is enough for a credible regular-paper submission; the bottleneck is clarity, not another generic sweep.

## Targeted extra data collected after ground check

A compact `gpt-4.1-mini` breadth sweep was run because model breadth was the cleanest remaining weakness:

- 280 trials, zero errors.
- Control: 0/40.
- Attacked: 68/240, 28.3%, Fisher p = 5.38e-06.
- `strict_hatch`: 0/48 attacked.
- `exemption`: 30/48 attacked, 62.5%.
- Contrast: 0/48 vs 30/48, Fisher p = 1.06e-12.

Impact: this improves the longer paper because the direct-channel provenance ordering now replicates on a third hosted model. It does not make a full frontier-model claim, because Sonnet remains a compact negative result.
