# A-Level Regular Paper Readiness Report

Date: 2026-09-06

## Final readiness verdict

The regular AIWILD paper is now at the strongest local non-destructive readiness state available before human/OpenReview upload. It is not literally guaranteed acceptance, but it is formatted, anonymized, evidence-backed, packaged, and validated against the workshop constraints.

Estimated current state:

- Submit readiness: 90-93% locally complete.
- A-level workshop competitiveness: 75-80% of ideal.
- Estimated acceptance odds after final hardening: 60-70%, depending on reviewer appetite for compact empirical scope versus novelty of the policy-provenance framing.

## What makes it competitive

- Agent-specific phenomenon: unsafe tool calls, not just unsafe text.
- Direct logged-action metric: no LLM judge for headline safety outcome.
- Clear thesis: fabricated authority is a policy-provenance failure mode.
- Controlled policy matrix: strict_hatch, strict, bare, autonomous, exemption, and length-control variants.
- Strong direct-channel result: strict_hatch 0/288 versus exemption 93/288.
- Robustness checks: length ablation, matched contrast, adaptive attacker, text/action divergence, small-model boundary.
- New all-scenario indirect result: clean 0/48, poisoned 32/48, strict_hatch 8/24, exemption 24/24.
- Honest limitation: prompt provenance helps direct user claims but does not replace runtime provenance for tool outputs.
- Submission resources: anonymous main PDF, supplement, metadata, manifest, upload zip, and artifact map.

## What remains below a true A+ archival paper

- Only two main hosted target models plus one compact Sonnet negative check.
- Single-turn scenarios.
- Hand-written scenarios rather than a large external benchmark.
- All-scenario indirect expansion is one trial per cell because of deadline constraints.
- Actual OpenReview upload was not performed because it requires user login and final confirmation.

## Final validation performed

- Main PDF compiles with Tectonic: 9 pages.
- Supplement compiles with Tectonic: 3 pages.
- Final zip integrity: passed.
- Final zip file count: 10.
- Main and supplement PDFs are unencrypted and parseable.
- Full repository test suite passed: 149/149.
- `uv build` passed.
- Public CLI smoke checks passed for sweep, gap, adaptive, and indirect interfaces.
- Zip contents scanned for author names, secret markers, and local paths: clean.
- Desktop archive refreshed.

## Final upload targets

- Main PDF: `submission_bundle/regular/aiwild_regular_anonymous.pdf`
- Supplement PDF: `submission_bundle/regular/aiwild_regular_supplement.pdf`
- Handoff zip: `submission_bundle/upload/aiwild_regular_submission_bundle.zip`
- OpenReview metadata: `submission_bundle/regular/OPENREVIEW_METADATA.md`

## Final recommendation

Submit the regular paper if OpenReview accepts one main PDF plus supplementary PDF. If the form only accepts one PDF, upload the main paper first and use the supplement only if the portal provides a supplementary-material field. Do not upload source files unless explicitly requested.
