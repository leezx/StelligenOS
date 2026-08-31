"""Machine acceptance for a MOD-TGT03 run: the E9 item-13 checklist turned into
executable checks (E10-8). This module executes item 13 (machine acceptance),
item 10 (input / binding invariants), item 11 (EP integrity), item 12 (proposal
/ fatal-review structural boundary) and item 16 (completion-before-grade). It is
NOT a "17-item YAML parser" -- items 03-09 science lives in classify / aggregate
/ completion / fatal, and items 14 / 17 are human / downstream responsibilities.

A HARD identity / provenance / completion-consistency / classification-
qualification failure rejects the WHOLE run (proposal = None); it is never
degraded to an accepted UNKNOWN. UNKNOWN from a genuinely incomplete public
clinical-persistence search is NOT an integrity failure.
"""

from __future__ import annotations

import re

from .aggregate import AggregationOutcome
from .completion import ClinicalPersistenceCompletion
from .contracts import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    AssessmentProposalEnvelope,
    EmittedEvidence,
    FatalReviewRecord,
    Tgt03ModuleInput,
)

_GRADED = ("DIRECT", "INDIRECT_STRONG")

# forbidden CONCLUSION wording the module's own templates never produce; scanned
# over each emitted EP's directly_supports + the aggregation rationale.
_F_CROSS_GATE = (
    "baseline malignant-cell coverage established", "adequate cohort-level consistency",
    "cell surface", "surface availability", "antigen density", "internalis", "internaliz",
    "localization established", "surface density established",
)
_F_DECISION_SUBSTR = ("public_fatal_signal_established", "should be killed", "fatal flag")
_F_DECISION_WORD_RE = re.compile(r"\b(kill|killed|hold|holds|decision|decisions)\b", re.I)
_SCORE_RE = re.compile(
    r"\b\d[\d,.]*\s*(%|-fold|percent|cells|tpm|fpkm|nmol|per cell|contexts|cohorts|cohort)\b"
    r"|\bh-?score\b|\bscore\s*=|\branking\b|\bcutoff\b|\bthreshold of\b|\bfold[- ]change\b",
    re.I,
)


def _ep_fact_text(emitted: list[EmittedEvidence]) -> str:
    parts: list[str] = []
    for e in emitted:
        ib = e.package.interpretation_boundary
        parts.extend(ib["directly_supports"])
    return " ".join(parts).lower()


def evaluate(
    *,
    emitted: list[EmittedEvidence],
    outcome: AggregationOutcome,
    completion: ClinicalPersistenceCompletion,
    fatal_review: FatalReviewRecord,
    hard_integrity_failures: list[tuple[str, str]],
    module_input: Tgt03ModuleInput,
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

    # --- frozen ladder hard locks (E9 item 05 / 09 / 13) ---------------
    transcript_or_model_direct = [
        e for e in admissible
        if e.observation.observation_kind in ("TREATED_METASTATIC_TRANSCRIPT", "RESISTANCE_MODEL")
        and e.classified.evidence_rung == "DIRECT"
    ]
    record(
        "transcript_or_resistance_model_never_proposes_above_indirect_strong",
        not transcript_or_model_direct,
        "a transcript / resistance-model observation was classified DIRECT",
    )
    weak_above = [
        e for e in admissible
        if e.observation.observation_kind in ("TREATMENT_NAIVE_PRIMARY", "DIFFERENT_TUMOR_TYPE")
        and e.classified.evidence_rung not in ("WEAK", "")
    ]
    record(
        "treatment_naive_primary_or_different_tumor_never_becomes_a_persistence_claim",
        not weak_above,
        "a treatment-naive primary CRC / different-tumor observation reached a rung above WEAK",
    )
    protein_no_qual_direct = [
        e for e in admissible
        if e.classified.evidence_rung == "DIRECT"
        and not (
            e.observation.is_protein_layer
            and e.observation.is_malignant_attributed
            and e.observation.is_protein_measurement_qualified
            and e.observation.is_context_qualified
            and e.observation.crc_specific
        )
    ]
    record(
        "protein_without_qualified_validation_malignant_attribution_and_qualified_context_never_reaches_direct",
        not protein_no_qual_direct,
        "a DIRECT rung was assigned without protein_measurement_validation_status "
        "== QUALIFIED + malignant-cell attribution + a QUALIFIED CRC context",
    )

    # --- qualification bases (E9 item 13) -----------------------------
    missing_basis = [
        e for e in admissible
        if (
            (e.observation.context_adequacy_status == "QUALIFIED"
             and (not e.observation.context_adequacy_basis.strip()
                  or not e.observation.clinical_context_basis.strip()))
            or (e.observation.persistence_pattern in ("NEAR_LOSS_OR_MARKED_LOSS",
                                                     "TRANSIENT_OR_MINOR_DOWNREGULATION")
                and not e.observation.persistence_pattern_basis)
            or (e.observation.protein_measurement_validation_status == "QUALIFIED"
                and not e.observation.protein_measurement_validation_basis.strip())
        )
    ]
    record(
        "every_qualified_or_loss_or_transient_observation_carries_an_auditable_basis",
        not missing_basis,
        "a QUALIFIED context adequacy status, a QUALIFIED protein measurement "
        "validation status, or a NEAR_LOSS_OR_MARKED_LOSS / "
        "TRANSIENT_OR_MINOR_DOWNREGULATION persistence pattern is missing its auditable basis",
    )
    bad_transient = [
        e for e in admissible
        if e.observation.persistence_pattern == "TRANSIENT_OR_MINOR_DOWNREGULATION"
        and (
            e.classified.persistence_implication == "OPPOSES_PERSISTENCE"
            or e.observation.residual_target_presence_status not in ("PRESENT", "UNRESOLVED")
        )
    ]
    record(
        "transient_or_minor_downregulation_never_opposes_and_carries_a_typed_residual_status",
        not bad_transient,
        "a TRANSIENT_OR_MINOR_DOWNREGULATION observation was scored OPPOSES_PERSISTENCE "
        "or lacks a typed residual_target_presence_status",
    )

    # --- no early grade (E9 item 16) --------------------------------
    needs_complete_landscape = d in ("POSITIVE", "NEGATIVE", "CONFLICTING") or (
        d == "INCONCLUSIVE" and s in _GRADED
    )
    record(
        "graded_direction_requires_a_completed_audited_persistence_landscape",
        (not needs_complete_landscape) or completion.landscape_complete,
        "a graded Direction x Strength was proposed before the mandatory "
        "clinical-persistence landscape was complete and audited",
    )

    # --- Direction x Strength == the frozen item-06 truth table -------
    record(
        "direction_strength_pair_is_a_legal_tgt03_pair",
        (d, s) in LEGAL_DIRECTION_STRENGTH_PAIRS,
        f"Direction x Strength {(d, s)} is not a legal TGT-03 pair "
        "(note: TGT-03 has no INCONCLUSIVE / WEAK)",
    )
    if s in _GRADED:
        expected = "DIRECT" if outcome.has_qualifying_direct else "INDIRECT_STRONG"
        record(
            "overall_strength_equals_the_highest_qualifying_evidence_class",
            s == expected,
            f"proposed_strength {s} != the highest qualifying evidence class {expected}",
        )
    record(
        "weak_only_or_incomplete_landscape_is_inconclusive_unknown_never_weak",
        s != "WEAK",
        "the proposal carries the WEAK strength -- TGT-03 maps a WEAK-only public "
        "landscape to INCONCLUSIVE / UNKNOWN",
    )
    record(
        "unknown_carries_no_evidence_refs",
        not (d == "INCONCLUSIVE" and s == "UNKNOWN") or not outcome.evidence_refs,
        "the INCONCLUSIVE / UNKNOWN state carries evidence_refs",
    )
    record(
        "graded_inconclusive_carries_contextual_evidence_refs",
        not (d == "INCONCLUSIVE" and s in _GRADED)
        or ("CONTEXTUAL" in roles and bool(outcome.evidence_refs)),
        "a graded INCONCLUSIVE proposal has no CONTEXTUAL evidence_ref",
    )

    # --- EvidenceRole consistency ---------------------------------
    record("positive_has_supporting_evidence",
           d != "POSITIVE" or "SUPPORTING" in roles,
           "a POSITIVE proposal has no SUPPORTING evidence_ref")
    record("negative_has_contradicting_evidence",
           d != "NEGATIVE" or "CONTRADICTING" in roles,
           "a NEGATIVE proposal has no CONTRADICTING evidence_ref")
    record("conflicting_has_supporting_and_contradicting",
           d != "CONFLICTING" or {"SUPPORTING", "CONTRADICTING"} <= roles,
           "a CONFLICTING proposal is missing a SUPPORTING or CONTRADICTING ref")

    # --- fatal_review boundary (E9 item 08 / 12) -----------------
    record(
        "fatal_review_is_at_most_a_potential_pattern",
        fatal_review.status in ("", "POTENTIAL_FATAL_PATTERN"),
        "fatal_review.status asserts more than a machine-detectable potential pattern",
    )
    record(
        "fatal_review_pattern_needs_a_completed_audited_landscape",
        (not fatal_review.required) or completion.landscape_complete,
        "a fatal_review pattern was raised without a completed audited "
        "clinical-persistence landscape",
    )
    if fatal_review.required:
        route_b = len(set(fatal_review.persistence_context_ids)) >= 2
        route_a = bool(fatal_review.reproducibility_basis_refs)
        record(
            "fatal_review_pattern_satisfies_route_a_or_route_b",
            route_a or route_b,
            "a fatal_review pattern was raised without Route A (a reproducibility "
            "basis ref) or Route B (>= 2 independent persistence_context_ids)",
        )
        record(
            "fatal_review_contributors_are_all_near_loss_or_marked_loss",
            set(fatal_review.persistence_class) == {"NEAR_LOSS_OR_MARKED_LOSS"},
            "a fatal_review contributor is not NEAR_LOSS_OR_MARKED_LOSS",
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

    # --- output must carry no cross-Gate / Decision conclusion -------
    facts = _ep_fact_text(emitted)
    scannable = " ".join(
        [outcome.aggregation_rationale.lower(), facts]
        + [u.lower() for u, _ in outcome.critical_unknowns]
    )
    record("no_tgt02_substitution_or_tgt04_conclusion_in_evidence_or_rationale",
           not any(t in scannable for t in _F_CROSS_GATE),
           "an emitted EvidencePackage or the rationale carries a TGT-02 "
           "baseline-coverage substitution or a TGT-04 surface / density conclusion")
    record("no_public_fatal_signal_kill_hold_or_decision_anywhere",
           not any(t in scannable for t in _F_DECISION_SUBSTR)
           and _F_DECISION_WORD_RE.search(scannable) is None,
           "an emitted EvidencePackage or the rationale carries a "
           "PUBLIC_FATAL_SIGNAL_ESTABLISHED / KILL / HOLD / Decision")
    record("no_numeric_or_ranking_score_or_context_count_threshold",
           _SCORE_RE.search(scannable) is None,
           "a numeric / ranking score or a context-count / %-positive / H-score / "
           "fold-change threshold appears in the proposal / evidence")

    return checks, reasons
