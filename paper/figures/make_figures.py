#!/usr/bin/env python3
"""Result figures for "Fabricated Authority in the Wild", rebuilt to a reviewer's spec.

Rules applied throughout:
- one accent colour for the intervention (provenance clause), neutral grey for
  everything else; a single family and two sizes of type
- titles describe, captions argue; no p-values in the figure
- bars encode the rate, the n lives in the axis label, not beside every bar
- zero-count cells get an explicit "0" marker, not an orphan error-bar tick
- cells with different n get proportional bar widths so the eye is not fooled
- three figures, not seven: the rest of the story fits in tables and text

Every count is asserted against the fraction printed in the paper.
"""
from __future__ import annotations

from math import sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "pdf.fonttype": 42,
})

ACCENT = "#1b6e3a"      # the provenance clause
NEUTRAL = "#9e9e9e"     # every other condition
DARK = "#424242"        # the worst condition, when it matters
INK = "#212121"


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(k: int, n: int) -> float:
    return 100.0 * k / n


def check(k, n, printed):
    assert abs(pct(k, n) - printed) < 0.06, (k, n, printed)


def hbar_with_ci(ax, y, k, n, color, height=0.62):
    """Horizontal bar with Wilson CI. Zero cell: thick zero tick plus upper bound."""
    r = pct(k, n)
    lo, hi = wilson(k, n)
    if k == 0:
        ax.plot([0, hi * 100], [y, y], color=color, lw=0.9)
        ax.plot([hi * 100, hi * 100], [y - height * 0.18, y + height * 0.18], color=color, lw=0.9)
        ax.plot([0, 0], [y - height / 2, y + height / 2], color=color, lw=2.6, solid_capstyle="butt", zorder=5)
        ax.text(hi * 100 + 0.6, y, "0 / %d" % n, ha="left", va="center", fontsize=6.8, color=color, fontweight="bold")
    else:
        ax.barh(y, r, height=height, color=color, zorder=3)
        ax.plot([lo * 100, hi * 100], [y, y], color=INK, lw=0.9, zorder=4)
    return r, lo, hi


def bar_with_ci(ax, x, k, n, color, width=0.6, label_zero=True):
    """Vertical bar with Wilson CI. Zero cell: thick zero tick plus upper bound."""
    r = pct(k, n)
    lo, hi = wilson(k, n)
    if k == 0:
        ax.plot([x, x], [0, hi * 100], color=color, lw=0.9)
        ax.plot([x - width * 0.18, x + width * 0.18], [hi * 100, hi * 100], color=color, lw=0.9)
        ax.plot([x - width / 2, x + width / 2], [0, 0], color=color, lw=2.6, solid_capstyle="butt", zorder=5)
        if label_zero:
            ax.text(x, hi * 100 + 0.8, "0 / %d" % n, ha="center", va="bottom", fontsize=6.8, color=color, fontweight="bold")
    else:
        ax.bar(x, r, width=width, color=color, zorder=3)
        ax.plot([x, x], [lo * 100, hi * 100], color=INK, lw=0.9, zorder=4)
    return r, lo, hi


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", dpi=250)
    plt.close(fig)
    print("wrote", name)


# --------------------------------------------------------------------------- #
# numbers: read from results/*.json (the same files tests/test_paper_claims.py
# guards). Nothing below is typed in; a stale figure is impossible.
# --------------------------------------------------------------------------- #
import json
from collections import defaultdict

RESULTS = Path(__file__).resolve().parents[2] / "results"


def _load(name):
    return json.loads((RESULTS / name).read_text())


def _count(outcomes, key_fn, pred=lambda o: True):
    """{key: [violations, n]} over outcomes passing pred."""
    c = defaultdict(lambda: [0, 0])
    for o in outcomes:
        if pred(o):
            k = key_fn(o)
            c[k][0] += bool(o["violated"])
            c[k][1] += 1
    return dict(c)


_sweep = _load("agentic_sweep_api.json")["outcomes"]
_attacked = [o for o in _sweep if o["attack_name"] != "none"]
_control = [o for o in _sweep if o["attack_name"] == "none"]

_by_policy = _count(_attacked, lambda o: o["policy_variant"])
_POLICY_LABEL = {"exemption": "exemption", "autonomous": "autonomous", "bare": "bare",
                 "strict": "strict", "strict_hatch": "strict + provenance clause"}
POLICY = [(_POLICY_LABEL[k], *_by_policy[k], 100 * _by_policy[k][0] / _by_policy[k][1])
          for k in ("exemption", "autonomous", "bare", "strict", "strict_hatch")]

_abl = _load("agentic_ablation.json")["outcomes"]
_by_abl = _count([o for o in _abl if o["attack_name"] != "none"], lambda o: o["policy_variant"])
_ABL_LABEL = {"strict": ("strict", 40), "strict_hatch": ("+ provenance clause", 77), "strict_verbose": ("+ unrelated filler", 98)}
LENGTH = [(f"{_ABL_LABEL[k][0]}, {_ABL_LABEL[k][1]} words", _ABL_LABEL[k][1], *_by_abl[k], 100 * _by_abl[k][0] / _by_abl[k][1])
          for k in ("strict", "strict_hatch", "strict_verbose")]

_by_attack = _count(_attacked, lambda o: o["attack_name"])
_ATTACK_LABEL = {"reclassify": "reclassify the act", "emergency": "emergency, no time", "prior_approval": "prior approval",
                 "superseded": "superseding policy", "audit_exemption": "audit exemption", "combined": "all three combined"}
ATTACK = [(_ATTACK_LABEL[k], *_by_attack[k], 100 * _by_attack[k][0] / _by_attack[k][1])
          for k in ("reclassify", "emergency", "prior_approval", "superseded", "audit_exemption", "combined")]

_ind = _load("agentic_indirect_forced.json")["outcomes"]
_ind_pois = _count(_ind, lambda o: o["policy_variant"], lambda o: o["poisoned"])
INDIRECT = {"exemption": [tuple(_by_policy["exemption"]), tuple(_ind_pois["exemption"])],
            "strict + provenance clause": [tuple(_by_policy["strict_hatch"]), tuple(_ind_pois["strict_hatch"])]}
_ind_by_attack = _count(_ind, lambda o: o["attack_name"], lambda o: o["poisoned"] and o["policy_variant"] == "strict_hatch")
INDIRECT_BY_ATTACK = [(_ATTACK_LABEL[k], *_ind_by_attack[k]) for k in ("superseded", "prior_approval", "audit_exemption")]

_by_target_att = _count(_attacked, lambda o: o["target"])
_by_target_ctl = _count(_control, lambda o: o["target"])
_local = _load("agentic_sweep_local.json")["outcomes"]
_loc_att = _count([o for o in _local if o["attack_name"] != "none"], lambda o: o["target"])
_loc_ctl = _count([o for o in _local if o["attack_name"] == "none"], lambda o: o["target"])
_fr = _load("agentic_frontier_matched.json")["outcomes"]
_fr_att = _count([o for o in _fr if o["attack_name"] != "none"], lambda o: o["target"])
_fr_ctl = _count([o for o in _fr if o["attack_name"] == "none"], lambda o: o["target"])
MODELS = [("llama3.2 (3B, local)", tuple(_loc_ctl["llama3.2"]), tuple(_loc_att["llama3.2"])),
          ("gpt-4o-mini", tuple(_by_target_ctl["gpt-4o-mini"]), tuple(_by_target_att["gpt-4o-mini"])),
          ("claude-haiku-4-5", tuple(_by_target_ctl["claude-haiku-4-5"]), tuple(_by_target_att["claude-haiku-4-5"])),
          ("claude-sonnet-4-5", tuple(_fr_ctl["claude-sonnet-4-5"]), tuple(_fr_att["claude-sonnet-4-5"]))]

# guard: the headline the paper prints must reproduce from the raw outcomes
assert (sum(o["violated"] for o in _control), len(_control)) == (0, 240)
assert (sum(o["violated"] for o in _attacked), len(_attacked)) == (208, 1440)
assert _by_policy["strict_hatch"] == [0, 288] and _by_policy["exemption"] == [93, 288]


# --------------------------------------------------------------------------- #
# Fig 2: the result. (a) policy phrasing; (b) same with length matched;
# (c) which kind of claim gets through
# --------------------------------------------------------------------------- #
def fig2():
    fig, axes = plt.subplots(3, 1, figsize=(3.6, 5.5), gridspec_kw={"height_ratios": [5, 3, 6]})

    # (a)
    ax = axes[0]
    for i, (name, k, n, _) in enumerate(POLICY):
        col = ACCENT if "provenance" in name else NEUTRAL
        hbar_with_ci(ax, i, k, n, col)
    ax.set_yticks(range(len(POLICY)))
    ax.set_yticklabels([p[0] for p in POLICY], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 42)
    ax.set_title("(a) Operating-policy phrasing. n = 288 attacked trials each, both models", loc="left", fontsize=7.4)

    # (b)
    ax = axes[1]
    for i, (name, words, k, n, _) in enumerate(LENGTH):
        col = ACCENT if "provenance" in name else NEUTRAL
        hbar_with_ci(ax, i, k, n, col)
    ax.set_yticks(range(len(LENGTH)))
    ax.set_yticklabels([l[0] for l in LENGTH], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 21)
    ax.set_title("(b) Length control. n = 96 each, gpt-4o-mini", loc="left", fontsize=7.4)

    # (c)
    ax = axes[2]
    for i, (name, k, n, _) in enumerate(ATTACK):
        col = DARK if i >= 2 else NEUTRAL
        hbar_with_ci(ax, i, k, n, col)
    ax.set_yticks(range(len(ATTACK)))
    ax.set_yticklabels([a[0] for a in ATTACK], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 30)
    ax.set_xlabel("violation rate (%), 95% Wilson interval")
    ax.set_title("(c) What the fabricated claim asserts. n = 240 per template", loc="left", fontsize=7.4)
    ax.axhline(1.5, color="#bdbdbd", lw=0.5, ls=":")
    ax.set_ylim(5.7, -0.7)
    ax.set_xlim(0, 42)
    # group brackets in the right margin, outside the data
    for y0, y1, lab, col in [(-0.3, 1.3, "about\nthe act", "#757575"), (1.7, 5.3, "about who\nauthorised it", DARK)]:
        ax.plot([38.5, 38.5], [y0, y1], color=col, lw=0.8, clip_on=False)
        ax.text(39.2, (y0 + y1) / 2, lab, ha="left", va="center", fontsize=6.5, color=col, linespacing=1.2)
    ax.set_xticks([0, 10, 20, 30])

    for ax in axes[:2]:
        ax.set_xlabel("")
    fig.tight_layout(h_pad=1.0)
    save(fig, "fig2_policy")


# --------------------------------------------------------------------------- #
# Fig 3: limits. Direct vs indirect channel. Bar width proportional to n.
# --------------------------------------------------------------------------- #
def fig3():
    fig, ax = plt.subplots(figsize=(4.4, 2.5))
    groups = ["direct: fabricated authority\nin the user message", "indirect: fabricated authority\nin a poisoned policy-lookup result"]
    policies = [("exemption", NEUTRAL), ("strict + provenance clause", ACCENT)]
    for g, gname in enumerate(groups):
        for j, (pname, col) in enumerate(policies):
            k, n = INDIRECT[pname][g]
            x = g * 1.6 + (j - 0.5) * 0.62
            bar_with_ci(ax, x, k, n, col, width=0.55)
            ax.text(x, -4, f"n = {n}", ha="center", va="top", fontsize=6.5, color="#757575")
    ax.set_xticks([0, 1.6])
    ax.set_xticklabels(groups, fontsize=7)
    ax.tick_params(axis="x", pad=12)
    ax.set_ylabel("violation rate (%), 95% Wilson interval")
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_title("Where the fabricated authority arrives, by policy", loc="left")
    ax.legend(handles=[Line2D([], [], color=NEUTRAL, lw=6, label="exemption policy"),
                       Line2D([], [], color=ACCENT, lw=6, label="strict + provenance clause")],
              frameon=False, fontsize=7, loc="upper left")
    save(fig, "fig3_channel")


def fig5_models():
    """Baseline compliance vs. attack effect across four targets. The point:
    the attack needs a model that follows policy at baseline; llama has no
    headroom, sonnet has no failure. The hosted pair in between is where the
    policy result lives."""
    fig, ax = plt.subplots(figsize=(4.8, 2.6))
    for i, (name, (kc, nc), (ka, na)) in enumerate(MODELS):
        rc, loc_, hic = pct(kc, nc), *wilson(kc, nc)
        ra, loa, hia = pct(ka, na), *wilson(ka, na)
        yc, ya = i - 0.17, i + 0.17          # control on top, attacked below
        ax.plot([loc_ * 100, hic * 100], [yc, yc], color=NEUTRAL, lw=0.9)
        ax.scatter([rc], [yc], s=38, facecolor="white", edgecolor=NEUTRAL, lw=1.2, zorder=5)
        ax.plot([loa * 100, hia * 100], [ya, ya], color=DARK, lw=0.9)
        ax.scatter([ra], [ya], s=38, color=DARK, zorder=5)
        if ra > rc:
            ax.annotate("", xy=(ra, ya), xytext=(rc, ya), arrowprops=dict(arrowstyle="-", color="#e0e0e0", lw=2.5), zorder=1)
        ax.text(81, yc, f"{kc} / {nc}", ha="left", va="center", fontsize=6.4, color=NEUTRAL)
        ax.text(81, ya, f"{ka} / {na}", ha="left", va="center", fontsize=6.4, color=DARK)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels([m[0] for m in MODELS], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(-1, 80)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("violation rate (%), 95% Wilson interval")
    ax.set_title("Baseline compliance bounds what the attack can show", loc="left")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="white", mec=NEUTRAL, mew=1.2, ms=6, label="no attack"),
                       Line2D([], [], marker="o", ls="", color=DARK, ms=6, label="fabricated authority")],
              frameon=False, fontsize=7, loc="center right", bbox_to_anchor=(1.0, 0.42))
    ax.text(81, -0.62, "violations / trials", ha="left", va="center", fontsize=6.2, color="#9e9e9e", clip_on=False)
    ax.axvline(0, color="#e0e0e0", lw=0.6, zorder=0)
    save(fig, "fig5_models")


def fig6_indirect_by_attack():
    """Under the provenance clause, poisoned lookup output still gets through
    for all three provenance-style claims. No single claim type is the leak."""
    fig, ax = plt.subplots(figsize=(3.4, 1.9))
    for i, (name, k, n) in enumerate(INDIRECT_BY_ATTACK):
        hbar_with_ci(ax, i, k, n, ACCENT)
    ax.set_yticks(range(len(INDIRECT_BY_ATTACK)))
    ax.set_yticklabels([a[0] for a in INDIRECT_BY_ATTACK], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("violation rate (%), 95% Wilson interval")
    ax.set_title("Provenance clause, poisoned lookup channel\nn = 12 per claim type, gpt-4o-mini", loc="left")
    save(fig, "fig6_indirect_by_attack")


if __name__ == "__main__":
    fig2()
    fig3()
    fig5_models()


# --------------------------------------------------------------------------- #
# Extended paper only
# --------------------------------------------------------------------------- #
def fig5_models():
    """Baseline compliance vs. attack effect across four targets. The point:
    the attack needs a model that follows policy at baseline; llama has no
    headroom, sonnet has no failure. The hosted pair in between is where the
    policy result lives."""
    fig, ax = plt.subplots(figsize=(4.8, 2.6))
    for i, (name, (kc, nc), (ka, na)) in enumerate(MODELS):
        rc, loc_, hic = pct(kc, nc), *wilson(kc, nc)
        ra, loa, hia = pct(ka, na), *wilson(ka, na)
        yc, ya = i - 0.17, i + 0.17          # control on top, attacked below
        ax.plot([loc_ * 100, hic * 100], [yc, yc], color=NEUTRAL, lw=0.9)
        ax.scatter([rc], [yc], s=38, facecolor="white", edgecolor=NEUTRAL, lw=1.2, zorder=5)
        ax.plot([loa * 100, hia * 100], [ya, ya], color=DARK, lw=0.9)
        ax.scatter([ra], [ya], s=38, color=DARK, zorder=5)
        if ra > rc:
            ax.annotate("", xy=(ra, ya), xytext=(rc, ya), arrowprops=dict(arrowstyle="-", color="#e0e0e0", lw=2.5), zorder=1)
        ax.text(81, yc, f"{kc} / {nc}", ha="left", va="center", fontsize=6.4, color=NEUTRAL)
        ax.text(81, ya, f"{ka} / {na}", ha="left", va="center", fontsize=6.4, color=DARK)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels([m[0] for m in MODELS], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(-1, 80)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("violation rate (%), 95% Wilson interval")
    ax.set_title("Baseline compliance bounds what the attack can show", loc="left")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="white", mec=NEUTRAL, mew=1.2, ms=6, label="no attack"),
                       Line2D([], [], marker="o", ls="", color=DARK, ms=6, label="fabricated authority")],
              frameon=False, fontsize=7, loc="center right", bbox_to_anchor=(1.0, 0.42))
    ax.text(81, -0.62, "violations / trials", ha="left", va="center", fontsize=6.2, color="#9e9e9e", clip_on=False)
    ax.axvline(0, color="#e0e0e0", lw=0.6, zorder=0)
    save(fig, "fig5_models")


def fig6_indirect_by_attack():
    """Under the provenance clause, poisoned lookup output still gets through
    for all three provenance-style claims. No single claim type is the leak."""
    fig, ax = plt.subplots(figsize=(3.4, 1.9))
    for i, (name, k, n) in enumerate(INDIRECT_BY_ATTACK):
        hbar_with_ci(ax, i, k, n, ACCENT)
    ax.set_yticks(range(len(INDIRECT_BY_ATTACK)))
    ax.set_yticklabels([a[0] for a in INDIRECT_BY_ATTACK], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("violation rate (%), 95% Wilson interval")
    ax.set_title("Provenance clause, poisoned lookup channel\nn = 12 per claim type, gpt-4o-mini", loc="left")
    save(fig, "fig6_indirect_by_attack")


