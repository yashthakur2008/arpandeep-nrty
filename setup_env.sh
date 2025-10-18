#!/bin/bash
# Environment Setup Script for RunPod

echo "🔧 Setting up environment for RunPod GRPO training..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# RunPod Configuration
RUNPOD_API_KEY=your_runpod_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
WANDB_API_KEY=your_wandb_api_key_here

# Training Configuration
WANDB_PROJECT=loki-runpod
CUDA_VISIBLE_DEVICES=0
TOKENIZERS_PARALLELISM=false
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
EOF
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env file and add your actual API keys"
else
    echo "✅ .env file already exists"
fi

# Source the environment variables
if [ -f .env ]; then
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
fi

# Check if API keys are set
echo ""
echo "🔑 Checking API keys..."

if [ -z "$RUNPOD_API_KEY" ] || [ "$RUNPOD_API_KEY" = "your_runpod_api_key_here" ]; then
    echo "❌ RUNPOD_API_KEY not set or is placeholder"
    echo "   Get your API key from: https://runpod.io/dashboard/settings/api"
else
    echo "✅ RUNPOD_API_KEY is set"
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set or is placeholder"
    echo "   Get your API key from: https://platform.openai.com/api-keys"
else
    echo "✅ OPENAI_API_KEY is set"
fi

if [ -z "$WANDB_API_KEY" ] || [ "$WANDB_API_KEY" = "your_wandb_api_key_here" ]; then
    echo "⚠️  WANDB_API_KEY not set (optional but recommended)"
    echo "   Get your API key from: https://wandb.ai/settings"
else
    echo "✅ WANDB_API_KEY is set"
fi

echo ""
echo "🎯 Quick Start Commands:"
echo "========================"
echo "1. Set your API keys:"
echo "   export RUNPOD_API_KEY='your_actual_key'"
echo "   export OPENAI_API_KEY='your_actual_key'"
echo "   export WANDB_API_KEY='your_actual_key'"
echo ""
echo "2. Run the setup guide:"
echo "   ./get_started_runpod.sh"
echo ""
echo "3. Or deploy directly:"
echo "   ./deploy_runpod.sh"
echo ""
echo "4. Monitor training:"
echo "   python monitor_training.py"

