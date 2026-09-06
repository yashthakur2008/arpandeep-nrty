# Final End-to-End Acceptance Validation

Date: 2026-09-06

## Upload-like checks

- Final zip: `submission_bundle/upload/aiwild_regular_submission_bundle.zip`.
- Zip integrity: `testzip` returned `None`.
- Zip file count: 9 files.
- Main PDF MIME type: `application/pdf`, 9 pages, unencrypted.
- Supplement PDF MIME type: `application/pdf`, 3 pages, unencrypted.
- Zip MIME type: `application/zip`.
- Current zip SHA-256: `b47f69ad8f73da1e29d40cf27fd13c1f0e41a25ce08e061ada3f542cbcdf4d5e`.

## Integration-boundary checks

- README references now resolve to included bundle files.
- Zip contents were scanned after rebuild for author names, local paths, and secret markers.
- No matches found for author names, OpenAI/Anthropic key markers, or local `/Users/yashthakur` path.
- PDFs parse through `pypdf`, which is a local proxy for upload/readability behavior.
- Desktop archive was refreshed with the rebuilt zip and corrected README.

## Boundary

This is the furthest non-destructive validation available locally. Actual OpenReview acceptance behavior still requires browser/login/upload and final submit confirmation from the user.
