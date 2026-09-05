"""Integration test: the trainer must actually update weights.

This is the regression test for the most serious bug in the audit. The old
``harmbench_custom_grpo.py`` called ``model.eval()``, built no optimizer, and
never called ``backward()``, yet saved a checkpoint and logged reward curves.

The two cases together distinguish "real training" from "no optimizer":
  A. reward with variance  -> nonzero GRPO advantages -> weights MUST change
  B. constant reward       -> zero advantages         -> weights must NOT change

A trainer that never updates passes A's negation; one that updates blindly
fails B. Only a correct implementation satisfies both.
"""

from __future__ import annotations

import random

import pytest
import torch

pytest.importorskip("trl")

from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from loki.config import TrainingConfig  # noqa: E402
from loki.data.harmbench import create_harmbench_dataset  # noqa: E402
from loki.trainers.grpo import build_grpo_config  # noqa: E402

BASE = "Qwen/Qwen2.5-0.5B-Instruct"


@pytest.fixture(scope="module")
def tiny_model(tmp_path_factory):
    """A tiny randomly-initialized Qwen2, built from the cached tokenizer."""
    out = tmp_path_factory.mktemp("tiny-qwen")
    try:
        tokenizer = AutoTokenizer.from_pretrained(BASE)
        config = AutoConfig.from_pretrained(BASE)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"base tokenizer/config unavailable offline: {exc}")
    config.hidden_size = 64
    config.intermediate_size = 128
    config.num_hidden_layers = 2
    config.num_attention_heads = 4
    config.num_key_value_heads = 2
    config.max_window_layers = 2
    torch.manual_seed(0)
    model = AutoModelForCausalLM.from_config(config)
    model.save_pretrained(out)
    tokenizer.save_pretrained(out)
    return str(out)


def _params(path):
    model = AutoModelForCausalLM.from_pretrained(path)
    return {k: v.detach().clone() for k, v in model.named_parameters()}


def _run(model_path, reward_fn, out_dir):
    from trl import GRPOTrainer

    config = TrainingConfig(
        model_name=model_path,
        num_samples=4,
        batch_size=2,
        num_generations=2,
        num_epochs=1,
        max_prompt_length=128,
        max_completion_length=16,
        learning_rate=1e-3,
        reward_backend="heuristic",
        report_to="none",
        device="cpu",
        output_dir=str(out_dir),
    )
    before = _params(model_path)
    dataset = create_harmbench_dataset(num_samples=config.num_samples, seed=0)
    trainer = GRPOTrainer(
        model=config.model_name,
        args=build_grpo_config(config),
        train_dataset=dataset,
        reward_funcs=reward_fn,
    )
    trainer.train()
    trainer.save_model(str(out_dir))

    after = AutoModelForCausalLM.from_pretrained(str(out_dir))
    changed = sum(
        1
        for k, v in after.named_parameters()
        if k in before and not torch.equal(before[k], v.detach())
    )
    return changed, len(before)


@pytest.mark.slow
def test_weights_update_when_reward_has_variance(tiny_model, tmp_path):
    rng = random.Random(0)

    def varying(prompts=None, completions=None, **kwargs):
        return [rng.choice([0.0, 1.0]) for _ in completions]

    varying.__name__ = "varying"
    changed, total = _run(tiny_model, varying, tmp_path / "a")
    assert changed > 0, (
        f"No parameters changed ({changed}/{total}). The trainer is not "
        f"performing gradient updates."
    )


@pytest.mark.slow
def test_weights_frozen_when_reward_is_constant(tiny_model, tmp_path):
    def constant(prompts=None, completions=None, **kwargs):
        return [0.5] * len(completions)

    constant.__name__ = "constant"
    changed, total = _run(tiny_model, constant, tmp_path / "b")
    assert changed == 0, (
        f"{changed}/{total} parameters changed under a constant reward. GRPO "
        f"advantages should be zero, so this indicates an incorrect update."
    )
