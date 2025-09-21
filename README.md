# FEVER Dataset Training with GRPO

This repository contains training scripts for the FEVER (Fact Extraction and VERification) dataset using Group Relative Policy Optimization (GRPO).

## Overview

- **Dataset**: FEVER claims from `train.jsonl`
- **Method**: GRPO (Group Relative Policy Optimization) for language model training
- **Task**: Fact-checking and claim verification
- **Labels**: SUPPORTS, REFUTES, NOT ENOUGH INFO

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## GRPO Training

Train a language model using GRPO on FEVER claims:

```bash
python Code/grpo_trainer.py
```

### Features

- **Reward Function**: Based on response quality, FEVER terminology, and classification accuracy
- **Base Model**: DialoGPT-medium (configurable)
- **Data Format**: Converts FEVER claims to prompt-completion pairs
- **Output**: Trained model saved to `outputs/fever-grpo/`

### Configuration

Edit `Code/grpo_trainer.py` to adjust:
- Model name (`microsoft/DialoGPT-medium`)
- Training epochs (default: 2)
- Batch size (default: 2)
- Learning rate (default: 5e-5)

## Usage

After training, use the model for inference:

```bash
python Code/fever_infer.py --model outputs/fever-grpo
```

### Examples

```bash
# Interactive mode
python Code/fever_infer.py --model outputs/fever-grpo

# Single claim
python Code/fever_infer.py --model outputs/fever-grpo --claim "Berlin is the capital of Germany."
```

## Team

- naemi
- tanish  
- yash
- example
