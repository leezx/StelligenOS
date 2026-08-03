from __future__ import annotations

import unittest

from pathlib import Path

import yaml

from extensions.stop_rule.contracts import (
    DEFAULT_SUFFICIENCY_BASELINES,
    EXTENSION_STATUS,
    GOVERNED_EXTENSION_STATUS,
    CalibrationStatus,
    EvidenceLedgerSnapshot,
    EvidenceSufficiencyContract,
    GovernanceStatus,
    StopDecision,
    StopVerdict,
    SufficiencyBaseline,
    evaluate_stop_condition,
    is_actionable,
)
from src.capabilities.gates import GATE_GROUPS


REPO_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_MANIFEST = REPO_ROOT / "extensions" / "stop_rule" / "extension.yaml"


def _contract(**overrides: object) -> EvidenceSufficiencyContract:
    defaults: dict[str, object] = {
        "gate_id": "tumor_cell_surface_availability",
        "contract_version": "0.1.0",
        "min_independent_evidence": 3,
        "max_unresolved_conflicts": 0,
        "min_confidence": 0.8,
        "require_major_unknown_cleared": True,
        "max_evidence_search_iterations": 3,
        "calibration_status": CalibrationStatus.EXPERT_CALIBRATED,
        "rationale_ref": "external:policies/stop-rule/t7",
    }
    defaults.update(overrides)
    return EvidenceSufficiencyContract(**defaults)  # type: ignore[arg-type]


def _snapshot(**overrides: object) -> EvidenceLedgerSnapshot:
    defaults: dict[str, object] = {
        "gate_id": "tumor_cell_surface_availability",
        "ledger_ref": "external:ledger/crc/t7",
        "independent_supporting_count": 3,
        "independent_opposing_count": 0,
        "unknown_count": 4,
        "unresolved_conflict_count": 0,
        "major_unknown_count": 0,
        "aggregate_confidence": 0.85,
        "completed_search_iterations": 1,
    }
    defaults.update(overrides)
    return EvidenceLedgerSnapshot(**defaults)  # type: ignore[arg-type]


def _baseline(**overrides: object) -> SufficiencyBaseline:
    defaults: dict[str, object] = {
        "gate_group": "target_opportunity",
        "min_independent_evidence": 3,
        "max_unresolved_conflicts": 0,
        "min_confidence": 0.8,
        "require_major_unknown_cleared": True,
        "max_evidence_search_iterations": 3,
    }
    defaults.update(overrides)
    return SufficiencyBaseline(**defaults)  # type: ignore[arg-type]


class StopRuleVerdictTests(unittest.TestCase):
    def test_all_criteria_met_stops_the_search(self) -> None:
        decision = evaluate_stop_condition(_contract(), _snapshot())
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)
        self.assertEqual(decision.unmet_criteria, ())
        self.assertFalse(decision.requires_human_decision)

    def test_unknown_evidence_alone_does_not_block_sufficiency(self) -> None:
        """unknown is not negative: a large unknown count is not a failure."""
        decision = evaluate_stop_condition(_contract(), _snapshot(unknown_count=172))
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)

    def test_insufficient_evidence_with_budget_left_continues(self) -> None:
        decision = evaluate_stop_condition(
            _contract(), _snapshot(independent_supporting_count=1)
        )
        self.assertEqual(decision.verdict, StopVerdict.INSUFFICIENT_CONTINUE)
        self.assertIn("min_independent_evidence", decision.unmet_criteria)
        self.assertEqual(decision.remaining_search_iterations, 2)
        self.assertFalse(decision.requires_human_decision)

    def test_exhausted_budget_escalates_and_is_never_a_failure(self) -> None:
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(independent_supporting_count=1, completed_search_iterations=3),
        )
        self.assertEqual(decision.verdict, StopVerdict.INSUFFICIENT_EXHAUSTED)
        self.assertTrue(decision.requires_human_decision)
        self.assertEqual(decision.remaining_search_iterations, 0)
        # The three-valued verdict must not contain a FAIL-like member.
        self.assertNotIn("fail", [member.value for member in StopVerdict])

    def test_overrunning_the_budget_clamps_to_zero_remaining(self) -> None:
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(independent_supporting_count=1, completed_search_iterations=99),
        )
        self.assertEqual(decision.remaining_search_iterations, 0)
        self.assertEqual(decision.verdict, StopVerdict.INSUFFICIENT_EXHAUSTED)

    def test_each_criterion_is_reported_independently(self) -> None:
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(
                independent_supporting_count=0,
                unresolved_conflict_count=2,
                aggregate_confidence=0.1,
                major_unknown_count=5,
            ),
        )
        self.assertEqual(
            set(decision.unmet_criteria),
            {
                "min_independent_evidence",
                "max_unresolved_conflicts",
                "min_confidence",
                "require_major_unknown_cleared",
            },
        )

    def test_major_unknown_is_ignored_when_not_required(self) -> None:
        decision = evaluate_stop_condition(
            _contract(require_major_unknown_cleared=False),
            _snapshot(major_unknown_count=5),
        )
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)

    def test_mismatched_gate_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_stop_condition(_contract(), _snapshot(gate_id="epitope_landscape"))


class DirectionNeutralSufficiencyTests(unittest.TestCase):
    """Sufficiency must not be biased toward the supporting direction.

    Without this, a decisively negative target has no way to end the search and
    is searched forever, which is the failure mode the Stop Rule exists to
    prevent.
    """

    def test_opposing_only_evidence_can_end_the_search(self) -> None:
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(
                independent_supporting_count=0, independent_opposing_count=3
            ),
        )
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)
        self.assertEqual(decision.unmet_criteria, ())

    def test_opposing_only_sufficiency_is_not_a_failure_verdict(self) -> None:
        """Sufficiency says "we can judge now", not "the answer is no"."""
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(
                independent_supporting_count=0, independent_opposing_count=9
            ),
        )
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)
        # The decision carries no direction and no pass/fail signal at all.
        self.assertFalse(hasattr(decision, "evidence_direction"))
        self.assertFalse(hasattr(decision, "gate_status"))

    def test_neither_direction_reaching_threshold_is_insufficient(self) -> None:
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(
                independent_supporting_count=2, independent_opposing_count=2
            ),
        )
        self.assertEqual(decision.verdict, StopVerdict.INSUFFICIENT_CONTINUE)
        self.assertIn("min_independent_evidence", decision.unmet_criteria)

    def test_directions_are_not_summed(self) -> None:
        """2 supporting + 2 opposing is conflict, not 4 units of evidence."""
        snapshot = _snapshot(
            independent_supporting_count=2, independent_opposing_count=2
        )
        self.assertEqual(snapshot.strongest_direction_count, 2)

    def test_strongest_direction_does_not_reveal_which_direction(self) -> None:
        supporting = _snapshot(
            independent_supporting_count=5, independent_opposing_count=0
        )
        opposing = _snapshot(
            independent_supporting_count=0, independent_opposing_count=5
        )
        self.assertEqual(
            supporting.strongest_direction_count, opposing.strongest_direction_count
        )


def _decision(**overrides: object) -> StopDecision:
    defaults: dict[str, object] = {
        "gate_id": "tumor_cell_surface_availability",
        "verdict": StopVerdict.SUFFICIENT,
        "unmet_criteria": (),
        "remaining_search_iterations": 2,
        "requires_human_decision": False,
        "actionable": False,
        "calibration_status": CalibrationStatus.EXPERT_CALIBRATED,
        "governance_status": GovernanceStatus.NOT_GOVERNED,
        "extension_status": EXTENSION_STATUS,
        "contract_version": "0.1.0",
        "ledger_ref": "external:ledger/crc/t7",
    }
    defaults.update(overrides)
    return StopDecision(**defaults)  # type: ignore[arg-type]


class ActionabilityGatingTests(unittest.TestCase):
    """Sufficiency, calibration and governance are three separate gates.

    Expert calibration reviews the numbers. Governance authorises use. Neither
    substitutes for the other, and EXT-04's own status caps both.
    """

    def test_proposed_baseline_sufficiency_is_not_actionable(self) -> None:
        decision = evaluate_stop_condition(
            _contract(calibration_status=CalibrationStatus.PROPOSED_BASELINE),
            _snapshot(),
        )
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)
        self.assertFalse(decision.actionable)
        self.assertEqual(
            decision.calibration_status, CalibrationStatus.PROPOSED_BASELINE
        )

    def test_calibrated_but_ungoverned_contract_is_not_actionable(self) -> None:
        """The blocker from PR #43 round 2: calibration alone must not authorise."""
        decision = evaluate_stop_condition(
            _contract(
                calibration_status=CalibrationStatus.EXPERT_CALIBRATED,
                governance_status=GovernanceStatus.NOT_GOVERNED,
            ),
            _snapshot(),
        )
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)
        self.assertFalse(decision.actionable)
        self.assertEqual(decision.governance_status, GovernanceStatus.NOT_GOVERNED)

    def test_calibrated_and_governed_contract_is_still_blocked_by_extension_status(
        self,
    ) -> None:
        """EXT-04 is active_design, so nothing it produces may be acted upon yet."""
        self.assertNotEqual(EXTENSION_STATUS, GOVERNED_EXTENSION_STATUS)
        decision = evaluate_stop_condition(
            _contract(
                calibration_status=CalibrationStatus.EXPERT_CALIBRATED,
                governance_status=GovernanceStatus.GOVERNED,
                governance_approval_ref="external:governance/pr-99-approval",
            ),
            _snapshot(),
        )
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)
        self.assertFalse(decision.actionable)
        self.assertEqual(decision.extension_status, EXTENSION_STATUS)

    def test_module_status_matches_the_extension_manifest(self) -> None:
        """The mirrored status must not drift from extension.yaml."""
        manifest = yaml.safe_load(EXTENSION_MANIFEST.read_text())
        self.assertEqual(manifest["extension"]["status"], EXTENSION_STATUS)

    def test_actionable_requires_all_three_gates_open(self) -> None:
        matrix = [
            (StopVerdict.SUFFICIENT, True, True, GOVERNED_EXTENSION_STATUS, True),
            (StopVerdict.SUFFICIENT, True, True, "active_design", False),
            (StopVerdict.SUFFICIENT, True, False, GOVERNED_EXTENSION_STATUS, False),
            (StopVerdict.SUFFICIENT, False, True, GOVERNED_EXTENSION_STATUS, False),
            (
                StopVerdict.INSUFFICIENT_CONTINUE,
                True,
                True,
                GOVERNED_EXTENSION_STATUS,
                False,
            ),
            (
                StopVerdict.INSUFFICIENT_EXHAUSTED,
                True,
                True,
                GOVERNED_EXTENSION_STATUS,
                False,
            ),
        ]
        for verdict, calibrated, governed, ext_status, expected in matrix:
            with self.subTest(
                verdict=verdict,
                calibrated=calibrated,
                governed=governed,
                ext_status=ext_status,
            ):
                self.assertEqual(
                    is_actionable(
                        verdict=verdict,
                        calibration_status=(
                            CalibrationStatus.EXPERT_CALIBRATED
                            if calibrated
                            else CalibrationStatus.PROPOSED_BASELINE
                        ),
                        governance_status=(
                            GovernanceStatus.GOVERNED
                            if governed
                            else GovernanceStatus.NOT_GOVERNED
                        ),
                        extension_status=ext_status,
                    ),
                    expected,
                )

    def test_insufficient_verdicts_are_never_actionable(self) -> None:
        for calibration in CalibrationStatus:
            for iterations in (1, 99):
                with self.subTest(calibration=calibration, iterations=iterations):
                    decision = evaluate_stop_condition(
                        _contract(calibration_status=calibration),
                        _snapshot(
                            independent_supporting_count=0,
                            completed_search_iterations=iterations,
                        ),
                    )
                    self.assertFalse(decision.actionable)

    def test_forged_actionability_is_rejected(self) -> None:
        for overrides in (
            {"calibration_status": CalibrationStatus.PROPOSED_BASELINE},
            {"governance_status": GovernanceStatus.NOT_GOVERNED},
            {"extension_status": "active_design"},
            {
                "verdict": StopVerdict.INSUFFICIENT_CONTINUE,
                "unmet_criteria": ("min_confidence",),
            },
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    _decision(actionable=True, **overrides)

    def test_hidden_actionability_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _decision(
                actionable=False,
                governance_status=GovernanceStatus.GOVERNED,
                extension_status=GOVERNED_EXTENSION_STATUS,
            )


class GovernanceReferenceTests(unittest.TestCase):
    def test_governed_contract_must_cite_an_approval(self) -> None:
        with self.assertRaises(ValueError):
            _contract(governance_status=GovernanceStatus.GOVERNED)

    def test_governance_approval_ref_must_be_external(self) -> None:
        with self.assertRaises(ValueError):
            _contract(
                governance_status=GovernanceStatus.GOVERNED,
                governance_approval_ref="docs/handoff/2026-08-03.md",
            )

    def test_ungoverned_contract_must_not_cite_an_approval(self) -> None:
        with self.assertRaises(ValueError):
            _contract(
                governance_status=GovernanceStatus.NOT_GOVERNED,
                governance_approval_ref="external:governance/pr-99-approval",
            )

    def test_contracts_default_to_ungoverned(self) -> None:
        self.assertEqual(_contract().governance_status, GovernanceStatus.NOT_GOVERNED)
        self.assertFalse(_contract().is_governed)


class StopRuleContractValidationTests(unittest.TestCase):
    def test_gate_id_must_exist_in_the_frozen_kernel_catalog(self) -> None:
        with self.assertRaises(ValueError):
            _contract(gate_id="not_a_real_gate")

    def test_rationale_ref_must_be_external(self) -> None:
        with self.assertRaises(ValueError):
            _contract(rationale_ref="docs/policies/stop-rule.md")

    def test_ledger_ref_must_be_external(self) -> None:
        with self.assertRaises(ValueError):
            _snapshot(ledger_ref="logs/ledger.tsv")

    def test_search_budget_must_allow_at_least_one_iteration(self) -> None:
        with self.assertRaises(ValueError):
            _contract(max_evidence_search_iterations=0)

    def test_confidence_threshold_must_be_a_probability(self) -> None:
        with self.assertRaises(ValueError):
            _contract(min_confidence=0.0)
        with self.assertRaises(ValueError):
            _contract(min_confidence=1.5)

    def test_negative_counts_are_rejected(self) -> None:
        for field in (
            "independent_supporting_count",
            "independent_opposing_count",
            "unknown_count",
            "unresolved_conflict_count",
            "major_unknown_count",
            "completed_search_iterations",
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    _snapshot(**{field: -1})

    def test_aggregate_confidence_must_be_a_probability(self) -> None:
        with self.assertRaises(ValueError):
            _snapshot(aggregate_confidence=-0.1)
        with self.assertRaises(ValueError):
            _snapshot(aggregate_confidence=1.1)


class SufficiencyBaselineTests(unittest.TestCase):
    def test_every_kernel_gate_group_has_a_baseline(self) -> None:
        self.assertEqual(set(DEFAULT_SUFFICIENCY_BASELINES), set(GATE_GROUPS))

    def test_baseline_rejects_unknown_gate_group(self) -> None:
        with self.assertRaises(ValueError):
            _baseline(gate_group="not_a_group")

    def test_baseline_rejects_evidence_threshold_below_one(self) -> None:
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _baseline(min_independent_evidence=value)

    def test_baseline_rejects_negative_conflict_allowance(self) -> None:
        with self.assertRaises(ValueError):
            _baseline(max_unresolved_conflicts=-1)

    def test_baseline_rejects_out_of_range_confidence(self) -> None:
        for value in (-0.5, 0.0, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _baseline(min_confidence=value)

    def test_baseline_rejects_non_positive_search_budget(self) -> None:
        for value in (0, -3):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _baseline(max_evidence_search_iterations=value)

    def test_baseline_and_contract_share_the_same_numeric_constraints(self) -> None:
        """Both carry the same thresholds, so both must reject the same values."""
        for overrides in (
            {"min_independent_evidence": 0},
            {"max_unresolved_conflicts": -1},
            {"min_confidence": 0.0},
            {"min_confidence": 1.5},
            {"max_evidence_search_iterations": 0},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    _baseline(**overrides)
                with self.assertRaises(ValueError):
                    _contract(**overrides)

    def test_shipped_baselines_are_within_their_own_constraints(self) -> None:
        for baseline in DEFAULT_SUFFICIENCY_BASELINES.values():
            self.assertGreaterEqual(baseline.min_independent_evidence, 1)
            self.assertGreaterEqual(baseline.max_evidence_search_iterations, 1)
            self.assertGreater(baseline.min_confidence, 0.0)
            self.assertLessEqual(baseline.min_confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
