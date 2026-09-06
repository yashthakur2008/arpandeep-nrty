# Second Set of Hands: Paper Progress Instructions

## Goal
Keep the repository moving toward a **submittable NeurIPS 2026 Agents in the Wild paper**. The current paper direction is the **agentic tool-call / policy-phrasing** result. Do **not** pivot back to the judge-validity-only story.

## What is already true
- The repo now has a working agentic harness, results, and paper draft.
- The strongest current contribution is:
  - fabricated authority can induce tool-call violations
  - policy phrasing changes attack success dramatically
  - the effect is measured with logged tool calls, not an LLM judge
- The adaptive attacker was tested and did **not** break `strict_hatch`, which supports the bounded claim.
- `paper/main.tex` was made standalone and the paper source should be kept aligned with the verified results.

## Highest-priority tasks
1. **Verify paper build health**
   - Confirm `paper/main.tex` still compiles cleanly.
   - Confirm the output stays within the workshop page limit.
   - If compile fails, fix the paper source, not the results.

2. **Keep claims aligned with evidence**
   - Check `docs/PAPER_DRAFT.md`, `results/AGENTIC_RESULTS.md`, and `paper/main.tex` against the JSON outputs.
   - Remove or soften any claim that is not directly supported by the logged runs.
   - Do not introduce stronger claims about robustness than the adaptive attack actually supports.

3. **Focus on paper readiness, not new experiments**
   - Only run new experiments if they directly strengthen the paper’s current core claim.
   - Prefer cheap verification, claim guards, formatting, and reproducibility over more exploration.

4. **Maintain repo hygiene**
   - Keep the working tree clean.
   - Avoid reintroducing stale artifacts or duplicate summaries.
   - Do not commit secrets or reference API keys.

## Suggested next checks
- Run the claim tests for the paper.
- Rebuild or re-render the paper PDF.
- Confirm the paper title, abstract, and conclusion all point to the same contribution.
- Confirm the limitation section clearly states what the adaptive attacker did and did not prove.

## If you need to act independently
- Prefer paper progression over experimentation.
- Prefer conservative claims over broader ones.
- If a result is uncertain, label it as a limitation.
- If a paper-facing file conflicts with the verified results JSON, update the paper-facing file.

## Do not do
- Do not revive the judge-only novelty angle as the main paper.
- Do not overclaim that `strict_hatch` is universally robust.
- Do not spend time on large new sweeps unless they directly improve submission quality.

## Definition of success
- Paper source compiles.
- Claims match verified results.
- Submission package is internally consistent.
- The paper is ready for final formatting and submission.
