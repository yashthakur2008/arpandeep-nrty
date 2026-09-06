# OpenReview-Facing Metadata

Title: Fabricated Authority in the Wild: Policy Provenance as a Control Surface for Tool-Calling Agents

Track: Regular paper, 9-page limit excluding references and supplement.

Anonymous authors field: Anonymous Author(s)

Keywords: tool-calling agents; agent safety; prompt injection; policy provenance; fabricated authority; tool-use evaluation; AI security

Abstract:
Tool-using language-model agents can refuse in text while still taking an unsafe action. We study fabricated authority: user-controlled claims that a forbidden action is allowed by a non-existent approval, exemption, or superseding policy. Across 1,968 hosted-model direct-channel trials with 8 scenarios, 6 operating-policy phrasings, 7 attack templates, and 2 production models, fabricated authority raises logged tool-call violations from 0/240 in controls to 208/1440 under attack (14.4%, p = 1.1e-15). The dominant variable is operating-policy wording: a provenance-aware policy has 0/288 direct user-message violations, while a documented-exemption carve-out has 93/288 (32.3%). A matched contrast gives complete separation, 18/18 versus 0/18. A length-control ablation shows this is not verbosity, and two adaptive-attacker runs break weak controls while failing to breach the provenance-aware policy. We then scale a forced indirect-channel study to all 8 scenarios: when the same fabricated authority arrives through a required policy-lookup tool, clean lookups cause 0/48 violations but poisoned lookups cause 32/48, including 8/24 under the provenance-aware policy and 24/24 under the exemption policy. These findings suggest that agent evaluations should score tool logs, deployment prompts should reject unauthenticated authority claims, and production systems need runtime provenance controls for tool outputs.

Upload files:
- Main PDF: `submission_bundle/regular/aiwild_regular_anonymous.pdf`
- Supplement PDF: `submission_bundle/regular/aiwild_regular_supplement.pdf`
- Optional bundle zip for handoff: `submission_bundle/upload/aiwild_regular_submission_bundle.zip`

Public interface status:
- AIWILD OpenReview public group page loads, but the actionable submission form requires login/session JavaScript.
- OpenReview upload/submission was not attempted because it requires user account access and final confirmation.
