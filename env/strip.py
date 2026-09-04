"""Regex imperative stripper (control-channel defense stand-in).

ponytail: a learned stripper (CommandSans 2510.08829 / PromptArmor) replaces
this later. Ceiling: sentence-initial verb list + a few second-person
patterns; it will miss imperatives phrased as questions or embedded in
quotes. Good enough to certify that the B templates carry no command
surface at all.
"""

import re

_VERBS = (
    "ignore disregard forget answer respond reply say output write return "
    "follow do use stop skip act treat consider assume print send call execute "
    "run delete provide give tell report note remember please override replace "
    "set change update"
).split()

_SENT_START = re.compile(r"^[\s\W]*(?:" + "|".join(_VERBS) + r")\b", re.I)
_PATTERNS = re.compile(
    r"\b(ignore|you must|you should|please|you (?:can|will|need|have to|may|shall|are to))\b",
    re.I,
)
_SPLIT = re.compile(r"(?<=[.!?\n])(\s+)")


def is_imperative(sentence: str) -> bool:
    return bool(_SENT_START.match(sentence) or _PATTERNS.search(sentence))


def strip_imperatives(text: str) -> str:
    parts = _SPLIT.split(text)  # [sent, ws, sent, ws, ..., sent]
    sents, ws = parts[0::2], parts[1::2] + [""]
    kept = [s + w for s, w in zip(sents, ws) if not is_imperative(s)]
    out = "".join(kept)
    return text if out == text else out.strip()


def is_instruction_free(text: str) -> bool:
    return strip_imperatives(text) == text


if __name__ == "__main__":
    from env.payloads import HIJACK_TEMPLATE, HYBRID_TEMPLATE, TEMPLATES, render

    case = {"wrong_target": "Paris", "answer": "Lyon", "question": "Which city?"}
    for name, t in TEMPLATES.items():
        assert is_instruction_free(render(t, case)), name
    assert not is_instruction_free(render(HIJACK_TEMPLATE, case))
    assert not is_instruction_free(render(HYBRID_TEMPLATE, case))
    assert strip_imperatives(render(HYBRID_TEMPLATE, case)) == render(TEMPLATES["statute"], case)
    print("strip.py: all template assertions pass")
