"""Machine acceptance for a MOD-TGT01 run: E1 item 13 (schema / resolvability /
admissible-class / strength-ceiling / dedup / required fields / no score) plus
the E1 item-16 stop-rule prerequisite (the same-target program inventory AND the
disclosed failure-reason sweep must both be complete before any acceptable
proposal -- a positive ceiling never licenses an early stop).
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .aggregate import AggregationOutcome
from .contracts import (
    ClassifiedPrecedent,
    SweepCompletionRecord,
    Tgt01ModuleInput,
)

_RANK = {"DIRECT": 3, "INDIRECT_STRONG": 2, "WEAK": 1, "UNKNOWN": 0}


def evaluate(
    *,
    module_input: Tgt01ModuleInput,
    admissible: list[ClassifiedPrecedent],
    by_program: dict[str, str],
    packages: tuple[EvidencePackage, ...],
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

    emitted = [c for c in admissible if c.record.program_id in by_program]

    # item 13 -- every EvidencePackage is a valid PR A object. Construction in
    # evidence.py raises on any shape violation, so reaching here with a full
    # set means they all validated.
    record(
        "every_evidence_package_validates",
        len(packages) == len(emitted),
        "an EvidencePackage failed PR A validation",
    )

    # item 13 -- every emitted record resolved to a registered primary source
    # (unresolved rows were rejected upstream, not emitted).
    record(
        "emitted_records_have_a_resolved_primary_source",
        all(c.record.primary_source_resolved for c in emitted),
        "an emitted record lacks a resolved primary source",
    )

    # item 13 -- every emitted record maps to a frozen admissible class.
    record(
        "only_frozen_admissible_classes_emitted",
        all(c.evidence_class for c in emitted),
        "an emitted record carries no frozen admissible class",
    )

    # item 13 -- proposed strength never exceeds the strongest rung actually met.
    if outcome.proposed_strength == "UNKNOWN":
        strength_ok = not emitted  # UNKNOWN state only when nothing was emitted
    else:
        strength_ok = bool(emitted) and _RANK[outcome.proposed_strength] <= max(
            _RANK[c.ladder_rung] for c in emitted
        )
    record(
        "proposed_strength_within_the_strongest_rung_met",
        strength_ok,
        "proposed strength exceeds the strongest Evidence Ladder rung actually met",
    )

    # item 13 -- dedup: one (source_id, claim) per emitted package.
    keys = [(c.record.source_id, c.record.claim.strip()) for c in emitted]
    record(
        "no_duplicate_source_claim_among_emitted",
        len(keys) == len(set(keys)),
        "a duplicate (source_id, claim) reached an emitted package",
    )

    # item 13 -- every evidence_ref points at an emitted package.
    emitted_ids = set(by_program.values())
    record(
        "every_evidence_ref_points_at_an_emitted_package",
        all(evidence_id in emitted_ids for evidence_id, _ in outcome.evidence_refs),
        "an evidence_ref does not resolve to an emitted EvidencePackage",
    )

    # item 16 -- the mandatory completion prerequisite. This is checked even
    # when a DIRECT positive precedent has already been found.
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
