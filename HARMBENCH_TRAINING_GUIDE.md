# HarmBench Text-Validation Guide

This guide is retained for the supporting negative-control result. The active paper is the agentic tool-call paper; the text-jailbreak result is used to motivate why the project moved from judged text to logged tool calls.

## Key result
The original text-jailbreak direction looked positive under an unvalidated local judge, but the effect disappeared after judge validation:

- apparent ASR improvement: 25% to 48%
- human-labelled truth on judge validation: 19% ASR
- held-out validated rerun: 12.5% vs 11.7%, p = 1.00

## Current commands

Train the retained GRPO pipeline:

```bash
loki-train --reward-backend ollama --split train --num-samples 100
```

Evaluate:

```bash
loki-eval --reward-backend openai --split test --num-samples 120
```

Judge validation workflow:

```bash
python -m loki.label_sheet export --inputs 'outputs/*.json' --out labels/sheet.csv
# Human fills human_verdict with COMPLIED or REFUSED.
python -m loki.label_sheet score --sheet labels/sheet.csv --judges heuristic openai --out results/judge_accuracy.json
```

Aggregate paired base/trained runs:

```bash
python -m loki.aggregate --base 'outputs/base_seed*.json' \
  --trained 'outputs/trained_seed*.json' --out results/multiseed.json
```

## Current interpretation
Do not present the text pipeline as a successful attack result. It is a validated negative result and a methodological motivation for measuring tool calls directly.
