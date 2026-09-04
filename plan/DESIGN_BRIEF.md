# Design brief: Loki -> AgentWild (NeurIPS 2026 Third Workshop on Agents in the Wild) v0, for review

Deadline: **Sept 5 2026 AoE** (= Sept 6 ~05:00 PDT, ~34h from now). Two tracks: Regular (9 pp) or **Short (4 pp)**, refs/appendix free. Any NeurIPS/ICLR/ICML template. Non-archival, double-blind (code links too). Must be "primarily related to AI agents" or desk-reject. LLM policy: NeurIPS 2026 main-track handbook (AI assistance ok, primarily human-authored).

## What the workshop wants (scanned all 3 editions)
Scope bullets: agent safety/alignment/control; **agent security, attack surfaces, defenses (prompt injection, tool/skill misuse, adversarial manipulation)**; privacy/**robustness/factuality**; agentic interpretability; **evaluation and benchmarking**; post-training; computer-use agents; multi-agent; emerging capabilities (autonomous research, co-work); governance.
Contributed talks selected at ICLR/ICML editions: "Mind the Gap: model- vs agentic-level vulnerabilities with action graphs", "Visual Exclusivity Attacks: multimodal red teaming via agentic planning", "OS-Sentinel", "LinuxArena: control setting in live prod software", "Remote Control: AI control with user actions", "AF-ARENA: alignment faking eval", "WARD: robust defense of web agents vs prompt injection", "Your Cursor is Not Secure: CLI agent TTPs". Pattern: **concrete threat model + realistic environment + measured ASR, or a defense with a security/utility tradeoff**. Organizers: Chenguang Wang (UCSC/Scale), Dawn Song lineage (Berkeley RDI), Bo Li. Invited: Bengio, Song, Bo Li, Zifan Wang, Eric Wallace earlier. Security-flavored, benchmark-loving crowd. Best-paper awards exist.

## What exists (Loki repo, unchanged)
- GRPO attacker policy (Qwen2.5-0.5B/1.5B) that emits `<reasoning>..</reasoning><misdirection>..</misdirection>`.
- Misdirection = **fabricated authoritative context**: fake laws, fake reports, fake dates/orgs, stated as fact. NOT "ignore previous instructions". Templates for HotpotQA (make QA target answer wrong while evidence still supports the truth), JailbreakBench/HarmBench (make target comply by citing fake policy that permits it), MathQA.
- Rewards: heuristic (format/length/keywords), "frozen target got fooled" (LLM-as-judge via Ollama or OpenAI), fallback heuristics.
- TRL GRPOTrainer configs, SFT trainer, RunPod deploy, wandb.

## Prior work that boxes us in (verified arxiv ids)
- PISmith 2603.13026 (COLM 2026): GRPO red-teaming of prompt-injection defenses, entropy tricks for sparse reward, evaluated on InjecAgent + AgentDojo. Closest.
- Learning to Inject 2602.05746: RL-automated prompt injection.
- PIMiner 2608.05108: agentic red-teaming with transferable strategy library.
- RETA 2606.15441, SecOPD 2608.21500, IH-Challenge 2603.10521: defenses trained against RL attackers.
- Benchmarks: AgentDojo 2406.13352, InjecAgent 2403.02691, WASP 2504.18575, ASB. "Firewalls all you need?" 2510.05244 says these are saturated by simple defenses and attacks are weak.
- ChatInject 2509.22830 (ICLR 2026).
All of these attack via **instruction hijack** (make agent do attacker's task). None target **belief poisoning**: agent still does the user's task, but does it *wrong* because retrieved/tool content contains fabricated authoritative facts. That is Loki's native attack class, and it maps to CFP bullets "factuality", "robustness", "tool misuse", "autonomous research / scientific discovery".

## Converged design (proposal to critique)

Working title: **"Convincing, not Commanding: RL-trained fabricated-authority injections degrade agent factuality without triggering injection defenses."**

Threat model: attacker controls one document/tool result the agent will read (web page, retrieved doc, email, file in repo). Attacker goal is NOT hijack. Goal is that the agent completes the user's task with a wrong answer/action that the attacker chose, by planting a plausible fabricated authority claim. Injection-detection defenses (firewalls, CommandSans-style instruction stripping, IH training) look for *instructions*; a fabricated fact contains none.

Contributions (4-page short paper):
1. **Attack class + attacker.** Loki's GRPO misdirection policy, reused verbatim, retargeted from "fool a QA model" to "fool an agent reading a tool result". Reward = target agent's final answer/action matches attacker's wrong target, minus a detectability penalty (a prompt-injection classifier / instruction-stripper must NOT flag or strip the injection). This is the existing reward with one term added.
2. **Environment.** Reuse AgentDojo (or InjecAgent) tasks but change the injection goal type: instead of "send money to attacker", plant "the correct recipient IBAN was updated to X per Bank Policy 2024-17" in a retrieved document. Measure (a) task-completion (agent thinks it succeeded), (b) attacker-goal success, (c) defense flag rate. Plus a HotpotQA/FEVER-style "research agent" env built from Loki's existing dataset builders: agent with a search tool, one poisoned result.
3. **Finding to sell.** Fabricated-authority injections achieve X% attacker-goal success at Y% defense flag rate vs Z% for instruction-style injections (PISmith / AgentDojo "important message" attacks) under the same defenses. Transfer across target models (Qwen 0.5B-trained attacker vs GPT-4o-mini / Claude Haiku / Llama targets). Ablation: which fabricated-authority features get learned (fake regulation numbers, dates, org names), interpretability histogram.
4. Optional defense probe: does a "fact-check the tool result against the user's original context" step recover accuracy, and at what utility cost.

## Compute
1x A100. Attacker: Qwen2.5-1.5B GRPO, num_generations 8, ≤128 tok, 500-1000 steps. Targets: local Llama-3.1-8B / Qwen2.5-7B via vLLM + API models for transfer table. AgentDojo runs on CPU/API.

## Questions for reviewers
1. Is "belief poisoning vs instruction hijack" a real, defensible distinction, or will reviewers say it is just indirect prompt injection with a different payload? What is the one experiment that proves it is different (e.g. defenses that stop hijack do not stop this)?
2. Biggest 34h risk.
3. Cut one, add one.
4. Must-cite list, and which prior work already does exactly this (if any, say so bluntly).
5. Short (4pp) or regular (9pp)?

## ADDENDUM (found after v0): knowledge poisoning already exists, sharpen or die
- PoisonedRAG 2402.07867 (USENIX Sec 2025): optimized malicious texts in RAG DB -> attacker-chosen answer, 90% ASR with 5 docs.
- **AgentPoison 2407.12784 (Chen, Xiang, Xiao, Dawn Song, Bo Li)**: backdoor via poisoned memory/KB for RAG agents. Song and Li are organizers/speakers at THIS workshop. Must cite, must position against.
- CorruptRAG-AK / "Architecture Matters" 2605.05632: adversarial *framing* (meta-epistemic credibility cues) drives ASR more than retrieval optimization; ASR 82% vanilla -> 24% RLM.
- Poisoned Playbooks 2606.24402: single poisoned write-up alters CTF security agents; introduces "Verification Boundary" (what evidence the agent can use to refute a claim).
- MemoryGraft 2512.16962, Cordon-MAS 2605.26754 (info-flow defense), Trustworthy RAG 2608.21095 (detector; notes "in-place edits / entity swaps remain hard to detect").
So "belief poisoning of agents" is known. What is still open and what Loki uniquely has:
(a) the poison is **RL-learned fabricated authority** (fake regulation numbers, dates, orgs) rather than hand-written or GCG-optimized text; CorruptRAG says framing matters most, we learn the framing;
(b) **evasion of instruction-based defenses** as an explicit reward term (detectability penalty), which none of the above optimize for;
(c) **action-taking agents on AgentDojo**, not QA accuracy;
(d) a **transfer table**: attacker trained against small local target, tested on frontier API agents.
Council: re-answer Q1 in light of this. Is (a)+(b)+(c) enough novelty for a 4-page short paper, or is there a sharper angle (e.g. measure which fabricated-authority *features* transfer across targets, or the Verification-Boundary framing: agents fall for poison exactly when they cannot refute it, so give the attacker a reward for staying inside the unverifiable zone)?
- AgentDojo 0.1.35 installs clean locally (verified).
