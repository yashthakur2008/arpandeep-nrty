"""
Reward function for adversarial question generation training.
"""

from typing import List, Dict, Any
import re
import openai
import os
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def reward_function(completions: List[Dict[str, Any]], 
                   original_question: List[str] = None,
                   evidence: List[str] = None,
                   answer: List[str] = None,
                   num_generations: int = 2,
                   **kwargs) -> List[float]:
    """
    Calculate rewards using LLM evaluation of adversarial questions.
    
    Args:
        completions: List of generated completions (multiple per prompt)
        original_question: List of original questions (one per prompt)
        evidence: List of evidence texts (one per prompt)
        answer: List of correct answers (one per prompt)
        num_generations: Number of completions generated per prompt
    """
    rewards = []
    
    for i, completion in enumerate(completions):
        # Map completion index to prompt index (multiple completions per prompt)
        prompt_idx = i // num_generations
        
        # Extract aligned inputs using prompt index
        question = original_question[prompt_idx] if original_question and prompt_idx < len(original_question) else ""
        current_evidence = evidence[prompt_idx] if evidence and prompt_idx < len(evidence) else ""
        correct_answer = answer[prompt_idx] if answer and prompt_idx < len(answer) else ""

        # Extract the text content from the completion
        response = completion

        # Extract the misdirection from the response
        misdirection = extract_misdirection_from_response(response)

        if not misdirection:
            print(f"Q: {question}")
            print(f"     No misdirection tags | R=0.0\n")
            rewards.append(0.0)
            continue
        
        print(f"Q: {question}")
        print(f"     Misdirection: {misdirection}")
        
        # Create the misleading question by appending misdirection
        misleading_question = f"{question} {misdirection}"
        
        # Use LLM to evaluate the misleading question
        llm_answer = evaluate_question_with_llm(misleading_question, current_evidence)
        
        # Calculate reward based on correctness (flipped: 1 for wrong, 0 for correct)
        if llm_answer and correct_answer:
            if correct_answer.lower().strip() == llm_answer.lower().strip():
                correctness_reward = 0.0
                result = "FAIL"
            else:
                correctness_reward = 1.0
                result = "SUCCESS"
        else:
            correctness_reward = 0.0
            result = "ERROR"
        
        print(f"     {result}: LLM={llm_answer} | Truth={correct_answer} | R={correctness_reward:.1f}\n")
        rewards.append(float(correctness_reward))
    
    # fix: Add small epsilon to avoid all-zero rewards causing numerical instability
    import numpy as np
    if len(rewards) > 0 and np.std(rewards) < 1e-8:
        rewards = [r + np.random.uniform(0, 0.01) for r in rewards]
    
    return rewards


def extract_misdirection_from_response(response: str) -> str:
    """
    Extract the misdirection from the model's response.
    Expected format: <reasoning>...</reasoning><misdirection>...</misdirection>
    Be tolerant of code fences and 'Output:' wrappers.
    """
    if not response:
        return ""
    # Strip common wrappers
    cleaned = response.strip()
    # Remove leading/trailing triple backtick fences and labels
    cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    # Remove a leading 'Output:' line if present
    cleaned = re.sub(r"^\s*Output:\s*\n", "", cleaned, flags=re.IGNORECASE)
    
    # Look for <misdirection>...</misdirection> tags (case-sensitive tags, tolerant of inner newlines)
    misdirection_match = re.search(r"<misdirection>([\s\S]*?)</misdirection>", cleaned)
    if misdirection_match:
        return misdirection_match.group(1).strip()
    
    return ""


def evaluate_question_with_llm(question: str, evidence: str) -> str:
    """
    Use OpenAI API to answer the question given the evidence.
    """
    try:
        # Load template
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env = Environment(loader=FileSystemLoader(os.path.join(current_dir, "prompts")))
        template = env.get_template("hotpotqa_prompt.j2")
        
        # Set up OpenAI client
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = template.render(evidence=evidence, question=question)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided evidence. Give a direct, concise answer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.1
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "error"


