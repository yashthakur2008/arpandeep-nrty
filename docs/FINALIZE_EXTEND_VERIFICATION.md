# Finalize-and-Extend Verification Report

This report closes the feedback-loop gap for the request: "fill in all the cracks" in the first draft, then begin a larger-page second draft.

## Requirement-to-check traceability

| Requirement / changed public output | Check exercised | Observed result |
|---|---|---|
| Finalize the first 4-page AIWILD draft | `tectonic paper/main.tex --outdir paper`; macOS `mdls -name kMDItemNumberOfPages paper/main.pdf` | Compile succeeded; generated PDF metadata reports 4 pages. |
| Preserve verified numerical claims | `uv run pytest tests/test_paper_claims.py tests/test_agentic.py -q`; direct JSON checks for headline numbers | 59/59 targeted tests passed; direct checks confirmed 0/240 controls, 208/1440 attacks, 54/80 llama controls, 270/480 llama attacks, adaptive 8/8 vs 0/8 and 7/8 vs 0/8. |
| Keep repository-level correctness after edits | `uv run pytest -q` | Full suite passed: 148 tests, with only existing transformer checkpoint warnings. |
| Keep style/lint clean | `uv run ruff check .` | Passed: all checks passed. |
| Exercise packaging/integration path | `uv build` | Built `dist/loki-0.2.0.tar.gz` and `dist/loki-0.2.0-py3-none-any.whl`. |
| Exercise public CLI interfaces | `uv run python -m loki.agentic.sweep --help`, `loki.agentic.gap --help`, `loki.agentic.adaptive --help`, `loki.eval --help`, `loki.judge_study --help` | All help commands exited successfully. |
| Document first-draft cracks | `docs/FIRST_DRAFT_CRACKS.md` content sanity check | File exists, 352 words, and includes novelty risk, length confound, scenario-strength confound, small-model boundary, and official-style caveat. |
| Begin larger-page second draft | `docs/PAPER_EXTENDED_DRAFT.md` content sanity check | File exists, 2,775 words, with abstract, introduction, threat model, setup, results, related work, recommendations, limitations, next additions, and conclusion. |
| Avoid stale placeholders | Scan `docs/FIRST_DRAFT_CRACKS.md`, `docs/PAPER_EXTENDED_DRAFT.md`, and `paper/main.tex` for common unfinished-marker strings | No placeholders found. |

## Real acceptance path exercised

The closest local acceptance path for the short paper was exercised: the submission PDF was regenerated from `paper/main.tex`, the page count was checked from the produced PDF, and the paper's claims were tested against raw result artifacts. External submission itself is blocked because it requires using the venue submission portal and, if required, the official AIWILD/NeurIPS style file. The repository contains a standalone fallback style, but the official style file is not vendored.

## Coverage beyond the narrow path

The validation covered main workflows, packaging, CLIs, paper compilation, claim traceability, result artifact loading, lint, and placeholder checks. The extended draft itself is markdown, not yet a long-form compiled LaTeX/PDF artifact, so its validation is content and traceability based rather than final-publication-format based.

## Assessment

The result is better than before: the first draft now has a crack checklist tied to concrete fixes and caveats, and the second draft now exists as a longer, structured paper draft rather than a plan. The remaining work for a future longer paper is substantive expansion: more targets, multi-turn and indirect-channel experiments, and possibly an RL-trained attacker against `strict_hatch`.
