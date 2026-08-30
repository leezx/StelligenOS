"""Machine acceptance for a MOD-TGT02 run: the E7 item-13 checklist turned into
executable checks (E8-7).

A HARD identity / provenance / completion-consistency / classification-
qualification failure rejects the WHOLE run (proposal = None); it is never
degraded to an accepted UNKNOWN. UNKNOWN from a genuinely incomplete public CRC
coverage search is NOT an integrity failure.
"""

from __future__ import annotations

import re

from .aggregate import AggregationOutcome
from .completion import CrcCohortCoverageCompletion
from .contracts import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    AssessmentProposalEnvelope,
    EmittedEvidence,
    FatalReviewRecord,
    Tgt02ModuleInput,
)

_GRADED = ("DIRECT", "INDIRECT_STRONG")

# forbidden CONCLUSION wording the module's own templates never produce; scanned
# over each emitted EP's directly_supports + the aggregation rationale.
_F_CROSS_GATE = (
    "persistence after treatment", "metastatic persistence", "cell surface",
    "surface availability", "antigen density", "internalis", "internaliz",
    "therapeutic index", "therapeutic window",
)
_F_DECISION_SUBSTR = ("public_fatal_signal_established", "should be killed", "fatal flag")
_F_DECISION_WORD_RE = re.compile(r"\b(kill|killed|hold|holds|decision|decisions)\b", re.I)
_SCORE_RE = re.compile(
    r"\b\d[\d,.]*\s*(%|-fold|percent|cells|tpm|fpkm|nmol|per cell|cohorts|cohort)\b"
    r"|\bh-?score\b|\bscore\s*=|\branking\b|\bcutoff\b|\bthreshold of\b",
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
    completion: CrcCohortCoverageCompletion,
    fatal_review: FatalReviewRecord,
    hard_integrity_failures: list[tuple[str, str]],
    module_input: Tgt02ModuleInput,
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

    # --- identity / hygiene ------------------------------------------------
    record(
        "no_hard_identity_provenance_or_completion_integrity_failure",
        not hard_integrity_failures,
        "hard identity / provenance / completion-consistency / classification-"
        "qualification integrity failure(s): "
        + "; ".join(f"{i}: {why}" for i, why in hard_integrity_failures),
    )
    record(
        "one_evidence_package_per_observation",
        len(ep_ids) == len(set(ep_ids)),
        "an observation does not map to exactly one EvidencePackage",
    )
    record(
        "every_emitted_observation_has_a_resolved_primary_or_repository_source",
        all(e.observation.primary_or_repository_source_resolved for e in emitted),
        "an emitted observation lacks a resolved primary / repository source",
    )
    keys = [(e.observation.source_id, e.observation.claim.strip()) for e in emitted]
    record(
        "no_duplicate_source_claim_among_emitted",
        len(keys) == len(set(keys)),
        "a duplicate (source_id, claim) reached an emitted package",
    )
    emitted_ids = set(ep_ids)
    ref_ids = [eid for eid, _ in outcome.evidence_refs]
    record(
        "every_evidence_ref_points_at_one_emitted_or_reused_package",
        all(eid in emitted_ids for eid in ref_ids) and len(ref_ids) == len(set(ref_ids)),
        "an evidence_ref is dangling or repeated",
    )

    # --- freshness -------------------------------------------------------
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

    # --- frozen ladder hard locks (E7 item 05 / 09 / 13) -----------------
    transcript_above_is = [
        e for e in admissible
        if e.observation.molecular_layer == "TRANSCRIPT"
        and e.classified.evidence_rung == "DIRECT"
    ]
    record(
        "transcript_level_evidence_never_proposes_above_indirect_strong",
        not transcript_above_is,
        "a transcript-level observation was classified DIRECT",
    )
    bad_malignant = [
        e for e in admissible
        if e.observation.observation_kind in ("BULK_CRC_RNA", "PAN_CANCER_UNRESOLVED")
        and e.classified.evidence_rung not in ("WEAK", "")
    ]
    record(
        "bulk_or_pan_cancer_never_becomes_malignant_cell_attributed_rung",
        not bad_malignant,
        "a bulk / pan-cancer observation reached a rung above WEAK",
    )
    protein_no_attr_direct = [
        e for e in admissible
        if e.classified.evidence_rung == "DIRECT"
        and not (
            e.observation.is_protein_layer
            and e.observation.is_malignant_attributed
            and e.observation.is_validated_protein_assay
            and e.observation.is_cohort_qualified
            and e.observation.crc_specific
        )
    ]
    record(
        "protein_without_validated_malignant_qualified_cohort_never_reaches_direct",
        not protein_no_attr_direct,
        "a DIRECT rung was assigned without a validated protein assay + "
        "malignant-cell attribution + a QUALIFIED CRC cohort",
    )

    # --- qualification bases (E7 item 13) ------------------------------
    missing_basis = [
        e for e in admissible
        if (
            (e.observation.cohort_adequacy_status == "QUALIFIED"
             and not e.observation.cohort_adequacy_basis.strip())
            or (e.observation.is_negative_coverage_pattern
                and (not e.observation.expression_pattern_basis
                     or not e.observation.expression_pattern_basis_detail.strip()))
        )
    ]
    record(
        "every_qualified_or_negative_coverage_observation_carries_an_auditable_basis",
        not missing_basis,
        "a QUALIFIED cohort adequacy status or an ABSENT / "
        "RARE_HIGHLY_HETEROGENEOUS expression pattern is missing its auditable basis",
    )

    # --- no early one-cohort grade (E7 item 16) -----------------------
    needs_complete_landscape = d in ("POSITIVE", "NEGATIVE", "CONFLICTING") or (
        d == "INCONCLUSIVE" and s in _GRADED
    )
    record(
        "graded_direction_requires_a_completed_audited_crc_coverage_landscape",
        (not needs_complete_landscape) or completion.landscape_complete,
        "a graded Direction x Strength was proposed before the mandatory CRC "
        "coverage landscape was complete and audited (a single positive / "
        "negative cohort is never a completed population-level answer)",
    )

    # --- Direction x Strength == the frozen item-06 truth table ---------
    record(
        "direction_strength_pair_is_a_legal_tgt02_pair",
        (d, s) in LEGAL_DIRECTION_STRENGTH_PAIRS,
        f"Direction x Strength {(d, s)} is not a legal TGT-02 pair "
        "(note: TGT-02 has no INCONCLUSIVE / WEAK)",
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
        "the proposal carries the WEAK strength -- TGT-02 maps a WEAK-only public "
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

    # --- EvidenceRole consistency ------------------------------------
    record("positive_has_supporting_evidence",
           d != "POSITIVE" or "SUPPORTING" in roles,
           "a POSITIVE proposal has no SUPPORTING evidence_ref")
    record("negative_has_contradicting_evidence",
           d != "NEGATIVE" or "CONTRADICTING" in roles,
           "a NEGATIVE proposal has no CONTRADICTING evidence_ref")
    record("conflicting_has_supporting_and_contradicting",
           d != "CONFLICTING" or {"SUPPORTING", "CONTRADICTING"} <= roles,
           "a CONFLICTING proposal is missing a SUPPORTING or CONTRADICTING ref")

    # --- fatal_review boundary (E7 item 08 / 12) --------------------
    record(
        "fatal_review_is_at_most_a_potential_pattern",
        fatal_review.status in ("", "POTENTIAL_FATAL_PATTERN"),
        "fatal_review.status asserts more than a machine-detectable potential pattern",
    )
    record(
        "fatal_review_pattern_needs_a_completed_audited_landscape",
        (not fatal_review.required) or completion.landscape_complete,
        "a fatal_review pattern was raised without a completed audited CRC "
        "coverage landscape",
    )
    record(
        "fatal_review_pattern_spans_at_least_two_independent_cohorts",
        (not fatal_review.required) or len(set(fatal_review.cohort_ids)) >= 2,
        "a fatal_review pattern was raised without at least two independent cohort_ids",
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

    # --- output must carry no cross-Gate / Decision conclusion ---------
    facts = _ep_fact_text(emitted)
    scannable = " ".join(
        [outcome.aggregation_rationale.lower(), facts]
        + [u.lower() for u, _ in outcome.critical_unknowns]
    )
    record("no_tgt03_tgt04_or_tgt05_conclusion_in_evidence_or_rationale",
           not any(t in scannable for t in _F_CROSS_GATE),
           "an emitted EvidencePackage or the rationale carries a TGT-03 "
           "persistence / TGT-04 surface-density / TGT-05 therapeutic-index conclusion")
    record("no_public_fatal_signal_kill_hold_or_decision_anywhere",
           not any(t in scannable for t in _F_DECISION_SUBSTR)
           and _F_DECISION_WORD_RE.search(scannable) is None,
           "an emitted EvidencePackage or the rationale carries a "
           "PUBLIC_FATAL_SIGNAL_ESTABLISHED / KILL / HOLD / Decision")
    record("no_numeric_or_ranking_score_or_cohort_size_threshold",
           _SCORE_RE.search(scannable) is None,
           "a numeric / ranking score or a cohort-size / %-positive / H-score / "
           "heterogeneity threshold appears in the proposal / evidence")

    return checks, reasons
