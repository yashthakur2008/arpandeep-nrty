import json
import os

from datasets import Dataset
from jinja2 import Environment, FileSystemLoader


def create_mathqa_dataset(data_dir: str = "data", num_samples: int = None, save: bool = True):
    # Load templates
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir, "prompts")))
    system_template = env.get_template("mathqa_system.j2")
    user_template = env.get_template("mathqa_user.j2")
    
    # Generate system prompt (same for all examples)
    system_prompt = system_template.render()
    
    # Check if processed dataset already exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    processed_path = os.path.join(project_root, data_dir, "mathqa.jsonl")
    if os.path.exists(processed_path) and not num_samples:
        print(f"Loading existing processed dataset from {processed_path}")
        return Dataset.from_json(processed_path)
    
    # Load MathQA dataset
    mathqa_path = os.path.join(project_root, "MathQA", "train.json")
    if not os.path.exists(mathqa_path):
        raise FileNotFoundError(f"MathQA train.json not found at {mathqa_path}")
    
    with open(mathqa_path, encoding='utf-8') as f:
        mathqa_data = json.load(f)
    
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    # Convert to our format
    data = []
    for item in mathqa_data:
        if num_samples and len(data) >= num_samples:
            break
            
        problem = item.get("Problem", "")
        options = item.get("options", "")
        correct = item.get("correct", "")
        rationale = item.get("Rationale", "")
        category = item.get("category", "")
        
        # Format options for display
        options_text = options if options else "No options provided"
        
        user_prompt = user_template.render(
            problem=problem, 
            options=options_text, 
            correct=correct
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
            "original_problem": problem,
            "options": options_text,
            "correct_answer": correct,
            "rationale": rationale,
            "category": category,
            "annotated_formula": item.get("annotated_formula", ""),
            "linear_formula": item.get("linear_formula", "")
        })
    
    dataset = Dataset.from_list(data)
    
    # Save processed dataset
    if save and not num_samples:
        dataset.to_json(processed_path)
        print(f"Saved processed dataset to {processed_path}")
    
    return dataset


def main():
    dataset = create_mathqa_dataset()
    print(f"Dataset size: {len(dataset)}")
    
    example = dataset[0]
    print("\n=== Example ===")
    print(f"Problem: {example['original_problem']}")
    print(f"Options: {example['options']}")
    print(f"Correct Answer: {example['correct_answer']}")
    print(f"Category: {example['category']}")
    print("\n--- Prompt Format (for TRL) ---")
    print(f"Type: {type(example['prompt'])}")
    print(f"Messages: {len(example['prompt'])}")
    for msg in example['prompt']:
        print(f"  - {msg['role']}: {msg['content'][:100]}...")
    print(f"\n--- User Prompt ---\n{example['user_prompt']}")


if __name__ == "__main__":
    main()
