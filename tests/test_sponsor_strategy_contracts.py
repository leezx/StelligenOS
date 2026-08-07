import unittest
from pathlib import Path

import yaml

from src.contracts.sponsor_strategy import DevelopmentSponsorProfile, ProgramThesis


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "sponsor_strategy.yaml"


class SponsorStrategyContractTests(unittest.TestCase):
    def test_contract_file_declares_only_external_instances(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        self.assertEqual(document["version"], "0.1.0")
        self.assertTrue(document["repository_policy"]["instances_external_only"])
        self.assertEqual(
            set(document["contracts"]),
            {"DevelopmentSponsorProfile", "ProgramThesis"},
        )
        self.assertEqual(
            document["contracts"]["DevelopmentSponsorProfile"]["contract_id"],
            "DevelopmentSponsorProfile@0.1.0",
        )
        self.assertEqual(
            document["contracts"]["ProgramThesis"]["contract_id"],
            "ProgramThesis@0.1.0",
        )

    def test_profile_requires_external_references_for_runtime_context(self):
        profile = DevelopmentSponsorProfile(
            sponsor_id="sponsor-1",
            company_stage="early",
            therapeutic_focus=("oncology",),
            disease_advantage=("patient-state biology",),
            modality_scope=("ADC",),
            owned_capabilities=("computational biology",),
            partnered_capabilities=("antibody generation",),
            unavailable_capabilities=("GMP manufacturing",),
            accessible_data=("external:data/1",),
            accessible_patient_samples=("external:samples/1",),
            accessible_models=("external:models/1",),
            capital_envelope="external:profile/capital",
            time_horizon="external:profile/time",
            maximum_self_funded_stage="preclinical POC",
            preferred_transaction_stage="partnerable prototype",
            acceptable_program_count="external:profile/program-capacity",
            risk_tolerance="bounded",
            geographic_scope=("global",),
            ip_strategy="external:profile/ip",
        )
        self.assertEqual(profile.sponsor_id, "sponsor-1")
        with self.assertRaises(ValueError):
            DevelopmentSponsorProfile(
                **{**profile.__dict__, "accessible_data": ("local:data/1",)}
            )

    def test_program_thesis_requires_sponsor_and_transfer_refs(self):
        thesis = ProgramThesis(
            thesis_id="thesis-1",
            opportunity_ref="external:opportunity/1",
            clinical_hypothesis_ref="external:clinical-hypothesis/1",
            intended_product_position_ref="external:product-position/1",
            sponsor_profile_ref="external:sponsor-profile/1",
            current_lifecycle_stage="opportunity_validation",
            target_transfer_milestone_ref="external:milestone/1",
            development_path="partnerable_asset_option",
            source_refs=("external:source/1",),
        )
        self.assertEqual(thesis.development_path, "partnerable_asset_option")
        with self.assertRaises(ValueError):
            ProgramThesis(
                **{**thesis.__dict__, "sponsor_profile_ref": "local:profile/1"}
            )
        with self.assertRaises(ValueError):
            ProgramThesis(
                **{**thesis.__dict__, "development_path": "self_fund_everything"}
            )

    def test_contracts_do_not_grant_commitment_or_execute_runs(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        thesis_invariants = document["contracts"]["ProgramThesis"]["invariants"]
        self.assertIn("thesis_does_not_grant_program_commitment", thesis_invariants)
        self.assertIn("thesis_does_not_execute_a_gate_or_asset_generation_run", thesis_invariants)


if __name__ == "__main__":
    unittest.main()
