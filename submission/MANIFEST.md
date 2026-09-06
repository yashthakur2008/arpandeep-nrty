# Submission Bundle Manifest

Generated: 2026-09-05

## Ready-to-submit short paper

- PDF: `submission/aiwild_short_anonymous.pdf`
- Source: `submission/aiwild_short_anonymous.tex`
- Title: **Fabricated Authority in the Wild: Policy Provenance Controls Direct Tool-Calling Agent Failures**
- Review mode: anonymous / double-blind
- Page count observed: 4 pages
- Lead author for camera-ready: Yash Thakur
- Backup authors for camera-ready: Aayushya Patel, Pranav Burra

## Longer follow-on draft

- PDF: `submission/extended_followon_anonymous.pdf`
- Source: `submission/extended_followon_anonymous.tex`
- Title: **Fabricated Authority in the Wild: Policy Provenance as a Control Surface for Tool-Calling Agents**
- Review mode: anonymous / double-blind
- Page count observed: 7 pages
- Status: updated after quick novelty check. The short-paper claim is now explicitly bounded to direct user-message fabricated authority; a forced indirect-channel pilot is treated as a limitation/follow-on.

## Verification performed

- `paper/main.tex` compiled with Tectonic.
- `paper/extended.tex` compiled with Tectonic.
- macOS metadata reports 4 pages for the short paper and 7 pages for the extended paper.
- Full project tests passed in the previous acceptance pass.
- Ruff passed in the previous acceptance pass.
- `uv build` passed in the previous acceptance pass.
- Public CLI and wheel-install acceptance checks passed in the previous acceptance pass.

## Final submission note

The repository does not vendor the official NeurIPS/AIWILD style file. The source compiles with the standalone fallback. If the submission portal requires the official style, place the official style file in `paper/`, enable the style switch in `paper/main.tex`, recompile, and recheck the 4-page limit before upload.


## Update 2026-09-05 late (short paper rewritten after council review)

`aiwild_short_anonymous.tex/.pdf` regenerated from `paper/main.tex`. Requires
`figures/fig1_threat_model.pdf`, `fig2_policy.pdf`, `fig3_channel.pdf` beside
it (copied here). Body + Appendix A on 4 pages, references on page 5.

What changed and why: see the commit message and `paper/council_2026-09-05/`.
Short version: three cold readers (a deployer, a science editor, a hostile ML
reviewer) independently found the abstract had ~33 undefined terms, the paper
opened with the abandoned judge experiment, the one-sentence mitigation was
never quoted, and five counts disagreed between abstract, figures, and drafts.
All fixed; `tests/test_paper_claims.py` 36/36 against the new text. Round-2
cold read: deployer 5 -> 7, editor 5 -> 6, deployer can state the result from
the abstract alone and names three concrete deployment changes.

The regular (9-page) paper in `submission_bundle/regular/` has NOT been
updated and still carries the old abstract, the 198/840 denominators, and the
8/24 indirect numbers from a different run than the short paper's 15/36.
