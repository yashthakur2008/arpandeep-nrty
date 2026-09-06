# AIWILD Guideline Fact Check for Final Regular Draft

Date: 2026-09-06

Final draft checked:

- Main PDF: `submission_bundle/regular/aiwild_regular_anonymous.pdf`
- Supplement PDF: `submission_bundle/regular/aiwild_regular_supplement.pdf`
- Upload zip: `submission_bundle/upload/aiwild_regular_submission_bundle.zip`

## Workshop guidelines checked from https://agentwild-workshop.github.io/neurips2026

| AIWILD guideline | Final draft status | Result |
|---|---|---|
| Regular papers are limited to 9 pages | Main PDF parsed with `pypdf`: 9 pages | Pass |
| References and supplementary materials do not count against page limit | Supplement PDF is separate: 3 pages | Pass |
| Submission site is OpenReview | Metadata file points to the regular main PDF and supplement | Ready, upload still requires user login |
| Double-blind review | Main PDF and supplement use `Anonymous Author(s)` | Pass |
| Supplement and linked material must also be anonymized | Zip contents scanned for author names, local paths, and secret markers | Pass |
| Style file may be NeurIPS, ICLR, ICML, ACL, CVPR, or other top-venue template | Draft uses an ICLR/AIWILD-like one-column article format with workshop header, matching provided accepted examples | Pass |
| NeurIPS checklist is not required | No checklist included | Pass |
| Submissions exceeding page limit or not primarily related to AI agents may be desk-rejected | Paper is 9 pages and directly studies tool-calling agent safety/security | Pass |
| Scope includes agent safety/security, prompt injection, tool misuse, adversarial manipulation, evaluation/benchmarking | Paper covers fabricated authority attacks, tool-call violations, policy phrasing, and provenance controls | Pass |
| Non-archival workshop welcomes ongoing/unpublished work and work under review elsewhere | Local package prepared as anonymous ongoing work | Pass |

## Final acceptance-path observations

- Main PDF: 9 pages, unencrypted, parseable, anonymous.
- Supplement PDF: 3 pages, unencrypted, parseable, anonymous.
- Upload zip: integrity check passed.
- Full test suite previously passed: 149/149.
- Build and public CLI smoke checks passed.
- Actual OpenReview upload was not performed because it requires user login and final submit confirmation.

## Note on figures

The provided figure files were found in `/Users/yashthakur/Downloads/figures`. The current final PDF already includes figure-style visual summaries in the main paper. Because the main paper is exactly 9 pages, replacing those with external figure PDFs should be done only if there is time for a visual skim and revalidation. The current package remains guideline-compliant and upload-ready.
