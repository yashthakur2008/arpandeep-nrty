# RunPod Deployment Guide for GRPO Training

This guide will help you deploy and run your GRPO training on RunPod with optimal performance and cost efficiency.

## 🎯 Recommended RunPod Environment

### **Best Choice: A100 40GB (Community Cloud)**
- **GPU**: NVIDIA RTX A100 40GB
- **Cost**: ~$0.29-0.39/hour
- **Memory**: 64GB RAM
- **Storage**: 100GB SSD
- **Why**: Perfect balance of performance and cost for Qwen2.5-0.5B training

### **Alternative Options:**
- **RTX 4090 24GB**: ~$0.20-0.25/hour (budget option)
- **A10G 24GB**: ~$0.30-0.35/hour (good middle ground)
- **H100 80GB**: ~$1.89/hour (if you need maximum performance)

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Set your API keys
export RUNPOD_API_KEY="your_runpod_api_key"
export OPENAI_API_KEY="your_openai_api_key"
export WANDB_API_KEY="your_wandb_api_key"  # Optional
```

### 2. Deploy with One Command
```bash
# Make deployment script executable
chmod +x deploy_runpod.sh

# Run deployment
./deploy_runpod.sh
```

### 3. Connect to Your Pod
```bash
# SSH into your pod (IP and port will be shown after deployment)
ssh root@<pod_ip> -p <ssh_port>

# Or use the saved connection info
ssh root@$(cat .runpod_ssh_ip) -p $(cat .runpod_ssh_port)
```

## 📋 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Create RunPod Instance
```bash
# Install runpodctl
curl -sSL https://runpod.io/install-runpodctl.sh | bash

# Create pod
runpodctl create pod \
    --gpuType "NVIDIA RTX A100 40GB" \
    --imageName "runpod/pytorch:2.6-py3.12-cuda-12.1" \
    --name "grpo-training" \
    --ports "8888:http,22:tcp,6006:tcp" \
    --containerDiskSize 50 \
    --volumeSize 100 \
    --mem 64 \
    --startSSH \
    --env "WANDB_PROJECT=loki-runpod" \
    --env "CUDA_VISIBLE_DEVICES=0"
```

### 2. Setup Environment
```bash
# SSH into your pod
ssh root@<pod_ip> -p <ssh_port>

# Install dependencies
cd /workspace
pip install -r requirements_runpod.txt

# Clone your repository
git clone https://github.com/yourusername/arpandeep-nrty.git
cd arpandeep-nrty
```

### 3. Upload Data
```bash
# Upload your data files
scp -P <ssh_port> data/hotpotqa.jsonl root@<pod_ip>:/workspace/arpandeep-nrty/data/
```

### 4. Start Training
```bash
# Start training
python training/grpo_trainer.py
```

## 📊 Monitoring Your Training

### Real-time Monitoring
```bash
# Run the monitoring script
python monitor_training.py --interval 60

# Or get a one-time status report
python monitor_training.py --once
```

### Web Interfaces
- **Jupyter**: `http://<pod_ip>:8888`
- **TensorBoard**: `http://<pod_ip>:6006`
- **WandB**: https://wandb.ai

### Key Metrics to Watch
- GPU utilization (should be >80%)
- GPU memory usage (should be <90%)
- Training loss and reward metrics
- Cost per hour

## 💰 Cost Optimization

### 1. Use Spot Instances
```yaml
# In runpod_config.yaml
cost_optimization:
  use_spot: true
  spot_price_limit: 0.25  # Max $0.25/hour
```

### 2. Auto-shutdown
```bash
# Set up auto-shutdown after training
echo "Training completed. Shutting down in 10 minutes..."
sleep 600
runpodctl stop pod <pod_id>
```

### 3. Monitor Costs
- Track hourly costs in RunPod dashboard
- Set up cost alerts
- Use the monitoring script to track estimated costs

## 🔧 Configuration Options

### Training Configuration
```python
# In grpo_trainer.py DEFAULT_CONFIG
{
    "batch_size": 4,  # Optimized for A100 40GB
    "gradient_accumulation_steps": 2,
    "fp16": True,  # Use mixed precision
    "gradient_checkpointing": True,  # Save memory
    "dataloader_num_workers": 4,  # Optimize data loading
}
```

### GPU Memory Optimization
```python
# Automatic batch size adjustment based on GPU memory
def get_optimal_batch_size(model_name: str, max_length: int = 1024) -> int:
    gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    if gpu_memory_gb >= 40:  # A100 40GB
        return 8
    elif gpu_memory_gb >= 24:  # RTX 4090, A10G
        return 4
    else:
        return 2
```

## 🐛 Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory
```bash
# Reduce batch size in runpod_config.yaml
training:
  batch_size: 2  # Reduce from 4 to 2
  gradient_accumulation_steps: 4  # Increase to maintain effective batch size
```

#### 2. Slow Data Loading
```bash
# Increase number of workers
training:
  dataloader_num_workers: 8  # Increase from 4
```

#### 3. API Rate Limits
```python
# In reward_function.py, add retry logic with exponential backoff
def evaluate_question_with_llm(question: str, evidence: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            # API call
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
```

#### 4. Connection Issues
```bash
# Check pod status
runpodctl get pod <pod_id>

# Restart pod if needed
runpodctl stop pod <pod_id>
runpodctl start pod <pod_id>
```

### Performance Issues

#### Low GPU Utilization
- Increase batch size if memory allows
- Check if data loading is the bottleneck
- Verify reward function isn't too slow

#### Slow Training
- Use mixed precision (fp16)
- Enable gradient checkpointing
- Optimize reward function with caching

## 📈 Scaling Up

### For Larger Models
```yaml
# Use H100 80GB for larger models
runpod:
  gpu_type: "NVIDIA H100 80GB"
  memory_gb: 128
  storage_gb: 200
```

### For Larger Datasets
```yaml
# Increase storage and memory
runpod:
  storage_gb: 500
  memory_gb: 128
```

### Multi-GPU Training
```python
# For multi-GPU setups (future enhancement)
training:
  batch_size: 8
  gradient_accumulation_steps: 1
  dataloader_num_workers: 16
```

## 🧹 Cleanup

### Stop Pod
```bash
# Stop your pod when done
runpodctl stop pod <pod_id>
```

### Clean Up Files
```bash
# Remove temporary files
rm -f .runpod_pod_id .runpod_ssh_ip .runpod_ssh_port
rm -f cleanup_script.sh
```

## 📞 Support

### RunPod Support
- Documentation: https://docs.runpod.io
- Discord: https://discord.gg/runpod
- Email: support@runpod.io

### Project Issues
- GitHub Issues: Create an issue in your repository
- WandB Community: https://wandb.ai/forum

## 🎉 Success Tips

1. **Start Small**: Begin with a small dataset to test your setup
2. **Monitor Costs**: Keep an eye on hourly costs
3. **Use Spot Instances**: Save up to 70% with spot pricing
4. **Optimize Batch Size**: Find the sweet spot for your GPU
5. **Cache Everything**: Cache templates, API clients, etc.
6. **Set Up Alerts**: Get notified when training completes or fails

Happy training! 🚀

