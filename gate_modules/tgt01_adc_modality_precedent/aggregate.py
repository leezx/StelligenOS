"""Deterministic Direction x Strength aggregation for TGT-01.

Strictly the E1 semantics (Strength orthogonal to Direction; no numeric score;
no fourth ladder). The frozen item-08 fatal / adverse pattern needs TWO OR MORE
independent same-target programs discontinued for a consistent target-mediated
failure -- a single failed ADC never triggers NEGATIVE / fatal.

  no admissible qualifying evidence          -> INCONCLUSIVE / UNKNOWN (the
                                               frozen UNKNOWN state, no refs)
  supporting precedent only                  -> POSITIVE, strength = strongest
                                               frozen rung actually met
  target-attributable adverse PATTERN only   -> NEGATIVE
  supporting precedent + adverse PATTERN     -> CONFLICTING
  admissible context but neither             -> INCONCLUSIVE with graded strength
"""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import ClassifiedPrecedent

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
    adverse_program_ids: tuple[str, ...]


def aggregate(
    admissible: list[ClassifiedPrecedent],
    by_program: dict[str, str],
) -> AggregationOutcome:
    """``by_program`` maps program_id -> the EvidencePackage id actually emitted
    for it; records with no emitted package (duplicates) are ignored here."""

    emitted = [c for c in admissible if c.record.program_id in by_program]

    supporting = [c for c in emitted if c.direction_role == "SUPPORTING"]
    adverse = [c for c in emitted if c.contributes_adverse_signal]
    contextual = [c for c in emitted if c.direction_role == "CONTEXTUAL"]

    adverse_program_ids = tuple(
        sorted({c.record.program_id for c in adverse})
    )
    adverse_pattern = len(adverse_program_ids) >= 2

    def ref(c: ClassifiedPrecedent, role: str) -> tuple[str, str]:
        return (by_program[c.record.program_id], role)

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
            adverse_program_ids=(),
        )

    refs: list[tuple[str, str]] = []
    unknowns: list[tuple[str, str]] = []

    if supporting and adverse_pattern:
        direction = "CONFLICTING"
        strength = _strongest(
            [c.ladder_rung for c in supporting] + [c.ladder_rung for c in adverse]
        )
        refs += [ref(c, "SUPPORTING") for c in supporting]
        refs += [ref(c, "CONTRADICTING") for c in adverse]
        refs += [ref(c, "CONTEXTUAL") for c in contextual]
        rationale = (
            f"{len(supporting)} admissible supporting ADC-precedent record(s) "
            f"co-present with a target-attributable failure pattern across "
            f"{len(adverse_program_ids)} independent same-target programs "
            f"({', '.join(adverse_program_ids)}), each discontinued for a "
            f"disclosed target-mediated / on-target reason. Direction is "
            f"CONFLICTING; strongest evidence directness is {strength}. The "
            f"fatal-condition adjudication is for the human review surface, not "
            f"this module."
        )
        unknowns.append(
            (
                "Supporting precedent co-present with a same-target "
                "target-mediated failure pattern; the frozen item-08 "
                "fatal-condition call requires human adjudication",
                "CURRENTLY_UNRESOLVABLE",
            )
        )
    elif supporting:
        direction = "POSITIVE"
        strength = _strongest([c.ladder_rung for c in supporting])
        refs += [ref(c, "SUPPORTING") for c in supporting]
        # a single sub-pattern failure and any non-attributed discontinuation
        # are context only.
        refs += [ref(c, "CONTEXTUAL") for c in adverse]
        refs += [ref(c, "CONTEXTUAL") for c in contextual]
        rationale = (
            f"{len(supporting)} admissible supporting ADC-precedent record(s); "
            f"strongest frozen rung actually met is {strength}. "
            + (
                f"{len(adverse_program_ids)} single target-mediated discontinuation(s) "
                "present but below the >= 2 independent-program threshold, so no "
                "adverse pattern (frozen item 08). "
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
        strength = _strongest([c.ladder_rung for c in adverse])
        refs += [ref(c, "CONTRADICTING") for c in adverse]
        refs += [ref(c, "CONTEXTUAL") for c in contextual]
        rationale = (
            f"A target-attributable failure pattern across "
            f"{len(adverse_program_ids)} independent same-target programs "
            f"({', '.join(adverse_program_ids)}), each discontinued for a "
            f"disclosed target-mediated / on-target reason, with no admissible "
            f"supporting precedent. Direction NEGATIVE; strongest evidence "
            f"directness is {strength}. The module reports the pattern; it never "
            f"performs a Candidate-level KILL."
        )
    else:
        # admissible context (a single sub-pattern failure and/or non-attributed
        # discontinuations) but no precedent and no pattern.
        direction = "INCONCLUSIVE"
        strength = _strongest(
            [c.ladder_rung for c in adverse] + [c.ladder_rung for c in contextual]
        )
        refs += [ref(c, "CONTEXTUAL") for c in adverse]
        refs += [ref(c, "CONTEXTUAL") for c in contextual]
        rationale = (
            "No admissible supporting ADC-modality precedent, and the "
            + (
                f"{len(adverse_program_ids)} target-mediated discontinuation(s) "
                "do not reach the >= 2 independent-program pattern (frozen item 08). "
                if adverse
                else "discontinued programs carry no target attribution. "
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
        adverse_program_ids=adverse_program_ids,
    )
