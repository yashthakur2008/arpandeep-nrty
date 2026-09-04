# env: single-call research-agent illusioning env

- `research_env.py`: `build_cases` (HotpotQA distractor, cached in `data/`), `render_agent_prompt`, `reward`, `utility`, targets.
- `payloads.py`: 10 declarative fabricated-authority templates (B0), `HIJACK_TEMPLATE` (A1), `HYBRID_TEMPLATE` (H).
- `strip.py`: regex imperative stripper. `python -m env.strip` asserts B passes, A1/H fail.
- `run_table.py`: rows A0/A1/B0x10/H, resumable jsonl in `results/`.

Run: `/tmp/nsrr-venv/bin/python -m env.run_table --target stub --n 100`

Swap in a real target: implement `VLLMTarget.answer` / `OpenAITarget.answer` in `research_env.py`
(one `chat.completions.create` call each, return `message.content`), then `--target vllm` or `--target openai`.
Constructor signatures are already fixed; `make_target` passes `**kw` through.

StubTarget has no model: it answers truthfully when the truthful doc is first, else flips to `wrong_target`
with p=0.3. Its numbers only prove the harness. Stripper flags on B rows (~1%) are false positives from
entity names such as "You Can Be a Star" matching `you can`; a learned stripper replaces the regex later.
