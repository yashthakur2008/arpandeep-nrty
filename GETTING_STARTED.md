# 🚀 Getting Started with RunPod for GRPO Training

This guide will walk you through setting up and running your GRPO training on RunPod from scratch.

## 📋 Prerequisites

Before you begin, you'll need:

1. **RunPod Account** - Sign up at [https://runpod.io](https://runpod.io)
2. **OpenAI API Key** - Get from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. **WandB Account** (Optional) - Sign up at [https://wandb.ai](https://wandb.ai)
4. **Credit Card** - For RunPod billing

## 🎯 Recommended RunPod Environment

**Best Choice: A100 40GB (Community Cloud)**
- **GPU**: NVIDIA RTX A100 40GB
- **Cost**: ~$0.29-0.39/hour
- **Memory**: 64GB RAM
- **Storage**: 100GB SSD
- **Why**: Perfect balance of performance and cost for your model

## 🚀 Quick Start (5 Minutes)

### Step 1: Set Up Environment
```bash
# Run the environment setup script
./setup_env.sh

# Set your API keys (replace with your actual keys)
export RUNPOD_API_KEY="your_runpod_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"
export WANDB_API_KEY="your_wandb_api_key_here"  # Optional
```

### Step 2: Run the Getting Started Guide
```bash
# This will guide you through the entire setup process
./get_started_runpod.sh
```

That's it! The script will:
- ✅ Check your API keys
- ✅ Configure RunPod CLI
- ✅ Test connection
- ✅ Create a pod with optimal settings
- ✅ Upload your project files
- ✅ Install dependencies
- ✅ Provide connection instructions

## 📖 Detailed Step-by-Step Guide

### Step 1: Get Your API Keys

#### RunPod API Key
1. Go to [https://runpod.io](https://runpod.io) and sign up
2. Navigate to Settings → API Keys
3. Click "Generate API Key"
4. Copy and save it securely

#### OpenAI API Key
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy and save it securely

#### WandB API Key (Optional)
1. Go to [https://wandb.ai](https://wandb.ai) and sign up
2. Go to Settings → API Keys
3. Copy your API key

### Step 2: Install RunPod CLI
```bash
# Install the RunPod Python package
python3 -m pip install runpod

# Verify installation
runpod --help
```

### Step 3: Configure RunPod CLI
```bash
# Configure with your API key
runpod config YOUR_RUNPOD_API_KEY

# Test connection
runpod pod list
```

### Step 4: Create Your First Pod

#### Option A: Use the Automated Script
```bash
# Run the getting started guide
./get_started_runpod.sh
```

#### Option B: Manual Creation
```bash
# Create a pod manually
runpod pod create \
    --gpu-type "NVIDIA RTX A100 40GB" \
    --image "runpod/pytorch:2.6-py3.12-cuda-12.1" \
    --name "grpo-training" \
    --ports "8888:http,22:tcp,6006:tcp" \
    --container-disk-size 50 \
    --volume-size 100 \
    --memory 64 \
    --env "WANDB_PROJECT=loki-runpod" \
    --env "CUDA_VISIBLE_DEVICES=0" \
    --env "OPENAI_API_KEY=$OPENAI_API_KEY"
```

### Step 5: Connect to Your Pod
```bash
# Get pod information
runpod pod list

# SSH into your pod (replace with your pod's IP and port)
ssh root@YOUR_POD_IP -p YOUR_SSH_PORT
```

### Step 6: Upload Your Project
```bash
# From your local machine, upload the project
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='wandb' --exclude='outputs' -czf project.tar.gz .
scp -P YOUR_SSH_PORT project.tar.gz root@YOUR_POD_IP:/workspace/

# On the pod, extract and install dependencies
ssh root@YOUR_POD_IP -p YOUR_SSH_PORT "cd /workspace && tar -xzf project.tar.gz && rm project.tar.gz && pip install -r requirements_runpod.txt"
```

### Step 7: Start Training
```bash
# SSH into your pod
ssh root@YOUR_POD_IP -p YOUR_SSH_PORT

# Navigate to your project
cd /workspace/arpandeep-nrty

# Start training
python training/grpo_trainer.py
```

### Step 8: Monitor Training
```bash
# In another terminal, monitor your training
python monitor_training.py --interval 60

# Or check status once
python monitor_training.py --once
```

## 🔗 Access Points

Once your pod is running, you can access:

- **SSH**: `ssh root@YOUR_POD_IP -p YOUR_SSH_PORT`
- **Jupyter**: `http://YOUR_POD_IP:8888`
- **TensorBoard**: `http://YOUR_POD_IP:6006`
- **WandB**: https://wandb.ai (your project: loki-runpod)

## 💰 Cost Management

### Monitor Costs
- Check hourly costs in RunPod dashboard
- Use the monitoring script to track estimated costs
- Set up cost alerts in RunPod

### Save Money
```bash
# Use spot instances for up to 70% savings
runpod pod create --gpu-type "NVIDIA RTX A100 40GB" --spot

# Stop your pod when done
runpod pod stop YOUR_POD_ID
```

### Auto-shutdown
```bash
# Set up auto-shutdown after training
echo "Training completed. Shutting down in 10 minutes..."
sleep 600
runpod pod stop YOUR_POD_ID
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "API key not found"
```bash
# Check if your API key is set
echo $RUNPOD_API_KEY

# Reconfigure if needed
runpod config YOUR_RUNPOD_API_KEY
```

#### 2. "Pod creation failed"
- Check your billing information in RunPod dashboard
- Ensure you have sufficient credits
- Try a different GPU type or region

#### 3. "SSH connection refused"
- Wait a few minutes for the pod to fully start
- Check the pod status: `runpod pod get YOUR_POD_ID`
- Ensure SSH is enabled in pod settings

#### 4. "CUDA out of memory"
```bash
# Reduce batch size in your training script
# Edit training/grpo_trainer.py
# Change batch_size from 4 to 2
```

#### 5. "Slow training"
- Check GPU utilization: `nvidia-smi`
- Increase batch size if memory allows
- Enable mixed precision (fp16) - already enabled in optimized code

### Getting Help

1. **RunPod Documentation**: https://docs.runpod.io
2. **RunPod Discord**: https://discord.gg/runpod
3. **Project Issues**: Create an issue in this repository
4. **WandB Community**: https://wandb.ai/forum

## 📊 Performance Tips

### Optimize GPU Usage
```bash
# Check GPU utilization
nvidia-smi

# Monitor in real-time
watch -n 1 nvidia-smi
```

### Optimize Training Speed
- Use mixed precision (fp16) - already enabled
- Enable gradient checkpointing - already enabled
- Optimize data loading - already optimized
- Use appropriate batch size for your GPU

### Monitor Training Progress
```bash
# Real-time monitoring
python monitor_training.py --interval 30

# Check WandB dashboard
# Check TensorBoard logs
```

## 🧹 Cleanup

### Stop Your Pod
```bash
# Stop your pod when training is complete
runpod pod stop YOUR_POD_ID
```

### Clean Up Local Files
```bash
# Remove temporary files
rm -f .runpod_pod_id .runpod_ssh_ip .runpod_ssh_port
rm -f project.tar.gz cleanup_script.sh
```

## 🎉 Success Tips

1. **Start Small**: Begin with a small dataset to test your setup
2. **Monitor Costs**: Keep an eye on hourly costs
3. **Use Spot Instances**: Save up to 70% with spot pricing
4. **Set Up Alerts**: Get notified when training completes or fails
5. **Backup Checkpoints**: Download important checkpoints before stopping pods
6. **Optimize Batch Size**: Find the sweet spot for your GPU memory

## 📚 Next Steps

Once you're comfortable with the basics:

1. **Scale Up**: Try larger models or datasets
2. **Multi-GPU**: Experiment with multi-GPU training
3. **Custom Images**: Create your own Docker images
4. **Automation**: Set up automated training pipelines
5. **Cost Optimization**: Implement advanced cost-saving strategies

Happy training! 🚀

---

**Need help?** Check out the [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md) for advanced deployment options, or create an issue in this repository.

