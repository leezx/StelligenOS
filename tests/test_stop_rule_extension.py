from __future__ import annotations

import unittest

from extensions.stop_rule.contracts import (
    DEFAULT_SUFFICIENCY_BASELINES,
    CalibrationStatus,
    EvidenceLedgerSnapshot,
    EvidenceSufficiencyContract,
    StopVerdict,
    evaluate_stop_condition,
)
from src.capabilities.gates import GATE_GROUPS


def _contract(**overrides: object) -> EvidenceSufficiencyContract:
    defaults: dict[str, object] = {
        "gate_id": "tumor_cell_surface_availability",
        "contract_version": "0.1.0",
        "min_independent_supporting": 3,
        "max_unresolved_conflicts": 0,
        "min_confidence": 0.8,
        "require_major_unknown_cleared": True,
        "max_evidence_search_iterations": 3,
        "calibration_status": CalibrationStatus.PROPOSED_BASELINE,
        "rationale_ref": "external:policies/stop-rule/t7",
    }
    defaults.update(overrides)
    return EvidenceSufficiencyContract(**defaults)  # type: ignore[arg-type]


def _snapshot(**overrides: object) -> EvidenceLedgerSnapshot:
    defaults: dict[str, object] = {
        "gate_id": "tumor_cell_surface_availability",
        "ledger_ref": "external:ledger/crc/t7",
        "independent_supporting_count": 3,
        "opposing_count": 0,
        "unknown_count": 4,
        "unresolved_conflict_count": 0,
        "major_unknown_count": 0,
        "aggregate_confidence": 0.85,
        "completed_search_iterations": 1,
    }
    defaults.update(overrides)
    return EvidenceLedgerSnapshot(**defaults)  # type: ignore[arg-type]


class StopRuleVerdictTests(unittest.TestCase):
    def test_all_criteria_met_stops_the_search(self) -> None:
        decision = evaluate_stop_condition(_contract(), _snapshot())
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)
        self.assertEqual(decision.unmet_criteria, ())
        self.assertFalse(decision.requires_human_decision)

    def test_unknown_evidence_alone_does_not_block_sufficiency(self) -> None:
        """unknown is not negative: a large unknown count is not a failure."""
        decision = evaluate_stop_condition(
            _contract(), _snapshot(unknown_count=172)
        )
        self.assertEqual(decision.verdict, StopVerdict.SUFFICIENT)

    def test_insufficient_evidence_with_budget_left_continues(self) -> None:
        decision = evaluate_stop_condition(
            _contract(), _snapshot(independent_supporting_count=1)
        )
        self.assertEqual(decision.verdict, StopVerdict.INSUFFICIENT_CONTINUE)
        self.assertIn("min_independent_supporting", decision.unmet_criteria)
        self.assertEqual(decision.remaining_search_iterations, 2)
        self.assertFalse(decision.requires_human_decision)

    def test_exhausted_budget_escalates_and_is_never_a_failure(self) -> None:
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(
                independent_supporting_count=1, completed_search_iterations=3
            ),
        )
        self.assertEqual(decision.verdict, StopVerdict.INSUFFICIENT_EXHAUSTED)
        self.assertTrue(decision.requires_human_decision)
        self.assertEqual(decision.remaining_search_iterations, 0)
        # The three-valued verdict must not contain a FAIL-like member.
        self.assertNotIn(
            "fail", [member.value for member in StopVerdict]
        )

    def test_overrunning_the_budget_clamps_to_zero_remaining(self) -> None:
        decision = evaluate_stop_condition(
            _contract(),
            _snapshot(
                independent_supporting_count=1, completed_search_iterations=99
            ),
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
                "min_independent_supporting",
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
            evaluate_stop_condition(
                _contract(),
                _snapshot(gate_id="epitope_landscape"),
            )


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
        with self.assertRaises(ValueError):
            _snapshot(independent_supporting_count=-1)


class SufficiencyBaselineTests(unittest.TestCase):
    def test_every_kernel_gate_group_has_a_baseline(self) -> None:
        self.assertEqual(set(DEFAULT_SUFFICIENCY_BASELINES), set(GATE_GROUPS))

    def test_baselines_are_marked_as_uncalibrated_in_the_manifest(self) -> None:
        """The numbers are expert suggestions, not calibrated thresholds."""
        for baseline in DEFAULT_SUFFICIENCY_BASELINES.values():
            self.assertGreaterEqual(baseline.min_independent_supporting, 1)
            self.assertGreaterEqual(baseline.max_evidence_search_iterations, 1)

    def test_baseline_rejects_unknown_gate_group(self) -> None:
        baseline = DEFAULT_SUFFICIENCY_BASELINES["target_opportunity"]
        with self.assertRaises(ValueError):
            type(baseline)(
                gate_group="not_a_group",
                min_independent_supporting=1,
                max_unresolved_conflicts=0,
                min_confidence=0.5,
                require_major_unknown_cleared=True,
                max_evidence_search_iterations=1,
            )


if __name__ == "__main__":
    unittest.main()
