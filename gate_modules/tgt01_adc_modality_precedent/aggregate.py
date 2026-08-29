"""Deterministic Direction x Strength aggregation for TGT-01.

Strictly the E1 semantics (Strength orthogonal to Direction; no numeric score;
no fourth ladder). The frozen item-08 fatal / adverse pattern needs TWO OR MORE
independent same-target programs discontinued for a CONSISTENT frozen adverse
class (target-mediated toxicity OR an intrinsically unachievable therapeutic
window) -- a single failed ADC, and a mix of different adverse classes, never
form a pattern.

  no admissible qualifying evidence          -> INCONCLUSIVE / UNKNOWN (the
                                               frozen UNKNOWN state, no refs)
  supporting precedent only                  -> POSITIVE, strength = strongest
                                               frozen rung actually met
  a consistent adverse PATTERN only          -> NEGATIVE
  supporting precedent + adverse PATTERN     -> CONFLICTING
  admissible context but neither             -> INCONCLUSIVE with graded strength
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .contracts import EmittedEvidence

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
    adverse_pattern: bool
    adverse_pattern_class: str
    adverse_program_ids: tuple[str, ...]


def aggregate(emitted: list[EmittedEvidence]) -> AggregationOutcome:
    """``emitted`` is one entry per admissible observation, each with its own
    EvidencePackage id (no program-keyed collapsing)."""

    supporting = [e for e in emitted if e.classified.direction_role == "SUPPORTING"]
    adverse = [e for e in emitted if e.classified.contributes_adverse_signal]
    contextual = [e for e in emitted if e.classified.direction_role == "CONTEXTUAL"]

    # a pattern needs >= 2 independent same-target programs failing for the SAME
    # frozen adverse class.
    programs_by_class: dict[str, set[str]] = defaultdict(set)
    for e in adverse:
        programs_by_class[e.classified.adverse_class].add(e.classified.record.program_id)
    pattern_classes = sorted(
        cls for cls, pids in programs_by_class.items() if len(pids) >= 2
    )
    adverse_pattern = bool(pattern_classes)
    adverse_pattern_class = pattern_classes[0] if len(pattern_classes) == 1 else (
        "MULTIPLE" if pattern_classes else ""
    )
    pattern_program_ids = tuple(
        sorted(
            {
                pid
                for cls in pattern_classes
                for pid in programs_by_class[cls]
            }
        )
    )
    # adverse observations whose class reached the pattern -> CONTRADICTING;
    # the rest (single-program / sub-threshold) -> CONTEXTUAL.
    pattern_adverse = [
        e for e in adverse if e.classified.adverse_class in pattern_classes
    ]
    subthreshold_adverse = [
        e for e in adverse if e.classified.adverse_class not in pattern_classes
    ]

    # --- the frozen UNKNOWN state ------------------------------------------
    if not supporting and not adverse_pattern and not adverse and not contextual:
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "No admissible ADC-modality precedent identified against the "
                "target or a biologically adjacent target in the enumerated "
                "public sources. Per the frozen TGT-01 unknown behaviour this is "
                "UNKNOWN, not KILL: a novel target is not disqualified by the "
                "absence of precedent."
            ),
            critical_unknowns=(
                (
                    "No same-target or adjacent-target ADC precedent found; a "
                    "later public disclosure could establish one",
                    "PUBLIC_RESOLVABLE",
                ),
            ),
            adverse_pattern=False,
            adverse_pattern_class="",
            adverse_program_ids=(),
        )

    refs: list[tuple[str, str]] = []
    unknowns: list[tuple[str, str]] = []
    consistent = (
        adverse_pattern_class.lower().replace("_", " ")
        if adverse_pattern_class not in ("", "MULTIPLE")
        else "a consistent target-attributable"
    )

    if supporting and adverse_pattern:
        direction = "CONFLICTING"
        strength = _strongest(
            [e.classified.ladder_rung for e in supporting]
            + [e.classified.ladder_rung for e in pattern_adverse]
        )
        refs += [(e.evidence_id, "SUPPORTING") for e in supporting]
        refs += [(e.evidence_id, "CONTRADICTING") for e in pattern_adverse]
        refs += [(e.evidence_id, "CONTEXTUAL") for e in subthreshold_adverse]
        refs += [(e.evidence_id, "CONTEXTUAL") for e in contextual]
        rationale = (
            f"{len(supporting)} admissible supporting ADC-precedent record(s) "
            f"co-present with a target-attributable failure pattern -- "
            f"{len(pattern_program_ids)} independent same-target programs "
            f"({', '.join(pattern_program_ids)}) discontinued for {consistent} "
            f"failure. Direction CONFLICTING; strongest evidence directness is "
            f"{strength}. The item-08 fatal-condition adjudication is for the "
            f"human review surface, not this module."
        )
        unknowns.append(
            (
                "Supporting precedent co-present with a same-target "
                f"{consistent} failure pattern; the frozen item-08 "
                "fatal-condition call requires human adjudication",
                "CURRENTLY_UNRESOLVABLE",
            )
        )
    elif supporting:
        direction = "POSITIVE"
        strength = _strongest([e.classified.ladder_rung for e in supporting])
        refs += [(e.evidence_id, "SUPPORTING") for e in supporting]
        refs += [(e.evidence_id, "CONTEXTUAL") for e in adverse]
        refs += [(e.evidence_id, "CONTEXTUAL") for e in contextual]
        n_adv_programs = len({e.classified.record.program_id for e in adverse})
        rationale = (
            f"{len(supporting)} admissible supporting ADC-precedent record(s); "
            f"strongest frozen rung actually met is {strength}. "
            + (
                f"{n_adv_programs} target-attributable discontinuation(s) present "
                "but no single frozen adverse class reaches >= 2 independent "
                "programs, so no consistent pattern (frozen item 08). "
                if adverse
                else ""
            )
            + "Direction POSITIVE."
        )
        if strength == "WEAK":
            unknowns.append(
                (
                    "Only class-level / hypothesis-generating precedent found; a "
                    "same-target clinical ADC precedent would raise the strength",
                    "PUBLIC_RESOLVABLE",
                )
            )
    elif adverse_pattern:
        direction = "NEGATIVE"
        strength = _strongest([e.classified.ladder_rung for e in pattern_adverse])
        refs += [(e.evidence_id, "CONTRADICTING") for e in pattern_adverse]
        refs += [(e.evidence_id, "CONTEXTUAL") for e in subthreshold_adverse]
        refs += [(e.evidence_id, "CONTEXTUAL") for e in contextual]
        rationale = (
            f"A target-attributable failure pattern -- {len(pattern_program_ids)} "
            f"independent same-target programs ({', '.join(pattern_program_ids)}) "
            f"discontinued for {consistent} failure -- with no admissible "
            f"supporting precedent. Direction NEGATIVE; strongest evidence "
            f"directness is {strength}. The module reports the pattern; it never "
            f"performs a Candidate-level KILL."
        )
    else:
        direction = "INCONCLUSIVE"
        strength = _strongest(
            [e.classified.ladder_rung for e in adverse]
            + [e.classified.ladder_rung for e in contextual]
        )
        refs += [(e.evidence_id, "CONTEXTUAL") for e in adverse]
        refs += [(e.evidence_id, "CONTEXTUAL") for e in contextual]
        n_adv_programs = len({e.classified.record.program_id for e in adverse})
        rationale = (
            "No admissible supporting ADC-modality precedent, and "
            + (
                f"the {n_adv_programs} target-attributable discontinuation(s) do "
                "not reach a consistent >= 2 independent-program pattern (frozen "
                "item 08). "
                if adverse
                else "the discontinued programs carry no target attribution. "
            )
            + "Direction INCONCLUSIVE with graded context; not UNKNOWN because "
            "qualified records were found."
        )

    return AggregationOutcome(
        proposed_direction=direction,
        proposed_strength=strength,
        evidence_refs=tuple(refs),
        aggregation_rationale=rationale,
        critical_unknowns=tuple(unknowns),
        adverse_pattern=adverse_pattern,
        adverse_pattern_class=adverse_pattern_class,
        adverse_program_ids=pattern_program_ids,
    )
