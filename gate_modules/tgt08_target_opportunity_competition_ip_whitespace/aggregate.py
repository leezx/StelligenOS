"""Deterministic Direction x Strength aggregation for TGT-08 (E6-3 / E6-4).

Frozen -- E6 has no discretion.

Per-axis authority ceiling comes from the completion state:
  competitive: primary_source_landscape_complete -> DIRECT
               else pipeline_inventory_complete   -> INDIRECT_STRONG
               else                               -> NOT_EVALUABLE
  patent:      composition_level_review_complete  -> DIRECT
               else target_level_search_complete  -> INDIRECT_STRONG
               else                               -> NOT_EVALUABLE

Overall Strength = the WEAKER required axis ceiling (never "both searched" ->
DIRECT).

Precedence (E5, four review rounds):
  * neither target-specific axis attempted AND admissible unmet-need evidence
    -> INCONCLUSIVE / WEAK  (the only two-axis exemption; CONTEXTUAL refs)
  * a target-specific landscape assessment WAS attempted and either mandatory
    axis is incomplete / not evaluable, OR there is no admissible evaluable
    landscape -> INCONCLUSIVE / UNKNOWN  (no evidence_refs)
  * both axes evaluable:
      only material SUPPORTS_OPPORTUNITY  -> POSITIVE  / overall rung
      only material OPPOSES_OPPORTUNITY   -> NEGATIVE  / overall rung
      both                                -> CONFLICTING / overall rung
      neither                             -> INCONCLUSIVE / overall rung (graded, CONTEXTUAL refs)

An absence SUPPORT is derived ONLY from an attempted + coverage-complete +
evaluable + audited completion whose qualifying set is empty -- never from
``records == []``. NEGATIVE is a Gate-relative opportunity judgement, never a
KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE.
"""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import (
    CompetitiveLandscapeCompletion,
    EmittedEvidence,
    PatentLandscapeCompletion,
    overall_strength,
)


@dataclass(frozen=True)
class AggregationOutcome:
    proposed_direction: str
    proposed_strength: str
    evidence_refs: tuple[tuple[str, str], ...]
    aggregation_rationale: str
    critical_unknowns: tuple[tuple[str, str], ...]
    competitive_ceiling: str
    patent_ceiling: str
    overall_ceiling: str
    competitive_absence_support: bool
    patent_absence_support: bool


def audit_snapshot_mismatch(
    record,
    competitive: CompetitiveLandscapeCompletion,
    patent: PatentLandscapeCompletion,
) -> str:
    """E6 round-1 blocker 1: a SEARCH_COMPLETION_AUDIT record that names a
    completion's ``audit_observation_id`` MUST carry a structured snapshot equal
    to that typed completion state. Return "" when it matches (or is not the
    certificate for either completion), else a drift reason. A non-empty return
    is a HARD run-level integrity failure -- the machine never derives an axis
    ceiling or an absence inference from an audit whose own snapshot disagrees
    with the completion it is supposed to certify."""

    axis = record.evidence_axis
    if axis == "COMPETITIVE":
        c = competitive
        if not c.attempted or c.audit_observation_id != record.observation_id:
            return ""
        pairs = (
            (record.audit_search_scope, c.search_scope, "audit_search_scope"),
            (set(record.audit_sources_searched), set(c.sources_searched),
             "audit_sources_searched"),
            (record.audit_coverage_complete, c.coverage_complete,
             "audit_coverage_complete"),
            (set(record.audit_unresolved_items), set(c.unresolved_items),
             "audit_unresolved_items"),
            (record.audit_primary_source_landscape_complete,
             c.primary_source_landscape_complete,
             "audit_primary_source_landscape_complete"),
            (record.audit_pipeline_inventory_complete, c.pipeline_inventory_complete,
             "audit_pipeline_inventory_complete"),
            (set(record.audit_qualifying_program_ids), set(c.qualifying_program_ids),
             "audit_qualifying_program_ids"),
        )
    elif axis == "PATENT":
        p = patent
        if not p.attempted or p.audit_observation_id != record.observation_id:
            return ""
        pairs = (
            (record.audit_search_scope, p.patent_scope, "audit_search_scope"),
            (set(record.audit_sources_searched), set(p.sources_searched),
             "audit_sources_searched"),
            (record.audit_coverage_complete, p.coverage_complete,
             "audit_coverage_complete"),
            (set(record.audit_unresolved_items), set(p.unresolved_items),
             "audit_unresolved_items"),
            (set(record.audit_jurisdictions), set(p.jurisdictions),
             "audit_jurisdictions"),
            (record.audit_composition_level_review_complete,
             p.composition_level_review_complete,
             "audit_composition_level_review_complete"),
            (record.audit_target_level_search_complete, p.target_level_search_complete,
             "audit_target_level_search_complete"),
            (set(record.audit_qualifying_patent_family_ids),
             set(p.qualifying_patent_family_ids), "audit_qualifying_patent_family_ids"),
        )
    else:
        return ""
    for got, want, name in pairs:
        if got != want:
            return (
                f"SEARCH_COMPLETION_AUDIT snapshot field {name} = {got!r} disagrees "
                f"with the typed completion state {want!r}"
            )
    return ""


def _audit_ep_for(emitted: list[EmittedEvidence], axis: str, observation_id: str) -> str:
    for e in emitted:
        r = e.classified.record
        if (
            r.observation_kind == "SEARCH_COMPLETION_AUDIT"
            and r.evidence_axis == axis
            and r.observation_id == observation_id
        ):
            return e.evidence_id
    return ""


def aggregate(
    emitted: list[EmittedEvidence],
    competitive: CompetitiveLandscapeCompletion,
    patent: PatentLandscapeCompletion,
) -> AggregationOutcome:
    comp_ceiling = competitive.axis_ceiling
    pat_ceiling = patent.axis_ceiling
    overall = overall_strength(comp_ceiling, pat_ceiling)

    target_specific_attempted = competitive.attempted or patent.attempted
    both_evaluable = competitive.evaluable and patent.evaluable

    unmet_need_ev = [
        e for e in emitted
        if e.classified.record.observation_kind == "UNMET_NEED_CONTEXT"
    ]
    opposes_ev = [
        e for e in emitted
        if e.classified.opportunity_implication == "OPPOSES_OPPORTUNITY"
    ]
    contextual_ev = [
        e for e in emitted
        if e.classified.opportunity_implication == "CONTEXTUAL"
    ]

    # --- absence SUPPORT derivation (E6-4) -------------------------------
    comp_support_ref = ""
    if (
        competitive.attempted
        and competitive.coverage_complete
        and competitive.evaluable
        and len(competitive.qualifying_program_ids) == 0
    ):
        comp_support_ref = _audit_ep_for(
            emitted, "COMPETITIVE", competitive.audit_observation_id
        )
    pat_support_ref = ""
    if (
        patent.attempted
        and patent.coverage_complete
        and patent.evaluable
        and len(patent.qualifying_patent_family_ids) == 0
    ):
        pat_support_ref = _audit_ep_for(
            emitted, "PATENT", patent.audit_observation_id
        )
    support_ep_ids = tuple(x for x in (comp_support_ref, pat_support_ref) if x)

    unknowns: list[tuple[str, str]] = []
    for item in (*competitive.unresolved_items, *patent.unresolved_items):
        unknowns.append((
            f"unresolved landscape item: {item} -- external legal / sponsor "
            "review may be required",
            "CURRENTLY_UNRESOLVABLE",
        ))

    # --- precedence -----------------------------------------------------
    if not target_specific_attempted:
        if unmet_need_ev:
            refs = [(e.evidence_id, "CONTEXTUAL") for e in unmet_need_ev]
            refs += [(e.evidence_id, "CONTEXTUAL") for e in contextual_ev
                     if e not in unmet_need_ev]
            return AggregationOutcome(
                proposed_direction="INCONCLUSIVE",
                proposed_strength="WEAK",
                evidence_refs=tuple(refs),
                aggregation_rationale=(
                    "no target-specific competitive or IP read was attempted; only "
                    "an indication-level unmet-need signal is available. Per the "
                    "frozen PR D WEAK rung this is a hypothesis only -- "
                    "INCONCLUSIVE / WEAK, never 'good opportunity', and it is "
                    "EXEMPT from the two-axis mandatory completion."
                ),
                critical_unknowns=tuple(unknowns),
                competitive_ceiling=comp_ceiling,
                patent_ceiling=pat_ceiling,
                overall_ceiling=overall,
                competitive_absence_support=False,
                patent_absence_support=False,
            )
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "no admissible evaluable landscape: no target-specific assessment "
                "was attempted and there is no admissible unmet-need context. "
                "INCONCLUSIVE / UNKNOWN -- 'we could not look', never attractive / "
                "uncrowded / whitespace."
            ),
            critical_unknowns=tuple(unknowns),
            competitive_ceiling=comp_ceiling,
            patent_ceiling=pat_ceiling,
            overall_ceiling=overall,
            competitive_absence_support=False,
            patent_absence_support=False,
        )

    if not both_evaluable:
        if not competitive.evaluable:
            unknowns.append((
                "the competitive-landscape axis is incomplete or not evaluable",
                "PUBLIC_RESOLVABLE",
            ))
        if not patent.evaluable:
            unknowns.append((
                "the composition-level patent-landscape axis is incomplete or not "
                "evaluable",
                "PUBLIC_RESOLVABLE",
            ))
        return AggregationOutcome(
            proposed_direction="INCONCLUSIVE",
            proposed_strength="UNKNOWN",
            evidence_refs=(),
            aggregation_rationale=(
                "a target-specific landscape assessment was attempted but a "
                "mandatory axis is incomplete / not evaluable. Per the frozen "
                "contract an incomplete landscape is INCONCLUSIVE / UNKNOWN -- a "
                "half landscape cannot yield a target-opportunity judgement."
            ),
            critical_unknowns=tuple(unknowns),
            competitive_ceiling=comp_ceiling,
            patent_ceiling=pat_ceiling,
            overall_ceiling=overall,
            competitive_absence_support=bool(comp_support_ref),
            patent_absence_support=bool(pat_support_ref),
        )

    # both axes evaluable -> graded assessment at the weaker required ceiling
    has_supports = bool(support_ep_ids)
    has_opposes = bool(opposes_ev)

    refs: list[tuple[str, str]] = []
    for ep_id in support_ep_ids:
        refs.append((ep_id, "SUPPORTING"))
    for e in opposes_ev:
        refs.append((e.evidence_id, "CONTRADICTING"))
    for e in contextual_ev:
        if e.evidence_id in support_ep_ids:
            continue
        refs.append((e.evidence_id, "CONTEXTUAL"))

    if has_supports and has_opposes:
        direction = "CONFLICTING"
        rationale = (
            "the completed two-axis landscape carries BOTH a material "
            "opportunity-supporting signal (an audited search found no qualifying "
            "landmark) and a material opportunity-opposing signal. Direction "
            f"CONFLICTING at the overall rung {overall} (the weaker required axis "
            "ceiling)."
        )
    elif has_opposes:
        direction = "NEGATIVE"
        rationale = (
            "the completed two-axis landscape carries only material "
            "opportunity-opposing signals (approved / registrational / "
            "active-clinical same-target programs and / or live composition-level "
            f"patent claims). Direction NEGATIVE at the overall rung {overall}. "
            "NEGATIVE weighs against a differentiated entry -- it is NOT a KILL, "
            "STOP_FOR_SPONSOR, OUT_OF_MANDATE, an FTO-blocked finding, or a "
            "scientific verdict on the target."
        )
    elif has_supports:
        direction = "POSITIVE"
        rationale = (
            "the completed two-axis landscape carries only material "
            "opportunity-supporting signals (an audited competitive / patent "
            "search found no qualifying landmark). Direction POSITIVE at the "
            f"overall rung {overall}."
        )
    else:
        direction = "INCONCLUSIVE"
        rationale = (
            "the two-axis landscape is coverage-complete and fully audited but "
            "carries no material directional target-specific signal -- neither a "
            "material SUPPORTS_OPPORTUNITY nor a material OPPOSES_OPPORTUNITY. "
            f"This is a GRADED INCONCLUSIVE at the overall rung {overall} (the "
            "landscape was audited and has a valid grade; it simply does not "
            "resolve direction), NOT INCONCLUSIVE / UNKNOWN."
        )

    return AggregationOutcome(
        proposed_direction=direction,
        proposed_strength=overall,
        evidence_refs=tuple(refs),
        aggregation_rationale=rationale,
        critical_unknowns=tuple(unknowns),
        competitive_ceiling=comp_ceiling,
        patent_ceiling=pat_ceiling,
        overall_ceiling=overall,
        competitive_absence_support=bool(comp_support_ref),
        patent_absence_support=bool(pat_support_ref),
    )
