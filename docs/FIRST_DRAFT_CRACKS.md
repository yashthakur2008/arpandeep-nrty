# First-draft cracks and fixes

This checklist records the cracks identified in the 4-page AIWILD draft and how they are handled before using it as the base for the longer draft.

## Fixed or explicitly handled

1. **Judge-reliability novelty risk.** The short paper no longer claims novelty for judge failure. It cites stronger concurrent work and uses the judge failure only as motivation for switching to logged tool calls.
2. **Outcome ambiguity.** The agentic dependent variable is a structured violation predicate over tool name and arguments. Text alone cannot decide success.
3. **Length confound.** The `strict_verbose` ablation shows that longer policy text is not the reason `strict_hatch` works: 0/96 vs 11/96, Fisher p = 0.000361.
4. **Scenario-strength confound.** The matched contrast fixes scenario, model, temperature, and attack text: `exemption` 18/18 vs `strict_hatch` 0/18, Fisher p = 1.1e-10.
5. **Weak adaptive attack false reassurance.** The hand-written adaptive attempt is reported as uninformative because it failed to break weak controls. The LLM adaptive attacker is reported only because it breaks control policies 8/8 and 7/8 while failing on `strict_hatch` 0/8 twice.
6. **Small-model generalization.** The llama3.2 run is not pooled. It bounds the recommendation: policy phrasing helps only when the model can follow policy at baseline.
7. **Text-vs-tool evaluation gap.** The paired gap study shows 32 cases where prose refusal and forbidden tool execution disagree, with 0 such cases in controls.
8. **Compile and page budget.** Tectonic compiles `paper/main.tex`; macOS metadata reports `paper/main.pdf` is exactly 4 pages.
9. **Claim drift.** `tests/test_paper_claims.py` guards the published numerical claims against raw JSON artifacts.
10. **Secrets.** The whole-result verification scanned tracked files for live key prefixes and found none.

## Still honest limitations

- Only two hosted targets are in the main sweep.
- Scenarios are hand-written.
- The strongest adaptive attacker is still `gpt-4o-mini`, not an RL-trained optimizer or a frontier red-team model.
- The official NeurIPS/AIWILD style file is not vendored. The fallback style compiles and fits, but final upload should be checked with the official style if required.
- The extended version should expand related work and methodology rather than overclaiming the mitigation as universal.
