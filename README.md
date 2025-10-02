# Loki: Adversarial Steering and Red-teaming for LLM Steerability Testing

Loki is a research project for training models using reinforcement learning to "trick" or mislead LLMs for red-teaming and steerability testing. The project uses Group Relative Policy Optimization (GRPO) to train models on various datasets including FEVER and HotpotQA.

## Overview

- **Project**: Loki - Adversarial steering and red-teaming toolkit
- **Method**: GRPO (Group Relative Policy Optimization) for language model training
- **Task**: Red-teaming, steerability testing, and adversarial model training
- **Datasets**: FEVER, HotpotQA, and other fact-checking datasets

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd loki

# Install dependencies with uv
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

## GRPO Training

Train a language model using GRPO on FEVER claims:

```bash
# Using uv to run the training script
uv run python code/grpo_trainer.py

# Or activate the environment and run directly
source .venv/bin/activate
python code/grpo_trainer.py
```

### Features

- **Reward Function**: Based on response quality, FEVER terminology, and classification accuracy
- **Base Model**: DialoGPT-medium (configurable)
- **Data Format**: Converts FEVER claims to prompt-completion pairs
- **Output**: Trained model saved to `outputs/fever-grpo/`

### Configuration

Edit `code/grpo_trainer.py` to adjust:
- Model name (`microsoft/DialoGPT-medium`)
- Training epochs (default: 2)
- Batch size (default: 2)
- Learning rate (default: 5e-5)

## Usage

After training, use the model for inference:

```bash
# Using uv to run inference
uv run python code/fever_infer.py --model outputs/fever-grpo

# Or activate the environment and run directly
source .venv/bin/activate
python code/fever_infer.py --model outputs/fever-grpo
```

### Examples

```bash
# Interactive mode
uv run python code/fever_infer.py --model outputs/fever-grpo

# Single claim
uv run python code/fever_infer.py --model outputs/fever-grpo --claim "Berlin is the capital of Germany."
```

## HotpotQA Dataset

This repository also includes experiments with the [HotpotQA dataset](https://hotpotqa.github.io/), specifically the **distractor train split**.

Due to GitHub’s 100MB file size limit, the full dataset is **not included** in this repository. 

See sample in `hotpotqa_sample.jsonl`

### Download Instructions
1. Run `hotpotqa_to_jsonl.py` file to load data set + jsonl
2. Access jsonl file in `hotpotqa_distractor_train.jsonl`

### Example Format
{
  "question": "What nationality is the wife of the man who won the 2016 Tour de France?",
  "answer": "Welsh",
  "supporting_facts": [["2016 Tour de France", "Winner"], ["Chris Froome", "Spouse"]]
}



## Team

- naemi
- tanish  
- yash
- example
