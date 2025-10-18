#!/bin/bash
# RunPod Deployment Script for GRPO Training

set -e  # Exit on any error

echo "🚀 RunPod GRPO Training Deployment"
echo "=================================="

# Check if required environment variables are set
if [ -z "$RUNPOD_API_KEY" ]; then
    echo "❌ Error: RUNPOD_API_KEY environment variable not set"
    echo "Please set your RunPod API key:"
    echo "export RUNPOD_API_KEY=your_api_key_here"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable not set"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

if [ -z "$WANDB_API_KEY" ]; then
    echo "⚠️  Warning: WANDB_API_KEY not set. WandB logging will be disabled."
fi

echo "✅ Environment variables checked"

# Install runpodctl if not present
if ! command -v runpodctl &> /dev/null; then
    echo "📦 Installing runpodctl..."
    curl -sSL https://runpod.io/install-runpodctl.sh | bash
    source ~/.bashrc
fi

echo "✅ runpodctl is available"

# Load configuration
CONFIG_FILE="runpod_config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: $CONFIG_FILE not found"
    exit 1
fi

echo "✅ Configuration file found"

# Extract configuration values
GPU_TYPE=$(grep "gpu_type:" $CONFIG_FILE | cut -d'"' -f2)
MEMORY_GB=$(grep "memory_gb:" $CONFIG_FILE | awk '{print $2}')
STORAGE_GB=$(grep "storage_gb:" $CONFIG_FILE | awk '{print $2}')
DOCKER_IMAGE=$(grep "docker_image:" $CONFIG_FILE | cut -d'"' -f2)

echo "🔧 Configuration:"
echo "   GPU Type: $GPU_TYPE"
echo "   Memory: ${MEMORY_GB}GB"
echo "   Storage: ${STORAGE_GB}GB"
echo "   Docker Image: $DOCKER_IMAGE"

# Create unique pod name
POD_NAME="grpo-training-$(date +%s)"

echo "🏗️  Creating RunPod instance: $POD_NAME"

# Create the pod
POD_ID=$(runpodctl create pod \
    --gpuType "$GPU_TYPE" \
    --imageName "$DOCKER_IMAGE" \
    --name "$POD_NAME" \
    --ports "8888:http,22:tcp,6006:tcp" \
    --containerDiskSize 50 \
    --volumeSize "$STORAGE_GB" \
    --mem "$MEMORY_GB" \
    --startSSH \
    --env "WANDB_PROJECT=loki-runpod" \
    --env "CUDA_VISIBLE_DEVICES=0" \
    --env "TOKENIZERS_PARALLELISM=false" \
    --env "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512" \
    --env "OPENAI_API_KEY=$OPENAI_API_KEY" \
    --env "WANDB_API_KEY=$WANDB_API_KEY" \
    --env "RUNPOD_API_KEY=$RUNPOD_API_KEY" \
    --output json | jq -r '.id')

if [ "$POD_ID" = "null" ] || [ -z "$POD_ID" ]; then
    echo "❌ Failed to create RunPod instance"
    exit 1
fi

echo "✅ RunPod instance created with ID: $POD_ID"

# Wait for pod to be ready
echo "⏳ Waiting for pod to be ready..."
sleep 30

# Get pod status
POD_STATUS=$(runpodctl get pod "$POD_ID" --output json | jq -r '.status')

echo "📊 Pod Status: $POD_STATUS"

# Get pod connection info
echo "🔗 Getting connection information..."
POD_INFO=$(runpodctl get pod "$POD_ID" --output json)

SSH_IP=$(echo "$POD_INFO" | jq -r '.runtime.ip')
SSH_PORT=$(echo "$POD_INFO" | jq -r '.runtime.port')
JUPYTER_URL=$(echo "$POD_INFO" | jq -r '.runtime.jupyterUrl')

echo ""
echo "🎉 RunPod instance is ready!"
echo "================================"
echo "Pod ID: $POD_ID"
echo "SSH: ssh root@$SSH_IP -p $SSH_PORT"
echo "Jupyter: $JUPYTER_URL"
echo ""

# Save pod information
echo "$POD_ID" > .runpod_pod_id
echo "$SSH_IP" > .runpod_ssh_ip
echo "$SSH_PORT" > .runpod_ssh_port

echo "📝 Pod information saved to .runpod_* files"

# Provide next steps
echo ""
echo "🚀 Next Steps:"
echo "==============="
echo "1. SSH into your pod:"
echo "   ssh root@$SSH_IP -p $SSH_PORT"
echo ""
echo "2. Clone your repository:"
echo "   cd /workspace"
echo "   git clone https://github.com/yourusername/arpandeep-nrty.git"
echo "   cd arpandeep-nrty"
echo ""
echo "3. Install dependencies:"
echo "   pip install -r requirements_runpod.txt"
echo ""
echo "4. Upload your data:"
echo "   # Copy your data files to /workspace/data/"
echo ""
echo "5. Start training:"
echo "   python training/grpo_trainer.py"
echo ""
echo "6. Monitor progress:"
echo "   - WandB: https://wandb.ai"
echo "   - Jupyter: $JUPYTER_URL"
echo "   - TensorBoard: http://$SSH_IP:6006"
echo ""

# Ask if user wants to upload files
read -p "🤔 Do you want to upload your project files now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading project files..."
    
    # Create a tarball of the project (excluding unnecessary files)
    tar --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='wandb' \
        --exclude='outputs' \
        --exclude='.runpod_*' \
        -czf project.tar.gz .
    
    # Upload to the pod
    scp -P "$SSH_PORT" project.tar.gz root@"$SSH_IP":/workspace/
    
    # Extract on the pod
    ssh -p "$SSH_PORT" root@"$SSH_IP" "cd /workspace && tar -xzf project.tar.gz && rm project.tar.gz"
    
    echo "✅ Project files uploaded successfully!"
    
    # Clean up local tarball
    rm project.tar.gz
fi

echo ""
echo "🎯 Training Commands:"
echo "===================="
echo "To start training, run these commands in your pod:"
echo ""
echo "cd /workspace/arpandeep-nrty"
echo "python training/grpo_trainer.py"
echo ""

# Ask about auto-cleanup
read -p "🧹 Do you want to set up auto-cleanup when training finishes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up auto-cleanup..."
    echo "echo 'Training completed. Pod will auto-shutdown in 10 minutes.'" > cleanup_script.sh
    echo "sleep 600" >> cleanup_script.sh
    echo "runpodctl stop pod $POD_ID" >> cleanup_script.sh
    chmod +x cleanup_script.sh
    echo "✅ Auto-cleanup script created: cleanup_script.sh"
fi

echo ""
echo "🎉 Deployment complete!"
echo "======================"
echo "Your RunPod instance is ready for GRPO training."
echo "Monitor your costs and stop the pod when done:"
echo "runpodctl stop pod $POD_ID"
echo ""

