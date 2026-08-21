"""Validate PR-A contract shape without reading or running external data."""

import pathlib
import unittest

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "pools" / "adcdb_atlas_adc_aidd_pr_a_contract.yaml"
CONTRACT = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))


class PRATargetSelectionContractTests(unittest.TestCase):
    def test_contract_is_design_only(self):
        contract = CONTRACT["contract"]
        self.assertEqual(contract["pipeline_version"], "ADCdb_Atlas_ADC_AIDD_Design@0.3.0")
        self.assertFalse(contract["authorizes_external_run"])
        self.assertEqual(contract["authorizes_next_stage_only_after_approval"], "PR-B")

    def test_source_admission_requires_snapshot_and_review_fields(self):
        source = CONTRACT["source_admission"]
        self.assertEqual(source["required_status"], "APPROVED")
        for field in ("snapshot_id", "source_version", "license_access_note", "human_review_ref"):
            self.assertIn(field, source["required_fields"])
        self.assertIn("manifest_sha256", source["snapshot_required_fields"])

    def test_lock_freezes_authoritative_territory_and_hypothesis_boundary(self):
        lock = CONTRACT["lock"]
        self.assertEqual(lock["schema"], "TargetSelectionLock@0.1.0")
        self.assertEqual(lock["authoritative_clinical_territory"], "clinical_territory.yaml")
        self.assertEqual(lock["derived_clinical_hypothesis"], "clinical_hypothesis.json")
        for field in ("territory_id", "schema_version", "refractory_definition", "intended_benefit", "endpoint_class", "review_status"):
            self.assertIn(field, lock["required_fields"])
        self.assertTrue(any("cannot widen" in rule for rule in lock["cross_field_invariants"]))

    def test_seed_keeps_population_and_causality_unresolved(self):
        seed = CONTRACT["target_seed"]
        self.assertEqual(
            seed["mandatory_unresolved_fields"],
            {"endpoint_driving_population": "UNRESOLVED", "population_causality": "UNRESOLVED"},
        )
        self.assertTrue(seed["expected_first_batch_size"]["is_capacity_target_not_pass_criterion"])

    def test_atlas_uses_patient_units_and_separate_gate_policies(self):
        atlas = CONTRACT["atlas"]
        self.assertEqual(atlas["statistical_units"]["patient"], "patient_id")
        self.assertFalse(atlas["g4_coverage"]["sample_count_is_patient_count"])
        for gate in ("g1_expression_prevalence", "g2_population_mapping", "g3_population_causality", "g4_coverage"):
            self.assertIn("policy_id", atlas[gate])
            self.assertIn("otherwise", atlas[gate])

    def test_patient_aggregation_and_g2_metric_are_frozen(self):
        atlas = CONTRACT["atlas"]
        aggregation = CONTRACT["patient_aggregation_policy"]
        self.assertEqual(aggregation["reducer"], "pooled_malignant_cells_across_valid_samples_within_patient")
        self.assertEqual(aggregation["numerator"], "target_positive_malignant_cells")
        self.assertEqual(aggregation["denominator"], "all_valid_malignant_cells")
        self.assertEqual(atlas["g2_population_mapping"]["pass"]["effect_metric"], "population_state_prevalence_ratio")
        self.assertEqual(atlas["g2_population_mapping"]["pass"]["effect_min"], 2.0)
        self.assertTrue(atlas["g2_population_mapping"]["pass"]["metric_must_be_frozen_before_run"])
        self.assertEqual(atlas["g4_coverage"]["pass"]["independent_cohorts_min"], 2)

    def test_developability_consumes_atlas_survivors(self):
        developability = CONTRACT["developability"]
        self.assertEqual(developability["consumes"], "atlas_must_pass_survivors_only")
        self.assertFalse(developability["target_count_guidance"]["hard_coded"])

    def test_target_commit_has_single_primary_invariant(self):
        commit = CONTRACT["target_commit"]
        self.assertEqual(commit["primary_max"], 1)
        self.assertEqual(commit["backup_max"], 1)
        self.assertTrue(commit["no_go_false_requires_exactly_one_primary"])
        self.assertTrue(commit["no_go_true_requires_empty_primary_and_backup"])

    def test_v03_is_not_authorized_or_modified_by_pr_a(self):
        boundary = CONTRACT["review_boundary"]
        self.assertTrue(boundary["approval_required"])
        self.assertFalse(boundary["execution_authorized_by_this_contract"])
        self.assertFalse(boundary["v0_3_design_modification_allowed"])


if __name__ == "__main__":
    unittest.main()
