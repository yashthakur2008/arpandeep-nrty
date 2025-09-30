from datasets import load_dataset

# Login using e.g. `huggingface-cli login` to access this dataset
ds = load_dataset("hotpotqa/hotpot_qa", "distractor")

# Save the train split to JSON Lines (.jsonl)
ds["train"].to_json("hotpotqa_distractor_train.jsonl")

# Save the validation split to JSON Lines
ds["validation"].to_json("hotpotqa_distractor_val.jsonl")