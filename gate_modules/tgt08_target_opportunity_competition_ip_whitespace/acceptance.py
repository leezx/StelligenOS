"""Machine acceptance for a MOD-TGT08 run: the E5 item-13 checklist turned into
executable checks (E6-7).

A HARD identity / provenance / completion-consistency / absence-provenance
failure rejects the WHOLE run (proposal = None); it is never degraded to an
accepted UNKNOWN. UNKNOWN from a genuinely incomplete landscape is NOT an
integrity failure.
"""

from __future__ import annotations

import re

from .aggregate import AggregationOutcome, audit_snapshot_mismatch
from .contracts import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    AssessmentProposalEnvelope,
    CompetitiveLandscapeCompletion,
    EmittedEvidence,
    PatentLandscapeCompletion,
    SponsorReviewRecord,
    Tgt08ModuleInput,
    overall_strength,
)

_GRADED = ("DIRECT", "INDIRECT_STRONG")

# forbidden CONCLUSION wording that the module's own templates never produce;
# scanned over each emitted EP's directly_supports + evidence_class (pure facts).
_F_FTO = (
    "freedom to operate", "freedom-to-operate", "will infringe", "infringement",
    "claim validity", "enforceability", "design-around", "design around",
    "legal clearance",
)
_F_STRATEGY = ("no differentiation path", "dominant", "well protected", "well-protected")
_F_SCIENCE = (
    "tgt-01", "tgt-02", "tgt-03", "tgt-04", "tgt-05", "tgt-06", "tgt-07",
    "de-risk", "scientifically",
)
_F_DECISION = ("kill", "stop_for_sponsor", "out_of_mandate", "decision")
_SCORE_RE = re.compile(
    r"\b\d[\d,.]*\s*(competitors|families|claims|%|-fold)|\bscore\s*=|\branking\b",
    re.I,
)


def _ep_fact_text(emitted: list[EmittedEvidence]) -> str:
    parts: list[str] = []
    for e in emitted:
        ib = e.package.interpretation_boundary
        parts.extend(ib["directly_supports"])
        parts.append(e.classified.evidence_class)
    return " ".join(parts).lower()


def evaluate(
    *,
    emitted: list[EmittedEvidence],
    outcome: AggregationOutcome,
    competitive: CompetitiveLandscapeCompletion,
    patent: PatentLandscapeCompletion,
    sponsor_review: SponsorReviewRecord,
    hard_integrity_failures: list[tuple[str, str]],
    module_input: Tgt08ModuleInput,
) -> tuple[list[tuple[str, bool]], list[str]]:
    """Return (ordered checks, failure reasons). ``accepted`` is ``all(ok)``."""

    checks: list[tuple[str, bool]] = []
    reasons: list[str] = []

    def record(name: str, ok: bool, why: str) -> None:
        checks.append((name, ok))
        if not ok:
            reasons.append(why)

    d, s = outcome.proposed_direction, outcome.proposed_strength
    roles = {r for _, r in outcome.evidence_refs}
    ep_ids = [e.evidence_id for e in emitted]

    # --- identity / hygiene ------------------------------------------------
    record(
        "no_hard_identity_or_provenance_integrity_failure",
        not hard_integrity_failures,
        "hard identity / provenance / completion integrity failure(s): "
        + "; ".join(f"{i}: {why}" for i, why in hard_integrity_failures),
    )
    record(
        "one_evidence_package_per_observation",
        len(ep_ids) == len(set(ep_ids)),
        "an observation does not map to exactly one EvidencePackage",
    )
    record(
        "every_emitted_record_has_a_resolved_primary_or_official_source",
        all(e.classified.record.primary_or_official_source_resolved for e in emitted),
        "an emitted record lacks a resolved primary / official source",
    )
    record(
        "only_frozen_tgt08_evidence_classes_emitted",
        all(e.classified.evidence_class for e in emitted),
        "an emitted record carries no frozen TGT-08 evidence class",
    )
    keys = [
        (e.classified.record.source_id, e.classified.record.claim.strip())
        for e in emitted
    ]
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
    fresh_ok = all(e.classified.record.landscape_as_of == as_of for e in emitted)
    if competitive.attempted:
        fresh_ok = fresh_ok and competitive.landscape_as_of == as_of
    if patent.attempted:
        fresh_ok = fresh_ok and patent.landscape_as_of == as_of
    record(
        "landscape_as_of_consistent_across_input_records_and_completions",
        fresh_ok,
        "an input record or completion state carries a landscape_as_of that "
        "disagrees with the run's landscape_as_of",
    )

    # --- completion <-> evidence consistency (E6-4) --------------------
    emitted_qualifying_programs = {
        e.classified.record.program_id
        for e in emitted
        if e.classified.observation_kind == "COMPETITOR_PROGRAM"
        and e.classified.qualifying_for_axis
    }
    record(
        "competitive_completion_consistent_with_emitted_records",
        set(competitive.qualifying_program_ids) == emitted_qualifying_programs,
        f"competitive_completion.qualifying_program_ids "
        f"{sorted(competitive.qualifying_program_ids)} != the qualifying competitor "
        f"EvidencePackages actually emitted {sorted(emitted_qualifying_programs)}",
    )
    emitted_qualifying_families = {
        e.classified.record.patent_family_id
        for e in emitted
        if e.classified.observation_kind == "PATENT_CLAIM"
        and e.classified.qualifying_for_axis
    }
    record(
        "patent_completion_consistent_with_emitted_records",
        set(patent.qualifying_patent_family_ids) == emitted_qualifying_families,
        f"patent_completion.qualifying_patent_family_ids "
        f"{sorted(patent.qualifying_patent_family_ids)} != the qualifying patent "
        f"EvidencePackages actually emitted {sorted(emitted_qualifying_families)}",
    )

    # --- completion audit snapshot parity (E6 round-1 blocker 1) --------
    audit_snapshot_ok = True
    audit_snapshot_why: list[str] = []
    for e in emitted:
        rec = e.classified.record
        if rec.observation_kind != "SEARCH_COMPLETION_AUDIT":
            continue
        why = audit_snapshot_mismatch(rec, competitive, patent)
        if why:
            audit_snapshot_ok = False
            audit_snapshot_why.append(f"{rec.observation_id}: {why}")
    record(
        "completion_audit_evidence_snapshots_its_typed_completion",
        audit_snapshot_ok,
        "; ".join(audit_snapshot_why),
    )

    # --- absence provenance (E6-4) -----------------------------------
    def _has_audit_ep(axis: str, obs_id: str) -> bool:
        return any(
            e.classified.observation_kind == "SEARCH_COMPLETION_AUDIT"
            and e.classified.record.evidence_axis == axis
            and e.classified.record.observation_id == obs_id
            for e in emitted
        )

    absence_ok = True
    absence_why: list[str] = []
    if outcome.competitive_absence_support and not _has_audit_ep(
        "COMPETITIVE", competitive.audit_observation_id
    ):
        absence_ok = False
        absence_why.append(
            "a competitive absence SUPPORT was derived without a backing "
            "SEARCH_COMPLETION_AUDIT EvidencePackage"
        )
    if outcome.patent_absence_support and not _has_audit_ep(
        "PATENT", patent.audit_observation_id
    ):
        absence_ok = False
        absence_why.append(
            "a patent absence SUPPORT was derived without a backing "
            "SEARCH_COMPLETION_AUDIT EvidencePackage"
        )
    record("absence_support_is_backed_by_a_completion_audit_evidence_package",
           absence_ok, "; ".join(absence_why))

    # --- frozen precedence / truth table (E6-3) ---------------------
    neither_attempted = not (competitive.attempted or patent.attempted)
    has_unmet_need = any(
        e.classified.observation_kind == "UNMET_NEED_CONTEXT" for e in emitted
    )
    if (d, s) == ("INCONCLUSIVE", "WEAK"):
        weak_ok = neither_attempted and has_unmet_need
    else:
        # a case that SHOULD have been WEAK must not be anything else
        weak_ok = not (neither_attempted and has_unmet_need)
    record(
        "weak_unmet_need_precedence_is_respected",
        weak_ok,
        "the unmet-need-only WEAK hypothesis vs incomplete-landscape UNKNOWN "
        "precedence was not respected",
    )

    both_evaluable = competitive.evaluable and patent.evaluable
    needs_two_axes = d in ("POSITIVE", "NEGATIVE", "CONFLICTING") or (
        d == "INCONCLUSIVE" and s in _GRADED
    )
    record(
        "target_specific_two_axis_completion_is_respected",
        (not needs_two_axes) or both_evaluable,
        "a target-specific graded assessment was proposed without both mandatory "
        "axes complete and evaluable",
    )

    if s in _GRADED:
        expected = overall_strength(outcome.competitive_ceiling, outcome.patent_ceiling)
        record(
            "overall_strength_equals_the_weaker_axis_ceiling",
            s == expected,
            f"proposed_strength {s} != the weaker required axis ceiling {expected}",
        )
        record(
            "direct_requires_both_axes_at_direct_authority",
            s != "DIRECT"
            or (outcome.competitive_ceiling == "DIRECT" and outcome.patent_ceiling == "DIRECT"),
            "an overall DIRECT was proposed without BOTH axes at DIRECT authority",
        )

    record(
        "direction_strength_pair_is_a_legal_tgt08_pair",
        (d, s) in LEGAL_DIRECTION_STRENGTH_PAIRS,
        f"Direction x Strength {(d, s)} is not a legal TGT-08 pair",
    )

    # --- EvidenceRole consistency ----------------------------------
    record("positive_has_supporting_evidence",
           d != "POSITIVE" or "SUPPORTING" in roles,
           "a POSITIVE proposal has no SUPPORTING evidence_ref")
    record("negative_has_contradicting_evidence",
           d != "NEGATIVE" or "CONTRADICTING" in roles,
           "a NEGATIVE proposal has no CONTRADICTING evidence_ref")
    record("conflicting_has_supporting_and_contradicting",
           d != "CONFLICTING" or {"SUPPORTING", "CONTRADICTING"} <= roles,
           "a CONFLICTING proposal is missing a SUPPORTING or CONTRADICTING ref")
    record("graded_inconclusive_has_contextual_evidence",
           not (d == "INCONCLUSIVE" and s in ("DIRECT", "INDIRECT_STRONG", "WEAK"))
           or ("CONTEXTUAL" in roles and bool(outcome.evidence_refs)),
           "a graded / WEAK INCONCLUSIVE proposal has no CONTEXTUAL evidence_ref")
    record("unknown_has_no_evidence_refs",
           not (d == "INCONCLUSIVE" and s == "UNKNOWN") or not outcome.evidence_refs,
           "the INCONCLUSIVE / UNKNOWN state carries evidence_refs")

    unmet_ep_ids = {
        e.evidence_id for e in emitted
        if e.classified.observation_kind == "UNMET_NEED_CONTEXT"
    }
    contradicting_from_unmet = any(
        eid in unmet_ep_ids for eid, r in outcome.evidence_refs if r == "CONTRADICTING"
    )
    record(
        "unmet_need_never_creates_a_target_specific_conflict",
        not contradicting_from_unmet,
        "an unmet-need EvidencePackage was scored CONTRADICTING (it is only ever "
        "a WEAK CONTEXTUAL hypothesis)",
    )

    # --- sponsor_review boundary (E6-5) ---------------------------
    record(
        "sponsor_review_is_at_most_a_potential_pattern",
        sponsor_review.status in ("", "POTENTIAL_SPONSOR_FATAL_PATTERN"),
        "sponsor_review.status asserts more than a machine-detectable potential pattern",
    )
    # E6 round-1 blocker 2: a sponsor_review trigger is a provisional-stop
    # handoff (E5 item 16) -- it is only actionable on a COMPLETED two-axis
    # landscape. A pattern found while a core axis is still incomplete (the run
    # would otherwise be an accepted INCONCLUSIVE / UNKNOWN) must NOT surface as
    # an actionable trigger; the run fails machine acceptance instead.
    record(
        "sponsor_review_requires_both_core_landscape_axes_complete",
        (not sponsor_review.required)
        or (competitive.coverage_complete and patent.coverage_complete),
        "a sponsor_review trigger was raised on an incomplete two-axis landscape "
        "(E5 item 16: the provisional stop still requires both core axes complete)",
    )
    record(
        "sponsor_review_is_not_a_proposal_field",
        not any(
            tok in n
            for n in AssessmentProposalEnvelope.field_names()
            for tok in ("sponsor", "fatal", "kill", "review")
        ),
        "the proposal envelope declares a sponsor / fatal field",
    )

    # --- output must carry no legal / strategic / scientific conclusion ---
    facts = _ep_fact_text(emitted)
    record("no_fto_infringement_or_design_around_conclusion_in_evidence",
           not any(t in facts for t in _F_FTO),
           "an emitted EvidencePackage carries an FTO / infringement / "
           "design-around conclusion")
    record("no_dominant_well_protected_or_no_differentiation_path_conclusion",
           not any(t in facts for t in _F_STRATEGY)
           and "dominant" not in outcome.aggregation_rationale.lower(),
           "an emitted EvidencePackage or the rationale asserts dominant / "
           "well-protected / no-differentiation-path")
    record("no_tgt01_through_tgt07_scientific_inference_in_evidence",
           not any(t in facts for t in _F_SCIENCE),
           "an emitted EvidencePackage carries a TGT-01..07 scientific inference")
    record("no_sponsor_decision_kill_stop_or_out_of_mandate_in_evidence",
           not any(t in facts for t in _F_DECISION),
           "an emitted EvidencePackage carries a KILL / Decision / STOP_FOR_SPONSOR "
           "/ OUT_OF_MANDATE")
    scannable = " ".join(
        [outcome.aggregation_rationale, facts]
        + [u for u, _ in outcome.critical_unknowns]
    )
    record("no_numeric_or_ranking_score",
           _SCORE_RE.search(scannable) is None,
           "a numeric threshold or ranking score appears in the proposal / evidence")

    return checks, reasons
