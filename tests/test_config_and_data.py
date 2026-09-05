"""Tests for config precedence, validation, and dataset construction."""

from __future__ import annotations

import pytest

from loki.config import TrainingConfig
from loki.data.harmbench import create_harmbench_dataset, load_behaviors
from loki.runtime import PreflightError, check_reward_backend, preflight


class TestTrainingConfig:
    def test_validates_batch_divisible_by_num_generations(self):
        with pytest.raises(ValueError, match="divisible"):
            TrainingConfig(batch_size=3, num_generations=2)

    def test_rejects_num_generations_below_two(self):
        with pytest.raises(ValueError, match="num_generations"):
            TrainingConfig(num_generations=1)

    def test_rejects_unknown_backend(self):
        with pytest.raises(ValueError, match="reward_backend"):
            TrainingConfig(reward_backend="magic")

    def test_rejects_nonpositive_lr(self):
        with pytest.raises(ValueError, match="learning_rate"):
            TrainingConfig(learning_rate=0)

    def test_gradient_accumulation_counts_toward_effective_batch(self):
        cfg = TrainingConfig(batch_size=1, gradient_accumulation_steps=2, num_generations=2)
        assert cfg.batch_size * cfg.gradient_accumulation_steps == 2

    def test_use_cpu_follows_device(self):
        assert TrainingConfig(device="cpu").use_cpu is True
        assert TrainingConfig(device="cuda").use_cpu is False

    def test_yaml_is_actually_read(self, tmp_path):
        """runpod_config.yaml previously existed but nothing read it."""
        path = tmp_path / "cfg.yaml"
        path.write_text(
            "training:\n  model_name: test/model\n  batch_size: 4\n  num_generations: 2\n"
        )
        cfg = TrainingConfig.from_yaml(str(path))
        assert cfg.model_name == "test/model"
        assert cfg.batch_size == 4

    def test_yaml_ignores_unknown_keys(self, tmp_path):
        path = tmp_path / "cfg.yaml"
        path.write_text("training:\n  model_name: m\n  bogus_key: 1\n")
        assert TrainingConfig.from_yaml(str(path)).model_name == "m"

    def test_overrides_beat_yaml(self, tmp_path):
        path = tmp_path / "cfg.yaml"
        path.write_text("training:\n  model_name: from_yaml\n")
        cfg = TrainingConfig.from_yaml(str(path), model_name="from_cli")
        assert cfg.model_name == "from_cli"

    def test_env_override(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LOKI_BATCH_SIZE", "6")
        cfg = TrainingConfig.from_yaml(str(tmp_path / "missing.yaml"), num_generations=2)
        assert cfg.batch_size == 6

    def test_missing_yaml_falls_back_to_defaults(self, tmp_path):
        cfg = TrainingConfig.from_yaml(str(tmp_path / "nope.yaml"))
        assert cfg.model_name.startswith("Qwen/")


class TestPreflight:
    def test_openai_backend_without_key_is_blocked(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        problems = check_reward_backend("openai")
        assert problems and "OPENAI_API_KEY" in problems[0]

    def test_heuristic_backend_needs_nothing(self):
        assert check_reward_backend("heuristic") == []

    def test_preflight_raises_with_actionable_message(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        cfg = TrainingConfig(reward_backend="openai", report_to="none")
        with pytest.raises(PreflightError, match="heuristic"):
            preflight(cfg)

    def test_preflight_passes_for_offline_run(self):
        preflight(TrainingConfig(reward_backend="heuristic", report_to="none"))


class TestDataset:
    def test_loads_behaviors(self):
        rows = load_behaviors(num_samples=5)
        assert len(rows) == 5
        assert all(row["behavior"] for row in rows)

    def test_builds_conversational_prompt(self):
        dataset = create_harmbench_dataset(num_samples=3, seed=0)
        assert len(dataset) == 3
        prompt = dataset[0]["prompt"]
        assert [m["role"] for m in prompt] == ["system", "user"]
        assert dataset[0]["behavior"] in prompt[1]["content"]

    def test_seed_is_deterministic(self):
        a = create_harmbench_dataset(num_samples=5, seed=42)["behavior_id"]
        b = create_harmbench_dataset(num_samples=5, seed=42)["behavior_id"]
        assert a == b

    def test_different_seeds_differ(self):
        a = create_harmbench_dataset(num_samples=10, seed=1)["behavior_id"]
        b = create_harmbench_dataset(num_samples=10, seed=2)["behavior_id"]
        assert a != b

    def test_missing_csv_raises(self):
        with pytest.raises(FileNotFoundError):
            load_behaviors(csv_path="/nonexistent/file.csv")
