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


class TestTrainTestSplit:
    """Training and eval previously both sampled seed=0 from the same list, so
    reported metrics were computed on behaviors the model had trained on."""

    def test_split_is_disjoint(self):
        from loki.data.harmbench import split_behaviors

        train, test = split_behaviors(seed=0)
        train_ids = {r["behavior_id"] for r in train}
        test_ids = {r["behavior_id"] for r in test}
        assert train_ids & test_ids == set()
        assert len(train) + len(test) == len(train_ids | test_ids)

    def test_split_is_deterministic(self):
        from loki.data.harmbench import split_behaviors

        a, _ = split_behaviors(seed=0)
        b, _ = split_behaviors(seed=0)
        assert [r["behavior_id"] for r in a] == [r["behavior_id"] for r in b]

    def test_sampled_datasets_do_not_overlap(self):
        train = create_harmbench_dataset(num_samples=20, seed=0, split="train")
        test = create_harmbench_dataset(num_samples=20, seed=0, split="test")
        assert set(train["behavior_id"]) & set(test["behavior_id"]) == set()

    def test_test_fraction_respected(self):
        from loki.data.harmbench import split_behaviors

        train, test = split_behaviors(seed=0, test_fraction=0.25)
        total = len(train) + len(test)
        assert abs(len(test) / total - 0.25) < 0.02

    def test_invalid_split_rejected(self):
        with pytest.raises(ValueError, match="split"):
            create_harmbench_dataset(num_samples=2, split="bogus")

    def test_config_rejects_bad_split(self):
        with pytest.raises(ValueError, match="split"):
            TrainingConfig(split="bogus")


class TestAggregate:
    """Multi-seed pooling must not silently drop or mis-pair behaviors."""

    def _write(self, path, records, summary=None):
        import json

        path.write_text(
            json.dumps(
                {
                    "summary": summary
                    or {"format_rate": 0.8, "tag_compliance_rate": 0.5},
                    "records": records,
                }
            )
        )

    def test_pairs_by_behavior_id(self, tmp_path):
        from loki.aggregate import aggregate

        # Deliberately different record ORDER between base and trained.
        self._write(
            tmp_path / "base_seed0.json",
            [
                {"behavior_id": "a", "score": 0.0},
                {"behavior_id": "b", "score": 1.0},
            ],
        )
        self._write(
            tmp_path / "trained_seed0.json",
            [
                {"behavior_id": "b", "score": 1.0},
                {"behavior_id": "a", "score": 1.0},
            ],
        )
        out = aggregate(
            str(tmp_path / "base_seed*.json"), str(tmp_path / "trained_seed*.json")
        )
        # a: 0->1 is a win, b: 1->1 is a tie. Order must not matter.
        assert out["pooled"]["mcnemar_wins"] == 1
        assert out["pooled"]["mcnemar_losses"] == 0

    def test_missing_score_counts_as_failed_attack(self, tmp_path):
        """Unparseable output is a failed attack, not an excluded sample."""
        from loki.aggregate import aggregate

        self._write(tmp_path / "base_seed0.json", [{"behavior_id": "a"}])
        self._write(tmp_path / "trained_seed0.json", [{"behavior_id": "a"}])
        out = aggregate(
            str(tmp_path / "base_seed*.json"), str(tmp_path / "trained_seed*.json")
        )
        assert out["pooled"]["n"] == 1
        assert out["pooled"]["base_asr"] == 0.0

    def test_pools_across_seeds(self, tmp_path):
        from loki.aggregate import aggregate

        for seed in (0, 1):
            self._write(
                tmp_path / f"base_seed{seed}.json", [{"behavior_id": "a", "score": 0.0}]
            )
            self._write(
                tmp_path / f"trained_seed{seed}.json",
                [{"behavior_id": "a", "score": 1.0}],
            )
        out = aggregate(
            str(tmp_path / "base_seed*.json"), str(tmp_path / "trained_seed*.json")
        )
        assert out["seeds"] == ["0", "1"]
        assert out["pooled"]["n"] == 2

    def test_no_matching_seeds_raises(self, tmp_path):
        from loki.aggregate import aggregate

        with pytest.raises(ValueError, match="No matching seeds"):
            aggregate(str(tmp_path / "nope*.json"), str(tmp_path / "nada*.json"))

    def test_null_effect_reports_not_significant(self, tmp_path):
        from loki.aggregate import aggregate

        recs = [{"behavior_id": str(i), "score": float(i % 2)} for i in range(20)]
        self._write(tmp_path / "base_seed0.json", recs)
        self._write(tmp_path / "trained_seed0.json", recs)
        out = aggregate(
            str(tmp_path / "base_seed*.json"), str(tmp_path / "trained_seed*.json")
        )
        assert out["pooled"]["delta"] == 0.0
        assert out["pooled"]["significant_at_05"] is False
