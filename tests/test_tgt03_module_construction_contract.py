"""Runtime Migration PR E9: the MOD-TGT03 construction contract.

Asserts:
* the 17-item acceptance checklist is present, complete and ordered (template
  reused from the approved PR E1 template);
* items 03 / 05 / 07 / 08 are a normalized-equality parity with the FROZEN PR D
  TGT-03 contract (crc_adc_target_gateset.yaml), item 04 is an EXACT derived
  parity (set equality, not a superset) against evidence_required + the ladder,
  and the inference_guard is pinned verbatim;
* TGT-03 is frozen as a BIDIRECTIONAL scientific persistence gate -- its
  canonical Assessment CAN be POSITIVE (retention supported) or a genuine
  scientific NEGATIVE (materially impaired persistence), and that NEGATIVE is
  never a fatal flag and never a KILL; a reproducible protein-level near / marked
  loss is surfaced at most as a machine-local fatal_review =
  POTENTIAL_FATAL_PATTERN;
* the four ChatGPT AI审核方案 scoping corrections are frozen: (1)
  TRANSIENT_OR_MINOR_DOWNREGULATION SUPPORTS persistence (it is not fixed to
  CONTEXTUAL) and never contributes NEGATIVE or fatal_review; (2) "reproducible"
  is established by Route A (explicit reproducibility qualification) OR Route B
  (>= 2 independent qualified contexts) and is NOT defined by a numeric context
  count / "> 2"; (3) DIRECT protein measurement is an OPEN set, not a closed
  three-assay whitelist; (4) an EvidencePackage MAY state the empirical
  persistence / loss fact and only Gate-relative conclusions are forbidden;
* baseline TGT-02 coverage never discharges TGT-03, generic EVGAP-02 contributes
  only if its source / context explicitly qualify, transcript / a resistance
  model never reach DIRECT, treatment-naive primary CRC never reaches a
  persistence claim, and a WEAK-only landscape is INCONCLUSIVE / UNKNOWN (never
  INCONCLUSIVE / WEAK);
* PR E9 ships no implementation -- no gate_modules/tgt03.../ directory, no
  provider / adapter / retrieval / runner, no numeric / ranking score, no
  fold-change / %-positive / H-score / down-regulation / context-count threshold,
  no generic GateModule framework; MOD-TGT03 primary_module_version stays
  "0.0.0"; the binding, the registry and every existing test are untouched (the
  only allowed existing-file mutation is an append to logs/worklog.md);
  MIGRATION_PENDING remains;
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt03_treatment_metastatic_persistence.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-03_Treatment_Metastatic_Persistence.md"
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


def _flatten(node) -> str:
    """All string content of a nested dict / list, lower-cased and whitespace-collapsed."""
    out = []
    if isinstance(node, dict):
        for v in node.values():
            out.append(_flatten(v))
    elif isinstance(node, (list, tuple)):
        for v in node:
            out.append(_flatten(v))
    else:
        out.append(str(node))
    return _norm(" ".join(out))


class ContractShapeTests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_version_and_migration_block(self):
        self.assertEqual(self.doc["version"], "0.1.0")
        m = self.doc["migration"]
        self.assertEqual(m["pr"], "runtime_migration_pr_e9")
        self.assertEqual(
            m["scope"],
            "tgt03_mod_tgt03_construction_contract_drawing_validation_and_acceptance_checklist_only",
        )
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e10", m["next"])
        self.assertIn("TGT-02 -> TGT-03 -> TGT-04", m["order"])

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
        self.assertIn("bidirectional scientific persistence gate", inv)
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

    def test_three_headline_conclusions_are_frozen_verbatim(self):
        hc = self.doc["headline_conclusions"]
        self.assertEqual(len(hc), 3)
        joined = _norm(" ".join(hc))
        self.assertIn("baseline expression is not persistence", joined)
        self.assertIn("bidirectional scientific persistence gate", joined)
        self.assertIn("negative is not fatal and not kill", joined)
        self.assertIn("reproducibility requires auditable evidence and is not defined solely by a numeric context count", joined)
        self.assertIn("the module never decides fatality", joined)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item01_gate_identity(self):
        i = self.item["01_gate_identity_and_version"]
        self.assertEqual(i["gate_id"], "TGT-03")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["gate_name"], "Treatment / Metastatic Persistence")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["gateset_version"], "1.0")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT03")
        self.assertEqual(i["module_implementation_version"], "0.0.0")
        self.assertIn("pr e10 builds it", _norm(i["rule"]))


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt03 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-03"]

    def test_item03_gate_question_parity(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt03["gate_question"]),
        )

    def test_item05_evidence_ladder_parity(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt03["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt03["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt03["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_parity(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt03["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt03["forbidden_inference"]],
        )

    def test_item07_inference_guard_pinned_verbatim(self):
        g = self.item["07_allowed_and_forbidden_inference"]["inference_guard"]
        self.assertEqual(_norm(g["text"]), _norm(self.tgt03["inference_guard"]))
        self.assertIn("only when its source and context are explicitly a qualified treatment / metastasis context", _norm(g["rule"]))

    def test_item08_fatal_conditions_parity(self):
        self.assertEqual(
            [_norm(x) for x in self.item["08_fatal_conditions"]["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt03["fatal_conditions"]],
        )

    def test_item08_potential_fatal_signal_is_verbatim_pr_d_only(self):
        # the potential_fatal_signal list holds ONLY the frozen PR D text; the
        # extra framing / criteria live in sibling keys.
        sig = self.item["08_fatal_conditions"]["potential_fatal_signal"]
        self.assertEqual(len(sig), 1)
        self.assertEqual(_norm(sig[0]), _norm(self.tgt03["fatal_conditions"][0]))

    def test_item04_derived_parity_is_exact_not_a_superset(self):
        item04 = self.item["04_admissible_evidence_classes"]
        got = set(_norm(x) for x in item04["admissible"])
        want = set(_norm(x) for x in self.tgt03["evidence_required"])
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            want |= set(_norm(x) for x in self.tgt03["evidence_ladder"][grade]["admissible_evidence_classes"])
        self.assertEqual(got, want)

    def test_item04_excludes_the_other_seven_gates(self):
        na = _norm(" ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"]))
        for tok in ("tgt-01", "tgt-04", "tgt-05", "tgt-07", "tgt-08"):
            self.assertIn(tok, na)
        # TGT-02 baseline coverage is not admissible AS A PERSISTENCE CLAIM
        self.assertIn("as a persistence claim", na)

    def test_pr_d_unknown_behavior_is_treatment_naive_to_unknown(self):
        self.assertIn(
            "only treatment-naive primary crc data",
            _norm(self.tgt03["unknown_behavior"]),
        )
        # and the contract reproduces it
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        self.assertIn("only treatment-naive primary crc data -> unknown", _norm(i15["weak_only_treatment_naive_or_different_tumor"]))


class BidirectionalDirectionTests(unittest.TestCase):
    def setUp(self):
        self.i06 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["06_direction_interpretation"]

    def test_direction_is_relative_to_the_gate_question(self):
        self.assertIn("relative to the gate question", _norm(self.i06["strength_direction_rule"]))
        self.assertIn("bidirectional scientific persistence gate", _norm(self.i06["strength_direction_rule"]))

    def test_negative_is_reachable_and_a_scientific_finding(self):
        d = self.i06["direction_definitions"]
        self.assertIn("materially impaired persistence", _norm(d["NEGATIVE"]))
        self.assertIn("retention / persistence of target expression", _norm(d["POSITIVE"]))

    def test_strength_is_the_highest_qualifying_class_not_a_two_axis_rule(self):
        s = _norm(self.i06["strength_is_the_highest_qualifying_evidence_class"])
        self.assertIn("highest qualifying frozen evidence class", s)
        self.assertIn("no e6-style two-axis weaker-ceiling rule", s)
        self.assertIn("search-space completeness, not a four-axis score", s)

    def test_persistence_pattern_is_upstream_qualified_never_computed(self):
        p = _norm(self.i06["persistence_pattern_is_upstream_qualified"])
        self.assertIn("does not compute them from a fold-change", p)
        self.assertIn("source_reported", p)
        self.assertIn("human_reviewed_normalization", p)
        self.assertIn("hard integrity failure", p)

    def test_direction_is_an_aggregate_not_an_observation(self):
        a = _norm(self.i06["direction_is_an_aggregate_not_an_observation"])
        self.assertIn("a single observation is never a direction", a)
        self.assertIn("not yet a negative / direct proposal, and not fatal", a)
        self.assertIn("completed, audited persistence-search landscape", a)

    def test_weak_only_landscape_is_unknown_not_weak(self):
        w = _norm(self.i06["weak_vs_unknown"])
        self.assertIn("weak-only public landscape yields inconclusive / unknown, not inconclusive / weak", w)
        self.assertIn("zero evidence_refs", w)

    def test_no_super_direct_rung_and_resistance_model_is_indirect_strong(self):
        n2 = _norm(self.i06["qualifying_is_rung_specific"]["note_2"])
        self.assertIn("still just direct -- there is no super_direct rung", n2)
        self.assertIn("resistance-model persistence result is indirect_strong even if it measures protein", n2)

    def test_conflicting_is_not_auto_equated_with_variation(self):
        c = _norm(self.i06["conflicting_vs_qualified_variation"])
        self.assertIn("do not auto-equate context / site / time heterogeneity with a conflict", c)
        self.assertIn("graded inconclusive", c)
        self.assertIn("strength is not auto-degraded by a conflict", c)


class Correction1TransientMinorSupportsPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_transient_minor_downregulation_supports_persistence_not_fixed_contextual(self):
        m = self.item["06_direction_interpretation"]["persistence_pattern_to_support_mapping"]
        t = _norm(m["TRANSIENT_OR_MINOR_DOWNREGULATION"])
        self.assertIn("supports_persistence", t)
        self.assertIn("can contribute a positive direction", t)
        self.assertIn("never contribute a negative direction", t)
        self.assertIn("never contribute to a fatal_review", t)
        self.assertIn("never establish tgt-04", t)
        self.assertIn('"not sufficient for fatal" is not the same as "scientifically non-directional"', t)

    def test_retained_and_near_loss_mapping(self):
        m = self.item["06_direction_interpretation"]["persistence_pattern_to_support_mapping"]
        self.assertIn("supports_persistence", _norm(str(m["RETAINED"])))
        self.assertIn("opposes_persistence", _norm(str(m["NEAR_LOSS_OR_MARKED_LOSS"])))
        self.assertIn("nondirectional", _norm(str(m["MIXED_OR_UNRESOLVED"])))

    def test_item15_transient_minor_is_supporting_not_negative_not_fatal(self):
        t = _norm(self.item["15_failure_unknown_and_conflict_behavior"]["transient_minor_downregulation"])
        self.assertIn("supporting (retention)", t)
        self.assertIn("never yields negative", t)
        self.assertIn("never contributes to fatal_review", t)

    def test_item13_transient_minor_is_never_contradicting(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("transient_or_minor_downregulation observation is never scored contradicting and never contributes to the fatal_review", checks)

    def test_residual_target_presence_status_is_the_typed_branch_fact(self):
        # ROUND 1 Blocker 1: the SUPPORTING-vs-CONTEXTUAL split for a transient /
        # minor down-regulation is a typed upstream fact, not free-text parsing.
        i06 = self.item["06_direction_interpretation"]
        k = _norm(i06["residual_target_presence_status_is_the_transient_minor_branch_fact"])
        self.assertIn("residual_target_presence_status in {present, unresolved}", k)
        self.assertIn("auditable residual_target_presence_basis", k)
        self.assertIn("not decided by free-text parsing", k)
        self.assertIn("present means the qualified observation itself establishes that target expression remains present", k)
        self.assertIn("unresolved means the observation is itself ambiguous", k)
        self.assertIn("the provider emits only the fact -- never supports_persistence, never a direction", k)
        self.assertIn("exact-reuse identity parity", k)
        self.assertIn("no numeric threshold is introduced", k)

    def test_transient_minor_mapping_routes_on_the_typed_field(self):
        m = _norm(self.item["06_direction_interpretation"]["persistence_pattern_to_support_mapping"]["TRANSIENT_OR_MINOR_DOWNREGULATION"])
        self.assertIn("residual_target_presence_status == present", m)
        self.assertIn("residual_target_presence_status == unresolved", m)
        self.assertIn("decided only by this typed field, never by free-text semantic parsing", m)

    def test_item13_transient_minor_branch_is_deterministic_and_hard_on_drift(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("residual_target_presence_status in {present, unresolved}", checks)
        self.assertIn("residual_target_presence_status == present routes it to supporting (retention), == unresolved routes it to contextual", checks)
        self.assertIn("no free-text semantic parsing", checks)
        self.assertIn("part of the exact canonical ep reuse parity", checks)

    def test_upstream_qualification_now_names_the_residual_field(self):
        p = _norm(self.item["06_direction_interpretation"]["persistence_pattern_is_upstream_qualified"])
        self.assertIn("residual_target_presence_status in {present, unresolved}", p)
        self.assertIn("hard integrity failure", p)


class Correction2ReproducibleIsTwoRoutesTests(unittest.TestCase):
    def setUp(self):
        self.i08 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["08_fatal_conditions"]

    def test_reproducible_has_route_a_and_route_b(self):
        crit = self.i08["machine_detection_criteria"]
        self.assertIn("route_a_explicit_reproducibility_qualification", crit)
        self.assertIn("route_b_independent_convergence", crit)
        a = _norm(crit["route_a_explicit_reproducibility_qualification"])
        self.assertIn("reproducibility_status == qualified", a)
        self.assertIn("auditable reproducibility_basis", a)
        b = _norm(crit["route_b_independent_convergence"])
        self.assertIn("at least two independent qualified clinical persistence context identities", b)

    def test_reproducible_is_not_defined_by_a_numeric_context_count(self):
        crit = self.i08["machine_detection_criteria"]
        rr = _norm(crit["reproducibility_requires_route_a_or_route_b"])
        self.assertIn('"reproducible" is not defined by a numeric context count', rr)
        b = _norm(crit["route_b_independent_convergence"])
        self.assertIn("not the word-meaning definition of \"reproducible\"", b)
        self.assertIn("not a new biological threshold", b)
        self.assertIn('not "more than two" / "> 2"', b)

    def test_route_b_uses_at_least_two_not_more_than_two(self):
        b = self.i08["machine_detection_criteria"]["route_b_independent_convergence"]
        self.assertIn("at least two", b.lower())
        self.assertNotIn("more than two independent", b.lower().replace('not "more than two"', ""))

    def test_fatal_candidate_excludes_the_five_non_qualifying_kinds(self):
        excl = [_norm(x) for x in self.i08["explicitly_excluded_from_a_fatal_trigger"]]
        for tok in ("transient_or_minor_downregulation", "transcript-only evidence",
                    "resistance-model-only evidence", "a different tumor type",
                    "treatment-naive primary crc"):
            self.assertIn(tok, excl)

    def test_machine_emits_at_most_potential_fatal_pattern(self):
        r = _norm(self.i08["machine_output_is_only_a_potential_pattern"])
        self.assertIn("at most a machine-local fatal_review with status potential_fatal_pattern", r)
        self.assertIn("never emits public_fatal_signal_established", r)
        self.assertIn("kill", r)

    def test_no_numeric_or_downregulation_threshold_in_the_fatal_rule(self):
        r = _norm(self.i08["rule"])
        self.assertIn("no numeric threshold, no percent-positive cutoff, no h-score cutoff, no down-regulation score", r)


class Correction3DirectIsNotAClosedWhitelistTests(unittest.TestCase):
    def setUp(self):
        self.i05 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["05_evidence_ladder_and_evidence_ceiling"]

    def test_direct_protein_measurement_is_an_open_set(self):
        k = _norm(self.i05["direct_protein_measurement_is_not_a_closed_assay_whitelist"])
        self.assertIn("does not list a closed set of assays", k)
        self.assertIn("admissible examples", k)
        self.assertIn("not an exhaustive closed enum", k)
        self.assertIn("must not auto-downgrade another reliable protein-level method", k)

    def test_item13_direct_is_not_gated_on_a_three_assay_whitelist(self):
        checks = _flatten(
            yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["13_machine_acceptance_criteria"]
            ["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]
        )
        self.assertIn("direct is not gated on a closed three-assay whitelist", checks)
        self.assertIn("protein_measurement_validation_status", checks)

    def test_protein_measurement_validation_predicate_is_frozen(self):
        # ROUND 1 Blocker 3: the assay vocabulary stays open, but the
        # measurement-validation predicate that drives DIRECT is a closed enum.
        pred = self.i05["protein_measurement_validation_predicate"]
        self.assertEqual(pred["protein_measurement_validation_status_enum"], ["QUALIFIED", "NOT_ESTABLISHED"])
        rules = _norm(" ".join(pred["rules"]))
        self.assertIn("qualified requires a non-empty auditable protein_measurement_validation_basis", rules)
        self.assertIn("direct requires protein_measurement_validation_status == qualified", rules)
        self.assertIn("not_established can never reach direct", rules)
        self.assertIn("not a closed assay whitelist", rules)
        self.assertIn("assay vocabulary stays open", _norm(pred["note"]))
        self.assertIn("only protein_measurement_validation_status is a closed enum", _norm(pred["note"]))

    def test_item13_closes_the_validation_predicate_too(self):
        checks = _flatten(
            yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["13_machine_acceptance_criteria"]
            ["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"]
        )
        self.assertIn("protein_measurement_validation_status is in {qualified, not_established}", checks)
        self.assertIn("direct requires protein_measurement_validation_status == qualified", checks)
        self.assertIn("not_established can never reach direct", checks)
        self.assertIn("assay_method vocabulary stays open", checks)


class Correction4EpMayStateEmpiricalFactTests(unittest.TestCase):
    def setUp(self):
        self.i11 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["11_evidencepackage_output_contract"]

    def test_ep_may_state_the_source_persistence_or_loss_fact(self):
        may = _norm(" ".join(self.i11["neutral_wording"]["may_say"]))
        self.assertIn("retained target protein staining", may)
        self.assertIn("marked reduction of target protein", may)
        self.assertIn("a literal source persistence / loss claim is an admissible empirical fact", may)

    def test_only_gate_relative_conclusions_are_forbidden(self):
        may_not = _norm(" ".join(self.i11["neutral_wording"]["may_not_say"]))
        self.assertIn("passes tgt-03", may_not)
        self.assertIn("tgt-03 negative", may_not)
        self.assertIn("meaningful target availability is lost", may_not)
        self.assertIn("never upgrades it into a tgt-03 gate conclusion", may_not)


class FatalReviewAndProposalTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item12_non_canonical_envelope_omits_review_and_fatal_flag(self):
        i12 = self.item["12_assessment_proposal_envelope_contract"]
        self.assertIn("not a candidategateassessment", _norm(i12["the_module_emits"]))
        never = _norm(" ".join(i12["the_proposal_envelope_never_carries"]))
        self.assertIn("assessment_id", never)
        self.assertIn("review.status", never)
        self.assertIn("a fatal flag", never)

    def test_item12_fatal_review_has_reproducibility_basis_refs(self):
        fr = self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]
        fields = _norm(" ".join(fr["fields"]))
        self.assertIn("reproducibility_basis_refs", fields)
        self.assertIn("persistence_class", fields)
        self.assertIn("context_ids", fields)
        self.assertEqual(fr["machine_may_emit"], "POTENTIAL_FATAL_PATTERN")
        self.assertIn("public_fatal_signal_established", _norm(fr["machine_never_emits"]))

    def test_item12_fatal_review_required_iff_route_a_or_route_b(self):
        r = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["required_is_true_iff"])
        self.assertIn("route a", r)
        self.assertIn("route b", r)
        self.assertIn("at least two independent qualified clinical context identities", r)
        self.assertIn("a single loss observation with no route a qualification and no independent convergence gives required = false", r)

    def test_item12_fatal_review_only_actionable_on_an_accepted_run(self):
        r = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["only_actionable_on_an_accepted_run"])
        self.assertIn("actionable handoff only on an accepted run", r)


class CompletionAndSourcePlanTests(unittest.TestCase):
    def setUp(self):
        self.i09 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["09_evidence_source_plan"]

    def test_regime_is_public_hybrid_current_public_only_no_provider(self):
        self.assertEqual(self.i09["dominant_evidence_regime_frozen_contract"], "PUBLIC_HYBRID")
        self.assertEqual(self.i09["current_instantiation_regime"], "PUBLIC_ONLY")
        self.assertFalse(self.i09["connect_provider_in_this_pr"])

    def test_four_mandatory_search_components_are_search_space_completeness(self):
        pl = self.i09["persistence_search_landscape"]
        comps = [_norm(x) for x in pl["declared_mandatory_search_components"]]
        self.assertEqual(len(comps), 4)
        self.assertTrue(any("refractory / prior-treated" in c for c in comps))
        self.assertTrue(any("metastatic crc lesion" in c and "liver / crlm / lung / peritoneal" in c for c in comps))
        self.assertTrue(any("paired pre-/post-treatment" in c for c in comps))
        self.assertTrue(any("resistance model" in c for c in comps))
        m = _norm(pl["mandatory_is_search_space_completeness_not_evidence_prerequisites"])
        self.assertIn("does not mean every component must yield evidence", m)
        self.assertIn("does not mean every component must be direct", m)
        self.assertIn("not a four-axis score", m)
        self.assertIn("searched / exhausted with zero qualifying records still counts as complete", m)
        self.assertIn("public_persistence_search_complete", m)

    def test_typed_completion_is_named_and_not_a_core_object(self):
        tc = _norm(self.i09["persistence_search_landscape"]["typed_completion_record"])
        self.assertIn("clinicalpersistencecompletion", tc)
        self.assertIn("not a seventh core object", tc)
        self.assertIn("no e6-style two mandatory axes", tc)
        self.assertIn("snapshot parity", tc)
        self.assertIn("dedup-lost snapshot -> hard reject", tc)

    def test_source_authority_hard_locks(self):
        rules = _norm(" ".join(self.i09["source_authority_rules"]))
        self.assertIn("neither becomes a direct call", rules)
        self.assertIn("treatment-naive primary crc expression can never become a persistence claim", rules)
        self.assertIn("different tumor type is weak context only", rules)
        self.assertIn("baseline malignant-cell coverage (tgt-02) never substitutes for demonstrated persistence", rules)
        self.assertIn("a persistence result never establishes tgt-04 surface / density", rules)
        self.assertIn("generic evgap-02 / crc-linkage observation contributes only if its source and context explicitly qualify", rules)

    def test_no_universal_threshold(self):
        n = _norm(self.i09["no_universal_threshold"])
        self.assertIn("no fold-change cutoff", n)
        self.assertIn("no down-regulation score", n)
        self.assertIn("no context-count threshold", n)


class RuntimeGeneInheritanceTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item10_fixed_instantiation_context_is_hard_pinned(self):
        i10 = _flatten(self.item["10_input_contract"])
        self.assertIn("ctx-crc-refractory-mcrc", i10)
        self.assertIn("context_version", i10 and i10)  # present
        self.assertIn("hard-pinned to the fixed instantiation", i10)
        self.assertIn("every observation.context_key equals the run's context_key", i10)
        self.assertIn("clinicalpersistencecompletion.search_scope equals the run's declared persistence_search_scope", i10)

    def test_item11_exact_reuse_and_dedup_safe_audit_ep(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("observation_id is part of the exact-reuse identity parity", i11)
        self.assertIn("reused ep's own provenance source_type / source_identifier / locator must still equal the resolved canonical sourceindex", i11)
        self.assertIn("must survive the shared (source_id, claim) dedup", i11)
        self.assertIn("kind / fact-specific study_context", i11)

    def test_local_persistence_context_namespace_is_separate_from_canonical(self):
        # ROUND 1 Blocker 2: the per-observation / completion / fatal_review
        # evidence-context identity is a LOCAL namespace, never the canonical
        # Instantiation context_id.
        i09 = _flatten(self.item["09_evidence_source_plan"])
        self.assertIn("qualifying_direct_persistence_context_ids", i09)
        self.assertIn("qualifying_indirect_persistence_context_ids", i09)
        ns = _norm(self.item["09_evidence_source_plan"]["persistence_search_landscape"]["persistence_context_id_namespace"])
        self.assertIn("local evidence-context identities", ns)
        self.assertIn("separate namespace from the canonical instantiation context_id (ctx-crc-refractory-mcrc", ns)
        self.assertIn("must never be collapsed onto it", ns)

        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("persistence_context_id / persistence_context_ids", i11)
        self.assertIn("deliberately not the canonical instantiation context_id (ctx-crc-refractory-mcrc)", i11)
        self.assertIn("never collapse a persistence_context_id onto the canonical context_id", i11)

        fr_fields = _norm(" ".join(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["fields"]))
        self.assertIn("persistence_context_ids", fr_fields)

        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("collapses a persistence_context_id onto the canonical context_id is a hard identity-namespace failure", checks)

    def test_audit_snapshot_uses_the_new_persistence_context_id_namespace(self):
        # ROUND 2 blocker: the item-11 SEARCH_COMPLETION_AUDIT structured snapshot
        # must name the SAME fields as the typed completion, so E10's
        # completion <-> SEARCH_COMPLETION_AUDIT exact snapshot parity has no
        # contradictory machine contract.
        pkg_rules = _norm(" ".join(self.item["11_evidencepackage_output_contract"]["each_package"]))
        self.assertIn("qualifying_direct_persistence_context_ids", pkg_rules)
        self.assertIn("qualifying_indirect_persistence_context_ids", pkg_rules)
        self.assertNotIn("qualifying_direct_context_ids,", pkg_rules)
        self.assertNotIn("qualifying_indirect_context_ids)", pkg_rules)
        # and nowhere in the whole contract does the old identifier survive
        raw = CONTRACT.read_text()
        self.assertNotIn("qualifying_direct_context_ids", raw)
        self.assertNotIn("qualifying_indirect_context_ids", raw)

    def test_canonical_context_id_pin_is_untouched(self):
        # the canonical Instantiation context_id must still be pinned in items 10 and 12.
        i10 = _flatten(self.item["10_input_contract"])
        self.assertIn("ctx-crc-refractory-mcrc", i10)
        pins = _norm(" ".join(self.item["12_assessment_proposal_envelope_contract"]["the_proposal_envelope_carries"]["identity_pins_for_deterministic_canonicalisation"]))
        self.assertIn("context_id (ctx-crc-refractory-mcrc)", pins)

    def test_item13_whole_run_reject_never_degraded_to_unknown(self):
        on_fail = _norm(self.item["13_machine_acceptance_criteria"]["on_failure"])
        self.assertIn("rejects the whole run -- it is never degraded to an accepted unknown", on_fail)
        self.assertIn("unknown from a genuinely incomplete public persistence search is not an integrity failure", on_fail)

    def test_item13_forbids_cross_gate_and_decision_wording(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("no tgt-02 baseline-coverage substitution, no tgt-04 surface / density conclusion", checks)
        self.assertIn("no public_fatal_signal_established / kill / hold / decision", checks)

    def test_item15_experiment_required_is_narrow(self):
        e = _norm(self.item["15_failure_unknown_and_conflict_behavior"]["experiment_required"])
        self.assertIn("only when the enumerated public persistence source space is completed / exhausted", e)
        self.assertIn("while any unresolved public item remains the resolution stays public_resolvable / currently_unresolvable -- do not auto-add experiment_required", e)
        self.assertIn("a paired pre-/post-treatment biopsy is one possible experimental form, not the only requirement", e)

    def test_item16_stop_rule_never_stops_on_first_loss(self):
        i16 = self.item["16_stop_rule"]
        self.assertIn("the module never stops on the first loss observation", _norm(" ".join(i16["potential_fatal_trigger"])))
        self.assertIn("only after the necessary persistence-search completeness is satisfied", _norm(" ".join(i16["potential_fatal_trigger"])))

    def test_item17_handoff_never_kills_and_tgt03_never_discharges_tgt04(self):
        i17 = self.item["17_downstream_consumer_and_handoff"]
        never = _flatten(i17["this_module_does_not"])
        self.assertIn("produce a candidate-level decision or kill", never)
        self.assertIn("let generic evgap-02 / crc linkage discharge tgt-03", never)
        cons = _flatten(i17["once_human_approved_the_resulting_canonical_CandidateGateAssessment_is_consumed_by"])
        self.assertIn("tgt-03 never discharges tgt-04", cons)


class ContractIsFrozenAndImplementedInPrE10Tests(unittest.TestCase):
    """The E9 construction contract is design-only and stays frozen. The
    implementation package it deferred is now built by PR E10, so the repository
    state -- the package exists and the TGT-03 binding is 1.0.0 -- reconciles
    with what the contract said would happen."""

    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation_and_registry_changes(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["trial_or_dataset_retrieval_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_or_ranking_scoring"], "forbidden")
        self.assertEqual(p["fold_change_or_percent_positive_or_hscore_or_downregulation_or_context_count_threshold"], "forbidden")
        self.assertEqual(p["generic_gatemodule_framework_or_base_class_in_this_pr"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt01"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt02"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt05"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt08"], "forbidden")
        self.assertEqual(p["modifies_binding_or_registry_or_existing_tests"], "forbidden")
        self.assertEqual(p["only_allowed_existing_file_mutation"], "append_to_logs_worklog_md")
        self.assertEqual(p["migration_pending"], "remains")

    def test_tgt03_implementation_package_now_exists_post_e10(self):
        pkg = ROOT / "gate_modules" / "tgt03_treatment_metastatic_persistence"
        self.assertTrue(pkg.is_dir(), "PR E10 builds the deferred implementation package")
        for f in ("__init__.py", "module.yaml", "contracts.py", "ports.py",
                  "classify.py", "evidence.py", "aggregate.py", "completion.py",
                  "fatal_review.py", "acceptance.py", "module.py"):
            self.assertTrue((pkg / f).is_file(), f)

    def test_tgt03_binding_is_now_one_zero_zero_and_the_others_untouched(self):
        gs = yaml.safe_load(CRC_GATESET.read_text())
        by_gate = {
            b["gate_id"]: b["primary_module_version"]
            for b in gs["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(by_gate["TGT-03"], "1.0.0")
        self.assertEqual(by_gate["TGT-01"], "1.0.0")
        self.assertEqual(by_gate["TGT-02"], "1.0.0")
        self.assertEqual(by_gate["TGT-05"], "1.0.0")
        self.assertEqual(by_gate["TGT-08"], "1.0.0")
        # PR E12 built MOD-TGT04; PR E14 built MOD-TGT06; TGT-07 stays unbuilt.
        self.assertEqual(by_gate["TGT-04"], "1.0.0")
        self.assertEqual(by_gate["TGT-06"], "1.0.0")
        for g in ("TGT-07",):
            self.assertEqual(by_gate[g], "0.0.0")

    def test_deferred_block_names_the_e10_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e10_plus"]).lower()
        self.assertIn("gate_modules/tgt03_treatment_metastatic_persistence/", joined)
        self.assertIn("clinicalpersistencecompletion", joined)
        self.assertIn("1.0.0", joined)
        self.assertIn("binding / registry reconciliation", joined)

    def test_only_the_built_per_gate_packages_exist_under_gate_modules(self):
        gm = ROOT / "gate_modules"
        py_files = sorted(str(p.relative_to(ROOT)) for p in gm.rglob("*.py"))
        allowed = (
            "tgt01_adc_modality_precedent",
            "tgt02_indication_specific_malignant_cell_coverage",
            "tgt03_treatment_metastatic_persistence",
            "tgt04_tumor_surface_availability_density_plausibility",
            "tgt05_normal_tissue_fatal_liability",
            "tgt06_internalization_trafficking_addressability",
            "tgt08_target_opportunity_competition_ip_whitespace",
        )
        self.assertTrue(all(any(pkg in p for pkg in allowed) for p in py_files), py_files)

    def test_no_numeric_or_threshold_language_in_the_contract(self):
        text = CONTRACT.read_text().lower()
        # a real threshold has a comparator and a number; none is present.
        self.assertIsNone(
            re.search(
                r"\d\s*%|h-?score\s*[<>=]\s*\d|fold[- ]change\s*[<>=]\s*\d"
                r"|[<>=]\s*\d+\s*(percent|cells|fold|contexts|cohorts)"
                r"|\bnumeric_score\s*=",
                text,
            )
        )
        self.assertIn("no fold-change cutoff", text)
        self.assertIn("no context-count threshold", text)
        self.assertIn('not "more than two" / "> 2"', text)


class DrawingTests(unittest.TestCase):
    def setUp(self):
        self.text = DRAWING.read_text()

    def test_drawing_exists_and_names_the_module_and_pr(self):
        self.assertIn("MOD-TGT03", self.text)
        self.assertIn("PR E9", self.text)
        self.assertIn("Treatment / Metastatic Persistence", self.text)

    def test_drawing_covers_all_seventeen_items(self):
        # the 17-row table -- each row starts "| N | **...".
        for n in range(1, 18):
            self.assertRegex(self.text, rf"\|\s*{n}\s*\|\s*\*\*", f"drawing row {n} missing")

    def test_drawing_has_the_three_headline_blockquotes(self):
        self.assertIn("Baseline expression is not persistence", self.text)
        self.assertIn("bidirectional scientific persistence gate", self.text)
        self.assertIn("Reproducible protein-level near / marked loss may trigger only", self.text)

    def test_drawing_freezes_the_four_corrections(self):
        t = self.text
        self.assertIn("TRANSIENT_OR_MINOR_DOWNREGULATION` → `SUPPORTS_PERSISTENCE`", t)
        self.assertIn("Route A", t)
        self.assertIn("Route B", t)
        self.assertIn("DIRECT protein measurement is NOT a closed three-assay whitelist", t)
        self.assertIn("a literal source persistence / loss claim is an admissible fact", t)

    def test_drawing_states_no_binding_or_registry_or_test_change(self):
        norm = " ".join(self.text.split()).lower()
        self.assertIn("append to `logs/worklog.md`", norm)
        self.assertIn("does not touch it, the binding, the registry or any existing test", norm)


if __name__ == "__main__":
    unittest.main()
