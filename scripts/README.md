# scripts/

Dataset conversion utilities for datasets not yet wired into the training
pipeline (`hotpotqa`, `mathqa`, `jailbreakbench`, `fever`, `ambigqa`).

The active HarmBench path lives in `loki/data/harmbench.py`.
`harmbench_behaviors_text_all.csv` is the HarmBench behavior source and is read
from here by `loki.data.harmbench`.
