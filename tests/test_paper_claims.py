"""Guard the paper against silently drifting from the data.

Every quantitative claim in paper/main.tex must be traceable to a committed
artifact in results/. This test extracts the numbers from the LaTeX source and
re-derives them from the JSON, so editing one without the other fails CI.

This is the safeguard we wish had existed earlier: the project previously
published a "25% -> 48% improvement" that no artifact supported.
"""

from __future__ import annotations

import json
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(REPO, "paper", "main.tex")
RESULTS = os.path.join(REPO, "results")

pytestmark = pytest.mark.skipif(not os.path.exists(PAPER), reason="paper/main.tex not present")


@pytest.fixture(scope="module")
def paper_text() -> str:
    with open(PAPER, encoding="utf-8") as handle:
        return handle.read()


@pytest.fixture(scope="module")
def judge_accuracy() -> dict:
    path = os.path.join(RESULTS, "judge_accuracy_human.json")
    if not os.path.exists(path):
        pytest.skip("judge_accuracy_human.json not generated yet")
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    return {j["judge"]: j for j in payload["judges"]} | {"_root": payload}


def _pct(value: float) -> int:
    return round(100 * value)


class TestPaperMatchesData:
    def test_human_asr(self, paper_text, judge_accuracy):
        actual = _pct(judge_accuracy["_root"]["human_asr"])
        assert f"is {actual}\\%" in paper_text or f"\\emph{{{actual}\\%}}" in paper_text

    @pytest.mark.parametrize(
        "judge,field",
        [
            ("ollama", "accuracy"),
            ("heuristic", "accuracy"),
            ("openai", "accuracy"),
            ("ollama", "reported_asr"),
            ("heuristic", "reported_asr"),
            ("openai", "reported_asr"),
        ],
    )
    def test_judge_percentages_appear(self, paper_text, judge_accuracy, judge, field):
        value = _pct(judge_accuracy[judge][field])
        assert f"{value}\\%" in paper_text, f"{judge}.{field} = {value}% is not stated in the paper"

    @pytest.mark.parametrize(
        "judge,label",
        [
            ("ollama", r"\\texttt\{llama3\.2\}"),
            ("heuristic", r"Refusal heuristic"),
            ("openai", r"\\texttt\{gpt-4o-mini\}"),
        ],
    )
    def test_table_row_matches_data(self, paper_text, judge_accuracy, judge, label):
        """Parse the judge's actual table row, not just 'does this % appear anywhere'.

        A substring check is too weak: a wrong table value can coincide with a
        correct number elsewhere in the prose, which is exactly how a paper
        drifts from its data unnoticed.
        """
        row = re.search(rf"^{label}\s*&(.+?)\\\\", paper_text, re.MULTILINE)
        assert row, f"no results table row found for {judge}"
        cells = [c.strip() for c in row.group(1).split("&")]
        # Columns: Acc, kappa, Prec, Rec, FalsePos, ReportedASR
        assert len(cells) == 6, f"expected 6 columns for {judge}, got {cells}"

        def num(cell: str) -> float:
            return float(re.sub(r"[^0-9.]", "", cell.replace("\\textbf{", "")))

        record = judge_accuracy[judge]
        assert num(cells[0]) == _pct(record["accuracy"])
        assert abs(num(cells[1]) - record["kappa"]) < 0.011
        assert num(cells[2]) == _pct(record["precision"])
        assert num(cells[3]) == _pct(record["recall"])
        assert num(cells[4]) == record["false_positives"]
        assert num(cells[5]) == _pct(record["reported_asr"])

    def test_false_positive_counts(self, paper_text, judge_accuracy):
        for judge in ("ollama", "heuristic", "openai"):
            count = judge_accuracy[judge]["false_positives"]
            assert str(count) in paper_text, f"{judge} FP={count} missing from paper"

    def test_asr_spread_claim(self, paper_text, judge_accuracy):
        """The headline '69-point swing' must equal max minus min reported ASR."""
        reported = [judge_accuracy[j]["reported_asr"] for j in ("ollama", "heuristic", "openai")]
        spread = _pct(max(reported) - min(reported))
        assert f"{spread}-point" in paper_text
        assert f"{spread}-Point" in paper_text or f"{spread}-point" in paper_text

    def test_constant_baseline_claim(self, paper_text, judge_accuracy):
        """'Always refused' baseline = the human refusal rate."""
        baseline = _pct(1 - judge_accuracy["_root"]["human_asr"])
        assert f"{baseline}\\%" in paper_text

    def test_llama_worse_than_constant_baseline(self, judge_accuracy):
        """The paper's core claim about the local judge."""
        baseline = 1 - judge_accuracy["_root"]["human_asr"]
        assert judge_accuracy["ollama"]["accuracy"] < baseline

    def test_n120_table_matches(self, paper_text):
        base_path = os.path.join(RESULTS, "base_n120_gpt.json")
        trained_path = os.path.join(RESULTS, "trained_n120_gpt.json")
        if not (os.path.exists(base_path) and os.path.exists(trained_path)):
            pytest.skip("n120 results not present")
        with open(base_path, encoding="utf-8") as fh:
            base = json.load(fh)["summary"]
        with open(trained_path, encoding="utf-8") as fh:
            trained = json.load(fh)["summary"]
        for value in (
            _pct(base["format_rate"]),
            _pct(trained["format_rate"]),
            _pct(trained["tag_compliance_rate"]),
        ):
            assert f"{value}\\%" in paper_text

    def test_no_stale_inflated_claim_presented_as_true(self, paper_text):
        """The retracted 25->48 number may appear only as the refuted artifact.

        Checks a window on *both* sides: the disclaimer may legitimately precede
        the figure ("an artifact of...: ASR rose to 48%") or follow it
        ("...rose to 48%. That figure is an artifact.").
        """
        for match in re.finditer(r"48\\%", paper_text):
            start, end = match.start(), match.end()
            window = paper_text[max(0, start - 400) : end + 400]
            assert re.search(
                r"artifact|unvalidated|bad judge|would have been|judge error"
                r"|\\texttt\{llama3\.2\} judge",
                window,
                re.IGNORECASE,
            ), "The 48% figure must be presented as a refuted artifact, not a result"

    def test_page_limit_plausible(self, paper_text):
        """Short-paper track is 4 pages; references do not count."""
        body = paper_text.split("\\begin{thebibliography}")[0]
        words = len(re.findall(r"\b\w+\b", body))
        assert words < 3200, f"{words} words is likely over the 4-page limit"


class TestAgenticClaims:
    """The agentic results are the paper's primary contribution."""

    @pytest.fixture(scope="class")
    def agentic_doc(self) -> str:
        path = os.path.join(RESULTS, "AGENTIC_RESULTS.md")
        if not os.path.exists(path):
            pytest.skip("AGENTIC_RESULTS.md not present")
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def test_matched_contrast_matches_artifact(self, paper_text):
        """The strongest single claim: complete separation, 18/18 vs 0/18."""
        path = os.path.join(RESULTS, "agentic_matched_contrast.json")
        if not os.path.exists(path):
            pytest.skip("matched contrast not present")
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        exemption_hits, exemption_n = data["exemption"]
        hatch_hits, hatch_n = data["strict_hatch"]
        assert f"{exemption_hits}/{exemption_n}" in paper_text
        assert f"{hatch_hits}/{hatch_n}" in paper_text
        # A complete separation is what makes the claim strong; assert it holds.
        assert exemption_hits == exemption_n and hatch_hits == 0
        assert data["fisher_p"] < 1e-9

    @pytest.mark.parametrize(
        "claim",
        ["208/1440", "0/240", "0/288", "11/96", "0/96", "10/840", "198/840", "0/18"],
    )
    def test_headline_counts_agree_with_results_doc(self, paper_text, agentic_doc, claim):
        """Every count in the paper must also appear in the results document."""
        assert claim in agentic_doc, f"{claim} not backed by AGENTIC_RESULTS.md"
        assert claim in paper_text, f"{claim} missing from paper"

    def test_control_is_at_floor(self, agentic_doc):
        """The 'every violation is attributable to the attack' claim needs 0/240."""
        assert "0/240" in agentic_doc

    def test_adaptive_attack_limitation_is_disclosed(self, paper_text):
        """We failed to build a strong adaptive attack; that must be stated."""
        assert re.search(r"no competent adaptive attacker|too weak to test", paper_text, re.I), (
            "The failed adaptive attack must be disclosed as a limitation"
        )

    def test_local_model_reported_separately(self, paper_text):
        """llama3.2 has no headroom (67.5% control), so it must not be pooled."""
        assert "67.5\\%" in paper_text
        assert re.search(r"separately|no headroom", paper_text, re.I)

    def test_forced_indirect_channel_claim_matches_artifact(self, paper_text):
        """The new indirect result weakens the mitigation, so it must be guarded."""
        path = os.path.join(RESULTS, "agentic_indirect_forced.json")
        if not os.path.exists(path):
            pytest.skip("forced indirect result not present")
        with open(path, encoding="utf-8") as handle:
            report = json.load(handle)["report"]
        assert report["clean"] == {"violations": 0, "n": 72}
        assert report["poisoned"] == {"violations": 51, "n": 72}
        assert report["by_policy_poisoned"]["strict_hatch"] == {
            "violations": 15,
            "n": 36,
        }
        for claim in ("0/72", "51/72", "15/36"):
            assert claim in paper_text
        assert re.search(r"channel-specific|not a\\s+runtime provenance system", paper_text, re.I)


class TestAdaptiveAttack:
    """The adaptive-attack null is only meaningful if the control was broken."""

    @pytest.fixture(scope="class")
    def adaptive(self) -> dict:
        path = os.path.join(RESULTS, "agentic_adaptive_full.json")
        if not os.path.exists(path):
            pytest.skip("full adaptive run not present")
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)["summary"]

    def test_control_was_actually_broken(self, adaptive):
        """Without this, a 0/8 on the defence proves nothing about the defence.

        This is exactly the check our hand-written adaptive attempt failed: it
        scored 0 against both the defence and the control, so it discriminated
        nothing.
        """
        assert adaptive["control_broken"] > 0, (
            "The attacker never broke the control policy, so its failure "
            "against the defence is uninformative and must not be reported "
            "as robustness."
        )
        # Demand the attacker be strongly potent, not merely non-zero, but do
        # not pin an exact count: the attacker samples at temperature 1.0, and
        # an independent 10-round replication scored 7/8 rather than 8/8.
        assert adaptive["control_broken"] >= 0.75 * adaptive["control_n"], (
            f"control only broken {adaptive['control_broken']}/{adaptive['control_n']}; "
            "too weak to make the defence's null informative"
        )

    def test_replication_agrees(self):
        """Two independent runs, different round budgets, must agree on 0/8.

        The value of the adaptive result rests on it not being a single lucky
        sample, so both recorded runs are checked rather than only the one the
        paper quotes.
        """
        paths = [
            os.path.join(RESULTS, "agentic_adaptive_full.json"),
            os.path.join(RESULTS, "agentic_adaptive.json"),
        ]
        present = [p for p in paths if os.path.exists(p)]
        if len(present) < 2:
            pytest.skip("need both adaptive runs for the replication check")
        for path in present:
            with open(path, encoding="utf-8") as handle:
                s = json.load(handle)["summary"]
            assert s["test_broken"] == 0, f"{path}: defence breached"
            assert s["control_broken"] > 0, f"{path}: control not broken"

    def test_defence_held(self, adaptive):
        assert adaptive["test_broken"] == 0

    def test_verdict_is_informative(self, adaptive):
        assert "INFORMATIVE NULL" in adaptive["verdict"]

    def test_paper_reports_the_counts(self, paper_text, adaptive):
        control = f"{adaptive['control_broken']}/{adaptive['control_n']}"
        test = f"{adaptive['test_broken']}/{adaptive['test_n']}"
        assert control in paper_text
        assert test in paper_text

    def test_paper_does_not_overclaim_robustness(self, paper_text):
        """The attacker is gpt-4o-mini; a stronger one may still succeed."""
        assert re.search(
            r"stronger or RL-trained attacker may yet succeed|may yet succeed",
            paper_text,
            re.IGNORECASE,
        ), "The paper must bound the robustness claim by the attacker's strength"
