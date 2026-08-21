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

    def test_run_order_and_capacity_are_explicit(self):
        run = CONTRACT["run"]
        self.assertEqual(run["ordered_steps"][0], "RUN_LOCK_VERIFY")
        self.assertEqual(run["ordered_steps"][-1], "ATLAS_MUST_PASS_EXPORT")
        self.assertEqual(run["batch_capacity"]["min"], 20)
        self.assertEqual(run["batch_capacity"]["max"], 50)
        self.assertTrue(run["batch_capacity"]["is_capacity_target_not_pass_criterion"])

    def test_seed_and_atlas_boundaries(self):
        seed = CONTRACT["target_seed"]
        self.assertEqual(seed["unresolved_at_stage_1"]["endpoint_driving_population"], "UNRESOLVED")
        self.assertEqual(seed["unresolved_at_stage_1"]["population_causality"], "UNRESOLVED")
        atlas = CONTRACT["atlas"]
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


if __name__ == "__main__":
    unittest.main()
