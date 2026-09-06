# Longer Paper Acceptance-Path Verification

Date: 2026-09-06

## Requirement-to-check map

| Requirement | Check exercised | Observed result |
|---|---|---|
| Longer paper thesis/abstract must be defensible and novel | Compared current extended draft against AIWILD call, two accepted AIWILD examples, and closest prior work: DarkCite, Context-Fractured Decomposition, and automated agentic prompt injection | Defensible only with narrow claim: policy-provenance phrasing for tool-calling agents, with direct vs indirect channel separation |
| Must have a realistic acceptance estimate | Wrote `docs/LONGER_GROUND_CHECK.md` with fit and odds after comparison | Current regular odds estimated 40-50%; after scaled result and polish 55-65%; best-case 65-70% |
| Must collect useful extra data before submission | Ran real OpenAI API scaled forced-indirect experiment over all 8 scenarios, 2 policies, 3 attacks, clean/poisoned, 1 trial | 96/96 valid trials, 0 errors, 96/96 lookup consultations |
| New result must improve the paper rather than only add volume | Analyzed `results/agentic_indirect_all8_t1.json` | Clean 0/48; poisoned 32/48; strict_hatch 8/24; exemption 24/24; all scenario families showed violations |
| Results must appear in the public submission artifact | Extracted text from `paper/extended.pdf` and searched for updated claims | Found “clean lookups cause 0/48”, “poisoned lookups cause 32/48”, “8/24 under the provenance-aware policy”, workshop header, and anonymous author text |
| Regular submission must fit page limit | Compiled with Tectonic and checked PDF page count with pypdf | `paper/extended.pdf` is 8 pages, under 9-page regular limit |
| Artifact must be readable/uploadable | Opened PDF with pypdf metadata/page parser | Repo and desktop archive PDFs are unencrypted, readable, 8 pages |
| Experiment interfaces must remain usable | Ran public CLI help paths | `loki.agentic.indirect`, `sweep`, `gap`, and `adaptive` CLIs all returned help successfully |
| Claim tests must still pass | Ran targeted test suite | `tests/test_agentic.py` and `tests/test_paper_claims.py`: 60 passed |
| Local archive must contain updated long-paper files | Checked archive PDF and copied updated files | Desktop archive has updated `paper/extended.pdf`, `paper/extended.tex`, `docs/LONGER_GROUND_CHECK.md`, and `results/agentic_indirect_all8_t1.json` |

## Acceptance-path status

The real OpenReview upload was not exercised because it requires user account/session interaction and final submission confirmation. The closest available acceptance path was exercised locally: compile the exact PDF artifact, verify it is anonymous and under page limit, parse the PDF as an uploadable file, verify the updated claims are in the compiled artifact, verify the public experiment CLIs, and verify the raw result artifact.

## Weak points remaining

- One minor LaTeX overfull hbox warning remains at line 152. It does not block PDF generation or page limit, but should be cleaned during final polish.
- `submission_bundle/` remains untracked and appears unrelated to this change. It was intentionally not committed.
- The all-scenario indirect run used 1 trial per cell to fit deadline constraints. It is broader than the prior 4-scenario result, but lower-repetition.
- The long paper still needs figures and related-work polish to read like an A-level regular submission.

## Verdict

The work is measurably better after the scaled result. The longer paper now has a stronger, channel-dependent thesis backed by all-scenario indirect evidence, and the compiled PDF reflects those claims. It is not yet A+ polished, but it is substantially closer to a credible regular-track submission than before this pass.
