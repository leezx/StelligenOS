"""Deterministic Direction x Strength aggregation for TGT-06 (E13 item 06, E14-4).

TGT-06 uses a HIGHEST-QUALIFYING-RUNG grading authority under an EXISTENCE-PROOF
truth table (the TGT-03 precedent, NOT the TGT-04 single-tier exception). E14
writes the frozen ``frozen_evaluation_order`` DIRECTLY -- there is no generic
``highest_rung`` / ``generic_bidirectional_aggregate`` helper and no pile of
exceptions.

Every configuration test is over the ONE frozen
``configuration_identity_projection`` (contracts.configuration_identity_projection):
a SINGLE observation projects to {its id}; an IDENTIFIED_MULTI observation
projects to its full id set (an IDENTIFIED_MULTI {A, B} failure contributes BOTH
A and B); an IDENTITY_NOT_DISCLOSED observation projects to {} .

frozen_evaluation_order -- applied in this exact order, STOP at the first match:

  0. not completed / audit-invalid -> handled by the item-16 stop rule (module.py)
  1. group DIRECT-quality observations (productive and failure) by projected id
  2. >= 1 CLEAN / uncontested productive DIRECT configuration (in a productive
     DIRECT observation's projection AND in NO DIRECT-quality failure
     observation's projection)                              -> POSITIVE / DIRECT
       (existence-proof dominance -- beats heterogeneous B / C failures AND a
        conflicted configuration A elsewhere)
  3. else a configuration identity carries BOTH a qualifying productive DIRECT
     observation AND a qualifying DIRECT-quality failure observation
                                                            -> CONFLICTING / DIRECT
       (v1 has NO machine conflict resolver -- the Module never reconciles it)
  4. else >= 2 independent DIRECT-quality failure configuration identities and no
     productive DIRECT                                       -> NEGATIVE / DIRECT
  5. else exactly ONE DIRECT-quality failure configuration identity and no
     productive DIRECT                                       -> INCONCLUSIVE / DIRECT
       (a single non-internalizing configuration NEVER establishes target-wide
        non-internalization -- PR D forbidden_inference)
  6. else no DIRECT-rung observation but >= 1 qualifying positive INDIRECT_STRONG
                                                            -> POSITIVE / INDIRECT_STRONG
  7. else WEAK-only / no qualifying evidence   -> INCONCLUSIVE / UNKNOWN, zero refs

Legal pairs (frozen, exactly 6): POSITIVE / DIRECT, POSITIVE / INDIRECT_STRONG,
NEGATIVE / DIRECT, CONFLICTING / DIRECT, INCONCLUSIVE / DIRECT,
INCONCLUSIVE / UNKNOWN.

Frozen proposal evidence-role mapping (E14-4): different-configuration failures
under a clean productive existence proof are CONTEXTUAL, NOT CONTRADICTING -- they
are configuration-specific information, not a logical disproof of the existence
proof.
"""

from __future__ import annotations

from dataclasses import dataclass

from .completion import InternalizationEvidenceCompletion
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
    has_qualifying_direct_productive: bool
    has_qualifying_direct_failure: bool
    has_qualifying_indirect: bool


_EXPERIMENT_UNKNOWN = (
    "test additional independent antibody / epitope configurations with an "
    "antibody-induced internalization + productive lysosomal trafficking readout "
    "on a CRC-relevant model"
)


def _incomplete_landscape_unknowns(
    completion: InternalizationEvidenceCompletion,
) -> tuple[tuple[str, str], ...]:
    unknowns: list[tuple[str, str]] = []
    for item in completion.unresolved_items:
        unknowns.append(
            (
                f"unresolved internalization-evidence search item: {item.description}",
                item.resolution,
            )
        )
    if not completion.attempted:
        unknowns.append(
            (
                "no target-specific public internalization-evidence search was attempted",
                "PUBLIC_RESOLVABLE",
            )
        )
    elif not completion.landscape_complete:
        unknowns.append(
            (
                "the mandatory public internalization-evidence landscape "
                "(antibody-configuration internalization / productive trafficking / "
                "same-target ADC functional-delivery precedent / receptor endocytosis "
                "and inference) is not complete",
                "PUBLIC_RESOLVABLE",
            )
        )
    return tuple(unknowns)


def aggregate(
    emitted: list[EmittedEvidence],
    completion: InternalizationEvidenceCompletion,
) -> AggregationOutcome:
    admissible = [e for e in emitted if e.classified.admissible]
    productive = [e for e in admissible if e.classified.qualifying_direct_productive]
    failures = [e for e in admissible if e.classified.qualifying_direct_failure]
    indirect = [e for e in admissible if e.classified.qualifying_indirect]
    has_productive = bool(productive)
    has_failure = bool(failures)
    has_indirect = bool(indirect)

    # --- step 0 / incomplete landscape -> UNKNOWN --------------------------
    if not completion.landscape_complete:
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "the mandatory public internalization-evidence landscape is not "
                "complete and audited. Per the frozen contract a single "
                "internalization movie, a single trafficking dataset or a single "
                "failure observation is never a completed answer -- INCONCLUSIVE / "
                "UNKNOWN, and the UNKNOWN carries zero evidence_refs."
            ),
            critical_unknowns=_incomplete_landscape_unknowns(completion),
            overall_ceiling="",
            landscape_complete=False,
            has_qualifying_direct_productive=has_productive,
            has_qualifying_direct_failure=has_failure,
            has_qualifying_indirect=has_indirect,
        )

    # --- step 1: project configuration identities ------------------------
    productive_ids: set[str] = set()
    for e in productive:
        productive_ids |= set(e.configuration_identities)
    failure_ids: set[str] = set()
    for e in failures:
        failure_ids |= set(e.configuration_identities)
    clean_productive_ids = productive_ids - failure_ids
    conflicted_ids = productive_ids & failure_ids

    unknowns: list[tuple[str, str]] = [
        (
            f"unresolved internalization-evidence search item: {i.description}",
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

    # --- step 2: a CLEAN / uncontested productive DIRECT configuration ----
    if clean_productive_ids:
        rationale = (
            "the completed audited internalization-evidence landscape carries at "
            "least one CLEAN / uncontested qualifying productive DIRECT antibody / "
            "epitope configuration (antibody-induced internalization AND lysosomal "
            "delivery in a qualified disease-relevant context, with no "
            "same-configuration DIRECT-quality failure). Internalization is "
            "configuration-specific: one addressable configuration is a sufficient "
            "existence proof. Direction POSITIVE / DIRECT (existence-proof dominance "
            "-- heterogeneous failures for other configurations, and a conflicted "
            "configuration elsewhere, are retained as CONTEXTUAL configuration-"
            "specific information and never reverse the target-level conclusion)."
        )
        return AggregationOutcome(
            proposed_direction="POSITIVE",
            proposed_strength="DIRECT",
            evidence_refs=_refs(productive, []),
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="DIRECT",
            landscape_complete=True,
            has_qualifying_direct_productive=True,
            has_qualifying_direct_failure=has_failure,
            has_qualifying_indirect=has_indirect,
        )

    # --- step 3: a single configuration carries BOTH a productive DIRECT and
    #     a DIRECT-quality failure -> CONFLICTING / DIRECT (NO resolver) -----
    if conflicted_ids:
        same_config_failures = [
            e for e in failures if set(e.configuration_identities) & conflicted_ids
        ]
        rationale = (
            "the completed audited internalization-evidence landscape carries, for "
            "the SAME antibody / epitope configuration identity, BOTH a qualifying "
            "productive DIRECT observation (antibody-induced internalization with "
            "lysosomal delivery) AND a qualifying DIRECT-quality "
            "productive-internalization / trafficking failure observation, both "
            "admissible. Per the frozen contract there is NO machine conflict "
            "resolver in v1 -- assay / model / context variation for that one "
            "configuration is a human-review question. Direction CONFLICTING / DIRECT."
        )
        return AggregationOutcome(
            proposed_direction="CONFLICTING",
            proposed_strength="DIRECT",
            evidence_refs=_refs(productive, same_config_failures),
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="DIRECT",
            landscape_complete=True,
            has_qualifying_direct_productive=True,
            has_qualifying_direct_failure=True,
            has_qualifying_indirect=has_indirect,
        )

    # --- steps 4 / 5: DIRECT-quality failures, no productive DIRECT --------
    if failure_ids:
        n = len(failure_ids)
        if n >= 2:
            rationale = (
                "the completed audited internalization-evidence landscape carries "
                "qualifying DIRECT-quality productive-internalization / trafficking "
                f"FAILURE evidence across {n} independent antibody / epitope "
                "configuration identities, and NO qualifying productive DIRECT "
                "configuration exists. This has escalated beyond a single "
                "configuration's failure to a target-level surface-static / "
                "non-productively-internalizing pattern. Direction NEGATIVE / DIRECT. "
                "This is a Gate-relative scientific addressability judgement; a "
                "separate machine-local review record is set only when the frozen "
                "Route A / Route B multiple-independent-configuration criteria are "
                "met, and the Candidate-level consequence is decided downstream, not "
                "by this Module."
            )
            direction, strength = "NEGATIVE", "DIRECT"
            refs = _refs([], failures)
        else:
            if public_space_exhausted:
                unknowns.append((_EXPERIMENT_UNKNOWN, "EXPERIMENT_REQUIRED"))
            rationale = (
                "the completed audited internalization-evidence landscape carries "
                "exactly ONE independent DIRECT-quality productive-internalization / "
                "trafficking FAILURE configuration identity and NO qualifying "
                "productive DIRECT configuration. A single non-internalizing "
                "antibody / epitope configuration NEVER establishes target-wide "
                "non-internalization (PR D forbidden_inference). Direction "
                "INCONCLUSIVE / DIRECT, carrying its OPPOSES_ADDRESSABILITY "
                "evidence_ref as CONTEXTUAL."
            )
            direction, strength = "INCONCLUSIVE", "DIRECT"
            refs = _refs([], [])  # failures fall through to CONTEXTUAL
        return AggregationOutcome(
            proposed_direction=direction,
            proposed_strength=strength,
            evidence_refs=refs,
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="DIRECT",
            landscape_complete=True,
            has_qualifying_direct_productive=False,
            has_qualifying_direct_failure=True,
            has_qualifying_indirect=has_indirect,
        )

    # --- step 6: no DIRECT-rung observation, >= 1 positive INDIRECT_STRONG -
    if has_indirect:
        rationale = (
            "the completed audited internalization-evidence landscape carries no "
            "DIRECT-rung antibody / epitope configuration observation but at least "
            "one qualifying positive INDIRECT_STRONG addressability observation "
            "(constitutive endocytosis / established internalizing-receptor biology "
            "/ non-CRC antibody-induced internalization / a successful same-target "
            "ADC functional-delivery precedent). Per the highest-qualifying-rung "
            "authority these are genuine positive addressability support. Direction "
            "POSITIVE / INDIRECT_STRONG."
        )
        return AggregationOutcome(
            proposed_direction="POSITIVE",
            proposed_strength="INDIRECT_STRONG",
            evidence_refs=_refs(indirect, []),
            aggregation_rationale=rationale,
            critical_unknowns=tuple(unknowns),
            overall_ceiling="INDIRECT_STRONG",
            landscape_complete=True,
            has_qualifying_direct_productive=False,
            has_qualifying_direct_failure=False,
            has_qualifying_indirect=True,
        )

    # --- step 7: WEAK-only / no qualifying evidence -> UNKNOWN ------------
    if public_space_exhausted:
        unknowns.append((_EXPERIMENT_UNKNOWN, "EXPERIMENT_REQUIRED"))
    rationale = (
        "the completed audited public internalization-evidence landscape yielded "
        "only WEAK receptor-family-membership / surface-localization-only inference "
        "evidence (or no qualifying evidence at all), which cannot answer the "
        "internalization / trafficking addressability question. Verbatim from the "
        "frozen contract: 'No internalization data for any configuration -> "
        "UNKNOWN.' INCONCLUSIVE / UNKNOWN with zero evidence_refs."
    )
    return AggregationOutcome(
        proposed_direction="INCONCLUSIVE",
        proposed_strength="UNKNOWN",
        evidence_refs=(),
        aggregation_rationale=rationale,
        critical_unknowns=tuple(unknowns),
        overall_ceiling="",
        landscape_complete=True,
        has_qualifying_direct_productive=False,
        has_qualifying_direct_failure=False,
        has_qualifying_indirect=False,
    )
