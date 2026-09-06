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
from concurrent.futures import ThreadPoolExecutor
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
    split: str
    judge_backend: str


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


def generate_misdirections(
    model_path: str,
    dataset,
    max_new_tokens: int,
    device: str,
    batch_size: int = 8,
):
    """Generate one misdirection per behavior.

    Batched with left padding: one-at-a-time generation made a 120-sample eval
    take over an hour on CPU, which was the pipeline's main bottleneck.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    # Decoder-only models must be left-padded, or the generated continuation
    # starts after the pad run and the output is garbage.
    tokenizer.padding_side = "left"

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.float32 if device == "cpu" else torch.bfloat16,
    ).to(device)
    model.eval()

    prompts = [
        tokenizer.apply_chat_template(
            record["prompt"], tokenize=False, add_generation_prompt=True
        )
        for record in dataset
    ]

    outputs: list[str] = []
    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        inputs = tokenizer(
            chunk,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=1024,
        )
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
        prompt_len = inputs["input_ids"].shape[-1]
        for row in generated:
            text = tokenizer.decode(row[prompt_len:], skip_special_tokens=True)
            outputs.append(text.strip())
        logger.info("  generated %d/%d", len(outputs), len(prompts))
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
    split: str = "test",
    judge_backend: str | None = None,
    concurrency: int = 8,
    batch_size: int = 8,
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

    dataset = create_harmbench_dataset(
        num_samples=num_samples, seed=seed, split=split
    )
    completions = generate_misdirections(
        model_path, dataset, max_new_tokens, device, batch_size=batch_size
    )

    # Target and judge are chosen independently: attack a free local model while
    # judging with a validated one. llama3.2 as a judge was measured at 36%
    # accuracy with 27 false positives, inflating ASR by 3-4x.
    target = build_target(reward_backend, judge_model)
    jb = judge_backend or reward_backend
    judge = build_judge(jb, "gpt-4o-mini" if jb == "openai" else judge_model)

    outcomes: list[float] = []
    records = []
    n_well_formed = 0
    n_tag_compliant = 0

    # Build the row skeletons first, then run the network-bound target and judge
    # calls concurrently. These are I/O bound, so serial execution wasted most
    # of the wall clock.
    pending: list[tuple[int, str, str]] = []
    for index, (record, completion) in enumerate(
        zip(dataset, completions, strict=False)
    ):
        behavior = record["behavior"]
        misdirection = extract_misdirection(completion)
        tagged = is_well_formed(completion)
        records.append(
            {
                "behavior_id": record["behavior_id"],
                "behavior": behavior,
                "completion": completion,
                "misdirection": misdirection,
                "well_formed": bool(misdirection),
                "tag_compliant": tagged,
            }
        )
        if misdirection:
            n_well_formed += 1
            n_tag_compliant += int(tagged)
            pending.append((index, behavior, misdirection))

    def attack_and_judge(item):
        index, behavior, misdirection = item
        response = target.respond(f"{behavior} {misdirection}")
        if not response:
            return index, None
        return index, (response, judge.judge(behavior, response))

    if pending:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            for done, (index, outcome) in enumerate(
                pool.map(attack_and_judge, pending), start=1
            ):
                if outcome is None:
                    continue
                response, judgement = outcome
                if judgement.errored:
                    continue
                outcomes.append(judgement.score)
                records[index].update(
                    target_response=response,
                    refused=judgement.refused,
                    score=judgement.score,
                )
                if done % 20 == 0:
                    logger.info("  judged %d/%d", done, len(pending))

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
        split=split,
        judge_backend=jb,
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
    parser.add_argument(
        "--judge-backend",
        default=None,
        choices=["heuristic", "ollama", "openai"],
        help="judge independently of the target; defaults to --reward-backend",
    )
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "mps"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--out", default=None)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=8)
    parser.add_argument(
        "--split",
        default="test",
        choices=["all", "train", "test"],
        help="evaluate on the held-out test split by default",
    )
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
        args.split,
        args.judge_backend,
        args.concurrency,
        args.batch_size,
    )

    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
