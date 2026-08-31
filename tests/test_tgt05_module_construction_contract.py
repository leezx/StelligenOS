"""Runtime Migration PR E3: the MOD-TGT05 construction contract.

Asserts:
* the 17-item acceptance checklist is present, complete and ordered (template
  reused from the approved PR E1 template);
* items 03 / 05 / 07 / 08 are a normalized-equality parity with the FROZEN PR D
  TGT-05 contract (crc_adc_target_gateset.yaml) -- not a hand approximation;
* TGT-05 is frozen as a one-way liability detector, never a safety predictor:
  a single ADC toxicity is not target-wide fatal, protein normal-tissue
  expression is not fatal, non-ADC toxicity severity does not transfer to an
  ADC, a negative atlas is not safety / NEGATIVE, incomplete coverage -> UNKNOWN,
  a product-specific therapeutic-window conclusion is forbidden;
* the asymmetric fatal-sweep-mandatory stop rule is present;
* PR E3 ships no implementation -- no gate_modules/tgt05.../ directory, no
  provider / adapter / runner, no numeric scoring, no biological threshold, no
  generic GateModule framework; MOD-TGT05 primary_module_version stays "0.0.0";
  MOD-TGT01 is untouched; MIGRATION_PENDING remains;
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt05_normal_tissue_fatal_liability.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-05_Normal_Tissue_Fatal_Liability.md"
CRC_GATESET = ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"
E1_CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt01_adc_modality_precedent.yaml"

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
        self.assertEqual(m["pr"], "runtime_migration_pr_e3")
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e4", m["next"])
        self.assertIn("TGT-01 -> TGT-05 -> TGT-08", m["order"])

    def test_template_provenance_reuses_the_e1_template(self):
        tp = self.doc["template_provenance"]
        self.assertEqual(tp["status"], "RECONSTRUCTED")
        self.assertTrue(tp["claim"]["not_claimed_verbatim_from_blueprint"])
        self.assertTrue(tp["claim"]["seventeen_item_template_reused_from_e1"])
        self.assertIn("e1 17-item construction template", tp["template_basis"].lower())
        self.assertTrue(E1_CONTRACT.is_file())

    def test_kernel_invariant_one_way_dependency_and_liability_detector(self):
        inv = self.doc["kernel_invariant"].lower()
        self.assertIn("src/ must never import gate_modules/", inv)
        self.assertIn("one-way normal-tissue liability detector", inv)
        self.assertIn("never a safety predictor", inv)

    def test_checklist_has_all_seventeen_items_in_order(self):
        checklist = self.doc["acceptance_checklist"]
        self.assertEqual(tuple(checklist), _CHECKLIST_KEYS)
        self.assertEqual(len(checklist), 17)

    def test_e3_checklist_keys_match_the_e1_template_keys(self):
        e1 = yaml.safe_load(E1_CONTRACT.read_text())["acceptance_checklist"]
        self.assertEqual(tuple(e1), _CHECKLIST_KEYS)


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt05 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-05"]

    def test_item01_gate_identity(self):
        i = self.item["01_gate_identity_and_version"]
        self.assertEqual(i["gate_id"], "TGT-05")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT05")
        self.assertEqual(i["module_implementation_version"], "0.0.0")

    def test_item03_gate_question_is_parity_with_pr_d(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt05["gate_question"]),
        )
        framing = self.item["03_gate_question"]["tgt05_framing"]
        self.assertIn("liability class", framing["answers"])
        joined = " ".join(framing["does_not_answer"]).lower()
        self.assertIn("therapeutic window", joined)
        self.assertIn('cannot confirm its absence', joined)

    def test_item04_excludes_the_other_gates(self):
        na = " ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"])
        for gid in ("TGT-01", "TGT-02", "TGT-03", "TGT-04", "TGT-06", "TGT-07", "TGT-08"):
            self.assertIn(gid, na)

    def test_item05_evidence_ladder_is_parity_with_pr_d(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt05["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt05["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt05["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_boundary_is_parity_with_pr_d(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt05["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt05["forbidden_inference"]],
        )

    def test_item08_fatal_conditions_are_parity_with_pr_d_and_not_a_kill(self):
        i = self.item["08_fatal_conditions"]
        self.assertEqual(
            [_norm(x) for x in i["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt05["fatal_conditions"]],
        )
        self.assertIn("never performs a candidate-level kill", i["rule"].lower())
        self.assertIn("no numeric severity score", i["rule"].lower())
        # the single-product vs target-intrinsic separation
        sep = i["single_product_vs_target_intrinsic_convergence"]
        self.assertIn("NOT target-wide fatal", sep["one_same_target_adc_with_explicit_target_mediated_toxicity"])
        self.assertIn("NOT fatal", sep["human_protein_expression_in_a_vital_organ"])
        self.assertIn("does not transfer", sep["same_target_non_adc_toxicity_car_t_tce_naked_ab"])
        # the convergence-audit fields
        per_obs = " ".join(i["convergence_audit_requirements"]["per_observation"]).lower()
        for field in ("construct fingerprint", "linker", "payload", "observed severity for this product",
                      "target-attribution basis", "primary source"):
            self.assertIn(field, per_obs)
        hr = " ".join(i["human_review_reserved"]).lower()
        self.assertIn("materially distinct", hr)
        self.assertIn("truly target-mediated", hr)


class LiabilityDetectorSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item06_direction_is_evidence_relative_not_candidate_desirability(self):
        i = self.item["06_direction_interpretation"]
        rule = i["strength_direction_rule"].lower()
        self.assertIn("not candidate desirability", rule)
        self.assertIn("does not flip direction", rule)
        self.assertIn("essentially unreachable", i["NEGATIVE"].lower())
        # a "no risk seen" negative is forbidden
        self.assertIn("no risk seen", i["NEGATIVE"].lower())

    def test_item06_frozen_truth_table_is_unambiguous(self):
        # review round 1: a single mapping, no E4 discretion. A WEAK-only signal
        # is INCONCLUSIVE (PR D "liability cannot be graded"), never POSITIVE.
        tt = self.item["06_direction_interpretation"]["frozen_truth_table"]
        self.assertEqual(tt["DIRECT_liability_evidence"], "POSITIVE / DIRECT")
        self.assertEqual(tt["INDIRECT_STRONG_liability_evidence"], "POSITIVE / INDIRECT_STRONG")
        self.assertEqual(tt["WEAK_only_liability_hypothesis"], "INCONCLUSIVE / WEAK")
        self.assertEqual(
            tt["no_qualifying_liability_evidence_and_public_coverage_incomplete_or_exhausted"],
            "INCONCLUSIVE / UNKNOWN",
        )
        self.assertIn("NEGATIVE / safe", tt["never"])
        self.assertIn("hypothesis only", tt["note"].lower())

    def test_item06_established_liability_is_not_downgraded_for_an_uncovered_organ(self):
        prec = self.item["06_direction_interpretation"]["positive_precedence_over_coverage_gaps"].lower()
        self.assertIn("does not downgrade the direction back to unknown", prec)
        self.assertIn("critical_unknowns", prec)

    def test_item06_conflicting_does_not_earn_a_negative_rung(self):
        c = self.item["06_direction_interpretation"]["CONFLICTING"].lower()
        self.assertIn("on the same liability observation", c)
        self.assertIn("not a new safety-negative", c)
        self.assertIn("does not earn a negative rung", c)
        self.assertIn("not contradictory evidence for the safety direction", c)

    def test_item06_negative_cannot_come_from_negative_atlas(self):
        neg = self.item["06_direction_interpretation"]["NEGATIVE"].lower()
        for token in ("hpa-negative", "rna-negative", "ihc-negative"):
            self.assertIn(token, neg)
        self.assertIn("do not produce negative = safe", neg)

    def test_item09_source_authority_hard_locks(self):
        rules = " ".join(
            self.item["09_evidence_source_plan"]["source_authority_rules"]
        ).lower()
        self.assertIn("rna-only evidence cannot become protein evidence", rules)
        self.assertIn("does not prove cell-surface accessibility", rules)
        self.assertIn("does not transfer to an adc", rules)
        self.assertIn("negative atlas does not prove safety", rules)

    def test_item09_has_a_vital_organ_coverage_map_and_no_threshold(self):
        i = self.item["09_evidence_source_plan"]
        organs = [o.lower() for o in i["coverage_map"]["vital_organs"]]
        for organ in ("central nervous system", "cardiac", "hepatic",
                      "pulmonary", "hematopoietic", "gastrointestinal"):
            self.assertIn(organ, organs)
        self.assertIn("no organ count", i["no_universal_threshold"].lower())
        self.assertFalse(i["connect_provider_in_this_pr"])
        self.assertEqual(i["current_instantiation_regime"], "PUBLIC_ONLY")

    def test_item15_incomplete_coverage_is_unknown_not_safe(self):
        i = self.item["15_failure_unknown_and_conflict_behavior"]
        self.assertIn("never auto-PASS", i["no_admissible_liability_evidence_and_incomplete_coverage"])
        abs_rules = " ".join(i["absolute_rules"]).lower()
        self.assertIn("not an integrity failure", abs_rules)
        self.assertIn("absence of public risk evidence is not a safety-negative", abs_rules)

    def test_item16_asymmetric_stop_rule_has_all_three_paths(self):
        i = self.item["16_stop_rule"]
        self.assertIn("absence of public risk evidence is not a stop condition", i["principle"].lower())
        pa = i["path_a_machine_detects_a_potential_fatal_pattern"]
        then = " ".join(pa["then"])
        self.assertIn("POTENTIAL_FATAL_PATTERN", then)
        self.assertNotIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", then)
        self.assertIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", " ".join(pa["the_machine_does_not"]))
        b = " ".join(i["path_b_only_one_direct_adc_toxicity"]["then_must_complete_before_any_stop"]).lower()
        self.assertIn("construct inventory", b)
        c = " ".join(i["path_c_no_direct_clinical_liability"]["then_must_complete_before_any_stop"]).lower()
        self.assertIn("vital-organ coverage sweep", c)
        self.assertIn(
            "EXPERIMENT_REQUIRED",
            i["path_c_no_direct_clinical_liability"]["if_unresolvable_by_public_sources"],
        )

    def test_item16_path_a_is_machine_detection_only_not_a_human_call(self):
        crit = self.item["16_stop_rule"][
            "path_a_machine_detects_a_potential_fatal_pattern"
        ]["machine_detection_criteria"]
        joined = " ".join(crit).lower()
        self.assertIn("distinct program", joined)
        self.assertIn("auditable construct fingerprint", joined)
        self.assertIn("disclosed target-attribution basis", joined)
        # the "materially distinct" call is NOT a machine detection criterion
        self.assertNotIn("materially distinct", joined)

    def test_no_product_specific_therapeutic_window_conclusion_anywhere(self):
        i13 = self.item["13_machine_acceptance_criteria"]
        crit = " ".join(i13["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]).lower()
        self.assertIn("no product-specific therapeutic-window conclusion", crit)
        i17 = " ".join(self.item["17_downstream_consumer_and_handoff"]["this_module_does_not"]).lower()
        self.assertIn("product-specific therapeutic-window conclusion", i17)
        self.assertIn("flip direction based on candidate desirability", i17)


class FatalReviewIsHumanOnlyTests(unittest.TestCase):
    """Review round 1: the fatal call is human-only. The machine emits at most a
    module-local POTENTIAL_FATAL_PATTERN, never PUBLIC_FATAL_SIGNAL_ESTABLISHED,
    and the structured signal lives in a fatal_review record, not the proposal
    envelope / a canonical field / a new core object."""

    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item08_machine_output_is_only_a_potential_pattern(self):
        m = self.item["08_fatal_conditions"]["machine_output_is_only_a_potential_pattern"]
        self.assertIn("POTENTIAL_FATAL_PATTERN", m)
        self.assertIn("NEVER emits", m)
        self.assertIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", m)
        hr = " ".join(self.item["08_fatal_conditions"]["human_review_reserved"]).lower()
        self.assertIn("biologically meaningful", hr)

    def test_item12_fatal_review_is_module_local_not_canonical(self):
        fr = self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]
        self.assertEqual(fr["machine_never_emits"], "PUBLIC_FATAL_SIGNAL_ESTABLISHED")
        self.assertIn("POTENTIAL_FATAL_PATTERN", fr["machine_may_emit"])
        what = fr["what_it_is"].lower()
        self.assertIn("non-canonical", what)
        self.assertIn("not a field of the proposal envelope", what)
        self.assertIn("not a new core object", what)
        self.assertIn("not a change to the pr a", what)
        fields = " ".join(fr["fields"]).lower()
        for f in ("required", "status", "evidence_ids", "program_ids",
                  "construct_fingerprints", "affected_tissues",
                  "target_attribution_basis_refs"):
            self.assertIn(f, fields)
        self.assertIn("single direct liability observation gives required = false",
                      fr["required_is_true_iff"].lower())
        never = " ".join(
            self.item["12_assessment_proposal_envelope_contract"]["the_proposal_envelope_never_carries"]
        ).lower()
        self.assertIn("a fatal flag", never)

    def test_item14_human_sees_and_judges_the_fatal_review(self):
        sees = " ".join(self.item["14_human_acceptance_and_review_surface"]["the_human_sees"]).lower()
        self.assertIn("fatal_review record", sees)
        judge = " ".join(
            self.item["14_human_acceptance_and_review_surface"]["human_only_judgements"]
        ).lower()
        self.assertIn("biologically meaningful", judge)
        self.assertIn("real target-intrinsic fatal signal", judge)

    def test_item13_and_17_forbid_public_fatal_signal_established(self):
        crit = " ".join(
            self.item["13_machine_acceptance_criteria"][
                "a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"
            ]
        )
        self.assertIn("never PUBLIC_FATAL_SIGNAL_ESTABLISHED", crit)
        not_do = " ".join(self.item["17_downstream_consumer_and_handoff"]["this_module_does_not"])
        self.assertIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", not_do)
        self.assertIn("POTENTIAL_FATAL_PATTERN", not_do)

    def test_public_fatal_signal_established_never_appears_in_a_machine_output_list(self):
        # structurally: it is never something item 16 Path A "then" does, and
        # never in the fatal_review machine_may_emit.
        i16 = self.item["16_stop_rule"]["path_a_machine_detects_a_potential_fatal_pattern"]
        self.assertNotIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", " ".join(i16["then"]))
        fr = self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]
        self.assertNotIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", fr["machine_may_emit"])
        self.assertNotIn(
            "PUBLIC_FATAL_SIGNAL_ESTABLISHED",
            " ".join(fr["fields"]) + fr["required_is_true_iff"],
        )


class InheritsPrE2GenesTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item10_uses_the_single_authoritative_target_identity(self):
        req = " ".join(self.item["10_input_contract"]["required_inputs"]).lower()
        self.assertIn("single authoritative target", req)
        self.assertIn("no separate drift-prone target argument", req)

    def test_item11_exact_canonical_ep_reuse_and_parity_on_reuse(self):
        rules = " ".join(self.item["11_evidencepackage_output_contract"]["rules"]).lower()
        self.assertIn("reuses the exact canonical package, never copies or re-creates", rules)
        self.assertIn("present and equal", rules)
        self.assertIn("hard identity integrity failure", rules)

    def test_item12_is_a_non_canonical_proposal_envelope_without_review(self):
        i = self.item["12_assessment_proposal_envelope_contract"]
        self.assertIn("not a candidategateassessment", i["the_module_emits"].lower())
        never = " ".join(i["the_proposal_envelope_never_carries"]).lower()
        self.assertIn("assessment_id", never)
        self.assertIn("review.status", never)
        self.assertIn("therapeutic-window conclusion", never)
        pins = " ".join(
            i["the_proposal_envelope_carries"]["identity_pins_for_deterministic_canonicalisation"]
        ).lower()
        for pin in ("candidate_id", "instantiation_id", "context_id", "gateset_id", "gate_id"):
            self.assertIn(pin, pins)

    def test_item13_hard_integrity_failure_rejects_the_run(self):
        on_fail = self.item["13_machine_acceptance_criteria"]["on_failure"].lower()
        self.assertIn("rejects the whole run", on_fail)
        self.assertIn("never degraded to", on_fail)
        self.assertIn("unknown from genuinely incomplete coverage is not an integrity failure", on_fail)


class NoImplementationInPrE3Tests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_scoring"], "forbidden")
        self.assertEqual(p["biological_thresholds_in_this_pr"], "forbidden")
        self.assertEqual(p["product_specific_therapeutic_window_logic"], "forbidden")
        self.assertEqual(p["generic_gatemodule_framework_or_base_class_in_this_pr"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt01"], "forbidden")
        self.assertEqual(p["migration_pending"], "remains")

    def test_deferred_block_names_the_e4_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e4_plus"]).lower()
        self.assertIn("gate_modules/tgt05_normal_tissue_fatal_liability/", joined)
        self.assertIn("1.0.0", joined)
        self.assertIn("runner", joined)

    def test_pr_e3_shipped_no_implementation_under_gate_modules(self):
        # PR E3 created no gate_modules/tgt05.../ implementation. If the
        # directory exists now it is the separately-approved PR E4 build, not
        # something E3 smuggled in.
        module_yaml = (
            ROOT / "gate_modules" / "tgt05_normal_tissue_fatal_liability" / "module.yaml"
        )
        if not module_yaml.exists():
            return
        manifest = yaml.safe_load(module_yaml.read_text())["module"]
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e4")
        self.assertEqual(
            manifest["construction_contract"],
            "src/contracts/gate_modules/tgt05_normal_tissue_fatal_liability.yaml",
        )

    def test_tgt05_binding_matches_the_module_build_state(self):
        gateset = yaml.safe_load(CRC_GATESET.read_text())
        binding = next(
            b for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-05"
        )
        self.assertEqual(binding["primary_module_id"], "MOD-TGT05")
        module_yaml = (
            ROOT / "gate_modules" / "tgt05_normal_tissue_fatal_liability" / "module.yaml"
        )
        expected = "0.0.0"
        if module_yaml.exists():
            expected = yaml.safe_load(module_yaml.read_text())["module"]["module_version"]
        self.assertEqual(binding["primary_module_version"], expected)

    def test_mod_tgt01_is_untouched(self):
        gateset = yaml.safe_load(CRC_GATESET.read_text())
        binding = next(
            b for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-01"
        )
        self.assertEqual(binding["primary_module_version"], "1.0.0")

    def test_no_generic_gate_module_framework_or_base_class_added(self):
        gm = ROOT / "gate_modules"
        py_files = sorted(str(p.relative_to(ROOT)) for p in gm.rglob("*.py"))
        # only the built per-gate packages may exist under gate_modules/ -- no
        # shared framework / base-class / registry module at the root.
        allowed = (
            "tgt01_adc_modality_precedent",
            "tgt02_indication_specific_malignant_cell_coverage",
            "tgt03_treatment_metastatic_persistence",
            "tgt04_tumor_surface_availability_density_plausibility",
            "tgt05_normal_tissue_fatal_liability",
            "tgt06_internalization_trafficking_addressability",
            "tgt08_target_opportunity_competition_ip_whitespace",
        )
        self.assertTrue(
            all(any(pkg in p for pkg in allowed) for p in py_files), py_files
        )

    def test_no_numeric_threshold_anywhere_in_the_contract(self):
        text = CONTRACT.read_text()
        self.assertIsNone(
            re.search(r"[<>]\s*\d|\b\d[\d,]*\s*(molecules|%|per cell|ng/ml|tpm|fpkm)", text, re.I)
        )


class DrawingTests(unittest.TestCase):
    def test_drawing_exists_and_covers_all_items(self):
        text = DRAWING.read_text()
        self.assertIn("MOD-TGT05's job is not to prove a target", text)
        self.assertIn("one-way liability detector", text.lower())
        self.assertIn("construction contract + drawing only", text.lower())
        self.assertIn("normalized-equality parity test", text.lower())
        for n in range(1, 18):
            self.assertRegex(text, rf"\|\s*{n}\s*\|", f"drawing missing checklist row {n}")

    def test_drawing_states_the_binding_version_is_not_touched(self):
        norm = _norm(DRAWING.read_text()).lower()
        self.assertIn("pr e3 does not touch it", norm)
        self.assertIn("pr e4 also bumps the tgt-05", norm)


if __name__ == "__main__":
    unittest.main()
