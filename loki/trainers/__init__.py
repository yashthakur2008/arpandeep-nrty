"""Trainers. Imported lazily so ``python -m loki.trainers.grpo`` is clean."""

__all__ = ["train"]


def __getattr__(name: str):
    if name == "train":
        from loki.trainers.grpo import train

        return train
    raise AttributeError(name)
