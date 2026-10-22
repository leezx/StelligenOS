"""Phase A declaration checks; no v2 Module or Decision execution."""

import hashlib
import json
import unittest
from pathlib import Path

import yaml

from src.objects.decision_model import Instantiation
from src.objects.gate_model import GateSet, GateSetMember


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "src/contracts/crc_adc_target_gateset.yaml"
V1_MODULE = ROOT / "src/contracts/gate_modules/tgt05_normal_tissue_fatal_liability.yaml"
V2 = ROOT / "src/contracts/crc_adc_target_gateset_v2.yaml"
V2_MODULE = ROOT / "src/contracts/gate_modules/tgt05_normal_tissue_adc_toxicity_v2.yaml"
REVIEW_SCHEMA = ROOT / "src/contracts/gate_modules/tgt05_decision_record_v2.schema.json"
BINDING_SCHEMA = ROOT / "src/contracts/data_layout/gate_binding.schema.yaml"
SOURCE = ROOT / "docs/architecture/TGT05_DECISION_MODEL_V1_SOURCE_SNAPSHOT.md"
POLICIES = ROOT / "src/contracts/gateset_policies/ADC_TARGET_GATESET/v2"


def load(path):
    return yaml.safe_load(path.read_text())


class V2LineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v1 = load(V1)
        cls.v2 = load(V2)
        cls.binding_schema = load(BINDING_SCHEMA)

    def test_v1_frozen_bytes_and_source_snapshot(self):
        self.assertEqual(hashlib.sha256(V1.read_bytes()).hexdigest(),
                         "558db82fd06ffba41226754b8cc55c789d206165bceb2ccf671a65d860b389ae")
        self.assertEqual(hashlib.sha256(V1_MODULE.read_bytes()).hexdigest(),
                         "529b79755139f6894f8f903dc588904d06247dd8117199715cc407b5b407be8b")
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                         self.v2["normative_source"]["source_snapshot_sha256"])
        self.assertEqual(self.v2["normative_source"]["rfc_merge_commit"],
                         "004fc44c02fbea9511274427904792b255141521")

    def test_exact_member_and_instantiation_lineage(self):
        gs = self.v2["gateset"]
        expected = [(f"TGT-{n:02}", "2.0" if n == 5 else "1.0") for n in range(1, 9)]
        self.assertEqual(gs["gateset_id"], self.v1["gateset"]["gateset_id"])
        self.assertEqual(gs["gateset_version"], "2.0")
        self.assertEqual([(m["gate_id"], m["gate_version"]) for m in gs["members"]], expected)
        self.assertEqual(self.v2["instantiation"]["instantiation_id"],
                         "INST-CRC-REFRACTORY-ADC-TARGET-v2")
        self.assertEqual(self.v2["instantiation"]["status"], "HOLD")
        self.assertEqual(self.v2["roster"][4]["planned_module_version"], "2.0.0")
        self.assertEqual(self.v2["roster"][4]["primary_module_version"], "0.0.0")

    def test_v2_gateset_and_inactive_instantiation_build_with_frozen_objects(self):
        gs = self.v2["gateset"]
        obj = GateSet(
            gateset_id=gs["gateset_id"], gateset_version=gs["gateset_version"],
            candidate_level=gs["candidate_level"],
            gates=tuple(GateSetMember(m["gate_id"], m["gate_version"]) for m in gs["members"]),
            decision_rule_ref=gs["decision_rule_ref"],
            fatal_gate_policy_ref=gs["fatal_gate_policy_ref"],
            required_gate_policy_ref=gs["required_gate_policy_ref"],
            unknown_policy_ref=gs["unknown_policy_ref"],
        )
        inst = Instantiation(**{k: v for k, v in self.v2["instantiation"].items()
                                if k != "activation_condition"})
        self.assertEqual(obj.gateset_version, "2.0")
        self.assertEqual(inst.gateset_version, "2.0")
        self.assertEqual(inst.status, "HOLD")

    def test_bindings_match_frozen_schema_and_versioned_members(self):
        defs = self.binding_schema["$defs"]
        bindings = self.v2["context_specific_bindings"]
        gb = bindings["gateset_binding"]
        self.assertEqual(set(gb), set(defs["gateset_binding"]["properties"]))
        self.assertEqual(gb["gates"], self.v2["gateset"]["members"])
        for key in ("decision_rule_ref", "fatal_gate_policy_ref", "required_gate_policy_ref"):
            self.assertEqual(gb[key], self.v2["gateset"][key])
        gate_bindings = bindings["gate_bindings"]
        self.assertEqual(len(gate_bindings), 8)
        for row, member in zip(gate_bindings, self.v2["gateset"]["members"]):
            self.assertEqual(set(row), set(defs["gate_binding"]["properties"]))
            self.assertEqual((row["gate_id"], row["gate_version"]),
                             (member["gate_id"], member["gate_version"]))
            self.assertEqual(row["gateset_version"], "2.0")
            self.assertEqual(row["instantiation_id"], gb["instantiation_id"])
        self.assertEqual(gate_bindings[4]["primary_module_version"], "0.0.0")
        for row in gate_bindings[:4] + gate_bindings[5:]:
            old = next(b for b in self.v1["context_specific_bindings"]["gate_bindings"]
                       if b["gate_id"] == row["gate_id"])
            for key in ("gate_version", "gate_contract_ref", "evidence_ladder_ref",
                        "assessment_rule_ref", "primary_module_id", "primary_module_version"):
                self.assertEqual(row[key], old[key])

    def test_tgt05_evidence_authority_and_boundary(self):
        gate = self.v2["gate_contracts"]["TGT-05"]
        ladder = gate["evidence_ladder"]
        self.assertEqual(set(ladder), {"DIRECT", "INDIRECT_STRONG", "WEAK"})
        self.assertEqual(gate["direction_rules"]["weak"].split(";")[0], "INCONCLUSIVE/WEAK")
        self.assertIn("INCONCLUSIVE/UNKNOWN", gate["direction_rules"]["unknown"])
        self.assertEqual(len(ladder["DIRECT"]["negative"]), 1)
        self.assertEqual(len(ladder["INDIRECT_STRONG"]["negative"]), 1)
        self.assertIn("RNA or ordinary IHC negative", gate["direction_rules"]["negative_forbidden"])
        self.assertIn("never automatic KILL", gate["potential_fatal_review"]["unresolved"])


class V2ReviewContractTests(unittest.TestCase):
    def test_seventeen_item_module_contract_and_noncanonical_record(self):
        mod = load(V2_MODULE)
        self.assertEqual(tuple(mod["acceptance_checklist"]),
                         tuple(f"{n:02}_{name}" for n, name in enumerate((
                             "gate_identity_and_version", "primary_module_identity_and_version",
                             "gate_question", "admissible_evidence_classes",
                             "evidence_ladder_and_evidence_ceiling", "direction_interpretation",
                             "allowed_and_forbidden_inference", "fatal_conditions",
                             "evidence_source_plan", "input_contract",
                             "evidencepackage_output_contract", "assessment_proposal_envelope_contract",
                             "machine_acceptance_criteria", "human_acceptance_and_review_surface",
                             "failure_unknown_and_conflict_behavior", "stop_rule",
                             "downstream_consumer_and_handoff"), 1)))
        record = json.loads(REVIEW_SCHEMA.read_text())
        self.assertEqual(record["properties"]["recommendation"]["enum"], ["GO", "HOLD", "KILL"])
        self.assertEqual(record["properties"]["review"]["properties"]["status"]["enum"],
                         ["DRAFT", "HUMAN_REVIEWED"])
        self.assertNotIn("decision", record["properties"])
        conditions = record["allOf"]
        go = next(x["then"] for x in conditions
                  if x.get("if", {}).get("properties", {}).get("recommendation", {}).get("const") == "GO")
        kill = next(x["then"] for x in conditions
                    if x.get("if", {}).get("properties", {}).get("recommendation", {}).get("const") == "KILL")
        self.assertEqual(go["properties"]["assessment_basis_cell"]["enum"],
                         ["NEGATIVE/DIRECT", "NEGATIVE/INDIRECT_STRONG"])
        self.assertEqual(kill["properties"]["assessment_basis_cell"]["const"], "POSITIVE/DIRECT")


class V2PolicyContractTests(unittest.TestCase):
    def test_four_policy_refs_and_owner_match_gateset(self):
        gs = load(V2)["gateset"]
        for name in ("decision_rule", "fatal_gate_policy", "required_gate_policy", "unknown_policy"):
            body = load(POLICIES / f"{name}.yaml")
            self.assertEqual(body["policy_id"], gs[f"{name}_ref"])
            self.assertEqual(body["policy_version"], "v2")
            self.assertEqual(body["owner_gateset_id"], "ADC_TARGET_GATESET")
            self.assertEqual(body["owner_gateset_version"], "2.0")

    def test_decision_precedence_and_strict_go(self):
        decision = load(POLICIES / "decision_rule.yaml")
        table = decision["ordered_truth_table"]
        self.assertEqual([r["order"] for r in table], list(range(8)))
        self.assertEqual([r["result"] for r in table], [
            "NO_CANONICAL_DECISION", "NO_CANONICAL_DECISION", "KILL", "HOLD",
            "MORE_EVIDENCE", "GO", "HOLD", "NO_CANONICAL_DECISION"])
        self.assertEqual(decision["decision_output"]["allowed_this_policy"],
                         ["GO", "HOLD", "MORE_EVIDENCE", "KILL"])
        required = load(POLICIES / "required_gate_policy.yaml")["required_for_GO"]
        self.assertEqual(set(required["gate_cells"]), {f"TGT-{n:02}" for n in range(1, 9)})
        self.assertEqual(required["review_status"], "HUMAN_APPROVED")
        self.assertEqual(required["critical_unknowns"], "empty in all eight approved assessments")
        self.assertEqual(required["gate_cells"]["TGT-05"]["direction"], "NEGATIVE")
        self.assertEqual(required["gate_cells"]["TGT-07"]["allowed_strengths"], ["DIRECT"])
        for row in required["gate_cells"].values():
            self.assertNotIn("WEAK", row["allowed_strengths"])

    def test_fatal_and_unknown_never_silently_grant_go_or_kill(self):
        fatal = load(POLICIES / "fatal_gate_policy.yaml")
        unknown = load(POLICIES / "unknown_policy.yaml")
        self.assertTrue(fatal["decision_boundary"]["no_automatic_fatal"])
        self.assertEqual(fatal["eligible_routes"]["TGT-08"],
                         "NO_SCIENTIFIC_KILL; commercial or IP concern belongs to sponsor review")
        self.assertIn("no_canonical_Decision_on_hard_reject", unknown["prohibitions"])
        self.assertIn("no_policy_fallback_to_v1", unknown["prohibitions"])

    def test_synthetic_acceptance_cases_cover_each_policy_row_and_key_tgt05_boundaries(self):
        cases = load(POLICIES / "acceptance_cases.yaml")["cases"]
        by_id = {case["id"]: case for case in cases}
        self.assertEqual(len(by_id), len(cases))
        table = load(POLICIES / "decision_rule.yaml")["ordered_truth_table"]
        for case in cases:
            row = table[case["governing_row"]]
            self.assertEqual(case["expected"], row["result"])
        for name in ("only_normal_tissue_rna", "only_total_protein_ihc",
                     "bounded_tgt05_negative_but_other_gates_missing"):
            self.assertEqual(by_id[name]["expected"], "MORE_EVIDENCE")
        self.assertEqual(by_id["confirmed_program_specific_clinical_route"]["expected"], "KILL")
        self.assertEqual(by_id["human_membrane_expression_unknown_consequence"]["expected"], "HOLD")
        self.assertEqual(by_id["eight_qualified_favorable_cells"]["expected"], "GO")


if __name__ == "__main__":
    unittest.main()
