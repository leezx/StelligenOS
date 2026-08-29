"""Machine acceptance for a MOD-TGT05 run.

Two layers:

* E1 item-13 hygiene (schema / resolvability / admissible-class /
  strength-ceiling / dedup / one-package-per-observation / evidence_ref
  resolvability / frozen truth-table output / no hard integrity failure); and
* the E4-6 path-based mandatory completion rule -- which sweeps MUST be
  complete before the run may be accepted depends on which path the evidence
  put the run on:

    Path A  fatal_review.required          -> a potential fatal pattern is
                                              already visible; the weaker
                                              atlas / RNA sweeps are NOT a
                                              prerequisite for a provisional
                                              stop, but the same-target ADC
                                              construct inventory + attribution
                                              sweep still must be complete
                                              (they built the pattern).
    Path B  a DIRECT ADC clinical liability -> require the same-target ADC
            exists AND fatal_review not        construct inventory + the ADC
            required                           toxicity attribution sweep.
    Path C  no DIRECT ADC clinical         -> require the full Path C sweep
            liability                          set (non-ADC same-target + NHP +
                                              RNA-supporting + all six
                                              vital-organ protein coverage
                                              searches complete).

A positive ceiling never licenses an early stop; an uncovered vital organ
never becomes "safe" -- it becomes a critical_unknown (handled by aggregate).
"""

from __future__ import annotations

from .aggregate import AggregationOutcome
from .contracts import EmittedEvidence, FatalReviewRecord, Tgt05SweepCompletionRecord

_RANK = {"DIRECT": 3, "INDIRECT_STRONG": 2, "WEAK": 1, "UNKNOWN": 0}

#: The only Direction x Strength pairs the frozen E3 item-06 truth table can
#: yield (plus the E4-4 CONFLICTING row). Anything else means aggregate broke.
_TRUTH_TABLE_OUTPUTS: frozenset[tuple[str, str]] = frozenset(
    {
        ("POSITIVE", "DIRECT"),
        ("POSITIVE", "INDIRECT_STRONG"),
        ("INCONCLUSIVE", "WEAK"),
        ("INCONCLUSIVE", "UNKNOWN"),
        ("CONFLICTING", "DIRECT"),
        ("CONFLICTING", "INDIRECT_STRONG"),
        ("CONFLICTING", "WEAK"),
    }
)


def classify_path(emitted: list[EmittedEvidence], fatal_review: FatalReviewRecord) -> str:
    """Return "A" | "B" | "C" -- the completion path this run is on (E4-6)."""

    if fatal_review.required:
        return "A"
    has_direct_adc_liability = any(
        e.classified.establishes_rung
        and e.classified.ladder_rung == "DIRECT"
        and e.classified.record.observation_kind == "ADC_CLINICAL_TOXICITY"
        for e in emitted
    )
    return "B" if has_direct_adc_liability else "C"


def evaluate(
    *,
    emitted: list[EmittedEvidence],
    outcome: AggregationOutcome,
    sweep: Tgt05SweepCompletionRecord,
    fatal_review: FatalReviewRecord,
    hard_integrity_failures: list[tuple[str, str]],
    path: str,
) -> tuple[list[tuple[str, bool]], list[str]]:
    """Return (ordered checks, failure reasons). ``accepted`` is ``all(ok)``."""

    checks: list[tuple[str, bool]] = []
    reasons: list[str] = []

    def record(name: str, ok: bool, why: str) -> None:
        checks.append((name, ok))
        if not ok:
            reasons.append(why)

    # --- E1 item 13 -----------------------------------------------------------

    # a hard identity / provenance integrity failure rejects the WHOLE run; it
    # is never washed into an accepted UNKNOWN.
    record(
        "no_hard_identity_or_provenance_integrity_failure",
        not hard_integrity_failures,
        "hard identity / provenance integrity failure(s): "
        + "; ".join(f"{pid}: {why}" for pid, why in hard_integrity_failures),
    )

    ep_ids = [e.evidence_id for e in emitted]
    record(
        "one_evidence_package_per_observation",
        len(ep_ids) == len(set(ep_ids)),
        "an observation does not map to exactly one EvidencePackage",
    )
    record(
        "emitted_records_have_a_resolved_primary_source",
        all(e.classified.record.primary_source_resolved for e in emitted),
        "an emitted record lacks a resolved primary source",
    )
    record(
        "only_frozen_admissible_classes_emitted",
        all(e.classified.evidence_class for e in emitted),
        "an emitted record carries no frozen admissible TGT-05 class",
    )

    # proposed strength never exceeds the strongest rung actually met. Coverage
    # and attribution EPs carry no rung -- only LIABILITY_RUNG_EVIDENCE does.
    rung_values = [
        e.classified.ladder_rung for e in emitted if e.classified.establishes_rung
    ]
    if outcome.proposed_strength == "UNKNOWN":
        strength_ok = not rung_values
    else:
        strength_ok = bool(rung_values) and _RANK[outcome.proposed_strength] <= max(
            _RANK[r] for r in rung_values
        )
    record(
        "proposed_strength_within_the_strongest_rung_met",
        strength_ok,
        "proposed strength exceeds the strongest Evidence Ladder rung actually met",
    )

    record(
        "proposed_direction_strength_is_a_frozen_truth_table_output",
        (outcome.proposed_direction, outcome.proposed_strength) in _TRUTH_TABLE_OUTPUTS,
        "the proposed Direction x Strength pair is not a frozen E3 truth-table output",
    )

    # a negative atlas is never a NEGATIVE direction / safety conclusion.
    record(
        "never_proposes_negative_or_safe",
        outcome.proposed_direction != "NEGATIVE",
        "MOD-TGT05 must never propose NEGATIVE / safe on the public path",
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
    ref_ids = [evidence_id for evidence_id, _ in outcome.evidence_refs]
    record(
        "every_evidence_ref_points_at_one_emitted_or_reused_package",
        all(evidence_id in emitted_ids for evidence_id in ref_ids)
        and len(ref_ids) == len(set(ref_ids)),
        "an evidence_ref is dangling or repeated",
    )

    # the machine's fatal output never exceeds a potential pattern.
    record(
        "fatal_review_never_asserts_an_established_fatal_signal",
        fatal_review.status in ("", "POTENTIAL_FATAL_PATTERN"),
        "fatal_review.status asserts more than a machine-detectable potential pattern",
    )

    # --- E4-6 path-based mandatory completion --------------------------------

    record("completion_path_is_resolved", path in ("A", "B", "C"),
           f"completion path {path!r} is not one of A / B / C")

    if path in ("A", "B"):
        record(
            "same_target_adc_construct_inventory_complete",
            sweep.same_target_adc_construct_inventory_complete,
            "the same-target ADC construct inventory sweep is not complete",
        )
        record(
            "adc_toxicity_attribution_sweep_complete",
            sweep.adc_toxicity_attribution_sweep_complete,
            "the ADC toxicity target-attribution sweep is not complete",
        )
    if path == "C":
        record(
            "path_c_full_sweep_set_complete",
            sweep.path_c_sweeps_complete,
            "path C requires the non-ADC same-target, NHP, RNA-supporting and all "
            "six vital-organ protein coverage searches to be complete before a stop",
        )

    # a per-organ coverage_result must be backed by an EvidencePackage a human
    # can click through -- the machine cannot assert ADMISSIBLE_PROTEIN_DATA_FOUND
    # (or its opposite) without a corresponding provenance-bearing observation.
    organs_with_protein_ep = {
        e.classified.record.vital_organ_class
        for e in emitted
        if e.classified.record.observation_kind == "HUMAN_NORMAL_EXPRESSION"
        and e.classified.record.molecular_layer == "PROTEIN"
        and e.classified.record.atlas_validated
        and e.classified.record.finding in ("DETECTED", "NOT_DETECTED")
        and e.classified.record.vital_organ_class
    }
    coverage_backing_ok = True
    coverage_backing_why: list[str] = []
    for organ, state in sorted(sweep.vital_organ_protein_coverage.items()):
        if not state.search_complete:
            continue
        has_ep = organ in organs_with_protein_ep
        if state.coverage_result == "ADMISSIBLE_PROTEIN_DATA_FOUND" and not has_ep:
            coverage_backing_ok = False
            coverage_backing_why.append(
                f"{organ}: ADMISSIBLE_PROTEIN_DATA_FOUND with no admissible "
                "human-protein EvidencePackage to back it"
            )
        if (
            state.coverage_result
            == "PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA"
            and has_ep
        ):
            coverage_backing_ok = False
            coverage_backing_why.append(
                f"{organ}: PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA but "
                "an admissible human-protein EvidencePackage exists for it"
            )
    record(
        "coverage_state_is_backed_by_evidence_packages",
        coverage_backing_ok,
        "; ".join(coverage_backing_why),
    )

    return checks, reasons
