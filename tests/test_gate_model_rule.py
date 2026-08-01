import unittest
from pathlib import Path

import yaml

from genmodules.gate_model_rule.core.contracts import (
    GateModelRuleRef,
    HistoricalRuleDescriptor,
    RuleApplicabilityAssessment,
    RuleApplicabilityBundle,
    RuleReview,
    RULE_MODEL_IMPLEMENTATION,
    validate_external_ref,
)


class GateModelRuleContractTests(unittest.TestCase):
    def test_rule_model_identity_is_versioned_and_gate_bound(self):
        ref = GateModelRuleRef(
            "adc-target-opportunity-rule",
            "0.1.0",
            "target_population_mapping",
        )
        self.assertEqual(ref.as_string(), "adc-target-opportunity-rule@0.1.0")

    def test_unknown_gate_is_rejected_against_frozen_topology(self):
        with self.assertRaises(ValueError):
            GateModelRuleRef("rule-model", "0.1.0", "not_a_gate")

    def test_historical_predicates_cannot_become_executable(self):
        with self.assertRaises(ValueError):
            HistoricalRuleDescriptor(
                "rule-1",
                "gate:target_population_mapping",
                "contrastive",
                "positive",
                "low",
                ("external:source/1",),
                ("external:limitation/1",),
                natural_language_predicates_executable=True,
            )

    def test_applicability_bundle_requires_external_review_references(self):
        assessment = RuleApplicabilityAssessment(
            "rule-1",
            "uncertain",
            "external:rationale/1",
            ("external:evidence/1",),
        )
        bundle = RuleApplicabilityBundle(
            "1.0.0",
            "external:candidate/1",
            "gate:target_population_mapping",
            RuleReview(
                "external:reviewer/1",
                "2026-08-01T00:00:00Z",
                "draft",
            ),
            (assessment,),
        )
        self.assertEqual(bundle.assessments[0].applicability, "uncertain")

    def test_yaml_contract_and_python_identity_share_implementation(self):
        root = Path(__file__).resolve().parents[1]
        contract = yaml.safe_load(
            (root / "genmodules/gate_model_rule/contracts/gate_model_rule.v1.yaml")
            .read_text()
        )["contract"]
        ref = GateModelRuleRef(
            "rule-model",
            "0.1.0",
            "target_population_mapping",
        )
        self.assertEqual(
            contract["model_identity"]["implementation"],
            RULE_MODEL_IMPLEMENTATION,
        )
        self.assertEqual(ref.implementation, RULE_MODEL_IMPLEMENTATION)

    def test_yaml_review_shape_matches_nested_python_review(self):
        root = Path(__file__).resolve().parents[1]
        contract = yaml.safe_load(
            (root / "genmodules/gate_model_rule/contracts/historical_rule_reference.v1.yaml")
            .read_text()
        )["contract"]["applicability_bundle"]
        self.assertIn("review", contract["required_fields"])
        self.assertEqual(
            set(contract["review_required_fields"]),
            {"reviewer_ref", "reviewed_at", "status"},
        )

    def test_repository_local_references_are_rejected(self):
        for value in ("candidate/1", "/tmp/candidate", "../candidate"):
            with self.assertRaises(ValueError):
                validate_external_ref(value)

    def test_invalid_rule_type_or_gate_reference_is_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalRuleDescriptor(
                "rule-1",
                "gate:not_a_gate",
                "unsupported",
                "positive",
                "low",
                (),
                (),
            )


if __name__ == "__main__":
    unittest.main()
