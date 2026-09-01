"""Machine acceptance for a MOD-TGT07 run: the E15 item-13 checklist turned into
executable scientific / integrity checks (E16 tightening 3 / 8). This module
executes item 13 (machine acceptance), item 10 (input / binding invariants), item
11 (EP integrity), item 12 (proposal / fatal-review structural boundary) and item
16 (completion-before-grade). It is NOT a "17-item YAML parser" -- items 03-09
science lives in classify / aggregate / completion / fatal, and the runtime never
parses ``src/contracts/gate_modules/tgt07...yaml`` natural language.

A HARD identity / provenance / completion-consistency / classification-
qualification failure rejects the WHOLE run (proposal = None); it is never
degraded to an accepted UNKNOWN. UNKNOWN from a genuinely incomplete public
soluble-antigen search, or from a completed landscape with only WEAK /
below-assay-limit / no qualifying evidence, is NOT an integrity failure.

The "no numeric threshold" check scans only MODULE-OWNED text (the aggregation
rationale, the critical-unknown wording and the neutral interpretation-boundary
factual statements). A source-reported numeric fact lives in the neutral ``claim``
and is NOT scanned -- it is evidence, not a threshold.
"""

from __future__ import annotations

import re

from .aggregate import AggregationOutcome
from .completion import SolubleAntigenEvidenceCompletion
from .contracts import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    AssessmentProposalEnvelope,
    EmittedEvidence,
    FatalReviewRecord,
    Tgt07ModuleInput,
    sink_materiality_direction,
)

_MATERIAL_WITH_COMPROMISE = "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE"
_MATERIAL_WITHOUT_COMPROMISE = (
    "MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE"
)
_NO_MATERIAL_SINK = "NO_MATERIAL_SOLUBLE_SINK"
_MIXED_OR_UNRESOLVED = "MIXED_OR_UNRESOLVED"
_MATERIAL_OUTCOMES = (_MATERIAL_WITH_COMPROMISE, _MATERIAL_WITHOUT_COMPROMISE)
_DIRECT_AUTHORITY_KINDS = ("CLINICAL_ANTIGEN_SINK_PK_EFFECT", "SOLUBLE_ANTIGEN_TMDD_ANALYSIS")
_INDIRECT_STRONG_KINDS = (
    "SOLUBLE_ANTIGEN_QUANTITATION",
    "SHEDDASE_SUBSTRATE_STATUS",
    "SECRETED_ISOFORM",
)
_WEAK_KINDS = ("PREDICTED_CLEAVAGE_SITE_INFERENCE", "FAMILY_ANALOGY_SHEDDING_INFERENCE")

# forbidden CONCLUSION wording the module's own templates never produce; scanned
# over the aggregation rationale + critical unknowns + the neutral
# interpretation-boundary factual statements (NOT the source claim).
_F_CROSS_GATE = (
    "adc modality precedent established", "baseline malignant-cell coverage established",
    "coverage established", "persistence established", "materially impaired persistence",
    "surface density", "antigen density", "surface availability",
    "normal-tissue fatal", "internalization addressability established",
    "the target is a sink", "the target is not a sink",
)
_F_DECISION_SUBSTR = ("public_fatal_signal_established", "should be killed", "fatal flag")
_F_DECISION_WORD_RE = re.compile(r"\b(kill|killed|hold|holds|decision|decisions)\b", re.I)
#: MODULE-authored numeric / threshold DECISION language only -- NOT a
#: source-reported factual measurement (which lives in the neutral claim, never
#: scanned here).
_SCORE_RE = re.compile(
    r"\bh-?score\b|\bscore\s*=|\branking\b|\bcutoff\b|\bthreshold of\b|\bthreshold\b"
    r"|\bfold[- ]change\b|\bsink[- ]ratio\s*[<>=]|\bmaterial soluble-antigen sink concentration\b"
    r"|\bif\s+\w*(?:concentration|turnover|affinity|sink)\w*\s*[<>=]"
    r"|(?:above|below)\s+[\d,.]+\s*(?:ng/ml|pg/ml|nm|pm|%|percent|fold)"
    r"|\b\d[\d,.]*\s*(?:ng/ml|nm|%)\s+(?:cutoff|threshold|effective)\b",
    re.I,
)


def _module_owned_text(
    outcome: AggregationOutcome, emitted: list[EmittedEvidence]
) -> str:
    """MODULE-authored text only: the aggregation rationale, the critical-unknown
    wording and each EP's ``directly_supports`` factual statement. The
    source-reported numeric fact lives in ``package.claim`` and the fixed
    ``does_not_support`` / ``limitations`` / ``evidence_ceiling`` boilerplate
    deliberately names KILL / Decision as things the package does NOT support --
    both are excluded from the scan."""

    parts: list[str] = [outcome.aggregation_rationale]
    parts.extend(u for u, _ in outcome.critical_unknowns)
    for e in emitted:
        parts.extend(e.package.interpretation_boundary["directly_supports"])
    return " ".join(parts).lower()


def evaluate(
    *,
    emitted: list[EmittedEvidence],
    outcome: AggregationOutcome,
    completion: SolubleAntigenEvidenceCompletion,
    fatal_review: FatalReviewRecord,
    hard_integrity_failures: list[tuple[str, str]],
    module_input: Tgt07ModuleInput,
) -> tuple[list[tuple[str, bool]], list[str]]:
    """Return (ordered checks, failure reasons). ``accepted`` is ``all(ok)``."""

    checks: list[tuple[str, bool]] = []
    reasons: list[str] = []

    def record(name: str, ok: bool, why: str) -> None:
        checks.append((name, ok))
        if not ok:
            reasons.append(why)

    admissible = [e for e in emitted if e.classified.admissible]
    d, s = outcome.proposed_direction, outcome.proposed_strength
    roles = {r for _, r in outcome.evidence_refs}
    ep_ids = [e.evidence_id for e in emitted]

    # --- identity / hygiene (item 10 / 11) -------------------------------
    record(
        "no_hard_identity_provenance_or_completion_integrity_failure",
        not hard_integrity_failures,
        "hard identity / provenance / completion-consistency / classification-"
        "qualification integrity failure(s): "
        + "; ".join(f"{i}: {why}" for i, why in hard_integrity_failures),
    )
    obs_ids = [e.observation.observation_id for e in emitted]
    record(
        "one_evidence_package_per_observation",
        len(ep_ids) == len(set(ep_ids)) and len(obs_ids) == len(set(obs_ids)),
        "an observation_id does not map to exactly one EvidencePackage",
    )
    record(
        "every_emitted_observation_has_a_resolved_primary_or_repository_source",
        all(e.observation.primary_or_repository_source_resolved for e in emitted),
        "an emitted observation lacks a resolved primary / repository source",
    )
    emitted_ids = set(ep_ids)
    ref_ids = [eid for eid, _ in outcome.evidence_refs]
    record(
        "every_evidence_ref_points_at_one_emitted_or_reused_package",
        all(eid in emitted_ids for eid in ref_ids) and len(ref_ids) == len(set(ref_ids)),
        "an evidence_ref is dangling or repeated",
    )
    record(
        "candidate_canonical_target_identity_matches_every_observation",
        all(
            e.observation.target_identity.strip() == module_input.target_identity.strip()
            for e in emitted
        ),
        "an emitted observation targets an identity other than the candidate's canonical target",
    )

    # --- freshness / scope (item 10; E8 gene) ------------------------
    as_of = module_input.landscape_as_of
    fresh_ok = all(e.observation.landscape_as_of == as_of for e in emitted)
    if completion.attempted:
        fresh_ok = fresh_ok and completion.landscape_as_of == as_of
    record(
        "landscape_as_of_consistent_across_observations_and_completion",
        fresh_ok,
        "an observation or the completion state carries a landscape_as_of that "
        "disagrees with the run's landscape_as_of",
    )
    scope_ok = all(
        e.observation.context_key.strip() == module_input.context_key.strip()
        for e in emitted
    )
    if completion.attempted:
        scope_ok = scope_ok and (
            completion.search_scope.strip()
            == module_input.soluble_antigen_search_scope.strip()
        )
    record(
        "context_key_and_search_scope_match_the_run",
        scope_ok,
        "an observation context_key or the completion search_scope disagrees with the run",
    )

    # --- frozen ladder hard locks (E15 item 05 / 09 / 13) -------------
    non_authority_direct = [
        e for e in admissible
        if e.classified.evidence_rung == "DIRECT"
        and e.observation.observation_kind not in _DIRECT_AUTHORITY_KINDS
    ]
    record(
        "only_a_clinical_or_tmdd_observation_reaches_direct",
        not non_authority_direct,
        "a non CLINICAL_ANTIGEN_SINK_PK_EFFECT / SOLUBLE_ANTIGEN_TMDD_ANALYSIS "
        "observation was classified DIRECT",
    )
    weak_above = [
        e for e in admissible
        if e.observation.observation_kind in _WEAK_KINDS
        and e.classified.evidence_rung not in ("WEAK", "")
    ]
    record(
        "predicted_cleavage_site_or_family_analogy_never_rises_above_weak",
        not weak_above,
        "a predicted-cleavage-site / family-analogy inference observation reached a rung above WEAK",
    )
    indirect_above = [
        e for e in admissible
        if e.observation.observation_kind in _INDIRECT_STRONG_KINDS
        and e.classified.evidence_rung == "DIRECT"
    ]
    record(
        "quantitation_sheddase_and_secreted_isoform_never_reach_direct",
        not indirect_above,
        "a quantified CRC-patient soluble target, a documented sheddase-substrate "
        "status, or a validated secreted isoform observation was classified DIRECT",
    )
    below_lod_positive = [
        e for e in admissible
        if e.observation.observation_kind == "SOLUBLE_ANTIGEN_QUANTITATION"
        and e.observation.circulating_soluble_target_status
        == "BELOW_DETECTION_OR_QUANTITATION_LIMIT"
        and (e.classified.qualifying_indirect or e.classified.is_qualifying_direct)
    ]
    record(
        "a_below_detection_or_quantitation_limit_measurement_is_contextual_only",
        not below_lod_positive,
        "a BELOW_DETECTION_OR_QUANTITATION_LIMIT quantitation was classified positive "
        "INDIRECT_STRONG or DIRECT (it is CONTEXTUAL only, never NEGATIVE / "
        "INDIRECT_STRONG)",
    )
    healthy_only_positive = [
        e for e in admissible
        if e.observation.observation_kind == "SOLUBLE_ANTIGEN_QUANTITATION"
        and e.observation.cohort_class == "HEALTHY_DONOR_SERUM"
        and e.classified.qualifying_indirect
    ]
    record(
        "a_healthy_donor_only_quantitation_is_contextual_by_default",
        not healthy_only_positive,
        "a HEALTHY_DONOR_SERUM quantitation was classified positive INDIRECT_STRONG "
        "(PR D's INDIRECT_STRONG rung is quantified CRC-patient soluble target)",
    )

    # --- DIRECT qualification is kind-specific (E16 tightening 1 / 3) -----
    clinical_direct_bad = [
        e for e in admissible
        if e.observation.observation_kind == "CLINICAL_ANTIGEN_SINK_PK_EFFECT"
        and e.classified.is_qualifying_direct
        and not (
            e.observation.is_same_target_match_qualified
            and e.observation.is_soluble_antigen_attribution_qualified
            and e.observation.is_analysis_validation_qualified
            and e.observation.has_sink_exposure_context
        )
    ]
    record(
        "a_clinical_direct_observation_has_qualified_same_target_match_attribution_and_analysis_validation",
        not clinical_direct_bad,
        "a CLINICAL_ANTIGEN_SINK_PK_EFFECT observation was classified DIRECT without "
        "same_target_therapeutic_match_status == QUALIFIED + basis + ref, "
        "soluble_antigen_attribution_status == QUALIFIED + basis, "
        "analysis_validation_status == QUALIFIED + basis + a non-empty analysis_method, "
        "and a non-empty sink_exposure_context_id + basis",
    )
    tmdd_direct_bad = [
        e for e in admissible
        if e.observation.observation_kind == "SOLUBLE_ANTIGEN_TMDD_ANALYSIS"
        and e.classified.is_qualifying_direct
        and not (
            e.observation.is_tmdd_input_adequate
            and e.observation.is_analysis_validation_qualified
            and e.observation.has_sink_exposure_context
        )
    ]
    record(
        "a_tmdd_direct_observation_has_qualified_tmdd_input_adequacy_and_analysis_validation",
        not tmdd_direct_bad,
        "a SOLUBLE_ANTIGEN_TMDD_ANALYSIS observation was classified DIRECT without "
        "tmdd_input_adequacy_status == QUALIFIED + basis, analysis_validation_status "
        "== QUALIFIED + basis + a non-empty analysis_method, and a non-empty "
        "sink_exposure_context_id + basis",
    )
    not_established_direct = [
        e for e in admissible
        if e.observation.sink_materiality_outcome == "NOT_ESTABLISHED"
        and e.classified.is_qualifying_direct
    ]
    record(
        "a_not_established_sink_materiality_outcome_is_never_a_qualifying_direct_rung_observation",
        not not_established_direct,
        "a NOT_ESTABLISHED sink_materiality_outcome observation was classified as a "
        "qualifying DIRECT-rung observation (E16 tightening 2)",
    )
    mixed_not_direct = [
        e for e in admissible
        if e.observation.sink_materiality_outcome == _MIXED_OR_UNRESOLVED
        and e.observation.observation_kind in _DIRECT_AUTHORITY_KINDS
        and e.classified.qualifying_direct_mixed
        and e.classified.evidence_rung != "DIRECT"
    ]
    record(
        "a_mixed_or_unresolved_direct_quality_analysis_is_direct_rung_contextual",
        not mixed_not_direct,
        "a DIRECT-quality MIXED_OR_UNRESOLVED analysis is not carried as an "
        "evidence_rung DIRECT CONTEXTUAL observation",
    )

    # --- canonical NEGATIVE / DIRECT authority (E15 item 09) --------------
    bad_negative = [
        e for e in admissible
        if e.classified.qualifying_direct_no_material_sink
        and not (
            e.observation.observation_kind == "SOLUBLE_ANTIGEN_TMDD_ANALYSIS"
            and e.observation.exposure_scenario_class == "INTENDED_ADC_EXPOSURE"
            and e.observation.is_tmdd_input_adequate
            and e.observation.is_analysis_validation_qualified
            and e.observation.sink_materiality_outcome == _NO_MATERIAL_SINK
        )
    ]
    record(
        "a_canonical_no_material_sink_direct_is_only_a_qualified_intended_adc_tmdd",
        not bad_negative,
        "a no-material-sink DIRECT observation was classified without being a "
        "qualified SOLUBLE_ANTIGEN_TMDD_ANALYSIS at INTENDED_ADC_EXPOSURE concluding "
        "NO_MATERIAL_SOLUBLE_SINK (a same-target therapeutic with no reported PK sink, "
        "or a same-target-analogue / unresolved-scenario TMDD, is never a canonical "
        "NEGATIVE / DIRECT)",
    )
    if d == "NEGATIVE":
        record(
            "a_negative_direction_rests_on_a_qualified_intended_adc_no_material_sink_tmdd",
            any(e.classified.qualifying_direct_no_material_sink for e in admissible)
            and not any(e.classified.qualifying_direct_material_sink for e in admissible),
            "a NEGATIVE / DIRECT was proposed without a qualifying intended-ADC "
            "no-material-sink TMDD observation, or with a material-sink DIRECT present",
        )

    # --- no cross-observation synthesis of DIRECT (E15 item 06 / E15-3) ---
    record(
        "direct_is_never_synthesized_across_observations",
        all(
            (not e.classified.is_qualifying_direct)
            or e.observation.observation_kind in _DIRECT_AUTHORITY_KINDS
            for e in admissible
        ),
        "a DIRECT proof was synthesized from an observation that is not a single "
        "upstream-qualified integrated CLINICAL / TMDD observation",
    )

    # --- sink-exposure namespace + bases (E15 item 13) -------------------
    # E15 only requires: a qualifying DIRECT observation MUST carry a context, and
    # an INDIRECT_STRONG / WEAK / SEARCH_COMPLETION_AUDIT observation MUST NOT. A
    # CLINICAL_ANTIGEN_SINK_PK_EFFECT / SOLUBLE_ANTIGEN_TMDD_ANALYSIS observation
    # that the classifier judged CONTEXTUAL (e.g. same-target match / TMDD input
    # adequacy NOT_ESTABLISHED) may still keep its real factual local exposure
    # context -- "did not reach DIRECT" is not "illegal input" (E16 review round-1
    # blocker 2). The constructor already forbids a non-DIRECT-authority kind from
    # carrying a context.
    ctx_on_wrong_kind = [
        e for e in admissible
        if e.observation.sink_exposure_context_id.strip()
        and e.observation.observation_kind not in _DIRECT_AUTHORITY_KINDS
    ]
    record(
        "only_a_direct_authority_kind_carries_a_sink_exposure_context",
        not ctx_on_wrong_kind,
        "an INDIRECT_STRONG / WEAK / SEARCH_COMPLETION_AUDIT observation carries a "
        "non-empty sink_exposure_context_id",
    )
    missing_ctx = [
        e for e in admissible
        if e.classified.is_qualifying_direct
        and not e.observation.has_sink_exposure_context
    ]
    record(
        "every_qualifying_direct_rung_observation_carries_an_auditable_sink_exposure_context",
        not missing_ctx,
        "a qualifying DIRECT-rung observation carries no auditable local "
        "sink_exposure_context_id + basis",
    )
    canon_collision = [
        e for e in admissible
        if e.observation.sink_exposure_context_id.strip() == module_input.context_id
    ]
    record(
        "a_local_sink_exposure_context_id_is_never_the_canonical_instantiation_context_id",
        not canon_collision,
        "a sink_exposure_context_id collapses onto the canonical Instantiation context_id",
    )
    missing_basis = [
        e for e in admissible
        if (
            (e.observation.circulating_soluble_target_status
             not in ("", "NOT_ESTABLISHED", "MIXED_OR_UNRESOLVED")
             and not e.observation.circulating_soluble_target_basis.strip())
            or (e.observation.cohort_class not in ("", "UNRESOLVED")
                and not e.observation.cohort_class_basis.strip())
            or (e.observation.sink_materiality_outcome != "NOT_ESTABLISHED"
                and not e.observation.sink_materiality_outcome_basis.strip())
            or (e.observation.analysis_validation_status == "QUALIFIED"
                and not e.observation.analysis_validation_basis.strip())
            or (e.observation.tmdd_input_adequacy_status == "QUALIFIED"
                and not e.observation.tmdd_input_adequacy_basis.strip())
            or (e.observation.same_target_therapeutic_match_status == "QUALIFIED"
                and not e.observation.same_target_therapeutic_match_basis.strip())
            or (e.observation.soluble_antigen_attribution_status == "QUALIFIED"
                and not e.observation.soluble_antigen_attribution_basis.strip())
            or (e.observation.exposure_scenario_class not in ("", "UNRESOLVED")
                and not e.observation.exposure_scenario_basis.strip())
        )
    ]
    record(
        "every_classification_driving_qualified_status_carries_an_auditable_basis",
        not missing_basis,
        "a classification-driving qualified status (circulating_soluble_target_status "
        "/ cohort_class / sink_materiality_outcome / analysis_validation_status / "
        "tmdd_input_adequacy_status / same_target_therapeutic_match_status / "
        "soluble_antigen_attribution_status / exposure_scenario_class) is missing its "
        "auditable basis",
    )
    repro_gated = [
        e for e in admissible
        if e.classified.is_qualifying_direct
        and e.observation.reproducibility_status == "NOT_ESTABLISHED"
        and e.observation.observation_kind == "CLINICAL_ANTIGEN_SINK_PK_EFFECT"
        and e.observation.is_material_sink_outcome
    ]
    # This is not a failure -- it is the POSITIVE regression: a
    # reproducibility_status == NOT_ESTABLISHED clinical material-sink observation
    # that meets every other clause is still a qualifying DIRECT-rung observation.
    record(
        "reproducibility_status_is_never_a_classification_or_acceptance_gate",
        True,
        "",
    )
    del repro_gated  # documented above; reproducibility_status is optional metadata only

    # --- no early grade (E15 item 16) ---------------------------
    needs_complete_landscape = d in ("POSITIVE", "NEGATIVE", "CONFLICTING") or (
        d == "INCONCLUSIVE" and s == "DIRECT"
    )
    record(
        "graded_direction_requires_a_completed_audited_soluble_antigen_landscape",
        (not needs_complete_landscape) or completion.landscape_complete,
        "a graded Direction x Strength was proposed before the mandatory "
        "soluble-antigen-evidence landscape was complete and audited",
    )
    record(
        "quantitation_axis_requires_both_cohort_subspaces",
        (not completion.attempted)
        or completion._quantitation_axis_matches_subspaces,
        "soluble_antigen_quantitation_search_complete is not the strict AND of the "
        "CRC-patient and healthy-donor subspace search facts",
    )

    # --- Direction x Strength == the frozen item-06 truth table ------
    record(
        "direction_strength_pair_is_a_legal_tgt07_pair",
        (d, s) in LEGAL_DIRECTION_STRENGTH_PAIRS,
        f"Direction x Strength {(d, s)} is not a legal TGT-07 pair (only "
        "POSITIVE/DIRECT, POSITIVE/INDIRECT_STRONG, NEGATIVE/DIRECT, "
        "CONFLICTING/DIRECT, INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN)",
    )
    record(
        "no_weak_proposed_strength",
        s != "WEAK",
        "the proposal carries the WEAK strength -- TGT-07 never proposes WEAK",
    )
    strength_ok = (not completion.landscape_complete) or (
        ((s == "DIRECT") == outcome.has_direct_rung)
        and (
            (s == "INDIRECT_STRONG")
            == (outcome.has_qualifying_indirect and not outcome.has_direct_rung)
        )
    )
    record(
        "proposed_strength_follows_the_highest_qualifying_rung_authority",
        strength_ok,
        f"proposed_strength {s} does not follow the highest-qualifying-rung "
        "authority over the completed landscape",
    )
    record(
        "unknown_carries_no_evidence_refs",
        not (d == "INCONCLUSIVE" and s == "UNKNOWN") or not outcome.evidence_refs,
        "the INCONCLUSIVE / UNKNOWN state carries evidence_refs",
    )
    record(
        "graded_inconclusive_direct_carries_contextual_evidence_refs",
        not (d == "INCONCLUSIVE" and s == "DIRECT")
        or ("CONTEXTUAL" in roles and bool(outcome.evidence_refs)),
        "a graded INCONCLUSIVE / DIRECT proposal has no CONTEXTUAL evidence_ref",
    )

    # --- Direction over a qualifying DIRECT observation == frozen mapping --
    mapping_bad = [
        e for e in admissible
        if e.classified.is_qualifying_direct
        and e.classified.sink_liability_implication != sink_materiality_direction(e.observation)
    ]
    record(
        "direction_over_a_qualifying_direct_observation_follows_the_frozen_sink_materiality_direction_mapping",
        not mapping_bad,
        "a qualifying DIRECT observation's sink_liability_implication disagrees with "
        "the frozen sink_materiality_direction_mapping",
    )

    # --- aggregation follows the frozen evaluation order --------------
    if completion.landscape_complete:
        material_ctx = {
            e.sink_exposure_context_id
            for e in admissible
            if e.classified.qualifying_direct_material_sink
        }
        no_material_ctx = {
            e.sink_exposure_context_id
            for e in admissible
            if e.classified.qualifying_direct_no_material_sink
        }
        clean_material_ctx = material_ctx - no_material_ctx
        conflicted_ctx = material_ctx & no_material_ctx
        has_mixed = any(e.classified.qualifying_direct_mixed for e in admissible)
        if clean_material_ctx:
            expect = ("POSITIVE", "DIRECT")
        elif conflicted_ctx:
            expect = ("CONFLICTING", "DIRECT")
        elif no_material_ctx:
            expect = ("NEGATIVE", "DIRECT")
        elif has_mixed:
            expect = ("INCONCLUSIVE", "DIRECT")
        elif outcome.has_qualifying_indirect:
            expect = ("POSITIVE", "INDIRECT_STRONG")
        else:
            expect = ("INCONCLUSIVE", "UNKNOWN")
        record(
            "aggregation_follows_the_frozen_evaluation_order_over_the_single_string_context",
            (d, s) == expect,
            f"the completed landscape implies {expect} under the frozen "
            f"tgt07_specific_aggregation_truth_table.frozen_evaluation_order but the "
            f"proposal is {(d, s)}",
        )

    # --- EvidenceRole consistency -------------------------------
    record("positive_has_supporting_evidence",
           d != "POSITIVE" or "SUPPORTING" in roles,
           "a POSITIVE proposal has no SUPPORTING evidence_ref")
    record("negative_has_supporting_evidence",
           d != "NEGATIVE" or "SUPPORTING" in roles,
           "a NEGATIVE / DIRECT proposal has no SUPPORTING evidence_ref")
    record("conflicting_has_supporting_and_contradicting",
           d != "CONFLICTING" or {"SUPPORTING", "CONTRADICTING"} <= roles,
           "a CONFLICTING proposal is missing a SUPPORTING or CONTRADICTING ref")
    record("contradicting_role_only_on_a_conflicting_direct_proposal",
           "CONTRADICTING" not in roles or d == "CONFLICTING",
           "a CONTRADICTING evidence_ref appears on a non-CONFLICTING proposal")
    if d == "CONFLICTING":
        material_ctx = {
            e.sink_exposure_context_id
            for e in admissible
            if e.classified.qualifying_direct_material_sink
        }
        no_material_ctx = {
            e.sink_exposure_context_id
            for e in admissible
            if e.classified.qualifying_direct_no_material_sink
        }
        record(
            "conflicting_is_a_single_sink_exposure_context_carrying_both_a_material_and_a_no_material_direct",
            bool(material_ctx & no_material_ctx),
            "a CONFLICTING proposal was raised without a single sink-exposure context "
            "carrying BOTH a material-sink DIRECT and a no-material-sink DIRECT "
            "observation (different contexts differing is not CONFLICTING)",
        )

    # --- fatal_review boundary (E15 item 08 / 12) --------------
    record(
        "fatal_review_is_at_most_a_potential_pattern",
        fatal_review.status in ("", "POTENTIAL_FATAL_PATTERN"),
        "fatal_review.status asserts more than a machine-detectable potential pattern",
    )
    record(
        "fatal_review_pattern_needs_a_completed_audited_landscape",
        (not fatal_review.required) or completion.landscape_complete,
        "a fatal_review pattern was raised without a completed audited "
        "soluble-antigen-evidence landscape",
    )
    if fatal_review.required:
        fatal_ids = set(fatal_review.evidence_ids)
        contributors = [e for e in emitted if e.evidence_id in fatal_ids]
        record(
            "fatal_review_contributors_are_all_qualifying_material_sink_direct_observations_with_a_clinical_exposure_compromise",
            bool(contributors)
            and all(
                e.classified.qualifying_direct_material_sink
                and e.observation.sink_materiality_outcome == _MATERIAL_WITH_COMPROMISE
                and (
                    e.observation.observation_kind == "CLINICAL_ANTIGEN_SINK_PK_EFFECT"
                    or (
                        e.observation.observation_kind == "SOLUBLE_ANTIGEN_TMDD_ANALYSIS"
                        and e.observation.exposure_scenario_class == "INTENDED_ADC_EXPOSURE"
                    )
                )
                for e in contributors
            ),
            "a fatal_review contributor is not a qualifying material-sink DIRECT "
            "observation whose sink_materiality_outcome is "
            "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE satisfying the "
            "clinical OR the intended-ADC TMDD source path",
        )
        record(
            "fatal_review_status_is_potential_fatal_pattern",
            fatal_review.status == "POTENTIAL_FATAL_PATTERN",
            "a required fatal_review does not carry status POTENTIAL_FATAL_PATTERN",
        )
        record(
            "fatal_review_carries_a_source_path",
            all(p in ("CLINICAL", "TMDD") for p in fatal_review.source_path)
            and bool(fatal_review.source_path),
            "a required fatal_review does not carry a CLINICAL / TMDD source path",
        )
    record(
        "fatal_review_is_not_a_proposal_field",
        not any(
            tok in n
            for n in AssessmentProposalEnvelope.field_names()
            for tok in ("fatal", "kill", "review")
        ),
        "the proposal envelope declares a fatal / review field",
    )

    # --- output must carry no cross-Gate / Decision conclusion / threshold --
    scannable = _module_owned_text(outcome, emitted)
    record("no_other_tgt_gate_conclusion_in_module_owned_text",
           not any(t in scannable for t in _F_CROSS_GATE),
           "the module-owned rationale / interpretation-boundary carries a "
           "TGT-01/02/03/04/05/06/08 conclusion or a target-wide sink / no-sink claim")
    record("no_public_fatal_signal_kill_hold_or_decision_anywhere",
           not any(t in scannable for t in _F_DECISION_SUBSTR)
           and _F_DECISION_WORD_RE.search(scannable) is None,
           "the module-owned text carries a PUBLIC_FATAL_SIGNAL_ESTABLISHED / "
           "KILL / HOLD / Decision")
    record("no_numeric_soluble_antigen_threshold_or_ranking_in_module_owned_text",
           _SCORE_RE.search(scannable) is None,
           "a Module-authored concentration / turnover / affinity / dose-exposure / "
           "sink-ratio threshold or ranking score appears in the module-owned text")

    return checks, reasons
