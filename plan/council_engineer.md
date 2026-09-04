# Council: engineer (feasibility, 34h)

Verdict: feasible only if the RL env is single-call, not AgentDojo. AgentDojo is eval-only. P(submit a real paper) ~70% on this plan, ~30% on the brief as written.

## Stage by stage

**1. Env selection (2h).** InjecAgent: skip, it is a "did the agent call attacker's tool" single-step check, belief poisoning does not fit. AgentDojo: every security case is a 5-15 call agent run (30-90s with an API model, more with local vLLM). Reward for GRPO through it is 64 agent runs/step = 30+ min/step sequential, ~2 min/step at 32-way concurrency. That kills training. Use it only as an eval bed, 20-30 hand-picked banking/travel/slack cases where the belief-poisoning goal is checkable by existing task args (IBAN swap on `send_money`, wrong hotel, wrong date). Train on a homegrown research env from Loki's HotpotQA builders: agent gets a question + 2 retrieved docs (1 truthful, 1 attacker-controlled), answers in one call. Reward = exact/contains match on attacker's wrong target answer (no LLM judge), minus Prompt Guard 2 (86M) or ProtectAI deberta-v3 injection score. Break: template injections already get >60% ASR on the 7B target so RL has nothing to learn; or <5% so reward is all zeros. Fix: measure template ASR in the first hour, swap target size (3B vs 7B) to land in 15-40%.

**2. Attacker GRPO (6h wall, 2 human).** Qwen2.5-1.5B full FT bf16, 8-bit Adam, lr 1e-6, beta 0.04, num_generations 8, per_device_batch 8 prompts (64 completions/step), max_completion 128, 300 steps. Target Qwen2.5-7B on vLLM co-located, gpu_memory_utilization 0.35, batched 64 reward calls in ~10-20s. Step time ~40-60s, 300 steps = 3-5h. Break: format collapse or reward hack (policy just emits the wrong answer with no fabricated authority). Fix: keep Loki's format reward, add 0.2 bonus for containing a regulation-like token (year, org, policy number) only if ASR reward > 0. Kill-switch: if step time > 3 min after the 20-step smoke run, drop to num_generations 4 or use gpt-4o-mini as reward target with 32 async calls.

**3. Detectability penalty (1h).** Prompt Guard 2 batched, one line in reward. Baseline: AgentDojo `important_message` attack should flag ~80-95%; templates ~5-15%. If templates already flag <5%, the penalty is inert and becomes an eval column only. Fine.

**4. Transfer table (3h wall).** 3 API targets x 200 cases x 3 attacks = 1800 runs. Research env (~2k in / 200 out tokens): gpt-4o-mini ~$1, Claude Haiku 4.5 ~$6, gpt-4o ~$13. Total under $20. If done in AgentDojo instead (~15k tokens, 5 calls/case): 4o-mini ~$6, Haiku ~$40, 4o ~$90, ~$140 total, 45-60 min at 20-way concurrency. Break: rate limits. Fix: asyncio semaphore 16, retries, resumable jsonl.

**4b. Baselines from addendum (1.5h, do it).** PoisonedRAG's black-box generator is one GPT call per case ("write text so Q is answered T"), 200 cases ~$1, drop-in as a 4th attack column. AgentPoison needs trigger optimization over embedding gradients plus a memory-retrieval agent; that is a day, not an hour. Cite it, borrow only its released poisoned examples if the format fits, do not re-run. Skipping both is a desk-kill with Song/Li reviewers.

**5. Defense probe (1.5h, first to drop).** One extra prompt "verify claims in tool result against user context" on the local target only, report ASR delta and refusal/utility delta on 100 clean tasks.

**6. Paper (8h).** 4 pages, NeurIPS template. Skeleton must exist by H18 regardless of results.

## Schedule (H0 = Sept 4 12:00 PDT, deadline Sept 6 05:00 PDT, target submit H32)

- H0-2: research env, template injections, classifier, vLLM target up. Measure template ASR and flag rate. Kill: if ASR outside 15-40%, change target model, do not touch RL.
- H2-4: GRPO plumbing, 20-step smoke. Kill: step > 3 min, see fix above.
- H4-9: 300-step run in background. Sleep 4h here. Also queue AgentDojo eval harness (20 cases, belief-poisoning variants).
- H9-12: eval on local target, 4 attack types x {ASR, task-completion, flag rate}. This is Figure 1. Kill: if RL attacker does not beat templates, paper becomes "templates suffice", still submittable.
- H12-15: transfer table via API (now 4 attacks incl. PoisonedRAG), backgrounded. Write paper intro/threat model in parallel.
- H15-17: AgentDojo eval (20 cases x 3 attacks x 1 local + 1 API target).
- H17-18: ablation histogram, regex over 500 generations.
- H18-26: write. Results section fills from jsonl. Defense probe only if H17 finished on time.
- H26-30: figures, refs, anonymize, page check.
- H30-32: submit. 2h buffer, do not spend it on new experiments.

## Drop order
1. Defense probe. 2. AgentDojo eval (keep research env only, say so). 3. Ablation histogram. 4. Third API target. 5. RL attacker (report template-only belief poisoning vs instruction hijack under defenses; still a paper, weaker).

Most likely failure: 4h lost porting AgentDojo before the research env exists. Research env first.
