"""Deterministic Direction x Strength aggregation for TGT-07 (E15 item 06; E16
tightening 3).

TGT-07 uses a HIGHEST-QUALIFYING-RUNG grading authority (Option A -- a qualifying
INDIRECT_STRONG soluble-antigen landscape with no DIRECT sink-exposure context
propagates to POSITIVE / INDIRECT_STRONG). E16 writes the frozen
``tgt07_specific_aggregation_truth_table.frozen_evaluation_order`` DIRECTLY --
there is no generic ``highest_rung`` aggregator.

``aggregate`` CONSUMES the already-classified result (E16 tightening 3). It never
re-checks same_target_therapeutic_match_status / soluble_antigen_attribution_status
/ tmdd_input_adequacy_status / analysis_validation_status -- those are classifier
authority. Every context test is over the single-string ``sink_exposure_context_id``
(there is NO IDENTIFIED_MULTI / third-state / projection helper).

frozen_evaluation_order -- applied in this exact order, STOP at the first match:

  0. not completed / audit-invalid -> handled by the item-16 stop rule (module.py)
  1. group qualifying DIRECT observations by sink_exposure_context_id
  2. >= 1 CLEAN / uncontested material-sink DIRECT sink-exposure context
     (a context id carrying >= 1 material-sink DIRECT AND NO no-material-sink
     DIRECT)                                                 -> POSITIVE / DIRECT
       (existence-proof dominance -- a no-material-sink DIRECT in a DIFFERENT
        context is retained as CONTEXTUAL and never reverses the conclusion)
  3. else a sink_exposure_context_id carries BOTH a qualifying material-sink DIRECT
     AND a qualifying no-material-sink DIRECT                 -> CONFLICTING / DIRECT
       (v1 has NO machine conflict resolver -- the Module never reconciles it)
  4. else >= 1 qualifying no-material-sink DIRECT (intended-ADC TMDD) and no
     material-sink DIRECT                                     -> NEGATIVE / DIRECT
  5. else >= 1 DIRECT-quality MIXED_OR_UNRESOLVED analysis and no material-sink
     DIRECT and no canonical no-material-sink DIRECT          -> INCONCLUSIVE / DIRECT
       (that DIRECT EP is CONTEXTUAL)
  6. else no DIRECT-rung observation but >= 1 qualifying positive INDIRECT_STRONG
                                                              -> POSITIVE / INDIRECT_STRONG
  7. else WEAK-only / below-assay-limit-only / no qualifying evidence
                                              -> INCONCLUSIVE / UNKNOWN, zero refs

Legal pairs (frozen, exactly 6): POSITIVE / DIRECT, POSITIVE / INDIRECT_STRONG,
NEGATIVE / DIRECT, CONFLICTING / DIRECT, INCONCLUSIVE / DIRECT,
INCONCLUSIVE / UNKNOWN.

Frozen proposal-relative EvidenceRole mapping (E15 item 12):

  POSITIVE / DIRECT           CLEAN material-sink DIRECT -> SUPPORTING;
                              other-context no-material-sink DIRECT -> CONTEXTUAL;
                              conflicted-context evidence -> CONTEXTUAL
  POSITIVE / INDIRECT_STRONG  qualifying quantitation / sheddase / isoform -> SUPPORTING
  NEGATIVE / DIRECT           intended-ADC no-material-sink TMDD -> SUPPORTING
  CONFLICTING / DIRECT        same-context material-sink -> SUPPORTING;
                              same-context no-material-sink -> CONTRADICTING
  INCONCLUSIVE / DIRECT       DIRECT-quality MIXED_OR_UNRESOLVED analysis -> CONTEXTUAL
  INCONCLUSIVE / UNKNOWN      zero evidence_refs
"""

from __future__ import annotations

from dataclasses import dataclass

from .completion import SolubleAntigenEvidenceCompletion
from .contracts import EmittedEvidence


@dataclass(frozen=True)
class AggregationOutcome:
    proposed_direction: str
    proposed_strength: str
    evidence_refs: tuple[tuple[str, str], ...]
    aggregation_rationale: str
    critical_unknowns: tuple[tuple[str, str], ...]
    overall_ceiling: str          # "" | INDIRECT_STRONG | DIRECT
    landscape_complete: bool
    has_direct_rung: bool
    has_qualifying_indirect: bool


_EXPERIMENT_UNKNOWN = (
    "quantify the soluble-antigen sink materiality with a qualified "
    "target-mediated-disposition analysis at the intended ADC exposure, or obtain "
    "documented same-target PK / PD antigen-sink evidence"
)


def _incomplete_landscape_unknowns(
    completion: SolubleAntigenEvidenceCompletion,
) -> tuple[tuple[str, str], ...]:
    unknowns: list[tuple[str, str]] = []
    for item in completion.unresolved_items:
        unknowns.append(
            (
                f"unresolved soluble-antigen-evidence search item: {item.description}",
                item.resolution,
            )
        )
    if not completion.attempted:
        unknowns.append(
            (
                "no target-specific public soluble-antigen-evidence search was attempted",
                "PUBLIC_RESOLVABLE",
            )
        )
    elif not completion.landscape_complete:
        unknowns.append(
            (
                "the mandatory public soluble-antigen-evidence landscape "
                "(soluble-antigen quantitation in CRC patients AND healthy donors / "
                "sheddase processing / secreted isoform / same-target PK / PD or "
                "target-mediated-disposition analysis) is not complete",
                "PUBLIC_RESOLVABLE",
            )
        )
    return tuple(unknowns)


def aggregate(
    emitted: list[EmittedEvidence],
    completion: SolubleAntigenEvidenceCompletion,
) -> AggregationOutcome:
    admissible = [e for e in emitted if e.classified.admissible]
    material = [e for e in admissible if e.classified.qualifying_direct_material_sink]
    no_material = [
        e for e in admissible if e.classified.qualifying_direct_no_material_sink
    ]
    mixed = [e for e in admissible if e.classified.qualifying_direct_mixed]
    indirect = [e for e in admissible if e.classified.qualifying_indirect]
    has_direct_rung = bool(material or no_material or mixed)
    has_indirect = bool(indirect)

    # --- step 0 / incomplete landscape -> UNKNOWN --------------------------
    if not completion.landscape_complete:
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the mandatory public soluble-antigen-evidence landscape is not "
                "complete and audited. Per the frozen contract a single quantitation "
                "record, a single sheddase annotation or a single analysis is never a "
                "completed answer -- INCONCLUSIVE / UNKNOWN, and the UNKNOWN carries "
                "zero evidence_refs."
            ),
            critical_unknowns=_incomplete_landscape_unknowns(completion),
            overall_ceiling="",
            landscape_complete=False,
            has_direct_rung=has_direct_rung,
            has_qualifying_indirect=has_indirect,
        )

    unknowns: list[tuple[str, str]] = [
        (
            f"unresolved soluble-antigen-evidence search item: {i.description}",
            i.resolution,
        )
        for i in completion.unresolved_items
    ]
    public_space_exhausted = not completion.unresolved_items

    def _refs(
        supporting: list[EmittedEvidence],
        contradicting: list[EmittedEvidence],
    ) -> tuple[tuple[str, str], ...]:
        used: set[str] = set()
        out: list[tuple[str, str]] = []
        for e in supporting:
            out.append((e.evidence_id, "SUPPORTING"))
            used.add(e.evidence_id)
        for e in contradicting:
            if e.evidence_id in used:
                continue
            out.append((e.evidence_id, "CONTRADICTING"))
            used.add(e.evidence_id)
        for e in admissible:
            if e.evidence_id in used:
                continue
            out.append((e.evidence_id, "CONTEXTUAL"))
        return tuple(out)

    # --- step 1: group qualifying DIRECT observations by sink_exposure_context_id
    material_ctx: set[str] = {e.sink_exposure_context_id for e in material}
    no_material_ctx: set[str] = {e.sink_exposure_context_id for e in no_material}
    clean_material_ctx = material_ctx - no_material_ctx
    conflicted_ctx = material_ctx & no_material_ctx

    # --- step 2: a CLEAN / uncontested material-sink DIRECT context -------
    if clean_material_ctx:
        clean_material = [
            e for e in material if e.sink_exposure_context_id in clean_material_ctx
        ]
        rationale = (
            "the completed audited soluble-antigen-evidence landscape carries at "
            "least one CLEAN / uncontested qualifying material-sink DIRECT "
            "sink-exposure context (a documented same-target PK / PD antigen-sink "
            "effect or a qualified quantitative TMDD analysis demonstrating a "
            "material soluble sink, with no same-context no-material-sink DIRECT "
            "result). Soluble-antigen materiality is exposure-context dependent: one "
            "clean material-sink context is a sufficient existence proof. Direction "
            "POSITIVE / DIRECT (existence-proof dominance -- a no-material-sink DIRECT "
            "result in a DIFFERENT sink-exposure context is retained as CONTEXTUAL "
            "and never reverses the target-level conclusion)."
        )
        return AggregationOutcome(
            proposed_direction="POSITIVE",
            proposed_strength="DIRECT",
            evidence_refs=_refs(clean_material, []),
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="DIRECT",
            landscape_complete=True,
            has_direct_rung=True,
            has_qualifying_indirect=has_indirect,
        )

    # --- step 3: a sink-exposure context carries BOTH -> CONFLICTING / DIRECT
    if conflicted_ctx:
        same_ctx_material = [
            e for e in material if e.sink_exposure_context_id in conflicted_ctx
        ]
        same_ctx_no_material = [
            e for e in no_material if e.sink_exposure_context_id in conflicted_ctx
        ]
        rationale = (
            "the completed audited soluble-antigen-evidence landscape carries, for "
            "the SAME sink-exposure context, BOTH a qualifying material-sink DIRECT "
            "observation AND a qualifying no-material-sink DIRECT observation, both "
            "admissible. Per the frozen contract there is NO machine conflict "
            "resolver in v1 -- reconciling opposite DIRECT conclusions in one "
            "sink-exposure context is a human-review question. Direction "
            "CONFLICTING / DIRECT."
        )
        return AggregationOutcome(
            proposed_direction="CONFLICTING",
            proposed_strength="DIRECT",
            evidence_refs=_refs(same_ctx_material, same_ctx_no_material),
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="DIRECT",
            landscape_complete=True,
            has_direct_rung=True,
            has_qualifying_indirect=has_indirect,
        )

    # --- step 4: a qualifying intended-ADC no-material-sink TMDD, no material-sink
    if no_material:
        rationale = (
            "the completed audited soluble-antigen-evidence landscape carries at "
            "least one qualifying no-material-sink DIRECT observation -- a "
            "SOLUBLE_ANTIGEN_TMDD_ANALYSIS at the intended ADC exposure, with TMDD "
            "input adequacy and analysis validation QUALIFIED, concluding "
            "NO_MATERIAL_SOLUBLE_SINK -- and NO qualifying material-sink DIRECT "
            "observation. Direction NEGATIVE / DIRECT. This is a Gate-relative "
            "scientific judgement; the Candidate-level consequence is determined "
            "downstream, not by this Module."
        )
        return AggregationOutcome(
            proposed_direction="NEGATIVE",
            proposed_strength="DIRECT",
            evidence_refs=_refs(no_material, []),
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="DIRECT",
            landscape_complete=True,
            has_direct_rung=True,
            has_qualifying_indirect=has_indirect,
        )

    # --- step 5: a DIRECT-quality MIXED_OR_UNRESOLVED analysis only --------
    if mixed:
        if public_space_exhausted:
            unknowns.append((_EXPERIMENT_UNKNOWN, "EXPERIMENT_REQUIRED"))
        rationale = (
            "the completed audited soluble-antigen-evidence landscape carries a "
            "DIRECT-quality analysis whose sink_materiality_outcome is "
            "MIXED_OR_UNRESOLVED, and no qualifying material-sink DIRECT and no "
            "canonical intended-ADC no-material-sink DIRECT observation. Direction "
            "INCONCLUSIVE / DIRECT, carrying that DIRECT-quality analysis EP as "
            "CONTEXTUAL."
        )
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="DIRECT",
            evidence_refs=_refs([], []),  # mixed EPs fall through to CONTEXTUAL
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="DIRECT",
            landscape_complete=True,
            has_direct_rung=True,
            has_qualifying_indirect=has_indirect,
        )

    # --- step 6: no DIRECT-rung observation, >= 1 positive INDIRECT_STRONG -
    if has_indirect:
        if public_space_exhausted:
            unknowns.append((_EXPERIMENT_UNKNOWN, "EXPERIMENT_REQUIRED"))
        rationale = (
            "the completed audited soluble-antigen-evidence landscape carries no "
            "DIRECT-rung sink-exposure-context observation but at least one "
            "qualifying positive INDIRECT_STRONG observation (a quantified "
            "CRC-patient circulating soluble target, a documented sheddase-substrate "
            "status, or a validated secreted isoform). Per the highest-qualifying-rung "
            "authority these support the presence of a soluble-antigen sink-liability "
            "class. Direction POSITIVE / INDIRECT_STRONG; materiality still requires "
            "DIRECT evidence."
        )
        return AggregationOutcome(
            proposed_direction="POSITIVE",
            proposed_strength="INDIRECT_STRONG",
            evidence_refs=_refs(indirect, []),
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="INDIRECT_STRONG",
            landscape_complete=True,
            has_direct_rung=False,
            has_qualifying_indirect=True,
        )

    # --- step 7: WEAK-only / below-assay-limit-only / no qualifying evidence
    if public_space_exhausted:
        unknowns.append((_EXPERIMENT_UNKNOWN, "EXPERIMENT_REQUIRED"))
    rationale = (
        "the completed audited public soluble-antigen-evidence landscape yielded "
        "only WEAK predicted-cleavage-site / family-analogy inference, a "
        "below-detection / below-quantitation-limit measurement, healthy-donor-only "
        "quantitation, or no qualifying evidence at all -- none of which answers the "
        "soluble-antigen sink-liability question. Verbatim from the frozen contract: "
        "'No soluble-antigen data -> UNKNOWN.' INCONCLUSIVE / UNKNOWN with zero "
        "evidence_refs."
    )
    return AggregationOutcome(
        proposed_direction="INCONCLUSIVE",
        proposed_strength="UNKNOWN",
        evidence_refs=(),
        aggregation_rationale=rationale,
        critical_unknowns=tuple(unknowns),
        overall_ceiling="",
        landscape_complete=True,
        has_direct_rung=False,
        has_qualifying_indirect=False,
    )
