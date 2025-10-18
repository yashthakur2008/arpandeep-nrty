import json
import os
from datasets import Dataset, load_dataset
from jinja2 import Environment, FileSystemLoader


def create_generalAnalysis_dataset(data_dir: str = "data", num_samples: int = None, save: bool = True):
    """
    Create dataset from GeneralAnalysis/GA_Jailbreak_Benchmark.
    
    Args:
        data_dir: Directory to save processed dataset
        num_samples: Number of samples to process (None for all)
        save: Whether to save the processed dataset
    
    Returns:
        HuggingFace Dataset in the format expected by TRL GRPO trainer
    """
    # Load templates (reuse existing jailbreak templates since it's the same type of data)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir, "prompts")))
    system_template = env.get_template("jailbreakbench_system.j2")
    user_template = env.get_template("jailbreakbench_user.j2")
    
    # Generate system prompt (same for all examples)
    system_prompt = system_template.render()
    
    # Check if processed dataset already exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    processed_path = os.path.join(project_root, data_dir, "generalAnalysis.jsonl")
    if os.path.exists(processed_path) and not num_samples:
        print(f"Loading existing processed dataset from {processed_path}")
        return Dataset.from_json(processed_path)
    
    # Load GeneralAnalysis JailbreakBench dataset
    print("Loading GeneralAnalysis/GA_Jailbreak_Benchmark dataset...")
    ds = load_dataset("GeneralAnalysis/GA_Jailbreak_Benchmark", "default")
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    print(f"Dataset loaded. Features: {ds['train'].features}")
    print(f"Number of examples: {len(ds['train'])}")
    
    # Convert to our format
    data = []
    for i, item in enumerate(ds["train"]):
        if num_samples and len(data) >= num_samples:
            break
            
        # Extract fields - we need to check what fields are available
        # Common field names in jailbreak datasets
        prompt = item.get("prompt", item.get("question", item.get("input", "")))
        target = item.get("target", item.get("expected_output", item.get("output", "")))
        behavior = item.get("behavior", item.get("category", item.get("type", "")))
        category = item.get("category", item.get("type", item.get("behavior", "")))
        source = item.get("source", item.get("origin", "GA_Jailbreak_Benchmark"))
        
        # Additional fields that might be useful
        difficulty = item.get("difficulty", item.get("level", ""))
        description = item.get("description", item.get("explanation", ""))
        
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
            "source": source,
            "difficulty": difficulty,
            "description": description
        })
    
    dataset = Dataset.from_list(data)
    
    # Save processed dataset
    if save and not num_samples:
        dataset.to_json(processed_path)
        print(f"Saved processed dataset to {processed_path}")
    
    return dataset


def main():
    """Main function to test the dataset creation."""
    dataset = create_generalAnalysis_dataset(num_samples=5)  # Test with 5 samples
    print(f"Dataset size: {len(dataset)}")
    
    if len(dataset) > 0:
        example = dataset[0]
        print(f"\n=== Example ===")
        print(f"Original Prompt: {example['original_prompt']}")
        print(f"Target: {example['target']}")
        print(f"Behavior: {example['behavior']}")
        print(f"Category: {example['category']}")
        print(f"Source: {example['source']}")
        print(f"Difficulty: {example['difficulty']}")
        print(f"Description: {example['description']}")
        print(f"\n--- Prompt Format (for TRL) ---")
        print(f"Type: {type(example['prompt'])}")
        print(f"Messages: {len(example['prompt'])}")
        for msg in example['prompt']:
            print(f"  - {msg['role']}: {msg['content'][:100]}...")
        print(f"\n--- User Prompt ---\n{example['user_prompt']}")
        
        # Show field distribution
        print(f"\n--- Field Analysis ---")
        categories = {}
        behaviors = {}
        sources = {}
        
        for item in dataset:
            cat = item.get('category', 'Unknown')
            beh = item.get('behavior', 'Unknown')
            src = item.get('source', 'Unknown')
            
            categories[cat] = categories.get(cat, 0) + 1
            behaviors[beh] = behaviors.get(beh, 0) + 1
            sources[src] = sources.get(src, 0) + 1
        
        print(f"Categories: {categories}")
        print(f"Behaviors: {behaviors}")
        print(f"Sources: {sources}")


if __name__ == "__main__":
    main()
