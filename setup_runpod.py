#!/usr/bin/env python3
"""
RunPod Setup Script for GRPO Training

This script helps you set up and deploy your GRPO training on RunPod.
"""

import os
import yaml
import subprocess
import sys
import time
from typing import Dict, Any
import requests
import json

class RunPodManager:
    def __init__(self, config_path: str = "runpod_config.yaml"):
        """Initialize RunPod manager with configuration."""
        self.config_path = config_path
        self.config = self.load_config()
        self.api_key = os.getenv("RUNPOD_API_KEY")
        
        if not self.api_key:
            raise ValueError("RUNPOD_API_KEY environment variable not set")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Configuration file {self.config_path} not found!")
            sys.exit(1)
    
    def check_runpod_cli(self) -> bool:
        """Check if runpodctl is installed."""
        try:
            result = subprocess.run(["runpodctl", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_runpod_cli(self):
        """Install runpodctl if not present."""
        print("Installing runpodctl...")
        try:
            subprocess.run([
                "curl", "-sSL", "https://runpod.io/install-runpodctl.sh"
            ], check=True)
            subprocess.run([
                "bash", "-c", "curl -sSL https://runpod.io/install-runpodctl.sh | bash"
            ], check=True)
            print("runpodctl installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install runpodctl: {e}")
            sys.exit(1)
    
    def create_pod(self) -> str:
        """Create a new RunPod instance."""
        runpod_config = self.config["runpod"]
        training_config = self.config["training"]
        
        # Build environment variables string
        env_vars = runpod_config.get("env_vars", {})
        env_string = " ".join([f'--env "{k}={v}"' for k, v in env_vars.items()])
        
        # Add training-specific environment variables
        env_string += f' --env "MODEL_NAME={training_config["model_name"]}"'
        env_string += f' --env "DATASET_PATH={training_config["dataset_path"]}"'
        env_string += f' --env "NUM_SAMPLES={training_config["num_samples"]}"'
        
        # Build ports string
        ports = runpod_config.get("ports", [])
        ports_string = " ".join([f'--ports "{port}"' for port in ports])
        
        # Build runpodctl command
        cmd = f"""
        runpodctl create pod \\
            --gpuType "{runpod_config['gpu_type']}" \\
            --imageName "{runpod_config['docker_image']}" \\
            --name "grpo-training-{int(time.time())}" \\
            {ports_string} \\
            --containerDiskSize {runpod_config['container_disk_size']} \\
            --volumeSize {runpod_config['storage_gb']} \\
            --mem {runpod_config['memory_gb']} \\
            --startSSH \\
            {env_string}
        """
        
        print("Creating RunPod instance...")
        print(f"Command: {cmd}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("RunPod instance created successfully!")
                return result.stdout.strip()
            else:
                print(f"Failed to create RunPod instance: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error creating RunPod instance: {e}")
            return None
    
    def setup_environment(self, pod_id: str):
        """Setup the training environment on the RunPod."""
        print(f"Setting up environment on pod {pod_id}...")
        
        # Commands to run on the pod
        setup_commands = [
            # Update system
            "apt-get update && apt-get install -y git wget curl",
            
            # Install Python dependencies
            "pip install -U pip",
            "pip install wandb",
            
            # Clone repository (you'll need to update this with your repo)
            "cd /workspace && git clone https://github.com/yourusername/arpandeep-nrty.git",
            "cd /workspace/arpandeep-nrty && pip install -e .",
            
            # Create data directory
            "mkdir -p /workspace/data",
            
            # Set up WandB
            "wandb login --relogin",
            
            # Create output directory
            "mkdir -p /workspace/outputs/grpo-training",
        ]
        
        for cmd in setup_commands:
            print(f"Running: {cmd}")
            # Here you would SSH into the pod and run these commands
            # For now, we'll just print them
            pass
    
    def start_training(self, pod_id: str):
        """Start the GRPO training on the RunPod."""
        print(f"Starting training on pod {pod_id}...")
        
        training_cmd = """
        cd /workspace/arpandeep-nrty && \\
        python training/grpo_trainer.py
        """
        
        print(f"Training command: {training_cmd}")
        print("Run this command in your RunPod terminal to start training.")
    
    def monitor_training(self, pod_id: str):
        """Monitor training progress."""
        print(f"Monitoring training on pod {pod_id}...")
        print("You can monitor progress through:")
        print("1. WandB dashboard: https://wandb.ai")
        print("2. SSH into the pod and check logs")
        print("3. Jupyter notebook at http://your-pod-ip:8888")
    
    def cleanup_pod(self, pod_id: str):
        """Clean up the RunPod instance."""
        print(f"Cleaning up pod {pod_id}...")
        
        cmd = f"runpodctl stop pod {pod_id}"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("Pod stopped successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop pod: {e}")

def main():
    """Main function to manage RunPod deployment."""
    print("RunPod GRPO Training Setup")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("RUNPOD_API_KEY"):
        print("ERROR: RUNPOD_API_KEY environment variable not set!")
        print("Please set your RunPod API key:")
        print("export RUNPOD_API_KEY=your_api_key_here")
        sys.exit(1)
    
    manager = RunPodManager()
    
    # Check if runpodctl is installed
    if not manager.check_runpod_cli():
        print("runpodctl not found. Installing...")
        manager.install_runpod_cli()
    
    # Create pod
    pod_id = manager.create_pod()
    if not pod_id:
        print("Failed to create pod. Exiting.")
        sys.exit(1)
    
    print(f"\nPod created with ID: {pod_id}")
    print("\nNext steps:")
    print("1. SSH into your pod: runpodctl ssh <pod_id>")
    print("2. Run the setup commands manually")
    print("3. Start training with: python training/grpo_trainer.py")
    print("4. Monitor progress on WandB")
    
    # Ask if user wants to clean up
    response = input("\nDo you want to set up auto-cleanup? (y/n): ")
    if response.lower() == 'y':
        print("Auto-cleanup will be configured...")
        # Add auto-cleanup logic here

if __name__ == "__main__":
    main()

