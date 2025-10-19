import json
import os
from datasets import Dataset, load_dataset
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
    
    # Load HarmBench dataset
    ds = load_dataset("walledai/HarmBench", "contextual")
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    # Convert to our format
    data = []
    for item in ds["train"]:
        if num_samples and len(data) >= num_samples:
            break
            
        # Extract fields from HarmBench dataset
        prompt = item.get("prompt", "")
        response = item.get("response", "")
        category = item.get("category", "")
        subcategory = item.get("subcategory", "")
        harmfulness = item.get("harmfulness", "")
        context = item.get("context", "")
        
        user_prompt = user_template.render(
            prompt=prompt,
            response=response,
            category=category,
            subcategory=subcategory,
            harmfulness=harmfulness,
            context=context
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
            "response": response,
            "category": category,
            "subcategory": subcategory,
            "harmfulness": harmfulness,
            "context": context
        })
    
    dataset = Dataset.from_list(data)
    
    # Save processed dataset
    if save and not num_samples:
        dataset.to_json(processed_path)
        print(f"Saved processed dataset to {processed_path}")
    
    return dataset


def main():
    dataset = create_harmbench_dataset()
    print(f"Dataset size: {len(dataset)}")
    
    example = dataset[0]
    print(f"\n=== Example ===")
    print(f"Original Prompt: {example['original_prompt']}")
    print(f"Response: {example['response']}")
    print(f"Category: {example['category']}")
    print(f"Subcategory: {example['subcategory']}")
    print(f"Harmfulness: {example['harmfulness']}")
    print(f"Context: {example['context']}")
    print(f"\n--- Prompt Format (for TRL) ---")
    print(f"Type: {type(example['prompt'])}")
    print(f"Messages: {len(example['prompt'])}")
    for msg in example['prompt']:
        print(f"  - {msg['role']}: {msg['content'][:100]}...")
    print(f"\n--- User Prompt ---\n{example['user_prompt']}")


if __name__ == "__main__":
    main()
