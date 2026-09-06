#!/usr/bin/env python3
"""RunPod command helper for the current Loki package layout.

This script intentionally avoids hidden interactive steps and does not reference
the removed ``training/`` directory. It can either print the exact commands for a
RunPod pod or, with ``--create``, call ``runpodctl create pod``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

DEFAULT_COMMANDS = [
    "cd /workspace/arpandeep-nrty",
    "python -m pip install -U pip",
    'python -m pip install -e ".[openai,anthropic,ollama]"',
    "python -m pytest -q",
    (
        "python -m loki.agentic.sweep --targets gpt-4o-mini claude-haiku-4-5 "
        "--policies strict_hatch strict exemption autonomous bare --trials 3"
    ),
    (
        "python -m loki.agentic.gap --targets gpt-4o-mini claude-haiku-4-5 "
        "--policies strict autonomous exemption --attacks none combined superseded --trials 3"
    ),
    "loki-train --reward-backend ollama --split train --num-samples 100",
]


def load_config(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def create_command(config: dict[str, Any], name: str) -> list[str]:
    runpod = config["runpod"]
    env = {
        **runpod.get("env_vars", {}),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
        "WANDB_API_KEY": os.environ.get("WANDB_API_KEY", ""),
    }
    cmd = [
        "runpodctl",
        "create",
        "pod",
        "--gpuType",
        runpod["gpu_type"],
        "--imageName",
        runpod["docker_image"],
        "--name",
        name,
        "--ports",
        "8888:http,22:tcp,6006:tcp",
        "--containerDiskSize",
        str(runpod["container_disk_size"]),
        "--volumeSize",
        str(runpod["storage_gb"]),
        "--mem",
        str(runpod["memory_gb"]),
        "--startSSH",
    ]
    for key, value in env.items():
        if value:
            cmd += ["--env", f"{key}={value}"]
    return cmd + ["--output", "json"]


def print_next_steps() -> None:
    print("Commands to run on the pod after cloning the repo:\n")
    for command in DEFAULT_COMMANDS:
        print(command)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare RunPod commands for Loki")
    parser.add_argument("--config", default="runpod_config.yaml")
    parser.add_argument("--name", default=f"loki-runpod-{int(time.time())}")
    parser.add_argument("--create", action="store_true", help="actually create the pod")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    cmd = create_command(config, args.name)

    if not args.create:
        print("Dry run. Add --create to create a pod.\n")
        print(" ".join(cmd))
        print()
        print_next_steps()
        return 0

    if not os.environ.get("RUNPOD_API_KEY"):
        raise SystemExit("RUNPOD_API_KEY is required when --create is used")
    if shutil.which("runpodctl") is None:
        raise SystemExit("runpodctl is required when --create is used")

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(result.stdout)
    try:
        pod_id = json.loads(result.stdout).get("id")
    except json.JSONDecodeError:
        pod_id = None
    if pod_id:
        Path(".runpod_pod_id").write_text(pod_id, encoding="utf-8")
        print(f"Saved pod id to .runpod_pod_id: {pod_id}")
    print_next_steps()
    return 0


if __name__ == "__main__":
    sys.exit(main())
