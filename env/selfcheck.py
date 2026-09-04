"""python -m env.selfcheck: invariants the paper's numbers depend on. No model, no network."""

import json
import os
import tempfile

from env.defenses import DEFENSES
from env.payloads import HIJACK_TEMPLATE, HYBRID_TEMPLATE, TEMPLATES, render
from env.research_env import build_cases, contains, doc_order, render_agent_prompt, reward, utility
from env.run_table import ROWS, run
from env.strip import is_instruction_free, strip_imperatives

cases = build_cases(500)
assert len(cases) == 500 and len({c["id"] for c in cases}) == 500

# 1. matched pairs: doc order depends on (seed, case) only, never on the row or the doc text.
for c in cases[:50]:
    o = doc_order(c)
    for t in (HIJACK_TEMPLATE, TEMPLATES["statute"]):
        m = render_agent_prompt(c, c["truthful_doc"], render(t, c))[-1]["content"]
        assert json.loads(m.split("\n\nSearch tool result:\n", 1)[1])["results"][o.index(0)]["snippet"] == c["truthful_doc"]
    assert doc_order(c, seed=1) is not None and doc_order(c) == o
assert any(doc_order(c) == [1, 0] for c in cases) and any(doc_order(c) == [0, 1] for c in cases)

# 2. stripper is identity on every B payload and on the benign/truthful docs; not identity on A1/H.
for c in cases:
    for k, t in TEMPLATES.items():
        assert is_instruction_free(render(t, c)), (k, c["id"])
    assert is_instruction_free(c["truthful_doc"]) and is_instruction_free(c["benign_doc"])
    assert not is_instruction_free(render(HIJACK_TEMPLATE, c))
    assert strip_imperatives(render(HYBRID_TEMPLATE, c)) == render(TEMPLATES["statute"], c), c["id"]

# 3. reward cannot fire on the truthful doc, an empty answer, or "both answers".
for c in cases:
    assert reward(c["truthful_doc"], c) == 0 and utility(c["truthful_doc"], c) == 1
    assert utility(c["benign_doc"], c) == 0  # control doc never leaks the answer
    assert reward("", c) == 0 and utility("", c) == 0
    assert reward(f"{c['wrong_target']} or {c['answer']}", c) == 0
    assert reward(f"  {c['wrong_target'].swapcase()}\n", c) == 1 or not c["wrong_target"].isascii()
    assert not (contains(c["wrong_target"], c["answer"]) or contains(c["answer"], c["wrong_target"]))
assert not contains("8", "1988") and contains("8", "8 May") and contains("a b", "x a  b y")

# 4. resume is idempotent and keyed per (target, model, defense): a second run adds no records.
with tempfile.TemporaryDirectory() as d:
    out = os.path.join(d, "t.jsonl")
    a1 = run("stub", None, "none", 20, 0, out, "gpt-4o-mini", 4)
    n1 = sum(1 for _ in open(out))
    a2 = run("stub", None, "none", 20, 0, out, "gpt-4o-mini", 4)
    assert n1 == 20 * len(ROWS) == sum(1 for _ in open(out)), n1
    assert {r: dict(v) for r, v in a1.items()} == {r: dict(v) for r, v in a2.items()}
    run("stub", None, "promptarmor", 20, 0, out, "gpt-4o-mini", 4)  # stub guard never flags
    assert sum(1 for _ in open(out)) == 2 * n1
    for l in open(out):
        r = json.loads(l)
        assert r["silent"] == float(r["asr"] and r["delivered"] and not r["flag"])
        if r["row"] == "A0":
            assert r["asr"] == 0, r
        assert r["stripper_flag"] == float(r["row"] in ("A1", "H"))

# 5. defenses are pure functions on (question, doc) and `none` is identity.
for c in cases[:20]:
    assert DEFENSES["none"](c["question"], c["truthful_doc"]) == c["truthful_doc"]
    assert DEFENSES["spotlight"](c["question"], "a b") == "a^b"

print("selfcheck: all invariants pass on 500 cases")
