import unittest
from pathlib import Path

import yaml

from src.contracts.value_inflection_plan import (
    LifecycleStage,
    TargetTransactionType,
    ValueInflectionPlan,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "value_inflection_plan.yaml"


def refs(prefix: str) -> tuple[str, ...]:
    return (f"external:{prefix}/1",)


def plan_kwargs() -> dict[str, object]:
    return {
        "plan_id": "vip-1",
        "program_thesis_ref": "external:program-thesis/1",
        "program_commitment_review_ref": "external:commitment-review/1",
        "current_stage": LifecycleStage.TARGET_OPPORTUNITY,
        "target_inflection_stage": LifecycleStage.PARTNERABLE_PACKAGE,
        "target_transaction_type": TargetTransactionType.PARTNERSHIP,
        "critical_uncertainty_refs": refs("uncertainty"),
        "planned_evidence_package_refs": refs("evidence"),
        "minimum_success_criteria_refs": refs("success"),
        "stop_condition_refs": refs("stop"),
        "estimated_cost_band_ref": "external:cost-band/1",
        "estimated_duration_band_ref": "external:duration-band/1",
        "required_capability_refs": refs("capability"),
        "capability_source_refs": refs("capability-source"),
        "expected_buyer_type_refs": refs("buyer-type"),
        "buyer_requirement_refs": refs("buyer-requirement"),
        "fallback_route_ref": "external:fallback/1",
        "human_approval_ref": "external:human-approval/1",
        "source_refs": refs("source"),
    }


class ValueInflectionPlanContractTests(unittest.TestCase):
    def test_contract_freezes_phase_four_fields_and_invariants(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        self.assertEqual(
            document["contract"]["contract_id"],
            "ValueInflectionPlan@0.1.0",
        )
        self.assertIn(
            "minimum_success_criteria_are_required_before_transfer",
            document["contract"]["invariants"],
        )
        self.assertIn(
            "no_value_inflection_plan_blocks_asset_generation",
            document["contract"]["invariants"],
        )

    def test_valid_plan_requires_the_complete_transfer_boundary(self):
        plan = ValueInflectionPlan(**plan_kwargs())
        self.assertEqual(plan.current_stage, LifecycleStage.TARGET_OPPORTUNITY)
        self.assertEqual(
            plan.target_transaction_type,
            TargetTransactionType.PARTNERSHIP,
        )

    def test_evidence_success_and_stop_conditions_cannot_be_empty(self):
        for field_name in (
            "planned_evidence_package_refs",
            "minimum_success_criteria_refs",
            "stop_condition_refs",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValueError):
                    ValueInflectionPlan(
                        **{**plan_kwargs(), field_name: ()}
                    )

    def test_all_boundary_refs_and_human_approval_must_be_external(self):
        for field_name in (
            "program_commitment_review_ref",
            "estimated_cost_band_ref",
            "fallback_route_ref",
            "human_approval_ref",
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValueError):
                    ValueInflectionPlan(
                        **{**plan_kwargs(), field_name: "local:ref/1"}
                    )

    def test_cost_and_duration_are_refs_not_runtime_numbers(self):
        with self.assertRaises(ValueError):
            ValueInflectionPlan(
                **{**plan_kwargs(), "estimated_cost_band_ref": 1000}
            )
        with self.assertRaises(ValueError):
            ValueInflectionPlan(
                **{**plan_kwargs(), "estimated_duration_band_ref": 12}
            )

    def test_contract_has_no_execution_or_scientific_gate_semantics(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        invariants = document["contract"]["invariants"]
        self.assertIn("plan_does_not_execute_experiments_or_advance_lifecycle", invariants)
        self.assertIn("plan_does_not_define_scientific_gate_truth", invariants)
        self.assertIn("plan_does_not_define_transaction_probability_or_buyer_matching", invariants)


if __name__ == "__main__":
    unittest.main()
