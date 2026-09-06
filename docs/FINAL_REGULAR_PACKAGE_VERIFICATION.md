# Final Regular Package Verification

Date: 2026-09-06

## Final upload candidate

- Main PDF: `submission_bundle/regular/aiwild_regular_anonymous.pdf`
- Supplement PDF: `submission_bundle/regular/aiwild_regular_supplement.pdf`
- Zip package: `submission_bundle/upload/aiwild_regular_submission_bundle.zip`

## Acceptance-path checks exercised

- Zip opens successfully and contains 9 expected files.
- Main PDF parses with `pypdf`: 9 pages, unencrypted.
- Supplement PDF parses with `pypdf`: 3 pages, unencrypted.
- PDF extracted text and bundled `.tex`/`.md` files were scanned for author-name strings and secret markers: none found.
- `uv build` succeeded.
- Public CLI smoke checks succeeded for `loki.agentic.indirect` and `loki.agentic.sweep`.
- Targeted tests passed: 60/60.
- Desktop archive refreshed with regular bundle and zip.

## Boundary

OpenReview upload was not exercised because it requires user login/session and explicit final submit confirmation. The local artifact path now matches the intended upload workflow as closely as possible without taking that consequential step.
