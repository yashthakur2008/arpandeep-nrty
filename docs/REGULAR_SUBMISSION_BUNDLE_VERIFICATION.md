# Regular Submission Bundle Verification

Date: 2026-09-06

## What this iteration adds

Because the main regular paper is now exactly 9 pages, remaining support was moved into an anonymous supplement and a regular-only submission bundle instead of expanding the main paper.

## Remaining hypotheses addressed

| Concern | Supplement/bundle support |
|---|---|
| Scenario design may look opaque | Supplement lists all 8 scenarios, families, and forbidden action classes |
| Policy variants may be under-specified | Supplement lists policy variants and the exact provenance clause |
| Attack taxonomy may be unclear | Supplement lists all attack families and the pressure types they represent |
| Raw claims may be hard to trace | Supplement maps each result JSON to its role in the paper |
| Reviewers may worry the main paper hides limitations | Supplement states remaining open hypotheses: multi-turn, stronger adaptive attacker, more repetition, broader models |

## Public-interface and acceptance behavior checks

- Main regular PDF: `submission_bundle/regular/aiwild_regular_anonymous.pdf`.
- Supplement PDF: `submission_bundle/regular/aiwild_regular_supplement.pdf`.
- Main PDF parsed successfully with `pypdf`: 9 pages, unencrypted.
- Supplement PDF parsed successfully with `pypdf`: 3 pages, unencrypted.
- Both PDFs contain `Anonymous Author(s)`.
- Both PDFs were scanned for identifying author-name strings: none found.
- Regular bundle `.tex` and `.md` files were scanned for identifying author-name strings: none found.
- Targeted tests passed: 60/60.
- Desktop archive refreshed with the regular bundle.

## OpenReview boundary

The actual OpenReview upload was not exercised because it requires the user's account/session and explicit final confirmation. The local bundle is the closest non-destructive acceptance-path proxy: the exact files intended for upload are parseable, anonymized, within page constraints, and backed by tests/artifacts.

## Verdict

The longer submission is now substantially stronger without exceeding the 9-page main-paper limit. It has a main PDF, anonymous supplement, result-artifact map, and a clean regular-only bundle suitable for final human skim and OpenReview upload.
