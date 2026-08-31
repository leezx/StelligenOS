"""Deterministic Direction x Strength aggregation for TGT-04 (E11 item 06, E12-4).

TGT-04 is a TWO-TIER evidence architecture (LOCALIZATION: INDIRECT_STRONG
membranous IHC / cell-surface proteomics; DENSITY: DIRECT quantitative
antigen density) with a SINGLE-TIER grading authority. This is NOT the E10-style
"highest qualifying rung == overall Strength" rule -- E12 writes the
TGT04-specific authority DIRECTLY.

Frozen -- E12 has no discretion.

Precedence:
  0. a HARD integrity failure -> no proposal            (module.py, not here)
  1. the mandatory surface-availability landscape is not complete / audited
        -> INCONCLUSIVE / UNKNOWN, zero evidence_refs
  2. the landscape is complete but its audit is invalid / missing
        -> HARD reject                                    (module.py, not here)
  3. the landscape is complete AND audited:
        if NO qualifying DIRECT quantitative antigen-density observation:
            -> INCONCLUSIVE / UNKNOWN, zero evidence_refs
               (100 qualifying INDIRECT_STRONG localization observations and
                0 DIRECT is still INCONCLUSIVE / UNKNOWN -- localization NEVER
                lifts the Gate-level Strength above UNKNOWN)
        else:
            overall Strength = DIRECT
            grade the Direction OVER THE QUALIFYING DIRECT observations only,
            per the frozen density_direction_mapping:
              material SUPPORTS + material OPPOSES, no resolver -> CONFLICTING / DIRECT
                (unless a typed multi-context MIXED_OR_UNRESOLVED characterisation
                 covering all material contexts resolves it -> INCONCLUSIVE / DIRECT)
              else material OPPOSES only                        -> NEGATIVE / DIRECT
              else material SUPPORTS only                       -> POSITIVE / DIRECT
              else (qualifying DIRECT exists, nondirectional)   -> INCONCLUSIVE / DIRECT

Legal pairs (frozen, exactly 5): POSITIVE / DIRECT, NEGATIVE / DIRECT,
CONFLICTING / DIRECT, INCONCLUSIVE / DIRECT, INCONCLUSIVE / UNKNOWN. There is NO
INDIRECT_STRONG proposed Strength and NO INCONCLUSIVE / WEAK. A single
quantitative negligible observation is a DIRECT-class OPPOSES observation, never
a NEGATIVE / DIRECT proposal on its own -- the proposal is an AGGREGATE over the
completed landscape. NEGATIVE weighs the science; it is never a KILL.
"""

from __future__ import annotations

from dataclasses import dataclass

from .completion import SurfaceAvailabilityCompletion
from .contracts import EmittedEvidence


@dataclass(frozen=True)
class AggregationOutcome:
    proposed_direction: str
    proposed_strength: str
    evidence_refs: tuple[tuple[str, str], ...]
    aggregation_rationale: str
    critical_unknowns: tuple[tuple[str, str], ...]
    overall_ceiling: str          # "" | DIRECT
    landscape_complete: bool
    has_qualifying_direct: bool
    has_qualifying_indirect: bool


_EXPERIMENT_UNKNOWN = (
    "a quantitative cell-surface antigen density measurement on CRC malignant cells"
)


def _incomplete_landscape_unknowns(
    completion: SurfaceAvailabilityCompletion,
) -> tuple[tuple[str, str], ...]:
    unknowns: list[tuple[str, str]] = []
    for item in completion.unresolved_items:
        unknowns.append((
            f"unresolved surface-availability search item: {item.description}",
            item.resolution,
        ))
    if not completion.attempted:
        unknowns.append((
            "no target-specific public surface-availability search was attempted",
            "PUBLIC_RESOLVABLE",
        ))
    elif not completion.landscape_complete:
        unknowns.append((
            "the mandatory public surface-availability landscape (quantitative "
            "surface density / validated membranous IHC / cell-surface proteomics "
            "/ subcellular localization) is not complete",
            "PUBLIC_RESOLVABLE",
        ))
    return tuple(unknowns)


def aggregate(
    emitted: list[EmittedEvidence],
    completion: SurfaceAvailabilityCompletion,
) -> AggregationOutcome:
    admissible = [e for e in emitted if e.classified.admissible]
    qualifying_indirect = [e for e in admissible if e.classified.qualifying_for_indirect]
    has_indirect = bool(qualifying_indirect)

    # --- precedence 1: incomplete / unaudited landscape -> UNKNOWN -----------
    if not completion.landscape_complete:
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the mandatory public surface-availability landscape is not "
                "complete and audited. Per the frozen contract a single "
                "quantitative dataset, a single localization dataset or a single "
                "negligible-antigen observation is never a completed answer -- "
                "INCONCLUSIVE / UNKNOWN, and the UNKNOWN carries zero evidence_refs."
            ),
            critical_unknowns=_incomplete_landscape_unknowns(completion),
            overall_ceiling="",
            landscape_complete=False,
            has_qualifying_direct=False,
            has_qualifying_indirect=has_indirect,
        )

    # --- precedence 3: completed audited landscape -------------------------
    qualifying_direct = [e for e in admissible if e.classified.qualifying_for_direct]
    has_direct = bool(qualifying_direct)

    unknowns: list[tuple[str, str]] = [
        (f"unresolved surface-availability search item: {i.description}", i.resolution)
        for i in completion.unresolved_items
    ]
    # EXPERIMENT_REQUIRED only once the enumerated public source space is TRULY
    # exhausted -- i.e. no declared unresolved public item still offers a
    # resolution path (E11 item 15 / E8 / E10 precedence).
    public_space_exhausted = not completion.unresolved_items

    # --- SINGLE-TIER grading authority: no qualifying DIRECT -> UNKNOWN -----
    # A localization-only completed landscape (any number of qualifying
    # INDIRECT_STRONG, zero qualifying DIRECT), and a WEAK-only landscape, are
    # both INCONCLUSIVE / UNKNOWN. Localization NEVER lifts the Strength above
    # UNKNOWN.
    if not has_direct:
        if public_space_exhausted:
            unknowns.append((_EXPERIMENT_UNKNOWN, "EXPERIMENT_REQUIRED"))
        if has_indirect:
            _tail = (
                "surface localization is clearly established (INDIRECT_STRONG "
                "membranous IHC / cell-surface proteomics) but NO qualifying DIRECT "
                "quantitative antigen-density measurement exists. Verbatim from the "
                "frozen contract: 'Only localization or RNA evidence available -> "
                "strength stays UNKNOWN on the density question; it is not upgraded.'"
            )
        else:
            _tail = (
                "the completed public search yielded only WEAK topology / prediction "
                "/ non-CRC / RNA-proxy evidence, which cannot answer the "
                "density-plausibility question."
            )
        _exp_tail = (
            " A new quantitative cell-surface antigen density measurement on CRC "
            "malignant cells is required."
            if public_space_exhausted
            else " The remaining unresolved public evidence path must be resolved "
            "before determining whether a new measurement is required."
        )
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the public surface-availability landscape is complete and audited "
                f"but carries no qualifying DIRECT quantitative antigen-density "
                f"observation. {_tail} INCONCLUSIVE / UNKNOWN with zero "
                f"evidence_refs;{_exp_tail}"
            ),
            critical_unknowns=tuple(unknowns),
            overall_ceiling="",
            landscape_complete=True,
            has_qualifying_direct=False,
            has_qualifying_indirect=has_indirect,
        )

    # --- a qualifying DIRECT quantitative antigen-density observation exists:
    #     overall Strength = DIRECT, grade over the qualifying DIRECT set ONLY.
    overall = "DIRECT"
    supports = [
        e for e in qualifying_direct
        if e.classified.density_implication == "SUPPORTS_DENSITY_PLAUSIBILITY"
    ]
    opposes = [
        e for e in qualifying_direct
        if e.classified.density_implication == "OPPOSES_DENSITY_PLAUSIBILITY"
    ]

    # explicit typed multi-context characterization resolver (E12 tightening 2):
    # a qualifying DIRECT observation with declared_multi_context_analysis and
    # density_plausibility_status == MIXED_OR_UNRESOLVED and an auditable basis
    # whose surface_context_ids cover the relevant contexts is an explicit
    # cross-context characterization -> graded INCONCLUSIVE / DIRECT, not
    # CONFLICTING. NOT_ESTABLISHED is NOT a resolver. Never semantic-parse prose.
    relevant_contexts: set[str] = set()
    for e in supports + opposes:
        relevant_contexts.update(e.observation.surface_context_identities)
    characterization_resolver = next(
        (
            e
            for e in qualifying_direct
            if e.observation.declared_multi_context_analysis
            and e.observation.density_plausibility_status == "MIXED_OR_UNRESOLVED"
            and e.observation.density_plausibility_basis
            and relevant_contexts
            and relevant_contexts <= set(e.observation.surface_context_identities)
        ),
        None,
    )

    has_supports = bool(supports)
    has_opposes = bool(opposes)

    def _refs(direction: str) -> tuple[tuple[str, str], ...]:
        used: set[str] = set()
        out: list[tuple[str, str]] = []
        if direction in ("POSITIVE", "CONFLICTING"):
            for e in supports:
                out.append((e.evidence_id, "SUPPORTING"))
                used.add(e.evidence_id)
        if direction in ("NEGATIVE", "CONFLICTING"):
            for e in opposes:
                out.append((e.evidence_id, "CONTRADICTING"))
                used.add(e.evidence_id)
        for e in admissible:
            if e.evidence_id in used:
                continue
            out.append((e.evidence_id, "CONTEXTUAL"))
        return tuple(out)

    if has_supports and has_opposes and characterization_resolver is not None:
        direction = "INCONCLUSIVE"
        rationale = (
            "the completed audited surface-availability landscape carries qualifying "
            "DIRECT quantitative observations supporting plausibly adequate density "
            "AND qualifying DIRECT quantitative observations opposing it, BUT an "
            "admissible declared multi-context analysis explicitly characterises the "
            "result as context-dependent (density_plausibility_status "
            "MIXED_OR_UNRESOLVED, basis "
            f"{characterization_resolver.observation.density_plausibility_basis}) "
            "across the relevant surface contexts. Per the frozen contract this is a "
            "GRADED INCONCLUSIVE / DIRECT, distinct from INCONCLUSIVE / UNKNOWN, "
            "carrying its CONTEXTUAL evidence_refs."
        )
        refs = _refs("INCONCLUSIVE")
    elif has_supports and has_opposes:
        direction = "CONFLICTING"
        rationale = (
            "the completed audited surface-availability landscape carries qualifying "
            "DIRECT quantitative observations that make genuinely incompatible "
            "density-plausibility claims (qualifying evidence for plausibly adequate "
            "cell-surface antigen density AND qualifying evidence for materially "
            "inadequate / negligible density) and no auditable context-specific "
            "characterisation resolves them. Direction CONFLICTING / DIRECT."
        )
        refs = _refs("CONFLICTING")
    elif has_opposes:
        direction = "NEGATIVE"
        rationale = (
            "the completed audited surface-availability landscape carries only "
            "qualifying opposing DIRECT quantitative observations -- materially "
            "inadequate / negligible cell-surface antigen density on CRC malignant "
            "cells (or a qualified well-matched CRC model). Direction NEGATIVE / "
            "DIRECT. This is a Gate-relative scientific density-plausibility "
            "judgement; a separate machine-local review record is set only when the "
            "frozen reproducibility criteria are met on CRC malignant-cell evidence, "
            "and the Candidate-level consequence is decided downstream, not by this "
            "Module."
        )
        refs = _refs("NEGATIVE")
    elif has_supports:
        direction = "POSITIVE"
        rationale = (
            "the completed audited surface-availability landscape carries only "
            "qualifying supporting DIRECT quantitative observations -- plausibly "
            "adequate cell-surface antigen density on CRC malignant cells (or a "
            "qualified well-matched CRC model). Direction POSITIVE / DIRECT."
        )
        refs = _refs("POSITIVE")
    else:
        direction = "INCONCLUSIVE"
        rationale = (
            "the completed audited surface-availability landscape contains qualifying "
            "DIRECT quantitative antigen-density measurements but their "
            "density_plausibility_status does not resolve adequate-vs-inadequate "
            "(MIXED_OR_UNRESOLVED / NOT_ESTABLISHED). This is a GRADED INCONCLUSIVE "
            "/ DIRECT (distinct from INCONCLUSIVE / UNKNOWN), carrying its CONTEXTUAL "
            "evidence_refs."
        )
        refs = _refs("INCONCLUSIVE")

    return AggregationOutcome(
        proposed_direction=direction,
        proposed_strength=overall,
        evidence_refs=refs,
        aggregation_rationale=rationale,
        critical_unknowns=tuple(unknowns),
        overall_ceiling=overall,
        landscape_complete=True,
        has_qualifying_direct=True,
        has_qualifying_indirect=has_indirect,
    )
