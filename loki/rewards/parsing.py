"""Parsing helpers shared by every reward backend.

Previously ``extract_misdirection_from_response`` was copy-pasted verbatim into
three modules, so a fix to one silently left the others stale.
"""

from __future__ import annotations

import re
from typing import Any

_FENCE_OPEN = re.compile(r"^```[a-zA-Z0-9_-]*\n?")
_FENCE_CLOSE = re.compile(r"```$")
_OUTPUT_LABEL = re.compile(r"^\s*Output:\s*\n?", flags=re.IGNORECASE)
_MISDIRECTION = re.compile(r"<misdirection>([\s\S]*?)</misdirection>", re.IGNORECASE)
_REASONING = re.compile(r"<reasoning>([\s\S]*?)</reasoning>", re.IGNORECASE)

# Instruction-tuned models very often emit a Markdown/plain label instead of the
# XML tag the system prompt asks for ("Misdirection: ...", "**Misdirection**").
# Measured on Qwen2.5-0.5B-Instruct, tag-only parsing scored 0/20 well-formed,
# which zeroed the reward and left GRPO with no gradient signal at all. We accept
# the label form so the reward can distinguish content quality, while the strict
# tag form is still what the format component rewards.
_MISDIRECTION_LABEL = re.compile(
    r"(?:^|\n)\s*(?:[*_#]{0,2}\s*)misdirection(?:[*_#]{0,2})\s*[:\-]\s*([\s\S]*?)"
    r"(?=\n\s*(?:[*_#]{0,2}\s*)(?:reasoning|misdirection|output|note)\b|\Z)",
    re.IGNORECASE,
)
_REASONING_LABEL = re.compile(
    r"(?:^|\n)\s*(?:[*_#]{0,2}\s*)reasoning(?:[*_#]{0,2})\s*[:\-]\s*([\s\S]*?)"
    r"(?=\n\s*(?:[*_#]{0,2}\s*)(?:reasoning|misdirection|output|note)\b|\Z)",
    re.IGNORECASE,
)


def completion_to_text(completion: Any) -> str:
    """Normalize the several shapes TRL may hand back into plain text.

    TRL >= 0.23 yields ``[{"role": "assistant", "content": ...}]`` for
    conversational datasets, plain ``str`` otherwise.
    """
    if completion is None:
        return ""
    if isinstance(completion, str):
        return completion.strip()
    if isinstance(completion, list):
        if not completion:
            return ""
        last = completion[-1]
        if isinstance(last, dict):
            return str(last.get("content", "")).strip()
        return str(last).strip()
    if isinstance(completion, dict):
        for key in ("content", "text", "generated_text"):
            value = completion.get(key)
            if value:
                return str(value).strip()
        return ""
    return str(completion).strip()


def _strip_wrappers(text: str) -> str:
    cleaned = text.strip()
    cleaned = _FENCE_OPEN.sub("", cleaned).strip()
    cleaned = _FENCE_CLOSE.sub("", cleaned).strip()
    cleaned = _OUTPUT_LABEL.sub("", cleaned)
    return cleaned.strip()


def extract_misdirection(response: str, strict: bool = False) -> str:
    """Return the misdirection text, or ``""``.

    With ``strict=False`` (default) a plain ``Misdirection:`` label is accepted
    as a fallback, so that a model which has not yet learned the tag format
    still produces a gradient. ``strict=True`` requires the XML tag and is what
    ``is_well_formed`` uses to report the true format-compliance rate.
    """
    if not response:
        return ""
    cleaned = _strip_wrappers(str(response))
    match = _MISDIRECTION.search(cleaned)
    if match:
        return match.group(1).strip()
    if strict:
        return ""
    match = _MISDIRECTION_LABEL.search(cleaned)
    return match.group(1).strip() if match else ""


def is_well_formed(response: str) -> bool:
    """True only when the model used the requested ``<misdirection>`` tags."""
    return bool(extract_misdirection(response, strict=True))


def extract_reasoning(response: str, strict: bool = False) -> str:
    """Return the text inside ``<reasoning>`` tags, or ``""``."""
    if not response:
        return ""
    cleaned = _strip_wrappers(str(response))
    match = _REASONING.search(cleaned)
    if match:
        return match.group(1).strip()
    if strict:
        return ""
    match = _REASONING_LABEL.search(cleaned)
    return match.group(1).strip() if match else ""


def align_column(kwargs: dict[str, Any], key: str, index: int, default: str = "") -> str:
    """Fetch ``kwargs[key][index]`` safely.

    TRL passes dataset columns already flattened to one entry per completion, so
    indexing is direct. The old ``index // num_generations`` arithmetic assumed
    one entry per *prompt* and silently misaligned rewards with their prompts.
    """
    column = kwargs.get(key)
    if not column:
        return default
    if isinstance(column, (list, tuple)):
        return column[index] if index < len(column) else default
    return str(column)
