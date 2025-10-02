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
                   **kwargs) -> List[float]:
    """
    Calculate rewards using LLM evaluation of adversarial questions.
    """
    rewards = []
    
    for i, completion in enumerate(completions):
        # Extract the text content from the completion
        response = completion
        
        print(f"\n[{i+1}] Model generated: {response}")
        
        # Extract the misdirection from the response
        misdirection = extract_misdirection_from_response(response)
        
        if not misdirection:
            print(f"No <misdirection> tags found")
            rewards.append(0.0)
            continue
        
        # Get the original question, evidence and correct answer for this example
        question = original_question[i] if original_question and i < len(original_question) else ""
        current_evidence = evidence[i] if evidence and i < len(evidence) else ""
        correct_answer = answer[i] if answer and i < len(answer) else ""
        
        # Create the misleading question by appending misdirection
        misleading_question = f"{question} {misdirection}"
        
        # Use LLM to evaluate the misleading question
        llm_answer = evaluate_question_with_llm(misleading_question, current_evidence)
        
        # Calculate reward based on correctness (flipped: 1 for wrong, 0 for correct)
        if llm_answer and correct_answer:
            if correct_answer.lower().strip() == llm_answer.lower().strip():
                correctness_reward = 0.0
                result = "FAILED"
            else:
                correctness_reward = 1.0
                result = "SUCCESS"
        else:
            correctness_reward = 0.0
            result = "NO_ANSWER"
        
        print(f"\n[{i+1}] Misdirection: {misdirection}")
        print(f"LLM: {llm_answer} | Truth: {correct_answer} | Result: {result} | Reward: {correctness_reward:.1f}")
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
    """
    # Look for <misdirection>...</misdirection> tags
    misdirection_match = re.search(r'<misdirection>(.*?)</misdirection>', response, re.DOTALL)
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


