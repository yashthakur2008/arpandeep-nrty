# Format review against example AIWILD papers

The saved package examples are published ICLR 2026 Agents in the Wild workshop papers. Observed format:

- One-column ML workshop layout.
- Header line: `Published at ICLR 2026 Workshop on Agents in the Wild`.
- Large centered title, often all-caps in the PDF rendering.
- Author block under title.
- `ABSTRACT` heading followed by a compact abstract.
- Numbered sections starting with `1 INTRODUCTION`.
- References after main text.

Applied to our drafts:

- `paper/main.tex` and `paper/extended.tex` now use a one-column workshop-style fallback.
- Header is set to `Submitted to NeurIPS 2026 Workshop on Agents in the Wild`, not `Published`, because this is a submission.
- Both drafts remain anonymous by default for AIWILD double-blind review.
- Camera-ready author context is preserved behind `\camerareadytrue`: Yash Thakur, Aayushya Patel, Pranav Burra.
- Short paper remains 4 pages. Extended regular draft remains under the 9-page regular-paper budget.

Remaining external check: if OpenReview supplies or requires a specific template, rebuild with that official style before upload.
