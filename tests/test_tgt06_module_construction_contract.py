"""Runtime Migration PR E13: the MOD-TGT06 construction contract.

Asserts:
* the 17-item acceptance checklist is present, complete and ordered (template
  reused from the approved PR E1 template);
* items 03 / 05 / 07 / 08 are a normalized-equality parity with the FROZEN PR D
  TGT-06 contract (crc_adc_target_gateset.yaml), item 04 is an EXACT derived
  parity (set equality, not a superset) against evidence_required + the ladder,
  and -- confirmed by the ChatGPT AI审核方案 E13-2 ruling -- the frozen PR D TGT-06
  contract has NO inference_guard field (EVGAP-01 is a TGT-04 construct only);
* TGT-06 is frozen as an EXISTENCE-PROOF, configuration-dependent gate with a
  HIGHEST-QUALIFYING-RUNG grading authority (the TGT-03 precedent), NOT the
  TGT-04 single-tier exception: a qualifying INDIRECT_STRONG addressability
  landscape with no DIRECT is POSITIVE / INDIRECT_STRONG, and the only legal
  Direction x Strength pairs are exactly SIX -- POSITIVE/DIRECT,
  POSITIVE/INDIRECT_STRONG, NEGATIVE/DIRECT, CONFLICTING/DIRECT,
  INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN;
* the ChatGPT AI审核方案 E13 scoping ruling is frozen: (E13-3) Option A -- IS
  propagates to POSITIVE / INDIRECT_STRONG; six legal pairs; a single
  DIRECT-quality failure configuration is INCONCLUSIVE / DIRECT, never NEGATIVE;
  a target-wide NEGATIVE / fatal needs multiple independent configurations;
  (E13-4) fatal Route A OR Route B, Route A itself must be a declared
  multi-configuration analysis, WELL_MATCHED_CRC_MODEL IS an eligible fatal
  contributor (unlike TGT-04), and any qualifying productive DIRECT existence
  proof cancels the target-wide surface-static machine fatal trigger; (E13-5)
  four renamed InternalizationEvidenceCompletion search axes and ONLY a
  qualifying_direct_configuration_ids set (no qualifying_indirect set); (E13-8)
  eight observation kinds, a CLOSED internalization_outcome enum keeping
  "_OR_TRAFFICKING", a declared_multi_configuration_analysis single-vs-multi
  identity pattern, and NO dedicated raw-value reuse-parity branch;
* the 3 headline conclusions are frozen verbatim; a target-wide surface-static
  potential fatal pattern needs productive-internalization / trafficking failure
  across multiple independent qualified configurations AND no qualifying
  productive DIRECT existence proof, and is surfaced at most as a machine-local
  fatal_review = POTENTIAL_FATAL_PATTERN;
* surface-localization-only / receptor-family-membership inference never above
  WEAK; a non-CRC internalization observation / a constitutive-endocytosis
  biology observation / a successful same-target ADC precedent never above
  INDIRECT_STRONG; DIRECT is an EXISTENCE PROOF that is never synthesized across
  unrelated observations or configurations;
* items 10-17 inherit the E2 / E4 / E6 / E8 / E10 / E12 runtime genes (an
  explicitly qualified disease-relevant context for a rung; the local
  internalization_configuration_id namespace separate from the canonical
  context_id; every qualified factual state carries an auditable basis; a CLOSED
  assay_validation_status enum + a non-empty factual assay_method for DIRECT; a
  kind / fact-specific non-inflated study_context);
* PR E13 ships no implementation -- no gate_modules/tgt06.../ directory, no
  provider / adapter / retrieval / runner, no numeric / ranking score, no
  internalization-rate cutoff or invented range, no generic GateModule
  framework; MOD-TGT06 primary_module_version stays "0.0.0"; the binding, the
  registry and every existing test are untouched (the only allowed existing-file
  mutation is an append to logs/worklog.md); MIGRATION_PENDING remains;
* the human-readable drawing exists and covers all 17 items.
"""

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "contracts" / "gate_modules" / "tgt06_internalization_trafficking_addressability.yaml"
DRAWING = ROOT / "docs" / "gate_modules" / "TGT-06_Internalization_Trafficking_Addressability.md"
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
        self.assertEqual(m["pr"], "runtime_migration_pr_e13")
        self.assertEqual(
            m["scope"],
            "tgt06_mod_tgt06_construction_contract_drawing_validation_and_acceptance_checklist_only",
        )
        self.assertIn("no implementation", m["boundary"].lower())
        self.assertIn("runtime_migration_pr_e14", m["next"])
        self.assertIn("TGT-04 -> TGT-06 -> TGT-07", m["order"])

    def test_template_provenance_reuses_the_e1_template(self):
        tp = self.doc["template_provenance"]
        self.assertEqual(tp["status"], "RECONSTRUCTED")
        self.assertTrue(tp["claim"]["not_claimed_verbatim_from_blueprint"])
        self.assertTrue(tp["claim"]["seventeen_item_template_reused_from_e1"])
        self.assertIn("e1 17-item construction template", tp["template_basis"].lower())
        self.assertTrue(E1_CONTRACT.is_file())

    def test_kernel_invariant_existence_proof_but_not_a_kill(self):
        inv = _norm(self.doc["kernel_invariant"])
        self.assertIn("src/ must never import gate_modules/", inv)
        self.assertIn("the gate_question is the internalization-and-trafficking-addressability", inv)
        self.assertIn("a direct rung is an existence proof", inv)
        self.assertIn("a single non-internalizing configuration is forbidden", inv)
        self.assertIn("does propagate to a gate-level strength", inv)
        self.assertIn("this is the highest-qualifying-rung grading authority, not the tgt-04 single-tier exception", inv)
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
        self.assertIn("internalization is configuration-specific, not a target-intrinsic constant", joined)
        self.assertIn("one qualifying disease-relevant antibody / epitope configuration", joined)
        self.assertIn("failure of one configuration is only configuration-level opposing evidence and can never establish target-wide non-internalization", joined)
        self.assertIn("direct productive-addressability authority requires an auditable integrated observation", joined)
        self.assertIn("may not be combined across unrelated observations or configurations to synthesize direct", joined)
        self.assertIn("a target-wide surface-static potential fatal pattern requires productive-internalization / trafficking failure across multiple independent qualified antibody / epitope configurations", joined)
        self.assertIn("the machine may surface only potential_fatal_pattern", joined)
        self.assertIn("it never decides fatality, adc efficacy, kill, hold or a candidate-level decision", joined)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item01_gate_identity(self):
        i = self.item["01_gate_identity_and_version"]
        self.assertEqual(i["gate_id"], "TGT-06")
        self.assertEqual(i["gate_version"], "1.0")
        self.assertEqual(i["gate_name"], "Internalization / Trafficking Addressability")
        self.assertEqual(i["canonical_gateset_id"], "ADC_TARGET_GATESET")
        self.assertEqual(i["gateset_version"], "1.0")
        self.assertEqual(i["candidate_level"], "L04")
        self.assertEqual(i["instantiation_binding"], "INST-CRC-REFRACTORY-ADC-TARGET-v1")

    def test_item02_module_identity_declared_not_built(self):
        i = self.item["02_primary_module_identity_and_version"]
        self.assertEqual(i["primary_module_id"], "MOD-TGT06")
        self.assertEqual(i["module_implementation_version"], "0.0.0")
        self.assertIn("pr e14 builds it", _norm(i["rule"]))


class VerbatimFromPrDTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.tgt06 = yaml.safe_load(CRC_GATESET.read_text())["gate_contracts"]["TGT-06"]

    def test_item03_gate_question_parity(self):
        self.assertEqual(
            _norm(self.item["03_gate_question"]["text"]),
            _norm(self.tgt06["gate_question"]),
        )

    def test_item05_evidence_ladder_parity(self):
        i = self.item["05_evidence_ladder_and_evidence_ceiling"]
        self.assertEqual(_norm(i["evidence_ceiling"]), _norm(self.tgt06["evidence_ceiling"]))
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            self.assertEqual(
                [_norm(x) for x in i[grade]["admissible_evidence_classes"]],
                [_norm(x) for x in self.tgt06["evidence_ladder"][grade]["admissible_evidence_classes"]],
            )
            self.assertEqual(
                _norm(i[grade]["ceiling_rule"]),
                _norm(self.tgt06["evidence_ladder"][grade]["ceiling_rule"]),
            )

    def test_item07_inference_parity(self):
        i = self.item["07_allowed_and_forbidden_inference"]
        self.assertEqual(
            [_norm(x) for x in i["allowed"]],
            [_norm(x) for x in self.tgt06["allowed_inference"]],
        )
        self.assertEqual(
            [_norm(x) for x in i["forbidden"]],
            [_norm(x) for x in self.tgt06["forbidden_inference"]],
        )

    def test_tgt06_has_no_inference_guard_field(self):
        # E13-2 ruling: the frozen PR D TGT-06 contract has NO inference_guard.
        self.assertNotIn("inference_guard", self.tgt06)
        i07 = self.item["07_allowed_and_forbidden_inference"]
        self.assertNotIn("inference_guard", i07)
        self.assertIn("has no inference_guard field", _norm(i07["no_inference_guard_field"]))
        self.assertIn("the evgap-01 surface-localization lock is a tgt-04 construct only", _norm(i07["no_inference_guard_field"]))

    def test_item08_fatal_conditions_parity(self):
        self.assertEqual(
            [_norm(x) for x in self.item["08_fatal_conditions"]["potential_fatal_signal"]],
            [_norm(x) for x in self.tgt06["fatal_conditions"]],
        )

    def test_item08_potential_fatal_signal_is_verbatim_pr_d_only(self):
        sig = self.item["08_fatal_conditions"]["potential_fatal_signal"]
        self.assertEqual(len(sig), 1)
        self.assertEqual(_norm(sig[0]), _norm(self.tgt06["fatal_conditions"][0]))

    def test_item04_derived_parity_is_exact_not_a_superset(self):
        item04 = self.item["04_admissible_evidence_classes"]
        got = set(_norm(x) for x in item04["admissible"])
        want = set(_norm(x) for x in self.tgt06["evidence_required"])
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            want |= set(_norm(x) for x in self.tgt06["evidence_ladder"][grade]["admissible_evidence_classes"])
        self.assertEqual(got, want)

    def test_item04_excludes_the_other_seven_gates_and_a_universal_range(self):
        na = _norm(" ".join(self.item["04_admissible_evidence_classes"]["not_admissible_into_this_gate"]))
        for tok in ("tgt-01", "tgt-02", "tgt-03", "tgt-04", "tgt-05", "tgt-07", "tgt-08"):
            self.assertIn(tok, na)
        self.assertIn("adc-effective internalization rate", na)

    def test_pr_d_unknown_behavior_is_no_data_for_any_configuration_to_unknown(self):
        self.assertIn(
            "no internalization data for any configuration",
            _norm(self.tgt06["unknown_behavior"]),
        )
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        self.assertIn(
            "no internalization data for any configuration -> unknown",
            _norm(i15["weak_only_or_no_qualifying_evidence_completed_landscape"]),
        )


class ExistenceProofAndHighestRungGradingTests(unittest.TestCase):
    def setUp(self):
        self.i06 = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]["06_direction_interpretation"]

    def test_highest_qualifying_rung_not_single_tier(self):
        t = _norm(self.i06["highest_qualifying_rung_grading_authority"])
        self.assertIn("highest-qualifying-rung grading authority (the tgt-03 precedent), not the tgt-04 single-tier exception", t)
        self.assertIn("positive / indirect_strong", t)
        self.assertIn('locks unknown only to "no internalization data for any configuration"', t)

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
        no = _norm(self.i06["no_other_pairs"])
        self.assertIn("exactly six legal direction x strength pairs", no)
        self.assertIn("no negative / indirect_strong", no)
        self.assertIn("no conflicting / indirect_strong", no)
        self.assertIn("no inconclusive / indirect_strong", no)
        self.assertIn("no inconclusive / weak", no)

    def test_aggregation_truth_table(self):
        tt = self.i06["tgt06_specific_aggregation_truth_table"]
        self.assertIn("positive / direct", _norm(tt["completed_and_at_least_one_clean_productive_direct_configuration"]))
        self.assertIn("positive / indirect_strong", _norm(tt["completed_and_no_direct_rung_observation_and_at_least_one_qualifying_positive_indirect_strong"]))
        one_fail = _norm(tt["completed_and_no_productive_direct_and_exactly_one_independent_direct_quality_failure_configuration"])
        self.assertIn("inconclusive / direct", one_fail)
        self.assertIn("a single non-internalizing configuration never establishes target-wide non-internalization", one_fail)
        two_fail = _norm(tt["completed_and_no_productive_direct_and_at_least_two_independent_direct_quality_failure_configurations"])
        self.assertIn("negative / direct", two_fail)
        self.assertIn("conflicting / direct", _norm(tt["completed_and_no_clean_productive_direct_and_a_configuration_identity_carries_both_a_productive_direct_and_a_direct_quality_failure_observation"]))
        self.assertIn("inconclusive / unknown", _norm(tt["completed_and_weak_only_or_no_qualifying_evidence"]))
        # PR E13 review round-1 gene: a frozen ordered evaluation
        order = _norm(tt["frozen_evaluation_order"])
        self.assertIn("stops at the first match", order)
        self.assertIn("if at least one clean / uncontested productive direct configuration exists -> positive / direct", order)
        self.assertIn("a conflicted configuration a plus a clean productive configuration b is still positive / direct", order)
        # PR E13 review round-2 gene: one frozen projection helper
        proj = _norm(tt["configuration_identity_projection"])
        self.assertIn("single -> {internalization_configuration_id}", proj)
        self.assertIn("identified_multi -> set(internalization_configuration_ids)", proj)
        self.assertIn("identity_not_disclosed_or_not_applicable -> {} (the empty set)", proj)

    def test_existence_proof_dominance(self):
        d = _norm(self.i06["existence_proof_dominance"])
        self.assertIn("a clean / uncontested positive existence proof dominates heterogeneous configuration failures and a conflicted configuration elsewhere", d)
        self.assertIn("the gate answer is positive / direct -- not negative and not automatically conflicting", d)
        self.assertIn("if configuration a is itself conflicted (it carries both a productive direct observation and a direct-quality failure observation) but a different configuration b is a clean productive direct configuration", d)
        self.assertIn("never reverse the target-level addressability conclusion", d)

    def test_different_configurations_differ_is_not_a_conflict(self):
        d = _norm(self.i06["different_configurations_differ_is_not_a_conflict"])
        self.assertIn("is not a conflicting signal", d)
        self.assertIn("this is a hard lock", d)
        self.assertIn("never map inter-configuration heterogeneity to conflicting", d)

    def test_inconclusive_direct_is_legal_and_distinct_from_unknown(self):
        d = _norm(self.i06["inconclusive_direct_is_legal"])
        self.assertIn("exactly one independent direct-quality failure configuration and no qualifying productive direct configuration", d)
        self.assertIn("distinct from inconclusive / unknown", d)
        self.assertIn("a single non-internalizing configuration is forbidden by pr d from being a target-wide negative", d)

    def test_no_cross_observation_synthesis_of_direct(self):
        s = _norm(self.i06["no_cross_observation_synthesis_of_direct"])
        self.assertIn("direct is never synthesized by the module from unrelated observations", s)
        self.assertIn("does not combine into a direct existence proof -- even for the same target", s)
        self.assertIn("one upstream-qualified integrated configuration observation", s)
        self.assertIn("mod-tgt06 itself never joins unrelated evidencepackages / configurations to assemble direct", s)

    def test_separate_typed_upstream_facts(self):
        s = _norm(self.i06["upstream_qualified_factual_states"])
        self.assertIn("must not overload one field to carry two meanings", s)
        self.assertIn("assay_validation_status", s)
        self.assertIn("qualified is not a positive addressability conclusion", s)
        self.assertIn("internalization_outcome", s)
        self.assertIn("never computed by the module from a number", s)
        self.assertIn("declared_multi_configuration_analysis", s)

    def test_internalization_direction_mapping(self):
        m = self.i06["internalization_direction_mapping"]
        self.assertEqual(_norm(m["internalization_outcome_productive_internalization_with_lysosomal_delivery"]), "supports_addressability")
        self.assertEqual(_norm(m["internalization_outcome_fails_productive_internalization_or_trafficking"]), "opposes_addressability")
        self.assertIn("nondirectional", _norm(m["internalization_outcome_mixed_or_unresolved_or_not_established"]))
        partial = _norm(m["internalization_observed_lysosomal_delivery_unresolved"])
        self.assertIn("indirect_strong ceiling only", partial)
        self.assertIn("never contributes an opposes_addressability direction", partial)

    def test_configuration_identity_single_vs_multi(self):
        c = _norm(self.i06["configuration_identity_single_vs_multi"])
        self.assertIn("one of exactly three frozen identity states", c)
        self.assertIn("(1) single --", c)
        self.assertIn("(2) identified_multi --", c)
        self.assertIn("(3) identity_not_disclosed_or_not_applicable --", c)
        self.assertIn("len(unique(internalization_configuration_ids)) >= 2", c)
        self.assertIn("any direct-quality observation", c)
        self.assertIn("must be single or identified_multi", c)
        self.assertIn("a direct-quality observation in the identity_not_disclosed_or_not_applicable state is a hard integrity failure", c)
        self.assertIn("never loses indirect_strong authority for being in the identity_not_disclosed_or_not_applicable state", c)
        self.assertIn('e14 must never assert "every qualifying indirect_strong observation has an internalization_configuration_id"', c)


class QuantitativeValuesAreEvidenceNotThresholdsTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_direct_is_an_existence_proof_not_an_efficiency_measurement(self):
        k = _norm(self.item["05_evidence_ladder_and_evidence_ceiling"]["direct_is_an_existence_proof_not_an_efficiency_measurement"])
        self.assertIn("the pr d direct class is an existence proof", k)
        self.assertIn("it is satisfied by one qualifying integrated configuration observation", k)
        self.assertIn("it does not require a quorum of configurations, a minimum internalization efficiency, or a minimum trafficking rate", k)
        self.assertIn("never crc_specific alone", k)

    def test_quantitative_values_are_evidence_not_thresholds(self):
        k = _norm(self.item["05_evidence_ladder_and_evidence_ceiling"]["quantitative_values_are_evidence_not_thresholds"])
        self.assertIn("may and should preserve a source-reported numeric assay fact when the source states one", k)
        self.assertIn('invented "adc-effective internalization rate" / "lysosomal colocalization cutoff"', k)
        self.assertIn("no tgt-04-style symmetric raw-value reuse-parity branch is needed", k)
        self.assertIn("the typed classification driver is internalization_outcome (a closed enum), never a number", k)

    def test_item09_no_universal_threshold(self):
        n = _norm(self.item["09_evidence_source_plan"]["no_universal_threshold"])
        self.assertIn("no internalization-rate cutoff", n)
        self.assertIn("no percent-internalized cutoff", n)
        self.assertIn('no invented "adc-effective internalization rate" range', n)
        self.assertIn("a source-reported numeric assay fact may be preserved as a factual measurement", n)

    def test_no_dedicated_raw_value_reuse_parity_branch(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("there is no dedicated typed raw numeric field for internalization and therefore no tgt-04-style symmetric raw-value reuse-parity branch", i11)

    def test_no_numeric_or_threshold_language_in_the_contract(self):
        # A bare source-reported number (e.g. "65% internalized at 4 h") is an
        # ADMISSIBLE factual measurement per the E13 ruling; what is forbidden is
        # a numeric DECISION / threshold construct.
        text = _norm(CONTRACT.read_text())
        self.assertIsNone(
            re.search(
                r"h-?score\s*[<>=]\s*\d|rate\s*[<>=]\s*\d|internalized\s*[<>=]\s*\d"
                r"|[<>=]\s*\d+\s*(percent|%|cells|molecules|configurations|contexts|cohorts)"
                r"|\d+\s*%\s*(cutoff|threshold|effective)|\bnumeric_score\s*="
                r"|if\s+\w+\s*[<>=]",
                text,
            )
        )
        self.assertIn("no internalization-rate cutoff", text)
        self.assertIn('not "more than two" / "> 2" / ">= 3"', text)


class FatalReviewAndProposalTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item08_global_precondition_no_productive_direct(self):
        gp = _norm(self.item["08_fatal_conditions"]["machine_detection_criteria"]["global_precondition"])
        self.assertIn("no qualifying productive direct configuration exists on the completed audited landscape", gp)
        self.assertIn("cancels the target-wide surface-static machine fatal trigger", gp)
        self.assertIn("this is a hard lock", gp)

    def test_item08_route_a_and_route_b_both_multi_configuration(self):
        crit = self.item["08_fatal_conditions"]["machine_detection_criteria"]
        self.assertIn("route_a_declared_multi_configuration_analysis", crit)
        self.assertIn("route_b_independent_convergence", crit)
        a = _norm(crit["route_a_declared_multi_configuration_analysis"])
        self.assertIn("that itself explicitly covers multiple independent antibody / epitope configurations", a)
        self.assertIn("declared_multi_configuration_analysis == true", a)
        self.assertIn("len(unique(internalization_configuration_ids)) >= 2", a)
        self.assertIn("does not satisfy route a", a)
        self.assertIn("bypass the frozen pr d", a)
        b = _norm(crit["route_b_independent_convergence"])
        self.assertIn("at least two distinct eligible direct-quality failure observations", b)
        self.assertIn("a single identified_multi observation, regardless of its projection cardinality, does not satisfy route b", b)
        self.assertIn('not "more than two" / "> 2" / ">= 3"', b)

    def test_item08_well_matched_model_is_an_eligible_fatal_contributor(self):
        crit = _flatten(self.item["08_fatal_conditions"]["machine_detection_criteria"]["each_contributing_observation_must_be"])
        self.assertIn("surface_context_class in {crc_malignant_cells, well_matched_crc_model}", crit)
        self.assertIn("unlike the tgt-04 fatal path, a qualified well_matched_crc_model context is eligible here", crit)
        self.assertIn("internalization_outcome == fails_productive_internalization_or_trafficking", crit)

    def test_item08_single_configuration_failure_is_excluded(self):
        excl = _flatten(self.item["08_fatal_conditions"]["explicitly_excluded_from_a_fatal_trigger"])
        self.assertIn("a single antibody / epitope configuration's productive-internalization failure", excl)
        self.assertIn("any landscape on which a qualifying productive direct configuration exists", excl)
        self.assertIn("non-internalizing-payload strategies -- they are outside this gate's fatal call", excl)

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
        self.assertIn('any internalization-rate threshold, cutoff or "adc-effective internalization rate range"', never)

    def test_item12_fatal_review_fields(self):
        fr = self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]
        fields = _norm(" ".join(fr["fields"]))
        self.assertIn("configuration_ids", fields)
        self.assertIn("internalization_outcome_class", fields)
        self.assertIn("assay_validation_basis_refs", fields)
        self.assertIn("reproducibility_basis_refs", fields)
        self.assertEqual(fr["machine_may_emit"], "POTENTIAL_FATAL_PATTERN")
        self.assertIn("public_fatal_signal_established", _norm(fr["machine_never_emits"]))
        r = _norm(fr["required_is_true_iff"])
        self.assertIn("no qualifying productive direct configuration exists", r)
        self.assertIn("route a", r)
        self.assertIn("route b", r)
        self.assertIn("a qualified well-matched crc model is eligible here, unlike tgt-04", r)
        self.assertIn("a single antibody / epitope configuration's failure -- even with reproducibility_status == qualified -- gives required = false", r)
        self.assertIn("a single identified_multi observation, regardless of its projection cardinality, does not satisfy route b", r)

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
        pl = self.i09["internalization_search_landscape"]
        comps = [_norm(x) for x in pl["declared_mandatory_search_components"]]
        self.assertEqual(len(comps), 4)
        self.assertTrue(any("antibody-induced internalization search" in c for c in comps))
        self.assertTrue(any("productive trafficking search" in c for c in comps))
        self.assertTrue(any("same-target adc functional-delivery precedent search" in c for c in comps))
        self.assertTrue(any("receptor endocytosis and inference search" in c for c in comps))
        m = _norm(pl["mandatory_is_search_completion_axes_not_evidence_prerequisites"])
        self.assertIn("not evidence prerequisites and not grading axes", m)
        self.assertIn("searched / exhausted with zero qualifying records still counts as complete", m)
        self.assertIn("public_internalization_search_complete", m)

    def test_typed_completion_is_named_and_has_only_a_direct_configuration_set(self):
        tc = _norm(self.i09["internalization_search_landscape"]["typed_completion_record"])
        self.assertIn("internalizationevidencecompletion", tc)
        self.assertIn("not a seventh core object", tc)
        self.assertIn("there is exactly one qualifying configuration set -- qualifying_direct_configuration_ids", tc)
        self.assertIn("there is deliberately no qualifying_indirect_configuration_ids set", tc)
        self.assertIn("the snapshot field names are the typed completion field names", tc)
        self.assertIn("a drift in the qualifying configuration set, -> hard reject", tc)

    def test_source_authority_hard_locks(self):
        rules = _norm(" ".join(self.i09["source_authority_rules"]))
        self.assertIn("surface localization alone never establishes internalization", rules)
        self.assertIn("receptor-family membership never establishes internalization -- weak only", rules)
        self.assertIn("a non-crc antibody-induced internalization observation is indirect_strong ceiling -- never direct", rules)
        self.assertIn("it does grant positive / indirect_strong", rules)
        self.assertIn("a functional adc delivery precedent must be a genuinely successful same-target adc", rules)
        self.assertIn('"a same-target adc exists / had a program" (tgt-01 territory) is not a tgt-06 delivery precedent', rules)
        self.assertIn("configuration a internalizes\" + \"configuration b reaches the lysosome\" from different observations never synthesize direct", rules)
        self.assertIn("antibody-induced internalization observed but lysosomal delivery not confirmed", rules)
        self.assertIn("there is no qualifying_indirect_configuration_ids set", rules)
        self.assertIn("never from crc_specific alone", rules)


class RuntimeGeneInheritanceTests(unittest.TestCase):
    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]

    def test_item10_fixed_instantiation_context_is_hard_pinned(self):
        i10 = _flatten(self.item["10_input_contract"])
        self.assertIn("ctx-crc-refractory-mcrc", i10)
        self.assertIn("a separate namespace from each observation's local internalization_configuration_id", i10)
        self.assertIn("every observation.context_key equals the run's context_key", i10)
        self.assertIn("internalizationevidencecompletion.search_scope equals the run's declared internalization_search_scope", i10)

    def test_item11_exact_reuse_dedup_and_namespace(self):
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("observation_id is part of the exact-reuse identity parity", i11)
        self.assertIn("including internalization_outcome for an integrated / failure observation", i11)
        self.assertIn("reused ep's own provenance source_type / source_identifier / locator must still equal the resolved canonical sourceindex record", i11)
        self.assertIn("dedup uses the improved tgt-03 rule", i11)
        self.assertIn("both observations survive", i11)
        self.assertIn("a search_completion_audit ep is never a dedup loser", i11)
        self.assertIn("internalization_configuration_id / internalization_configuration_ids is a local evidence-context identity namespace", i11)
        self.assertIn("never collapse an internalization_configuration_id onto the canonical context_id", i11)
        self.assertIn("kind / fact-specific study_context", i11)
        self.assertIn("antibody_identity / epitope_identity_or_region / affinity_context / conjugation_context are open factual strings -- not all four are required", i11)

    def test_item13_runtime_genes(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        # explicitly qualified disease-relevant context for a rung
        self.assertIn("a direct rung requires an explicitly qualified disease-relevant context", checks)
        self.assertIn("a bare crc_specific == true never reaches a rung", checks)
        # local configuration namespace never the canonical context_id
        self.assertIn("the local configuration namespace", checks)
        self.assertIn("collapses an internalization_configuration_id onto the canonical context_id is a hard identity-namespace failure", checks)
        # single-vs-multi identity consistency (three frozen states)
        self.assertIn("the configuration identity is exactly one of the three frozen states", checks)
        self.assertIn("identity_not_disclosed_or_not_applicable is permitted only for a non-direct-quality observation kind", checks)
        self.assertIn("any direct-quality observation (productive direct or direct-quality failure) in the identity_not_disclosed_or_not_applicable state is a hard integrity failure", checks)
        # every qualified status carries an auditable basis
        self.assertIn("every classification-driving qualified status carries an auditable basis", checks)
        # closed validation enum + non-empty assay_method for DIRECT
        self.assertIn("assay_validation_status is in {qualified, not_established}", checks)
        self.assertIn("a non-empty factual assay_method", checks)
        # kind / fact-specific non-inflated study_context is item 11
        i11 = _flatten(self.item["11_evidencepackage_output_contract"])
        self.assertIn("never promote a non-crc / receptor-family-inference / surface-localization-only / audit observation's source study context", i11)

    def test_item13_strength_follows_highest_qualifying_rung(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("the gate-level proposed_strength follows the highest-qualifying-rung authority under the item-06 tgt06_specific_aggregation_truth_table", checks)
        self.assertIn("indirect_strong when the highest qualifying rung is a positive indirect_strong observation and no direct-rung observation exists", checks)
        self.assertIn("a proposal with proposed_strength == weak is a hard failure", checks)

    def test_item13_direct_never_synthesized_across_observations(self):
        checks = _flatten(self.item["13_machine_acceptance_criteria"]["a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"])
        self.assertIn("direct is never synthesized across observations", checks)
        self.assertIn("does not combine into a direct existence proof", checks)
        self.assertIn("a proposal that does so is a hard failure", checks)

    def test_item13_whole_run_reject_never_degraded_to_unknown(self):
        on_fail = _norm(self.item["13_machine_acceptance_criteria"]["on_failure"])
        self.assertIn("rejects the whole run -- it is never degraded to an accepted unknown", on_fail)
        self.assertIn("a direct rung synthesized across unrelated observations", on_fail)
        self.assertIn("a declared_multi_configuration_analysis / configuration id inconsistency", on_fail)
        self.assertIn("a local internalization_configuration_id equal to the canonical context_id", on_fail)
        self.assertIn("a direct rung asserted on a non_crc_context / unresolved context", on_fail)

    def test_item15_indirect_strong_only_and_experiment_required_are_narrow(self):
        i15 = self.item["15_failure_unknown_and_conflict_behavior"]
        iso = _norm(i15["indirect_strong_only_completed_landscape"])
        self.assertIn("positive / indirect_strong (highest-qualifying-rung authority)", iso)
        self.assertIn("this is not inconclusive", iso)
        sf = _norm(i15["single_failure_is_never_a_target_wide_negative"])
        self.assertIn("inconclusive / direct, never negative", sf)
        self.assertIn("is forbidden", sf)
        e = _norm(i15["experiment_required"])
        self.assertIn("only when the enumerated public internalization source space is completed / exhausted", e)
        self.assertIn("across additional independent antibody / epitope configurations", e)
        self.assertIn("do not auto-add experiment_required", e)

    def test_item16_stop_rule_never_stops_on_first_failure_observation(self):
        i16 = self.item["16_stop_rule"]
        pf = _norm(" ".join(i16["potential_fatal_trigger"]))
        self.assertIn("the module never stops on the first configuration-failure observation", pf)
        self.assertIn("only after the necessary internalization-search completeness is satisfied", pf)
        self.assertIn("only when no qualifying productive direct configuration exists", pf)

    def test_item17_handoff_never_kills_and_tgt06_never_discharges_tgt07(self):
        i17 = self.item["17_downstream_consumer_and_handoff"]
        never = _flatten(i17["this_module_does_not"])
        self.assertIn("produce a candidate-level decision or kill", never)
        self.assertIn("synthesize a direct existence proof from unrelated observations or configurations", never)
        self.assertIn("decide adc efficacy or adequate payload release", never)
        cons = _flatten(i17["once_human_approved_the_resulting_canonical_CandidateGateAssessment_is_consumed_by"])
        self.assertIn("tgt-06 never discharges tgt-07", cons)


class ScopingRulingRegressionTests(unittest.TestCase):
    """The 7 key freeze points from the ChatGPT AI审核方案 E13 pre-code scoping ruling."""

    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.i06 = self.item["06_direction_interpretation"]
        self.checks = _flatten(
            self.item["13_machine_acceptance_criteria"][
                "a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"
            ]
        )

    # ---- freeze point 1: Option A -------------------------------------------
    def test_option_a_indirect_strong_propagates_to_positive(self):
        self.assertIn("POSITIVE / INDIRECT_STRONG", [p for p in self.i06["legal_direction_strength_pairs"]])
        impl = self.i06["indirect_strong_implication"]
        self.assertIn("does grant a gate-level positive / indirect_strong when no direct configuration exists", _norm(impl["constitutive_endocytosis_or_internalizing_receptor_biology"]))
        self.assertIn("it does grant positive / indirect_strong", _norm(impl["non_crc_antibody_induced_internalization"]))
        self.assertIn("does grant positive / indirect_strong", _norm(impl["successful_same_target_adc_functional_delivery_precedent"]))

    # ---- freeze point 2: exactly six legal pairs --------------------------
    def test_exactly_six_legal_pairs(self):
        self.assertEqual(len(self.i06["legal_direction_strength_pairs"]), 6)

    # ---- freeze point 3: one DIRECT failure -> INCONCLUSIVE, not NEGATIVE --
    def test_one_direct_failure_is_inconclusive_not_negative(self):
        tt = self.i06["tgt06_specific_aggregation_truth_table"]
        row = _norm(tt["completed_and_no_productive_direct_and_exactly_one_independent_direct_quality_failure_configuration"])
        self.assertIn("inconclusive / direct", row)
        self.assertIn("pr d forbidden_inference", row)

    # ---- freeze point 4: NEGATIVE / fatal need multiple independent configs -
    def test_negative_and_fatal_need_multiple_independent_configurations(self):
        tt = _norm(self.i06["tgt06_specific_aggregation_truth_table"]["completed_and_no_productive_direct_and_at_least_two_independent_direct_quality_failure_configurations"])
        self.assertIn("negative / direct", tt)
        neg_def = _norm(self.i06["direction_definitions"]["NEGATIVE"])
        self.assertIn("at least two independent qualified antibody / epitope configurations", neg_def)
        self.assertIn("no qualifying productive direct configuration exists on the completed landscape", neg_def)

    # ---- freeze point 5: Route A must also be multi-configuration ---------
    def test_route_a_must_itself_be_multi_configuration(self):
        a = _norm(self.item["08_fatal_conditions"]["machine_detection_criteria"]["route_a_declared_multi_configuration_analysis"])
        self.assertIn("a single antibody / epitope configuration with reproducibility_status == qualified", a)
        self.assertIn("does not satisfy route a", a)
        self.assertIn('that would bypass the frozen pr d "multiple independent configurations"', a)

    # ---- freeze point 6: model can contribute fatal, but productive DIRECT cancels it
    def test_model_contributes_fatal_but_productive_direct_cancels_the_trigger(self):
        crit = _flatten(self.item["08_fatal_conditions"]["machine_detection_criteria"]["each_contributing_observation_must_be"])
        self.assertIn("a qualified well_matched_crc_model context is eligible here", crit)
        gp = _norm(self.item["08_fatal_conditions"]["machine_detection_criteria"]["global_precondition"])
        self.assertIn("any single qualifying direct observation whose internalization_outcome maps to supports_addressability cancels the target-wide surface-static machine fatal trigger", gp)
        self.assertIn("if the module-local fatal_review record has required = true", self.checks)
        self.assertIn("no qualifying productive direct configuration exists on the landscape", self.checks)

    # ---- freeze point 7: no qualifying_indirect_configuration_ids ---------
    def test_completion_has_no_indirect_configuration_set(self):
        tc = _norm(self.item["09_evidence_source_plan"]["internalization_search_landscape"]["typed_completion_record"])
        self.assertIn("there is deliberately no qualifying_indirect_configuration_ids set", tc)
        rules = _norm(" ".join(self.item["09_evidence_source_plan"]["source_authority_rules"]))
        self.assertIn("forcing one would rewrite the frozen indirect_strong evidence class", rules)

    # ---- E13-8: observation kinds + internalization_outcome enum ----------
    def test_e14_conceptual_shape_observation_kinds(self):
        d = DRAWING.read_text()
        for kind in (
            "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
            "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
            "TRAFFICKING_OR_RECYCLING_ONLY",
            "SAME_TARGET_ADC_DELIVERY_PRECEDENT",
            "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
            "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
            "SURFACE_LOCALIZATION_ONLY_INFERENCE",
            "SEARCH_COMPLETION_AUDIT",
        ):
            self.assertIn(kind, d)

    def test_e14_internalization_outcome_enum_keeps_or_trafficking(self):
        d = DRAWING.read_text()
        for member in (
            "PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY",
            "INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED",
            "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING",
            "MIXED_OR_UNRESOLVED",
            "NOT_ESTABLISHED",
        ):
            self.assertIn(member, d)
        i06 = _norm(self.i06["tgt06_specific_aggregation_truth_table"]["note"])
        self.assertIn("fails_productive_internalization_or_trafficking", i06)


class ReviewRound1RegressionTests(unittest.TestCase):
    """PR E13 ChatGPT AI审核方案 review round 1 -- the 4 narrow construction-contract
    blockers.

    (1) declared_multi_configuration_analysis identity shape was self-contradictory
        -- a constitutive-endocytosis / same-target-ADC-precedent / inference /
        audit / non-CRC-without-disclosed-config observation must be valid with NO
        configuration id. Now THREE frozen identity states, with
        IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE permitted only for a
        non-DIRECT-quality observation kind.
    (2) the aggregation truth table had no frozen evaluation ORDER -- now a
        stop-at-first-match ordered algorithm; a clean productive DIRECT
        configuration dominates a conflicted configuration elsewhere.
    (3) item 03 tgt06_framing.answers mis-wrote the whole Gate as a DIRECT
        existence-proof question -- now the Gate question is distinct from the
        DIRECT ceiling.
    (4) TRAFFICKING_OR_RECYCLING_ONLY was an observation kind with no failure /
        fatal authority -- now an ASYMMETRIC authority: positive at most
        INDIRECT_STRONG, negative a DIRECT-quality failure that participates in
        the truth table and Route A / Route B fatal.
    """

    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.i06 = self.item["06_direction_interpretation"]
        self.checks = _flatten(
            self.item["13_machine_acceptance_criteria"][
                "a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"
            ]
        )

    # ---- blocker 1 -------------------------------------------------------------
    def test_three_frozen_configuration_identity_states(self):
        c = _norm(self.i06["configuration_identity_single_vs_multi"])
        self.assertIn("(1) single -- declared_multi_configuration_analysis == false and internalization_configuration_id != \"\" and internalization_configuration_ids == () and configuration_identity_basis != \"\"", c)
        self.assertIn("(2) identified_multi -- declared_multi_configuration_analysis == true and internalization_configuration_id == \"\" and len(unique(internalization_configuration_ids)) >= 2 and configuration_identity_basis != \"\"", c)
        self.assertIn("(3) identity_not_disclosed_or_not_applicable -- declared_multi_configuration_analysis == false and internalization_configuration_id == \"\" and internalization_configuration_ids == ()", c)
        self.assertIn("permitted only for a non-direct-quality observation", c)
        self.assertIn("a constitutive_endocytosis_or_receptor_biology observation, a same_target_adc_delivery_precedent observation", c)
        self.assertIn("any direct-quality observation", c)
        self.assertIn("must be single or identified_multi", c)

    def test_receptor_biology_and_precedent_without_config_id_are_valid(self):
        c = _norm(self.i06["configuration_identity_single_vs_multi"])
        self.assertIn("a constitutive_endocytosis_or_receptor_biology / same_target_adc_delivery_precedent observation never loses indirect_strong authority for being in the identity_not_disclosed_or_not_applicable state", c)

    # ---- blocker 2 -----------------------------------------------------------
    def test_frozen_evaluation_order(self):
        order = _norm(self.i06["tgt06_specific_aggregation_truth_table"]["frozen_evaluation_order"])
        self.assertIn("in this exact order and stops at the first match", order)
        # step 2 precedes step 3: a clean productive B beats a conflicted A
        idx_clean = order.index("if at least one clean / uncontested productive direct configuration exists")
        idx_conflict = order.index("else if any configuration identity carries both a qualifying productive direct observation and a qualifying direct-quality failure observation")
        self.assertLess(idx_clean, idx_conflict)
        self.assertIn("a conflicted configuration a plus a clean productive configuration b is still positive / direct", order)
        self.assertIn("a single non-internalizing configuration never establishes target-wide non-internalization", order)

    def test_clean_productive_definition(self):
        note = _norm(self.i06["tgt06_specific_aggregation_truth_table"]["note"])
        self.assertIn('a "clean / uncontested productive direct configuration" is a configuration identity that appears in at least one direct productive observation\'s projection set and appears in no direct-quality failure observation\'s projection set', note)
        self.assertIn("there is no machine conflict resolver", note)

    # ---- blocker 3 -----------------------------------------------------------
    def test_gate_question_is_not_the_direct_ceiling(self):
        a = _norm(self.item["03_gate_question"]["tgt06_framing"]["answers"])
        self.assertIn("whether admissible public evidence supports internalization / trafficking addressability of the target-antibody complex", a)
        self.assertIn("the gate question is not identical to the direct ceiling", a)
        self.assertIn("a completed landscape with qualifying indirect_strong addressability evidence and no direct configuration is still a real, graded answer (positive / indirect_strong)", a)

    # ---- blocker 4 -----------------------------------------------------------
    def test_trafficking_or_recycling_only_asymmetric_authority(self):
        t = _norm(self.i06["trafficking_or_recycling_only_authority"])
        self.assertIn("has asymmetric authority", t)
        self.assertIn("positive direction -- lysosomal trafficking observed but no integrated same-configuration antibody-induced internalization proof -> at most indirect_strong / supporting; it can never synthesize a positive direct", t)
        self.assertIn("is a direct-quality failure observation (maps to opposes_addressability)", t)
        self.assertIn("it is an eligible fatal_review contributor (item 08)", t)

    def test_trafficking_or_recycling_only_in_the_fatal_contributor_set(self):
        crit = _flatten(self.item["08_fatal_conditions"]["machine_detection_criteria"]["each_contributing_observation_must_be"])
        self.assertIn("observation_kind in {antibody_configuration_internalization_trafficking, antibody_configuration_internalization_only, trafficking_or_recycling_only}", crit)
        self.assertIn("a trafficking_or_recycling_only observation is eligible only in its negative direction", crit)
        self.assertIn("observation_kind in {antibody_configuration_internalization_trafficking, antibody_configuration_internalization_only, trafficking_or_recycling_only}", self.checks)

    def test_positive_direct_still_requires_an_integrated_observation(self):
        t = _norm(self.i06["trafficking_or_recycling_only_authority"])
        self.assertIn("a positive direct contributor must still be an integrated same-configuration internalization + lysosomal delivery observation", t)


class ReviewRound2RegressionTests(unittest.TestCase):
    """PR E13 ChatGPT AI审核方案 review round 2 -- 3 narrow consistency blockers
    (the 4 round-1 blockers were all CLOSED).

    (1) item 12 fatal_review.required_is_true_iff did not sync the
        TRAFFICKING_OR_RECYCLING_ONLY contributor kind (item 08 / item 13 had).
    (2) the same-configuration conflict still referenced a non-existent typed
        resolver -- now there is NO machine conflict resolver in v1: a single
        configuration identity carrying both a productive DIRECT and a
        DIRECT-quality failure observation is simply CONFLICTING / DIRECT.
    (3) how an IDENTIFIED_MULTI observation's config-id SET enters grouping /
        counting was not locked -- now the frozen configuration_identity_projection
        helper is the ONE interpretation everything uses.
    """

    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.i06 = self.item["06_direction_interpretation"]
        self.checks = _flatten(
            self.item["13_machine_acceptance_criteria"][
                "a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"
            ]
        )

    # ---- blocker 1 ---------------------------------------------------------
    def test_item12_required_iff_uses_the_three_kind_contributor_set(self):
        r = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["required_is_true_iff"])
        self.assertIn("observation_kind in {antibody_configuration_internalization_trafficking, antibody_configuration_internalization_only, trafficking_or_recycling_only}", r)
        self.assertIn("the exact three-kind contributor set of item 08", r)
        self.assertIn("a trafficking_or_recycling_only observation is eligible only in its negative / failure direction", r)

    def test_item08_item12_item13_share_the_same_contributor_set(self):
        i08 = _flatten(self.item["08_fatal_conditions"]["machine_detection_criteria"]["each_contributing_observation_must_be"])
        i12 = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["required_is_true_iff"])
        wanted = "{antibody_configuration_internalization_trafficking, antibody_configuration_internalization_only, trafficking_or_recycling_only}"
        self.assertIn(wanted, i08)
        self.assertIn(wanted, i12)
        self.assertIn(wanted, self.checks)

    # ---- blocker 2 ---------------------------------------------------------
    def test_no_machine_conflict_resolver_in_v1(self):
        dd = _norm(self.i06["direction_definitions"]["CONFLICTING"])
        self.assertIn("the same antibody / epitope configuration identity carries both a qualifying productive direct observation and a qualifying direct-quality failure observation", dd)
        self.assertIn("there is no machine conflict resolver in v1", dd)
        self.assertIn("is a human-review question", dd)
        d = _norm(self.i06["different_configurations_differ_is_not_a_conflict"])
        self.assertIn("it never runs a machine conflict resolver to explain away a genuine same-configuration productive-vs-failure pair", d)
        note = _norm(self.i06["tgt06_specific_aggregation_truth_table"]["note"])
        self.assertIn("there is no machine conflict resolver -- a same-configuration productive-vs-failure pair is simply conflicting / direct", note)
        # the resolver-language must be gone
        self.assertNotIn("typed / auditable characterization", note)
        self.assertNotIn("no auditable characterization resolves them", dd)

    def test_conflicting_row_key_and_evaluation_step(self):
        tt = self.i06["tgt06_specific_aggregation_truth_table"]
        self.assertIn("completed_and_no_clean_productive_direct_and_a_configuration_identity_carries_both_a_productive_direct_and_a_direct_quality_failure_observation", tt)
        order = _norm(tt["frozen_evaluation_order"])
        self.assertIn("else if any configuration identity carries both a qualifying productive direct observation and a qualifying direct-quality failure observation -> conflicting / direct (no machine conflict resolver; the module never reconciles it)", order)

    # ---- blocker 3 ---------------------------------------------------------
    def test_frozen_configuration_identity_projection_helper(self):
        proj = _norm(self.i06["tgt06_specific_aggregation_truth_table"]["configuration_identity_projection"])
        self.assertIn("the one deterministic helper every configuration-identity operation uses", proj)
        self.assertIn("single -> {internalization_configuration_id}", proj)
        self.assertIn("identified_multi -> set(internalization_configuration_ids)", proj)
        self.assertIn("identity_not_disclosed_or_not_applicable -> {} (the empty set)", proj)
        self.assertIn("an identified_multi {a, b} failure observation contributes both a and b to the failure configuration set", proj)
        self.assertIn("per-configuration grouping, clean / uncontested detection", proj)
        self.assertIn("route b convergence (item 08), and completion.qualifying_direct_configuration_ids (item 09) -- operate over this projection set", proj)

    def test_route_b_and_completion_use_the_projection(self):
        rb = _norm(self.item["08_fatal_conditions"]["machine_detection_criteria"]["route_b_independent_convergence"])
        self.assertIn("the union of the item-06 configuration_identity_projection sets of those eligible failure observations has size >= 2", rb)
        tc = _norm(self.item["09_evidence_source_plan"]["internalization_search_landscape"]["typed_completion_record"])
        self.assertIn("it is the union of the item-06 configuration_identity_projection sets of every observation classified qualifying direct-rung", tc)
        self.assertIn("an identified_multi {a, b} qualifying observation contributes both a and b", tc)

    def test_item13_aggregation_check_uses_the_projection(self):
        self.assertIn("every configuration test is over the frozen item-06 configuration_identity_projection", self.checks)
        self.assertIn("there is no machine conflict resolver -- the module never reconciles or characterises the pair", self.checks)


class ReviewRound3RegressionTests(unittest.TestCase):
    """PR E13 ChatGPT AI审核方案 review round 3 -- 1 narrow Route A/B consistency
    blocker (round-1 4/4 and round-2 3/3 all CLOSED).

    Fatal Route B previously let a single IDENTIFIED_MULTI {A,B} failure
    observation satisfy the convergence test purely on projection cardinality,
    bypassing Route A's reproducibility_status == QUALIFIED gate. Now Route B
    requires BOTH >= 2 DISTINCT eligible failure OBSERVATIONS AND a projected
    configuration-identity union of size >= 2; a single IDENTIFIED_MULTI
    observation can establish the fatal pattern ONLY through Route A. The
    ordinary Gate-level aggregation (item 06) is UNCHANGED -- a single
    IDENTIFIED_MULTI {A,B} failure observation still projects to two failure
    configuration identities and may still support NEGATIVE / DIRECT. A Gate
    NEGATIVE scientific assessment != a machine POTENTIAL_FATAL_PATTERN.
    """

    def setUp(self):
        self.item = yaml.safe_load(CONTRACT.read_text())["acceptance_checklist"]
        self.checks = _flatten(
            self.item["13_machine_acceptance_criteria"][
                "a_proposal_envelope_and_its_packages_are_machine_acceptable_iff"
            ]
        )

    def test_route_b_requires_two_distinct_eligible_observations(self):
        rb = _norm(self.item["08_fatal_conditions"]["machine_detection_criteria"]["route_b_independent_convergence"])
        self.assertIn("at least two distinct eligible direct-quality failure observations", rb)
        self.assertIn("the union of the item-06 configuration_identity_projection sets of those eligible failure observations has size >= 2", rb)
        self.assertIn("a single identified_multi observation, regardless of its projection cardinality, does not satisfy route b", rb)
        self.assertIn("a single multi-configuration observation may establish the fatal pattern only through route a, which additionally requires reproducibility_status == qualified", rb)

    def test_ordinary_negative_is_explicitly_unchanged(self):
        rb = _norm(self.item["08_fatal_conditions"]["machine_detection_criteria"]["route_b_independent_convergence"])
        self.assertIn("this route b restriction is a machine potential_fatal_pattern gate only; the ordinary gate-level aggregation (item 06) is unchanged", rb)
        self.assertIn("a single identified_multi {a, b} failure observation still projects to two failure configuration identities and may still support negative / direct", rb)
        self.assertIn("a gate negative scientific assessment is not a machine potential_fatal_pattern", rb)

    def test_item12_and_item13_sync_the_route_b_restriction(self):
        r12 = _norm(self.item["12_assessment_proposal_envelope_contract"]["fatal_review"]["required_is_true_iff"])
        self.assertIn("route b (at least two distinct eligible failure observations and the union of their item-06 configuration_identity_projection sets has size >= 2)", r12)
        self.assertIn("a single identified_multi observation, regardless of its projection cardinality, does not satisfy route b", r12)
        self.assertIn("route b (>= 2 distinct eligible failure observations and their projected configuration-identity union has size >= 2)", self.checks)
        self.assertIn("a single identified_multi observation does not satisfy route b regardless of its projection cardinality", self.checks)


class NoImplementationInPrE13Tests(unittest.TestCase):
    """PR E13 is design-only. The implementation package it defers is built by
    PR E14; until then the repository must show no MOD-TGT06 package and the
    TGT-06 binding still 0.0.0."""

    def setUp(self):
        self.doc = yaml.safe_load(CONTRACT.read_text())

    def test_repository_policy_forbids_implementation_and_registry_changes(self):
        p = self.doc["repository_policy"]
        self.assertEqual(p["implementation_code_in_this_pr"], "forbidden")
        self.assertEqual(p["provider_or_adapter_in_this_pr"], "forbidden")
        self.assertEqual(p["trial_or_dataset_retrieval_in_this_pr"], "forbidden")
        self.assertEqual(p["numeric_or_ranking_scoring"], "forbidden")
        self.assertEqual(p["internalization_rate_or_half_life_or_percent_internalized_or_colocalization_coefficient_threshold"], "forbidden")
        self.assertEqual(p["invented_adc_effective_internalization_rate_range"], "forbidden")
        self.assertEqual(p["generic_gatemodule_framework_or_base_class_in_this_pr"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt01"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt02"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt03"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt04"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt05"], "forbidden")
        self.assertEqual(p["modifies_mod_tgt08"], "forbidden")
        self.assertEqual(p["modifies_binding_or_registry_or_existing_tests"], "forbidden")
        self.assertEqual(p["only_allowed_existing_file_mutation"], "append_to_logs_worklog_md")
        self.assertEqual(p["migration_pending"], "remains")

    def test_no_tgt06_implementation_package_yet(self):
        pkg = ROOT / "gate_modules" / "tgt06_internalization_trafficking_addressability"
        self.assertFalse(pkg.exists(), "PR E13 ships no implementation; PR E14 builds the package")

    def test_tgt06_binding_is_still_zero_and_the_others_untouched(self):
        gs = yaml.safe_load(CRC_GATESET.read_text())
        by_gate = {
            b["gate_id"]: b["primary_module_version"]
            for b in gs["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(by_gate["TGT-06"], "0.0.0")
        self.assertEqual(by_gate["TGT-07"], "0.0.0")
        for g in ("TGT-01", "TGT-02", "TGT-03", "TGT-04", "TGT-05", "TGT-08"):
            self.assertEqual(by_gate[g], "1.0.0")

    def test_deferred_block_names_the_e14_implementation(self):
        joined = " ".join(self.doc["deferred_to_pr_e14_plus"]).lower()
        self.assertIn("gate_modules/tgt06_internalization_trafficking_addressability/", joined)
        self.assertIn("internalizationevidencecompletion", joined)
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
            "tgt08_target_opportunity_competition_ip_whitespace",
        )
        self.assertTrue(all(any(pkg in p for pkg in allowed) for p in py_files), py_files)


class DrawingTests(unittest.TestCase):
    def setUp(self):
        self.text = DRAWING.read_text()

    def test_drawing_exists_and_names_the_module_and_pr(self):
        self.assertIn("MOD-TGT06", self.text)
        self.assertIn("PR E13", self.text)
        self.assertIn("Internalization / Trafficking Addressability", self.text)

    def test_drawing_covers_all_seventeen_items(self):
        for n in range(1, 18):
            self.assertRegex(self.text, rf"\|\s*{n}\s*\|\s*\*\*", f"drawing row {n} missing")

    def test_drawing_has_the_three_headline_blockquotes(self):
        self.assertIn("Internalization is configuration-specific, not a target-intrinsic", self.text)
        self.assertIn("DIRECT productive-addressability authority requires an auditable", self.text)
        self.assertIn("A target-wide surface-static potential fatal pattern requires", self.text)

    def test_drawing_freezes_the_key_rulings(self):
        t = self.text
        norm = " ".join(t.split()).lower()
        self.assertIn("highest-qualifying-rung grading authority", norm)
        self.assertIn("Legal Direction × Strength pairs (exactly 6)", t)
        self.assertIn("existence-proof dominance", norm)
        self.assertIn("Route A", t)
        self.assertIn("Route B", t)
        self.assertIn("no cross-observation synthesis of direct", norm)
        self.assertIn("no `qualifying_indirect_configuration_ids`", norm)

    def test_drawing_states_no_binding_or_registry_or_test_change(self):
        norm = " ".join(self.text.split()).lower()
        self.assertIn("append to `logs/worklog.md`", norm)
        self.assertIn("does not touch it, the binding, the registry or any existing test", norm)


if __name__ == "__main__":
    unittest.main()
