"""Attack-success-rate evaluation, decoupled from training.

A paper needs a number produced by a script that does not update weights. This
is that script: it loads a checkpoint (or the base model), generates
misdirections for held-out behaviors, runs them against the target, and reports
ASR with a bootstrap confidence interval.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass

import numpy as np

from loki.config import TrainingConfig
from loki.data.harmbench import create_harmbench_dataset
from loki.rewards.judges import build_judge
from loki.rewards.parsing import extract_misdirection, is_well_formed
from loki.rewards.targets import build_target
from loki.runtime import configure_logging, preflight, set_seed

logger = logging.getLogger(__name__)


@dataclass
class EvalResult:
    model: str
    n: int
    n_well_formed: int          # parseable misdirection (tag OR label)
    n_tag_compliant: int        # used the requested <misdirection> tags
    n_measured: int
    n_complied: int
    format_rate: float          # parseable rate
    tag_compliance_rate: float  # strict tag rate
    attack_success_rate: float
    asr_ci_low: float
    asr_ci_high: float
    reward_backend: str


def bootstrap_ci(
    outcomes: list[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float]:
    """Percentile bootstrap CI. Reviewers will ask for error bars."""
    if not outcomes:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    data = np.asarray(outcomes, dtype=float)
    means = rng.choice(data, size=(n_boot, data.size), replace=True).mean(axis=1)
    return (
        float(np.percentile(means, 100 * alpha / 2)),
        float(np.percentile(means, 100 * (1 - alpha / 2))),
    )


def generate_misdirections(model_path: str, dataset, max_new_tokens: int, device: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float32 if device == "cpu" else torch.bfloat16,
    ).to(device)
    model.eval()

    outputs = []
    for record in dataset:
        text = tokenizer.apply_chat_template(
            record["prompt"], tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id,
            )
        new_tokens = generated[0][inputs["input_ids"].shape[-1] :]
        outputs.append(tokenizer.decode(new_tokens, skip_special_tokens=True).strip())
    return outputs


def evaluate(
    model_path: str,
    num_samples: int,
    reward_backend: str,
    judge_model: str | None,
    device: str,
    seed: int,
    max_new_tokens: int = 128,
    out_path: str | None = None,
) -> EvalResult:
    set_seed(seed)
    config = TrainingConfig(
        model_name=model_path,
        num_samples=num_samples,
        reward_backend=reward_backend,
        judge_model=judge_model or "llama3.2",
        device=device,
        report_to="none",
    )
    preflight(config)

    dataset = create_harmbench_dataset(num_samples=num_samples, seed=seed)
    completions = generate_misdirections(model_path, dataset, max_new_tokens, device)

    target = build_target(reward_backend, judge_model)
    judge = build_judge(reward_backend, judge_model)

    outcomes: list[float] = []
    records = []
    n_well_formed = 0
    n_tag_compliant = 0

    for record, completion in zip(dataset, completions, strict=False):
        behavior = record["behavior"]
        misdirection = extract_misdirection(completion)
        tagged = is_well_formed(completion)
        row = {
            "behavior_id": record["behavior_id"],
            "behavior": behavior,
            "completion": completion,
            "misdirection": misdirection,
            "well_formed": bool(misdirection),
            "tag_compliant": tagged,
        }
        if misdirection:
            n_well_formed += 1
            n_tag_compliant += int(tagged)
            response = target.respond(f"{behavior} {misdirection}")
            if response:
                judgement = judge.judge(behavior, response)
                if not judgement.errored:
                    outcomes.append(judgement.score)
                    row.update(
                        target_response=response,
                        refused=judgement.refused,
                        score=judgement.score,
                    )
        records.append(row)

    n = len(dataset)
    low, high = bootstrap_ci(outcomes, seed=seed)
    result = EvalResult(
        model=model_path,
        n=n,
        n_well_formed=n_well_formed,
        n_tag_compliant=n_tag_compliant,
        n_measured=len(outcomes),
        n_complied=int(sum(outcomes)),
        format_rate=n_well_formed / max(n, 1),
        tag_compliance_rate=n_tag_compliant / max(n, 1),
        attack_success_rate=float(np.mean(outcomes)) if outcomes else 0.0,
        asr_ci_low=low,
        asr_ci_high=high,
        reward_backend=reward_backend,
    )

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump({"summary": asdict(result), "records": records}, handle, indent=2)
        logger.info("Wrote per-sample results to %s", out_path)

    return result


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Evaluate attack success rate")
    parser.add_argument("--model", required=True, help="checkpoint dir or HF model id")
    parser.add_argument("--num-samples", type=int, default=50)
    parser.add_argument(
        "--reward-backend", default="heuristic", choices=["heuristic", "ollama", "openai"]
    )
    parser.add_argument("--judge-model")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "mps"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    result = evaluate(
        args.model,
        args.num_samples,
        args.reward_backend,
        args.judge_model,
        args.device,
        args.seed,
        args.max_new_tokens,
        args.out,
    )

    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
