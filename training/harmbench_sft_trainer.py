"""
HarmBench SFT Trainer - Simpler supervised fine-tuning approach.

This script fine-tunes a model on HarmBench dataset using standard next-token prediction.
More stable than GRPO on CPU and completes in ~10-15 minutes.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import Dataset
import numpy as np
import warnings
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from scripts.harmbench import create_harmbench_dataset

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
torch.backends.mps.is_available = lambda: False


def prepare_dataset_for_sft(dataset, tokenizer, max_length=512):
    """
    Prepare dataset for SFT by tokenizing prompts + misdirection.
    """
    def format_example(example):
        # Combine prompt with misdirection for training
        prompt = example.get('behavior', '')
        misdirection = f"<misdirection>{example.get('semantic_category', '')} advisory prompt</misdirection>"
        text = f"{prompt} {misdirection}"
        return {"text": text}
    
    # Format examples
    formatted = dataset.map(format_example, remove_columns=dataset.column_names)
    
    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )
    
    tokenized = formatted.map(tokenize_function, batched=True, remove_columns=["text"])
    return tokenized


def main():
    """
    Main SFT training function.
    """
    print("HARMBENCH SFT TRAINING")
    print("=" * 80)
    
    # Set wandb project
    os.environ["WANDB_PROJECT"] = "loki-harmbench"
    
    # Configuration
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    num_samples = 5
    batch_size = 2
    num_epochs = 1
    learning_rate = 5e-5
    
    # Load tokenizer
    print(f"\nLoading tokenizer from {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load dataset
    print(f"\nLoading HarmBench dataset with {num_samples} samples...")
    dataset = create_harmbench_dataset(num_samples=num_samples, save=False)
    
    print(f"Loaded {len(dataset)} examples")
    print("\nSample data:")
    for i in range(min(2, len(dataset))):
        example = dataset[i]
        print(f"  [{i+1}] Behavior: {example.get('behavior', 'N/A')[:80]}...")
    
    # Prepare dataset
    print("\nPreparing dataset for SFT...")
    train_dataset = prepare_dataset_for_sft(dataset, tokenizer)
    
    # Load model
    print(f"\nLoading model {model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="cpu",
        torch_dtype=torch.float32,
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./outputs/harmbench-sft",
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        logging_steps=1,
        save_strategy="epoch",
        report_to="wandb",
        run_name="harmbench-sft-test",
        push_to_hub=False,
        log_level="info",
        gradient_accumulation_steps=1,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Not using masked LM
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
    )
    
    # Train
    print("\nStarting training...")
    print("=" * 80)
    
    try:
        trainer.train()
        
        print(f"\nSaving model to: {training_args.output_dir}")
        trainer.save_model()
        
        print("\nTraining completed successfully!")
        print(f"View results at: https://wandb.ai/tsavla23-cupertino-high-school/loki-harmbench")
        
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
