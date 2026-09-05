"""The target model under attack, i.e. the thing we try to jailbreak.

Kept separate from the judge so the two roles can use different backends (for
example, a free local target with a hosted judge) and so neither silently
substitutes for the other.
"""

from __future__ import annotations

import logging
import os
from typing import Protocol

logger = logging.getLogger(__name__)


class Target(Protocol):
    name: str

    def respond(self, prompt: str) -> str | None:
        """Return the target's reply, or ``None`` if the call failed.

        ``None`` is distinct from ``""``: it means "no measurement", so the
        caller can drop the sample instead of scoring it as a refusal.
        """


class EchoTarget:
    """Offline stand-in used by tests and by ``--reward-backend heuristic``.

    Deliberately trivial: it makes the absence of a real target obvious rather
    than fabricating plausible-looking responses.
    """

    name = "echo"

    def respond(self, prompt: str) -> str:
        return ""


class OllamaTarget:
    name = "ollama"

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")

    def respond(self, prompt: str) -> str | None:
        import ollama

        try:
            result = ollama.generate(
                model=self.model, prompt=prompt, options={"temperature": 0.7}
            )
        except Exception as exc:  # noqa: BLE001 - surfaced to caller as None
            logger.warning("Ollama target call failed: %s", exc)
            return None
        return str(result.get("response", "")).strip()


class OpenAITarget:
    name = "openai"

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import openai

            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY is required for the OpenAI target")
            self._client = openai.OpenAI(api_key=key, timeout=30, max_retries=3)
        return self._client

    def respond(self, prompt: str) -> str | None:
        try:
            completion = self._get_client().chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1,
            )
        except Exception as exc:  # noqa: BLE001 - surfaced to caller as None
            logger.warning("OpenAI target call failed: %s", exc)
            return None
        return (completion.choices[0].message.content or "").strip()


def build_target(backend: str, model: str | None = None) -> Target:
    if backend == "heuristic":
        return EchoTarget()
    if backend == "ollama":
        return OllamaTarget(model)
    if backend == "openai":
        return OpenAITarget(model or "gpt-4o-mini")
    raise ValueError(f"unknown reward backend: {backend!r}")
