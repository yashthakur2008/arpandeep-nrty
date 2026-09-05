"""Cross-cutting runtime concerns: logging, seeding, tracking, preflight.

The preflight check exists because the repository's reward path silently
depended on credentials and a local Ollama server that may not exist. Failing
in the first second with a clear message is much cheaper than failing after a
model download, or worse, not failing at all and training on all-zero rewards.
"""

from __future__ import annotations

import logging
import os
import random
import shutil
import sys

logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def set_seed(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


class PreflightError(RuntimeError):
    """Raised when the run cannot possibly succeed as configured."""


def check_reward_backend(backend: str, model: str | None = None) -> list[str]:
    """Return a list of blocking problems for the chosen reward backend."""
    problems: list[str] = []

    if backend == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            problems.append(
                "reward_backend='openai' but OPENAI_API_KEY is not set. "
                "Set it, or use --reward-backend heuristic (free, offline)."
            )
    elif backend == "ollama":
        if shutil.which("ollama") is None:
            problems.append(
                "reward_backend='ollama' but the ollama binary is not installed. "
                "Install from https://ollama.com, or use --reward-backend heuristic."
            )
        else:
            try:
                import ollama

                available = [m.model for m in ollama.list().models]
                wanted = model or os.getenv("OLLAMA_MODEL", "llama3.2")
                if not any(wanted in name for name in available):
                    problems.append(
                        f"Ollama model {wanted!r} is not pulled. Run: ollama pull {wanted}"
                    )
            except Exception as exc:  # noqa: BLE001
                problems.append(
                    f"Ollama server is not reachable ({exc}). "
                    f"Start it with: ollama serve"
                )
    return problems


def preflight(config) -> None:
    """Validate the environment before any expensive work begins."""
    problems = check_reward_backend(config.reward_backend, config.judge_model)

    if config.report_to == "wandb" and not (
        os.getenv("WANDB_API_KEY") or os.path.exists(os.path.expanduser("~/.netrc"))
    ):
        problems.append(
            "report_to='wandb' but no WANDB_API_KEY and no ~/.netrc. "
            "Run `wandb login`, or use --report-to none."
        )

    if problems:
        raise PreflightError(
            "Preflight failed:\n" + "\n".join(f"  - {p}" for p in problems)
        )

    logger.info(
        "Preflight OK | device=%s reward_backend=%s tracking=%s",
        config.device,
        config.reward_backend,
        config.report_to,
    )


def setup_tracking(config):
    """Initialize wandb if requested. Returns the run handle or ``None``."""
    if config.report_to != "wandb":
        return None
    import wandb

    os.environ["WANDB_PROJECT"] = config.wandb_project
    return wandb.init(
        project=config.wandb_project, name=config.run_name, config=config.to_dict()
    )


def log_metrics(payload: dict) -> None:
    """Log to wandb only when a run is active; otherwise debug-log."""
    try:
        import wandb

        if wandb.run is not None:
            wandb.log(payload)
            return
    except ImportError:
        pass
    logger.debug("metrics: %s", payload)


def teardown_tracking(run) -> None:
    if run is None:
        return
    try:
        import wandb

        wandb.finish()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to close wandb run: %s", exc)
