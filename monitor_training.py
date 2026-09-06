#!/usr/bin/env python3
"""
Training Monitor for RunPod GRPO Training

This script monitors your training progress on RunPod and provides
real-time updates on performance, costs, and resource usage.
"""

import logging
import os
import subprocess
import time
from datetime import datetime
from typing import Any

import GPUtil
import psutil

import wandb

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TrainingMonitor:
    def __init__(self, pod_id: str | None = None):
        """Initialize training monitor."""
        self.pod_id = pod_id or self.get_pod_id()
        self.start_time = datetime.now()
        self.initial_cost = 0.0
        self.runpod_api_key = os.getenv("RUNPOD_API_KEY")

        if not self.runpod_api_key:
            logger.warning("RUNPOD_API_KEY not set. Cost monitoring will be disabled.")

    def get_pod_id(self) -> str | None:
        """Get pod ID from saved file."""
        try:
            with open(".runpod_pod_id") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.warning("No pod ID found. Please provide pod ID manually.")
            return None

    def get_system_stats(self) -> dict[str, Any]:
        """Get current system statistics."""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        }

        # GPU stats if available
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # First GPU
                stats.update(
                    {
                        "gpu_name": gpu.name,
                        "gpu_memory_used_mb": gpu.memoryUsed,
                        "gpu_memory_total_mb": gpu.memoryTotal,
                        "gpu_memory_percent": gpu.memoryUtil * 100,
                        "gpu_temperature": gpu.temperature,
                        "gpu_load_percent": gpu.load * 100,
                    }
                )
        except Exception as e:
            logger.debug(f"Could not get GPU stats: {e}")

        return stats

    def get_runpod_cost(self) -> float:
        """Get current RunPod cost."""
        if not self.runpod_api_key or not self.pod_id:
            return 0.0

        try:
            # This is a simplified cost calculation
            # In practice, you'd call the RunPod API
            elapsed_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            # Assuming A100 40GB at ~$0.39/hour
            estimated_cost = elapsed_hours * 0.39
            return estimated_cost
        except Exception as e:
            logger.debug(f"Could not calculate cost: {e}")
            return 0.0

    def get_wandb_stats(self) -> dict[str, Any]:
        """Get WandB training statistics."""
        try:
            # Get the latest run
            api = wandb.Api()
            runs = api.runs("loki-runpod", per_page=1)

            if runs:
                run = runs[0]
                return {
                    "run_id": run.id,
                    "run_name": run.name,
                    "state": run.state,
                    "config": dict(run.config),
                    "summary": dict(run.summary),
                    "url": run.url,
                }
        except Exception as e:
            logger.debug(f"Could not get WandB stats: {e}")

        return {}

    def get_training_logs(self, lines: int = 20) -> str:
        """Get recent training logs."""
        try:
            # Check for common log files
            log_files = [
                "/workspace/outputs/harmbench-grpo/training.log",
                "/workspace/logs/training.log",
                "nohup.out",
            ]

            for log_file in log_files:
                if os.path.exists(log_file):
                    result = subprocess.run(
                        ["tail", "-n", str(lines), log_file], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        return result.stdout

            return "No training logs found"
        except Exception as e:
            logger.debug(f"Could not get training logs: {e}")
            return f"Error getting logs: {e}"

    def print_status_report(self):
        """Print a comprehensive status report."""
        print("\n" + "=" * 80)
        print(f"🚀 GRPO TRAINING MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # System stats
        stats = self.get_system_stats()
        print("💻 System Resources:")
        print(f"   CPU Usage: {stats['cpu_percent']:.1f}%")
        print(
            f"   Memory: {stats['memory_used_gb']:.1f}GB / "
            f"{stats['memory_total_gb']:.1f}GB "
            f"({stats['memory_percent']:.1f}%)"
        )

        if "gpu_name" in stats:
            print(f"   GPU: {stats['gpu_name']}")
            print(
                f"   GPU Memory: {stats['gpu_memory_used_mb']}MB / "
                f"{stats['gpu_memory_total_mb']}MB "
                f"({stats['gpu_memory_percent']:.1f}%)"
            )
            print(f"   GPU Load: {stats['gpu_load_percent']:.1f}%")
            print(f"   GPU Temperature: {stats['gpu_temperature']}°C")

        # Cost information
        cost = self.get_runpod_cost()
        elapsed = datetime.now() - self.start_time
        print("\n💰 Cost Information:")
        print(f"   Runtime: {elapsed}")
        print(f"   Estimated Cost: ${cost:.2f}")

        # WandB stats
        wandb_stats = self.get_wandb_stats()
        if wandb_stats:
            print("\n📊 Training Progress:")
            print(f"   Run: {wandb_stats.get('run_name', 'N/A')}")
            print(f"   State: {wandb_stats.get('state', 'N/A')}")
            print(f"   WandB URL: {wandb_stats.get('url', 'N/A')}")

            summary = wandb_stats.get("summary", {})
            if "reward/mean" in summary:
                print(f"   Mean Reward: {summary['reward/mean']:.3f}")
            if "reward/success_rate" in summary:
                print(f"   Success Rate: {summary['reward/success_rate']:.1%}")

        # Recent logs
        print("\n📝 Recent Training Logs:")
        logs = self.get_training_logs(10)
        if logs.strip():
            for line in logs.strip().split("\n")[-5:]:  # Last 5 lines
                print(f"   {line}")
        else:
            print("   No recent logs available")

        print("=" * 80)

    def monitor_loop(self, interval: int = 60):
        """Run monitoring loop."""
        logger.info("Starting training monitor...")
        logger.info(f"Monitoring pod: {self.pod_id}")
        logger.info(f"Update interval: {interval} seconds")

        try:
            while True:
                self.print_status_report()

                # Check if training is still running
                stats = self.get_system_stats()
                if stats["cpu_percent"] < 5 and stats["gpu_load_percent"] < 5:
                    logger.warning("Low system activity detected. Training may have finished.")

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor GRPO training on RunPod")
    parser.add_argument("--pod-id", help="RunPod instance ID")
    parser.add_argument("--interval", type=int, default=60, help="Update interval in seconds")
    parser.add_argument("--once", action="store_true", help="Print status once and exit")

    args = parser.parse_args()

    monitor = TrainingMonitor(pod_id=args.pod_id)

    if args.once:
        monitor.print_status_report()
    else:
        monitor.monitor_loop(interval=args.interval)


if __name__ == "__main__":
    main()
