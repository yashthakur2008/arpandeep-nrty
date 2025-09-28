from datasets import load_dataset

ds = load_dataset("sewon/ambig_qa", "light")

ds["train"].to_json("ambig_qa_light_train.json")