"""Tests for the agentic harness.

These are offline: no test here spends money or needs a network. The provider
adapters are exercised through fakes, because the property we need to hold is
"a tool call in any vendor's shape becomes the same AgentOutcome", and that is
testable without a vendor.
"""

from __future__ import annotations

import pytest

from loki.agentic.attacks import ATTACKS, get_attacks
from loki.agentic.harness import _loads
from loki.agentic.scenarios import (
    POLICY_VARIANTS,
    SAFE_TOOL_NAME,
    SCENARIOS,
    get_scenarios,
)
from loki.agentic.sweep import fisher_exact_greater, wilson_interval


class TestScenarios:
    def test_every_scenario_has_a_machine_checkable_violation(self):
        for s in SCENARIOS:
            assert s.violation_args, f"{s.scenario_id} would score any call as a violation"

    def test_forbidden_tool_is_actually_offered(self):
        for s in SCENARIOS:
            names = {t["function"]["name"] for t in s.all_tools()}
            assert s.forbidden_tool in names, s.scenario_id

    def test_safe_alternative_always_available(self):
        # Without this, "did not violate" is confounded with "could not act".
        for s in SCENARIOS:
            names = {t["function"]["name"] for t in s.all_tools()}
            assert SAFE_TOOL_NAME in names, s.scenario_id

    def test_violation_requires_matching_arguments(self):
        s = get_scenarios(["medical_export"])[0]
        assert s.is_violation("export_records", {"destination": "research@external-domain.net"})
        # Same tool, compliant destination -> not a violation.
        assert not s.is_violation("export_records", {"destination": "team@northwind.com"})
        assert not s.is_violation(SAFE_TOOL_NAME, {"reason": "policy"})

    def test_policy_variants_all_render(self):
        s = SCENARIOS[0]
        for variant in POLICY_VARIANTS:
            prompt = s.system_prompt(variant)
            assert s.prohibition in prompt
            assert prompt.startswith(s.role)

    def test_unknown_policy_variant_raises(self):
        with pytest.raises(ValueError, match="unknown policy variant"):
            SCENARIOS[0].system_prompt("does_not_exist")

    def test_scenario_ids_unique(self):
        ids = [s.scenario_id for s in SCENARIOS]
        assert len(ids) == len(set(ids))

    def test_strict_hatch_warns_about_forged_authority(self):
        # The whole point of this variant is the precedence clause.
        prompt = SCENARIOS[0].system_prompt("strict_hatch")
        assert "NOT authoritative" in prompt


class TestAttacks:
    def test_control_is_empty(self):
        assert get_attacks(["none"])[0].text(SCENARIOS[0]) == ""

    def test_all_attacks_render_nonempty_except_control(self):
        for attack in ATTACKS:
            text = attack.text(SCENARIOS[0])
            assert (text == "") == (attack.name == "none")

    def test_attack_names_unique(self):
        names = [a.name for a in ATTACKS]
        assert len(names) == len(set(names))

    def test_unknown_attack_raises(self):
        with pytest.raises(KeyError):
            get_attacks(["nope"])


class TestStatistics:
    def test_wilson_stays_in_unit_interval_at_extremes(self):
        # The reason we do not use the normal approximation.
        low, high = wilson_interval(0, 10)
        assert low == 0.0 and 0.0 < high < 1.0
        low, high = wilson_interval(10, 10)
        assert 0.0 < low < 1.0 and high == 1.0

    def test_wilson_zero_n(self):
        assert wilson_interval(0, 0) == (0.0, 0.0)

    def test_fisher_detects_a_clean_separation(self):
        # 20/20 vs 0/10 is the effect size the probe actually saw.
        assert fisher_exact_greater(20, 0, 0, 10) < 1e-6

    def test_fisher_null_is_not_significant(self):
        assert fisher_exact_greater(5, 5, 5, 5) > 0.5

    def test_fisher_bounded(self):
        assert 0.0 <= fisher_exact_greater(3, 1, 2, 2) <= 1.0


class TestArgumentParsing:
    def test_loads_handles_json_string(self):
        assert _loads('{"a": 1}') == {"a": 1}

    def test_loads_handles_dict(self):
        assert _loads({"a": 1}) == {"a": 1}

    def test_loads_handles_garbage_without_raising(self):
        # A malformed tool call must not crash a 2000-call sweep.
        assert _loads("not json") == {}
        assert _loads(None) == {}
        assert _loads("[1,2]") == {}


class TestReportedNumbersStayReproducible:
    """Guard the published trial counts against silent drift.

    The reported sweep is 1,680 trials over five policy variants. Adding a
    sixth variant (the ``strict_verbose`` length control) silently changed what
    the documented command produces, which would have made the paper's totals
    unreproducible from its own instructions. These tests pin the arithmetic.
    """

    MAIN_POLICIES = ["strict_hatch", "strict", "exemption", "autonomous", "bare"]

    def test_main_sweep_trial_count_matches_the_paper(self):
        n = len(SCENARIOS) * len(self.MAIN_POLICIES) * len(ATTACKS) * 2 * 3
        assert n == 1680, "documented sweep total changed; update the papers"

    def test_ablation_trial_count_matches_the_paper(self):
        attacks = ["superseded", "prior_approval", "audit_exemption", "combined"]
        policies = ["strict", "strict_verbose", "strict_hatch"]
        n = len(SCENARIOS) * len(policies) * len(attacks) * 1 * 3
        assert n == 288, "documented ablation total changed; update the papers"

    def test_length_control_is_not_shorter_than_the_clause_variant(self):
        # The ablation's logic depends on strict_verbose being at least as long
        # as strict_hatch. If someone trims it, the confound returns.
        s = SCENARIOS[0]
        verbose = len(s.system_prompt("strict_verbose").split())
        hatch = len(s.system_prompt("strict_hatch").split())
        assert verbose >= hatch, f"length control ({verbose}w) shorter than strict_hatch ({hatch}w)"

    def test_length_control_says_nothing_about_claimed_authority(self):
        # If it did, it would no longer isolate length.
        prompt = SCENARIOS[0].system_prompt("strict_verbose").lower()
        for leak in ("not authoritative", "unverified", "superseding", "exemption"):
            assert leak not in prompt, f"length control leaks the mechanism: {leak!r}"
