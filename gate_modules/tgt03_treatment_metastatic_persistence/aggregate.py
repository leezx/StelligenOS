"""Deterministic Direction x Strength aggregation for TGT-03 (E9 item 06, E10-4).

Frozen -- E10 has no discretion.

Precedence:
  0. a HARD integrity failure -> no proposal            (module.py, not here)
  1. the mandatory clinical-persistence landscape is not complete / audited
        -> INCONCLUSIVE / UNKNOWN, zero evidence_refs
  2. the landscape is complete but its audit is invalid / missing
        -> HARD reject                                    (module.py, not here)
  3. the landscape is complete AND audited -> evaluate the qualifying evidence:

     overall Strength = the HIGHEST qualifying frozen evidence class
       any qualifying DIRECT clinical-context protein  -> DIRECT
       else any qualifying INDIRECT_STRONG             -> INDIRECT_STRONG
       else (only WEAK / contextual)                   -> INCONCLUSIVE / UNKNOWN

     Direction over the qualifying directional evidence:
       material SUPPORTS + material OPPOSES, no resolver -> CONFLICTING
         (unless an explicit typed multi-context MIXED characterization resolves
          it -> graded INCONCLUSIVE)
       else material OPPOSES only                        -> NEGATIVE
       else material SUPPORTS only                       -> POSITIVE
       else (qualifying evidence exists, nondirectional) -> graded INCONCLUSIVE

There is NO E6-style two-axis weaker-ceiling rule. The four mandatory search
components are search-space COMPLETENESS, not a four-axis score. A single
clinical-context protein loss is a DIRECT-class OPPOSES observation, never a
NEGATIVE / DIRECT proposal on its own -- the proposal is an AGGREGATE over the
completed landscape. NEGATIVE weighs the science against retained persistence; it
is never a KILL.
"""

from __future__ import annotations

from dataclasses import dataclass

from .completion import ClinicalPersistenceCompletion
from .contracts import EmittedEvidence, overall_strength


@dataclass(frozen=True)
class AggregationOutcome:
    proposed_direction: str
    proposed_strength: str
    evidence_refs: tuple[tuple[str, str], ...]
    aggregation_rationale: str
    critical_unknowns: tuple[tuple[str, str], ...]
    overall_ceiling: str          # "" | DIRECT | INDIRECT_STRONG
    landscape_complete: bool
    has_qualifying_direct: bool
    has_qualifying_indirect: bool


_UNKNOWN_CEILING = ""


def _incomplete_landscape_unknowns(
    completion: ClinicalPersistenceCompletion,
) -> tuple[tuple[str, str], ...]:
    unknowns: list[tuple[str, str]] = []
    for item in completion.unresolved_items:
        unknowns.append((
            f"unresolved clinical-persistence search item: {item.description}",
            item.resolution,
        ))
    if not completion.attempted:
        unknowns.append((
            "no target-specific public clinical-persistence search was attempted",
            "PUBLIC_RESOLVABLE",
        ))
    elif not completion.landscape_complete:
        unknowns.append((
            "the mandatory public clinical-persistence landscape (refractory / "
            "prior-treated / metastatic lesion / paired pre-post / resistance "
            "model) is not complete",
            "PUBLIC_RESOLVABLE",
        ))
    return tuple(unknowns)


def aggregate(
    emitted: list[EmittedEvidence],
    completion: ClinicalPersistenceCompletion,
) -> AggregationOutcome:
    admissible = [e for e in emitted if e.classified.admissible]

    # --- precedence 1: incomplete / unaudited landscape -> UNKNOWN -----------
    if not completion.landscape_complete:
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the mandatory public clinical-persistence landscape is not "
                "complete and audited. Per the frozen contract a single paired "
                "biopsy series, a single metastatic cohort or a single loss "
                "observation is never a completed population-level answer -- "
                "INCONCLUSIVE / UNKNOWN, and the UNKNOWN carries zero evidence_refs."
            ),
            critical_unknowns=_incomplete_landscape_unknowns(completion),
            overall_ceiling=_UNKNOWN_CEILING,
            landscape_complete=False,
            has_qualifying_direct=False,
            has_qualifying_indirect=False,
        )

    # --- precedence 3: completed audited landscape -------------------------
    qualifying_direct = [e for e in admissible if e.classified.qualifying_for_direct]
    qualifying_indirect = [e for e in admissible if e.classified.qualifying_for_indirect]
    has_direct = bool(qualifying_direct)
    has_indirect = bool(qualifying_indirect)
    overall = overall_strength(has_direct, has_indirect)

    unknowns: list[tuple[str, str]] = [
        (f"unresolved clinical-persistence search item: {i.description}", i.resolution)
        for i in completion.unresolved_items
    ]
    # EXPERIMENT_REQUIRED only once the enumerated public source space is TRULY
    # exhausted -- i.e. no declared unresolved public item still offers a
    # resolution path (E9 item 15 / E8 / E10-7 precedence).
    public_space_exhausted = not completion.unresolved_items

    # --- WEAK-only completed landscape -> INCONCLUSIVE / UNKNOWN -----------
    if not overall:
        if public_space_exhausted:
            unknowns.append((
                "a new treated / refractory / metastatic CRC clinical-context "
                "malignant-cell-resolved persistence measurement -- the completed "
                "public search yielded only treatment-naive primary CRC / "
                "different-tumor evidence, which cannot answer the persistence question",
                "EXPERIMENT_REQUIRED",
            ))
        _weak_tail = (
            "a new treated / refractory / metastatic CRC persistence measurement "
            "is required."
            if public_space_exhausted
            else "the remaining unresolved public evidence path must be resolved "
            "before determining whether a new measurement is required."
        )
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the public clinical-persistence landscape is complete and audited "
                "but carries only WEAK treatment-naive primary CRC / different-tumor "
                "evidence. Verbatim from the frozen contract: 'Only treatment-naive "
                "primary CRC data -> UNKNOWN.' INCONCLUSIVE / UNKNOWN with zero "
                f"evidence_refs; {_weak_tail}"
            ),
            critical_unknowns=tuple(unknowns),
            overall_ceiling=_UNKNOWN_CEILING,
            landscape_complete=True,
            has_qualifying_direct=False,
            has_qualifying_indirect=False,
        )

    qualifying = qualifying_direct + qualifying_indirect
    supports = [
        e for e in qualifying if e.classified.persistence_implication == "SUPPORTS_PERSISTENCE"
    ]
    opposes = [
        e for e in qualifying if e.classified.persistence_implication == "OPPOSES_PERSISTENCE"
    ]

    # explicit typed multi-context characterization resolver (E10-4): an
    # admissible declared multi-context observation whose persistence_context_ids
    # cover the relevant contexts and whose persistence_pattern is
    # MIXED_OR_UNRESOLVED is an explicit cross-context characterization ->
    # graded INCONCLUSIVE, not CONFLICTING. Never semantic-parse source prose.
    relevant_contexts: set[str] = set()
    for e in supports + opposes:
        relevant_contexts.update(e.observation.persistence_context_identities)
    characterization_resolver = next(
        (
            e
            for e in qualifying
            if e.observation.declared_multi_context_analysis
            and e.observation.persistence_pattern == "MIXED_OR_UNRESOLVED"
            and relevant_contexts
            and relevant_contexts <= set(e.observation.persistence_context_identities)
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
            "the completed audited clinical-persistence landscape carries qualifying "
            "observations supporting retention AND qualifying observations "
            "supporting near / marked loss, BUT an admissible declared multi-context "
            "analysis explicitly characterises the result as context-dependent "
            f"(persistence_pattern MIXED_OR_UNRESOLVED, basis "
            f"{characterization_resolver.observation.persistence_pattern_basis}) "
            "across the relevant persistence contexts. Per the frozen contract this "
            f"is a GRADED INCONCLUSIVE at the overall rung {overall}, distinct from "
            "INCONCLUSIVE / UNKNOWN, carrying its CONTEXTUAL evidence_refs."
        )
        refs = _refs("INCONCLUSIVE")
    elif has_supports and has_opposes:
        direction = "CONFLICTING"
        rationale = (
            "the completed audited clinical-persistence landscape carries qualifying "
            "observations that make genuinely incompatible OVERALL persistence claims "
            "(qualifying evidence for retained persistence AND qualifying evidence "
            "for materially impaired persistence) and no auditable context-specific "
            f"characterisation resolves them. Direction CONFLICTING at the overall "
            f"rung {overall}."
        )
        refs = _refs("CONFLICTING")
    elif has_opposes:
        direction = "NEGATIVE"
        rationale = (
            "the completed audited clinical-persistence landscape carries only "
            "qualifying opposing evidence -- clinical-context protein and / or "
            "treated / metastatic transcript / resistance-model observations "
            "supporting near / marked loss of target expression in the actual "
            f"refractory / metastatic setting. Direction NEGATIVE at the overall "
            f"rung {overall}. This is a Gate-relative scientific persistence "
            "judgement; a separate machine-local review record is set only when the "
            "frozen reproducibility criteria are met, and the Candidate-level "
            "consequence is decided downstream, not by this Module."
        )
        refs = _refs("NEGATIVE")
    elif has_supports:
        direction = "POSITIVE"
        rationale = (
            "the completed audited clinical-persistence landscape carries only "
            "qualifying supporting evidence -- clinical-context protein and / or "
            "treated / metastatic transcript / resistance-model observations "
            "supporting retained target expression in the actual refractory / "
            f"metastatic setting. Direction POSITIVE at the overall rung {overall}."
        )
        refs = _refs("POSITIVE")
    else:
        direction = "INCONCLUSIVE"
        rationale = (
            "the completed audited clinical-persistence landscape contains qualifying "
            "DIRECT / INDIRECT_STRONG-quality evidence but the persistence direction "
            "is MIXED and does not resolve retention vs materially impaired "
            f"persistence. This is a GRADED INCONCLUSIVE at the overall rung "
            f"{overall} (distinct from INCONCLUSIVE / UNKNOWN), carrying its "
            "CONTEXTUAL evidence_refs."
        )
        refs = _refs("INCONCLUSIVE")

    # EXPERIMENT_REQUIRED -- the one E9-explicit graded mapping: a directional
    # INDIRECT_STRONG assessment with no qualifying DIRECT clinical-context
    # protein needs a protein-level confirmation. Only once the public source
    # space is truly exhausted.
    if (
        public_space_exhausted
        and direction in ("POSITIVE", "NEGATIVE")
        and overall == "INDIRECT_STRONG"
        and not has_direct
    ):
        unknowns.append((
            "clinical-context malignant-cell-resolved protein confirmation of the "
            "treated / metastatic persistence direction",
            "EXPERIMENT_REQUIRED",
        ))

    return AggregationOutcome(
        proposed_direction=direction,
        proposed_strength=overall,
        evidence_refs=refs,
        aggregation_rationale=rationale,
        critical_unknowns=tuple(unknowns),
        overall_ceiling=overall,
        landscape_complete=True,
        has_qualifying_direct=has_direct,
        has_qualifying_indirect=has_indirect,
    )
