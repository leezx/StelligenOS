"""Machine acceptance for a MOD-TGT04 run: the E11 item-13 checklist turned into
executable checks (E12-8). This module executes item 13 (machine acceptance),
item 10 (input / binding invariants), item 11 (EP integrity), item 12 (proposal
/ fatal-review structural boundary) and item 16 (completion-before-grade). It is
NOT a "17-item YAML parser" -- items 03-09 science lives in classify / aggregate
/ completion / fatal, and items 14 / 17 are human / downstream responsibilities.

A HARD identity / provenance / completion-consistency / classification-
qualification failure rejects the WHOLE run (proposal = None); it is never
degraded to an accepted UNKNOWN. UNKNOWN from a genuinely incomplete public
surface-availability search, or from a completed landscape with no qualifying
DIRECT quantitative density evidence, is NOT an integrity failure.
"""

from __future__ import annotations

import re

from .aggregate import AggregationOutcome
from .completion import SurfaceAvailabilityCompletion
from .contracts import (
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    AssessmentProposalEnvelope,
    EmittedEvidence,
    FatalReviewRecord,
    Tgt04ModuleInput,
)

# forbidden CONCLUSION wording the module's own templates never produce; scanned
# over each emitted EP's directly_supports + the aggregation rationale.
_F_CROSS_GATE = (
    "baseline malignant-cell coverage established", "persistence established",
    "materially impaired persistence", "internalis", "internaliz",
    "receptor-mediated endocytosis", "adequate antigen density established",
    "the antigen density is inadequate for an adc", "clinically effective range",
    "clinically effective antigen-density range",
)
_F_DECISION_SUBSTR = ("public_fatal_signal_established", "should be killed", "fatal flag")
_F_DECISION_WORD_RE = re.compile(r"\b(kill|killed|hold|holds|decision|decisions)\b", re.I)
#: DECISION language only -- a Module-authored numeric cutoff / ranking / effective
#: range, NOT a raw factual measurement. A verbatim raw ``reported_density_*``
#: value / unit / summary an EP is SANCTIONED to preserve (E11 item 11) is
#: stripped from the scanned text first (see ``_scannable_ep_fact_text``), so a
#: legitimate "12000 molecules per cell by QIFIKIT" factual summary is never a
#: hit (E12 review round 1, blocker 1).
_SCORE_RE = re.compile(
    r"\bh-?score\b|\bscore\s*=|\branking\b|\bcutoff\b|\bthreshold of\b|\bthreshold\b"
    r"|\bfold[- ]change\b|\bclinically effective range\b"
    r"|(?:above|below)\s+[\d,.]+\s+(?:molecules|abc|%|percent)"
    r"|\b\d[\d,.]*\s*(%|percent)\s+(?:cutoff|threshold|effective)\b",
    re.I,
)


def _scannable_ep_fact_text(emitted: list[EmittedEvidence]) -> str:
    """The EP-level factual text scanned for forbidden CONCLUSION / threshold
    wording. A raw ``reported_density_value`` / ``reported_density_unit`` /
    ``reported_density_summary`` an EP is SANCTIONED to preserve as a factual
    measurement (E11 item 11) is removed verbatim first -- it is evidence, not a
    threshold (E12 review round 1, blocker 1). Anything the Module's own
    templates wrote stays scannable."""

    parts: list[str] = []
    for e in emitted:
        ib = e.package.interpretation_boundary
        text = " ".join(ib["directly_supports"])
        sc = e.package.study_context
        for key in ("reported_density_value", "reported_density_unit", "reported_density_summary"):
            raw = str(sc.get(key, "")).strip()
            if raw:
                text = text.replace(raw, " ")
        parts.append(text)
    return " ".join(parts).lower()


def evaluate(
    *,
    emitted: list[EmittedEvidence],
    outcome: AggregationOutcome,
    completion: SurfaceAvailabilityCompletion,
    fatal_review: FatalReviewRecord,
    hard_integrity_failures: list[tuple[str, str]],
    module_input: Tgt04ModuleInput,
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

    # --- frozen ladder hard locks (E11 item 05 / 09 / 13) -------------
    non_density_direct = [
        e for e in admissible
        if e.observation.observation_kind != "QUANTITATIVE_SURFACE_DENSITY"
        and e.classified.evidence_rung == "DIRECT"
    ]
    record(
        "only_a_quantitative_surface_density_observation_ever_reaches_direct",
        not non_density_direct,
        "a non-QUANTITATIVE_SURFACE_DENSITY observation was classified DIRECT",
    )
    model_indirect = [
        e for e in admissible
        if e.observation.surface_context_class != "CRC_MALIGNANT_CELLS"
        and e.classified.evidence_rung == "INDIRECT_STRONG"
    ]
    record(
        "an_indirect_strong_localization_rung_requires_crc_malignant_cells",
        not model_indirect,
        "an INDIRECT_STRONG rung was assigned on a WELL_MATCHED_CRC_MODEL / "
        "NON_CRC_MODEL / unresolved surface context",
    )
    weak_above = [
        e for e in admissible
        if e.observation.observation_kind in (
            "SUBCELLULAR_LOCALIZATION", "TOPOLOGY_OR_GO_PREDICTION",
            "NON_CRC_SURFACE_EVIDENCE", "RNA_SURFACE_PROXY",
        )
        and e.classified.evidence_rung not in ("WEAK", "")
    ]
    record(
        "subcellular_topology_non_crc_or_rna_proxy_never_rises_above_weak",
        not weak_above,
        "a subcellular-localization / topology-prediction / non-CRC / RNA-proxy "
        "observation reached a rung above WEAK",
    )
    density_no_qual_direct = [
        e for e in admissible
        if e.classified.evidence_rung == "DIRECT"
        and not (
            e.observation.is_protein_layer
            and e.observation.assay_method.strip()
            and e.observation.is_malignant_attributed
            and e.observation.is_measurement_qualified
            and e.observation.is_context_qualified
            and e.observation.crc_specific
            and e.observation.surface_context_class in ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL")
        )
    ]
    record(
        "quantitative_density_without_qualified_validation_malignant_attribution_and_a_qualified_context_never_reaches_direct",
        not density_no_qual_direct,
        "a DIRECT rung was assigned without measurement_validation_status == "
        "QUALIFIED + a non-empty assay_method + malignant-cell attribution + a "
        "QUALIFIED CRC / well-matched-model surface context",
    )
    # localization NEVER grants density-question grading authority.
    record(
        "localization_never_grants_density_question_grading_authority",
        not (outcome.has_qualifying_indirect and not outcome.has_qualifying_direct and s != "UNKNOWN"),
        "a localization-only landscape produced a graded Strength above UNKNOWN",
    )

    # --- qualification bases (E11 item 13) --------------------------
    missing_basis = [
        e for e in admissible
        if (
            (e.observation.context_adequacy_status == "QUALIFIED"
             and (not e.observation.context_adequacy_basis.strip()
                  or not e.observation.surface_context_basis.strip()))
            or (e.observation.measurement_validation_status == "QUALIFIED"
                and not e.observation.measurement_validation_basis.strip())
            or (e.observation.surface_localization_status in (
                    "SURFACE_LOCALIZED", "NOT_SURFACE_LOCALIZED", "MIXED_OR_UNRESOLVED")
                and not e.observation.surface_localization_basis.strip())
            or (e.observation.density_plausibility_status in (
                    "PLAUSIBLY_ADEQUATE", "NOT_PLAUSIBLY_ADEQUATE", "MIXED_OR_UNRESOLVED")
                and not e.observation.density_plausibility_basis)
            or (e.observation.surface_antigen_level in (
                    "QUANTITATIVELY_PRESENT", "LOW_BUT_PRESENT",
                    "NEGLIGIBLE_OR_UNDETECTABLE", "MIXED_OR_UNRESOLVED")
                and not e.observation.surface_antigen_level_basis.strip())
        )
    ]
    record(
        "every_qualified_or_asserted_factual_state_carries_an_auditable_basis",
        not missing_basis,
        "a QUALIFIED context adequacy / measurement validation status, or an "
        "asserted surface_localization_status / density_plausibility_status / "
        "surface_antigen_level, is missing its auditable basis",
    )
    # a LOW_BUT_PRESENT observation is never scored CONTRADICTING on the
    # antigen-level fact alone.
    bad_low = [
        e for e in admissible
        if e.observation.surface_antigen_level == "LOW_BUT_PRESENT"
        and e.classified.density_implication == "OPPOSES_DENSITY_PLAUSIBILITY"
        and e.observation.density_plausibility_status != "NOT_PLAUSIBLY_ADEQUATE"
    ]
    record(
        "low_but_present_alone_never_opposes_density_plausibility",
        not bad_low,
        "a LOW_BUT_PRESENT observation was scored OPPOSES_DENSITY_PLAUSIBILITY "
        "without an auditable density_plausibility_status == NOT_PLAUSIBLY_ADEQUATE",
    )

    # --- no early grade (E11 item 16) -----------------------------
    needs_complete_landscape = d in ("POSITIVE", "NEGATIVE", "CONFLICTING") or (
        d == "INCONCLUSIVE" and s == "DIRECT"
    )
    record(
        "graded_direction_requires_a_completed_audited_surface_landscape",
        (not needs_complete_landscape) or completion.landscape_complete,
        "a graded Direction x Strength was proposed before the mandatory "
        "surface-availability landscape was complete and audited",
    )

    # --- Direction x Strength == the frozen item-06 truth table ------
    record(
        "direction_strength_pair_is_a_legal_tgt04_pair",
        (d, s) in LEGAL_DIRECTION_STRENGTH_PAIRS,
        f"Direction x Strength {(d, s)} is not a legal TGT-04 pair "
        "(only POSITIVE/DIRECT, NEGATIVE/DIRECT, CONFLICTING/DIRECT, "
        "INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN)",
    )
    record(
        "proposed_strength_is_direct_iff_a_qualifying_direct_quantitative_observation_exists",
        (s == "DIRECT") == outcome.has_qualifying_direct,
        f"proposed_strength {s} does not match whether a qualifying DIRECT "
        f"quantitative antigen-density observation exists ({outcome.has_qualifying_direct})",
    )
    record(
        "no_indirect_strong_or_weak_proposed_strength",
        s not in ("INDIRECT_STRONG", "WEAK"),
        f"the proposal carries the {s} strength -- TGT-04 never proposes "
        "INDIRECT_STRONG or WEAK",
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
    record("negative_has_contradicting_evidence",
           d != "NEGATIVE" or "CONTRADICTING" in roles,
           "a NEGATIVE proposal has no CONTRADICTING evidence_ref")
    record("conflicting_has_supporting_and_contradicting",
           d != "CONFLICTING" or {"SUPPORTING", "CONTRADICTING"} <= roles,
           "a CONFLICTING proposal is missing a SUPPORTING or CONTRADICTING ref")

    # --- fatal_review boundary (E11 item 08 / 12) --------------
    record(
        "fatal_review_is_at_most_a_potential_pattern",
        fatal_review.status in ("", "POTENTIAL_FATAL_PATTERN"),
        "fatal_review.status asserts more than a machine-detectable potential pattern",
    )
    record(
        "fatal_review_pattern_needs_a_completed_audited_landscape",
        (not fatal_review.required) or completion.landscape_complete,
        "a fatal_review pattern was raised without a completed audited "
        "surface-availability landscape",
    )
    if fatal_review.required:
        route_b = len(set(fatal_review.surface_context_ids)) >= 2
        route_a = bool(fatal_review.reproducibility_basis_refs)
        record(
            "fatal_review_pattern_satisfies_route_a_or_route_b",
            route_a or route_b,
            "a fatal_review pattern was raised without Route A (a reproducibility "
            "basis ref) or Route B (>= 2 independent surface_context_ids)",
        )
        record(
            "fatal_review_contributors_are_all_negligible_or_undetectable",
            set(fatal_review.antigen_level_class) == {"NEGLIGIBLE_OR_UNDETECTABLE"},
            "a fatal_review contributor is not NEGLIGIBLE_OR_UNDETECTABLE",
        )
        # CRC malignant-cell only -- a well-matched CRC model contributor is
        # forbidden (E12-6).
        fatal_ids = set(fatal_review.evidence_ids)
        model_contributor = [
            e for e in emitted
            if e.evidence_id in fatal_ids
            and e.observation.surface_context_class != "CRC_MALIGNANT_CELLS"
        ]
        record(
            "fatal_review_contributors_are_all_crc_malignant_cell_observations",
            not model_contributor,
            "a fatal_review contributor is not on CRC_MALIGNANT_CELLS (a "
            "well-matched CRC model observation is never a fatal contributor)",
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

    # --- output must carry no cross-Gate / Decision conclusion ------
    facts = _scannable_ep_fact_text(emitted)
    scannable = " ".join(
        [outcome.aggregation_rationale.lower(), facts]
        + [u.lower() for u, _ in outcome.critical_unknowns]
    )
    record("no_tgt02_tgt03_or_tgt06_conclusion_in_evidence_or_rationale",
           not any(t in scannable for t in _F_CROSS_GATE),
           "an emitted EvidencePackage or the rationale carries a TGT-02 "
           "baseline-coverage substitution, a TGT-03 persistence conclusion, a "
           "TGT-06 internalization conclusion, or an invented clinically effective "
           "antigen-density range")
    record("no_public_fatal_signal_kill_hold_or_decision_anywhere",
           not any(t in scannable for t in _F_DECISION_SUBSTR)
           and _F_DECISION_WORD_RE.search(scannable) is None,
           "an emitted EvidencePackage or the rationale carries a "
           "PUBLIC_FATAL_SIGNAL_ESTABLISHED / KILL / HOLD / Decision")
    record("no_numeric_or_ranking_score_or_density_threshold",
           _SCORE_RE.search(scannable) is None,
           "a numeric / ranking score or an antigen-density / molecules-per-cell "
           "/ ABC / %-positive / H-score threshold appears in the proposal / evidence")

    return checks, reasons
