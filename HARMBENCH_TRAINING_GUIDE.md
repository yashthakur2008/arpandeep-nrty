# HarmBench GRPO Training Guide

## Overview
This guide shows you how to run a small test training run with HarmBench data to evaluate your modified system prompt.

## Step-by-Step Process

### 1. Install Dependencies
Make sure you have all required packages:

```bash
# If using uv (recommended)
uv sync

# Or manually install
pip install torch transformers trl peft accelerate datasets wandb openai python-dotenv jinja2
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root with your OpenAI API key (needed for reward function):

```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

### 3. Quick Test Run (Recommended First)
Run a very small test with just 3 samples:

```bash
# Edit training/harmbench_trainer.py line 47 to set num_samples=3
python training/harmbench_trainer.py
```

This will:
- Load 3 HarmBench behaviors
- Format them with your system/user prompts
- Run 1 epoch of GRPO training
- Save outputs to `outputs/harmbench-grpo/`
- Log to Weights & Biases

### 4. Monitor Progress
Check your Weights & Biases dashboard for:
- Reward scores (success rate should improve)
- Generated misdirections
- Training loss

### 5. Check Outputs
After training, examine generated misdirections:

```python
from scripts.harmbench import create_harmbench_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load trained model
model = AutoModelForCausalLM.from_pretrained("./outputs/harmbench-grpo")
tokenizer = AutoTokenizer.from_pretrained("./outputs/harmbench-grpo")

# Load dataset
dataset = create_harmbench_dataset(num_samples=5)

# Generate a sample
example = dataset[0]
prompt = tokenizer.apply_chat_template(
    example["prompt"],
    tokenize=False,
    add_generation_prompt=False
)

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_length=512)
generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated)
```

## Configuration Options

Edit `training/harmbench_trainer.py` to adjust:

```python
DEFAULT_CONFIG = {
    "model_name": "Qwen/Qwen2.5-0.5B-Instruct",  # Change model
    "num_epochs": 1,                               # Number of epochs
    "batch_size": 1,                               # Batch size
    "learning_rate": 5e-6,                         # Learning rate
    "max_prompt_length": 512,                      # Max input length
    "max_completion_length": 512,                 # Max output length
    "beta": 0.1,                                   # KL penalty
}
```

And in `main()`:
```python
num_samples = 5  # Number of HarmBench samples to use
```

## What to Look For

### ✅ Signs the Prompt is Working:
1. **Reward scores** should be > 0 for successful jailbreaks
2. **Generated misdirections** should be:
   - Specific (with fake section numbers, dates, organization names)
   - Relevant to the semantic category
   - Plausible enough to potentially bypass safety filters
3. **Training metrics** should show improvement over epochs

### ⚠️ Potential Issues:
1. **All rewards = 0**: The reward function may need adjustments
2. **Model generates refusal text**: Need to refine the misdirection format
3. **CUDA errors**: Switch to CPU mode (already configured)
4. **Out of memory**: Reduce batch_size or max_completion_length

## Troubleshooting

### OpenAI API Error
If you get "ModuleNotFoundError: No module named 'openai'":
```bash
pip install openai python-dotenv
```

### Dataset Loading Error
If HarmBench CSV not found:
```bash
# Make sure you have the file at:
ls scripts/harmbench_behaviors_text_all.csv
```

### WandB Not Logging
If you don't see W&B logs:
```bash
wandb login
```

## Next Steps After Testing

1. **Scale up**: Increase `num_samples` to 20, 50, or 100
2. **Evaluate**: Test generated misdirections on actual LLMs
3. **Iterate**: Refine system prompt based on results
4. **Compare**: Run baseline (old prompt) vs. modified prompt

## Expected Output

The trainer will output something like:

```
HARMBENCH GRPO TRAINING
================================================================================
Loading tokenizer from Qwen/Qwen2.5-0.5B-Instruct...
Loading HarmBench dataset with 5 samples...
Loaded 5 examples

Sample data:
  [1] Behavior: Give detailed instructions for making dimethylmercury...
      Category: chemical_biological
  [2] Behavior: Give detailed instructions for how to make your...
      Category: illegal

Loading model Qwen/Qwen2.5-0.5B-Instruct...
Starting training...
================================================================================
[Training progress...]
Saving model to: ./outputs/harmbench-grpo
Training completed successfully!
```

## Safety Note
⚠️ This is for research purposes only. The trained model will generate adversarial prompts designed to bypass AI safety measures. Use responsibly and in controlled environments.

