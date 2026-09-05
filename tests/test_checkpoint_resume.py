"""Tests for checkpoint/resume.

This is the gate on using spot/interruptible instances. Spot is only safe if an
interrupted run resumes from the latest checkpoint with optimizer and scheduler
state intact, rather than silently restarting from step 0.
"""

from __future__ import annotations

import os

import pytest
import torch

pytest.importorskip("trl")

from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from loki.config import TrainingConfig  # noqa: E402
from loki.data.harmbench import create_harmbench_dataset  # noqa: E402
from loki.trainers.grpo import build_grpo_config, resolve_resume_checkpoint  # noqa: E402

BASE = "Qwen/Qwen2.5-0.5B-Instruct"


@pytest.fixture(scope="module")
def tiny_model(tmp_path_factory):
    out = tmp_path_factory.mktemp("tiny-qwen-ckpt")
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
    AutoModelForCausalLM.from_config(config).save_pretrained(out)
    tokenizer.save_pretrained(out)
    return str(out)


class TestResolveResumeCheckpoint:
    def test_none_starts_fresh(self, tmp_path):
        cfg = TrainingConfig(resume_from_checkpoint="none", output_dir=str(tmp_path))
        assert resolve_resume_checkpoint(cfg) is None

    def test_auto_with_no_output_dir_starts_fresh(self, tmp_path):
        cfg = TrainingConfig(
            resume_from_checkpoint="auto", output_dir=str(tmp_path / "missing")
        )
        assert resolve_resume_checkpoint(cfg) is None

    def test_auto_finds_latest_checkpoint(self, tmp_path):
        for step in (10, 30, 20):
            (tmp_path / f"checkpoint-{step}").mkdir()
        cfg = TrainingConfig(resume_from_checkpoint="auto", output_dir=str(tmp_path))
        assert resolve_resume_checkpoint(cfg).endswith("checkpoint-30")

    def test_explicit_path_is_used(self, tmp_path):
        ckpt = tmp_path / "checkpoint-5"
        ckpt.mkdir()
        cfg = TrainingConfig(resume_from_checkpoint=str(ckpt), output_dir=str(tmp_path))
        assert resolve_resume_checkpoint(cfg) == str(ckpt)

    def test_missing_explicit_path_raises(self, tmp_path):
        cfg = TrainingConfig(
            resume_from_checkpoint="/nonexistent/ckpt", output_dir=str(tmp_path)
        )
        with pytest.raises(FileNotFoundError):
            resolve_resume_checkpoint(cfg)


def _make_config(model_path, out_dir, epochs, save_steps=1):
    return TrainingConfig(
        model_name=model_path,
        num_samples=4,
        batch_size=2,
        num_generations=2,
        num_epochs=epochs,
        max_prompt_length=128,
        max_completion_length=16,
        learning_rate=1e-3,
        reward_backend="heuristic",
        report_to="none",
        device="cpu",
        output_dir=str(out_dir),
        save_steps=save_steps,
    )


def _reward(prompts=None, completions=None, **kwargs):
    # Deterministic alternating reward: has variance, so gradients are nonzero.
    return [float(i % 2) for i in range(len(completions))]


_reward.__name__ = "alternating"


@pytest.mark.slow
def test_checkpoints_are_written_during_training(tiny_model, tmp_path):
    from trl import GRPOTrainer

    config = _make_config(tiny_model, tmp_path / "run", epochs=1)
    dataset = create_harmbench_dataset(num_samples=config.num_samples, seed=0)
    trainer = GRPOTrainer(
        model=config.model_name,
        args=build_grpo_config(config),
        train_dataset=dataset,
        reward_funcs=_reward,
    )
    trainer.train()

    checkpoints = [d for d in os.listdir(config.output_dir) if d.startswith("checkpoint-")]
    assert checkpoints, "no intermediate checkpoints written; a spot reclaim would lose the run"


@pytest.mark.slow
def test_resume_continues_instead_of_restarting(tiny_model, tmp_path):
    """Interrupt after 1 epoch, then resume: must continue, not restart at 0."""
    from trl import GRPOTrainer

    out = tmp_path / "resumable"

    # Phase 1: train one epoch and stop.
    first_cfg = _make_config(tiny_model, out, epochs=1)
    dataset = create_harmbench_dataset(num_samples=first_cfg.num_samples, seed=0)
    first = GRPOTrainer(
        model=first_cfg.model_name,
        args=build_grpo_config(first_cfg),
        train_dataset=dataset,
        reward_funcs=_reward,
    )
    first.train()
    steps_after_first = first.state.global_step
    assert steps_after_first > 0

    # Phase 2: same output_dir, more epochs. resume="auto" must pick up the
    # checkpoint and start from steps_after_first rather than from zero.
    second_cfg = _make_config(tiny_model, out, epochs=2)
    resume = resolve_resume_checkpoint(second_cfg)
    assert resume is not None, "auto-resume found no checkpoint to resume from"

    second = GRPOTrainer(
        model=second_cfg.model_name,
        args=build_grpo_config(second_cfg),
        train_dataset=dataset,
        reward_funcs=_reward,
    )
    second.train(resume_from_checkpoint=resume)

    assert second.state.global_step > steps_after_first, (
        f"resumed run ended at step {second.state.global_step}, which is not "
        f"beyond the {steps_after_first} steps already completed"
    )


@pytest.mark.slow
def test_resume_restores_optimizer_state(tiny_model, tmp_path):
    """A checkpoint must carry optimizer state, not just weights."""
    from trl import GRPOTrainer

    out = tmp_path / "optstate"
    config = _make_config(tiny_model, out, epochs=1)
    dataset = create_harmbench_dataset(num_samples=config.num_samples, seed=0)
    trainer = GRPOTrainer(
        model=config.model_name,
        args=build_grpo_config(config),
        train_dataset=dataset,
        reward_funcs=_reward,
    )
    trainer.train()

    latest = resolve_resume_checkpoint(config)
    assert latest is not None
    files = set(os.listdir(latest))
    assert "optimizer.pt" in files, (
        f"checkpoint {latest} has no optimizer.pt; resuming would reset Adam "
        f"moments and corrupt the optimization trajectory. Found: {sorted(files)}"
    )
    assert "trainer_state.json" in files, "checkpoint has no trainer_state.json"
