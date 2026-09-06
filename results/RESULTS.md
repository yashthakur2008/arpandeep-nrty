# Measured results

Attacker: Qwen2.5-0.5B-Instruct. Target: llama3.2 (Ollama, local, free).
Judge: **gpt-4o-mini**, validated at 90% accuracy against manual labels.
Held-out test split (no train/test overlap), n=120, seed 0.

## Headline: GRPO teaches the output format, not the attack

| Metric | Base | GRPO-trained | Significance |
|---|---|---|---|
| Format rate (parseable) | 71% | **91%** | large |
| Tag compliance (`<misdirection>`) | 0% | **46%** | **p = 5.6e-17** |
| End-to-end ASR (all 120) | 12.5% | 11.7% | **p = 1.00, no effect** |
| Conditional ASR (parseable only) | 17.6% | 12.8% | no improvement |

**The attack does not improve.** GRPO reliably teaches the model to emit the
requested `<misdirection>` tags (0% → 46%, overwhelmingly significant), but the
misdirections it learns to produce are no better at jailbreaking the target than
the base model's. The reward's format and quality terms are learnable; the attack
term is not being optimized at this scale.

## This contradicts our own earlier numbers, which were wrong

An earlier run reported ASR improving 25% → 48% (n=25, llama3.2 judge). That was
an artifact. llama3.2 as a judge is **36% accurate** and scored 27 explicit
refusals such as `"I can't fulfill that request."` as successful jailbreaks.
See `JUDGE_VALIDATION.md`. All llama3.2-judged numbers are void.

The lesson generalizes: with a bad judge this project would have reported a
23-point improvement that does not exist.

## Caveats

- Single seed, single target model, single attacker scale (0.5B).
- 20 training steps on 40 behaviors is a small run; a negative result at this
  scale does not prove the method cannot work at larger scale.
- The judge measures *compliance*, not *harm*. A complied-with request for song
  lyrics counts as a success here.

## Reproduce

```bash
loki-train --reward-backend ollama --num-samples 40 --split train
loki-eval --model outputs/harmbench-grpo-v1 --num-samples 120 \
    --reward-backend ollama --judge-backend openai --split test
python -m loki.judge_study --input outputs/trained_n120_gpt.json \
    --judges heuristic ollama openai
```

## Files

- `base_n120_gpt.json`, `trained_n120_gpt.json` — the headline comparison
- `judge_study_trained.json` — three-judge disagreement study
- `JUDGE_VALIDATION.md` — judge accuracy analysis
