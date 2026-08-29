"""Deterministic Direction x Strength aggregation for TGT-05 (E4-3 + E4-4).

Verbatim from the frozen E3 item-06 truth table -- no E4 discretion, no "safety
score":

  any undisputed DIRECT liability                -> POSITIVE / DIRECT
  else any undisputed INDIRECT_STRONG liability  -> POSITIVE / INDIRECT_STRONG
  else only WEAK liability hypotheses            -> INCONCLUSIVE / WEAK
  else                                           -> INCONCLUSIVE / UNKNOWN

Positive precedence (E3 / E4-3): once a DIRECT / INDIRECT_STRONG liability is
established, an uncovered other vital organ does NOT downgrade the direction to
UNKNOWN -- it stays POSITIVE and the coverage gap goes into critical_unknowns.

CONFLICTING (E4-4) is per ``liability_event_id`` only: a disputed liability event
(an admissible source SUPPORTS the target attribution and another admissible
source REFUTES it) that has no independent UNDISPUTED DIRECT / INDIRECT_STRONG
liability alongside it. A refutation never earns a NEGATIVE rung. "ADC-A has
toxicity, ADC-B reports no toxicity" is never a conflict.

Absence of risk evidence NEVER produces NEGATIVE / safe.
"""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import EmittedEvidence, Tgt05SweepCompletionRecord

_RANK = {"DIRECT": 3, "INDIRECT_STRONG": 2, "WEAK": 1}


def _strongest(rungs: list[str]) -> str:
    return max(rungs, key=lambda r: _RANK[r])


@dataclass(frozen=True)
class AggregationOutcome:
    proposed_direction: str
    proposed_strength: str
    evidence_refs: tuple[tuple[str, str], ...]
    aggregation_rationale: str
    critical_unknowns: tuple[tuple[str, str], ...]
    disputed_event_ids: tuple[str, ...]


def _coverage_unknowns(sweep: Tgt05SweepCompletionRecord) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for organ, state in sorted(sweep.vital_organ_protein_coverage.items()):
        if state.coverage_result == "ADMISSIBLE_PROTEIN_DATA_FOUND":
            continue
        if state.exhausted_without_admissible_protein:
            out.append((
                f"{organ}: public protein-atlas search exhausted with no "
                "admissible data; a definitive normal-tissue read needs "
                "non-public data",
                "EXPERIMENT_REQUIRED",
            ))
        else:  # NOT_YET_COMPLETE
            out.append((
                f"{organ}: normal-tissue protein coverage sweep not yet complete",
                "PUBLIC_RESOLVABLE",
            ))
    return out


def aggregate(
    emitted: list[EmittedEvidence],
    sweep: Tgt05SweepCompletionRecord,
) -> AggregationOutcome:
    rung_ev = [e for e in emitted if e.classified.establishes_rung]
    attr_ev = [
        e for e in emitted
        if e.classified.evidence_function == "ATTRIBUTION_ADJUDICATION"
    ]
    cov_ev = [
        e for e in emitted
        if e.classified.evidence_function == "COVERAGE_CONTEXT"
    ]

    # disputes are per liability_event_id: a rung event whose attribution is
    # refuted by an admissible ATTRIBUTION_ADJUDICATION record.
    refuted_events = {
        e.classified.record.liability_event_id
        for e in attr_ev
        if e.classified.attribution_stance == "REFUTES_TARGET_ATTRIBUTION"
    }
    rung_events = {e.classified.record.liability_event_id for e in rung_ev}
    disputed = sorted(refuted_events & rung_events)
    disputed_set = set(disputed)

    undisputed_rungs = [
        e for e in rung_ev
        if e.classified.record.liability_event_id not in disputed_set
    ]
    disputed_rungs = [
        e for e in rung_ev
        if e.classified.record.liability_event_id in disputed_set
    ]

    refs: list[tuple[str, str]] = []
    unknowns: list[tuple[str, str]] = []
    unknowns.extend(_coverage_unknowns(sweep))

    undisputed_rung_values = [e.classified.ladder_rung for e in undisputed_rungs]
    has_direct = "DIRECT" in undisputed_rung_values
    has_indirect = "INDIRECT_STRONG" in undisputed_rung_values
    has_weak_only = (
        bool(undisputed_rung_values)
        and not has_direct
        and not has_indirect
    )

    if has_direct or has_indirect:
        # An independent undisputed liability class exists, so the overall
        # assessment is POSITIVE. EvidenceRole is relative to THIS assessment,
        # not to a local event: a disputed event -- its rung AND its
        # support / refute adjudication -- is CONTEXTUAL here, plus a
        # critical_unknown. Nothing in a POSITIVE assessment is CONTRADICTING.
        direction = "POSITIVE"
        strength = "DIRECT" if has_direct else "INDIRECT_STRONG"
        for e in undisputed_rungs:
            refs.append((e.evidence_id, "SUPPORTING"))
        for e in disputed_rungs:
            refs.append((e.evidence_id, "CONTEXTUAL"))
        for e in attr_ev:
            refs.append((e.evidence_id, "CONTEXTUAL"))
        for e in cov_ev:
            refs.append((e.evidence_id, "CONTEXTUAL"))
        for event_id in disputed:
            unknowns.append((
                f"liability event {event_id}: target attribution disputed by an "
                "admissible primary source; human adjudication required",
                "CURRENTLY_UNRESOLVABLE",
            ))
        rationale = (
            f"{len(undisputed_rungs)} undisputed liability observation(s) "
            f"establish a {strength} normal-tissue on-target liability class. "
            + (
                f"{len(disputed)} liability event(s) have a disputed target "
                "attribution -> critical_unknowns / contextual, not a downgrade. "
                if disputed else ""
            )
            + "Coverage gaps in other vital organs, if any, go to "
            "critical_unknowns; the direction stays POSITIVE."
        )
    elif disputed_rungs:
        # No independent undisputed strong liability. The direction is
        # CONFLICTING, but only refs tied to a DISPUTED event carry
        # SUPPORTING / CONTRADICTING -- an unrelated attribution record, or an
        # undisputed WEAK rung, is CONTEXTUAL (E4-4: CONFLICTING is per
        # liability_event_id and never pollutes another event).
        direction = "CONFLICTING"
        strength = _strongest([e.classified.ladder_rung for e in disputed_rungs])
        for e in disputed_rungs:
            refs.append((e.evidence_id, "SUPPORTING"))
        for e in undisputed_rungs:
            refs.append((e.evidence_id, "CONTEXTUAL"))
        for e in attr_ev:
            if e.classified.record.liability_event_id not in disputed_set:
                refs.append((e.evidence_id, "CONTEXTUAL"))
            elif e.classified.attribution_stance == "REFUTES_TARGET_ATTRIBUTION":
                refs.append((e.evidence_id, "CONTRADICTING"))
            else:
                refs.append((e.evidence_id, "SUPPORTING"))
        for e in cov_ev:
            refs.append((e.evidence_id, "CONTEXTUAL"))
        rationale = (
            f"the only liability observation(s) reaching a {strength} rung have a "
            f"disputed target attribution ({', '.join(disputed)}) and there is no "
            "independent undisputed DIRECT / INDIRECT_STRONG liability. Direction "
            "CONFLICTING at the strongest rung the disputed observation could "
            "reach; a refutation earns no NEGATIVE rung."
        )
    elif has_weak_only:
        direction = "INCONCLUSIVE"
        strength = "WEAK"
        for e in undisputed_rungs:
            refs.append((e.evidence_id, "CONTEXTUAL"))
        for e in cov_ev:
            refs.append((e.evidence_id, "CONTEXTUAL"))
        rationale = (
            "only WEAK RNA-level / rodent-only liability hypotheses were found "
            "(PR D: liability cannot be graded; hypothesis only). Direction "
            "INCONCLUSIVE / WEAK -- not POSITIVE, and never NEGATIVE."
        )
    else:
        direction = "INCONCLUSIVE"
        strength = "UNKNOWN"
        rationale = (
            "no admissible liability evidence was found. Per the frozen TGT-05 "
            "unknown behaviour this is UNKNOWN, never auto-PASS and never "
            "NEGATIVE / safe: a negative atlas proves a tissue was checked, not "
            "that the target is safe. Coverage state and any exhausted searches "
            "are in critical_unknowns."
        )
        # the UNKNOWN state carries no evidence_refs (PR A oneOf)
        refs = []

    return AggregationOutcome(
        proposed_direction=direction,
        proposed_strength=strength,
        evidence_refs=tuple(refs),
        aggregation_rationale=rationale,
        critical_unknowns=tuple(unknowns),
        disputed_event_ids=tuple(disputed),
    )
