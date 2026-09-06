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
