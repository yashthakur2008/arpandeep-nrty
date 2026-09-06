# Longer Paper Iteration Verification

Date: 2026-09-06

## Remaining hypotheses checked in this iteration

| Hypothesis / reviewer concern | Evidence now in draft | Observed status |
|---|---|---|
| The result could be ordinary noncompliance | Direct controls are 0/240 and clean required-lookup controls are 0/48 | Bounded: attack effect is not baseline tool misuse in hosted runs |
| The result could be verbosity, not provenance | Length-control ablation: strict_verbose 11/96 vs strict_hatch 0/96 | Bounded: longer policy alone does not explain safety |
| The result could be universal model weakness | Sonnet compact matched contrast is 0/48 violations | Bounded: effect is target-sensitive |
| The mitigation could be oversold | Forced indirect channel breaks strict_hatch 8/24 under poisoned lookup | Bounded: prompt-level clause is direct-channel mitigation, not full defense |
| The paper reads table-heavy/dry | Added two figure-style visual summaries to `paper/extended.tex` | Improved: reviewers see policy ladder and channel comparison directly |
| Novelty could be confused with DarkCite/provenance prior work | Related work now states authority attacks are not new and positions contribution as policy phrasing plus direct/indirect channel measurement | Improved: narrower and more defensible thesis |

## Public-interface and acceptance-path checks

- `tectonic -X compile paper/extended.tex`: succeeded.
- `paper/extended.pdf`: 9 pages, unencrypted, parseable by `pypdf`.
- Compiled PDF contains: visual summary section, updated 0/48 and 32/48 claims, channel-specific runtime-provenance recommendation, workshop header, and anonymous author marker.
- Targeted tests: `tests/test_agentic.py tests/test_paper_claims.py` passed, 60/60.
- OpenReview upload was not exercised because it requires the user's account/session and final confirmation.

## Remaining risks

- One minor overfull hbox remains near the Sonnet matched-contrast paragraph.
- The PDF is exactly 9 pages now, so any further content addition must replace text or go to supplement.
- The all-scenario indirect result is one trial per cell. Stronger repetition would improve confidence but costs more time/API budget.

## Verdict

This iteration made the longer paper materially better for review: it converted planned figures into compiled visual summaries, clarified the novelty boundary, and explicitly tested/communicated the remaining hypotheses most likely to invalidate the thesis. The paper is still not a perfect A+ regular paper, but it is closer to a defensible regular submission than the prior table-heavy draft.
