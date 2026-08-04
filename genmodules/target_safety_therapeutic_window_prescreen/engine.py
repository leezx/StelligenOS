"""Deterministic fatal-first pre-screen rules.

This evaluator consumes already-normalized claims. Evidence retrieval, source
interpretation, and persistence belong to the external runtime.
"""

from __future__ import annotations

from collections import defaultdict

from .contracts import (
    AssessmentRequest,
    AssessmentResult,
    AxisSummary,
    Criticality,
    Decision,
    DifferentialStatus,
    EvidenceAxis,
    EvidenceClaim,
    EvidenceLevel,
    FatalFlag,
    RiskDirection,
)


_LEVEL_ORDER = {
    EvidenceLevel.U: 0,
    EvidenceLevel.D: 1,
    EvidenceLevel.C: 2,
    EvidenceLevel.B: 3,
    EvidenceLevel.A: 4,
}

_NEXT_EXPERIMENTS = {
    EvidenceAxis.NORMAL_TISSUE_EXPRESSION: "external:experiment/normal-tissue-microarray",
    EvidenceAxis.SURFACE_ACCESSIBILITY: "external:experiment/primary-cell-binding",
    EvidenceAxis.ANTIGEN_DENSITY: "external:experiment/calibrated-flow-cytometry",
    EvidenceAxis.SOLUBLE_SINK: "external:experiment/soluble-antigen-binding-pk-sink",
    EvidenceAxis.EXISTING_MODALITY_TOXICITY: "external:experiment/cross-modality-toxicity-review",
    EvidenceAxis.TISSUE_CONSEQUENCE: "external:experiment/tissue-cross-reactivity",
}


def _axis_summaries(claims: tuple[EvidenceClaim, ...]) -> tuple[AxisSummary, ...]:
    grouped: dict[EvidenceAxis, list[EvidenceClaim]] = defaultdict(list)
    for claim in claims:
        grouped[claim.axis].append(claim)
    summaries = []
    for axis in EvidenceAxis:
        axis_claims = grouped[axis]
        summaries.append(
            AxisSummary(
                axis=axis,
                claim_count=len(axis_claims),
                highest_level=max(
                    (claim.level for claim in axis_claims),
                    key=lambda level: _LEVEL_ORDER[level],
                    default=EvidenceLevel.U,
                ),
                unresolved=any(
                    claim.unresolved
                    or claim.level == EvidenceLevel.U
                    or claim.direction == RiskDirection.UNKNOWN
                    for claim in axis_claims
                )
                or not axis_claims,
                risk_claim_count=sum(
                    claim.direction == RiskDirection.SUPPORTS_RISK
                    for claim in axis_claims
                ),
                safety_claim_count=sum(
                    claim.direction == RiskDirection.SUPPORTS_SAFETY
                    for claim in axis_claims
                ),
                conflict_claim_count=sum(
                    claim.direction == RiskDirection.CONFLICTING
                    for claim in axis_claims
                ),
            )
        )
    return tuple(summaries)


def _fatal_flags(claims: tuple[EvidenceClaim, ...]) -> tuple[FatalFlag, ...]:
    flags: list[FatalFlag] = []
    high_quality_surface_risk = any(
        claim.axis == EvidenceAxis.SURFACE_ACCESSIBILITY
        and claim.surface_exposed is True
        and claim.level in {EvidenceLevel.A, EvidenceLevel.B}
        and claim.direction == RiskDirection.SUPPORTS_RISK
        for claim in claims
    )
    high_quality_critical_tissue_risk = any(
        claim.criticality
        in {Criticality.CRITICAL_NON_REGENERATIVE, Criticality.CRITICAL_REVERSIBLE}
        and claim.level in {EvidenceLevel.A, EvidenceLevel.B}
        and claim.direction == RiskDirection.SUPPORTS_RISK
        for claim in claims
    )
    if any(
        (
            claim.axis == EvidenceAxis.SURFACE_ACCESSIBILITY
            and claim.surface_exposed is True
            and claim.criticality == Criticality.CRITICAL_NON_REGENERATIVE
            and claim.level in {EvidenceLevel.A, EvidenceLevel.B}
            and claim.direction == RiskDirection.SUPPORTS_RISK
        )
        for claim in claims
    ):
        flags.append(FatalFlag.CRITICAL_SURFACE_HAZARD)
    elif high_quality_surface_risk and high_quality_critical_tissue_risk:
        flags.append(FatalFlag.CRITICAL_SURFACE_HAZARD)
    if any(
        claim.axis == EvidenceAxis.EXISTING_MODALITY_TOXICITY
        and claim.severe
        and claim.clinically_demonstrated
        and claim.toxicity_attribution == "confirmed_on_target_on_tissue"
        and claim.level == EvidenceLevel.A
        for claim in claims
    ):
        flags.append(FatalFlag.CONFIRMED_ON_TARGET_TOXICITY)
    high_quality_density_risk = any(
        claim.axis == EvidenceAxis.ANTIGEN_DENSITY
        and claim.normal_density_relation in {"similar", "higher"}
        and claim.level in {EvidenceLevel.A, EvidenceLevel.B}
        and claim.direction == RiskDirection.SUPPORTS_RISK
        for claim in claims
    )
    if high_quality_density_risk and high_quality_surface_risk and high_quality_critical_tissue_risk:
        flags.append(FatalFlag.NORMAL_DENSITY_NOT_LOWER)
    if any(
        claim.axis == EvidenceAxis.SOLUBLE_SINK
        and claim.severe
        and claim.clinically_demonstrated
        and claim.level == EvidenceLevel.A
        and claim.direction == RiskDirection.SUPPORTS_RISK
        for claim in claims
    ):
        flags.append(FatalFlag.CLINICAL_SINK_EXPOSURE_FAILURE)
    if any(
        claim.axis == EvidenceAxis.NORMAL_TISSUE_EXPRESSION
        and claim.differential_status == DifferentialStatus.ABSENT
        and claim.level in {EvidenceLevel.A, EvidenceLevel.B}
        and claim.direction == RiskDirection.SUPPORTS_RISK
        for claim in claims
    ):
        flags.append(FatalFlag.NO_EXPLOITABLE_DIFFERENTIAL)
    return tuple(flags)


def assess_target(request: AssessmentRequest) -> AssessmentResult:
    """Assess target-intrinsic risk without claiming product safety."""

    summaries = _axis_summaries(request.claims)
    fatal_flags = _fatal_flags(request.claims)
    unresolved_refs = tuple(
        claim.claim_ref
        for claim in request.claims
        if claim.unresolved
        or claim.level == EvidenceLevel.U
        or claim.direction == RiskDirection.UNKNOWN
    )
    conflict_refs = tuple(
        claim.claim_ref
        for claim in request.claims
        if claim.direction == RiskDirection.CONFLICTING
    )
    critical_unknown = any(
        claim.criticality
        in {Criticality.CRITICAL_NON_REGENERATIVE, Criticality.CRITICAL_REVERSIBLE}
        and (
            claim.unresolved
            or claim.level in {EvidenceLevel.D, EvidenceLevel.U}
            or claim.direction in {RiskDirection.UNKNOWN, RiskDirection.CONFLICTING}
        )
        for claim in request.claims
    )
    material_risk_refs = tuple(
        claim.claim_ref
        for claim in request.claims
        if claim.direction == RiskDirection.SUPPORTS_RISK
    )
    incomplete_axes = any(summary.unresolved for summary in summaries)
    has_plausible_differential = any(
        claim.differential_status == DifferentialStatus.PRESENT
        and claim.direction == RiskDirection.SUPPORTS_SAFETY
        and claim.axis
        in {
            EvidenceAxis.SURFACE_ACCESSIBILITY,
            EvidenceAxis.ANTIGEN_DENSITY,
            EvidenceAxis.TISSUE_CONSEQUENCE,
        }
        and claim.level in {EvidenceLevel.B, EvidenceLevel.C}
        for claim in request.claims
    )
    if fatal_flags:
        decision = Decision.KILL
    elif (
        not request.claims
        or critical_unknown
        or conflict_refs
        or unresolved_refs
        or incomplete_axes
    ):
        decision = Decision.HOLD
    elif material_risk_refs:
        decision = (
            Decision.CONDITIONAL_GO
            if has_plausible_differential
            else Decision.HOLD
        )
    else:
        decision = Decision.GO

    needed_axes = {
        summary.axis for summary in summaries if summary.unresolved
    }
    next_experiments = tuple(_NEXT_EXPERIMENTS[axis] for axis in EvidenceAxis if axis in needed_axes)
    mitigation_refs = (
        ("external:mitigation/epitope-or-density-differential",)
        if decision == Decision.CONDITIONAL_GO
        else ()
    )
    confidence = "high" if fatal_flags or not unresolved_refs else "low"
    if decision == Decision.CONDITIONAL_GO and confidence == "high":
        confidence = "medium"
    return AssessmentResult(
        contract_version="0.2.0",
        request_ref=request.request_ref,
        target_ref=request.target.target_ref,
        axis_summaries=summaries,
        fatal_flags=fatal_flags,
        unresolved_refs=unresolved_refs,
        conflict_refs=conflict_refs,
        material_risk_refs=material_risk_refs,
        mitigation_refs=mitigation_refs,
        next_experiment_refs=next_experiments,
        decision=decision,
        confidence=confidence,
        limitation_ref="external:limitation/target-level-not-product-therapeutic-window",
    )
