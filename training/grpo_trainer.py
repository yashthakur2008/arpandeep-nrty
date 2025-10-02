"""
General GRPO Trainer using TRL.

This script provides a flexible GRPO trainer that can work with
various datasets and reward functions for different tasks.
"""

import os
import json
from typing import Dict, Any, List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import GRPOTrainer, GRPOConfig
from datasets import Dataset
import numpy as np
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from reward_function import reward_function


# Default Configuration
DEFAULT_CONFIG = {
    "model_name": "Qwen/Qwen2-0.5B-Instruct",
    "num_epochs": 3,
    "batch_size": 2,
    "learning_rate": 5e-6,
    "max_prompt_length": 256,
    "max_completion_length": 128,
    "beta": 0.1,  # KL penalty coefficient
    "output_dir": "./outputs/grpo-training",
    "reward_type": "quality"
}


def load_dataset_from_jsonl(jsonl_path: str, num_samples: int = None, 
                           prompt_key: str = "prompt", 
                           completion_key: str = "completion") -> Dataset:
    """
    Load dataset from JSONL file with flexible key mapping.
    
    Args:
        jsonl_path: Path to JSONL file
        num_samples: Number of samples to load (None for all)
        prompt_key: Key for prompt field in JSON
        completion_key: Key for completion field in JSON
    
    Returns:
        HuggingFace Dataset
    """
    data = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            if not line.strip():
                continue
            if num_samples and line_num >= num_samples:
                break
                
            obj = json.loads(line)
            
            # Extract prompt and completion
            prompt = obj.get(prompt_key, "")
            completion = obj.get(completion_key, "")
            
            # Create dataset entry
            entry = {
                "prompt": prompt,
                "completion": completion
            }
            
            # Add any additional fields from the original data
            for key, value in obj.items():
                if key not in [prompt_key, completion_key]:
                    entry[key] = value
            
            data.append(entry)
    
    return Dataset.from_list(data)


def create_grpo_config(config: Dict[str, Any]) -> GRPOConfig:
    """
    Create GRPO configuration from config dictionary.
    """
    grpo_config = GRPOConfig(
        output_dir=config["output_dir"],
        num_train_epochs=1,
        per_device_train_batch_size=2,
        learning_rate=1e-6,
        num_generations=2,
        max_prompt_length=256,
        max_completion_length=128,
        logging_steps=1,
        beta=0.0,
    )
    
    return grpo_config


def main():
    """
    Main training function.
    """
    print("HOTPOTQA GRPO TRAINING")
    print("=" * 80)
    
    # Configuration
    model_name = "Qwen/Qwen2-0.5B-Instruct"
    data_path = "../data/hotpotqa.jsonl"
    num_samples = 2
    
    # Load data
    dataset = load_dataset_from_jsonl(data_path, num_samples=num_samples)
    print(f"\nDataset: {len(dataset)} examples")
    for i in range(min(2, len(dataset))):
        example = dataset[i]
        print(f"[{i+1}] Q: {example.get('original_question', 'N/A')}")
        print(f"    A: {example.get('answer', 'N/A')}")
    
    # Create GRPO config
    grpo_config = create_grpo_config(DEFAULT_CONFIG)
    
    print(f"\nLoading {model_name}...")
    
    # Create trainer (let GRPOTrainer load the model internally to avoid sampler issues)
    trainer = GRPOTrainer(
        model=model_name,
        args=grpo_config,
        train_dataset=dataset,
        reward_funcs=reward_function,
    )
    
    # Start training
    print("\nStarting training...")
    print("=" * 80)
    
    try:
        trainer.train()
        
        # Save the final model
        print(f"\nSaving model to: {grpo_config.output_dir}")
        trainer.save_model()
        print("Training complete")
        
    except Exception as e:
        print(f"\nTraining failed: {e}")
        raise


if __name__ == "__main__":
    main()
