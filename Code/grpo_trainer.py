#reward system

# # train_grpo.py
# from datasets import load_dataset
# from trl import GRPOConfig, GRPOTrainer

# dataset = load_dataset("trl-lib/ultrafeedback-prompt", split="train")

# # Dummy reward function for demonstration purposes
# def reward_num_unique_letters(completions, **kwargs):
#     """Reward function that rewards completions with more unique letters."""
#     completion_contents = [completion[0]["content"] for completion in completions]
#     return [float(len(set(content))) for content in completion_contents]

# training_args = GRPOConfig(output_dir="Qwen2-0.5B-GRPO")
# trainer = GRPOTrainer(
#     model="Qwen/Qwen2-0.5B-Instruct",
#     reward_funcs=reward_num_unique_letters,
#     args=training_args,
#     train_dataset=dataset,
# )
# trainer.train()