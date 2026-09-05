"""GRPO trainer for HarmBench misdirection generation.

Replaces ``training/harmbench_trainer.py`` and ``harmbench_custom_grpo.py``.
The latter claimed to perform "manual weight updates" but set ``model.eval()``,
never built an optimizer, and never called ``backward()``; it saved the
untouched base model and logged reward curves that could not possibly move. Any
result produced by it should be treated as void.

This trainer delegates the optimization to TRL's ``GRPOTrainer``, which does
implement the algorithm, and fails loudly instead of exiting 0 on error.
"""

from __future__ import annotations

import logging
import os
import sys

from loki.config import TrainingConfig, config_from_cli
from loki.data.harmbench import create_harmbench_dataset
from loki.rewards.harmbench import HarmBenchReward
from loki.runtime import (
    PreflightError,
    configure_logging,
    log_metrics,
    preflight,
    set_seed,
    setup_tracking,
    teardown_tracking,
)

logger = logging.getLogger(__name__)


def build_grpo_config(config: TrainingConfig):
    from trl import GRPOConfig

    return GRPOConfig(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        num_generations=config.num_generations,
        max_prompt_length=config.max_prompt_length,
        max_completion_length=config.max_completion_length,
        beta=config.beta,
        logging_steps=1,
        log_completions=True,
        seed=config.seed,
        # Periodic checkpoints so an interrupted run resumes instead of
        # restarting. Prerequisite for spot/interruptible instances.
        save_strategy="steps",
        save_steps=config.save_steps,
        save_total_limit=config.save_total_limit,
        # Device comes from config rather than a hardcoded use_cpu=True, which
        # previously made the RunPod GPU path unable to use the GPU.
        use_cpu=config.use_cpu,
        bf16=config.device == "cuda",
        fp16=False,
        report_to=config.report_to,
        run_name=config.run_name,
    )


def resolve_resume_checkpoint(config: TrainingConfig) -> str | None:
    """Decide which checkpoint, if any, ``train()`` should resume from.

    Returns a path, or ``None`` to start fresh. ``"auto"`` looks for the latest
    checkpoint in ``output_dir``, which is what makes a reclaimed spot instance
    or a dropped SSH session recoverable.
    """
    setting = (config.resume_from_checkpoint or "auto").strip()

    if setting.lower() in {"none", "false", ""}:
        return None

    if setting.lower() != "auto":
        if not os.path.isdir(setting):
            raise FileNotFoundError(f"resume_from_checkpoint not found: {setting}")
        return setting

    from transformers.trainer_utils import get_last_checkpoint

    if not os.path.isdir(config.output_dir):
        return None
    return get_last_checkpoint(config.output_dir)


def train(config: TrainingConfig):
    from trl import GRPOTrainer

    set_seed(config.seed)
    preflight(config)

    logger.info("Loading HarmBench dataset (num_samples=%s)", config.num_samples)
    dataset = create_harmbench_dataset(num_samples=config.num_samples, seed=config.seed)
    logger.info("Loaded %d examples", len(dataset))

    run = setup_tracking(config)
    reward = HarmBenchReward.from_config(config, log_fn=log_metrics)

    logger.info(
        "Training %s on %s | batch=%d gens=%d lr=%g backend=%s",
        config.model_name,
        config.device,
        config.batch_size,
        config.num_generations,
        config.learning_rate,
        config.reward_backend,
    )

    trainer = GRPOTrainer(
        model=config.model_name,
        args=build_grpo_config(config),
        train_dataset=dataset,
        reward_funcs=reward,
    )

    resume = resolve_resume_checkpoint(config)
    if resume:
        logger.info("Resuming from checkpoint: %s", resume)

    try:
        result = trainer.train(resume_from_checkpoint=resume)
        os.makedirs(config.output_dir, exist_ok=True)
        trainer.save_model(config.output_dir)
        logger.info("Saved trained model to %s", config.output_dir)
        return result
    finally:
        teardown_tracking(run)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    try:
        config = config_from_cli(argv)
    except ValueError as exc:
        logger.error("Invalid configuration: %s", exc)
        return 2

    try:
        train(config)
    except PreflightError as exc:
        # Expected, actionable misconfiguration: report cleanly, exit nonzero.
        logger.error("%s", exc)
        return 2
    # Any other exception propagates: a crashed run must not exit 0 and look
    # like a success, which is what the old bare `except Exception` did.
    logger.info("Training completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
