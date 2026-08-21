"""Validate PR-B production contract without reading external data."""

import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = yaml.safe_load((ROOT / "docs/pools/adcdb_atlas_adc_aidd_pr_b_production.yaml").read_text(encoding="utf-8"))


class PRBProductionContractTests(unittest.TestCase):
    def test_pr_b_is_blocked_until_approval(self):
        contract = CONTRACT["contract"]
        self.assertEqual(contract["parent_contract"], "ADCdb_Atlas_ADC_AIDD_PR_A_Contract@0.1.0")
        self.assertFalse(contract["authorizes_external_run"])
        self.assertTrue(contract["approval_required_before_external_run"])

    def test_preconditions_pin_approved_pr_a_and_source(self):
        preconditions = CONTRACT["preconditions"]
        self.assertTrue(preconditions["required_pr_a_approval"])
        self.assertEqual(preconditions["required_pr_a_head_ref"], "2a2e21b07c946e3b2b4f3e83a047c260cb5a3e28")
        self.assertEqual(preconditions["required_territory_review_status"], "APPROVED")
        self.assertEqual(preconditions["required_source_admission_status"], "APPROVED")
        self.assertEqual(preconditions["required_snapshot_checksum_status"], "PASS")
        self.assertEqual(preconditions["required_atlas_registry_status"], "APPROVED_FOR_PR_B")
        self.assertEqual(preconditions["required_primary_cohort_count"], 2)

    def test_run_order_and_capacity_are_explicit(self):
        run = CONTRACT["run"]
        self.assertEqual(run["ordered_steps"][0], "RUN_LOCK_VERIFY")
        self.assertEqual(run["ordered_steps"][-1], "ATLAS_MUST_PASS_EXPORT")
        self.assertEqual(run["batch_capacity"]["min"], 20)
        self.assertEqual(run["batch_capacity"]["max"], 50)
        self.assertTrue(run["batch_capacity"]["is_capacity_target_not_pass_criterion"])
        self.assertTrue(run["run_id_equals_pipeline_run_id"])

    def test_seed_and_atlas_boundaries(self):
        seed = CONTRACT["target_seed"]
        scope = seed["seed_source_scope"]
        self.assertEqual(scope["adcdb_indication_filter"], "NONE")
        self.assertEqual(scope["allowed_precedent_scope"], "all_cancers_and_diseases_in_approved_adcdb_snapshot")
        self.assertEqual(scope["clinical_territory_filter_applies_at"], "atlas_kill_screen")
        self.assertFalse(scope["crc_indication_precedent_required_for_seed"])
        self.assertIn("precedent_disease_or_indication_refs", seed["required_seed_provenance"])
        self.assertEqual(seed["unresolved_at_stage_1"]["endpoint_driving_population"], "UNRESOLVED")
        self.assertEqual(seed["unresolved_at_stage_1"]["population_causality"], "UNRESOLVED")
        atlas = CONTRACT["atlas"]
        self.assertEqual(atlas["source_project_ref"], "external:${BIOWORKSPACE_ROOT}/PR/CRC-Atlas")
        self.assertEqual(atlas["primary_independent_cohorts"], ["GSE178318", "HTAN_CRC_progressive_plasticity"])
        self.assertEqual(atlas["supplementary_cohorts"], ["CRLM_NMP_ATLAS"])
        self.assertTrue(atlas["primary_cohort_admission_rule"].startswith("both_cohorts"))
        self.assertEqual(atlas["shared_patient_policy_ref"], "PR-A-PATIENT-AGGREGATION-v0.1.0")
        self.assertFalse(atlas["rna_surface_boundary"]["rna_is_surface_protein"])

    def test_gates_and_survivor_rule_are_closed(self):
        gates = CONTRACT["atlas"]["gates"]
        self.assertEqual([gate["gate_id"] for gate in gates], ["G1", "G2", "G3", "G4"])
        self.assertEqual(CONTRACT["outputs"]["survivor_rule"], "only_seeds_with_G1_G2_G3_G4_all_PASS")
        self.assertEqual(CONTRACT["outputs"]["empty_survivor_status"], "NO_SURVIVOR")

    def test_prohibited_outputs_are_not_authorized(self):
        prohibited = set(CONTRACT["contract"]["prohibited_outputs"])
        self.assertIn("TargetCommit", prohibited)
        self.assertIn("PRIMARY_TARGET", prohibited)
        self.assertIn("G5_G6_G7_results", prohibited)

    def test_output_root_matches_canonical_v03_root(self):
        root = CONTRACT["outputs"]["external_run_root"]
        self.assertEqual(root, "${BIOWORKSPACE_ROOT}/DATA/2.PROJECTS/Stelligen-ADCdev-OS/result/<pipeline_run_id>/")
        self.assertFalse(any(path.startswith("03_atlas_must_pass/") for path in CONTRACT["outputs"]["required_artifacts"]))
        self.assertTrue(any(path.startswith("03_atlas_kill_screen/") for path in CONTRACT["outputs"]["required_artifacts"]))


if __name__ == "__main__":
    unittest.main()
