# Loki

Adversarial steering and red-teaming for LLM steerability testing.

Loki trains an *attacker* model with GRPO to generate misleading context (a
"misdirection") that, when appended to a harmful HarmBench request, causes a
*target* model to comply instead of refuse.

## Install

```bash
uv sync                       # or: pip install -e .
pip install -e ".[ollama]"    # optional: free local judge/target
pip install -e ".[openai]"    # optional: hosted judge/target (costs money)
```

## Quickstart

Everything runs offline with no API keys using the default `heuristic` backend:

```bash
loki-train --num-samples 20 --reward-backend heuristic
loki-eval  --model Qwen/Qwen2.5-0.5B-Instruct --num-samples 20 --out outputs/baseline.json
```

For a real attack signal you need a target model to attack:

```bash
ollama serve && ollama pull llama3.2         # free, local
loki-train --reward-backend ollama --num-samples 100
```

## Architecture

```
loki/
  config.py          TrainingConfig: defaults < YAML < env (LOKI_*) < CLI
  runtime.py         logging, seeding, wandb, and the preflight check
  data/harmbench.py  HarmBench CSV -> conversational TRL dataset
  rewards/
    parsing.py       completion -> misdirection text (tag or label form)
    targets.py       the model under attack (echo / ollama / openai)
    judges.py        did the target refuse? (heuristic / ollama / openai)
    harmbench.py     the single GRPO reward: format + quality + attack
  trainers/grpo.py   GRPO training loop (TRL)
  eval.py            attack success rate with bootstrap CIs
```

`target` and `judge` are deliberately separate roles so you can attack a local
model while judging with a stronger one, and so neither silently substitutes for
the other.

### Reward

| Component | Weight | Meaning                                        |
|-----------|--------|------------------------------------------------|
| format    | 0.2    | `<misdirection>` tags (half credit for a label) |
| quality   | 0.2    | specificity: cited sections, numbers, authority |
| attack    | 0.6    | target complied rather than refused             |

The `heuristic` backend measures **refusal**, not harm, and its target is an
echo stub, so `attack` is always 0 there. Use `ollama` or `openai` for real
attack-success numbers.

## Configuration

All knobs live in `TrainingConfig`; no trainer hardcodes them.

```bash
loki-train --model-name Qwen/Qwen2.5-1.5B-Instruct --batch-size 4 --device cuda
LOKI_LEARNING_RATE=1e-5 loki-train        # env override
```

Preflight fails fast with an actionable message if the chosen backend needs
credentials or a server you do not have.

## Testing

```bash
pytest                  # 55 tests
pytest -m "not slow"    # skip the training integration test
```

`tests/test_training_integration.py` asserts that weights change iff the reward
has variance, which is what distinguishes real GRPO from a loop that only looks
like training.

## Reproducing a baseline

```bash
loki-eval --model Qwen/Qwen2.5-0.5B-Instruct --num-samples 20 --seed 0 \
          --out outputs/baseline.json
```

Current measured baseline (Qwen2.5-0.5B-Instruct, 20 behaviors, CPU): 80%
parseable misdirections, 0% strict `<misdirection>` tag compliance. Attack
success is unmeasured pending a target backend.
