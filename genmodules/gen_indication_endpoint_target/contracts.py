"""Pure contracts for the ``gen_indication_endpoint_target`` module.

Instances are in-memory contract values. They are not records, database
models, evidence stores, or executable Gate/Rule/Model evaluators.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final


EXTERNAL_PREFIX: Final[str] = "external:"


def _require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _require_external(value: str, field_name: str) -> str:
    _require_non_empty(value, field_name)
    if not value.startswith(EXTERNAL_PREFIX):
        raise ValueError(f"{field_name} must be an external reference")
    return value


def _require_ids(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        _require_non_empty(value, field_name)


class EvaluationStatus(str, Enum):
    """Status values that preserve unknown or unevaluated domains."""

    EVALUATED = "EVALUATED"
    NOT_EVALUATED = "NOT_EVALUATED"
    UNRESOLVED = "UNRESOLVED"


class CandidateDisposition(str, Enum):
    """Early filter disposition; this enum is explicitly not a Gate result."""

    RETAIN = "RETAIN"
    EXCLUDE = "EXCLUDE"
    DEFER = "DEFER"


class EvidenceDirection(str, Enum):
    SUPPORTS = "SUPPORTS"
    OPPOSES = "OPPOSES"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class ReviewStatus(str, Enum):
    UNREVIEWED = "UNREVIEWED"
    REVIEWED = "REVIEWED"
    DISPUTED = "DISPUTED"


class CandidateLifecycle(str, Enum):
    SCOPE_DEFINED = "SCOPE_DEFINED"
    CLINICAL_FRAME_GENERATED = "CLINICAL_FRAME_GENERATED"
    CLINICAL_FRAME_RETAINED = "CLINICAL_FRAME_RETAINED"
    TARGET_CANDIDATE_GENERATED = "TARGET_CANDIDATE_GENERATED"
    UNDER_T_GATE_EVALUATION = "UNDER_T_GATE_EVALUATION"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    CONDITIONALLY_RETAINED = "CONDITIONALLY_RETAINED"
    REJECTED = "REJECTED"
    READY_FOR_ADVERSARIAL_REVIEW = "READY_FOR_ADVERSARIAL_REVIEW"
    READY_FOR_T12_DECISION = "READY_FOR_T12_DECISION"
    OPPORTUNITY_RETAINED = "OPPORTUNITY_RETAINED"
    OPPORTUNITY_ON_HOLD = "OPPORTUNITY_ON_HOLD"
    OPPORTUNITY_REJECTED = "OPPORTUNITY_REJECTED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class OpportunitySearchScope:
    """The immutable search boundary supplied by an external workspace."""

    scope_id: str
    version: str
    indication: str
    disease_setting: str
    line_of_therapy: str
    treatment_context: str
    comparator: str
    patient_segment_constraints: tuple[str, ...]
    endpoint_definition: str
    endpoint_time_horizon: str
    clinical_success_condition: str
    modality: str
    evidence_cutoff_date: str
    candidate_budget: int
    source_policy_id: str
    evaluation_plan_id: str

    def __post_init__(self) -> None:
        for name in (
            "scope_id",
            "version",
            "indication",
            "disease_setting",
            "line_of_therapy",
            "treatment_context",
            "comparator",
            "endpoint_definition",
            "endpoint_time_horizon",
            "clinical_success_condition",
            "modality",
            "evidence_cutoff_date",
            "source_policy_id",
            "evaluation_plan_id",
        ):
            _require_non_empty(getattr(self, name), name)
        _require_ids(self.patient_segment_constraints, "patient_segment_constraints")
        if self.modality != "ADC":
            raise ValueError("gen_indication_endpoint_target requires modality=ADC")
        if self.candidate_budget < 1:
            raise ValueError("candidate_budget must be positive")


@dataclass(frozen=True)
class ClinicalFrame:
    """A constrained clinical frame produced by T0/T1 work."""

    frame_id: str
    scope_id: str
    indication: str
    disease_setting: str
    line_of_therapy: str
    treatment_context: str
    comparator: str
    endpoint_definition: str
    endpoint_time_horizon: str
    endpoint_driving_population: str
    source_evidence_ids: tuple[str, ...]
    t0_gate_result_ref: str
    t1_gate_result_ref: str
    status: EvaluationStatus = EvaluationStatus.EVALUATED

    def __post_init__(self) -> None:
        for name in (
            "frame_id",
            "scope_id",
            "indication",
            "disease_setting",
            "line_of_therapy",
            "treatment_context",
            "comparator",
            "endpoint_definition",
            "endpoint_time_horizon",
            "endpoint_driving_population",
        ):
            _require_non_empty(getattr(self, name), name)
        _require_ids(self.source_evidence_ids, "source_evidence_ids")
        _require_external(self.t0_gate_result_ref, "t0_gate_result_ref")
        _require_external(self.t1_gate_result_ref, "t1_gate_result_ref")


@dataclass(frozen=True)
class TargetCandidate:
    """A target hypothesis candidate with an auditable clinical identity."""

    candidate_id: str
    clinical_frame_id: str
    indication: str
    patient_population: str
    clinical_endpoint: str
    adc_target: str
    disease_setting: str
    line_of_therapy: str
    treatment_context: str
    comparator: str
    endpoint_time_horizon: str
    biological_hypothesis: str
    adc_hypothesis: str
    generation_method: str
    source_run_ref: str
    positive_evidence_ids: tuple[str, ...] = ()
    negative_evidence_ids: tuple[str, ...] = ()
    unknown_claims: tuple[str, ...] = ()
    lifecycle: CandidateLifecycle = CandidateLifecycle.TARGET_CANDIDATE_GENERATED

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "clinical_frame_id",
            "indication",
            "patient_population",
            "clinical_endpoint",
            "adc_target",
            "disease_setting",
            "line_of_therapy",
            "treatment_context",
            "comparator",
            "endpoint_time_horizon",
            "biological_hypothesis",
            "adc_hypothesis",
            "generation_method",
        ):
            _require_non_empty(getattr(self, name), name)
        _require_external(self.source_run_ref, "source_run_ref")
        _require_ids(self.positive_evidence_ids, "positive_evidence_ids")
        _require_ids(self.negative_evidence_ids, "negative_evidence_ids")
        _require_ids(self.unknown_claims, "unknown_claims")

    @property
    def opportunity_identity(self) -> tuple[str, str, str, str]:
        """Return the required indication/population/endpoint/target identity."""

        return (
            self.indication,
            self.patient_population,
            self.clinical_endpoint,
            self.adc_target,
        )


@dataclass(frozen=True)
class CandidateFilterResult:
    """Non-Gate early filtering result that preserves insufficient evidence."""

    filter_id: str
    candidate_id: str
    disposition: CandidateDisposition
    status: EvaluationStatus
    reason_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    filter_policy_ref: str = ""

    def __post_init__(self) -> None:
        for name in ("filter_id", "candidate_id"):
            _require_non_empty(getattr(self, name), name)
        _require_ids(self.reason_codes, "reason_codes")
        _require_ids(self.evidence_ids, "evidence_ids")
        if self.filter_policy_ref:
            _require_external(self.filter_policy_ref, "filter_policy_ref")


@dataclass(frozen=True)
class EvidenceRecord:
    """Minimum provenance contract for an externally managed evidence claim."""

    evidence_id: str
    claim_id: str
    candidate_id: str
    clinical_frame_id: str
    gate_id: str
    rule_id: str
    model_id: str
    evidence_type: str
    direction: EvidenceDirection
    source_type: str
    source_reference: str
    source_date: str
    access_date: str
    extraction_method: str
    raw_observation: str
    normalized_claim: str
    confidence: float
    limitations: tuple[str, ...]
    independence_group: str
    review_status: ReviewStatus

    def __post_init__(self) -> None:
        for name in (
            "evidence_id",
            "claim_id",
            "candidate_id",
            "clinical_frame_id",
            "gate_id",
            "rule_id",
            "model_id",
            "evidence_type",
            "source_type",
            "source_date",
            "access_date",
            "extraction_method",
            "raw_observation",
            "normalized_claim",
            "independence_group",
        ):
            _require_non_empty(getattr(self, name), name)
        _require_external(self.source_reference, "source_reference")
        _require_ids(self.limitations, "limitations")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class AdversarialReview:
    """Review record; it is not a Gate and cannot create a Gate result."""

    review_id: str
    candidate_id: str
    objections: tuple[str, ...]
    counter_evidence_ids: tuple[str, ...]
    alternative_explanations: tuple[str, ...]
    critical_unknowns: tuple[str, ...]
    validation_tasks: tuple[str, ...]
    reviewer_ref: str
    status: EvaluationStatus

    def __post_init__(self) -> None:
        _require_non_empty(self.review_id, "review_id")
        _require_non_empty(self.candidate_id, "candidate_id")
        _require_ids(self.objections, "objections")
        _require_ids(self.counter_evidence_ids, "counter_evidence_ids")
        _require_ids(self.alternative_explanations, "alternative_explanations")
        _require_ids(self.critical_unknowns, "critical_unknowns")
        _require_ids(self.validation_tasks, "validation_tasks")
        _require_external(self.reviewer_ref, "reviewer_ref")


@dataclass(frozen=True)
class TargetOpportunityHandoff:
    """T12 handoff contract that returns references, never local records."""

    handoff_id: str
    candidate_id: str
    opportunity_ref: str
    target_hypothesis_ref: str
    t12_gate_result_ref: str
    evidence_refs: tuple[str, ...]
    adversarial_review_ref: str
    lifecycle: CandidateLifecycle
    readiness: EvaluationStatus

    def __post_init__(self) -> None:
        _require_non_empty(self.handoff_id, "handoff_id")
        _require_non_empty(self.candidate_id, "candidate_id")
        for name in (
            "opportunity_ref",
            "target_hypothesis_ref",
            "t12_gate_result_ref",
            "adversarial_review_ref",
        ):
            _require_external(getattr(self, name), name)
        _require_ids(self.evidence_refs, "evidence_refs")

