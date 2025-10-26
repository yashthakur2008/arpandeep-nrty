import json
import os
import csv
from datasets import Dataset
from jinja2 import Environment, FileSystemLoader


def create_harmbench_dataset(data_dir: str = "data", num_samples: int = None, save: bool = True):
    # Load templates
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir, "prompts")))
    system_template = env.get_template("harmbench_system.j2")
    user_template = env.get_template("harmbench_user.j2")
    
    # Generate system prompt (same for all examples)
    system_prompt = system_template.render()
    
    # Check if processed dataset already exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    processed_path = os.path.join(project_root, data_dir, "harmbench.jsonl")
    if os.path.exists(processed_path) and not num_samples:
        print(f"Loading existing processed dataset from {processed_path}")
        return Dataset.from_json(processed_path)
    
    # Load HarmBench CSV file
    csv_path = os.path.join(current_dir, "harmbench_behaviors_text_all.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"HarmBench CSV file not found at {csv_path}")
    
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    # Convert to our format
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if num_samples and len(data) >= num_samples:
                break
            
            # Extract fields from CSV
            behavior = row.get("Behavior", "")
            functional_category = row.get("FunctionalCategory", "")
            semantic_category = row.get("SemanticCategory", "")
            behavior_id = row.get("BehaviorID", "")
            
            # Skip empty behaviors
            if not behavior:
                continue
            
            user_prompt = user_template.render(
                behavior=behavior,
                functional_category=functional_category,
                semantic_category=semantic_category
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
                "behavior": behavior,
                "functional_category": functional_category,
                "semantic_category": semantic_category,
                "behavior_id": behavior_id
            })
    
    dataset = Dataset.from_list(data)
    
    # Save processed dataset
    if save and not num_samples:
        dataset.to_json(processed_path)
        print(f"Saved processed dataset to {processed_path}")
    
    return dataset


def main():
    # Create a small test dataset with 5 samples
    dataset = create_harmbench_dataset(num_samples=5)
    print(f"Dataset size: {len(dataset)}")
    
    # Print all examples in a readable format
    print("\n" + "="*80)
    print("HARMBENCH TEST DATASET")
    print("="*80)
    
    for i, example in enumerate(dataset, 1):
        print(f"\n--- Example {i} ---")
        print(f"Behavior: {example['behavior']}")
        print(f"Functional Category: {example['functional_category']}")
        print(f"Semantic Category: {example['semantic_category']}")
        print(f"Behavior ID: {example['behavior_id']}")
        
        print(f"\nSystem Prompt (first 150 chars): {example['system_prompt'][:150]}...")
        print(f"\nUser Prompt:\n{example['user_prompt']}")
        print("-" * 80)


if __name__ == "__main__":
    main()
