"""Single source of truth for run configuration.

Replaces the per-file ``DEFAULT_CONFIG`` dicts that previously disagreed with
each other and with ``runpod_config.yaml``. Precedence, lowest to highest:

    dataclass defaults  <  YAML file  <  environment variables  <  CLI flags
"""

from __future__ import annotations

import argparse
import dataclasses
import os
from dataclasses import dataclass, field
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = "runpod_config.yaml"


def _detect_device() -> str:
    """Pick the best available device instead of hardcoding CPU everywhere."""
    try:
        import torch
    except ImportError:  # pragma: no cover - torch is a hard dep in practice
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    # MPS is opt-in: the fp32 training path is unreliable on Metal for TRL.
    if os.getenv("LOKI_ALLOW_MPS") == "1" and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@dataclass
class TrainingConfig:
    """Everything a trainer needs. No trainer may hardcode these values."""

    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    num_epochs: int = 1
    batch_size: int = 2
    gradient_accumulation_steps: int = 1
    num_generations: int = 2
    learning_rate: float = 5e-6
    max_prompt_length: int = 256
    max_completion_length: int = 128
    beta: float = 0.0
    num_samples: int | None = 5
    output_dir: str = "./outputs/harmbench-grpo"
    seed: int = 0

    # Checkpointing. Required before spot/interruptible instances are safe:
    # without periodic saves a reclaim loses the entire run.
    save_steps: int = 10
    save_total_limit: int = 3
    # "auto" resumes from the latest checkpoint in output_dir if one exists,
    # "none" always starts fresh, or pass an explicit checkpoint path.
    resume_from_checkpoint: str = "auto"

    # Reward backend: "heuristic" (offline), "ollama", or "openai".
    reward_backend: str = "heuristic"
    judge_model: str = "llama3.2"

    # Infrastructure
    device: str = field(default_factory=_detect_device)
    report_to: str = "none"
    run_name: str = "harmbench-grpo"
    wandb_project: str = "loki-harmbench"

    @property
    def use_cpu(self) -> bool:
        return self.device == "cpu"

    def __post_init__(self) -> None:
        self._coerce_types()
        self.validate()

    def _coerce_types(self) -> None:
        """Coerce field values to their declared types.

        Necessary because YAML 1.1 parses ``5e-6`` as a *string* (it lacks the
        decimal point and sign that the spec's float pattern requires), so an
        unguarded ``learning_rate <= 0`` raised TypeError at startup.
        """
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)
            if value is None or isinstance(value, bool):
                continue
            annotation = str(f.type)
            try:
                if "int" in annotation and "None" not in annotation:
                    setattr(self, f.name, int(value))
                elif "int" in annotation and not isinstance(value, int):
                    setattr(self, f.name, int(value))
                elif "float" in annotation and not isinstance(value, float):
                    setattr(self, f.name, float(value))
                elif annotation.startswith("str") and not isinstance(value, str):
                    setattr(self, f.name, str(value))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"config field {f.name!r} has value {value!r}, "
                    f"which is not a valid {annotation}"
                ) from exc

    def validate(self) -> None:
        """Fail fast on configs that TRL would only reject deep into training."""
        if self.num_generations < 2:
            raise ValueError(
                f"num_generations must be >= 2 for GRPO advantages, got {self.num_generations}"
            )
        effective_batch = self.batch_size * self.gradient_accumulation_steps
        if effective_batch % self.num_generations != 0:
            raise ValueError(
                f"effective batch ({effective_batch}) must be divisible by "
                f"num_generations ({self.num_generations}); TRL requires this to "
                f"group completions per prompt"
            )
        if self.reward_backend not in {"heuristic", "ollama", "openai"}:
            raise ValueError(f"unknown reward_backend: {self.reward_backend!r}")
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be positive, got {self.learning_rate}")
        if self.num_samples is not None and self.num_samples < 1:
            raise ValueError(f"num_samples must be >= 1 or None, got {self.num_samples}")

    @classmethod
    def field_names(cls) -> set[str]:
        return {f.name for f in dataclasses.fields(cls)}

    @classmethod
    def from_yaml(cls, path: str = DEFAULT_CONFIG_PATH, **overrides: Any) -> TrainingConfig:
        """Load the ``training:`` block of the YAML config, if the file exists."""
        values: dict[str, Any] = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}
            known = cls.field_names()
            for key, value in (raw.get("training") or {}).items():
                if key in known:
                    values[key] = value
        values.update(cls._from_env())
        values.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**values)

    @staticmethod
    def _from_env() -> dict[str, Any]:
        """Read ``LOKI_*`` environment overrides, coercing to field types."""
        types = {f.name: f.type for f in dataclasses.fields(TrainingConfig)}
        out: dict[str, Any] = {}
        for name, annotation in types.items():
            raw = os.getenv(f"LOKI_{name.upper()}")
            if raw is None:
                continue
            text = str(annotation)
            if "int" in text and "None" not in text:
                out[name] = int(raw)
            elif "int" in text:
                out[name] = None if raw.lower() in {"none", ""} else int(raw)
            elif "float" in text:
                out[name] = float(raw)
            else:
                out[name] = raw
        return out

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["use_cpu"] = self.use_cpu
        return data


def add_cli_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Expose every config field as an optional CLI flag."""
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--model-name", dest="model_name")
    parser.add_argument("--num-epochs", dest="num_epochs", type=int)
    parser.add_argument("--batch-size", dest="batch_size", type=int)
    parser.add_argument("--num-generations", dest="num_generations", type=int)
    parser.add_argument("--learning-rate", dest="learning_rate", type=float)
    parser.add_argument("--num-samples", dest="num_samples", type=int)
    parser.add_argument("--max-prompt-length", dest="max_prompt_length", type=int)
    parser.add_argument("--max-completion-length", dest="max_completion_length", type=int)
    parser.add_argument(
        "--gradient-accumulation-steps", dest="gradient_accumulation_steps", type=int
    )
    parser.add_argument("--beta", type=float)
    parser.add_argument("--output-dir", dest="output_dir")
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"])
    parser.add_argument(
        "--reward-backend", dest="reward_backend", choices=["heuristic", "ollama", "openai"]
    )
    parser.add_argument("--judge-model", dest="judge_model")
    parser.add_argument("--report-to", dest="report_to", choices=["none", "wandb"])
    parser.add_argument("--run-name", dest="run_name")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--save-steps", dest="save_steps", type=int)
    parser.add_argument("--save-total-limit", dest="save_total_limit", type=int)
    parser.add_argument(
        "--resume-from-checkpoint",
        dest="resume_from_checkpoint",
        help="'auto' (default), 'none', or an explicit checkpoint path",
    )
    return parser


def config_from_cli(argv: list[str] | None = None) -> TrainingConfig:
    parser = add_cli_args(argparse.ArgumentParser(description="Loki training"))
    args = parser.parse_args(argv)
    overrides = {k: v for k, v in vars(args).items() if k != "config" and v is not None}
    return TrainingConfig.from_yaml(args.config, **overrides)
