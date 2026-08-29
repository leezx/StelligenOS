"""Machine acceptance for a MOD-TGT01 run: E1 item 13 (schema / resolvability /
admissible-class / strength-ceiling / dedup / one-package-per-observation / no
score) plus the E1 item-16 stop-rule prerequisite (the same-target program
inventory AND the disclosed failure-reason sweep must both be complete before
any acceptable proposal -- a positive ceiling never licenses an early stop).
"""

from __future__ import annotations

from .aggregate import AggregationOutcome
from .contracts import EmittedEvidence, SweepCompletionRecord

_RANK = {"DIRECT": 3, "INDIRECT_STRONG": 2, "WEAK": 1, "UNKNOWN": 0}


def evaluate(
    *,
    emitted: list[EmittedEvidence],
    outcome: AggregationOutcome,
    sweep: SweepCompletionRecord,
) -> tuple[list[tuple[str, bool]], list[str]]:
    """Return (ordered checks, failure reasons). ``accepted`` is ``all(ok)``."""

    checks: list[tuple[str, bool]] = []
    reasons: list[str] = []

    def record(name: str, ok: bool, why: str) -> None:
        checks.append((name, ok))
        if not ok:
            reasons.append(why)

    # item 13 -- one package per admissible observation (never program-keyed).
    ep_ids = [e.evidence_id for e in emitted]
    record(
        "one_evidence_package_per_observation",
        len(ep_ids) == len(set(ep_ids)),
        "an observation does not map to exactly one EvidencePackage",
    )

    # item 13 -- every emitted record resolved to a registered primary source
    # (unresolved / mismatched rows were rejected upstream, not emitted).
    record(
        "emitted_records_have_a_resolved_primary_source",
        all(e.classified.record.primary_source_resolved for e in emitted),
        "an emitted record lacks a resolved primary source",
    )

    # item 13 -- every emitted record maps to a frozen admissible class.
    record(
        "only_frozen_admissible_classes_emitted",
        all(e.classified.evidence_class for e in emitted),
        "an emitted record carries no frozen admissible class",
    )

    # item 13 -- proposed strength never exceeds the strongest rung actually met.
    if outcome.proposed_strength == "UNKNOWN":
        strength_ok = not emitted
    else:
        strength_ok = bool(emitted) and _RANK[outcome.proposed_strength] <= max(
            _RANK[e.classified.ladder_rung] for e in emitted
        )
    record(
        "proposed_strength_within_the_strongest_rung_met",
        strength_ok,
        "proposed strength exceeds the strongest Evidence Ladder rung actually met",
    )

    # item 13 -- dedup: one (source_id, claim) per emitted package.
    keys = [
        (e.classified.record.source_id, e.classified.record.claim.strip())
        for e in emitted
    ]
    record(
        "no_duplicate_source_claim_among_emitted",
        len(keys) == len(set(keys)),
        "a duplicate (source_id, claim) reached an emitted package",
    )

    # item 13 -- every evidence_ref points at exactly one emitted package.
    emitted_ids = set(ep_ids)
    ref_ids = [evidence_id for evidence_id, _ in outcome.evidence_refs]
    record(
        "every_evidence_ref_points_at_one_emitted_package",
        all(evidence_id in emitted_ids for evidence_id in ref_ids)
        and len(ref_ids) == len(set(ref_ids)),
        "an evidence_ref is dangling or repeated",
    )

    # item 16 -- the mandatory completion prerequisite, checked even when a
    # DIRECT positive precedent has already been found.
    record(
        "same_target_program_inventory_complete",
        sweep.same_target_program_inventory_complete,
        "the same-target ADC program inventory (active / approved AND "
        "discontinued / failed) is not complete",
    )
    record(
        "disclosed_failure_reason_sweep_complete",
        sweep.failure_reason_sweep_complete,
        "the disclosed failure / discontinuation-reason sweep is not complete",
    )

    return checks, reasons
