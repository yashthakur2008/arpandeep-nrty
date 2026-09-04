# Annotated bibliography: "Convincing, not Commanding" (AgentWild @ NeurIPS 2026)

Written 2026-09-04. Sources: 27 Consensus queries (Semantic Scholar / arXiv index) plus arXiv API verification of every 2026 id. Citation counts are Consensus/Semantic Scholar snapshots on 2026-09-04 and will drift. Every arXiv id below was resolved by `export.arxiv.org/api/query?id_list=` or returned by Consensus with a `10.48550/arxiv.*` DOI. No ⚠️ entries remain; every id resolved.

Legend for **Cite in**: intro / threat / related / method / results / discussion.

Design recap the relevance lines refer to: attacker writes one tool result, no imperatives, agent completes user task with attacker-chosen wrong answer/action. Table 1 = payload families (A hijack, B fabricated authority, H hybrid) x defenses (none, stripper, spotlighting, PromptGuard, IH-trained target, verifier). Reward for B3/B4 = fooled − PG2 score − refuter success.

---

## A. Organizer / reviewer-lineage papers (cite in paragraph one of related work)

### A1. AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases
Zhaorun Chen, Zhen Xiang, Chaowei Xiao, Dawn Song, Bo Li. 2024. NeurIPS 2024. arXiv:2407.12784. ~456 citations.
Backdoor attack on RAG/memory-based agents: optimizes a trigger phrase so that user queries containing it retrieve attacker-planted demonstrations from the poisoned KB with high probability, while benign queries are unaffected. Trigger optimization is a constrained embedding-space objective, no model training. >80% ASR on driving, EHR, and QA agents with <0.1% poison rate and <1% benign degradation.
**Relevance:** Organizer paper (Song, Li). Must be first citation. Position against on three axes: (i) they need a trigger in the *user query*, we need none; (ii) they need a write to persistent memory/KB, we need one transient tool result; (iii) they poison with *demonstrations* (procedural), we poison with *facts* (declarative), and they never evaluate against instruction-channel defenses. Do not re-run.
**Cite in:** intro, related (para 1), threat.

### A2. AdvWeb: Controllable Black-box Attacks on VLM-powered Web Agents (a.k.a. AdvAgent)
Chejian Xu, Mintong Kang, Jiawei Zhang, Zeyi Liao, Lingbo Mo, Mengqi Yuan, Huan Sun, Bo Li. 2024. arXiv:2410.17401 (v2 retitled "AdvAgent: Controllable Blackbox Red-teaming on Web Agents"). ~42-48 citations across the two titles.
Trains an adversarial prompter LM with DPO on black-box feedback from a GPT-4 web agent. Injected strings are hidden in HTML and flip a single action (wrong recipient, wrong amount) while the rest of the user task proceeds. Reports stealth and controllability, and that prompt-based defenses give limited protection.
**Relevance:** Organizer paper (Li). Closest "learned attacker, wrong action, task otherwise unchanged" prior. Position: their payloads are still instruction-shaped (they target the control channel via the agent's action parser); ours contain no instruction by construction (stripper-identity filter). They report against prompt defenses only; we report against six including a verifier. Their DPO vs our GRPO is not the contribution and should not be framed as one.
**Cite in:** intro, related (para 1), method (learned attacker lineage).

### A3. PromptArmor: Simple yet Effective Prompt Injection Defenses
Tianneng Shi, Kaijie Zhu, Zhun Wang, Yuqi Jia, Will Cai, Weida Liang, Haihui Wang, Hongwei Li, Fengjun Zhou, ... Dawn Song. 2025. arXiv:2507.15219. ~118 citations.
Prompts an off-the-shelf LLM (GPT-4o / o4-mini) to detect and *remove* injected prompts from tool output before the agent sees it. <1% FPR and FNR on AgentDojo; ASR after removal <1%. Recommended as the standard defense baseline.
**Relevance:** Organizer paper (Shi is an AgentWild organizer). Gives us a 7th defense column if budget allows (one API call per tool result). Prediction: PromptArmor removes A rows and passes B rows because a fabricated regulation is "relevant data," not "an injected prompt." If it removes B rows too, that is a result and belongs in the discussion. Cite as the strongest detector-remover we test.
**Cite in:** related (para 2), method (defense list), results.

### A4. AutoDojo: Adaptive Black-Box Attacks Reveal the Limits of IPI Defenses and Task-Specification Effects in LLM Agents
Xinhang Ma, Taoran Li, Chaowei Xiao, Zhiyuan Yu, Ning Zhang, Yevgeniy Vorobeychik. 2026. arXiv:2606.15057. ~4 citations.
Adaptive extension of AgentDojo: a frontier LLM iteratively rewrites the injection against a given defense. Recovers 28% ASR against a filter that zeroes static ASR. Key second finding: on *action-open* tasks (user delegates the action choice to retrieved content) ASR is much higher because "the injection can pose as ordinary data rather than an explicit instruction, bypassing defenses that rely on detecting instruction-like text."
**Relevance:** Xiao (AgentPoison coauthor) lineage. This sentence is our thesis stated as a side observation. Pre-empts the objection "you just found action-open tasks." Our answer: we make the data-posing payload *the whole attack*, enforce it with a stripper filter, learn it, and add the verification-boundary axis they lack. Cite and quote.
**Cite in:** intro, related (para 1), discussion.

---

## B. Learned / RL prompt-injection attackers (closest methodology)

### B1. PISmith: Reinforcement Learning-based Red Teaming for Prompt Injection Defenses
Chenlong Yin, Yanting Wang, ..., Jinyuan Jia. 2026. COLM 2026. arXiv:2603.13026. ~13 citations.
GRPO-trains a black-box attacker LM against defended targets. Finds vanilla GRPO collapses under reward sparsity (most injections blocked) and adds adaptive entropy regularization plus dynamic advantage weighting. Beats 7 baselines on 13 benchmarks; works on InjecAgent and AgentDojo against GPT-4o-mini and GPT-5-nano.
**Relevance:** The paper a hostile reviewer will say we are. Same trainer (GRPO), same benchmark family. Position: PISmith optimizes *hijack* payloads to survive defenses; the payloads remain instructions. We optimize *facts* under a no-instruction constraint plus a refutability penalty. Row A2 in Table 1 is "PISmith-style RL hijack" (cite if not run). Their entropy trick is relevant if our B3 run collapses; cite in method as the known fix.
**Cite in:** intro, related (para 2), method, results (A2 row).

### B2. RL Is a Hammer and LLMs Are Nails: A Simple Reinforcement Learning Recipe for Strong Prompt Injection (RL-Hammer)
Yuxin Wen, ... (Meta FAIR). 2025. arXiv:2510.04885. ~31 citations.
Trains attackers from scratch with RL; 98% ASR on GPT-4o, 72% on GPT-5 with Instruction Hierarchy. Shows attacker models reward-hack diversity objectives, and that the attacker can be trained to *evade multiple prompt-injection detectors*.
**Relevance:** Prior art for "detector-evasion as a reward term." We must not claim that as novel. Our novelty is the *pairing* of detector-evasion with a no-imperative constraint and a refuter penalty. Also the Goodhart warning (reward-hacked diversity) is our biggest 34h risk; cite when describing the format gate.
**Cite in:** related (para 2), method (reward design), discussion (Goodhart).

### B3. Learning to Inject: Automated Prompt Injection via Reinforcement Learning (AutoInject)
Xin Chen et al. 2026. arXiv:2602.05746. ~6 citations.
Black-box RL learns adversarial *suffixes* for prompt injection with a learned comparison-based reward that densifies the binary success signal. Beats templates, GCG, TAP, and adaptive attacks on AgentDojo; breaks Meta-SecAlign-70B where templates fail.
**Relevance:** Establishes that preference-trained (SecAlign-class) defenses fall to adaptive RL *hijack*. Our IH-trained column is therefore expected to be weak against A2 already; the interesting comparison is A1 (template hijack, which SecAlign blocks) vs B0 (template fact, which we predict SecAlign passes). Cite to justify why the template hijack row, not the RL hijack row, is the fair control.
**Cite in:** related (para 2), results.

### B4. PIMiner: Agent Against Agent: An Agentic System for Automatic Prompt Injection Red Teaming
Yanting Wang, Chenlong Yin, Runpeng Geng, Jinyuan Jia. 2026. arXiv:2608.05108. ~0 citations (Aug 2026).
Replaces RL attackers (which "generalize poorly to new target LLMs") with a strategy-library agent that transfers to unseen targets with ~10 queries. 86.7% ASR vs Gemini-2.5-Pro, 40% vs Claude-Sonnet-4.5 on AgentDojo.
**Relevance:** Pre-empts "why RL at all." Their critique of RL transfer is exactly why we (a) keep RL as one row, (b) freeze a template attacker at H0, and (c) put transfer in the appendix. One sentence in related work.
**Cite in:** related (para 2), discussion.

---

## C. Knowledge poisoning and illusioning (closest threat model)

### C1. PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models
Wei Zou, Runpeng Geng, Binghui Wang, Jinyuan Jia. 2024. USENIX Security 2025. arXiv:2402.07867. ~292 citations.
Formalizes knowledge corruption as an optimization: inject N texts so the LLM answers an attacker-chosen answer to an attacker-chosen question. Black-box variant is a single LLM call ("generate a passage that makes the answer X"). 90% ASR with 5 texts in a million-document corpus. Evaluated defenses (paraphrase, perplexity, duplicate removal, KAD) insufficient.
**Relevance:** Row B2 in Table 1 is literally PoisonedRAG's black-box generator, one GPT call per case. It is our mandatory non-RL baseline. Position: they optimize retrievability plus answer flip on QA; we assume retrieval (one tool result) and optimize framing plus defense evasion on *action* agents. Their number to be compared against: template-vs-generator gap in our env.
**Cite in:** intro, related (para 1), method (baseline), results.

### C2. Practical Poisoning Attacks against Retrieval-Augmented Generation (CorruptRAG, incl. CorruptRAG-AK)
Baolei Zhang, Yuxi Chen, Zhuqing Liu, Lihai Nie, Tong Li, Zheli Liu, Minghong Fang. 2025. ACM SACMAT 2026. arXiv:2504.03957. ~41 citations.
Single-document (N=1) poisoning. Two variants: CorruptRAG-AS (adversarial statement) and CorruptRAG-AK (adversarial knowledge), the latter wrapping the false claim in meta-epistemic credibility cues ("the following was verified by ..."). Beats PoisonedRAG at N=1.
**Relevance:** CorruptRAG-AK is the hand-written ancestor of our B0 templates. Exact positioning sentence: "CorruptRAG-AK hand-writes credibility framing; we learn it under an instruction-stripper constraint and a refuter penalty, and measure it on action agents under six defenses." If B0 already beats every defense, the paper is "CorruptRAG-AK on AgentDojo" and must say so honestly.
**Cite in:** intro, related (para 1), method (template design).

### C3. Architecture Matters: Comparing RAG Systems under Knowledge Base Poisoning
Samuel Korn. 2026. arXiv:2605.05632. ~1 citation.
Runs CorruptRAG-AK against vanilla, agentic, MADAM-RAG, and Recursive LM architectures on 921 NQ pairs. ASR ranges 81.9% (vanilla) to 24.4% (RLM). Decomposition shows *adversarial framing, not retrieval optimization*, drives most of the advantage for three of four architectures, localizing the vulnerability at the content-reasoning stage.
**Relevance:** Independent evidence that framing is the load-bearing variable, which is the premise of learning framing. Also our closest "defense-architecture table" precedent; our table swaps RAG architectures for injection defenses. Their 82% -> 24% spread is the kind of number our verifier column should produce.
**Cite in:** intro, related (para 1), discussion.

### C4. Poisoned Playbooks: Demystifying Knowledge Poisoning Effects on AI Security Agents
Juho Park, Hyunmin Choi, Kevin Nam. 2026. arXiv:2606.24402. ~0 citations.
One poisoned write-up injected into public-style security knowledge alters RAG-based CTF/CVE agents across 11 challenges, 3 model families, 11 CVEs. Introduces the **Verification Boundary (VB)**, a 3-level classification by what evidence the agent can use to refute a retrieved claim. Verification prompting and multi-source retrieval help only when stronger evidence exists; both weaken under sparse-evidence and zero-day conditions.
**Relevance:** Source of our mechanism vocabulary. They name the boundary and hand-write poisons; we reward the attacker for *staying outside* it (B4 refuter penalty). Their "verification prompting helps only when evidence exists" is the prediction for our verifier column. Adopt their term verbatim, cite on first use, do not rename.
**Cite in:** intro, threat, method (B4 reward), discussion.

### C5. Dissecting Adversarial Robustness of Multimodal LM Agents
Chen Henry Wu, Rishi Shah, Jing Yu Koh, Ruslan Salakhutdinov, Daniel Fried, Aditi Raghunathan. 2024. ICLR 2025. arXiv:2406.12814. ~122 citations.
200 targeted adversarial tasks on VisualWebArena; Agent Robustness Evaluation views the agent as a graph of components. Defines two attack goals: **illusioning** (agent believes a false environment state and does the user's task wrong) and **goal misdirection** (agent pursues attacker's goal). Image perturbations under 5% of pixels hijack frontier agents up to 67%.
**Relevance:** The terminology. Our attack is text illusioning; hijack rows are goal misdirection. Use their words in the title and threat model; a reviewer from that lab will check. Position: they illusion via pixels, we via fabricated authority in text, and we test defense stacks they do not.
**Cite in:** title footnote, intro, threat, related (para 1).

### C6. On the Risk of Misinformation Pollution with Large Language Models
Yikang Pan, Liangming Pan, Wenhu Chen, Preslav Nakov, Min-Yen Kan, William Yang Wang. 2023. EMNLP Findings 2023. arXiv:2305.13661. ~220 citations.
LLM-generated misinformation injected into the retrieval corpus degrades ODQA accuracy sharply. Tests prompting, misinformation detection, and majority voting as defenses; all partial.
**Relevance:** Our HotpotQA research env is a descendant. Cite once to show the QA-level effect is known and that our contribution is the agent-plus-defenses layer. Their majority-voting defense is the ancestor of RobustRAG.
**Cite in:** related (para 1).

### C7. Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection
Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, Mario Fritz. 2023. AISec 2023. arXiv:2302.12173. ~1842 citations.
Coins indirect prompt injection; taxonomy from a security perspective including data theft, worming, and **information ecosystem contamination / misinformation** as goal classes. Demonstrates on Bing Chat.
**Relevance:** Their taxonomy already lists misinformation as an IPI goal. Cite to concede the goal class is old; our claim is about *which defense family is structurally blind to it*, not that the goal is new.
**Cite in:** intro (first sentence), related (para 1).

---

## D. Benchmarks and environments

### D1. AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents
Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, Florian Tramèr. 2024. NeurIPS 2024 D&B. arXiv:2406.13352. ~145 citations.
97 tasks, 629 security cases across banking/slack/travel/workspace; extensible attacks (`important_message`, `tool_knowledge`) and defenses (`tool_filter`, `spotlighting_with_delimiting`, `repeat_user_prompt`, `transformers_pi_detector`). Reports utility, ASR, utility-under-attack.
**Relevance:** Our eval bed (25 matched cases). We inherit their metrics, their `important_message` payload as row A1, and their two prompt-level defenses as columns. A0 utility must match their published number for the target model within 10 points (N4 sanity check). Note their `transformers_pi_detector` is a DeBERTa classifier, a ready PromptGuard-class column.
**Cite in:** method (eval), results.

### D2. InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents
Qiusi Zhan, Zhixiang Liang, Zifan Ying, Daniel Kang. 2024. ACL Findings 2024. arXiv:2403.02691. ~519 citations.
1,054 cases, 17 user tools, 62 attacker tools; two harm classes (direct harm, data exfiltration). ReAct GPT-4 falls 24% of the time, nearly doubling with an "enhanced" hacking-prompt prefix.
**Relevance:** Second standard bench; cite as the other target PISmith reports on. We do not run it. One sentence.
**Cite in:** related (para 2).

### D3. WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks
Ivan Evtimov, Arman Zharmagambetov, Aaron Grattafiori, Chuan Guo, Kamalika Chaudhuri. 2025. arXiv:2504.18575. ~137 citations.
End-to-end web-agent injection bench with realistic low-effort human injections. Attacks *partially* succeed up to 86% but agents often fail to complete the attacker's full goal: "security by incompetence."
**Relevance:** Motivates our silent-failure metric: illusioning has no multi-step attacker goal to fail at, the wrong action *is* the user's action, so incompetence does not protect. Cite in discussion of why ASR alone undercounts our threat.
**Cite in:** related (para 2), discussion.

### D4. Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents
Hanrong Zhang, Jingyuan Huang, Kai Mei, Yifei Yao, Zhenting Wang, Chenlu Zhan, Hongwei Wang, Yongfeng Zhang. 2024. arXiv:2410.02644. ~362 citations.
10 scenarios, 400+ tools, 27 attack/defense methods, 13 backbones; includes memory poisoning and a Plan-of-Thought backdoor. Highest average ASR 84.3%; defenses weak.
**Relevance:** Cite as the third bench that Firewalls (E6) saturates; not run. One sentence.
**Cite in:** related (para 2).

---

## E. Defenses we test against (mechanism, and which Table 1 column each gives)

### E1. The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions
Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke, Alex Beutel. 2024. arXiv:2404.13208. ~481 citations.
Defines system > user > tool privilege levels; generates training data so the model ignores lower-privileged *instructions* that conflict with higher ones. Large robustness gains on GPT-3.5 for unseen attack types.
**Relevance:** Mechanism: deprivileges *instructions* in tool text. A fact needs no privilege, so IH is structurally blind to illusioning. Column "IH-trained target." Also see IH-Challenge (Guo et al. 2026, arXiv:2603.10521) for the RL-trained frontier version; one sentence.
**Cite in:** threat, method (defense list), results.

### E2. Meta SecAlign: A Secure Foundation LLM Against Prompt Injection Attacks
Sizhe Chen, Arman Zharmagambetov, David Wagner, Chuan Guo. 2025. arXiv:2507.02735. ~68 citations. (Lineage: StruQ arXiv:2402.06363 ~389 cites; SecAlign CCS 2025, arXiv:2410.05451 ~195 cites.)
Open-weight 8B/70B models trained with SecAlign-style preference optimization (prefer response to the user instruction over response to the injected one). Security generalizes to unseen tool-calling and web tasks.
**Relevance:** The open IH-trained target we can actually run (8B fits). Same structural blindness argument as E1. Note AutoInject (B3) already breaks Meta-SecAlign-70B with RL hijack, so our claim is not "we break SecAlign" but "template facts pass SecAlign where template hijacks do not."
**Cite in:** method (defense list), results.

### E3. SecOPD: Mitigating Adaptive Prompt Injections by On-Policy Distillation
Yibo Peng, Long Lian, David Wagner, Sizhe Chen. 2026. EMNLP 2026. arXiv:2608.21500. ~0 citations (Aug 2026).
Token-level feedback for defensive fine-tuning: rollouts on injected input are scored by the initialization model on the clean input. Qwen3.6-27B-SecOPD: 9.0% ASR against PISmith vs 94.0% for Meta-SecAlign; 4.7% in agentic tool calling. Weights on HF (`pybbb/Qwen3.6-27B-SecOPD`).
**Relevance:** The strongest IH-class defense as of submission; also explicitly hardened against PISmith, so it is the ideal target for the "hijack collapses, fact holds" split. Use it as the IH column if it fits the GPU (27B, bf16 ~54GB; A100-80 yes, A100-40 no). Training signal is "tokens that differ from the clean-input rollout," and a fabricated fact *changes* the rollout, so this is the defense most likely to partially catch B rows. Say so.
**Cite in:** method (defense list), results, discussion.

### E4. Defending Against Indirect Prompt Injection Attacks With Spotlighting
Keegan Hines, Gary Lopez, Matthew Hall, Federico Zarfati, Yonatan Zunger, Emre Kiciman. 2024. arXiv:2403.14720. ~254 citations.
Prompt-engineering family (delimiting, datamarking, base64 encoding) that gives the model a continuous provenance signal for untrusted text. ASR from >50% to <2% on GPT-family with minimal utility loss.
**Relevance:** Column "spotlighting" (AgentDojo's `spotlighting_with_delimiting`). Mechanism marks text as *data*; our payload *is* data, so it passes. Cheapest column, run first.
**Cite in:** method (defense list), results.

### E5. CommandSans: Securing AI Agents with Surgical Precision Prompt Sanitization
Debeshee Das, Luca Beurer-Kellner, Marc Fischer, Maximilian Baader. 2025. arXiv:2510.08829. ~11 citations.
Token-level sanitizer removes "instructions directed at AI systems" from tool outputs; non-blocking, no calibration, trained on ordinary instruction-tuning data. 34% -> 3% ASR on AgentDojo without utility loss.
**Relevance:** Column "stripper," and the *definition* of our attacker constraint: a CommandSans-style stripper must return every B payload unchanged (assert in N0). If weights are not public, a regex plus small classifier stands in and we say so. Also the hybrid row H is designed to strip down to exactly B.
**Cite in:** threat (attacker capability), method (constraint), results.

### E6. Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?
Rishika Bhagwatkar, Kevin Kasa, Abhay Puri, Gabriel Huang, Irina Rish, Krishnamurthy Dvijotham, Alexandre Lacoste, Jason Stanley. 2025. arXiv:2510.05244. ~18 citations.
Tool-Input Firewall (Minimizer) plus Tool-Output Firewall (Sanitizer: an LLM asked to remove content not relevant to the task). Reports perfect security with high utility on AgentDojo, ASB, InjecAgent, tau-Bench, and argues those benches are saturated; proposes a three-stage cascade of adaptive attacks.
**Relevance:** The paper that can eat us. Mandatory honest paragraph: their sanitizer removes *irrelevant* content, and a fabricated regulation about the user's task is relevant, so the firewall should pass it. Run as a 7th column if the prompt is reproducible; if it kills B rows, that becomes the defense-probe result and the paper still stands as "firewalls need a relevance-plus-veracity check." Also cite their benchmark critique when explaining why we hand-pick 25 checkable cases.
**Cite in:** related (para 2), method, results, discussion (dedicated paragraph).

### E7. LlamaFirewall: An open source guardrail system for building secure AI agents (PromptGuard 2)
Sahana Chennabasappa, Cyrus Nikolaidis, Daniel Song, David Molnar, ... (Meta). 2025. arXiv:2505.03574. ~116 citations.
Three guardrails: PromptGuard 2 (22M/86M universal jailbreak/injection classifier), AlignmentCheck (CoT auditor for goal misalignment), CodeShield. PromptGuard 2 is the classifier we use.
**Relevance:** Column "PromptGuard" and the detectability term in the B3/B4 reward. Classifier is trained on command-shaped payloads; fabricated facts should score low even before RL. Also AlignmentCheck is a task-deviation monitor, which our threat model predicts returns zero on illusioning; mention in the control paragraph. Report PG2 false-positive rate on benign tool outputs alongside.
**Cite in:** method (reward, defense list), results.

### E8. Certifiably Robust RAG against Retrieval Corruption (RobustRAG)
Chong Xiang, Tong Wu, Zexuan Zhong, David Wagner, Danqi Chen, Prateek Mittal. 2024. ICLR 2025. arXiv:2405.15556. ~157 citations.
Isolate-then-aggregate: answer from each retrieved passage separately, then securely aggregate (keyword or decoding). Certifies a lower bound on response quality against k corrupted passages.
**Relevance:** The natural evidence-channel defense (reviewer seat flagged it). With one truthful and one poisoned doc, RobustRAG reduces to a 1-vs-1 vote, which is exactly where its certificate is vacuous, and it does not apply to single-action agent steps. Cite to explain why our verifier column is a refuter, not an aggregator, and as future work for multi-source retrieval.
**Cite in:** related (para 2), discussion.

---

## F. AI control and monitoring framing

### F1. AI Control: Improving Safety Despite Intentional Subversion
Ryan Greenblatt, Buck Shlegeris, Kshitij Sachan, Fabien Roger. 2023. ICML 2024. arXiv:2312.06942. ~202 citations.
Protocols (trusted monitoring, trusted editing, untrusted monitoring) evaluated against an untrusted model that actively subverts them, in an APPS backdooring setting. Introduces the safety-vs-usefulness frame.
**Relevance:** Frame for the "silent failure" claim: a trusted monitor scoring task deviation sees an on-task action and returns zero. Our illusioned agent is not scheming, but the defender's visibility is the same as in control settings, so the failure is monitor-blind. One paragraph; do not overclaim that this is a control paper. Also cite Terekhov et al. 2025 (arXiv:2510.09462, "Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols") for the observation that monitor-based protocols are a single point of failure.
**Cite in:** threat (defender visibility), discussion.

### F2. The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents
Feiran Jia, Tong Wu, Xin Qin, Anna Squicciarini. 2024. arXiv:2412.16682. ~94 citations.
Test-time defense verifying every instruction and tool call contributes to the user's stated goal. 2.07% ASR at 69.79% utility on AgentDojo (GPT-4o).
**Relevance:** Canonical task-alignment monitor. Illusioning passes it by construction (the wrong `send_money` is the user's goal). Cite as the representative of the "task-deviation monitor" row in the defense taxonomy table; optional 8th column if time.
**Cite in:** threat (defense taxonomy), discussion.

---

## G. Persuasion, authority, sycophancy (why fabricated authority works)

### G1. How Johnny Can Persuade LLMs to Jailbreak Them: Rethinking Persuasion to Challenge AI Safety by Humanizing LLMs (PAP)
Yi Zeng, Hongpeng Lin, Jingwen Zhang, Diyi Yang, Ruoxi Jia, Weiyan Shi. 2024. ACL 2024. arXiv:2401.06373. ~704 citations.
Persuasion taxonomy from social science (authority endorsement, evidence-based persuasion, expert endorsement, ...) used to generate interpretable jailbreak prompts; >92% ASR on Llama-2, GPT-3.5, GPT-4.
**Relevance:** Names the technique family our templates draw from ("authority endorsement," "evidence-based persuasion"). Cite when describing the 10 hand templates; borrow their category labels for the appendix histogram if kept.
**Cite in:** method (templates), related (para 3).

### G2. The Dark Side of Trust: Authority Citation-Driven Jailbreak Attacks on Large Language Models (DarkCite)
Xikang Yang, Xuehai Tang, Jizhong Han, Songlin Hu. 2024. arXiv:2411.11407. ~8 citations.
Generates fabricated authoritative citations matched to risk type (e.g., GitHub for malware) to jailbreak aligned LLMs; 76% vs 68% on Llama-2. Proposes an authenticity-and-harm verification defense (DPR 11% -> 74%).
**Relevance:** Why the JailbreakBench/HarmBench track was cut: fake-authority jailbreaks exist. Cite to show fabricated authority is known for *refusal bypass*, and that we move it to *action agents under injection defenses*. Their verification defense is the jailbreak-side analogue of our refuter column.
**Cite in:** related (para 3), discussion.

### G3. Adaptive Chameleon or Stubborn Sloth: Revealing the Behavior of Large Language Models in Knowledge Conflicts
Jian Xie, Kai Zhang, Jiangjie Chen, Renze Lou, Yu Su. 2023. ICLR 2024. arXiv:2305.13300. ~375 citations.
Controlled counter-memory experiments: LLMs are highly receptive to external evidence that conflicts with parametric memory *when the evidence is coherent and convincing*, but show confirmation bias when the evidence partially agrees with memory.
**Relevance:** The mechanism behind the mechanism: coherence and convincingness are what our attacker learns. Also explains why hybrid row H (fact plus imperative) may underperform pure B: the imperative breaks coherence. Cite in the intro's second paragraph.
**Cite in:** intro, discussion.

### G4. Authority, Truth, and Citation Bias: A Large-Scale Multi-Domain Benchmark for Studying Epistemic Susceptibility in Large Language Models (AuthorityBench)
Aryan Khurana et al. 2026. arXiv:2606.13104. ~0 citations.
220k prompts, 2x2 claim-veracity x citation-veracity design across four domains and four venue-prestige tiers. Citation presence, real or fabricated, raises hallucination rates; strongest when fabricated citations accompany claims (3-22 pt increase; 35-77% in general knowledge). Venue prestige and author demographics have negligible effect.
**Relevance:** Direct evidence that *fabricated* citations move models, and that surface prestige does not matter, which predicts our RL attacker will learn citation *shape* (numbers, dates, section references) rather than famous names. Cite when interpreting what B3/B4 learned.
**Cite in:** results (qualitative), discussion.

---

## H. Similar motivation, different method

### H1. Reasoning Hijacking: The Fragility of Reasoning Alignment in Large Language Models (Criteria Attack)
Yuansen Liu, Yixuan Tang, Anthony Kum Hoe Tun. 2026. ACL 2026. arXiv:2601.10294. ~1 citation.
Distinguishes Goal Hijacking (override the task) from Reasoning Hijacking (keep the task, inject spurious decision criteria). Criteria Attack on toxic-comment, review, and spam classifiers bypasses SecAlign and StruQ "because the model's explicit intent remains aligned with the user's instructions."
**Relevance:** Same structural argument (goal intact, so goal-deviation defenses are blind) on classification tasks with injected *criteria*. We make the injected object a *fact*, move to tool-using agents, and add the verification axis. Cite as the closest independent confirmation of the control-vs-evidence-channel split; borrow their "blind spot" phrasing sparingly.
**Cite in:** related (para 1 or 2), discussion.

### H2. Is Deep Research Reliable? Misleading Knowledge Induces False Conclusions (MisKnow-Agent)
Pengyu Zhu, Lijun Li, Longju Yang, Sen Su, Jing Shao. 2026. arXiv:2607.20891. ~1 citation.
5,933 misleading documents with controlled authority cues and source styles injected into DeepResearch Bench tasks. One document raises report-level false-conclusion adoption from 0% to 54.7% mean across DeerFlow, WebThinker, and Gemini Deep Research. Source authority and presentation style matter; search rank and extra documents do not. Cross-model verification flags the documents yet agents still adopt them.
**Relevance:** Song's autonomous-research line, done. Gives us the "one poisoned search result flips a conclusion" example without running it, and the striking finding that *detection without refusal-to-adopt* is the failure (same as Cordon-MAS's "monitoring-control gap," arXiv:2605.26754). Position: they vary authority cues by hand; we learn them and test against injection defenses rather than research-pipeline defenses.
**Cite in:** intro (motivating example), related (para 1), discussion.

### H3. MemMorph: Tool Hijacking in LLM Agents via Memory Poisoning
Xuanye Zhang et al. 2026. arXiv:2605.26154. ~5 citations.
Biases tool *selection* by injecting a few memory records "disguised as technical facts, incident reports, and operational policies"; the agent infers the attacker-preferred tool itself. Up to 85.9% ASR with three records; survives three defenses.
**Relevance:** Fabricated-policy framing on agents, via memory rather than tool output, targeting tool choice rather than tool arguments. Cite alongside AgentPoison to show the memory-write family; our one-shot tool-result channel needs no persistence. One sentence.
**Cite in:** related (para 1).

---

## Also cite (one line each, ids verified)

- Yi et al. 2023, BIPIA, arXiv:2312.14197 (KDD 2025): first IPI benchmark; "boundary awareness" defense. Related para 2.
- Zhan et al. 2025, Adaptive Attacks Break Defenses Against IPI, arXiv:2503.00061: eight defenses bypassed >50%. Related para 2.
- Nasr et al. 2025, The Attacker Moves Second, arXiv:2510.09023: adaptive attacks bypass 12 defenses >90%; justifies why static-defense tables need an adaptive row (B3/B4). Related para 2.
- Guo et al. 2026, IH-Challenge, arXiv:2603.10521: OpenAI RL dataset for IH; note that it "saturates an internal static agentic prompt injection evaluation," i.e., static hijack is solved, illusioning is not measured. Related para 2.
- Wang et al. 2025, AgentVigil/AgentFuzzer, arXiv:2505.05849 (Song lab): MCTS fuzzing on AgentDojo, 71% vs o3-mini. Related para 2.
- Yu et al. 2026, Cordon-MAS, arXiv:2605.26754: "monitoring-control gap," models detect contradictions yet act on poison; information-flow defense. Discussion (verifier column).
- Xue et al. 2024, BadRAG, arXiv:2406.00083: retrieval-side backdoor triggers; steering/DoS. Related para 1, one clause.
- Dong et al. 2025, MINJA, arXiv:2503.03704 (NeurIPS 2025): query-only memory injection. Related para 1, one clause.
- Chen et al. 2023, Can LLM-Generated Misinformation Be Detected?, arXiv:2309.13788: LLM misinformation is harder to detect than human-written. Discussion.
- Geng et al. 2025, Control Illusion, arXiv:2502.15851 (AAAI 2026, DOI 10.1609/aaai.v40i36.40339): "societal hierarchy framings (authority, expertise, consensus) show stronger influence than system/user roles." Strong support for G.
- Wang et al. 2026, Landscape of Prompt Injection Threats / AgentPI, arXiv:2602.10453: defenses suppress contextual inputs and fail on context-dependent tasks. Discussion.

---

## Reading notes: 10 insights that change how we write

1. **Do not claim the goal class is new.** Greshake 2023 lists misinformation as an IPI goal; Wu et al. 2024 name it illusioning; PoisonedRAG/CorruptRAG/AgentPoison/Poisoned Playbooks all do knowledge poisoning. First sentence of related work should concede this in one breath, then pivot: "what is unmeasured is which *defense family* is structurally blind to it, and whether an attacker can be trained to stay blind-side."

2. **Exact novelty sentence vs AgentPoison and CorruptRAG-AK.** "AgentPoison needs a query trigger and a persistent KB write and tests no instruction-channel defenses; CorruptRAG-AK hand-writes credibility framing on QA and tests RAG architectures. We need one transient tool result, learn the framing under a no-instruction constraint and a refuter penalty, and report ASR-under-defense on action agents." Every clause maps to a row or column in Table 1.

3. **AutoDojo already wrote our thesis as an aside.** Their "injection can pose as ordinary data rather than an explicit instruction, bypassing defenses that rely on detecting instruction-like text" must be quoted, not paraphrased around. Our differentiator is that we make it the constraint (stripper-identity), the reward, and the mechanism (verification boundary). If we omit it a Xiao-lineage reviewer will supply it.

4. **Detector-evasion reward is prior art (RL-Hammer).** Say "following Wen et al." when introducing the PG2 penalty. The new term is the refuter penalty, and the new *constraint* is no imperatives. Frame B4, not B3, as the contribution row.

5. **RL is a row, not the title, and the field agrees.** PIMiner argues RL attackers transfer poorly; PISmith needs entropy hacks; AutoInject needs a learned dense reward. Keep "RL" out of the title, keep the template attacker as the headline if B0 already wins, and cite PIMiner when explaining why transfer sits in the appendix.

6. **The verifier column is where the field says the fight is.** Poisoned Playbooks (verification prompting fails under sparse evidence), MisKnow-Agent (cross-model verification flags the doc, agent adopts anyway), Cordon-MAS (monitoring-control gap), and Architecture Matters (framing dominates at the content-reasoning stage) all point the same way. Write the verifier column result as the mechanism finding, and report *refuter flagged but agent still acted* as its own number.

7. **Firewalls needs its own paragraph, and the argument is "relevance is not veracity."** Their sanitizer removes task-irrelevant content; a fake policy about the user's task is maximally relevant. If we cannot run it, state the prediction and the falsifier explicitly. If we run it and it wins, the paper becomes "firewalls need a veracity check," which is still a workshop result.

8. **SecOPD is the strongest IH target and the most likely to partially catch us.** Its token-level signal penalizes deviation from the clean-input rollout; a believed fact deviates. Pre-register that B rows may drop under SecOPD more than under SecAlign, and interpret a drop as "IH training that scores *outputs* rather than *instructions* leaks into the evidence channel," not as a loss.

9. **Silent failure needs a number, and WASP explains why ASR undercounts.** WASP's "security by incompetence" (agent fails the attacker's multi-step goal) does not apply when the attacker's goal is the user's single action. Report silent-failure rate (success + agent reports success + no flag) as the headline alongside ASR, and cite Task Shield / AlignmentCheck as monitors that return zero by construction.

10. **What the attacker learns should be reported in AuthorityBench's terms.** Fabricated citations raise hallucination independent of venue prestige or author names, and Control Illusion finds authority/expertise/consensus framings outrank system/user roles. Predict that B3/B4 learn citation *structure* (section numbers, dates, version strings), not famous names, and check the sampled payloads against that prediction in one appendix table. If the histogram is kept at all, this is its only job.

---

## BibTeX

```bibtex
@inproceedings{chen2024agentpoison,
  title={AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases},
  author={Chen, Zhaorun and Xiang, Zhen and Xiao, Chaowei and Song, Dawn and Li, Bo},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2024},
  note={arXiv:2407.12784}
}

@article{xu2024advweb,
  title={AdvWeb: Controllable Black-box Attacks on VLM-powered Web Agents},
  author={Xu, Chejian and Kang, Mintong and Zhang, Jiawei and Liao, Zeyi and Mo, Lingbo and Yuan, Mengqi and Sun, Huan and Li, Bo},
  journal={arXiv preprint arXiv:2410.17401},
  year={2024},
  note={Later version titled AdvAgent: Controllable Blackbox Red-teaming on Web Agents}
}

@article{shi2025promptarmor,
  title={PromptArmor: Simple yet Effective Prompt Injection Defenses},
  author={Shi, Tianneng and Zhu, Kaijie and Wang, Zhun and Jia, Yuqi and Cai, Will and Liang, Weida and Wang, Haihui and Li, Hongwei and Zhou, Fengjun and others},
  journal={arXiv preprint arXiv:2507.15219},
  year={2025}
}

@article{ma2026autodojo,
  title={AutoDojo: Adaptive Black-Box Attacks Reveal the Limits of IPI Defenses and Task-Specification Effects in LLM Agents},
  author={Ma, Xinhang and Li, Taoran and Xiao, Chaowei and Yu, Zhiyuan and Zhang, Ning and Vorobeychik, Yevgeniy},
  journal={arXiv preprint arXiv:2606.15057},
  year={2026}
}

@inproceedings{yin2026pismith,
  title={PISmith: Reinforcement Learning-based Red Teaming for Prompt Injection Defenses},
  author={Yin, Chenlong and Wang, Yanting and others and Jia, Jinyuan},
  booktitle={Conference on Language Modeling (COLM)},
  year={2026},
  note={arXiv:2603.13026}
}

@article{wen2025rlhammer,
  title={RL Is a Hammer and LLMs Are Nails: A Simple Reinforcement Learning Recipe for Strong Prompt Injection},
  author={Wen, Yuxin and others},
  journal={arXiv preprint arXiv:2510.04885},
  year={2025}
}

@article{chen2026autoinject,
  title={Learning to Inject: Automated Prompt Injection via Reinforcement Learning},
  author={Chen, Xin and others},
  journal={arXiv preprint arXiv:2602.05746},
  year={2026}
}

@article{wang2026piminer,
  title={Agent Against Agent: An Agentic System for Automatic Prompt Injection Red Teaming},
  author={Wang, Yanting and Yin, Chenlong and Geng, Runpeng and Jia, Jinyuan},
  journal={arXiv preprint arXiv:2608.05108},
  year={2026}
}

@inproceedings{zou2025poisonedrag,
  title={PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models},
  author={Zou, Wei and Geng, Runpeng and Wang, Binghui and Jia, Jinyuan},
  booktitle={USENIX Security Symposium},
  year={2025},
  note={arXiv:2402.07867}
}

@inproceedings{zhang2026corruptrag,
  title={Practical Poisoning Attacks against Retrieval-Augmented Generation},
  author={Zhang, Baolei and Chen, Yuxi and Liu, Zhuqing and Nie, Lihai and Li, Tong and Liu, Zheli and Fang, Minghong},
  booktitle={ACM Symposium on Access Control Models and Technologies (SACMAT)},
  year={2026},
  note={arXiv:2504.03957. Introduces CorruptRAG-AS and CorruptRAG-AK}
}

@article{korn2026architecture,
  title={Architecture Matters: Comparing RAG Systems under Knowledge Base Poisoning},
  author={Korn, Samuel},
  journal={arXiv preprint arXiv:2605.05632},
  year={2026}
}

@article{park2026poisonedplaybooks,
  title={Poisoned Playbooks: Demystifying Knowledge Poisoning Effects on AI Security Agents},
  author={Park, Juho and Choi, Hyunmin and Nam, Kevin},
  journal={arXiv preprint arXiv:2606.24402},
  year={2026}
}

@inproceedings{wu2025dissecting,
  title={Dissecting Adversarial Robustness of Multimodal LM Agents},
  author={Wu, Chen Henry and Shah, Rishi and Koh, Jing Yu and Salakhutdinov, Ruslan and Fried, Daniel and Raghunathan, Aditi},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2025},
  note={arXiv:2406.12814}
}

@inproceedings{pan2023misinformation,
  title={On the Risk of Misinformation Pollution with Large Language Models},
  author={Pan, Yikang and Pan, Liangming and Chen, Wenhu and Nakov, Preslav and Kan, Min-Yen and Wang, William Yang},
  booktitle={Findings of EMNLP},
  year={2023},
  note={arXiv:2305.13661}
}

@inproceedings{greshake2023not,
  title={Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection},
  author={Greshake, Kai and Abdelnabi, Sahar and Mishra, Shailesh and Endres, Christoph and Holz, Thorsten and Fritz, Mario},
  booktitle={Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec)},
  year={2023},
  doi={10.1145/3605764.3623985},
  note={arXiv:2302.12173}
}

@inproceedings{debenedetti2024agentdojo,
  title={AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents},
  author={Debenedetti, Edoardo and Zhang, Jie and Balunovi{\'c}, Mislav and Beurer-Kellner, Luca and Fischer, Marc and Tram{\`e}r, Florian},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks},
  year={2024},
  note={arXiv:2406.13352}
}

@inproceedings{zhan2024injecagent,
  title={InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents},
  author={Zhan, Qiusi and Liang, Zhixiang and Ying, Zifan and Kang, Daniel},
  booktitle={Findings of ACL},
  year={2024},
  note={arXiv:2403.02691}
}

@article{evtimov2025wasp,
  title={WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks},
  author={Evtimov, Ivan and Zharmagambetov, Arman and Grattafiori, Aaron and Guo, Chuan and Chaudhuri, Kamalika},
  journal={arXiv preprint arXiv:2504.18575},
  year={2025}
}

@article{zhang2024asb,
  title={Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents},
  author={Zhang, Hanrong and Huang, Jingyuan and Mei, Kai and Yao, Yifei and Wang, Zhenting and Zhan, Chenlu and Wang, Hongwei and Zhang, Yongfeng},
  journal={arXiv preprint arXiv:2410.02644},
  year={2024}
}

@article{wallace2024instruction,
  title={The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions},
  author={Wallace, Eric and Xiao, Kai and Leike, Reimar and Weng, Lilian and Heidecke, Johannes and Beutel, Alex},
  journal={arXiv preprint arXiv:2404.13208},
  year={2024}
}

@article{chen2025metasecalign,
  title={Meta SecAlign: A Secure Foundation LLM Against Prompt Injection Attacks},
  author={Chen, Sizhe and Zharmagambetov, Arman and Wagner, David and Guo, Chuan},
  journal={arXiv preprint arXiv:2507.02735},
  year={2025}
}

@inproceedings{chen2025secalign,
  title={SecAlign: Defending Against Prompt Injection with Preference Optimization},
  author={Chen, Sizhe and Zharmagambetov, Arman and Mahloujifar, Saeed and Chaudhuri, Kamalika and Wagner, David and Guo, Chuan},
  booktitle={ACM SIGSAC Conference on Computer and Communications Security (CCS)},
  year={2025},
  doi={10.1145/3719027.3744836},
  note={arXiv:2410.05451}
}

@inproceedings{chen2025struq,
  title={StruQ: Defending Against Prompt Injection with Structured Queries},
  author={Chen, Sizhe and Piet, Julien and Sitawarin, Chawin and Wagner, David},
  booktitle={USENIX Security Symposium},
  year={2025},
  note={arXiv:2402.06363}
}

@inproceedings{peng2026secopd,
  title={SecOPD: Mitigating Adaptive Prompt Injections by On-Policy Distillation},
  author={Peng, Yibo and Lian, Long and Wagner, David and Chen, Sizhe},
  booktitle={Proceedings of EMNLP},
  year={2026},
  note={arXiv:2608.21500}
}

@article{hines2024spotlighting,
  title={Defending Against Indirect Prompt Injection Attacks With Spotlighting},
  author={Hines, Keegan and Lopez, Gary and Hall, Matthew and Zarfati, Federico and Zunger, Yonatan and Kiciman, Emre},
  journal={arXiv preprint arXiv:2403.14720},
  year={2024}
}

@article{das2025commandsans,
  title={CommandSans: Securing AI Agents with Surgical Precision Prompt Sanitization},
  author={Das, Debeshee and Beurer-Kellner, Luca and Fischer, Marc and Baader, Maximilian},
  journal={arXiv preprint arXiv:2510.08829},
  year={2025}
}

@article{bhagwatkar2025firewalls,
  title={Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?},
  author={Bhagwatkar, Rishika and Kasa, Kevin and Puri, Abhay and Huang, Gabriel and Rish, Irina and Dvijotham, Krishnamurthy and Lacoste, Alexandre and Stanley, Jason},
  journal={arXiv preprint arXiv:2510.05244},
  year={2025}
}

@article{chennabasappa2025llamafirewall,
  title={LlamaFirewall: An Open Source Guardrail System for Building Secure AI Agents},
  author={Chennabasappa, Sahana and Nikolaidis, Cyrus and Song, Daniel and Molnar, David and others},
  journal={arXiv preprint arXiv:2505.03574},
  year={2025},
  note={Introduces PromptGuard 2}
}

@inproceedings{xiang2025robustrag,
  title={Certifiably Robust RAG against Retrieval Corruption},
  author={Xiang, Chong and Wu, Tong and Zhong, Zexuan and Wagner, David and Chen, Danqi and Mittal, Prateek},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2025},
  note={arXiv:2405.15556}
}

@inproceedings{greenblatt2024aicontrol,
  title={AI Control: Improving Safety Despite Intentional Subversion},
  author={Greenblatt, Ryan and Shlegeris, Buck and Sachan, Kshitij and Roger, Fabien},
  booktitle={International Conference on Machine Learning (ICML)},
  year={2024},
  note={arXiv:2312.06942}
}

@article{terekhov2025adaptive,
  title={Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols},
  author={Terekhov, Mikhail and others},
  journal={arXiv preprint arXiv:2510.09462},
  year={2025}
}

@article{jia2024taskshield,
  title={The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents},
  author={Jia, Feiran and Wu, Tong and Qin, Xin and Squicciarini, Anna},
  journal={arXiv preprint arXiv:2412.16682},
  year={2024}
}

@inproceedings{zeng2024johnny,
  title={How Johnny Can Persuade LLMs to Jailbreak Them: Rethinking Persuasion to Challenge AI Safety by Humanizing LLMs},
  author={Zeng, Yi and Lin, Hongpeng and Zhang, Jingwen and Yang, Diyi and Jia, Ruoxi and Shi, Weiyan},
  booktitle={Proceedings of ACL},
  year={2024},
  note={arXiv:2401.06373}
}

@article{yang2024darkcite,
  title={The Dark Side of Trust: Authority Citation-Driven Jailbreak Attacks on Large Language Models},
  author={Yang, Xikang and Tang, Xuehai and Han, Jizhong and Hu, Songlin},
  journal={arXiv preprint arXiv:2411.11407},
  year={2024}
}

@inproceedings{xie2024chameleon,
  title={Adaptive Chameleon or Stubborn Sloth: Revealing the Behavior of Large Language Models in Knowledge Conflicts},
  author={Xie, Jian and Zhang, Kai and Chen, Jiangjie and Lou, Renze and Su, Yu},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2024},
  note={arXiv:2305.13300}
}

@article{khurana2026authoritybench,
  title={Authority, Truth, and Citation Bias: A Large-Scale Multi-Domain Benchmark for Studying Epistemic Susceptibility in Large Language Models},
  author={Khurana, Aryan and others},
  journal={arXiv preprint arXiv:2606.13104},
  year={2026}
}

@inproceedings{liu2026reasoninghijacking,
  title={Reasoning Hijacking: The Fragility of Reasoning Alignment in Large Language Models},
  author={Liu, Yuansen and Tang, Yixuan and Tun, Anthony Kum Hoe},
  booktitle={Proceedings of ACL},
  year={2026},
  note={arXiv:2601.10294}
}

@article{zhu2026misknow,
  title={Is Deep Research Reliable? Misleading Knowledge Induces False Conclusions},
  author={Zhu, Pengyu and Li, Lijun and Yang, Longju and Su, Sen and Shao, Jing},
  journal={arXiv preprint arXiv:2607.20891},
  year={2026}
}

@article{zhang2026memmorph,
  title={MemMorph: Tool Hijacking in LLM Agents via Memory Poisoning},
  author={Zhang, Xuanye and others},
  journal={arXiv preprint arXiv:2605.26154},
  year={2026}
}

@inproceedings{yi2025bipia,
  title={Benchmarking and Defending against Indirect Prompt Injection Attacks on Large Language Models},
  author={Yi, Jingwei and Xie, Yueqi and Zhu, Bin and Kiciman, Emre and Sun, Guangzhong and Xie, Xing and Wu, Fangzhao},
  booktitle={Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining},
  year={2025},
  doi={10.1145/3690624.3709179},
  note={arXiv:2312.14197}
}

@article{zhan2025adaptive,
  title={Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents},
  author={Zhan, Qiusi and Fang, Richard and Panchal, Henil Shalin and Kang, Daniel},
  journal={arXiv preprint arXiv:2503.00061},
  year={2025}
}

@article{nasr2025attacker,
  title={The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections},
  author={Nasr, Milad and others},
  journal={arXiv preprint arXiv:2510.09023},
  year={2025}
}

@article{guo2026ihchallenge,
  title={IH-Challenge: A Training Dataset to Improve Instruction Hierarchy on Frontier LLMs},
  author={Guo, Chuan and others},
  journal={arXiv preprint arXiv:2603.10521},
  year={2026}
}

@article{wang2025agentvigil,
  title={AgentVigil: Generic Black-Box Red-teaming for Indirect Prompt Injection against LLM Agents},
  author={Wang, Zhun and others},
  journal={arXiv preprint arXiv:2505.05849},
  year={2025},
  note={Also titled AgentFuzzer}
}

@article{yu2026cordon,
  title={Cordon-MAS: Defending RAG against Knowledge Poisoning via Information-Flow Control},
  author={Yu, Zhengtao and others},
  journal={arXiv preprint arXiv:2605.26754},
  year={2026}
}

@article{xue2024badrag,
  title={BadRAG: Identifying Vulnerabilities in Retrieval Augmented Generation of Large Language Models},
  author={Xue, Jiaqi and others},
  journal={arXiv preprint arXiv:2406.00083},
  year={2024}
}

@inproceedings{dong2025minja,
  title={Memory Injection Attacks on LLM Agents via Query-Only Interaction},
  author={Dong, Shen and others},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2025},
  note={arXiv:2503.03704}
}

@article{chen2023detected,
  title={Can LLM-Generated Misinformation Be Detected?},
  author={Chen, Canyu and Shu, Kai},
  journal={arXiv preprint arXiv:2309.13788},
  year={2023}
}

@inproceedings{geng2026controlillusion,
  title={Control Illusion: The Failure of Instruction Hierarchies in Large Language Models},
  author={Geng, Yilin and others},
  booktitle={Proceedings of AAAI},
  year={2026},
  doi={10.1609/aaai.v40i36.40339},
  note={arXiv:2502.15851}
}

@article{wang2026landscape,
  title={The Landscape of Prompt Injection Threats in LLM Agents: From Taxonomy to Analysis},
  author={Wang, Pei and others},
  journal={arXiv preprint arXiv:2602.10453},
  year={2026}
}
```
