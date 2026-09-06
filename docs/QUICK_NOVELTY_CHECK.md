# Quick Novelty Check

Date: 2026-09-05

## Bottom line
The paper is still defensible, but the title and claims must stay narrow.

## Closest overlaps found

1. **DarkCite / authority-citation jailbreaks**
   - Covers fabricated authority/citation as a text jailbreak pattern.
   - Difference: our dependent variable is a logged tool call under explicit operating-policy variants.

2. **Judge-reliability work, including “A Coin Flip for Safety” and “How Reliable Is Your Jailbreak Judge?”**
   - Covers LLM judge failure at larger scale.
   - Difference: our judge result is only motivation. The agentic result avoids judges entirely.

3. **Agent safety benchmarks such as GAP and AgentSeer**
   - Covers text/tool safety gaps and tool-call safety measurement.
   - Difference: our independent variable is deployer policy wording, especially exemption/provenance phrasing.

4. **AutoInject**
   - Covers automated prompt injection against tool-using agents with binary tool-call success.
   - Difference: our focus is fabricated authority and policy-provenance wording, not generic prompt-injection optimization.

5. **Context-Fractured Decomposition Attacks on Tool-Using LLM Agents: Exploiting Artifact Provenance Gaps (arXiv:2606.09084)**
   - Very close on provenance gaps and cross-context artifacts.
   - Difference: their focus is delayed artifact-mediated multi-step composition and provenance lineage tagging. Our short-paper claim is a direct single-turn/user-message policy-phrasing matrix. The new forced indirect pilot overlaps their artifact-provenance setting and should be framed as a limitation/follow-up, not as the short paper's core novelty.

## Updated claim boundary
Novel: **policy-provenance phrasing as an experimentally controlled deployer-side variable for fabricated-authority attacks, measured by tool logs.**

Not novel enough as main claim:
- judges are unreliable
- prompt injection can hijack tools
- provenance gaps exist in multi-step artifacts
- fabricated citations can jailbreak text models

## Important new pilot
A forced indirect-channel pilot was run after this check:
- clean lookup: 0/72 violations
- poisoned lookup: 51/72 violations
- `strict_hatch`: 15/36 violations
- `exemption`: 36/36 violations

This means the one-sentence clause is strong for direct user-message fabricated authority, but not a universal protection once a tool result itself is poisoned and the agent is forced to consult it. The paper should not say the clause simply “stops” fabricated authority without specifying the channel.
