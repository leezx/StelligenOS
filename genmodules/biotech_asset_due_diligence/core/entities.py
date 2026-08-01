"""Canonical Phase 1A records.

These records are deliberately plain and immutable at the Python boundary. They
carry no ADC-specific scoring and do not collapse recommendation into decision.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .artifact_refs import ArtifactRef
from .ids import validate_id


class Record:
    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Asset(Record):
    asset_id: str
    canonical_name: str
    asset_class: str
    status: str = "active"
    programme_owner: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.asset_id, "asset")
        if self.status not in {"active", "paused", "terminated", "archived"}:
            raise ValueError(f"invalid asset status: {self.status}")


@dataclass(frozen=True)
class AssetVariant(Record):
    variant_id: str
    asset_id: str
    variant_kind: str
    molecular_identity_refs: tuple[str, ...] = ()
    indication_context_ids: tuple[str, ...] = ()
    parent_variant_id: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.variant_id, "variant")
        validate_id(self.asset_id, "asset")
        if self.parent_variant_id:
            validate_id(self.parent_variant_id, "variant")


@dataclass(frozen=True)
class AssessmentRun(Record):
    assessment_run_id: str
    asset_id: str
    variant_ids: tuple[str, ...]
    evidence_cutoff: str
    adapter_versions: tuple[str, ...]
    policy_versions: tuple[str, ...]
    reviewer_context: str | None
    artifact_refs: tuple[ArtifactRef, ...] = ()

    def __post_init__(self) -> None:
        validate_id(self.assessment_run_id, "assessment")
        validate_id(self.asset_id, "asset")
        for variant_id in self.variant_ids:
            validate_id(variant_id, "variant")


@dataclass(frozen=True)
class EvidenceSource(Record):
    source_id: str
    source_type: str
    canonical_locator: str
    retrieval_date: str | None = None
    checksum: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.source_id, "source")


@dataclass(frozen=True)
class EvidenceClaim(Record):
    claim_id: str
    source_id: str
    assertion: str
    subject_ref: str
    direction: str
    directness: str = "unknown"

    def __post_init__(self) -> None:
        validate_id(self.claim_id, "claim")
        validate_id(self.source_id, "source")
        if self.direction not in {"supportive", "adverse", "mixed", "neutral"}:
            raise ValueError(f"invalid claim direction: {self.direction}")


@dataclass(frozen=True)
class Observation(Record):
    observation_id: str
    subject_ref: str
    measurement_type: str
    value: Any
    unit: str | None
    quality_status: str
    source_claim_ids: tuple[str, ...]
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_id(self.observation_id, "observation")
        if self.quality_status not in {"usable", "unusable", "unknown", "conflicting"}:
            raise ValueError(f"invalid observation quality: {self.quality_status}")


@dataclass(frozen=True)
class Hypothesis(Record):
    hypothesis_id: str
    statement: str
    subject_ref: str
    state: str
    supporting_claim_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    falsification_criteria: tuple[str, ...]

    def __post_init__(self) -> None:
        validate_id(self.hypothesis_id, "hypothesis")
        if self.state not in {"supported", "unresolved", "contradicted", "conflicting"}:
            raise ValueError(f"invalid hypothesis state: {self.state}")


@dataclass(frozen=True)
class FailureMode(Record):
    failure_mode_id: str
    catalog_ref: str
    status: str
    route_terminating: bool
    basis_refs: tuple[str, ...]
    blocking_for_advance: bool

    def __post_init__(self) -> None:
        validate_id(self.failure_mode_id, "failure_mode")
        if self.status not in {"supported", "excluded", "unresolved", "conflicting"}:
            raise ValueError(f"invalid failure mode status: {self.status}")


@dataclass(frozen=True)
class DecisionUncertainty(Record):
    uncertainty_id: str
    decision_question: str
    candidate_actions: tuple[str, ...]
    blocking_refs: tuple[str, ...]
    resolution_experiment_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        validate_id(self.uncertainty_id, "uncertainty")


@dataclass(frozen=True)
class ExperimentBranch(Record):
    experiment_id: str
    question: str
    hypothesis_ids: tuple[str, ...]
    readiness_status: str
    outcome_branches: tuple[dict[str, Any], ...]

    def __post_init__(self) -> None:
        validate_id(self.experiment_id, "experiment")
        if len(self.outcome_branches) < 2:
            raise ValueError("an experiment requires at least two explicit outcome branches")


@dataclass(frozen=True)
class SystemRecommendation(Record):
    recommendation_id: str
    assessment_run_id: str
    policy_version: str
    action: str
    rejected_alternatives: tuple[dict[str, Any], ...]
    basis_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        validate_id(self.recommendation_id, "recommendation")
        if self.action not in {"advance", "hold_for_evidence", "pivot", "abandon_route", "abandon_asset", "insufficient_information"}:
            raise ValueError(f"invalid recommendation action: {self.action}")


@dataclass(frozen=True)
class HumanDecision(Record):
    human_decision_id: str
    system_recommendation_id: str
    selected_action: str
    decision_status: str
    override_rationale: str | None

    def __post_init__(self) -> None:
        validate_id(self.human_decision_id, "human_decision")
        if self.decision_status not in {"accepted", "overridden", "rejected", "pending"}:
            raise ValueError(f"invalid human decision status: {self.decision_status}")
