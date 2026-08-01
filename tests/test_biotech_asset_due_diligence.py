import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from genmodules.biotech_asset_due_diligence.core.contract_validation import (
    ContractError,
    validate_record,
)
from genmodules.biotech_asset_due_diligence.core.artifact_refs import ArtifactRef
from genmodules.biotech_asset_due_diligence.core.entities import (
    Asset,
    ExperimentBranch,
    HumanDecision,
    SystemRecommendation,
)
from genmodules.biotech_asset_due_diligence.core.ids import stable_id
from genmodules.biotech_asset_due_diligence.adapters.antibody_engineering import build_vertical_slice


class BiotechAssetDueDiligenceTests(unittest.TestCase):
    def test_records_keep_recommendation_and_human_decision_separate(self):
        asset = Asset("asset:demo", "Demo asset", "biologic")
        recommendation = SystemRecommendation(
            recommendation_id=stable_id("recommendation", asset.asset_id),
            assessment_run_id="assessment:demo",
            policy_version="phase1a@0.1.0",
            action="hold_for_evidence",
            rejected_alternatives=(),
            basis_refs=(),
        )
        self.assertIsNone(getattr(recommendation, "human_decision", None))
        decision = HumanDecision(
            human_decision_id="human_decision:demo",
            system_recommendation_id=recommendation.recommendation_id,
            selected_action="hold_for_evidence",
            decision_status="pending",
            override_rationale=None,
        )
        self.assertEqual(decision.system_recommendation_id, recommendation.recommendation_id)

    def test_experiment_requires_explicit_alternatives(self):
        with self.assertRaises(ValueError):
            ExperimentBranch("experiment:demo", "question", (), "ready", ({"outcome": "one"},))

    def test_contract_validator_rejects_unknown_fields(self):
        contract = {
            "$id": "demo",
            "version": "1.0.0",
            "additionalProperties": False,
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        with self.assertRaises(ContractError):
            validate_record({"name": "ok", "unexpected": True}, contract)

    def test_contract_validator_recurses_into_arrays_and_objects(self):
        contract = {
            "$id": "nested",
            "version": "1.0.0",
            "type": "object",
            "additionalProperties": False,
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["kind"],
                        "properties": {"kind": {"type": "string", "enum": ["usable"]}},
                    },
                },
            },
        }
        with self.assertRaises(ContractError):
            validate_record({"items": [{"kind": 7}]}, contract)

    def test_artifact_ref_requires_external_root_and_rejects_escape(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact.txt"
            artifact.write_text("external")
            reference = ArtifactRef(
                "artifact:demo", "artifact.txt", __import__("hashlib").sha256(b"external").hexdigest(),
                artifact.stat().st_size, "Demo@1.0.0",
            )
            self.assertEqual(reference.verify(root), artifact.resolve())
            with self.assertRaises(ValueError):
                reference.verify(None)
            escaping = ArtifactRef(
                "artifact:escape", "../artifact.txt", reference.sha256, reference.bytes, reference.producer_contract,
            )
            with self.assertRaises(ValueError):
                escaping.verify(root)

    def test_adapter_accepts_current_binder_contract_without_writing_repo(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "manifest.yaml"
            normalized_path = root / "normalized.yaml"
            manifest_path.write_text(yaml.safe_dump({
                "manifest_contract": "AntibodyAssetRunManifest@0.4.0",
                "module_id": "antibody_binder_asset_engineering",
                "module_version": "0.4.0",
                "output_contract": "AntibodyAssetEngineeringPackage@0.4.0",
                "contract_validation": {"status": "passed"},
                "execution_order": list(range(14)),
                "run_id": "run:demo",
            }))
            normalized_path.write_text(yaml.safe_dump({
                "input_contract": "ExistingBinderAssetInput@0.4.0",
                "known_evidence": {},
            }))
            digest = __import__("hashlib").sha256
            package = build_vertical_slice({
                "asset": {
                    "asset_id": "asset:demo",
                    "canonical_name": "Demo asset",
                    "asset_class": "biologic",
                },
                "variant": {
                    "variant_id": "variant:demo",
                    "variant_kind": "parent",
                },
                "upstream_manifest": {
                    "path": "manifest.yaml",
                    "sha256": digest(manifest_path.read_bytes()).hexdigest(),
                    "bytes": manifest_path.stat().st_size,
                },
                "upstream_normalized_input": {
                    "path": "normalized.yaml",
                    "sha256": digest(normalized_path.read_bytes()).hexdigest(),
                    "bytes": normalized_path.stat().st_size,
                },
            }, root)
            self.assertEqual(package["system_recommendation"]["action"], "hold_for_evidence")
            self.assertIsNone(package["human_decision"])
            self.assertEqual(sorted(path.name for path in root.iterdir()), ["manifest.yaml", "normalized.yaml"])


if __name__ == "__main__":
    unittest.main()
