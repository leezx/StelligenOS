"""Deterministic Direction x Strength aggregation for TGT-02 (E7 item 06, E8-4).

Frozen -- E8 has no discretion.

Precedence:
  0. a HARD integrity failure -> no proposal            (module.py, not here)
  1. the mandatory CRC coverage landscape is not complete / audited
        -> INCONCLUSIVE / UNKNOWN, zero evidence_refs
  2. the landscape is complete but its audit is invalid / missing
        -> HARD reject                                    (module.py, not here)
  3. the landscape is complete AND audited -> evaluate the qualifying evidence:

     overall Strength = the HIGHEST qualifying frozen evidence class
       any qualifying DIRECT protein cohort   -> DIRECT
       else any qualifying INDIRECT_STRONG    -> INDIRECT_STRONG
       else (only WEAK / contextual)          -> INCONCLUSIVE / UNKNOWN

     Direction over the qualifying directional evidence:
       a valid audited multi-cohort finding that characterises coverage as
         RARE_HIGHLY_HETEROGENEOUS across >= 2 cohorts   -> NEGATIVE (never CONFLICTING)
       else material SUPPORTS + material OPPOSES          -> CONFLICTING
       else material OPPOSES only                         -> NEGATIVE
       else material SUPPORTS only                        -> POSITIVE
       else (qualifying evidence exists, nondirectional)  -> graded INCONCLUSIVE

There is NO E6-style two-axis weaker-ceiling rule. A single negative protein
cohort is a DIRECT-class NEGATIVE-supporting observation, never a NEGATIVE /
DIRECT proposal on its own -- the proposal is an AGGREGATE over the completed
landscape. NEGATIVE weighs the science against adequate malignant-cell coverage;
it is never a KILL.
"""

from __future__ import annotations

from dataclasses import dataclass

from .completion import CrcCohortCoverageCompletion
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
    completion: CrcCohortCoverageCompletion,
) -> tuple[tuple[str, str], ...]:
    unknowns: list[tuple[str, str]] = []
    for item in completion.unresolved_items:
        unknowns.append((
            f"unresolved CRC coverage search item: {item.description}",
            item.resolution,
        ))
    if not completion.attempted:
        unknowns.append((
            "no target-specific public CRC malignant-cell coverage search was attempted",
            "PUBLIC_RESOLVABLE",
        ))
    elif not completion.landscape_complete:
        unknowns.append((
            "the mandatory public CRC coverage landscape (protein cohort / "
            "malignant-compartment sc-spatial / TMA concordance / matched "
            "normal-tumor) is not complete",
            "PUBLIC_RESOLVABLE",
        ))
    return tuple(unknowns)


def aggregate(
    emitted: list[EmittedEvidence],
    completion: CrcCohortCoverageCompletion,
) -> AggregationOutcome:
    admissible = [e for e in emitted if e.classified.admissible]

    # --- precedence 1: incomplete / unaudited landscape -> UNKNOWN -----------
    if not completion.landscape_complete:
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the mandatory public CRC malignant-cell coverage landscape is not "
                "complete and audited. Per the frozen contract a single positive or "
                "negative cohort is never a completed population-level answer -- "
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
        (f"unresolved CRC coverage search item: {i.description}", i.resolution)
        for i in completion.unresolved_items
    ]
    # EXPERIMENT_REQUIRED only when the public source space is TRULY exhausted --
    # i.e. no declared unresolved public item still offers a resolution path
    # (E7 item 15 / E8-7). While any unresolved item remains, a blocked / not-yet-
    # fetched public source could still supply the missing measurement.
    public_space_exhausted = not completion.unresolved_items

    # WEAK-only completed landscape -> INCONCLUSIVE / UNKNOWN (never / WEAK).
    if not overall:
        if public_space_exhausted:
            unknowns.append((
                "the completed public CRC coverage search yielded no DIRECT protein "
                "cohort and no qualifying malignant-compartment sc / spatial / TMA "
                "concordance evidence -- only bulk / pan-cancer signal remains, which "
                "cannot answer the CRC x malignant-compartment x cohort-level question",
                "EXPERIMENT_REQUIRED",
            ))
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the public CRC coverage landscape is complete and audited but "
                "carries only WEAK bulk / pan-cancer evidence. Verbatim from the "
                "frozen contract: 'Only bulk RNA available -> UNKNOWN, not a pass.' "
                "INCONCLUSIVE / UNKNOWN with zero evidence_refs; a new "
                "malignant-cell-resolved protein / adequately powered cohort "
                "measurement is required."
            ),
            critical_unknowns=tuple(unknowns),
            overall_ceiling=_UNKNOWN_CEILING,
            landscape_complete=True,
            has_qualifying_direct=False,
            has_qualifying_indirect=False,
        )

    qualifying = qualifying_direct + qualifying_indirect
    supports = [e for e in qualifying if e.classified.coverage_support == "SUPPORTS_COVERAGE"]
    opposes = [e for e in qualifying if e.classified.coverage_support == "OPPOSES_COVERAGE"]

    # qualified-heterogeneity precedence: a valid audited multi-cohort finding
    # that characterises coverage as RARE_HIGHLY_HETEROGENEOUS across >= 2
    # independent cohort identities is NEGATIVE, not CONFLICTING.
    heterogeneity_resolver = next(
        (
            e
            for e in qualifying
            if e.observation.expression_pattern == "RARE_HIGHLY_HETEROGENEOUS"
            and e.observation.declared_multi_cohort_analysis
            and e.observation.expression_pattern_basis
            and len(set(e.observation.cohort_identities)) >= 2
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

    if heterogeneity_resolver is not None:
        direction = "NEGATIVE"
        rationale = (
            "a valid audited multi-cohort finding across at least two independent "
            "cohort identities explicitly characterises malignant-cell target "
            f"coverage as RARE_HIGHLY_HETEROGENEOUS (basis "
            f"{heterogeneity_resolver.observation.expression_pattern_basis}). Per "
            "the frozen contract this is NEGATIVE, not CONFLICTING, and the "
            f"Strength is not auto-degraded. Direction NEGATIVE at the overall "
            f"rung {overall}. This is a Gate-relative scientific coverage "
            "judgement; the Candidate-level consequence is decided by human "
            "review and the GateSet policy downstream, not by this Module."
        )
        refs = _refs("NEGATIVE")
    elif has_supports and has_opposes:
        direction = "CONFLICTING"
        rationale = (
            "the completed audited CRC coverage landscape carries qualifying "
            "observations that make genuinely incompatible coverage claims "
            "(qualifying evidence for broad malignant-cell presence AND qualifying "
            "evidence for absent / non-covered malignant compartment) and no valid "
            f"cross-cohort characterisation resolves them. Direction CONFLICTING at "
            f"the overall rung {overall}."
        )
        refs = _refs("CONFLICTING")
    elif has_opposes:
        direction = "NEGATIVE"
        rationale = (
            "the completed audited CRC coverage landscape carries only qualifying "
            "opposing evidence -- protein-cohort and / or malignant-compartment "
            "observations supporting absent or non-covered malignant-cell target "
            f"expression. Direction NEGATIVE at the overall rung {overall}. This "
            "is a Gate-relative scientific coverage judgement; a separate "
            "cross-cohort machine-local review record is set only when the "
            "frozen cross-cohort criteria are met, and the Candidate-level "
            "consequence is decided downstream, not by this Module."
        )
        refs = _refs("NEGATIVE")
    elif has_supports:
        direction = "POSITIVE"
        rationale = (
            "the completed audited CRC coverage landscape carries only qualifying "
            "supporting evidence -- protein-cohort and / or malignant-compartment "
            "observations supporting broad consistent malignant-cell target "
            f"presence. Direction POSITIVE at the overall rung {overall}."
        )
        refs = _refs("POSITIVE")
    else:
        direction = "INCONCLUSIVE"
        rationale = (
            "the completed audited CRC coverage landscape contains qualifying "
            "DIRECT / INDIRECT_STRONG-quality evidence but the coverage direction "
            "is MIXED and does not resolve presence vs inadequate coverage. This "
            f"is a GRADED INCONCLUSIVE at the overall rung {overall} (distinct "
            "from INCONCLUSIVE / UNKNOWN), carrying its CONTEXTUAL evidence_refs."
        )
        refs = _refs("INCONCLUSIVE")

    # EXPERIMENT_REQUIRED -- exactly the one E7-explicit graded mapping: a
    # directional INDIRECT_STRONG assessment with no qualifying DIRECT protein
    # cohort needs a protein-level confirmation. Only once the public source
    # space is truly exhausted (no unresolved public item still offers a path).
    if (
        public_space_exhausted
        and direction in ("POSITIVE", "NEGATIVE")
        and overall == "INDIRECT_STRONG"
        and not has_direct
    ):
        unknowns.append((
            "protein-level malignant-cell cohort confirmation of the "
            "malignant-compartment coverage direction",
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
