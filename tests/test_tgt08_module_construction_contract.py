"""Runtime Migration PR E5: the MOD-TGT08 construction contract.

Asserts:
* the 17-item acceptance checklist is present, complete and ordered (template
  reused from the approved PR E1 template);
* items 03 / 05 / 07 / 08 are a normalized-equality parity with the FROZEN PR D
  TGT-08 contract (crc_adc_target_gateset.yaml), and item 04 is a derived parity
  against evidence_required + the ladder -- not a hand approximation;
* TGT-08 is frozen as the external-opportunity gate: it is NOT scientific
  de-risking and NOT a sponsor decision; its canonical Assessment CAN be
  NEGATIVE, and that NEGATIVE is never a KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE;
  a freedom-to-operate / "no design-around" / "no differentiation path"
  conclusion is forbidden; DIRECT requires BOTH the competitive axis and the
  composition-level patent review; an absence-based whitespace claim needs
  completion provenance; sponsor_review is a machine-local review trigger only;
* PR E5 ships no implementation -- no gate_modules/tgt08.../ directory, no
  provider / adapter / retrieval / runner, no numeric or ranking scoring, no
  FTO logic, no generic GateModule framework; MOD-TGT08 primary_module_version
  stays "0.0.0"; MOD-TGT01 / MOD-TGT05 are untouched; MIGRATION_PENDING remains;
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt08_target_opportunity_competition_ip_whitespace.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-08_Target_Opportunity_Competition_IP_Whitespace.md"
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


def _norm(text) -> str:
    return " ".join(str(text).split()).strip().lower()


class ContractShapeTests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_version_and_migration_block(self):
        self.assertEqual(self.doc["version"], "0.1.0")
        m = self.doc["migration"]
        self.assertEqual(m["pr"], "runtime_migration_pr_e5")
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e6", m["next"])
        self.assertIn("TGT-01 -> TGT-05 -> TGT-08 -> TGT-02", m["order"])

    def test_template_provenance_reuses_the_e1_template(self):
        tp = self.doc["template_provenance"]
        self.assertEqual(tp["status"], "RECONSTRUCTED")
        self.assertTrue(tp["claim"]["not_claimed_verbatim_from_blueprint"])
        self.assertTrue(tp["claim"]["seventeen_item_template_reused_from_e1"])
        self.assertIn("e1 17-item construction template", tp["template_basis"].lower())
        self.assertTrue(E1_CONTRACT.is_file())

    def test_kernel_invariant_boundary_and_ip_whitespace_is_not_fto(self):
        inv = self.doc["kernel_invariant"].lower()
        self.assertIn("src/ must never import gate_modules/", inv)
        self.assertIn("does not evaluate the target's scientific validity", inv)
        self.assertIn("does not decide whether this sponsor should proceed", inv)
        self.assertIn("ip whitespace is an evidence-backed landscape signal; it is not freedom to operate", inv)

    def test_checklist_has_all_seventeen_items_in_order(self):
        checklist = self.doc["acceptance_checklist"]
        self.assertEqual(tuple(checklist), _CHECKLIST_KEYS)
        self.assertEqual(len(checklist), 17)

    def test_checklist_keys_match_the_e1_template_keys(self):
        e1 = yaml.safe_load(E1_CONTRACT.read_text())["acceptance_checklist"]
        self.assertEqual(tuple(e1), _CHECKLIST_KEYS)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item01_gate_identity(self):
        i = self.item["01_gate_identity_and_version"]
        self.assertEqual(i["gate_id"], "TGT-08")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["gateset_version"], "1.0")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT08")
        self.assertEqual(i["module_implementation_version"], "0.0.0")


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt08 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-08"]

    def test_item03_gate_question_parity(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt08["gate_question"]),
        )

    def test_item05_evidence_ladder_parity(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt08["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt08["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt08["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_parity(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt08["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt08["forbidden_inference"]],
        )

    def test_item08_fatal_conditions_parity(self):
        self.assertEqual(
            [_norm(x) for x in self.item["08_fatal_conditions"]["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt08["fatal_conditions"]],
        )

    def test_item04_derived_parity_against_evidence_required_and_ladder(self):
        i = self.item["04_admissible_evidence_classes"]
        self.assertEqual(
            [_norm(x) for x in i["evidence_required_from_pr_d"]],
            [_norm(x) for x in self.tgt08["evidence_required"]],
        )
        ladder_classes = []
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            ladder_classes += [
                _norm(x) for x in self.tgt08["evidence_ladder"][grade]["admissible_evidence_classes"]
            ]
        self.assertEqual([_norm(x) for x in i["admissible"]], ladder_classes)

    def test_item04_excludes_the_other_seven_gates(self):
        na = " ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"])
        for gid in ("TGT-01", "TGT-02", "TGT-03", "TGT-04", "TGT-05", "TGT-06", "TGT-07"):
            self.assertIn(gid, na)

    def test_pr_d_unknown_behavior_is_incomplete_landscape_to_unknown(self):
        self.assertEqual(_norm(self.tgt08["unknown_behavior"]), "incomplete landscape -> unknown.")


class CommercialStrategicBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_negative_is_reachable_and_bounded(self):
        framing = self.item["03_gate_question"]["tgt08_framing"]
        blob = _norm(framing["negative_is_reachable_and_bounded"])
        self.assertIn("can propose a canonical negative assessment", blob)
        self.assertIn("not: a scientifically bad target, a kill", blob)
        self.assertIn("out_of_mandate", blob)
        i06 = self.item["06_direction_interpretation"]
        self.assertIn("reachable", _norm(i06["NEGATIVE"]))
        tt = i06["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["completed_landscape_only_material_opportunity_opposing_signals"]),
            "negative / <overall rung>",
        )
        self.assertEqual(
            _norm(tt["completed_landscape_only_material_opportunity_supporting_signals"]),
            "positive / <overall rung>",
        )

    def test_negative_is_never_a_kill_or_sponsor_stop(self):
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        blob = _norm(i15["negative_is_not_a_kill"])
        self.assertIn("never a kill, stop_for_sponsor or out_of_mandate", blob)
        self.assertIn("never de-risks or re-risks tgt-01 through tgt-07", blob)

    def test_favorable_commercial_picture_cannot_de_risk_the_science(self):
        forb = [_norm(x) for x in self.item["07_allowed_and_forbidden_inference"]["forbidden"]]
        self.assertTrue(any("scientific de-risking (tgt-01 through tgt-07) from a favorable commercial picture" in x for x in forb))
        tt = self.item["06_direction_interpretation"]["frozen_truth_table"]
        never = [_norm(x) for x in tt["never"]]
        self.assertIn("a favorable commercial picture -> tgt-01 through tgt-07 are de-risked", never)

    def test_fto_and_no_design_around_are_explicitly_forbidden(self):
        i07 = self.item["07_allowed_and_forbidden_inference"]
        forb = [_norm(x) for x in i07["forbidden"]]
        self.assertTrue(any("freedom-to-operate opinion or a \"no viable design-around\" conclusion" in x for x in forb))
        also = [_norm(x) for x in i07["also_forbidden_for_the_module"]]
        self.assertTrue(any("no design-around exists" in x for x in also))
        self.assertTrue(any("no differentiation path" in x for x in also))
        i09 = self.item["09_evidence_source_plan"]
        self.assertIn("not a freedom-to-operate judgement",
                      _norm(i09["two_axes"]["composition_level_patent_axis"]["not_fto"]))

    def test_sponsor_variables_excluded_from_direction(self):
        i06 = self.item["06_direction_interpretation"]
        self.assertIn("must not enter the module's direction", _norm(i06["sponsor_variables_excluded"]))
        na = " ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"]).lower()
        self.assertIn("sponsor capability", na)
        self.assertIn("company mandate", na)


class TwoAxisEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_direct_requires_both_axes_at_direct_authority_not_just_coverage(self):
        i16 = self.item["16_stop_rule"]
        dr = _norm(i16["direct_requires"])
        self.assertIn("both required axes complete at direct authority", dr)
        self.assertIn("capped at indirect_strong", dr)
        two = i16["two_axis_mandatory_coverage"]
        self.assertEqual(len(two["before_a_complete_landscape_assessment_both_must_complete"]), 2)
        cinc = _norm(two["coverage_complete_is_not_direct_quality"])
        self.assertIn("precondition for a target-specific direct / indirect_strong graded opportunity assessment, not by themselves a direct one", cinc)
        self.assertIn("not a precondition for the frozen unmet-need-only weak hypothesis", cinc)
        i13 = " ".join(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]).lower()
        self.assertIn("an overall direct requires both the primary-source competitive axis and the composition-level patent review complete at direct authority", i13)

    def test_overall_strength_is_the_weaker_required_axis_ceiling(self):
        i06 = self.item["06_direction_interpretation"]
        s = _norm(i06["strength_is_the_weaker_required_axis_ceiling"])
        self.assertIn("it is the ceiling of the weaker required axis", s)
        self.assertIn("competitive direct + patent indirect_strong -> overall capped at indirect_strong", s)
        tt = i06["frozen_truth_table"]
        never = [_norm(x) for x in tt["never"]]
        self.assertIn("both axes searched -> direct (the overall rung is the weaker required axis ceiling)", never)
        i13 = " ".join(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]).lower()
        self.assertIn("the overall proposed_strength equals the weaker required axis ceiling", i13)

    def test_completed_landscape_with_no_directional_signal_is_a_graded_inconclusive(self):
        tt = self.item["06_direction_interpretation"]["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["completed_landscape_no_material_directional_signal_direct_authority"]),
            "inconclusive / direct",
        )
        self.assertEqual(
            _norm(tt["completed_landscape_no_material_directional_signal_indirect_strong_authority"]),
            "inconclusive / indirect_strong",
        )
        gvu = _norm(self.item["06_direction_interpretation"]["graded_inconclusive_vs_unknown"])
        self.assertIn("inconclusive / unknown means the landscape is materially incomplete", gvu)
        self.assertIn("we could not look", gvu)
        self.assertIn("we looked well and the evidence does not resolve direction", gvu)
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        cl = _norm(i15["completed_landscape_with_no_material_directional_signal"])
        self.assertIn("propose a graded inconclusive", cl)
        self.assertIn("not inconclusive / unknown", cl)
        self.assertIn("evidence_refs are non-empty", cl)
        i13 = " ".join(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]).lower()
        self.assertIn("a graded inconclusive carries non-empty evidence_refs", i13)
        self.assertIn("inconclusive / unknown carries no evidence_refs", i13)

    def test_pipeline_db_alone_caps_at_indirect_strong(self):
        i09 = self.item["09_evidence_source_plan"]["two_axes"]["competitive_landscape_axis"]
        self.assertIn("never the evidence authority",
                      _norm(i09["indirect_strong_only"][0]))
        i05 = self.item["05_evidence_ladder_and_evidence_ceiling"]["INDIRECT_STRONG"]["admissible_evidence_classes"]
        self.assertTrue(any("pipeline-database competitor summaries" in _norm(x) for x in i05))

    def test_target_level_patent_search_alone_caps_at_indirect_strong(self):
        i05 = self.item["05_evidence_ladder_and_evidence_ceiling"]["INDIRECT_STRONG"]["admissible_evidence_classes"]
        self.assertTrue(any("target-level (not composition-level) patent search" in _norm(x) for x in i05))
        cap = _norm(self.item["09_evidence_source_plan"]["two_axes"]["composition_level_patent_axis"]["indirect_strong_only"][0])
        self.assertIn("target-level (not composition-level) patent search", cap)

    def test_unmet_need_alone_is_weak_no_opportunity_claim(self):
        i05 = self.item["05_evidence_ladder_and_evidence_ceiling"]["WEAK"]
        self.assertIn("no opportunity / whitespace claim; hypothesis only", _norm(i05["ceiling_rule"]))
        tt = self.item["06_direction_interpretation"]["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["indication_level_unmet_need_only_no_target_specific_read_attempted"]),
            "inconclusive / weak",
        )
        never = [_norm(x) for x in tt["never"]]
        self.assertIn("refractory mcrc is grim -> this target is a good opportunity", never)

    def test_incomplete_landscape_is_unknown(self):
        tt = self.item["06_direction_interpretation"]["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["target_specific_landscape_attempted_but_a_mandatory_axis_incomplete_or_no_admissible_evaluable_landscape"]),
            "inconclusive / unknown",
        )
        i15 = _norm(self.item["15_failure_unknown_and_conflict_behavior"]["incomplete_landscape"])
        self.assertIn("incomplete landscape -> unknown", i15)
        self.assertIn("we could not look", i15)
        one_axis = _norm(self.item["16_stop_rule"]["two_axis_mandatory_coverage"]["one_axis_not_done"])
        self.assertIn("half landscape cannot yield a target-opportunity judgement", one_axis)

    def test_unmet_need_only_weak_is_exempt_from_the_two_axis_completion_rule(self):
        i06 = self.item["06_direction_interpretation"]
        prec = _norm(i06["unmet_need_only_vs_incomplete_target_landscape"])
        self.assertIn("is a prerequisite for a target-specific direct / indirect_strong opportunity assessment, not for the frozen unmet-need-only weak hypothesis", prec)
        self.assertIn("no target-specific competitive / ip read attempted -> inconclusive / weak", prec)
        self.assertIn("one mandatory axis is incomplete -> inconclusive / unknown", prec)
        self.assertIn("both pr d statements are preserved", prec)
        s = _norm(i06["strength_is_the_weaker_required_axis_ceiling"])
        self.assertIn("the explicit indication-level unmet-need-only weak hypothesis is exempt from the two-axis precondition", s)
        one_axis = _norm(self.item["16_stop_rule"]["two_axis_mandatory_coverage"]["one_axis_not_done"])
        self.assertIn("exception: the explicit indication-level unmet-need-only weak hypothesis", one_axis)
        self.assertIn("not unknown", one_axis)
        never = [_norm(x) for x in i06["frozen_truth_table"]["never"]]
        self.assertTrue(any("unmet-need-only with no target-specific read attempted -> unknown" in x for x in never))
        w = _norm(self.item["15_failure_unknown_and_conflict_behavior"]["weak_unmet_need_only"])
        self.assertIn("exempt from the two-axis mandatory completion", w)
        # item 13 machine acceptance must carry the SAME precedence, not the
        # old generalized "unsearched mandatory axis -> UNKNOWN" rule.
        i13 = " ".join(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]).lower()
        self.assertIn("unmet-need-only with no target-specific competitive / ip read attempted -> inconclusive / weak", i13)
        self.assertIn("a target-specific landscape assessment was attempted and a mandatory axis is incomplete, or there is no admissible evaluable landscape -> inconclusive / unknown", i13)

    def test_absence_inference_needs_completion_provenance(self):
        i09 = _norm(self.item["09_evidence_source_plan"]["absence_inference_needs_completion_provenance"])
        self.assertIn("complete audited search returned no qualifying competitor -- never from records == [] alone", i09)
        self.assertIn("\"no patent found\" is not \"patent whitespace\"", i09)
        self.assertIn("not a seventh core object", i09)
        i13 = " ".join(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]).lower()
        self.assertIn("absence-based whitespace / no-competitor claim is backed by an explicit completed-search provenance record", i13)
        self.assertIn("an absence claim with no completion provenance",
                      _norm(self.item["13_machine_acceptance_criteria"]["on_failure"]))

    def test_index_is_not_evidence_authority(self):
        pa = _norm(self.item["09_evidence_source_plan"]["two_axes"]["composition_level_patent_axis"]["patent_database_authority"])
        self.assertIn("index is not evidence authority", pa)
        self.assertIn("same rule as adcdb in tgt-01", pa)


class SponsorReviewTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_sponsor_review_is_machine_local_only_and_distinct_from_fatal_review(self):
        sr = self.item["12_assessment_proposal_envelope_contract"]["sponsor_review"]
        blob = _norm(sr["what_it_is"])
        self.assertIn("non-canonical, module-local", blob)
        self.assertIn("not a new core object", blob)
        self.assertIn("distinct record from tgt-05's fatal_review", blob)
        self.assertEqual(sr["machine_may_emit"], "POTENTIAL_SPONSOR_FATAL_PATTERN")
        never = [_norm(x) for x in sr["machine_never_emits"]]
        for token in ("kill", "stop_for_sponsor", "out_of_mandate", "a canonical fatal flag"):
            self.assertIn(token, never)

    def test_machine_cannot_assert_dominant_well_protected_or_no_differentiation_path(self):
        mvh = self.item["08_fatal_conditions"]["machine_vs_human_split"]
        never = [_norm(x) for x in mvh["machine_never_asserts"]]
        self.assertIn("the competitor is truly \"dominant\"", never)
        self.assertIn("the patent estate is legally \"well protected\"", never)
        self.assertIn("there is \"no differentiation path\"", never)
        self.assertIn("this sponsor should stop", never)

    def test_sponsor_review_cannot_become_a_canonical_kill(self):
        i17 = self.item["17_downstream_consumer_and_handoff"]
        does_not = [_norm(x) for x in i17["this_module_does_not"]]
        self.assertTrue(any("route the sponsor_review record through the scientific fatal_gate_policy or turn it into a canonical scientific fatal" in x for x in does_not))
        routed = " ".join(i17["the_sponsor_review_record_is_routed_to"]).lower()
        self.assertIn("external sponsor governance", routed)
        self.assertIn("sponsor-relative axis", routed)

    def test_sponsor_review_not_in_the_proposal_envelope(self):
        never = [_norm(x) for x in self.item["12_assessment_proposal_envelope_contract"]["the_proposal_envelope_never_carries"]]
        self.assertTrue(any("the potential-sponsor-fatal-pattern signal lives in the module-local sponsor_review record, not the proposal envelope" in x for x in never))
        self.assertTrue(any("no differentiation path" in x for x in never))


class InheritsRuntimeGenesTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item10_single_authoritative_target_and_landscape_as_of(self):
        i10 = self.item["10_input_contract"]
        req = " ".join(i10["required_inputs"]).lower()
        self.assertIn("single authoritative target", req)
        self.assertIn("no separate drift-prone target argument", req)
        self.assertIn("landscape_as_of", req)
        self.assertIn("a landscape with no as_of date is not admissible", _norm(i10["forbidden"]))

    def test_item11_gate_neutral_and_exact_canonical_reuse(self):
        i11 = self.item["11_evidencepackage_output_contract"]
        each = " ".join(i11["each_package"]).lower()
        self.assertIn("gate-neutral", each)
        rules = " ".join(i11["rules"]).lower()
        self.assertIn("reuses the exact canonical package, never copies or re-creates one", rules)
        self.assertIn("present and equal", rules)
        self.assertIn("hard identity integrity failure", rules)
        self.assertIn("no tgt-08 opportunity conclusion stamped onto it", each)

    def test_item12_non_canonical_envelope_omits_canonical_fields(self):
        i12 = self.item["12_assessment_proposal_envelope_contract"]
        never = " ".join(i12["the_proposal_envelope_never_carries"]).lower()
        self.assertIn("assessment_id / assessment_version", never)
        self.assertIn("review.status", never)
        pins = i12["the_proposal_envelope_carries"]["identity_pins_for_deterministic_canonicalisation"]
        joined = " ".join(pins)
        for pin in ("candidate_id", "instantiation_id", "context_id", "context_version",
                    "gateset_id", "gateset_version", "gate_id (TGT-08)", "gate_version"):
            self.assertIn(pin, joined)

    def test_item13_hard_integrity_failure_rejects_the_run(self):
        onf = _norm(self.item["13_machine_acceptance_criteria"]["on_failure"])
        self.assertIn("rejects the whole run", onf)
        self.assertIn("never degraded to an accepted unknown", onf)
        self.assertIn("unknown from a genuinely incomplete landscape is not an integrity failure", onf)

    def test_no_experiment_required_resolution_for_fto(self):
        i15 = _norm(self.item["15_failure_unknown_and_conflict_behavior"]["resolution_kinds"])
        self.assertIn("does not use experiment_required", i15)
        i16 = _norm(self.item["16_stop_rule"]["fto_is_not_an_experiment"])
        self.assertIn("never written as experiment_required", i16)


class NoImplementationInPrE5Tests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["trial_or_patent_retrieval_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_or_ranking_scoring"], "forbidden")
        self.assertEqual(p["freedom_to_operate_or_legal_logic_in_this_pr"], "forbidden")
        self.assertEqual(p["sponsor_decision_runtime_in_this_pr"], "forbidden")
        self.assertEqual(p["generic_gatemodule_framework_or_base_class_in_this_pr"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt01"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt05"], "forbidden")
        self.assertEqual(p["migration_pending"], "remains")

    def test_deferred_block_names_the_e6_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e6_plus"]).lower()
        self.assertIn("gate_modules/tgt08_target_opportunity_competition_ip_whitespace/", joined)
        self.assertIn("1.0.0", joined)
        self.assertIn("sponsor_review detector", joined)

    def test_pr_e5_shipped_no_implementation_under_gate_modules(self):
        module_yaml = (
            ROOT / "gate_modules" / "tgt08_target_opportunity_competition_ip_whitespace" / "module.yaml"
        )
        if not module_yaml.exists():
            return
        manifest = yaml.safe_load(module_yaml.read_text())["module"]
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e6")
        self.assertEqual(
            manifest["construction_contract"],
            "src/contracts/gate_modules/tgt08_target_opportunity_competition_ip_whitespace.yaml",
        )

    def test_tgt08_binding_matches_the_module_build_state(self):
        gateset = yaml.safe_load(CRC_GATESET.read_text())
        binding = next(
            b for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-08"
        )
        self.assertEqual(binding["primary_module_id"], "MOD-TGT08")
        module_yaml = (
            ROOT / "gate_modules" / "tgt08_target_opportunity_competition_ip_whitespace" / "module.yaml"
        )
        expected = "0.0.0"
        if module_yaml.exists():
            expected = yaml.safe_load(module_yaml.read_text())["module"]["module_version"]
        self.assertEqual(binding["primary_module_version"], expected)

    def test_mod_tgt01_and_mod_tgt05_bindings_are_untouched(self):
        gateset = yaml.safe_load(CRC_GATESET.read_text())
        by_gate = {
            b["gate_id"]: b["primary_module_version"]
            for b in gateset["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(by_gate["TGT-01"], "1.0.0")
        self.assertEqual(by_gate["TGT-05"], "1.0.0")

    def test_no_generic_gate_module_framework_or_base_class_added(self):
        gm = ROOT / "gate_modules"
        py_files = sorted(str(p.relative_to(ROOT)) for p in gm.rglob("*.py"))
        allowed = (
            "tgt01_adc_modality_precedent",
            "tgt05_normal_tissue_fatal_liability",
            "tgt08_target_opportunity_competition_ip_whitespace",
        )
        self.assertTrue(
            all(any(pkg in p for pkg in allowed) for p in py_files), py_files
        )

    def test_no_numeric_threshold_or_ranking_score_in_the_contract(self):
        text = CONTRACT.read_text()
        self.assertIsNone(
            re.search(r"[<>]\s*\d|\b\d[\d,]*\s*(competitors|families|claims|%)", text, re.I)
        )
        self.assertIn("no competitor count cutoff", text.lower())

    def test_migration_pending_remains(self):
        self.assertEqual(self.doc["repository_policy"]["migration_pending"], "remains")
        gateset = yaml.safe_load(CRC_GATESET.read_text())
        self.assertIn("per_gate_primary_modules", gateset["migration"]["deferred"])


class DrawingTests(unittest.TestCase):
    def test_drawing_exists_and_covers_all_items(self):
        text = DRAWING.read_text()
        self.assertIn("MOD-TGT08", text)
        self.assertIn("Runtime Migration **PR E5**", text)
        self.assertIn(
            "TGT-08 evaluates the external opportunity landscape; it does not evaluate\n> the target's scientific validity",
            text,
        )
        self.assertIn(
            "IP whitespace is an evidence-backed landscape signal. It is not freedom to\n> operate.",
            text,
        )
        for n in range(1, 18):
            self.assertIn(f"| {n} | **", text, f"drawing row {n} missing")
        self.assertIn("PR E5 does not touch it", text.replace("**", ""))
        self.assertIn("PR E6", text)

    def test_drawing_states_negative_is_reachable(self):
        text = " ".join(DRAWING.read_text().lower().split())
        self.assertIn("the first gate whose canonical assessment can be `negative`", text)
        self.assertIn("it is **not** a scientifically bad target", text)

    def test_drawing_item06_does_not_conflate_coverage_complete_with_direct(self):
        text = " ".join(DRAWING.read_text().lower().split())
        self.assertNotIn("at `direct` if both axes complete", text)
        self.assertIn("overall strength = the weaker required axis ceiling", text)
        self.assertIn("no material directional signal → a graded `inconclusive`", text)
        self.assertIn('*"both axes searched"* alone never yields `direct`', text)


if __name__ == "__main__":
    unittest.main()
