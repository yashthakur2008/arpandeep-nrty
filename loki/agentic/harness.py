"""Agent harness: run a policy-constrained scenario against a tool-calling target.

The outcome is a logged tool call, not a judged string. Three providers are
supported so a result can be shown to generalise beyond one vendor's safety
tuning:

    openai     gpt-4o-mini and friends        (costs money, cheap)
    anthropic  claude-haiku-4-5 and friends   (costs money, cheap)
    ollama     llama3.2 local                 (free)

Each provider returns the same ``AgentOutcome``, so the analysis code never
branches on vendor. Normalising tool calls into one shape is the only part of
this file that is vendor-specific, and it is deliberately isolated in the three
``_call_*`` functions.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from loki.agentic.scenarios import SAFE_TOOL_NAME, Scenario

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutcome:
    """What the agent did. ``violated`` is the paper's dependent variable."""

    scenario_id: str
    policy_variant: str
    target: str
    attack_name: str
    violated: bool
    called_safe_tool: bool
    tool_calls: list[ToolCall]
    text: str
    errored: bool = False
    error: str = ""

    @property
    def acted(self) -> bool:
        return bool(self.tool_calls)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "policy_variant": self.policy_variant,
            "target": self.target,
            "attack_name": self.attack_name,
            "violated": self.violated,
            "called_safe_tool": self.called_safe_tool,
            "tool_calls": [{"name": c.name, "arguments": c.arguments} for c in self.tool_calls],
            "text": self.text[:2000],
            "errored": self.errored,
            "error": self.error,
        }


def _loads(raw: Any) -> dict[str, Any]:
    """Arguments arrive as a JSON string (OpenAI) or a dict (Anthropic/Ollama)."""
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


# --------------------------------------------------------------------------
# Provider adapters
# --------------------------------------------------------------------------


def _call_openai(model: str, system: str, user: str, tools: list[dict], temperature: float):
    import openai

    client = openai.OpenAI(timeout=60, max_retries=3)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        tools=tools,
        temperature=temperature,
    )
    message = response.choices[0].message
    calls = [
        ToolCall(c.function.name, _loads(c.function.arguments))
        for c in (message.tool_calls or [])
    ]
    return calls, (message.content or "")


def _anthropic_create(client, temperature: float, **kwargs):
    """Call ``messages.create`` across Anthropic SDK generations.

    Some SDK versions accept ``temperature=`` directly; others removed it from
    the typed signature, where it has to travel in ``extra_body``. Rather than
    pinning a version, try both and fall back to the server default.

    Without this every Anthropic trial 400s, the target silently drops out of
    the results table, and the paper quietly becomes single-vendor. The failure
    is logged rather than swallowed for the same reason.
    """
    try:
        return client.messages.create(temperature=temperature, **kwargs)
    except TypeError:
        pass
    try:
        return client.messages.create(extra_body={"temperature": temperature}, **kwargs)
    except TypeError:
        logger.warning("anthropic SDK accepts no temperature control; using default")
        return client.messages.create(**kwargs)


def _call_anthropic(model: str, system: str, user: str, tools: list[dict], temperature: float):
    import anthropic

    client = anthropic.Anthropic(timeout=60, max_retries=3)
    # Anthropic uses a flat tool schema rather than OpenAI's nested "function".
    converted = [
        {
            "name": t["function"]["name"],
            "description": t["function"]["description"],
            "input_schema": t["function"]["parameters"],
        }
        for t in tools
    ]
    response = _anthropic_create(
        client,
        model=model,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=converted,
        temperature=temperature,
    )
    calls, text = [], ""
    for block in response.content:
        if block.type == "tool_use":
            calls.append(ToolCall(block.name, dict(block.input or {})))
        elif block.type == "text":
            text += block.text
    return calls, text


def _call_ollama(model: str, system: str, user: str, tools: list[dict], temperature: float):
    import ollama

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        tools=tools,
        options={"temperature": temperature},
    )
    message = response["message"]
    calls = [
        ToolCall(c["function"].name if hasattr(c["function"], "name") else c["function"]["name"],
                 _loads(getattr(c["function"], "arguments", None)
                        if hasattr(c["function"], "arguments")
                        else c["function"].get("arguments")))
        for c in (message.get("tool_calls") or [])
    ]
    return calls, str(message.get("content") or "")


_PROVIDERS = {
    "openai": _call_openai,
    "anthropic": _call_anthropic,
    "ollama": _call_ollama,
}

# Friendly names -> (provider, model). Keeps result tables readable and stops
# a typo in a model id from silently becoming a different experiment.
TARGETS: dict[str, tuple[str, str]] = {
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "gpt-4.1-mini": ("openai", "gpt-4.1-mini"),
    "claude-haiku-4-5": ("anthropic", "claude-haiku-4-5-20251001"),
    "claude-sonnet-4-5": ("anthropic", "claude-sonnet-4-5-20250929"),
    "llama3.2": ("ollama", "llama3.2"),
}


def required_credential(target: str) -> str | None:
    provider, _ = TARGETS[target]
    return {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}.get(provider)


def available_targets(candidates: list[str]) -> list[str]:
    """Drop targets whose credentials are absent, loudly."""
    ok = []
    for name in candidates:
        cred = required_credential(name)
        if cred and not os.getenv(cred):
            logger.warning("skipping target %s: %s is not set", name, cred)
            continue
        ok.append(name)
    return ok


def run_scenario(
    scenario: Scenario,
    policy_variant: str,
    target: str,
    attack_text: str = "",
    attack_name: str = "none",
    temperature: float = 1.0,
) -> AgentOutcome:
    """Run one (scenario, policy, target, attack) trial."""
    if target not in TARGETS:
        raise ValueError(f"unknown target {target!r}; expected one of {sorted(TARGETS)}")
    provider, model = TARGETS[target]

    system = scenario.system_prompt(policy_variant)
    user = f"{scenario.task} {attack_text}".strip()
    tools = scenario.all_tools()

    try:
        calls, text = _PROVIDERS[provider](model, system, user, tools, temperature)
    except Exception as exc:  # noqa: BLE001 - recorded, never silently scored
        logger.warning("target %s failed: %s", target, exc)
        return AgentOutcome(
            scenario_id=scenario.scenario_id,
            policy_variant=policy_variant,
            target=target,
            attack_name=attack_name,
            violated=False,
            called_safe_tool=False,
            tool_calls=[],
            text="",
            errored=True,
            error=str(exc),
        )

    violated = any(scenario.is_violation(c.name, c.arguments) for c in calls)
    return AgentOutcome(
        scenario_id=scenario.scenario_id,
        policy_variant=policy_variant,
        target=target,
        attack_name=attack_name,
        violated=violated,
        called_safe_tool=any(c.name == SAFE_TOOL_NAME for c in calls),
        tool_calls=calls,
        text=text,
    )
