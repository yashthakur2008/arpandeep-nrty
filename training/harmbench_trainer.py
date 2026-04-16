"""
HarmBench GRPO Trainer using TRL.

This script trains a model to generate adversarial prompts for HarmBench behaviors.
"""

import os
from typing import Dict, Any
import torch
from trl import GRPOTrainer, GRPOConfig
import warnings
import sys
import subprocess
import time
import ollama

# Add scripts directory to path to import harmbench module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from scripts.harmbench import create_harmbench_dataset
from harmbench_reward_function import harmbench_reward_function

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Force CPU usage to avoid MPS issues
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
torch.backends.mps.is_available = lambda: False


# Default Configuration
DEFAULT_CONFIG = {
    "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
    "num_epochs": 1,
    "batch_size": 2,       # per_device_train_batch_size (must align with num_generations)
    "num_generations": 2,  # completions sampled per prompt
    "learning_rate": 5e-6,
    "max_prompt_length": 256,
    "max_completion_length": 128,  # keep short for CPU speed
    "beta": 0.0,           # 0 = no reference model, saves memory
    "output_dir": "./outputs/harmbench-grpo",
}


def create_grpo_config(config: Dict[str, Any]) -> GRPOConfig:
    return GRPOConfig(
        output_dir=config["output_dir"],
        num_train_epochs=config.get("num_epochs", 1),
        per_device_train_batch_size=config.get("batch_size", 2),
        learning_rate=config.get("learning_rate", 5e-6),
        num_generations=config.get("num_generations", 2),
        max_prompt_length=config.get("max_prompt_length", 256),
        max_completion_length=config.get("max_completion_length", 128),
        beta=config.get("beta", 0.0),
        logging_steps=1,
        log_completions=True,
        # CPU settings
        use_cpu=True,
        bf16=False,
        fp16=False,
        gradient_checkpointing=False,
        # Disable wandb for quick local test (set to "wandb" to enable)
        report_to="wandb",
        run_name=config.get("run_name", "harmbench-grpo-test"),
    )


def ensure_ollama_running():
    """Start Ollama server if it's not already running, and pull the model if needed."""
    try:
        ollama.list()
        print("Ollama is already running.")
    except Exception:
        print("Ollama not running — starting it...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Wait for it to come up
        for _ in range(20):
            time.sleep(1)
            try:
                ollama.list()
                print("Ollama started successfully.")
                break
            except Exception:
                pass
        else:
            raise RuntimeError("Ollama failed to start after 20 seconds.")

    # Ensure the reward model is pulled
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2")
    available = [m.model for m in ollama.list().models]
    if not any(model_name in m for m in available):
        print(f"Model '{model_name}' not found locally — pulling it (this may take a few minutes)...")
        ollama.pull(model_name)
        print(f"Model '{model_name}' pulled successfully.")
    else:
        print(f"Model '{model_name}' is available.")


def main():
    print("HARMBENCH GRPO TRAINING")
    print("=" * 80)

    ensure_ollama_running()

    config = DEFAULT_CONFIG
    model_name = config["model_name"]
    num_samples = 5

    # Load dataset
    print(f"\nLoading HarmBench dataset ({num_samples} samples)...")
    dataset = create_harmbench_dataset(num_samples=num_samples, save=False)
    print(f"Loaded {len(dataset)} examples")

    for i in range(min(2, len(dataset))):
        ex = dataset[i]
        print(f"  [{i+1}] {ex.get('behavior', 'N/A')[:80]}...")

    # Create config and trainer
    grpo_config = create_grpo_config(config)

    print(f"\nLoading model {model_name}...")
    print(f"Config: batch={grpo_config.per_device_train_batch_size}, "
          f"gens={grpo_config.num_generations}, "
          f"max_completion={grpo_config.max_completion_length}, "
          f"beta={grpo_config.beta}")

    trainer = GRPOTrainer(
        model=model_name,
        args=grpo_config,
        train_dataset=dataset,
        reward_funcs=harmbench_reward_function,
    )

    print("\nStarting training...")
    print("=" * 80)

    try:
        trainer.train()
        print(f"\nSaving model to: {grpo_config.output_dir}")
        trainer.save_model()
        print("\nTraining completed successfully!")
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
