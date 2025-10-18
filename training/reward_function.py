"""
Reward function for adversarial question generation training.
"""

from typing import List, Dict, Any
import re
import openai
import os
import asyncio
import aiohttp
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import wandb
import time
import logging
from functools import lru_cache

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Cache for OpenAI client to avoid recreating it
_openai_client = None

@lru_cache(maxsize=1000)
def _cached_template_render(evidence: str, question: str, template_path: str) -> str:
    """Cache template rendering to avoid repeated file I/O."""
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    return template.render(evidence=evidence, question=question)

def _get_openai_client():
    """Get or create OpenAI client with connection pooling."""
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=30,  # 30 second timeout
            max_retries=3  # Retry failed requests
        )
    return _openai_client

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
    start_time = time.time()
    
    logger.info(f"Processing {len(completions)} completions for reward calculation")
    
    for i, completion in enumerate(completions):
        try:
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
                logger.debug(f"Q: {question}")
                logger.debug(f"     No misdirection tags | R=0.0")
                rewards.append(0.0)
                continue
            
            logger.debug(f"Q: {question}")
            logger.debug(f"     Misdirection: {misdirection}")
            
            # Create the misleading question by appending misdirection
            misleading_question = f"{question} {misdirection}"
            
            # Use LLM to evaluate the misleading question with timeout
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
            
            logger.debug(f"     {result}: LLM={llm_answer} | Truth={correct_answer} | R={correctness_reward:.1f}")
            rewards.append(float(correctness_reward))
            
        except Exception as e:
            logger.error(f"Error processing completion {i}: {e}")
            rewards.append(0.0)  # Default to 0 reward on error
    
    processing_time = time.time() - start_time
    logger.info(f"Reward calculation completed in {processing_time:.2f}s")
    
    # Log reward metrics to wandb
    if len(rewards) > 0 and wandb.run is not None:
        import numpy as np
        success_count = sum(1 for r in rewards if r > 0.5)
        success_rate = success_count / len(rewards)
        
        wandb.log({
            "reward/mean": np.mean(rewards),
            "reward/std": np.std(rewards),
            "reward/min": np.min(rewards),
            "reward/max": np.max(rewards),
            "reward/success_rate": success_rate,
            "reward/success_count": success_count,
            "reward/total_completions": len(rewards),
        })
    
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


def evaluate_question_with_llm(question: str, evidence: str, max_retries: int = 3) -> str:
    """
    Use OpenAI API to answer the question given the evidence with retry logic.
    """
    # Get template path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(current_dir, "prompts", "hotpotqa_prompt.j2")
    
    for attempt in range(max_retries):
        try:
            # Use cached template rendering
            prompt = _cached_template_render(evidence, question, template_path)
            
            # Get OpenAI client
            client = _get_openai_client()
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided evidence. Give a direct, concise answer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"OpenAI API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"All {max_retries} attempts failed for OpenAI API call")
                return "error"


