"""Runtime Migration PR E15: the MOD-TGT07 construction contract.

Asserts:
* the 17-item acceptance checklist is present, complete and ordered (template
  reused from the approved PR E1 template);
* items 03 / 05 / 07 / 08 are a normalized-equality parity with the FROZEN PR D
  TGT-07 contract (crc_adc_target_gateset.yaml), item 04 is an EXACT derived
  parity (set equality, not a superset) against evidence_required + the ladder,
  and -- confirmed by the ChatGPT AI审核方案 E15-2 ruling -- the frozen PR D TGT-07
  contract has NO inference_guard field (EVGAP-01 is a TGT-04 construct only);
* TGT-07 is frozen as an EXPOSURE-CONTEXT-DEPENDENT sink-liability gate with a
  HIGHEST-QUALIFYING-RUNG grading authority (the TGT-03 / TGT-06 precedent), NOT
  the TGT-04 single-tier exception: a qualifying INDIRECT_STRONG soluble-antigen
  landscape with no DIRECT is POSITIVE / INDIRECT_STRONG, and the only legal
  Direction x Strength pairs are exactly SIX -- POSITIVE/DIRECT,
  POSITIVE/INDIRECT_STRONG, NEGATIVE/DIRECT, CONFLICTING/DIRECT,
  INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN;
* the ChatGPT AI审核方案 E15 scoping ruling is frozen as SEVEN required
  tightenings: (1) Option A -- IS propagates; six legal pairs; no
  NEGATIVE / INDIRECT_STRONG; (2) a below-detection / below-quantitation-limit
  quantitation is CONTEXTUAL, not positive IS and not NEGATIVE -- a new CLOSED
  circulating_soluble_target_status enum; (3) a canonical NEGATIVE / DIRECT is
  produced ONLY by a qualified intended-ADC SOLUBLE_ANTIGEN_TMDD_ANALYSIS
  concluding NO_MATERIAL_SOLUBLE_SINK; (4) fatal is ONE predicate + TWO source
  paths (clinical / TMDD) -- no Route A / Route B convergence, NO mandatory
  reproducibility predicate on the single-observation clinical fatal path
  (reproducibility_status is optional factual metadata only -- PR E15 review
  round-1), and NO global cancellation precondition; (5) a lightweight
  single-string
  sink_exposure_context_id (DIRECT only) -- no declared_multi / IDENTIFIED_MULTI
  / third-state machinery; (6) typed tmdd_input_adequacy_status /
  same_target_therapeutic_match_status / soluble_antigen_attribution_status --
  E16 never semantic-parses prose for DIRECT / fatal authority; (7) four
  SolubleAntigenEvidenceCompletion search axes (the quantitation axis needs both
  cohort subspaces), no qualifying_indirect_evidence_context_ids set;
* the 3 headline conclusions are frozen verbatim; the TGT-07 potential fatal
  signal is a STRICT SUBSET of POSITIVE / DIRECT, surfaced at most as a
  machine-local fatal_review = POTENTIAL_FATAL_PATTERN;
* predicted-cleavage-site / family-analogy inference never above WEAK; a
  quantified CRC-patient soluble target without a TMDD analysis / a
  sheddase-substrate status / a secreted isoform never above INDIRECT_STRONG;
  DIRECT is a MATERIALITY proof that is never synthesized across unrelated
  observations;
* items 10-17 inherit the E2 / E4 / E6 / E8 / E10 / E12 / E14 runtime genes (an
  explicitly qualified evidence context for a rung; the local
  sink_exposure_context_id namespace separate from the canonical context_id;
  every qualified factual state carries an auditable basis; CLOSED typed status
  enums + a non-empty factual analysis_method for DIRECT; a kind / fact-specific
  non-inflated study_context; the frozen proposal-relative EvidenceRole mapping);
* PR E15 ships no implementation -- no gate_modules/tgt07.../ directory, no
  provider / adapter / retrieval / runner, no numeric / ranking score, no
  concentration / sink-ratio cutoff or invented range, no generic GateModule
  framework; MOD-TGT07 primary_module_version stays "0.0.0"; the binding, the
  registry and every existing test are untouched (the only allowed existing-file
  mutation is an append to logs/worklog.md); MIGRATION_PENDING remains;
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt07_shedding_soluble_antigen_sink_liability.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-07_Shedding_Soluble_Antigen_Sink_Liability.md"
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

_OBSERVATION_KINDS = (
    "CLINICAL_ANTIGEN_SINK_PK_EFFECT",
    "SOLUBLE_ANTIGEN_TMDD_ANALYSIS",
    "SOLUBLE_ANTIGEN_QUANTITATION",
    "SHEDDASE_SUBSTRATE_STATUS",
    "SECRETED_ISOFORM",
    "PREDICTED_CLEAVAGE_SITE_INFERENCE",
    "FAMILY_ANALOGY_SHEDDING_INFERENCE",
    "SEARCH_COMPLETION_AUDIT",
)

_SINK_MATERIALITY_OUTCOMES = (
    "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE",
    "MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE",
    "NO_MATERIAL_SOLUBLE_SINK",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
)

_CIRCULATING_SOLUBLE_TARGET_STATUS = (
    "QUANTIFIED_PRESENT",
    "BELOW_DETECTION_OR_QUANTITATION_LIMIT",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
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
        self.assertEqual(m["pr"], "runtime_migration_pr_e15")
        self.assertEqual(
            m["scope"],
            "tgt07_mod_tgt07_construction_contract_drawing_validation_and_acceptance_checklist_only",
        )
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e16", m["next"])
        self.assertIn("TGT-06 -> TGT-07", m["order"])
        self.assertIn("LAST primary Module", m["order"])

    def test_template_provenance_reuses_the_e1_template(self):
        tp = self.doc["template_provenance"]
        self.assertEqual(tp["status"], "RECONSTRUCTED")
        self.assertTrue(tp["claim"]["not_claimed_verbatim_from_blueprint"])
        self.assertTrue(tp["claim"]["seventeen_item_template_reused_from_e1"])
        self.assertIn("e1 17-item construction template", tp["template_basis"].lower())
        self.assertTrue(E1_CONTRACT.is_file())

    def test_kernel_invariant_exposure_context_but_not_a_kill(self):
        inv = _norm(self.doc["kernel_invariant"])
        self.assertIn("src/ must never import gate_modules/", inv)
        self.assertIn("the gate_question is the shedding / soluble-antigen / sink liability question", inv)
        self.assertIn("one clean material-sink direct sink-exposure context is a sufficient positive / direct answer", inv)
        self.assertIn("a canonical negative / direct is reachable only from a qualified soluble_antigen_tmdd_analysis", inv)
        self.assertIn("does propagate to a gate-level strength", inv)
        self.assertIn("this is the highest-qualifying-rung grading authority, not the tgt-04 single-tier exception", inv)
        self.assertIn("the fatal signal is a strict subset of positive / direct and there is no global cancellation precondition", inv)
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
        self.assertIn("a measurable soluble form is not the same thing as a material antigen sink", joined)
        self.assertIn("materiality requires direct evidence from a documented same-target pk / pd sink effect or a qualified quantitative tmdd analysis", joined)
        self.assertIn("is never converted by the module into a universal material-sink threshold", joined)
        self.assertIn("soluble-antigen materiality is exposure-context dependent", joined)
        self.assertIn("one clean direct material-sink context is sufficient for positive / direct", joined)
        self.assertIn("the machine has no conflict resolver in v1", joined)
        self.assertIn("the tgt-07 potential-fatal signal is a strict subset of positive / direct, not a convergence rule", joined)
        self.assertIn("clinical and tmdd evidence are alternative qualified source paths", joined)
        self.assertIn("the machine never decides fatality, kill, hold, therapeutic efficacy or the candidate-level consequence", joined)

    def test_headline_conclusions_match_the_manifest_style_frozen_list(self):
        self.assertEqual(
            [_norm(x) for x in self.doc["headline_conclusions"]],
            [_norm(x) for x in self.doc["three_headline_conclusions"]],
        )


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item01_gate_identity(self):
        i = self.item["01_gate_identity_and_version"]
        self.assertEqual(i["gate_id"], "TGT-07")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["gate_name"], "Shedding / Soluble-Antigen / Sink Liability")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["gateset_version"], "1.0")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT07")
        self.assertEqual(i["module_implementation_version"], "0.0.0")
        self.assertIn("pr e16 builds it", _norm(i["rule"]))


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt07 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-07"]

    def test_item03_gate_question_parity(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt07["gate_question"]),
        )

    def test_item05_evidence_ladder_parity(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt07["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt07["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt07["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_parity(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt07["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt07["forbidden_inference"]],
        )

    def test_tgt07_has_no_inference_guard_field(self):
        # E15-2 ruling: the frozen PR D TGT-07 contract has NO inference_guard.
        self.assertNotIn("inference_guard", self.tgt07)
        i07 = self.item["07_allowed_and_forbidden_inference"]
        self.assertNotIn("inference_guard", i07)
        self.assertIn("has no inference_guard field", _norm(i07["no_inference_guard_field"]))
        self.assertIn("the evgap-01 surface-localization lock is a tgt-04 construct only", _norm(i07["no_inference_guard_field"]))

    def test_item08_fatal_conditions_parity(self):
        self.assertEqual(
            [_norm(x) for x in self.item["08_fatal_conditions"]["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt07["fatal_conditions"]],
        )

    def test_item08_potential_fatal_signal_is_verbatim_pr_d_only(self):
        sig = self.item["08_fatal_conditions"]["potential_fatal_signal"]
        self.assertEqual(len(sig), 1)
        self.assertEqual(_norm(sig[0]), _norm(self.tgt07["fatal_conditions"][0]))

    def test_item04_derived_parity_is_exact_not_a_superset(self):
        item04 = self.item["04_admissible_evidence_classes"]
        got = set(_norm(x) for x in item04["admissible"])
        want = set(_norm(x) for x in self.tgt07["evidence_required"])
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            want |= set(_norm(x) for x in self.tgt07["evidence_ladder"][grade]["admissible_evidence_classes"])
        self.assertEqual(got, want)

    def test_item04_excludes_the_other_seven_gates_and_a_universal_range(self):
        na = _norm(" ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"]))
        for tok in ("tgt-01", "tgt-02", "tgt-03", "tgt-04", "tgt-05", "tgt-06", "tgt-08"):
            self.assertIn(tok, na)
        self.assertIn("material soluble-antigen sink concentration", na)

    def test_pr_d_unknown_behavior_is_no_soluble_antigen_data_to_unknown(self):
        self.assertIn("no soluble-antigen data", _norm(self.tgt07["unknown_behavior"]))
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        self.assertIn(
            "no soluble-antigen data -> unknown",
            _norm(i15["weak_only_or_below_assay_limit_only_or_no_qualifying_evidence_completed_landscape"]),
        )


class ExposureContextAndHighestRungGradingTests(unittest.TestCase):
    def setUp(self):
        self.i06 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["06_direction_interpretation"]

    def test_highest_qualifying_rung_not_single_tier(self):
        t = _norm(self.i06["highest_qualifying_rung_grading_authority"])
        self.assertIn("highest-qualifying-rung grading authority (the tgt-03 / tgt-06 precedent), not the tgt-04 single-tier exception", t)
        self.assertIn("positive / indirect_strong", t)
        self.assertIn('locks unknown only to "no soluble-antigen data -> unknown"', t)

    def test_legal_direction_strength_pairs_are_exactly_six(self):
        pairs = [_norm(p) for p in self.i06["legal_direction_strength_pairs"]]
        self.assertEqual(
            set(pairs),
            {
                "positive / direct",
                "positive / indirect_strong",
                "negative / direct",
                "conflicting / direct",
                "inconclusive / direct",
                "inconclusive / unknown",
            },
        )
        self.assertEqual(len(self.i06["legal_direction_strength_pairs"]), 6)
        no = _norm(self.i06["no_other_pairs"])
        self.assertIn("exactly six legal direction x strength pairs", no)
        self.assertIn("no negative / indirect_strong", no)
        self.assertIn("no conflicting / indirect_strong", no)
        self.assertIn("no inconclusive / indirect_strong", no)
        self.assertIn("no inconclusive / weak", no)

    def test_aggregation_truth_table(self):
        tt = self.i06["tgt07_specific_aggregation_truth_table"]
        self.assertIn("positive / direct", _norm(tt["completed_and_at_least_one_clean_material_sink_direct_exposure_context"]))
        self.assertIn("conflicting / direct", _norm(tt["completed_and_no_clean_material_sink_direct_and_a_sink_exposure_context_carries_both_a_material_sink_direct_and_a_no_material_sink_direct_observation"]))
        self.assertIn("negative / direct", _norm(tt["completed_and_no_material_sink_direct_and_at_least_one_qualifying_intended_adc_no_material_sink_tmdd"]))
        self.assertIn("inconclusive / direct", _norm(tt["completed_and_no_material_sink_direct_and_no_canonical_no_material_sink_tmdd_and_at_least_one_direct_quality_mixed_or_unresolved_analysis"]))
        self.assertIn("positive / indirect_strong", _norm(tt["completed_and_no_direct_rung_observation_and_at_least_one_qualifying_positive_indirect_strong"]))
        self.assertIn("inconclusive / unknown", _norm(tt["completed_and_weak_only_or_below_assay_limit_only_or_no_qualifying_evidence"]))
        order = _norm(tt["frozen_evaluation_order"])
        self.assertIn("in this exact order and stops at the first match", order)
        self.assertIn("if at least one clean / uncontested material-sink direct sink-exposure context exists -> positive / direct", order)
        self.assertIn("a no-material-sink direct context b alongside a clean material-sink context a is still positive / direct", order)
        self.assertIn("no machine conflict resolver", order)
        self.assertIn("different sink-exposure contexts having different materiality is never mapped to conflicting", order)

    def test_sink_exposure_context_identity_is_a_single_string_no_multi_machinery(self):
        s = _norm(self.i06["tgt07_specific_aggregation_truth_table"]["sink_exposure_context_identity"])
        self.assertIn("a single local string", s)
        self.assertIn("must carry a non-empty sink_exposure_context_id", s)
        self.assertIn("an indirect_strong observation, a weak observation and a search_completion_audit observation carry sink_exposure_context_id == \"\"", s)
        self.assertIn("there is deliberately no declared_multi analysis, no identified_multi state", s)
        self.assertIn("no set-projection helper", s)
        self.assertIn("a sink_exposure_context_id equal to the canonical instantiation context_id (ctx-crc-refractory-mcrc) is a hard identity-namespace failure", s)

    def test_existence_proof_dominance(self):
        d = _norm(self.i06["existence_proof_dominance"])
        self.assertIn("dominates a no-material-sink direct result in a different sink-exposure context", d)
        self.assertIn("the gate answer is positive / direct -- not negative and not automatically conflicting", d)
        self.assertIn("it never reverses the target-level sink-liability conclusion", d)

    def test_different_exposure_contexts_differ_is_not_a_conflict(self):
        d = _norm(self.i06["different_exposure_contexts_differ_is_not_a_conflict"])
        self.assertIn("is not a conflicting signal", d)
        self.assertIn("this is a hard lock", d)
        self.assertIn("never map inter-context heterogeneity to conflicting", d)
        self.assertIn("it never runs a machine conflict resolver", d)

    def test_below_detection_is_contextual(self):
        b = _norm(self.i06["below_detection_is_contextual"])
        self.assertIn("does not satisfy the positive indirect_strong class", b)
        self.assertIn("does not become a negative / indirect_strong", b)
        self.assertIn("there is no frozen negative indirect_strong evidence class", b)
        self.assertIn("if the completed landscape contains only this kind of evidence -> inconclusive / unknown", b)
        self.assertIn("this is an explicit frozen ruling", b)

    def test_canonical_negative_direct_only_from_intended_adc_tmdd(self):
        c = _norm(self.i06["canonical_negative_direct_only_from_intended_adc_tmdd"])
        self.assertIn("a canonical negative / direct is produced only by a qualifying soluble_antigen_tmdd_analysis whose exposure_scenario_class == intended_adc_exposure", c)
        self.assertIn('"some same-target therapeutic did not observe a pk sink" is not a negative / direct', c)
        self.assertIn("the frozen direct clinical class is a documented antigen-sink effect, not a clinical study with no observed effect", c)

    def test_no_cross_observation_synthesis_of_direct(self):
        s = _norm(self.i06["no_cross_observation_synthesis_of_direct"])
        self.assertIn("direct is never synthesized by the module from unrelated observations", s)
        self.assertIn("do not combine into a direct material-sink proof -- even for the same target", s)
        self.assertIn("one upstream-qualified observation", s)
        self.assertIn("mod-tgt07 itself never joins unrelated evidencepackages to assemble direct", s)

    def test_separate_typed_upstream_facts(self):
        s = _norm(self.i06["upstream_qualified_factual_states"])
        self.assertIn("e16 must not overload one field to carry two meanings", s)
        self.assertIn("e16 must never semantic-parse prose to obtain direct or fatal authority", s)
        self.assertIn("circulating_soluble_target_status", s)
        self.assertIn("sink_materiality_outcome", s)
        self.assertIn("never computed by the module from a number", s)
        self.assertIn("tmdd_input_adequacy_status", s)
        self.assertIn("same_target_therapeutic_match_status", s)
        self.assertIn("soluble_antigen_attribution_status", s)
        self.assertIn("exposure_scenario_class", s)
        self.assertIn("qualified is not a positive sink-liability conclusion", s)

    def test_sink_materiality_direction_mapping(self):
        m = self.i06["sink_materiality_direction_mapping"]
        self.assertIn("supports_sink_liability", _norm(m["sink_materiality_outcome_material_soluble_sink_with_clinical_exposure_compromise"]))
        self.assertIn("fatal eligible", _norm(m["sink_materiality_outcome_material_soluble_sink_with_clinical_exposure_compromise"]))
        self.assertIn("supports_sink_liability", _norm(m["sink_materiality_outcome_material_soluble_sink_without_established_clinical_exposure_compromise"]))
        self.assertIn("nonfatal", _norm(m["sink_materiality_outcome_material_soluble_sink_without_established_clinical_exposure_compromise"]))
        no_mat = _norm(m["sink_materiality_outcome_no_material_soluble_sink"])
        self.assertIn("opposes_sink_liability", no_mat)
        self.assertIn("only from a soluble_antigen_tmdd_analysis with exposure_scenario_class == intended_adc_exposure", no_mat)
        self.assertIn("otherwise contextual", no_mat)
        self.assertIn("contextual", _norm(m["sink_materiality_outcome_mixed_or_unresolved"]))
        self.assertIn("contextual", _norm(m["sink_materiality_outcome_not_established"]))

    def test_inconclusive_direct_is_legal_and_distinct_from_unknown(self):
        d = _norm(self.i06["inconclusive_direct_is_legal"])
        self.assertIn("sink_materiality_outcome == mixed_or_unresolved", d)
        self.assertIn("distinct from inconclusive / unknown", d)


class QuantitativeValuesAreEvidenceNotThresholdsTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_direct_is_a_materiality_proof_not_a_concentration_measurement(self):
        k = _norm(self.item["05_evidence_ladder_and_evidence_ceiling"]["direct_is_a_materiality_proof_not_a_concentration_measurement"])
        self.assertIn("the pr d direct class is a materiality proof", k)
        self.assertIn("it is satisfied by one qualifying integrated observation in a qualified sink-exposure context", k)
        self.assertIn("it does not require a quorum of studies, a minimum soluble-antigen concentration, or a minimum sink ratio", k)

    def test_quantitative_values_are_evidence_not_thresholds(self):
        k = _norm(self.item["05_evidence_ladder_and_evidence_ceiling"]["quantitative_values_are_evidence_not_thresholds"])
        self.assertIn("may and should preserve a source-reported numeric fact when the source states one", k)
        self.assertIn('invented universal "material soluble-antigen sink concentration"', k)
        self.assertIn("no tgt-04-style symmetric raw-value reuse-parity branch is needed", k)
        self.assertIn("circulating_soluble_target_status and sink_materiality_outcome (closed enums), never a number", k)

    def test_item09_no_universal_threshold(self):
        n = _norm(self.item["09_evidence_source_plan"]["no_universal_threshold"])
        self.assertIn("no circulating soluble-antigen concentration cutoff", n)
        self.assertIn("no sink-ratio threshold", n)
        self.assertIn('no invented universal "material soluble-antigen sink concentration" range', n)
        self.assertIn("a source-reported numeric fact may be preserved as a factual measurement", n)

    def test_no_dedicated_raw_value_reuse_parity_branch(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("there is no dedicated typed raw numeric field for soluble antigen and therefore no tgt-04-style symmetric raw-value reuse-parity branch", i11)

    def test_no_numeric_or_threshold_language_in_the_contract(self):
        # A bare source-reported number (e.g. "serum soluble target 18 ng/mL") is
        # an ADMISSIBLE factual measurement per the E15 ruling; what is forbidden
        # is a numeric DECISION / threshold construct.
        text = _norm(CONTRACT.read_text())
        self.assertIsNone(
            re.search(
                r"concentration\s*[<>=]\s*\d|sink[- ]ratio\s*[<>=]\s*\d|turnover\s*[<>=]\s*\d"
                r"|[<>=]\s*\d+\s*(ng|pg|ug|mg|nm|pm|percent|%|fold)"
                r"|\d+\s*(ng/ml|nm|%)\s*(cutoff|threshold)|\bnumeric_score\s*="
                r"|if\s+\w+\s*[<>=]",
                text,
            )
        )
        self.assertIn("no circulating soluble-antigen concentration cutoff", text)
        self.assertIn("is never converted by the module into a universal material-sink threshold", text)


class FatalReviewAndProposalTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item08_no_global_precondition(self):
        c = self.item["08_fatal_conditions"]["machine_detection_criteria"]
        gp = _norm(c["no_global_precondition"])
        self.assertIn("there is no global cancellation precondition", gp)
        self.assertIn("a positive / direct does not cancel the fatal trigger", gp)
        self.assertIn("the tgt-07 fatal signal is a stronger sub-class of positive / direct", gp)

    def test_item08_no_convergence_requirement(self):
        c = self.item["08_fatal_conditions"]["machine_detection_criteria"]
        nc = _norm(c["no_convergence_requirement"])
        self.assertIn("one qualifying direct observation is sufficient", nc)
        self.assertIn("does not require two independent findings, cross-study convergence, multiple constructs, or a tgt-06-style route a / route b", nc)
        self.assertIn("two admissible source paths, not two convergence routes", nc)

    def test_item08_fatal_predicate_and_two_source_paths(self):
        c = self.item["08_fatal_conditions"]["machine_detection_criteria"]
        pred = _norm(c["fatal_predicate"])
        self.assertIn("sink_materiality_outcome == material_soluble_sink_with_clinical_exposure_compromise", pred)
        self.assertIn("satisfies the clinical source path or the tmdd source path", pred)
        clinical = _flatten(c["clinical_source_path"])
        self.assertIn("observation_kind == clinical_antigen_sink_pk_effect", clinical)
        self.assertIn("same_target_therapeutic_match_status == qualified", clinical)
        self.assertIn("same_target_therapeutic_ref != \"\"", clinical)
        self.assertIn("soluble_antigen_attribution_status == qualified", clinical)
        self.assertIn("analysis_validation_status == qualified", clinical)
        self.assertIn("sink_materiality_outcome == material_soluble_sink_with_clinical_exposure_compromise", clinical)
        # PR E15 review round-1: NO mandatory reproducibility predicate on the clinical fatal path
        self.assertNotIn("reproducibility_status == qualified with an auditable reproducibility_basis", clinical)
        self.assertIn("reproducibility_status is not a prerequisite", clinical)
        tmdd = _flatten(c["tmdd_source_path"])
        self.assertIn("observation_kind == soluble_antigen_tmdd_analysis", tmdd)
        self.assertIn("tmdd_input_adequacy_status == qualified", tmdd)
        self.assertIn("analysis_method != \"\"", tmdd)
        self.assertIn("exposure_scenario_class == intended_adc_exposure", tmdd)
        two = _norm(c["two_source_paths_not_routes"])
        self.assertIn("they are not a route a / route b convergence pair and not combined", two)
        self.assertIn("one qualifying observation on either path is sufficient", two)
        self.assertIn("no mandatory reproducibility predicate for the single-observation clinical fatal path in v1", two)

    def test_item08_exclusions(self):
        excl = _flatten(self.item["08_fatal_conditions"]["explicitly_excluded_from_a_fatal_trigger"])
        self.assertIn("a measured circulating soluble-antigen concentration by itself", excl)
        self.assertIn("a below-detection / below-quantitation-limit soluble-antigen measurement", excl)
        self.assertIn("material_soluble_sink_without_established_clinical_exposure_compromise", excl)
        self.assertIn("a tmdd analysis whose exposure_scenario_class is same_target_therapeutic_analogue or unresolved", excl)

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
        self.assertIn('"material soluble-antigen sink concentration range"', never)

    def test_item12_frozen_proposal_relative_evidence_role_mapping(self):
        m = _flatten(self.item["12_assessment_proposal_envelope_contract"]["the_proposal_envelope_carries"]["frozen_proposal_relative_evidence_role_mapping"])
        self.assertIn("positive / direct: a clean material-sink direct observation -> supporting", m)
        self.assertIn("negative / direct: the intended-adc no-material-sink tmdd observation -> supporting", m)
        self.assertIn("conflicting / direct: the same-context material-sink direct observation -> supporting; the same-context no-material-sink direct observation -> contradicting", m)
        self.assertIn("inconclusive / direct: the direct-quality mixed_or_unresolved analysis -> contextual", m)
        self.assertIn("positive / indirect_strong: a qualifying quantified-crc-patient / sheddase-substrate / secreted-isoform observation -> supporting", m)
        self.assertIn("contradicting appears only on a conflicting / direct proposal", m)

    def test_item12_fatal_review_fields_and_required_iff(self):
        fr = self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]
        fields = _norm(" ".join(fr["fields"]))
        self.assertIn("sink_exposure_context_ids", fields)
        self.assertIn("sink_materiality_outcome_class", fields)
        self.assertIn("source_path", fields)
        self.assertIn("clinical_attribution_basis_refs", fields)
        self.assertIn("tmdd_input_adequacy_basis_refs", fields)
        self.assertEqual(fr["machine_may_emit"], "POTENTIAL_FATAL_PATTERN")
        self.assertIn("public_fatal_signal_established", _norm(fr["machine_never_emits"]))
        r = _norm(fr["required_is_true_iff"])
        self.assertIn("sink_materiality_outcome == material_soluble_sink_with_clinical_exposure_compromise", r)
        self.assertIn("either the clinical source path", r)
        self.assertIn("or the tmdd source path", r)
        self.assertIn("one qualifying observation on either path is sufficient", r)
        self.assertIn("not a convergence pair", r)
        self.assertIn("there is no global cancellation precondition -- a positive / direct does not clear the fatal signal", r)
        self.assertIn("material_soluble_sink_without_established_clinical_exposure_compromise gives required = false", r)

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
        pl = self.i09["soluble_antigen_search_landscape"]
        comps = [_norm(x) for x in pl["declared_mandatory_search_components"]]
        self.assertEqual(len(comps), 4)
        self.assertTrue(any("soluble_antigen_quantitation_search" in c for c in comps))
        self.assertTrue(any("sheddase_processing_search" in c for c in comps))
        self.assertTrue(any("secreted_isoform_search" in c for c in comps))
        self.assertTrue(any("same_target_pk_pd_or_tmdd_search" in c for c in comps))
        both = _norm(pl["soluble_antigen_quantitation_axis_requires_both_cohort_subspaces"])
        self.assertIn("only when both the crc-patient serum / plasma subspace and the healthy-donor serum / plasma subspace have been searched / exhausted", both)
        m = _norm(pl["mandatory_is_search_completion_axes_not_evidence_prerequisites"])
        self.assertIn("not evidence prerequisites and not grading axes", m)
        self.assertIn("searched / exhausted with zero qualifying records still counts as complete", m)
        self.assertIn("public_soluble_antigen_search_complete", m)

    def test_typed_completion_is_named_and_has_only_a_direct_context_set(self):
        tc = _norm(self.i09["soluble_antigen_search_landscape"]["typed_completion_record"])
        self.assertIn("solubleantigenevidencecompletion", tc)
        self.assertIn("not a seventh core object", tc)
        self.assertIn("there is exactly one qualifying context set -- qualifying_direct_evidence_context_ids", tc)
        self.assertIn("there is deliberately no qualifying_indirect_evidence_context_ids set", tc)
        self.assertIn("the snapshot field names are the typed completion field names", tc)
        self.assertIn("a drift in the qualifying context set, -> hard reject", tc)

    def test_source_authority_hard_locks(self):
        rules = _norm(" ".join(self.i09["source_authority_rules"]))
        self.assertIn("a predicted cleavage site never establishes shedding", rules)
        self.assertIn("family analogy never establishes shedding -- weak only", rules)
        self.assertIn("a below-detection / below-quantitation-limit soluble-antigen measurement", rules)
        self.assertIn("a healthy-donor-only quantitation is contextual by default", rules)
        self.assertIn("a clinical same-target therapeutic with no reported pk sink does not automatically become direct negative", rules)
        self.assertIn("a canonical negative / direct (no_material_soluble_sink) is authoritative only from a qualified soluble_antigen_tmdd_analysis whose exposure_scenario_class == intended_adc_exposure", rules)
        self.assertIn("never synthesize direct", rules)
        self.assertIn("tgt-07 has no inference_guard", rules)


class RuntimeGeneInheritanceTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item10_fixed_instantiation_context_is_hard_pinned(self):
        i10 = _flatten(self.item["10_input_contract"])
        self.assertIn("ctx-crc-refractory-mcrc", i10)
        self.assertIn("a separate namespace from each observation's local sink_exposure_context_id", i10)
        self.assertIn("every observation.context_key equals the run's context_key", i10)
        self.assertIn("solubleantigenevidencecompletion.search_scope equals the run's declared soluble_antigen_search_scope", i10)

    def test_item11_exact_reuse_dedup_and_namespace(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("observation_id is part of the exact-reuse identity parity", i11)
        self.assertIn("including circulating_soluble_target_status and sink_materiality_outcome", i11)
        self.assertIn("reused ep's own provenance source_type / source_identifier / locator must still equal the resolved canonical sourceindex record", i11)
        self.assertIn("dedup uses the improved tgt-03 rule", i11)
        self.assertIn("both observations survive", i11)
        self.assertIn("a search_completion_audit ep is never a dedup loser", i11)
        self.assertIn("sink_exposure_context_id is a local evidence-context identity namespace", i11)
        self.assertIn("never collapse a sink_exposure_context_id onto the canonical context_id", i11)
        self.assertIn("kind / fact-specific study_context", i11)

    def test_item13_runtime_genes(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("direct is a materiality proof, not a concentration measurement and not a closed method whitelist", checks)
        self.assertIn("analysis_validation_status is in {qualified, not_established}", checks)
        self.assertIn("a non-empty factual analysis_method", checks)
        self.assertIn("the local sink-exposure namespace", checks)
        self.assertIn("collapses a sink_exposure_context_id onto the canonical context_id is a hard identity-namespace failure", checks)
        self.assertIn("a below-detection / below-quantitation-limit soluble-antigen measurement", checks)
        self.assertIn("is contextual only", checks)
        self.assertIn("every classification-driving qualified status carries an auditable basis", checks)
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("never promote a healthy-donor / predicted-cleavage-site / family-analogy / audit observation's source study context", i11)

    def test_item13_strength_follows_highest_qualifying_rung(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("the gate-level proposed_strength follows the highest-qualifying-rung authority under the item-06 tgt07_specific_aggregation_truth_table", checks)
        self.assertIn("indirect_strong when the highest qualifying rung is a positive indirect_strong observation and no direct-rung observation exists", checks)
        self.assertIn("a proposal with proposed_strength == weak is a hard failure", checks)

    def test_item13_direct_never_synthesized_and_canonical_negative_narrow(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("direct is never synthesized across observations", checks)
        self.assertIn("a proposal that does so is a hard failure", checks)
        self.assertIn("a canonical negative / direct (no_material_soluble_sink) is only produced by a soluble_antigen_tmdd_analysis with exposure_scenario_class == intended_adc_exposure", checks)

    def test_item13_whole_run_reject_never_degraded_to_unknown(self):
        on_fail = _norm(self.item["13_machine_acceptance_criteria"]["on_failure"])
        self.assertIn("rejects the whole run -- it is never degraded to an accepted unknown", on_fail)
        self.assertIn("a direct rung synthesized across unrelated observations", on_fail)
        self.assertIn("a canonical negative / direct proposed without a qualified intended-adc no-material-sink tmdd", on_fail)
        self.assertIn("a local sink_exposure_context_id equal to the canonical context_id", on_fail)

    def test_item15_indirect_strong_only_and_experiment_required_are_narrow(self):
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        iso = _norm(i15["indirect_strong_only_completed_landscape"])
        self.assertIn("positive / indirect_strong (highest-qualifying-rung authority)", iso)
        self.assertIn("this is not inconclusive", iso)
        b = _norm(i15["weak_only_or_below_assay_limit_only_or_no_qualifying_evidence_completed_landscape"])
        self.assertIn("inconclusive / unknown, zero proposal evidence_refs", b)
        self.assertIn("experiment_required", b)
        e = _norm(i15["experiment_required"])
        self.assertIn("only when the enumerated public soluble-antigen source space is completed / exhausted", e)
        self.assertIn("do not auto-add experiment_required", e)

    def test_item16_completed_state_precedence(self):
        prec = _flatten(self.item["16_stop_rule"]["completed_state_precedence"])
        self.assertIn("a hard integrity problem -> reject the whole run", prec)
        self.assertIn("the mandatory public soluble-antigen search is incomplete -> inconclusive / unknown with zero evidence_refs", prec)
        self.assertIn("completion claims complete but the audit is invalid -> hard reject", prec)
        self.assertIn("is-only -> positive / indirect_strong", prec)
        self.assertIn("a direct-quality analysis with mixed_or_unresolved -> inconclusive / direct", prec)
        self.assertIn("an unresolved public path remains -> public_resolvable / currently_unresolvable, do not auto-add experiment_required", prec)

    def test_item16_no_global_cancellation_precondition(self):
        pf = _flatten(self.item["16_stop_rule"]["potential_fatal_trigger"])
        self.assertIn("there is no global cancellation precondition -- a positive / direct does not clear the fatal signal", pf)
        self.assertIn("only after the necessary soluble-antigen-search completeness is satisfied", pf)

    def test_item17_handoff_never_kills(self):
        i17 = self.item["17_downstream_consumer_and_handoff"]
        never = _flatten(i17["this_module_does_not"])
        self.assertIn("produce a candidate-level decision or kill", never)
        self.assertIn("synthesize a direct material-sink proof from unrelated observations", never)
        self.assertIn("decide therapeutic efficacy or the achievable adc dose", never)


class ScopingRulingRegressionTests(unittest.TestCase):
    """The 7 required tightenings from the ChatGPT AI审核方案 E15 pre-code scoping
    ruling, plus the E16 conceptual shape."""

    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())
        self.item = self.doc["acceptance_checklist"]
        self.i06 = self.item["06_direction_interpretation"]

    def test_seven_required_tightenings_are_frozen(self):
        rt = self.doc["seven_required_tightenings"]
        self.assertEqual(len(rt), 7)
        joined = _norm(" ".join(rt))
        self.assertIn("option a: positive indirect_strong propagates; exactly 6 legal direction x strength pairs; there is no negative / indirect_strong", joined)
        self.assertIn("a below-detection / below-quantitation-limit soluble-antigen quantitation is contextual", joined)
        self.assertIn("new closed circulating_soluble_target_status typed enum", joined)
        self.assertIn("a canonical negative / direct is produced only by a qualified soluble_antigen_tmdd_analysis with exposure_scenario_class == intended_adc_exposure", joined)
        self.assertIn("fatal does not use a tgt-06-style route a / route b convergence", joined)
        self.assertIn("clinical and tmdd are two alternative source paths, not two convergence routes", joined)
        self.assertIn("there is no mandatory reproducibility predicate for the single-observation clinical fatal path in v1", joined)
        self.assertNotIn("reproducibility_status == qualified gate", joined)
        self.assertIn("there is no global cancellation precondition", joined)
        self.assertIn("introduce a lightweight single-string sink_exposure_context_id", joined)
        self.assertIn("no tgt-06 declared_multi / identified_multi / third-state machinery and no set-projection helper", joined)
        self.assertIn("e16 must never semantic-parse prose to obtain direct or fatal authority", joined)
        self.assertIn("no qualifying_indirect_evidence_context_ids set", joined)
        self.assertIn("soluble_antigen_quantitation_search_complete is true iff both the crc-patient and the healthy-donor serum / plasma search subspaces are done", joined)

    def test_tightening_1_option_a_indirect_strong_propagates(self):
        self.assertIn("POSITIVE / INDIRECT_STRONG", list(self.i06["legal_direction_strength_pairs"]))
        impl = self.i06["indirect_strong_implication"]
        self.assertIn("does grant a gate-level positive / indirect_strong when no direct sink-exposure context exists", _norm(impl["quantified_crc_patient_circulating_soluble_target"]))
        self.assertIn("does grant positive / indirect_strong", _norm(impl["documented_sheddase_substrate_status"]))
        self.assertIn("does grant positive / indirect_strong", _norm(impl["validated_secreted_isoform"]))

    def test_tightening_2_below_detection_typed_enum(self):
        s = _norm(self.i06["upstream_qualified_factual_states"])
        for member in _CIRCULATING_SOLUBLE_TARGET_STATUS:
            self.assertIn(member.lower(), s)
        impl = _norm(self.i06["indirect_strong_implication"]["below_detection_or_quantitation_limit_soluble_antigen"])
        self.assertIn("a contextual factual observation only", impl)
        self.assertIn("is not a positive indirect_strong and is not a negative", impl)

    def test_tightening_4_fatal_two_source_paths_no_convergence(self):
        c = self.item["08_fatal_conditions"]["machine_detection_criteria"]
        self.assertIn("no_global_precondition", c)
        self.assertIn("no_convergence_requirement", c)
        self.assertIn("clinical_source_path", c)
        self.assertIn("tmdd_source_path", c)
        self.assertIn("two_source_paths_not_routes", c)
        self.assertNotIn("route_a_declared_multi_configuration_analysis", c)
        self.assertNotIn("route_b_independent_convergence", c)

    def test_tightening_5_no_multi_or_third_state_machinery(self):
        # TGT-07 uses a single-string sink_exposure_context_id -- none of the
        # TGT-06 declared_multi / three-state / set-projection structures exist as
        # contract keys, and the identity block says so explicitly.
        tt = self.i06["tgt07_specific_aggregation_truth_table"]
        self.assertIn("sink_exposure_context_identity", tt)
        self.assertNotIn("configuration_identity_projection", tt)
        self.assertNotIn("configuration_identity_single_vs_multi", self.i06)
        self.assertNotIn("declared_multi_configuration_analysis", _flatten(self.i06["upstream_qualified_factual_states"]))
        ident = _norm(tt["sink_exposure_context_identity"])
        self.assertIn("there is deliberately no declared_multi analysis, no identified_multi state", ident)
        self.assertIn("no identity_not_disclosed_or_not_applicable state and no set-projection helper", ident)

    def test_e16_conceptual_shape_observation_kinds(self):
        d = DRAWING.read_text()
        for kind in _OBSERVATION_KINDS:
            self.assertIn(kind, d)

    def test_e16_sink_materiality_outcome_enum(self):
        d = DRAWING.read_text()
        for member in _SINK_MATERIALITY_OUTCOMES:
            self.assertIn(member, d)
        note = _norm(self.i06["tgt07_specific_aggregation_truth_table"]["note"])
        self.assertIn("material_soluble_sink_with_clinical_exposure_compromise", note)

    def test_e16_circulating_soluble_target_status_enum(self):
        d = DRAWING.read_text()
        for member in _CIRCULATING_SOLUBLE_TARGET_STATUS:
            self.assertIn(member, d)


class ContractIsFrozenAndDeferredToPrE16Tests(unittest.TestCase):
    """The E15 construction contract is design-only. The implementation it
    defers is built by PR E16 -- the eighth and final primary Module -- which
    also lifts MIGRATION_PENDING. Until then MOD-TGT07 stays 0.0.0 and there is
    no gate_modules/tgt07.../ package."""

    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation_and_registry_changes_in_the_e15_pr(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["trial_or_dataset_retrieval_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_or_ranking_scoring"], "forbidden")
        self.assertEqual(p["soluble_antigen_concentration_or_turnover_or_affinity_or_dose_exposure_or_sink_ratio_threshold"], "forbidden")
        self.assertEqual(p["invented_material_soluble_antigen_sink_concentration_range"], "forbidden")
        self.assertEqual(p["generic_gatemodule_framework_or_base_class_in_this_pr"], "forbidden")
        for g in ("tgt01", "tgt02", "tgt03", "tgt04", "tgt05", "tgt06", "tgt08"):
            self.assertEqual(p[f"modifies_mod_{g}"], "forbidden")
        self.assertEqual(p["modifies_binding_or_registry_or_existing_tests"], "forbidden")
        self.assertEqual(p["only_allowed_existing_file_mutation"], "append_to_logs_worklog_md")
        self.assertEqual(p["migration_pending"], "remains")

    def test_tgt07_implementation_package_does_not_exist_yet(self):
        pkg = ROOT / "gate_modules" / "tgt07_shedding_soluble_antigen_sink_liability"
        self.assertFalse(pkg.exists(), "PR E15 ships no implementation package; PR E16 builds it")

    def test_tgt07_binding_is_still_unbuilt_and_others_are_one_zero_zero(self):
        gs = yaml.safe_load(CRC_GATESET.read_text())
        by_gate = {
            b["gate_id"]: b["primary_module_version"]
            for b in gs["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(by_gate["TGT-07"], "0.0.0")
        for g in ("TGT-01", "TGT-02", "TGT-03", "TGT-04", "TGT-05", "TGT-06", "TGT-08"):
            self.assertEqual(by_gate[g], "1.0.0")

    def test_migration_pending_still_remains(self):
        gs = yaml.safe_load(CRC_GATESET.read_text())
        self.assertIn("per_gate_primary_modules", gs["migration"]["deferred"])

    def test_deferred_block_names_the_e16_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e16_plus"]).lower()
        self.assertIn("gate_modules/tgt07_shedding_soluble_antigen_sink_liability/", joined)
        self.assertIn("solubleantigenevidencecompletion", joined)
        self.assertIn("1.0.0", joined)
        self.assertIn("binding / registry reconciliation", joined)
        self.assertIn("lifting migration_pending", joined)

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


class DrawingTests(unittest.TestCase):
    def setUp(self):
        self.text = DRAWING.read_text()

    def test_drawing_exists_and_names_the_module_and_pr(self):
        self.assertIn("MOD-TGT07", self.text)
        self.assertIn("PR E15", self.text)
        self.assertIn("Shedding / Soluble-Antigen / Sink Liability", self.text)

    def test_drawing_covers_all_seventeen_items(self):
        for n in range(1, 18):
            self.assertRegex(self.text, rf"\|\s*{n}\s*\|\s*\*\*", f"drawing row {n} missing")

    def test_drawing_has_the_three_headline_blockquotes(self):
        self.assertIn("A measurable soluble form is not the same thing as a material antigen", self.text)
        self.assertIn("Soluble-antigen materiality is exposure-context dependent", self.text)
        self.assertIn("The TGT-07 potential-fatal signal is a strict subset of POSITIVE /", self.text)

    def test_drawing_freezes_the_key_rulings(self):
        t = self.text
        norm = " ".join(t.split()).lower()
        self.assertIn("highest-qualifying-rung grading authority", norm)
        self.assertIn("Legal Direction × Strength pairs (exactly 6)", t)
        self.assertIn("existence-proof dominance", norm)
        self.assertIn("no cross-observation synthesis of direct", norm)
        self.assertIn("no `qualifying_indirect_evidence_context_ids`", norm)
        self.assertIn("one fatal predicate, two admissible source paths", norm)
        self.assertIn("no global cancellation precondition", norm)

    def test_drawing_states_no_binding_or_registry_or_test_change(self):
        norm = " ".join(self.text.split()).lower()
        self.assertIn("append to `logs/worklog.md`", norm)
        self.assertIn("does not touch it, the binding, the registry or any existing test", norm)


class ReviewRound1RegressionTests(unittest.TestCase):
    """PR E15 ChatGPT AI审核方案 review round 1 -- 1 narrow blocker.

    The clinical fatal source path had wrongly added a mandatory
    `reproducibility_status == QUALIFIED` predicate (propagated into item 08 /
    item 12 / item 13 / seven_required_tightenings / manifest E15-4 / the tests),
    contradicting the pre-code ruling that the PR D fatal condition is a singular
    authority. FIX: the single-observation clinical fatal path has NO mandatory
    reproducibility predicate in v1; `reproducibility_status` /
    `reproducibility_basis` stay as OPTIONAL factual metadata -- carried, shown
    to the human reviewer, never a fatal or machine-acceptance gate.
    """

    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())
        self.item = self.doc["acceptance_checklist"]
        self.i06 = self.item["06_direction_interpretation"]
        self.mdc = self.item["08_fatal_conditions"]["machine_detection_criteria"]
        self.drawing = DRAWING.read_text()

    def test_clinical_fatal_path_has_no_mandatory_reproducibility_gate(self):
        clinical = _flatten(self.mdc["clinical_source_path"])
        self.assertNotIn("reproducibility_status == qualified with an auditable reproducibility_basis", clinical)
        self.assertIn("reproducibility_status is not a prerequisite", clinical)
        self.assertIn("still fatal-eligible", clinical)
        two = _norm(self.mdc["two_source_paths_not_routes"])
        self.assertIn("no mandatory reproducibility predicate for the single-observation clinical fatal path in v1", two)
        self.assertIn("reproducibility_status is optional factual metadata, never a fatal or machine-acceptance gate", two)

    def test_item12_required_iff_and_item13_drop_the_reproducibility_predicate(self):
        r12 = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["required_is_true_iff"])
        self.assertNotIn("reproducibility_status == qualified + basis", r12)
        self.assertIn("no mandatory reproducibility predicate for the single-observation clinical fatal path", r12)
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        # the clinical fatal check enumeration no longer contains the reproducibility predicate
        self.assertNotIn("analysis_validation_status == qualified + reproducibility_status == qualified", checks)
        self.assertIn("no mandatory reproducibility predicate for the single-observation clinical fatal path", checks)

    def test_reproducibility_status_is_optional_factual_metadata(self):
        s = _norm(self.i06["upstream_qualified_factual_states"])
        self.assertIn("reproducibility_status in {qualified, not_established} + reproducibility_basis is optional factual metadata only", s)
        self.assertIn("never a mandatory fatal or machine-acceptance predicate", s)
        # item 13 basis list no longer treats it as a classification-driving HARD basis
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("reproducibility_status is not a classification-driving status", checks)
        # drawing conceptual shape says the same
        norm_d = " ".join(self.drawing.split()).lower()
        self.assertIn("optional factual metadata only", norm_d)

    def test_other_clinical_qualifiers_still_gate_fatal(self):
        clinical = _flatten(self.mdc["clinical_source_path"])
        self.assertIn("same_target_therapeutic_match_status == qualified", clinical)
        self.assertIn("soluble_antigen_attribution_status == qualified", clinical)
        self.assertIn("analysis_validation_status == qualified", clinical)
        excl = _flatten(self.item["08_fatal_conditions"]["explicitly_excluded_from_a_fatal_trigger"])
        self.assertIn("a same-target therapeutic with an abnormal pk that is not qualified-attributable to soluble antigen", excl)

    def test_tightening_4_no_reproducibility_gate_wording(self):
        rt4 = _norm(self.doc["seven_required_tightenings"][3])
        self.assertIn("there is no mandatory reproducibility predicate for the single-observation clinical fatal path in v1", rt4)
        self.assertNotIn("reproducibility_status == qualified gate", rt4)
        self.assertIn("a reproducibility_status == not_established clinical observation that meets every other clause is still fatal-eligible", rt4)


if __name__ == "__main__":
    unittest.main()
