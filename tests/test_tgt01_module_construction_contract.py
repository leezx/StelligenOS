"""Runtime Migration PR E1: the MOD-TGT01 construction contract.

Asserts:
* the 17-item acceptance checklist is present and complete;
* items 3 / 5 / 7 / 8 quote the frozen PR D TGT-01 contract verbatim (the Module
  may not redefine the gate_question, the Evidence Ladder, the inference
  boundary or the fatal conditions);
* the contract carries a RECONSTRUCTED template_provenance;
* PR E1 ships no implementation -- no gate_modules/ directory, no provider /
  adapter / runner, no numeric scoring, MIGRATION_PENDING remains;
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt01_adc_modality_precedent.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-01_ADC_Modality_Precedent.md"
CRC_GATESET = ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"

_CHECKLIST_KEYS = (
    "01_gate_identity_and_version",
    "02_primary_module_identity_and_version",
    "03_gate_question",
    "04_admissible_evidence_classes",
    "05_evidence_ladder_and_evidence_ceiling",
    "06_direction_interpretation",
    "07_allowed_and_forbidden_inference",
    "08_fatal_conditions",
    "09_evidence_source_plan",
    "10_input_contract",
    "11_evidencepackage_output_contract",
    "12_assessment_proposal_envelope_contract",
    "13_machine_acceptance_criteria",
    "14_human_acceptance_and_review_surface",
    "15_failure_unknown_and_conflict_behavior",
    "16_stop_rule",
    "17_downstream_consumer_and_handoff",
)


def _norm(text: str) -> str:
    return " ".join(str(text).split())


class ContractShapeTests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_version_and_migration_block(self):
        self.assertEqual(self.doc["version"], "0.1.0")
        m = self.doc["migration"]
        self.assertEqual(m["pr"], "runtime_migration_pr_e1")
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e2", m["next"])
        self.assertIn("TGT-01 -> TGT-05 -> TGT-08", m["order"])

    def test_template_provenance_is_reconstructed(self):
        tp = self.doc["template_provenance"]
        self.assertEqual(tp["status"], "RECONSTRUCTED")
        self.assertTrue(tp["claim"]["not_claimed_verbatim_from_blueprint"])
        joined = " ".join(tp["source"]).lower()
        self.assertIn("blueprint v1.3 section h2.8", joined)
        self.assertIn("not present in this repository", joined)

    def test_kernel_invariant_one_way_dependency(self):
        inv = self.doc["kernel_invariant"].lower()
        self.assertIn("src/ must never import gate_modules/", inv)
        self.assertIn("may not modify the gate id", inv)

    def test_checklist_has_all_seventeen_items_in_order(self):
        checklist = self.doc["acceptance_checklist"]
        self.assertEqual(tuple(checklist), _CHECKLIST_KEYS)
        self.assertEqual(len(checklist), 17)


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt01 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-01"]

    def test_item01_gate_identity(self):
        i = self.item["01_gate_identity_and_version"]
        self.assertEqual(i["gate_id"], "TGT-01")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT01")
        self.assertEqual(i["module_implementation_version"], "0.0.0")

    def test_item03_gate_question_is_verbatim(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt01["gate_question"]),
        )
        framing = self.item["03_gate_question"]["tgt01_framing"]
        self.assertIn("already been reality-tested", framing["answers"])

    def test_item04_excludes_the_other_gates(self):
        na = " ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"])
        for gid in ("TGT-02", "TGT-03", "TGT-04", "TGT-05", "TGT-06", "TGT-07", "TGT-08"):
            self.assertIn(gid, na)

    def test_item05_evidence_ladder_is_verbatim(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt01["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt01["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt01["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_boundary_is_verbatim(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt01["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt01["forbidden_inference"]],
        )

    def test_item08_fatal_conditions_are_verbatim_and_not_a_kill(self):
        i = self.item["08_fatal_conditions"]
        self.assertEqual(
            [_norm(x) for x in i["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt01["fatal_conditions"]],
        )
        self.assertIn("never performs a candidate-level kill", i["rule"].lower())

    def test_item15_unknown_is_never_pass(self):
        i = self.item["15_failure_unknown_and_conflict_behavior"]
        self.assertIn("not KILL", i["no_admissible_evidence_at_all"])
        self.assertIn("never silently converted", i["absolute_rule"].lower())

    def test_item12_is_a_non_canonical_proposal_envelope(self):
        # review round 1: the Module must not emit a CandidateGateAssessment
        # (PR A: that object is HUMAN_APPROVED-only).
        i = self.item["12_assessment_proposal_envelope_contract"]
        self.assertIn("not a candidategateassessment", i["the_module_emits"].lower())
        self.assertIn("human_approved", i["the_module_emits"].lower())
        rules = " ".join(i["rules"]).lower()
        self.assertIn("omitting the canonical assessment identity/version", rules)
        self.assertIn("the review block", rules)
        self.assertIn("only after human approval", rules)
        self.assertIn("canonicalisation", i["shape_ref"].lower())
        # downstream items no longer claim the Module builds the canonical object
        self.assertIn(
            "the review surface constructs the canonical candidategateassessment",
            self.item["14_human_acceptance_and_review_surface"]["human_only_judgements"][-1].lower(),
        )
        self.assertIn(
            "construct a candidategateassessment",
            " ".join(self.item["17_downstream_consumer_and_handoff"]["this_module_does_not"]).lower(),
        )

    def test_item16_has_a_mandatory_adverse_sweep_before_any_stop(self):
        # review round 1: fatal-first -- a positive ceiling must not stop the
        # search before the discontinued-programme / failure-reason sweep.
        i = self.item["16_stop_rule"]
        self.assertIn("mandatory_completion_before_any_stop", i)
        mand = " ".join(i["mandatory_completion_before_any_stop"]).lower()
        self.assertIn("discontinued", mand)
        self.assertIn("failure / discontinuation-reason sweep", mand)
        self.assertIn("then_stop_searching_public_evidence_when_any_of", i)
        self.assertIn("contradicts fatal-first", i["rationale_for_the_mandatory_sweep"].lower())
        self.assertIn(
            "item-16 mandatory completion conditions",
            " ".join(
                self.item["13_machine_acceptance_criteria"][
                    "a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"
                ]
            ),
        )

    def test_item09_adcdb_is_a_discovery_index_not_an_evidence_authority(self):
        # review round 1: no secondary-index evidence laundering.
        i = self.item["09_evidence_source_plan"]
        strong = " ".join(i["source_classes"]["strong"]).lower()
        self.assertNotIn("adcdb", strong)
        self.assertNotIn("adc-target database", strong)
        self.assertIn("discovery_and_index_layer", i)
        rule = i["discovery_index_authority_rule"].lower()
        self.assertIn("does not independently establish an evidence ladder rung", rule)
        self.assertIn("underlying primary disclosure", rule)
        self.assertIn("retrieval lead, not rung-establishing evidence", rule)

    def test_item12_proposal_envelope_carries_all_identity_pins(self):
        # review round 2: the proposal envelope must be independently auditable --
        # it carries the canonical assessment identity pins (PR A required fields)
        # so canonicalisation is a deterministic field map, not a re-derivation
        # from item-10 external context. It still omits assessment_id /
        # assessment_version / review (human canonicalisation only).
        i = self.item["12_assessment_proposal_envelope_contract"]
        carries = i["the_proposal_envelope_carries"]
        pins = " ".join(carries["identity_pins_for_deterministic_canonicalisation"]).lower()
        for pin in (
            "candidate_id",
            "instantiation_id",
            "context_id",
            "context_version",
            "gateset_id",
            "gateset_version",
            "gate_id",
            "gate_version",
        ):
            self.assertIn(pin, pins, f"item 12 proposal envelope missing identity pin {pin}")
        never = " ".join(i["the_proposal_envelope_never_carries"]).lower()
        self.assertIn("assessment_id", never)
        self.assertIn("assessment_version", never)
        self.assertIn("review.status", never)
        # scientific fields stay proposal-specific
        sci = " ".join(carries["scientific_fields"]).lower()
        self.assertIn("proposed_direction", sci)
        self.assertIn("proposed_strength", sci)
        self.assertIn("evidence_refs", sci)


class NoImplementationInPrE1Tests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_scoring"], "forbidden")
        self.assertEqual(p["migration_pending"], "remains")

    def test_deferred_block_names_the_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e2_plus"]).lower()
        self.assertIn("gate_modules/", joined)
        self.assertIn("implementation", joined)
        self.assertIn("runner", joined)

    def test_e1_shipped_no_implementation_under_gate_modules(self):
        # PR E1 created no top-level gate_modules/ implementation. If the
        # directory exists now it is the separately-approved PR E2 build, not
        # something E1 smuggled in.
        module_yaml = ROOT / "gate_modules" / "tgt01_adc_modality_precedent" / "module.yaml"
        if not module_yaml.exists():
            return
        manifest = yaml.safe_load(module_yaml.read_text())["module"]
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e2")
        self.assertEqual(
            manifest["construction_contract"],
            "src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml",
        )

    def test_source_plan_connects_no_provider(self):
        self.assertFalse(
            self.doc["acceptance_checklist"]["09_evidence_source_plan"]["connect_provider_in_this_pr"]
        )

    def test_no_numeric_threshold_anywhere_in_the_contract(self):
        text = CONTRACT.read_text()
        # allow "phase 2 or 3" / "PR A-D" style; forbid ">N" "<N" "N%" "N/cell"
        self.assertIsNone(
            re.search(r"[<>]\s*\d|\b\d[\d,]*\s*(molecules|%|per cell|ng/ml)", text, re.I)
        )


class DrawingTests(unittest.TestCase):
    def test_drawing_exists_and_covers_all_items(self):
        text = DRAWING.read_text()
        self.assertIn("Has this target already been reality-tested by the ADC modality", text)
        self.assertIn("RECONSTRUCTED", text)
        self.assertIn("construction contract + drawing only", text.lower())
        # every checklist item number 1..17 appears as a table row
        for n in range(1, 18):
            self.assertRegex(text, rf"\|\s*{n}\s*\|", f"drawing missing checklist row {n}")

    def test_drawing_has_no_stale_proposed_candidategateassessment_wording(self):
        # review round 3: the same proposal/canonical boundary blocker had two
        # documentation residuals -- the Gate-ordering chain and the item-17 row
        # must not describe the Module as producing a CandidateGateAssessment.
        norm = _norm(DRAWING.read_text())
        self.assertNotIn("proposed CandidateGateAssessment", norm)
        # the ordering chain now names the proposal envelope and the terminal
        # HUMAN_APPROVED canonical record
        self.assertIn(
            "atomic EvidencePackages -> assessment proposal envelope".replace("->", "→"),
            norm,
        )
        self.assertIn("HUMAN_APPROVED CandidateGateAssessment", norm)
        # item 17 makes the human-review hop explicit before MatrixView / decisions
        self.assertIn("Only **after** `HUMAN_APPROVED`", norm)
        self.assertIn(
            "Module's own output never enters the `MatrixView` or the decision layer directly",
            norm,
        )


if __name__ == "__main__":
    unittest.main()
