#!/bin/bash
# Get Started with RunPod - Step by Step Guide

set -e

echo "🚀 Getting Started with RunPod for GRPO Training"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${BLUE}📋 Step $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check API Keys
print_step 1 "Check Environment Variables"

if [ -z "$RUNPOD_API_KEY" ]; then
    print_error "RUNPOD_API_KEY not set!"
    echo "Please set your RunPod API key:"
    echo "export RUNPOD_API_KEY='your_api_key_here'"
    echo ""
    echo "Get your API key from: https://runpod.io/dashboard/settings/api"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    print_error "OPENAI_API_KEY not set!"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your_openai_key_here'"
    echo ""
    echo "Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi

print_success "API keys are set"

# Step 2: Configure RunPod CLI
print_step 2 "Configure RunPod CLI"

if ! runpod config --check > /dev/null 2>&1; then
    echo "Setting up RunPod CLI with your API key..."
    runpod config "$RUNPOD_API_KEY"
    print_success "RunPod CLI configured"
else
    print_success "RunPod CLI already configured"
fi

# Step 3: Test RunPod Connection
print_step 3 "Test RunPod Connection"

echo "Testing connection to RunPod..."
if runpod pod list > /dev/null 2>&1; then
    print_success "Successfully connected to RunPod"
else
    print_error "Failed to connect to RunPod"
    echo "Please check your API key and internet connection"
    exit 1
fi

# Step 4: Check Available GPU Types
print_step 4 "Check Available GPU Types"

echo "Checking available GPU types..."
echo "Available GPU types:"
runpod pod list-gpu-types | head -20

# Step 5: Show Recommended Configuration
print_step 5 "Recommended Configuration"

echo "For GRPO training with Qwen2.5-0.5B, we recommend:"
echo ""
echo "🎯 GPU Type: NVIDIA RTX A100 40GB"
echo "💰 Cost: ~$0.29-0.39/hour"
echo "💾 Memory: 64GB RAM"
echo "💿 Storage: 100GB SSD"
echo ""

# Step 6: Ask if user wants to create a pod
print_step 6 "Create RunPod Instance"

read -p "🤔 Do you want to create a RunPod instance now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating RunPod instance..."
    
    # Create pod with recommended settings
    POD_NAME="grpo-training-$(date +%s)"
    
    echo "Creating pod: $POD_NAME"
    
    POD_ID=$(runpod pod create \
        --gpu-type "NVIDIA RTX A100 40GB" \
        --image "runpod/pytorch:2.6-py3.12-cuda-12.1" \
        --name "$POD_NAME" \
        --ports "8888:http,22:tcp,6006:tcp" \
        --container-disk-size 50 \
        --volume-size 100 \
        --memory 64 \
        --env "WANDB_PROJECT=loki-runpod" \
        --env "CUDA_VISIBLE_DEVICES=0" \
        --env "TOKENIZERS_PARALLELISM=false" \
        --env "OPENAI_API_KEY=$OPENAI_API_KEY" \
        --output json | jq -r '.id')
    
    if [ "$POD_ID" = "null" ] || [ -z "$POD_ID" ]; then
        print_error "Failed to create RunPod instance"
        exit 1
    fi
    
    print_success "RunPod instance created with ID: $POD_ID"
    
    # Save pod information
    echo "$POD_ID" > .runpod_pod_id
    echo "Pod ID saved to .runpod_pod_id"
    
    # Wait for pod to be ready
    echo "⏳ Waiting for pod to be ready..."
    sleep 30
    
    # Get pod info
    POD_INFO=$(runpod pod get "$POD_ID" --output json)
    SSH_IP=$(echo "$POD_INFO" | jq -r '.runtime.ip')
    SSH_PORT=$(echo "$POD_INFO" | jq -r '.runtime.port')
    
    echo "$SSH_IP" > .runpod_ssh_ip
    echo "$SSH_PORT" > .runpod_ssh_port
    
    print_success "Pod is ready!"
    echo ""
    echo "🔗 Connection Information:"
    echo "   Pod ID: $POD_ID"
    echo "   SSH: ssh root@$SSH_IP -p $SSH_PORT"
    echo "   Jupyter: http://$SSH_IP:8888"
    echo "   TensorBoard: http://$SSH_IP:6006"
    echo ""
    
    # Ask if user wants to upload files
    read -p "📤 Do you want to upload your project files now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Uploading project files..."
        
        # Create a tarball of the project
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
        ssh -p "$SSH_PORT" root@"$SSH_IP" "cd /workspace && tar -xzf project.tar.gz && rm project.tar.gz && pip install -r requirements_runpod.txt"
        
        print_success "Project files uploaded and dependencies installed!"
        
        # Clean up local tarball
        rm project.tar.gz
    fi
    
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo "Your RunPod instance is ready for GRPO training."
    echo ""
    echo "Next steps:"
    echo "1. SSH into your pod: ssh root@$SSH_IP -p $SSH_PORT"
    echo "2. Navigate to your project: cd /workspace/arpandeep-nrty"
    echo "3. Start training: python training/grpo_trainer.py"
    echo "4. Monitor progress: python monitor_training.py"
    echo ""
    echo "To stop your pod when done:"
    echo "runpod pod stop $POD_ID"
    
else
    echo "No pod created. You can create one later using:"
    echo "runpod pod create --help"
fi

print_success "Setup guide completed!"
echo ""
echo "📚 Additional Resources:"
echo "   - RunPod Docs: https://docs.runpod.io"
echo "   - RunPod Discord: https://discord.gg/runpod"
echo "   - Project README: RUNPOD_DEPLOYMENT.md"

