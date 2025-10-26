"""
Quick test script to verify HarmBench setup is working correctly.
Run this before the full training to catch issues early.
"""

import sys
import os

# Add scripts and training to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("HARMBENCH SETUP TEST")
print("=" * 80)

# Test 1: Import HarmBench dataset creator
print("\n[1/4] Testing HarmBench dataset import...")
try:
    from scripts.harmbench import create_harmbench_dataset
    print("✓ HarmBench module imported successfully")
except Exception as e:
    print(f"✗ Failed to import HarmBench module: {e}")
    sys.exit(1)

# Test 2: Load a small sample
print("\n[2/4] Testing dataset loading...")
try:
    dataset = create_harmbench_dataset(num_samples=2, save=False)
    print(f"✓ Loaded {len(dataset)} examples from HarmBench")
    
    # Show first example
    example = dataset[0]
    print(f"  Example 1: {example.get('behavior', 'N/A')[:60]}...")
    print(f"    Category: {example.get('semantic_category', 'N/A')}")
    print(f"    Has prompt: {example.get('prompt') is not None}")
    
except Exception as e:
    print(f"✗ Failed to load dataset: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check reward function
print("\n[3/4] Testing reward function import...")
try:
    from training.harmbench_reward_function import harmbench_reward_function
    print("✓ Reward function imported successfully")
except Exception as e:
    print(f"✗ Failed to import reward function: {e}")
    print("  (This is okay if you haven't installed openai yet)")
    import traceback
    traceback.print_exc()

# Test 4: Check transformers/tokenizer
print("\n[4/4] Testing transformers library...")
try:
    from transformers import AutoTokenizer
    print("✓ Transformers library available")
    
    # Test loading a small tokenizer
    print("  Testing tokenizer load...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    print("✓ Tokenizer loaded successfully")
    
except Exception as e:
    print(f"⚠ Transformers issue: {e}")
    print("  You may need to: pip install transformers")

print("\n" + "=" * 80)
print("SETUP TEST COMPLETE")
print("=" * 80)
print("\n✓ All core components verified!")
print("\nNext steps:")
print("  1. Install OpenAI: pip install openai python-dotenv")
print("  2. Create .env file with OPENAI_API_KEY")
print("  3. Run: python training/harmbench_trainer.py")
print("\nOr check HARMBENCH_TRAINING_GUIDE.md for detailed instructions")

