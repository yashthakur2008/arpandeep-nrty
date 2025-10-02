import json
import os
from datasets import Dataset, load_dataset
from jinja2 import Environment, FileSystemLoader


def create_hotpotqa_dataset(data_dir: str = "data", num_samples: int = None, save: bool = True):
    # Load template
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(os.path.join(current_dir, "prompts")))
    template = env.get_template("hotpotqa_prompt.j2")
    
    # Check if processed dataset already exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    processed_path = os.path.join(project_root, data_dir, "hotpotqa.jsonl")
    if os.path.exists(processed_path) and not num_samples:
        print(f"Loading existing processed dataset from {processed_path}")
        return Dataset.from_json(processed_path)
    
    # Download dataset
    ds = load_dataset("hotpotqa/hotpot_qa", "distractor")
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    # Convert to our format
    data = []
    for item in ds["train"]:
        if num_samples and len(data) >= num_samples:
            break
            
        question = item.get("question", "")
        answer = item.get("answer", "")
        
        # Get evidence from supporting facts
        evidence = ""
        supporting_facts = item.get("supporting_facts", {})
        context = item.get("context", {})
        if supporting_facts and context:
            for title, sent_id in zip(supporting_facts.get("title", []), supporting_facts.get("sent_id", [])):
                if title in context.get("title", []):
                    title_idx = context["title"].index(title)
                    sentences = context["sentences"][title_idx]
                    if sent_id < len(sentences):
                        evidence += sentences[sent_id] + " "
        
        prompt = template.render(question=question, evidence=evidence.strip(), answer=answer)
        
        data.append({
            "prompt": prompt,
            "original_question": question,
            "answer": answer,
            "evidence": evidence.strip()
        })
    
    dataset = Dataset.from_list(data)
    
    # Save processed dataset
    if save and not num_samples:
        dataset.to_json(processed_path)
        print(f"Saved processed dataset to {processed_path}")
    
    return dataset


def main():
    dataset = create_hotpotqa_dataset()
    print(f"Dataset size: {len(dataset)}")
    
    example = dataset[0]
    print(f"Question: {example['original_question']}")
    print(f"Answer: {example['answer']}")


if __name__ == "__main__":
    main()
