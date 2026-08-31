"""Runtime Migration PR E11: the MOD-TGT04 construction contract.

Asserts:
* the 17-item acceptance checklist is present, complete and ordered (template
  reused from the approved PR E1 template);
* items 03 / 05 / 07 / 08 are a normalized-equality parity with the FROZEN PR D
  TGT-04 contract (crc_adc_target_gateset.yaml), item 04 is an EXACT derived
  parity (set equality, not a superset) against evidence_required + the ladder,
  and the EVGAP-01 inference_guard is pinned verbatim;
* TGT-04 is frozen as a TWO-TIER evidence architecture (localization vs
  quantitative density) with a SINGLE-TIER grading authority: only a qualifying
  DIRECT quantitative antigen-density observation grants a graded Direction /
  DIRECT; a localization-only completed landscape is INCONCLUSIVE / UNKNOWN, and
  the only legal Direction x Strength pairs are POSITIVE/DIRECT, NEGATIVE/DIRECT,
  CONFLICTING/DIRECT, INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN;
* the four ChatGPT AI审核方案 scoping corrections are frozen: (1) localization-only
  -> INCONCLUSIVE / UNKNOWN, never INCONCLUSIVE / INDIRECT_STRONG; (2) the
  measurement-validity status and the density-direction interpretation are
  SEPARATE typed fields (measurement_validation_status vs density_plausibility_status
  vs surface_antigen_level); (3) raw quantitative density values / units are
  admissible factual evidence but any numeric decision cutoff / invented range is
  forbidden; (4) fatal Route A / Route B with the local identity named
  surface_context_id(s) and Route B "at least two" (never "> 2");
* the 3 headline conclusions are frozen verbatim; a reproducible quantitative
  NEGLIGIBLE_OR_UNDETECTABLE surface antigen is surfaced at most as a
  machine-local fatal_review = POTENTIAL_FATAL_PATTERN, and LOW_BUT_PRESENT is
  never fatal and never automatically NEGATIVE;
* RNA / prediction / non-CRC surface evidence never above WEAK, localization
  never above INDIRECT_STRONG and never grants density grading authority, and
  surface localization never discharges the quantitative antigen-density
  requirement;
* items 10-17 inherit the E2 / E4 / E6 / E8 / E10 runtime genes including the
  five E10-review corrections (explicitly qualified surface context for a rung;
  the local surface_context_id namespace separate from the canonical context_id;
  every qualified factual state carries an auditable basis; a CLOSED
  measurement_validation_status enum + a non-empty factual assay_method for
  DIRECT; a kind / fact-specific non-inflated study_context);
* PR E11 ships no implementation -- no gate_modules/tgt04.../ directory, no
  provider / adapter / retrieval / runner, no numeric / ranking score, no
  antigen-density cutoff or invented range, no generic GateModule framework;
  MOD-TGT04 primary_module_version stays "0.0.0"; the binding, the registry and
  every existing test are untouched (the only allowed existing-file mutation is
  an append to logs/worklog.md); MIGRATION_PENDING remains;
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt04_tumor_surface_availability_density_plausibility.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-04_Tumor_Surface_Availability_Density_Plausibility.md"
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
        self.assertEqual(m["pr"], "runtime_migration_pr_e11")
        self.assertEqual(
            m["scope"],
            "tgt04_mod_tgt04_construction_contract_drawing_validation_and_acceptance_checklist_only",
        )
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e12", m["next"])
        self.assertIn("TGT-03 -> TGT-04 -> TGT-06", m["order"])

    def test_template_provenance_reuses_the_e1_template(self):
        tp = self.doc["template_provenance"]
        self.assertEqual(tp["status"], "RECONSTRUCTED")
        self.assertTrue(tp["claim"]["not_claimed_verbatim_from_blueprint"])
        self.assertTrue(tp["claim"]["seventeen_item_template_reused_from_e1"])
        self.assertIn("e1 17-item construction template", tp["template_basis"].lower())
        self.assertTrue(E1_CONTRACT.is_file())

    def test_kernel_invariant_two_tier_but_not_a_kill(self):
        inv = _norm(self.doc["kernel_invariant"])
        self.assertIn("src/ must never import gate_modules/", inv)
        self.assertIn("the gate_question is the density-plausibility question", inv)
        self.assertIn("it never propagates to a gate-level proposed strength", inv)
        self.assertIn("a localization-only completed landscape is inconclusive / unknown", inv)
        self.assertIn("there is no reliable cross-target universal adc-effective density range", inv)
        self.assertIn("it is not a fatal flag and not a kill", inv)
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
        self.assertIn("surface localization is not antigen density", joined)
        self.assertIn("quantitative values are evidence, not thresholds", joined)
        self.assertIn("it never derives a universal adc-effective density cutoff", joined)
        self.assertIn("reproducible quantitative negligible_or_undetectable surface antigen may surface only potential_fatal_pattern", joined)
        self.assertIn("low-but-present antigen is not automatically negative or fatal", joined)
        self.assertIn("the module never decides fatality or adc efficacy", joined)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item01_gate_identity(self):
        i = self.item["01_gate_identity_and_version"]
        self.assertEqual(i["gate_id"], "TGT-04")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["gate_name"], "Tumor Surface Availability / Density Plausibility")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["gateset_version"], "1.0")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT04")
        self.assertEqual(i["module_implementation_version"], "0.0.0")
        self.assertIn("pr e12 builds it", _norm(i["rule"]))


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt04 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-04"]

    def test_item03_gate_question_parity(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt04["gate_question"]),
        )

    def test_item05_evidence_ladder_parity(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt04["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt04["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt04["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_parity(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt04["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt04["forbidden_inference"]],
        )

    def test_item07_inference_guard_pinned_verbatim(self):
        g = self.item["07_allowed_and_forbidden_inference"]["inference_guard"]
        self.assertEqual(_norm(g["text"]), _norm(self.tgt04["inference_guard"]))
        self.assertIn("never discharges the quantitative antigen-density requirement", _norm(g["rule"]))

    def test_item08_fatal_conditions_parity(self):
        self.assertEqual(
            [_norm(x) for x in self.item["08_fatal_conditions"]["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt04["fatal_conditions"]],
        )

    def test_item08_potential_fatal_signal_is_verbatim_pr_d_only(self):
        sig = self.item["08_fatal_conditions"]["potential_fatal_signal"]
        self.assertEqual(len(sig), 1)
        self.assertEqual(_norm(sig[0]), _norm(self.tgt04["fatal_conditions"][0]))

    def test_item04_derived_parity_is_exact_not_a_superset(self):
        item04 = self.item["04_admissible_evidence_classes"]
        got = set(_norm(x) for x in item04["admissible"])
        want = set(_norm(x) for x in self.tgt04["evidence_required"])
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            want |= set(_norm(x) for x in self.tgt04["evidence_ladder"][grade]["admissible_evidence_classes"])
        self.assertEqual(got, want)

    def test_item04_excludes_the_other_seven_gates_and_a_universal_range(self):
        na = _norm(" ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"]))
        for tok in ("tgt-01", "tgt-02", "tgt-03", "tgt-05", "tgt-06", "tgt-07", "tgt-08"):
            self.assertIn(tok, na)
        self.assertIn("clinically effective antigen-density range", na)

    def test_pr_d_unknown_behavior_is_localization_only_to_unknown(self):
        self.assertIn(
            "only localization or rna evidence available",
            _norm(self.tgt04["unknown_behavior"]),
        )
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        self.assertIn(
            "strength stays unknown on the density question; it is not upgraded",
            _norm(i15["localization_only_completed_landscape"]),
        )


class TwoTierGradingAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.i06 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["06_direction_interpretation"]

    def test_two_tier_architecture_single_tier_grading(self):
        t = _norm(self.i06["two_tier_architecture_single_tier_grading"])
        self.assertIn("only a qualifying direct quantitative antigen-density observation", t)
        self.assertIn("a localization-only completed landscape, however strong, stays inconclusive / unknown", t)
        self.assertIn('e12 must not copy the e10-style "highest qualifying rung == overall strength" rule', t)

    def test_tgt04_specific_strength_rule(self):
        r = self.i06["tgt04_specific_strength_rule"]
        self.assertIn("overall strength = direct", _norm(r["if_qualifying_direct_density_evidence_exists"]))
        self.assertIn("inconclusive / unknown", _norm(r["else"]))
        self.assertIn("zero evidence_refs", _norm(r["else"]))

    def test_legal_direction_strength_pairs_are_exactly_five(self):
        pairs = [_norm(p) for p in self.i06["legal_direction_strength_pairs"]]
        self.assertEqual(
            set(pairs),
            {
                "positive / direct",
                "negative / direct",
                "conflicting / direct",
                "inconclusive / direct",
                "inconclusive / unknown",
            },
        )
        no = _norm(self.i06["no_other_pairs"])
        self.assertIn("no positive / indirect_strong", no)
        self.assertIn("no inconclusive / indirect_strong", no)
        self.assertIn("no inconclusive / weak", no)
        self.assertIn("a localization-only landscape maps straight to inconclusive / unknown", no)

    def test_inconclusive_direct_is_legal_and_distinct_from_unknown(self):
        d = _norm(self.i06["inconclusive_direct_is_legal"])
        self.assertIn("qualifying direct quantitative density measurements", d)
        self.assertIn("density_plausibility_status mixed_or_unresolved / not_established", d)
        self.assertIn("distinct from inconclusive / unknown", d)

    def test_separate_typed_upstream_facts(self):
        s = _norm(self.i06["upstream_qualified_factual_states"])
        self.assertIn("must not overload one field to carry two meanings", s)
        self.assertIn("measurement_validation_status", s)
        self.assertIn("qualified is not a positive density conclusion", s)
        self.assertIn("density_plausibility_status", s)
        self.assertIn("never computed by the module from a number", s)
        self.assertIn("surface_antigen_level", s)
        self.assertIn("frozen separately for the fatal path", s)

    def test_density_direction_mapping(self):
        m = self.i06["density_direction_mapping"]
        self.assertEqual(_norm(m["surface_antigen_level_negligible_or_undetectable"]), "opposes_density_plausibility")
        self.assertEqual(_norm(m["else_density_plausibility_status_plausibly_adequate"]), "supports_density_plausibility")
        self.assertEqual(_norm(m["density_plausibility_status_not_plausibly_adequate"]), "opposes_density_plausibility")
        self.assertIn("nondirectional", _norm(m["density_plausibility_status_mixed_or_unresolved_or_not_established"]))
        low = _norm(m["low_but_present_alone"])
        self.assertIn("not automatically negative, not a fatal input", low)
        self.assertIn("never enters a fatal_review contribution", low)

    def test_localization_never_contributes_a_gate_direction(self):
        li = self.i06["localization_implication"]
        self.assertIn("never contributes a gate-level direction or strength", _norm(li["surface_localized_with_qualifying_ihc_or_surfaceomics"]))
        self.assertIn("does not produce a negative gate direction", _norm(li["not_surface_localized_alone"]))


class QuantitativeValuesAreEvidenceNotThresholdsTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_raw_density_values_admissible_but_no_cutoff(self):
        k = _norm(self.item["05_evidence_ladder_and_evidence_ceiling"]["quantitative_values_are_evidence_not_thresholds"])
        self.assertIn("may and should preserve a measured antigen-density value and its unit", k)
        self.assertIn("what is forbidden is the module deriving a direction or a fatal signal by comparing that value to any threshold", k)
        self.assertIn('invented "clinically effective range"', k)
        self.assertIn("never as a number-vs-cutoff computation", k)

    def test_direct_is_not_a_closed_assay_whitelist(self):
        k = _norm(self.item["05_evidence_ladder_and_evidence_ceiling"]["direct_is_not_a_closed_assay_whitelist"])
        self.assertIn("not a closed enum", k)
        self.assertIn("is not auto-downgraded", k)
        self.assertIn("a non-empty factual assay_method to drive direct", k)

    def test_item09_no_universal_threshold(self):
        n = _norm(self.item["09_evidence_source_plan"]["no_universal_threshold"])
        self.assertIn("no antigen-density cutoff", n)
        self.assertIn("no molecules-per-cell threshold", n)
        self.assertIn('no invented "clinically effective antigen-density range"', n)
        self.assertIn("raw quantitative antigen-density values and units may be preserved as factual measurement", n)

    def test_item11_ep_may_carry_a_raw_number(self):
        each = _flatten(self.item["11_evidencepackage_output_contract"]["each_package"])
        self.assertIn("reported_density_value", each)
        self.assertIn("a factual measurement the module never compares to a threshold", each)
        may = _norm(" ".join(self.item["11_evidencepackage_output_contract"]["neutral_wording"]["may_say"]))
        self.assertIn("~12000 target molecules per cell", may)
        may_not = _norm(" ".join(self.item["11_evidencepackage_output_contract"]["neutral_wording"]["may_not_say"]))
        self.assertIn("above / below a clinically effective range", may_not)

    def test_no_numeric_or_threshold_language_in_the_contract(self):
        text = _norm(CONTRACT.read_text())
        self.assertIsNone(
            re.search(
                r"\d\s*%|h-?score\s*[<>=]\s*\d|density\s*[<>=]\s*\d"
                r"|[<>=]\s*\d+\s*(percent|cells|molecules|contexts|cohorts)"
                r"|\bnumeric_score\s*=",
                text,
            )
        )
        self.assertIn("no antigen-density cutoff", text)
        self.assertIn('not "more than two" / "> 2"', text)


class FatalReviewAndProposalTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item08_route_a_and_route_b(self):
        crit = self.item["08_fatal_conditions"]["machine_detection_criteria"]
        self.assertIn("route_a_explicit_reproducibility_qualification", crit)
        self.assertIn("route_b_independent_convergence", crit)
        a = _norm(crit["route_a_explicit_reproducibility_qualification"])
        self.assertIn("reproducibility_status == qualified", a)
        self.assertIn("auditable reproducibility_basis", a)
        b = _norm(crit["route_b_independent_convergence"])
        self.assertIn("at least two independent qualified crc malignant-cell surface-context identities", b)
        self.assertIn("a well-matched crc model identity does not count toward the convergence", b)
        self.assertIn('not "more than two" / "> 2"', b)

    def test_item08_fatal_contributor_is_negligible_not_low_but_present(self):
        crit = _flatten(self.item["08_fatal_conditions"]["machine_detection_criteria"]["each_contributing_observation_must_be"])
        self.assertIn("surface_antigen_level == negligible_or_undetectable", crit)
        self.assertIn("not low_but_present", crit)
        excl = _flatten(self.item["08_fatal_conditions"]["explicitly_excluded_from_a_fatal_trigger"])
        self.assertIn("low_but_present surface antigen", excl)
        self.assertIn("any threshold comparison against a putative universal antigen-density range", excl)

    def test_item08_machine_emits_at_most_potential_fatal_pattern(self):
        r = _norm(self.item["08_fatal_conditions"]["machine_output_is_only_a_potential_pattern"])
        self.assertIn("at most a machine-local fatal_review with status potential_fatal_pattern", r)
        self.assertIn("never emits public_fatal_signal_established", r)
        self.assertIn("kill", r)

    def test_item12_non_canonical_envelope_omits_review_and_fatal_flag(self):
        i12 = self.item["12_assessment_proposal_envelope_contract"]
        self.assertIn("not a candidategateassessment", _norm(i12["the_module_emits"]))
        never = _norm(" ".join(i12["the_proposal_envelope_never_carries"]))
        self.assertIn("assessment_id", never)
        self.assertIn("review.status", never)
        self.assertIn("a fatal flag", never)
        self.assertIn("any antigen-density threshold, cutoff or \"clinically effective range\"", never)

    def test_item12_fatal_review_fields(self):
        fr = self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]
        fields = _norm(" ".join(fr["fields"]))
        self.assertIn("surface_context_ids", fields)
        self.assertIn("antigen_level_class", fields)
        self.assertIn("measurement_validation_basis_refs", fields)
        self.assertIn("reproducibility_basis_refs", fields)
        self.assertEqual(fr["machine_may_emit"], "POTENTIAL_FATAL_PATTERN")
        self.assertIn("public_fatal_signal_established", _norm(fr["machine_never_emits"]))
        r = _norm(fr["required_is_true_iff"])
        self.assertIn("route a", r)
        self.assertIn("route b", r)
        self.assertIn("each on crc malignant cells only", r)
        self.assertIn("a low_but_present observation, and a well-matched crc model observation, never contribute", r)

    def test_item12_fatal_review_only_actionable_on_an_accepted_run(self):
        r = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["only_actionable_on_an_accepted_run"])
        self.assertIn("actionable handoff only on an accepted run", r)

    def test_item12_identity_pins_carry_the_canonical_context_id(self):
        pins = _norm(" ".join(self.item["12_assessment_proposal_envelope_contract"]["the_proposal_envelope_carries"]["identity_pins_for_deterministic_canonicalisation"]))
        self.assertIn("context_id (ctx-crc-refractory-mcrc)", pins)


class CompletionAndSourcePlanTests(unittest.TestCase):
    def setUp(self):
        self.i09 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["09_evidence_source_plan"]

    def test_regime_is_public_hybrid_current_public_only_no_provider(self):
        self.assertEqual(self.i09["dominant_evidence_regime_frozen_contract"], "PUBLIC_HYBRID")
        self.assertEqual(self.i09["current_instantiation_regime"], "PUBLIC_ONLY")
        self.assertFalse(self.i09["connect_provider_in_this_pr"])

    def test_four_mandatory_search_completion_axes(self):
        pl = self.i09["surface_search_landscape"]
        comps = [_norm(x) for x in pl["declared_mandatory_search_components"]]
        self.assertEqual(len(comps), 4)
        self.assertTrue(any("quantitative cell-surface antigen density search" in c for c in comps))
        self.assertTrue(any("validated membranous ihc search" in c for c in comps))
        self.assertTrue(any("cell-surface proteomics" in c for c in comps))
        self.assertTrue(any("subcellular localization search" in c for c in comps))
        m = _norm(pl["mandatory_is_search_completion_axes_not_evidence_prerequisites"])
        self.assertIn("not evidence prerequisites and not grading axes", m)
        self.assertIn("searched / exhausted with zero qualifying records still counts as complete", m)
        self.assertIn("public_surface_search_complete", m)

    def test_typed_completion_is_named_and_not_a_core_object(self):
        tc = _norm(self.i09["surface_search_landscape"]["typed_completion_record"])
        self.assertIn("surfaceavailabilitycompletion", tc)
        self.assertIn("not a seventh core object", tc)
        self.assertIn("qualifying_direct_surface_context_ids / qualifying_indirect_surface_context_ids", tc)
        self.assertIn("only direct quantitative density observations grant density-question grading authority", tc)
        self.assertIn("adding qualifying_indirect_surface_context_ids does not make indirect_strong propagate to a gate-level strength", tc)
        self.assertIn("the snapshot field names are the typed completion field names", tc)
        self.assertIn("dedup-lost snapshot, or a drift in either qualifying surface-context set, -> hard reject", tc)

    def test_source_authority_hard_locks(self):
        rules = _norm(" ".join(self.i09["source_authority_rules"]))
        self.assertIn("rna / bulk expression never establishes surface protein or surface density", rules)
        self.assertIn("surface localization (membranous ihc / cell-surface proteomics) never discharges the quantitative antigen-density requirement", rules)
        self.assertIn("topology / signal-peptide / go-term surface prediction is weak only", rules)
        self.assertIn("surface evidence from non-crc cell lines only is weak only", rules)
        self.assertIn("never from crc_specific alone", rules)
        self.assertIn("the evgap-01 surface-localization lock contributes surface-localization evidence only, never antigen density", rules)


class RuntimeGeneInheritanceTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item10_fixed_instantiation_context_is_hard_pinned(self):
        i10 = _flatten(self.item["10_input_contract"])
        self.assertIn("ctx-crc-refractory-mcrc", i10)
        self.assertIn("a separate namespace from each observation's local surface_context_id", i10)
        self.assertIn("every observation.context_key equals the run's context_key", i10)
        self.assertIn("surfaceavailabilitycompletion.search_scope equals the run's declared surface_search_scope", i10)

    def test_item11_exact_reuse_dedup_and_namespace(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("observation_id is part of the exact-reuse identity parity", i11)
        self.assertIn("reused ep's own provenance source_type / source_identifier / locator must still equal the resolved canonical sourceindex", i11)
        self.assertIn("dedup uses the improved tgt-03 rule", i11)
        self.assertIn("both observations survive", i11)
        self.assertIn("a search_completion_audit ep is never a dedup loser", i11)
        self.assertIn("surface_context_id / surface_context_ids is a local evidence-context identity namespace", i11)
        self.assertIn("never collapse a surface_context_id onto the canonical context_id", i11)
        self.assertIn("kind / fact-specific study_context", i11)

    def test_item13_five_e10_review_genes(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        # (a) explicitly qualified surface context for a rung
        self.assertIn("a direct rung requires an explicitly qualified surface context", checks)
        self.assertIn("an indirect_strong localization rung is narrower", checks)
        self.assertIn("it requires surface_context_class == crc_malignant_cells", checks)
        self.assertIn("a bare crc_specific == true never reaches a rung", checks)
        # (b) local surface-context namespace + a qualifying observation carries one
        self.assertIn("the local surface-context namespace", checks)
        self.assertIn("collapses a surface_context_id onto the canonical context_id is a hard identity-namespace failure", checks)
        self.assertIn("any observation classified qualifying direct or qualifying indirect_strong carries at least one auditable local surface_context_id", checks)
        # (c) every qualified status carries an auditable basis
        self.assertIn("every classification-driving qualified status carries an auditable basis", checks)
        # (d) closed validation enum + non-empty assay_method for DIRECT
        self.assertIn("measurement_validation_status is in {qualified, not_established}", checks)
        self.assertIn("a non-empty factual assay_method", checks)
        # (e) kind / fact-specific non-inflated study_context is item 11
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("never promote a non-crc / prediction / rna-proxy / audit observation's source study context", i11)

    def test_item13_strength_is_direct_iff_a_qualifying_direct_exists(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("the gate-level proposed_strength is direct iff a qualifying direct quantitative antigen-density observation exists", checks)
        self.assertIn("there is no highest-qualifying-rung propagation from indirect_strong localization", checks)
        self.assertIn("a proposal with proposed_strength == indirect_strong or weak is a hard failure", checks)

    def test_item13_whole_run_reject_never_degraded_to_unknown(self):
        on_fail = _norm(self.item["13_machine_acceptance_criteria"]["on_failure"])
        self.assertIn("rejects the whole run -- it is never degraded to an accepted unknown", on_fail)
        self.assertIn("a local surface_context_id equal to the canonical context_id", on_fail)
        self.assertIn("a qualifying direct or qualifying indirect_strong observation with no local surface_context_id", on_fail)
        self.assertIn("an indirect_strong rung asserted on a well_matched_crc_model / non_crc_model context", on_fail)
        self.assertIn("a well-matched crc model observation used as a fatal_review contributor", on_fail)

    def test_item15_localization_only_and_experiment_required_are_narrow(self):
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        loc = _norm(i15["localization_only_completed_landscape"])
        self.assertIn("inconclusive / unknown", loc)
        self.assertIn("zero proposal evidence_refs", loc)
        self.assertIn("experiment_required", loc)
        e = _norm(i15["experiment_required"])
        self.assertIn("only when the enumerated public surface source space is completed / exhausted", e)
        self.assertIn("while any unresolved public item remains the resolution stays public_resolvable / currently_unresolvable -- do not auto-add experiment_required", e)
        low = _norm(i15["low_but_present"])
        self.assertIn("supporting / contextual by default", low)
        self.assertIn("never yields a fatal_review contribution", low)

    def test_item16_stop_rule_never_stops_on_first_negligible_observation(self):
        i16 = self.item["16_stop_rule"]
        pf = _norm(" ".join(i16["potential_fatal_trigger"]))
        self.assertIn("the module never stops on the first negligible-antigen observation", pf)
        self.assertIn("only after the necessary surface-search completeness is satisfied", pf)

    def test_item17_handoff_never_kills_and_tgt04_never_discharges_tgt06(self):
        i17 = self.item["17_downstream_consumer_and_handoff"]
        never = _flatten(i17["this_module_does_not"])
        self.assertIn("produce a candidate-level decision or kill", never)
        self.assertIn("let surface localization discharge the quantitative antigen-density requirement", never)
        self.assertIn("derive an antigen-density threshold, cutoff or \"clinically effective range\" from a measured value", never)
        cons = _flatten(i17["once_human_approved_the_resulting_canonical_CandidateGateAssessment_is_consumed_by"])
        self.assertIn("tgt-04 never discharges tgt-06", cons)


class ReviewRound1RegressionTests(unittest.TestCase):
    """PR E11 ChatGPT AI审核方案 review round 1 -- the 4 narrow blockers.

    (1) the "or well-matched CRC models" ladder permission is DIRECT-only -- an
        INDIRECT_STRONG localization rung requires surface_context_class ==
        CRC_MALIGNANT_CELLS;
    (2) a fatal_review contributor is a CRC-malignant-cell quantitative
        observation ONLY -- a well-matched CRC model observation may drive an
        ordinary Direction but is never a fatal contributor, and Route B
        convergence is across CRC malignant-cell surface-context identities;
    (3) BOTH a qualifying DIRECT and a qualifying INDIRECT_STRONG observation
        carry an auditable local surface_context_id, and the
        SurfaceAvailabilityCompletion carries qualifying_indirect_surface_context_ids
        as an audit-integrity set (never a grading axis -- localization-only +
        a valid indirect set is still INCONCLUSIVE / UNKNOWN);
    (4) for a QUANTITATIVE_SURFACE_DENSITY observation the raw
        reported_density_value / _unit / _summary are factual exact-reuse parity
        fields when present -- a drift on reuse is a HARD identity failure.
    """

    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.checks = _flatten(
            self.item["13_machine_acceptance_criteria"][
                "a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"
            ]
        )

    # ---- blocker 1 ---------------------------------------------------------
    def test_indirect_strong_rung_context_is_crc_malignant_cells_only(self):
        checks = self.checks
        self.assertIn("an indirect_strong localization rung is narrower than direct on context", checks)
        self.assertIn("it requires surface_context_class == crc_malignant_cells (never well_matched_crc_model, never non_crc_model)", checks)
        self.assertIn('the "or well-matched crc models" permission exists only in the direct quantitative-density class', checks)
        self.assertIn("a well-matched crc model membranous-ihc / surface-proteomics observation is a contextual localization reading, never an indirect_strong rung", checks)
        rca = _norm(self.item["06_direction_interpretation"]["rung_context_authority"])
        self.assertIn('the "or well-matched crc models" permission in the frozen pr d ladder is direct-only', rca)
        self.assertIn("may qualify only on surface_context_class == crc_malignant_cells", rca)

    def test_well_matched_model_quantitative_density_still_reaches_direct(self):
        rules = _norm(" ".join(self.item["09_evidence_source_plan"]["source_authority_rules"]))
        self.assertIn("a quantitative antigen-density measurement in a well-matched crc model can reach direct", rules)
        self.assertIn("a membranous-ihc / cell-surface-proteomics localization observation in a well-matched crc model never reaches indirect_strong", rules)

    # ---- blocker 2 ---------------------------------------------------------
    def test_fatal_contributor_is_crc_malignant_cell_only(self):
        crit = _flatten(self.item["08_fatal_conditions"]["machine_detection_criteria"]["each_contributing_observation_must_be"])
        self.assertIn("on crc malignant cells only -- not a well-matched crc model and not any model proxy", crit)
        self.assertIn("it does not extend fatal authority", crit)
        self.assertIn("surface_context_class == crc_malignant_cells", crit)
        excl = _flatten(self.item["08_fatal_conditions"]["explicitly_excluded_from_a_fatal_trigger"])
        self.assertIn("a well-matched crc model quantitative negligible_or_undetectable observation", excl)
        self.assertIn("it may drive an ordinary direct opposes direction but is never a fatal_review contributor", excl)

    def test_fatal_review_required_iff_excludes_the_model_proxy(self):
        r = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["required_is_true_iff"])
        self.assertIn("each on crc malignant cells only", r)
        self.assertIn("not a well-matched crc model", r)
        self.assertIn("across at least two independent qualified crc malignant-cell surface-context identities", r)
        c13 = self.checks
        self.assertIn("every contributing observation is a direct-class quantitative crc-malignant-cell negligible_or_undetectable observation", c13)
        self.assertIn("no well-matched crc model / localization / rna / non-crc / low-but-present contributor", c13)

    # ---- blocker 3 ---------------------------------------------------------
    def test_both_direct_and_indirect_strong_qualifying_obs_carry_a_local_id(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("both a qualifying direct quantitative density observation and a qualifying indirect_strong localization observation must carry at least one auditable local surface_context_id", i11)
        self.assertIn("any observation classified qualifying direct or qualifying indirect_strong carries at least one auditable local surface_context_id", self.checks)
        i06 = _norm(self.item["06_direction_interpretation"]["qualifying_local_surface_context_identity"])
        self.assertIn("this is evidence / audit-integrity identity, not a grading axis", i06)
        self.assertIn("a localization-only completed landscape (even with a valid indirect surface-context set) still maps to inconclusive / unknown", i06)

    def test_completion_carries_qualifying_indirect_surface_context_ids(self):
        tc = _norm(self.item["09_evidence_source_plan"]["surface_search_landscape"]["typed_completion_record"])
        self.assertIn("qualifying_direct_surface_context_ids / qualifying_indirect_surface_context_ids", tc)
        self.assertIn("this is evidence / audit-integrity reconciliation, not a grading axis", tc)
        self.assertIn("both qualifying context id sets -- direct and indirect", tc)
        each = _flatten(self.item["11_evidencepackage_output_contract"]["each_package"])
        self.assertIn("qualifying_direct_surface_context_ids, qualifying_indirect_surface_context_ids", each)
        namespace = self.checks
        self.assertIn("completion.qualifying_indirect_surface_context_ids", namespace)

    def test_localization_only_with_valid_indirect_set_is_still_unknown(self):
        loc = _norm(self.item["15_failure_unknown_and_conflict_behavior"]["localization_only_completed_landscape"])
        self.assertIn("even when a non-empty valid qualifying_indirect_surface_context_ids set is reconciled", loc)
        self.assertIn("the indirect set is audit-integrity only, it never lifts the strength above unknown", loc)

    # ---- blocker 4 ---------------------------------------------------------
    def test_raw_density_value_is_an_exact_reuse_parity_field(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("the raw factual reported_density_value / reported_density_unit / reported_density_summary are factual exact-reuse parity fields when present", i11)
        self.assertIn("a reused ep whose stored raw density value, unit or summary differs from the canonical package's is a hard identity integrity failure", i11)
        self.assertIn("this is empirical-identity parity of a canonical observation, not classification authority", i11)
        self.assertIn("no drifted reported_density_value / reported_density_unit / reported_density_summary on a reused quantitative_surface_density package when present", self.checks)

    def test_raw_density_drift_is_hard_but_not_a_scoring_event(self):
        checks = self.checks
        self.assertIn("a drift in the stored reported_density_value / reported_density_unit / reported_density_summary (when present on the canonical package) is a hard identity integrity failure, not a scoring event", checks)
        on_fail = _norm(self.item["13_machine_acceptance_criteria"]["on_failure"])
        self.assertIn("a drifted reused reported_density_value / reported_density_unit / reported_density_summary", on_fail)


class NoImplementationInPrE11Tests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation_and_registry_changes(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["trial_or_dataset_retrieval_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_or_ranking_scoring"], "forbidden")
        self.assertEqual(p["antigen_density_cutoff_or_molecules_per_cell_or_abc_or_percent_positive_or_hscore_threshold"], "forbidden")
        self.assertEqual(p["invented_clinically_effective_antigen_density_range"], "forbidden")
        self.assertEqual(p["generic_gatemodule_framework_or_base_class_in_this_pr"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt01"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt02"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt03"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt05"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt08"], "forbidden")
        self.assertEqual(p["modifies_binding_or_registry_or_existing_tests"], "forbidden")
        self.assertEqual(p["only_allowed_existing_file_mutation"], "append_to_logs_worklog_md")
        self.assertEqual(p["migration_pending"], "remains")

    def test_no_tgt04_implementation_package_exists_yet(self):
        pkg = ROOT / "gate_modules" / "tgt04_tumor_surface_availability_density_plausibility"
        self.assertFalse(pkg.exists(), "PR E11 is design-only; the package is PR E12")

    def test_tgt04_binding_is_still_zero_and_the_built_five_are_untouched(self):
        gs = yaml.safe_load(CRC_GATESET.read_text())
        by_gate = {
            b["gate_id"]: b["primary_module_version"]
            for b in gs["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(by_gate["TGT-04"], "0.0.0")
        for g in ("TGT-01", "TGT-02", "TGT-03", "TGT-05", "TGT-08"):
            self.assertEqual(by_gate[g], "1.0.0")
        for g in ("TGT-06", "TGT-07"):
            self.assertEqual(by_gate[g], "0.0.0")

    def test_deferred_block_names_the_e12_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e12_plus"]).lower()
        self.assertIn("gate_modules/tgt04_tumor_surface_availability_density_plausibility/", joined)
        self.assertIn("surfaceavailabilitycompletion", joined)
        self.assertIn("1.0.0", joined)
        self.assertIn("binding / registry reconciliation", joined)

    def test_only_the_five_built_packages_exist_and_no_tgt04_dir(self):
        gm = ROOT / "gate_modules"
        py_files = sorted(str(p.relative_to(ROOT)) for p in gm.rglob("*.py"))
        allowed = (
            "tgt01_adc_modality_precedent",
            "tgt02_indication_specific_malignant_cell_coverage",
            "tgt03_treatment_metastatic_persistence",
            "tgt05_normal_tissue_fatal_liability",
            "tgt08_target_opportunity_competition_ip_whitespace",
        )
        self.assertTrue(all(any(pkg in p for pkg in allowed) for p in py_files), py_files)


class DrawingTests(unittest.TestCase):
    def setUp(self):
        self.text = DRAWING.read_text()

    def test_drawing_exists_and_names_the_module_and_pr(self):
        self.assertIn("MOD-TGT04", self.text)
        self.assertIn("PR E11", self.text)
        self.assertIn("Tumor Surface Availability / Density Plausibility", self.text)

    def test_drawing_covers_all_seventeen_items(self):
        for n in range(1, 18):
            self.assertRegex(self.text, rf"\|\s*{n}\s*\|\s*\*\*", f"drawing row {n} missing")

    def test_drawing_has_the_three_headline_blockquotes(self):
        self.assertIn("Surface localization is not antigen density", self.text)
        self.assertIn("Quantitative values are evidence, not thresholds", self.text)
        self.assertIn("Reproducible quantitative `NEGLIGIBLE_OR_UNDETECTABLE` surface antigen may", self.text)

    def test_drawing_freezes_the_key_corrections(self):
        t = self.text
        self.assertIn("single-tier grading authority", " ".join(t.split()).lower())
        self.assertIn("Legal Direction × Strength pairs (exactly 5)", t)
        self.assertIn("`LOW_BUT_PRESENT` alone", t)
        self.assertIn("Route A", t)
        self.assertIn("Route B", t)
        self.assertIn("not a closed assay whitelist", " ".join(t.split()).lower())

    def test_drawing_states_no_binding_or_registry_or_test_change(self):
        norm = " ".join(self.text.split()).lower()
        self.assertIn("append to `logs/worklog.md`", norm)
        self.assertIn("does not touch it, the binding, the registry or any existing test", norm)


if __name__ == "__main__":
    unittest.main()
