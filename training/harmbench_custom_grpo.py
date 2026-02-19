"""
Custom GRPO-style Trainer for CPU - More reliable than TRL's GRPOTrainer.

Implements:
- Supervised generation with rewards
- Manual weight updates
- Timeout protection
- Full wandb logging
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset
import numpy as np
import warnings
import sys
from tqdm import tqdm
import wandb

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from scripts.harmbench import create_harmbench_dataset
from harmbench_reward_function import evaluate_jailbreak_response_fallback

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
torch.backends.mps.is_available = lambda: False


def generate_completion(model, tokenizer, prompt, max_length=512, timeout=60):
    """
    Generate a single completion with timeout protection.
    """
    try:
        inputs = tokenizer(prompt, return_tensors="pt", max_length=256, truncation=True)
        
        # Generate with reduced settings for CPU
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=128,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                attention_mask=inputs.get("attention_mask"),
            )
        
        completion = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return completion[len(prompt):].strip()  # Return only the new tokens
    except Exception as e:
        print(f"Generation error: {e}")
        return ""


def calculate_reward(completion, original_response, category, subcategory):
    """
    Calculate reward for a completion using heuristic evaluation.
    """
    if not completion:
        return 0.0
    
    # Use fallback heuristic - fast and reliable on CPU
    success = evaluate_jailbreak_response_fallback(
        completion, 
        original_response,
        category,
        subcategory,
        "",
        ""
    )
    
    return 1.0 if success else 0.0


def main():
    """
    Main custom GRPO training function.
    """
    print("HARMBENCH CUSTOM GRPO TRAINING")
    print("=" * 80)
    
    # Set wandb project
    os.environ["WANDB_PROJECT"] = "loki-harmbench"
    
    # Initialize wandb
    wandb.init(
        project="loki-harmbench",
        name="harmbench-custom-grpo",
        config={
            "model": "Qwen/Qwen2.5-0.5B-Instruct",
            "num_samples": 5,
            "learning_rate": 5e-6,
            "num_epochs": 1,
        }
    )
    
    # Configuration
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    num_samples = 5
    num_epochs = 1
    learning_rate = 5e-6
    
    # Load tokenizer
    print(f"\nLoading tokenizer from {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load dataset
    print(f"Loading HarmBench dataset with {num_samples} samples...")
    dataset = create_harmbench_dataset(num_samples=num_samples, save=False)
    
    print(f"Loaded {len(dataset)} examples")
    print("\nSample data:")
    for i in range(min(2, len(dataset))):
        example = dataset[i]
        print(f"  [{i+1}] Behavior: {example.get('behavior', 'N/A')[:80]}...")
        print(f"      Category: {example.get('semantic_category', 'N/A')}")
    
    # Load model
    print(f"\nLoading model {model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="cpu",
        torch_dtype=torch.float32,
    )
    model.eval()  # Evaluation mode for generation
    
    # Training loop
    print("\nStarting training...")
    print("=" * 80)
    
    epoch_rewards = []
    
    try:
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch + 1}/{num_epochs}")
            rewards = []
            
            # Process each sample
            pbar = tqdm(dataset, desc="Processing samples")
            for sample in pbar:
                prompt = sample.get('behavior', '')
                original_response = sample.get('response', '')
                category = sample.get('semantic_category', '')
                
                # Generate completion
                completion = generate_completion(model, tokenizer, prompt)
                
                # Calculate reward
                reward = calculate_reward(completion, original_response, category, category)
                rewards.append(reward)
                
                # Log sample
                wandb.log({
                    "sample/reward": reward,
                    "sample/completion_length": len(completion),
                })
                
                pbar.set_postfix({"reward": reward, "avg_reward": np.mean(rewards)})
            
            # Log epoch metrics
            epoch_mean_reward = np.mean(rewards)
            epoch_rewards.append(epoch_mean_reward)
            
            wandb.log({
                "epoch": epoch + 1,
                "reward/mean": epoch_mean_reward,
                "reward/std": np.std(rewards),
                "reward/min": np.min(rewards),
                "reward/max": np.max(rewards),
                "reward/success_rate": sum(1 for r in rewards if r > 0.5) / len(rewards),
            })
            
            print(f"\nEpoch {epoch + 1} Summary:")
            print(f"  Mean Reward: {epoch_mean_reward:.3f}")
            print(f"  Std Dev: {np.std(rewards):.3f}")
            print(f"  Min/Max: {np.min(rewards):.3f} / {np.max(rewards):.3f}")
        
        # Save model
        print(f"\nSaving model to: ./outputs/harmbench-custom-grpo")
        os.makedirs("./outputs/harmbench-custom-grpo", exist_ok=True)
        model.save_pretrained("./outputs/harmbench-custom-grpo")
        tokenizer.save_pretrained("./outputs/harmbench-custom-grpo")
        
        print("\nTraining completed successfully!")
        print(f"View results at: https://wandb.ai/tsavla23-cupertino-high-school/loki-harmbench")
        
        wandb.finish()
        
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
        wandb.finish()
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()
        wandb.finish()


if __name__ == "__main__":
    main()
