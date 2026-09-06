# OpenReview-Facing Validation

Date: 2026-09-06

## Public interface check

- Public AIWILD OpenReview group URL fetched: `https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/AIWILD`.
- The public page loads but does not expose the actionable submission form without the logged-in JavaScript app/session.
- AIWILD workshop guidelines confirm: regular papers are 9 pages, references and supplementary material excluded, double-blind anonymization required, and OpenReview is the submission site.

## Prepared metadata

Metadata prepared in `submission_bundle/regular/OPENREVIEW_METADATA.md`:

- Title
- Track
- Anonymous author field
- Keywords
- Plain-text abstract with LaTeX stripped
- Main/supplement upload file paths
- Public-interface boundary note

## Final validation after adding metadata

- Rebuilt `submission_bundle/upload/aiwild_regular_submission_bundle.zip`.
- Zip integrity: passed.
- Zip file count: 10.
- Main PDF: 9 pages, unencrypted, parseable.
- Supplement PDF: 3 pages, unencrypted, parseable.
- Zip contents scanned for author names, secret markers, and local paths: clean.
- Desktop archive refreshed with rebuilt zip and metadata.
- Current zip SHA-256: `f281e640745b5a0818499a5f58461838ab5d54fef8eefba859911364091d9dbc`.

## Boundary

This validates the submission package against the public venue requirements and upload-like local behavior. It does not press OpenReview submit, because that requires the user's account/session and explicit final confirmation.
