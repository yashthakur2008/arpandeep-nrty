# AIWILD Submission Checklist

## Current status
- Main contribution: fabricated-authority attacks against policy-constrained tool-using agents.
- Measurement: logged tool calls, not LLM-judged text.
- Draft source: `paper/main.tex`.
- Markdown draft: `docs/PAPER_DRAFT.md`.
- Results summary: `results/AGENTIC_RESULTS.md`.
- Handoff for second set of hands: `docs/SECOND_HANDS.md`.

## Verification completed
- Offline test suite passes: `python -m pytest -q`.
- Repo lint passes: `ruff check .`.
- Paper compiles standalone with Tectonic.
- Compiled PDF is 4 pages on the fallback standalone style.

## Before submission
1. Put the official workshop/NeurIPS style file in `paper/` if required by the submission site.
2. Recompile `paper/main.tex` after adding the official style.
3. Confirm the PDF remains within the workshop page limit.
4. Re-run claim guards: `python -m pytest -q tests/test_paper_claims.py`.
5. Do one final read of abstract, limitations, and conclusion for consistency.
6. Remove any generated `.aux`, `.out`, or local build artifacts before committing.

## Do not change unless necessary
- Do not pivot back to the judge-only paper.
- Do not weaken the central tool-call measurement story.
- Do not claim universal robustness for `strict_hatch`; claim only what the logged experiments show.
- Do not add new expensive sweeps unless they directly improve the submission.

## Strongest paper claims to preserve
- Control produced 0/240 hosted-target violations.
- Fabricated authority produced 208/1440 hosted-target violations.
- `strict_hatch` produced 0/288 violations in the main sweep.
- Matched contrast: 0/18 vs 18/18 on identical scenario/attacks.
- Length control refutes “more words equals safer policy”.
- Text can refuse while the tool still fires: 32/432 paired trials.
- Adaptive attacker broke 7-8/8 control scenarios and 0/8 `strict_hatch` scenarios across two runs.
