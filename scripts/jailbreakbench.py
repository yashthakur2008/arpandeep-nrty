import json
import os
from datasets import Dataset, load_dataset
from jinja2 import Environment, FileSystemLoader


def create_jailbreakbench_dataset(data_dir: str = "data", num_samples: int = None, save: bool = True):
    # Load templates
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir, "prompts")))
    system_template = env.get_template("jailbreakbench_system.j2")
    user_template = env.get_template("jailbreakbench_user.j2")
    
    # Generate system prompt (same for all examples)
    system_prompt = system_template.render()
    
    # Check if processed dataset already exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    processed_path = os.path.join(project_root, data_dir, "jailbreakbench.jsonl")
    if os.path.exists(processed_path) and not num_samples:
        print(f"Loading existing processed dataset from {processed_path}")
        return Dataset.from_json(processed_path)
    
    # Load JailbreakBench dataset
    ds = load_dataset("JailbreakBench/JBB-Behaviors", "behaviors")
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    # Convert to our format
    data = []
    for item in ds["train"]:
        if num_samples and len(data) >= num_samples:
            break
            
        prompt = item.get("prompt", "")
        target = item.get("target", "")
        behavior = item.get("behavior", "")
        category = item.get("category", "")
        source = item.get("source", "")
        
        user_prompt = user_template.render(
            prompt=prompt,
            target=target,
            behavior=behavior,
            category=category
        )
        
        # Create conversational format for TRL GRPO trainer
        prompt_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        data.append({
            "prompt": prompt_messages,  # TRL expects this format
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "original_prompt": prompt,
            "target": target,
            "behavior": behavior,
            "category": category,
            "source": source
        })
    
    dataset = Dataset.from_list(data)
    
    # Save processed dataset
    if save and not num_samples:
        dataset.to_json(processed_path)
        print(f"Saved processed dataset to {processed_path}")
    
    return dataset


def main():
    dataset = create_jailbreakbench_dataset()
    print(f"Dataset size: {len(dataset)}")
    
    example = dataset[0]
    print(f"\n=== Example ===")
    print(f"Original Prompt: {example['original_prompt']}")
    print(f"Target: {example['target']}")
    print(f"Behavior: {example['behavior']}")
    print(f"Category: {example['category']}")
    print(f"Source: {example['source']}")
    print(f"\n--- Prompt Format (for TRL) ---")
    print(f"Type: {type(example['prompt'])}")
    print(f"Messages: {len(example['prompt'])}")
    for msg in example['prompt']:
        print(f"  - {msg['role']}: {msg['content'][:100]}...")
    print(f"\n--- User Prompt ---\n{example['user_prompt']}")


if __name__ == "__main__":
    main()
