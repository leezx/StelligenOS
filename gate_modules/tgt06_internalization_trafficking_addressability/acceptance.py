"""Machine acceptance for a MOD-TGT06 run: the E13 item-13 checklist turned into
executable checks (E14-8). This module executes item 13 (machine acceptance),
item 10 (input / binding invariants), item 11 (EP integrity), item 12 (proposal
/ fatal-review structural boundary) and item 16 (completion-before-grade). It is
NOT a "17-item YAML parser" -- items 03-09 science lives in classify / aggregate
/ completion / fatal, and items 14 / 17 are human / downstream responsibilities.

A HARD identity / provenance / completion-consistency / classification-
qualification failure rejects the WHOLE run (proposal = None); it is never
degraded to an accepted UNKNOWN. UNKNOWN from a genuinely incomplete public
internalization search, or from a completed landscape with only WEAK / no
qualifying evidence, is NOT an integrity failure.

E14-6 tightening 6: the "no numeric threshold" check scans only MODULE-OWNED text
(the aggregation rationale, the critical-unknown wording and the neutral
interpretation-boundary templates). A source-reported numeric assay fact lives in
the neutral ``claim`` and is NOT scanned -- it is evidence, not a threshold.
"""

from __future__ import annotations

import re

from .aggregate import AggregationOutcome
from .completion import InternalizationEvidenceCompletion
from .contracts import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    AssessmentProposalEnvelope,
    EmittedEvidence,
    FatalReviewRecord,
    Tgt06ModuleInput,
)

# forbidden CONCLUSION wording the module's own templates never produce; scanned
# over the aggregation rationale + critical unknowns + the neutral
# interpretation-boundary templates (NOT the source claim).
_F_CROSS_GATE = (
    "baseline malignant-cell coverage established", "coverage established",
    "persistence established", "materially impaired persistence",
    "surface density", "antigen density", "surface availability",
    "the target is internalizing", "the target is non-internalizing",
)
_F_DECISION_SUBSTR = ("public_fatal_signal_established", "should be killed", "fatal flag")
_F_DECISION_WORD_RE = re.compile(r"\b(kill|killed|hold|holds|decision|decisions)\b", re.I)
#: MODULE-authored numeric / threshold DECISION language only (E14-6 tightening 6)
#: -- NOT a source-reported factual measurement (which lives in the neutral claim,
#: never scanned here).
_SCORE_RE = re.compile(
    r"\bh-?score\b|\bscore\s*=|\branking\b|\bcutoff\b|\bthreshold of\b|\bthreshold\b"
    r"|\bfold[- ]change\b|\badc-effective\b|\beffective internalization rate\b"
    r"|\bcolocalization coefficient\s*[<>=]|\bhalf-life\s*(?:cutoff|threshold|[<>=])"
    r"|\bif\s+\w*internali\w*\s*[<>=]"
    r"|(?:above|below)\s+[\d,.]+\s*(?:%|percent|h\b|hours)"
    r"|\b\d[\d,.]*\s*(?:%|percent)\s+(?:cutoff|threshold|effective)\b",
    re.I,
)


def _module_owned_text(
    outcome: AggregationOutcome, emitted: list[EmittedEvidence]
) -> str:
    """MODULE-authored text only (E14-6 tightening 6): the aggregation rationale,
    the critical-unknown wording and each EP's ``directly_supports`` factual
    statement. The source-reported numeric assay fact lives in ``package.claim``
    and the fixed ``does_not_support`` / ``limitations`` / ``evidence_ceiling``
    boilerplate deliberately names KILL / Decision as things the package does NOT
    support -- both are excluded from the scan."""

    parts: list[str] = [outcome.aggregation_rationale]
    parts.extend(u for u, _ in outcome.critical_unknowns)
    for e in emitted:
        parts.extend(e.package.interpretation_boundary["directly_supports"])
    return " ".join(parts).lower()


def evaluate(
    *,
    emitted: list[EmittedEvidence],
    outcome: AggregationOutcome,
    completion: InternalizationEvidenceCompletion,
    fatal_review: FatalReviewRecord,
    hard_integrity_failures: list[tuple[str, str]],
    module_input: Tgt06ModuleInput,
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

    # --- freshness ------------------------------------------------------
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

    # --- frozen ladder hard locks (E13 item 05 / 09 / 13) -------------
    non_integrated_direct = [
        e for e in admissible
        if e.classified.evidence_rung == "DIRECT"
        and e.observation.observation_kind not in (
            "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
            "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
            "TRAFFICKING_OR_RECYCLING_ONLY",
        )
    ]
    record(
        "only_an_antibody_configuration_internalization_or_trafficking_observation_reaches_direct",
        not non_integrated_direct,
        "a non-internalization / trafficking observation was classified DIRECT",
    )
    productive_not_integrated = [
        e for e in admissible
        if e.classified.qualifying_direct_productive
        and (
            e.observation.observation_kind != "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING"
            or e.observation.internalization_outcome
            != "PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"
        )
    ]
    record(
        "a_productive_direct_contributor_is_one_integrated_configuration_observation",
        not productive_not_integrated,
        "a qualifying productive DIRECT observation is not a single integrated "
        "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING observation with "
        "internalization_outcome PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY "
        "(DIRECT is never synthesized across observations)",
    )
    weak_above = [
        e for e in admissible
        if e.observation.observation_kind in (
            "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
            "SURFACE_LOCALIZATION_ONLY_INFERENCE",
        )
        and e.classified.evidence_rung not in ("WEAK", "")
    ]
    record(
        "receptor_family_or_surface_localization_inference_never_rises_above_weak",
        not weak_above,
        "a receptor-family-membership / surface-localization-only inference "
        "observation reached a rung above WEAK",
    )
    indirect_above = [
        e for e in admissible
        if e.observation.observation_kind in (
            "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
            "SAME_TARGET_ADC_DELIVERY_PRECEDENT",
        )
        and e.classified.evidence_rung == "DIRECT"
    ]
    non_crc_direct = [
        e for e in admissible
        if e.observation.surface_context_class == "NON_CRC_CONTEXT"
        and e.classified.evidence_rung == "DIRECT"
    ]
    record(
        "constitutive_receptor_biology_same_target_adc_precedent_and_non_crc_internalization_never_reach_direct",
        not indirect_above and not non_crc_direct,
        "a constitutive-endocytosis / internalizing-receptor biology observation, "
        "a successful same-target ADC functional-delivery precedent, or a non-CRC "
        "antibody-induced internalization observation was classified DIRECT",
    )
    delivery_unresolved_direct = [
        e for e in admissible
        if e.observation.internalization_outcome
        == "INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED"
        and e.classified.evidence_rung == "DIRECT"
    ]
    record(
        "internalization_observed_but_lysosomal_delivery_unresolved_never_reaches_direct",
        not delivery_unresolved_direct,
        "an INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED observation was "
        "classified DIRECT (it is positive support at INDIRECT_STRONG ceiling only)",
    )
    direct_without_qualification = [
        e for e in admissible
        if e.classified.is_qualifying_direct
        and not (
            e.observation.is_configuration_resolved
            and e.observation.is_disease_relevant_context
            and e.observation.assay_validation_status == "QUALIFIED"
            and e.observation.assay_method.strip()
        )
    ]
    record(
        "a_qualifying_direct_rung_observation_carries_a_qualified_context_a_qualified_assay_and_a_disclosed_configuration",
        not direct_without_qualification,
        "a qualifying DIRECT-rung observation was assigned without a QUALIFIED "
        "disease-relevant context + auditable bases, assay_validation_status == "
        "QUALIFIED + a non-empty assay_method, and a SINGLE / IDENTIFIED_MULTI "
        "configuration identity",
    )
    bare_crc_direct = [
        e for e in admissible
        if e.classified.is_qualifying_direct
        and e.observation.context_adequacy_status != "QUALIFIED"
    ]
    record(
        "a_bare_crc_specific_flag_never_reaches_a_direct_rung",
        not bare_crc_direct,
        "a DIRECT rung was assigned on a context with context_adequacy_status != QUALIFIED",
    )

    # --- configuration identity states + local namespace (item 13) ---------
    bad_state = []
    for e in admissible:
        st = e.observation.configuration_identity_state
        if st not in ("SINGLE", "IDENTIFIED_MULTI", "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE"):
            bad_state.append(e)
        if e.classified.is_qualifying_direct and st == "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE":
            bad_state.append(e)
    record(
        "configuration_identity_is_exactly_one_of_the_three_frozen_states_and_direct_quality_evidence_discloses_it",
        not bad_state,
        "an observation carries an illegal configuration-identity state, or a "
        "DIRECT-quality observation is in the IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE state",
    )
    missing_direct_config = [
        e for e in admissible
        if e.classified.is_qualifying_direct and not e.classified.configuration_identities
    ]
    record(
        "every_qualifying_direct_rung_observation_carries_at_least_one_local_configuration_id",
        not missing_direct_config,
        "a qualifying DIRECT-rung observation carries no auditable local "
        "internalization_configuration_id",
    )

    # --- qualification bases (E13 item 06 / 13) --------------------
    missing_basis = [
        e for e in admissible
        if (
            (e.observation.surface_context_class in ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL", "NON_CRC_CONTEXT")
             and not e.observation.surface_context_basis.strip())
            or (e.observation.context_adequacy_status == "QUALIFIED"
                and not e.observation.context_adequacy_basis.strip())
            or (e.observation.assay_validation_status == "QUALIFIED"
                and not e.observation.assay_validation_basis.strip())
            or (e.observation.internalization_outcome != "NOT_ESTABLISHED"
                and not e.observation.internalization_outcome_basis.strip())
            or (e.observation.reproducibility_status == "QUALIFIED"
                and not e.observation.reproducibility_basis.strip())
            or (e.observation.declared_multi_configuration_analysis
                and not e.observation.configuration_identity_basis.strip())
        )
    ]
    record(
        "every_classification_driving_qualified_status_carries_an_auditable_basis",
        not missing_basis,
        "a classification-driving qualified status (surface_context_class / "
        "context_adequacy_status / assay_validation_status / internalization_outcome "
        "/ reproducibility_status / configuration identity) is missing its auditable basis",
    )
    canon_collision = [
        e for e in admissible
        if any(
            one.strip() == module_input.context_id
            for one in (
                e.observation.internalization_configuration_id,
                *e.observation.internalization_configuration_ids,
            )
        )
    ]
    record(
        "a_local_configuration_id_is_never_the_canonical_instantiation_context_id",
        not canon_collision,
        "an internalization_configuration_id collapses onto the canonical "
        "Instantiation context_id",
    )

    # --- no early grade (E13 item 16) -----------------------------
    needs_complete_landscape = d in ("POSITIVE", "NEGATIVE", "CONFLICTING") or (
        d == "INCONCLUSIVE" and s == "DIRECT"
    )
    record(
        "graded_direction_requires_a_completed_audited_internalization_landscape",
        (not needs_complete_landscape) or completion.landscape_complete,
        "a graded Direction x Strength was proposed before the mandatory "
        "internalization-evidence landscape was complete and audited",
    )

    # --- Direction x Strength == the frozen item-06 truth table ------
    record(
        "direction_strength_pair_is_a_legal_tgt06_pair",
        (d, s) in LEGAL_DIRECTION_STRENGTH_PAIRS,
        f"Direction x Strength {(d, s)} is not a legal TGT-06 pair (only "
        "POSITIVE/DIRECT, POSITIVE/INDIRECT_STRONG, NEGATIVE/DIRECT, "
        "CONFLICTING/DIRECT, INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN)",
    )
    record(
        "no_weak_proposed_strength",
        s != "WEAK",
        "the proposal carries the WEAK strength -- TGT-06 never proposes WEAK",
    )
    # only enforced on a COMPLETED landscape -- an incomplete landscape is always
    # INCONCLUSIVE / UNKNOWN regardless of what qualifying observations exist.
    strength_ok = (not completion.landscape_complete) or (
        (
            (s == "DIRECT")
            == (outcome.has_qualifying_direct_productive or outcome.has_qualifying_direct_failure)
        )
        and (
            (s == "INDIRECT_STRONG")
            == (
                outcome.has_qualifying_indirect
                and not outcome.has_qualifying_direct_productive
                and not outcome.has_qualifying_direct_failure
            )
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

    # --- EvidenceRole consistency -------------------------------
    record("positive_has_supporting_evidence",
           d != "POSITIVE" or "SUPPORTING" in roles,
           "a POSITIVE proposal has no SUPPORTING evidence_ref")
    # proposal-relative role (E14 review round-1 blocker 2B): a NEGATIVE / DIRECT
    # proposal's DIRECT-quality failure evidence SUPPORTS the NEGATIVE proposal.
    record("negative_has_supporting_evidence",
           d != "NEGATIVE" or "SUPPORTING" in roles,
           "a NEGATIVE / DIRECT proposal has no SUPPORTING evidence_ref")
    record("conflicting_has_supporting_and_contradicting",
           d != "CONFLICTING" or {"SUPPORTING", "CONTRADICTING"} <= roles,
           "a CONFLICTING proposal is missing a SUPPORTING or CONTRADICTING ref")
    # a CONTRADICTING role only ever appears on the same-configuration failure
    # half of a CONFLICTING / DIRECT pair.
    record("contradicting_role_only_on_a_conflicting_direct_proposal",
           "CONTRADICTING" not in roles or d == "CONFLICTING",
           "a CONTRADICTING evidence_ref appears on a non-CONFLICTING proposal")
    # different configurations behaving differently is NEVER CONFLICTING --
    # CONFLICTING requires a single configuration identity carrying BOTH a
    # productive DIRECT and a DIRECT-quality failure observation.
    if d == "CONFLICTING":
        prod_ids: set[str] = set()
        for e in admissible:
            if e.classified.qualifying_direct_productive:
                prod_ids |= set(e.classified.configuration_identities)
        fail_ids: set[str] = set()
        for e in admissible:
            if e.classified.qualifying_direct_failure:
                fail_ids |= set(e.classified.configuration_identities)
        record(
            "conflicting_is_a_single_configuration_carrying_both_a_productive_and_a_failure_observation",
            bool(prod_ids & fail_ids),
            "a CONFLICTING proposal was raised without a single configuration "
            "identity carrying BOTH a productive DIRECT and a DIRECT-quality "
            "failure observation (inter-configuration heterogeneity is not CONFLICTING)",
        )

    # --- fatal_review boundary (E13 item 08 / 12) --------------
    record(
        "fatal_review_is_at_most_a_potential_pattern",
        fatal_review.status in ("", "POTENTIAL_FATAL_PATTERN"),
        "fatal_review.status asserts more than a machine-detectable potential pattern",
    )
    record(
        "fatal_review_pattern_needs_a_completed_audited_landscape",
        (not fatal_review.required) or completion.landscape_complete,
        "a fatal_review pattern was raised without a completed audited "
        "internalization-evidence landscape",
    )
    if fatal_review.required:
        record(
            "fatal_review_has_no_qualifying_productive_direct_configuration",
            not outcome.has_qualifying_direct_productive,
            "a fatal_review pattern was raised while a qualifying productive DIRECT "
            "configuration exists on the landscape (global precondition violated)",
        )
        fatal_ids = set(fatal_review.evidence_ids)
        contributors = [e for e in emitted if e.evidence_id in fatal_ids]
        record(
            "fatal_review_contributors_are_all_direct_quality_failures_of_the_three_eligible_kinds",
            all(
                e.classified.qualifying_direct_failure
                and e.observation.observation_kind in (
                    "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
                    "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
                    "TRAFFICKING_OR_RECYCLING_ONLY",
                )
                and e.observation.internalization_outcome
                == "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"
                for e in contributors
            )
            and bool(contributors),
            "a fatal_review contributor is not a DIRECT-quality FAILS observation "
            "of an eligible kind",
        )
        n_obs = len(contributors)
        union_ids: set[str] = set()
        for e in contributors:
            union_ids |= set(e.classified.configuration_identities)
        route_a = any(
            e.observation.configuration_identity_state == "IDENTIFIED_MULTI"
            and len(e.classified.configuration_identities) >= 2
            and e.observation.is_reproducibility_qualified
            for e in contributors
        )
        route_b = n_obs >= 2 and len(union_ids) >= 2
        record(
            "fatal_review_pattern_satisfies_route_a_or_route_b",
            route_a or route_b,
            "a fatal_review pattern was raised without Route A (one IDENTIFIED_MULTI "
            "observation, projection >= 2, reproducibility QUALIFIED + basis) or "
            "Route B (>= 2 distinct eligible failure observations AND projected "
            "configuration union >= 2)",
        )
        record(
            "fatal_review_configuration_ids_span_at_least_two_independent_identities",
            len(set(fatal_review.configuration_ids)) >= 2,
            "a fatal_review pattern spans fewer than two independent configuration_ids",
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
    record("no_tgt02_tgt03_or_tgt04_conclusion_in_module_owned_text",
           not any(t in scannable for t in _F_CROSS_GATE),
           "the module-owned rationale / interpretation-boundary carries a TGT-02 "
           "baseline-coverage substitution, a TGT-03 persistence conclusion, a "
           "TGT-04 surface-availability conclusion, or a target-wide "
           "internalizing / non-internalizing claim")
    record("no_public_fatal_signal_kill_hold_or_decision_anywhere",
           not any(t in scannable for t in _F_DECISION_SUBSTR)
           and _F_DECISION_WORD_RE.search(scannable) is None,
           "the module-owned text carries a PUBLIC_FATAL_SIGNAL_ESTABLISHED / "
           "KILL / HOLD / Decision")
    record("no_numeric_internalization_threshold_or_ranking_in_module_owned_text",
           _SCORE_RE.search(scannable) is None,
           "a Module-authored numeric internalization-rate / half-life / "
           "percent-internalized / colocalization-coefficient threshold or "
           "ranking score appears in the module-owned text")

    return checks, reasons
