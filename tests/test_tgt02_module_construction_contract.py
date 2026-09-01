"""Runtime Migration PR E7: the MOD-TGT02 construction contract.

Asserts:
* the 17-item acceptance checklist is present, complete and ordered (template
  reused from the approved PR E1 template);
* items 03 / 05 / 07 / 08 are a normalized-equality parity with the FROZEN PR D
  TGT-02 contract (crc_adc_target_gateset.yaml), and item 04 is a derived parity
  against evidence_required + the ladder; the inference_guard is pinned verbatim;
* TGT-02 is frozen as a BIDIRECTIONAL scientific coverage gate -- its canonical
  Assessment CAN be POSITIVE or a genuine scientific NEGATIVE, and that NEGATIVE
  is never a fatal flag and never a KILL; a cross-cohort protein-level
  negative-coverage pattern is surfaced at most as a machine-local fatal_review
  = POTENTIAL_FATAL_PATTERN; "rare / highly heterogeneous" is upstream-qualified,
  never computed by the Module; transcript never becomes protein; bulk /
  pan-cancer is WEAK and a WEAK-only landscape is INCONCLUSIVE / UNKNOWN (never
  INCONCLUSIVE / WEAK); a single cohort is never a population-level answer (a
  typed CrcCohortCoverageCompletion gates the grade); EXPERIMENT_REQUIRED is
  allowed but narrow;
* the E7 contract PR shipped no implementation -- it forbade a
  gate_modules/tgt02.../ directory, a provider / adapter / retrieval / runner, a
  numeric / ranking score, a cohort-size / %-positive / H-score / heterogeneity
  threshold and a generic GateModule framework, and left MOD-TGT02
  primary_module_version at "0.0.0". Runtime Migration PR E8 then built the
  deferred implementation package against this still-frozen contract and raised
  the binding to "1.0.0"; MOD-TGT01 / MOD-TGT05 / MOD-TGT08 stay untouched and
  MIGRATION_PENDING remains (see ContractIsFrozenAndImplementedInPrE8Tests);
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt02_indication_specific_malignant_cell_coverage.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-02_Indication_Specific_Malignant_Cell_Coverage.md"
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
        self.assertEqual(m["pr"], "runtime_migration_pr_e7")
        self.assertEqual(
            m["scope"],
            "tgt02_mod_tgt02_construction_contract_drawing_validation_and_acceptance_checklist_only",
        )
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e8", m["next"])
        self.assertIn("TGT-08 -> TGT-02 -> TGT-03", m["order"])

    def test_template_provenance_reuses_the_e1_template(self):
        tp = self.doc["template_provenance"]
        self.assertEqual(tp["status"], "RECONSTRUCTED")
        self.assertTrue(tp["claim"]["not_claimed_verbatim_from_blueprint"])
        self.assertTrue(tp["claim"]["seventeen_item_template_reused_from_e1"])
        self.assertIn("e1 17-item construction template", tp["template_basis"].lower())
        self.assertTrue(E1_CONTRACT.is_file())

    def test_kernel_invariant_bidirectional_but_not_a_kill(self):
        inv = _norm(self.doc["kernel_invariant"])
        self.assertIn("src/ must never import gate_modules/", inv)
        self.assertIn("bidirectional scientific coverage gate", inv)
        self.assertIn("negative is a gate-relative scientific assessment; it is not a fatal flag and not a kill", inv)
        self.assertIn("potential_fatal_pattern", inv)
        self.assertIn("the module never passes and never kills the target", inv)

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
        self.assertEqual(i["gate_id"], "TGT-02")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["gateset_version"], "1.0")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT02")
        self.assertEqual(i["module_implementation_version"], "0.0.0")
        self.assertIn("pr e8 builds it", _norm(i["rule"]))


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt02 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-02"]

    def test_item03_gate_question_parity(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt02["gate_question"]),
        )

    def test_item05_evidence_ladder_parity(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt02["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt02["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt02["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_parity(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt02["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt02["forbidden_inference"]],
        )

    def test_item07_inference_guard_pinned_verbatim(self):
        g = self.item["07_allowed_and_forbidden_inference"]["inference_guard"]
        self.assertEqual(_norm(g["text"]), _norm(self.tgt02["inference_guard"]))
        self.assertIn("generic crc linkage does not discharge tgt-03", _norm(g["rule"]))

    def test_item08_fatal_conditions_parity(self):
        self.assertEqual(
            [_norm(x) for x in self.item["08_fatal_conditions"]["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt02["fatal_conditions"]],
        )

    def test_item04_derived_parity_is_exact_not_just_a_superset(self):
        # E7 round-1 blocker 4: item 04 admissible MUST equal the union of the
        # frozen PR D evidence_required and the ladder classes -- not merely a
        # superset -- so a new unfrozen evidence class cannot be smuggled in.
        i = self.item["04_admissible_evidence_classes"]
        self.assertEqual(
            [_norm(x) for x in i["evidence_required_from_pr_d"]],
            [_norm(x) for x in self.tgt02["evidence_required"]],
        )
        expected = {_norm(x) for x in self.tgt02["evidence_required"]}
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            expected |= {
                _norm(x)
                for x in self.tgt02["evidence_ladder"][grade]["admissible_evidence_classes"]
            }
        actual = {_norm(x) for x in i["admissible"]}
        self.assertEqual(actual, expected)

    def test_item04_excludes_the_other_seven_gates(self):
        na = " ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"])
        for gid in ("TGT-01", "TGT-03", "TGT-04", "TGT-05", "TGT-06", "TGT-07", "TGT-08"):
            self.assertIn(gid, na)

    def test_pr_d_unknown_behavior_is_bulk_rna_to_unknown(self):
        self.assertEqual(
            _norm(self.tgt02["unknown_behavior"]),
            "only bulk rna available -> unknown, not a pass.",
        )


class BidirectionalDirectionTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.i06 = self.item["06_direction_interpretation"]

    def test_direction_is_relative_to_the_gate_question(self):
        d = self.i06["direction_definitions"]
        self.assertIn("supports malignant-cell target coverage", _norm(d["POSITIVE"]))
        self.assertIn("supports a lack of adequate malignant-cell target coverage", _norm(d["NEGATIVE"]))
        self.assertIn("genuinely incompatible coverage claims", _norm(d["CONFLICTING"]))
        self.assertIn("not the candidate", _norm(self.i06["absolute_note"]))

    def test_negative_is_reachable_and_a_scientific_finding(self):
        tt = self.i06["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["qualifying_protein_cohort_supports_absent_expression"]),
            "negative / direct",
        )
        self.assertEqual(
            _norm(tt["qualifying_protein_cohort_supports_rare_highly_heterogeneous_coverage"]),
            "negative / direct",
        )
        self.assertEqual(
            _norm(tt["qualifying_protein_cohort_supports_broad_consistent_presence"]),
            "positive / direct",
        )
        self.assertEqual(
            _norm(tt["qualifying_sc_spatial_or_tma_concordance_supports_absent_or_strongly_non_covered"]),
            "negative / indirect_strong",
        )

    def test_strength_is_the_highest_qualifying_class_not_a_two_axis_rule(self):
        s = _norm(self.i06["strength_is_the_highest_qualifying_evidence_class"])
        self.assertIn("highest qualifying frozen evidence class actually met", s)
        self.assertIn("no e6-style two-axis weaker-ceiling rule here", s)

    def test_qualifying_is_rung_specific_not_a_single_protein_bar(self):
        # E7 round-1 blocker 1: "qualifying" is rung-specific, so sc/spatial can
        # be qualifying INDIRECT_STRONG without being protein-level.
        q = self.i06["qualifying_is_rung_specific"]
        self.assertIn("rung-specific", _norm(q["note"]))
        self.assertIn("protein-level", _norm(q["DIRECT_qualification_additionally_requires"]))
        self.assertIn("malignant-compartment", _norm(q["INDIRECT_STRONG_qualification_requires"]))
        self.assertIn("without being protein-level", _norm(q["note_2"]))
        self.assertIn("rung-specific", _norm(self.i06["frozen_truth_table"]["note"]))

    def test_direction_is_an_aggregate_not_an_observation(self):
        # E7 round-1 blocker 3: a single observation is never a Direction; the
        # classifier emits a rung-classed, direction-SUPPORTING observation and
        # aggregate produces the proposal only over a completed landscape.
        d = _norm(self.i06["direction_is_an_aggregate_not_an_observation"])
        self.assertIn("a single observation is never a direction", d)
        self.assertIn("direct-class, negative-supporting observation", d)
        self.assertIn("not yet a negative / direct proposal", d)
        self.assertIn("until that landscape is complete the final assessment stays inconclusive / unknown", d)
        tt = self.i06["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["single_direct_class_negative_cohort_with_the_crc_coverage_landscape_incomplete"]),
            "inconclusive / unknown",
        )
        self.assertEqual(
            _norm(tt["completed_audited_landscape_highest_rung_direct_material_negative_no_unresolved_incompatible_positive"]),
            "negative / direct",
        )
        self.assertEqual(
            _norm(tt["completed_audited_landscape_with_incompatible_positive_and_negative_evidence_and_no_qualified_heterogeneity_pattern"]),
            "conflicting / direct",
        )

    def test_rare_or_heterogeneous_is_upstream_qualified_never_computed(self):
        r = _norm(self.i06["rare_or_highly_heterogeneous_is_upstream_qualified"])
        self.assertIn("does not compute them from a percent-positive value, an h-score or a cohort n", r)
        self.assertIn("source_reported", r)
        self.assertIn("human_reviewed_normalization", r)
        self.assertIn("hard integrity failure", r)

    def test_weak_only_landscape_is_unknown_not_weak(self):
        tt = self.i06["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["weak_only_public_evidence_or_incomplete_crc_coverage_search"]),
            "inconclusive / unknown",
        )
        never = [_norm(x) for x in tt["never"]]
        self.assertTrue(any("weak-only public landscape -> inconclusive / weak" in x for x in never))
        wvu = _norm(self.i06["weak_vs_unknown"])
        self.assertIn("not inconclusive / weak", wvu)
        self.assertIn("inconclusive / unknown carries zero evidence_refs", wvu)

    def test_graded_inconclusive_vs_unknown_is_distinct(self):
        tt = self.i06["frozen_truth_table"]
        self.assertEqual(
            _norm(tt["qualifying_direct_authority_landscape_with_no_directional_resolution"]),
            "inconclusive / direct",
        )
        self.assertEqual(
            _norm(tt["qualifying_indirect_strong_landscape_with_no_directional_resolution"]),
            "inconclusive / indirect_strong",
        )
        g = _norm(self.i06["graded_inconclusive_vs_unknown"])
        self.assertIn("qualifying direct- or indirect_strong-quality evidence exists", g)
        self.assertIn("strictly distinct", g)

    def test_conflicting_is_not_auto_equated_with_heterogeneity(self):
        c = _norm(self.i06["conflicting_vs_qualified_heterogeneity"])
        self.assertIn("do not auto-equate real biological heterogeneity with a conflict", c)
        self.assertIn("characterizes coverage as rare_highly_heterogeneous is negative, not conflicting", c)
        never = [_norm(x) for x in self.i06["frozen_truth_table"]["never"]]
        self.assertTrue(any("rare_highly_heterogeneous -> conflicting (that is negative)" in x for x in never))

    def test_transcript_never_becomes_protein_in_the_ladder_rule(self):
        rule = _norm(self.item["05_evidence_ladder_and_evidence_ceiling"]["rule"])
        self.assertIn("transcript evidence never exceeds indirect_strong", rule)
        self.assertIn("never raises the evidence-class ceiling to direct", rule)


class FatalBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.i08 = self.item["08_fatal_conditions"]

    def test_single_cohort_is_a_supporting_observation_not_a_direction_or_fatal(self):
        s = self.i08["single_cohort_vs_cross_cohort_pattern"]
        one = _norm(s["one_protein_cohort_supporting_absent_or_rare_heterogeneous_coverage"])
        self.assertIn("direct-class, negative-supporting observation", one)
        self.assertIn("not yet a negative / direct proposal", one)
        self.assertIn("not fatal", one)
        self.assertIn("not fatal", _norm(s["transcript_only_negative_signal"]))

    def test_across_cohorts_is_at_least_two_not_more_than_two(self):
        # E7 round-1 blocker 2: the frozen scoping is plural logic (>= 2), NOT
        # "more than two" / "> 2" (which would be an unintended >= 3 threshold).
        a = _norm(self.i08["across_cohorts_is_plural_cohorts_logic_not_a_new_threshold"])
        self.assertIn("at least two independent cohort identities", a)
        self.assertIn("two independent qualifying cohorts is a cross-cohort candidate pattern", a)
        self.assertIn('it is not "more than two" / "> 2"', a)
        self.assertNotIn("more than two independent", a.replace('it is not "more than two"', ""))
        crit = " ".join(self.i08["machine_detection_criteria"]).lower()
        self.assertIn("at least two independent cohort identities", crit)
        self.assertNotIn("more than two", crit)
        riff = _norm(
            self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["required_is_true_iff"]
        )
        self.assertIn("at least two independent cohort identities", riff)
        self.assertNotIn("more than two", riff)
        # the whole contract must not smuggle a "> 2" threshold back in
        body = CONTRACT.read_text()
        self.assertNotIn("> 2 independent", body)

    def test_machine_emits_at_most_potential_fatal_pattern(self):
        m = _norm(self.i08["machine_output_is_only_a_potential_pattern"])
        self.assertIn("status potential_fatal_pattern", m)
        self.assertIn("never emits public_fatal_signal_established, a canonical fatal flag, a kill, a hold or a decision", m)
        self.assertIn("fatal_gate_policy_ref is an independent gateset-level policy reference", m)

    def test_no_numeric_threshold_in_fatal_rule(self):
        rule = _norm(self.i08["rule"])
        self.assertIn("no numeric threshold, no percent-positive cutoff, no h-score cutoff, no heterogeneity score", rule)
        crit = " ".join(self.i08["machine_detection_criteria"]).lower()
        self.assertIn("qualified cohort adequacy status", crit)
        self.assertIn("auditable expression_pattern_basis", crit)
        self.assertIn("completed, audited crc coverage landscape", crit)

    def test_human_review_reserved_covers_independence_and_justification(self):
        hr = " ".join(self.i08["human_review_reserved"]).lower()
        self.assertIn("genuinely independent / non-overlapping", hr)
        self.assertIn('"rare and highly heterogeneous" characterisation is justified', hr)
        self.assertIn("satisfies the gateset fatal policy", hr)


class CompletionAndSourcePlanTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.i09 = self.item["09_evidence_source_plan"]

    def test_regime_is_public_hybrid_current_public_only_no_provider(self):
        self.assertEqual(self.i09["dominant_evidence_regime_frozen_contract"], "PUBLIC_HYBRID")
        self.assertEqual(self.i09["current_instantiation_regime"], "PUBLIC_ONLY")
        self.assertFalse(self.i09["connect_provider_in_this_pr"])

    def test_source_hard_locks(self):
        locks = " ".join(self.i09["source_authority_rules"]).lower()
        self.assertIn("transcript never becomes protein", locks)
        self.assertIn("bulk crc rna and pan-cancer data can never become malignant-cell attributed", locks)
        self.assertIn("stromal expression, immune-cell expression and unresolved mixed-tissue expression are not crc malignant-cell expression", locks)
        self.assertIn("never \"normal low + tumor high -> favorable therapeutic index\"", locks)
        self.assertIn("never raises the evidence-class ceiling above indirect_strong", locks)

    def test_completion_landscape_has_four_mandatory_components_and_a_typed_record(self):
        c = self.i09["crc_cohort_coverage_landscape"]
        self.assertEqual(len(c["declared_mandatory_search_components"]), 4)
        rule = _norm(c["rule"])
        self.assertIn("no single positive or negative cohort \"counts as\" a population-level answer", rule)
        self.assertIn("module-local typed crccohortcoveragecompletion record", rule)
        self.assertIn("not a seventh core object", rule)

    def test_no_universal_threshold(self):
        n = _norm(self.i09["no_universal_threshold"])
        self.assertIn("no cohort-size cutoff, no percent-positive cutoff, no h-score cutoff, no heterogeneity score, no ranking", n)


class RuntimeGeneAndProposalTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item10_single_authoritative_target_no_implicit_context(self):
        i = self.item["10_input_contract"]
        joined = " ".join(i["required_inputs"]).lower()
        self.assertIn("canonical target identity", joined)
        self.assertIn("no separate drift-prone target argument", joined)
        self.assertIn("declared crc coverage search scope", joined)
        self.assertIn("fail rather than assume", _norm(i["forbidden"]))

    def test_item11_gate_neutral_exact_reuse_and_audit_snapshot(self):
        i = self.item["11_evidencepackage_output_contract"]
        each = " ".join(i["each_package"]).lower()
        self.assertIn("atomic and gate-neutral", each)
        self.assertIn("structured snapshot of the crccohortcoveragecompletion it certifies", each)
        may_not = " ".join(i["neutral_wording"]["may_not_say"]).lower()
        self.assertIn("target_a passes tgt-02", may_not)
        self.assertIn("target_a should be killed", may_not)
        rules = " ".join(i["rules"]).lower()
        self.assertIn("reuses the exact canonical package", rules)
        self.assertIn("hard identity integrity failure", rules)

    def test_item12_non_canonical_envelope_and_module_local_fatal_review(self):
        i = self.item["12_assessment_proposal_envelope_contract"]
        never = " ".join(i["the_proposal_envelope_never_carries"]).lower()
        self.assertIn("assessment_id", never)
        self.assertIn("review.status", never)
        self.assertIn("a fatal flag", never)
        fr = i["fatal_review"]
        self.assertEqual(fr["machine_may_emit"], "POTENTIAL_FATAL_PATTERN")
        mne = fr["machine_never_emits"].lower()
        self.assertIn("public_fatal_signal_established", mne)
        self.assertIn("canonical fatal flag", mne)
        self.assertIn("kill", mne)
        self.assertIn("actionable handoff only on an accepted run", _norm(fr["only_actionable_on_an_accepted_run"]))
        fields = " ".join(fr["fields"]).lower()
        self.assertIn("cohort_ids", fields)
        self.assertIn("expression_pattern_basis_refs", fields)

    def test_item13_machine_acceptance_hard_locks(self):
        crit = " ".join(
            self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]
        ).lower()
        self.assertIn("completion <-> search_completion_audit snapshot parity passes", crit)
        self.assertIn("transcript-level evidence never proposes above indirect_strong", crit)
        self.assertIn("protein without malignant-cell attribution never reaches direct", crit)
        self.assertIn("weak-only public evidence -> inconclusive / unknown (never inconclusive / weak)", crit)
        self.assertIn("inconclusive / unknown carries zero evidence_refs", crit)
        self.assertIn("no numeric or ranking score anywhere", crit)
        self.assertIn("no cohort-size / percent-positive / h-score / heterogeneity threshold", crit)
        self.assertIn("no tgt-03 persistence conclusion", crit)
        self.assertIn("no public_fatal_signal_established / kill / hold / decision", crit)
        on_fail = _norm(self.item["13_machine_acceptance_criteria"]["on_failure"])
        self.assertIn("rejects the whole run", on_fail)
        self.assertIn("never degraded to an accepted unknown", on_fail)
        self.assertIn("unknown from a genuinely incomplete public crc coverage search is not an integrity failure", on_fail)

    def test_item15_weak_and_incomplete_are_unknown_and_experiment_required_is_narrow(self):
        i = self.item["15_failure_unknown_and_conflict_behavior"]
        self.assertIn("never inconclusive / weak", _norm(i["weak_only_bulk_or_pan_cancer"]))
        self.assertIn("do not grade early", _norm(i["incomplete_crc_coverage_search"]))
        er = _norm(i["experiment_required"])
        self.assertIn("enumerated public crc coverage source space is completed / exhausted", er)
        self.assertIn("known public dataset that has not been fetched", er)
        self.assertIn("public_resolvable", er)
        self.assertIn("currently_unresolvable", er)
        self.assertIn("stops chasing weaker proxy evidence", er)
        ar = " ".join(i["absolute_rules"]).lower()
        self.assertIn("a scientific negative is never a fatal flag and never a kill", ar)

    def test_item16_stop_rule_never_stops_on_first_negative_cohort(self):
        i = self.item["16_stop_rule"]
        self.assertIn("completed and audited before any graded direction", _norm(i["principle"]))
        self.assertIn("the module never stops on the first negative cohort", _norm(" ".join(i["potential_fatal_trigger"])))
        self.assertEqual(len(i["normal_stop_requires_all_of"]), 3)

    def test_item17_handoff_never_kills_and_never_discharges_tgt03(self):
        i = self.item["17_downstream_consumer_and_handoff"]
        notdo = " ".join(i["this_module_does_not"]).lower()
        self.assertIn("produce a candidate-level decision or kill", notdo)
        self.assertIn("emit public_fatal_signal_established", notdo)
        self.assertIn("let generic crc linkage discharge tgt-03", notdo)
        self.assertIn("grade a direction before the mandatory crc coverage landscape is complete", notdo)
        cons = " ".join(i["once_human_approved_the_resulting_canonical_CandidateGateAssessment_is_consumed_by"]).lower()
        self.assertIn("the next gate in the fatal-first order (tgt-03) as context only", cons)


class ContractIsFrozenAndImplementedInPrE8Tests(unittest.TestCase):
    """The E7 construction contract is design-only and stays frozen. The
    implementation package it deferred is now built by PR E8, so the repository
    state -- the package exists and the TGT-02 binding is 1.0.0 -- reconciles
    with what the contract said would happen."""

    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation_in_the_contract_pr(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["trial_or_dataset_retrieval_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_or_ranking_scoring"], "forbidden")
        self.assertEqual(p["cohort_size_or_percent_positive_or_hscore_or_heterogeneity_threshold"], "forbidden")
        self.assertEqual(p["generic_gatemodule_framework_or_base_class_in_this_pr"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt01"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt05"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt08"], "forbidden")
        # MIGRATION_PENDING remains -- five of eight primary Modules were still
        # unbuilt when the contract froze; it stays until all eight ship.
        self.assertEqual(p["migration_pending"], "remains")

    def test_tgt02_implementation_package_now_exists_post_e8(self):
        pkg = ROOT / "gate_modules" / "tgt02_indication_specific_malignant_cell_coverage"
        self.assertTrue(pkg.is_dir(), "PR E8 builds the deferred implementation package")
        for f in ("__init__.py", "module.yaml", "contracts.py", "ports.py",
                  "classify.py", "evidence.py", "aggregate.py", "completion.py",
                  "fatal_review.py", "acceptance.py", "module.py"):
            self.assertTrue((pkg / f).is_file(), f)

    def test_tgt02_binding_is_now_one_zero_zero_and_others_untouched(self):
        gs = yaml.safe_load(CRC_GATESET.read_text())
        by_gate = {
            b["gate_id"]: b["primary_module_version"]
            for b in gs["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(by_gate["TGT-02"], "1.0.0")
        self.assertEqual(by_gate["TGT-01"], "1.0.0")
        self.assertEqual(by_gate["TGT-05"], "1.0.0")
        self.assertEqual(by_gate["TGT-08"], "1.0.0")
        # PR E10 built MOD-TGT03; the remaining three stay unbuilt.
        self.assertEqual(by_gate["TGT-03"], "1.0.0")
        # PR E12 built MOD-TGT04; PR E14 built MOD-TGT06; PR E16 built MOD-TGT07.
        self.assertEqual(by_gate["TGT-04"], "1.0.0")
        self.assertEqual(by_gate["TGT-06"], "1.0.0")
        self.assertEqual(by_gate["TGT-07"], "1.0.0")

    def test_deferred_block_named_the_e8_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e8_plus"]).lower()
        self.assertIn("gate_modules/tgt02_indication_specific_malignant_cell_coverage/", joined)
        self.assertIn("crccohortcoveragecompletion", joined)
        self.assertIn("1.0.0", joined)

    def test_no_generic_gate_module_framework_or_base_class_added(self):
        gm = ROOT / "gate_modules"
        py_files = sorted(str(p.relative_to(ROOT)) for p in gm.rglob("*.py"))
        allowed = (
            "tgt01_adc_modality_precedent",
            "tgt02_indication_specific_malignant_cell_coverage",
            "tgt03_treatment_metastatic_persistence",
            "tgt04_tumor_surface_availability_density_plausibility",
            "tgt05_normal_tissue_fatal_liability",
            "tgt06_internalization_trafficking_addressability",
            "tgt07_shedding_soluble_antigen_sink_liability",
            "tgt08_target_opportunity_competition_ip_whitespace",
        )
        self.assertTrue(all(any(pkg in p for pkg in allowed) for p in py_files), py_files)

    def test_no_numeric_threshold_or_ranking_score_in_the_contract(self):
        # "at least two independent cohort identities" is plural-cohorts logic,
        # explicitly NOT a biological threshold (E7-4). A real threshold is a percent / an
        # H-score / a per-cell or expression cutoff, or a ranking score.
        text = CONTRACT.read_text().lower()
        # a real threshold is a percent / an H-score / a per-cell or expression
        # cutoff with a comparator and a number -- never present. The contract's
        # "no ... score" / "no ... cutoff" prohibitions are expected.
        self.assertIsNone(
            re.search(
                r"\d\s*%|h-?score\s*[<>=]\s*\d|[<>=]\s*\d+\s*(percent|cells|tpm|fpkm|nmol|per cell)"
                r"|\bnumeric_score\s*=",
                text,
            )
        )
        self.assertIn("no cohort-size cutoff", text)
        self.assertIn("never emits a numeric or ranking score", text)
        self.assertIn("no numeric or ranking score anywhere", text)


class DrawingTests(unittest.TestCase):
    def setUp(self):
        self.text = DRAWING.read_text()

    def test_drawing_exists_and_names_the_module_and_pr(self):
        self.assertIn("MOD-TGT02", self.text)
        self.assertIn("Runtime Migration **PR E7**", self.text)
        self.assertIn("`MIGRATION_PENDING` remains", self.text)

    def test_drawing_covers_all_seventeen_items(self):
        for n in range(1, 18):
            self.assertRegex(self.text, rf"\|\s*{n}\s*\|", f"drawing row for item {n} missing")

    def test_drawing_states_negative_is_a_scientific_finding_not_a_kill(self):
        t = " ".join(self.text.lower().split())
        self.assertIn("a tgt-02 `negative` is not a fatal flag and not a `kill`", t)
        self.assertIn("bidirectional scientific coverage gate", t)
        self.assertIn("one pretty cohort is not a population-level answer", t)

    def test_drawing_freezes_the_completion_and_observation_shape(self):
        t = " ".join(self.text.lower().split())
        self.assertIn("crccohortcoveragecompletion", t)
        self.assertIn("no e6-style two mandatory axes", t)
        self.assertIn("expression_pattern_basis", t)
        self.assertIn("`experiment_required`", t)


if __name__ == "__main__":
    unittest.main()
