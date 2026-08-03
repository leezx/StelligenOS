"""External-only Phase 6 evidence sufficiency and adversarial review ports.

These contracts define policy evaluation, evidence-independence review, and
adversarial review boundaries. They do not read evidence, create review
records, execute Gates/T12, or persist ValidationTasks in StelligenOS.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .opportunity_generation import require_external_reference


class EvidenceReadiness(str, Enum):
    READY_FOR_T12_DECISION = "READY_FOR_T12_DECISION"
    HOLD = "HOLD"
    VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
    INELIGIBLE_FOR_T12 = "INELIGIBLE_FOR_T12"


class AdversarialReviewStatus(str, Enum):
    COMPLETE = "COMPLETE"
    REQUIRES_VALIDATION = "REQUIRES_VALIDATION"
    HOLD = "HOLD"


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        try:
            require_external_reference(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must contain external references") from exc


@dataclass(frozen=True)
class PositiveEvidencePolicy:
    """Configuration for readiness; thresholds are not hard-coded in logic."""

    policy_id: str
    required_gate_ids: tuple[str, ...]
    minimum_independent_source_groups: int
    maximum_critical_unknowns: int
    allow_model_only_support: bool = False
    allow_rule_only_support: bool = False

    def __post_init__(self) -> None:
        require_external_reference(self.policy_id)
        if not self.required_gate_ids:
            raise ValueError("required_gate_ids must be configured externally")
        if self.minimum_independent_source_groups < 1:
            raise ValueError("minimum_independent_source_groups must be positive")
        if self.maximum_critical_unknowns < 0:
            raise ValueError("maximum_critical_unknowns must not be negative")


@dataclass(frozen=True)
class EvidenceIndependenceCheckRequest:
    """References supplied to an external evidence independence checker."""

    request_id: str
    candidate_ref: str
    evidence_refs: tuple[str, ...]
    evidence_ledger_ref: str
    policy_ref: str
    run_context_ref: str

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "candidate_ref",
            "evidence_ledger_ref",
            "policy_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.evidence_refs, "evidence_refs")


@dataclass(frozen=True)
class EvidenceIndependenceCheckResult:
    """External independence assessment references."""

    request_id: str
    independence_report_ref: str
    independent_group_refs: tuple[str, ...]
    duplicate_or_dependent_evidence_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]
    run_ref: str

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        require_external_reference(self.independence_report_ref)
        require_external_reference(self.run_ref)
        for name in (
            "independent_group_refs",
            "duplicate_or_dependent_evidence_refs",
            "missing_information_refs",
        ):
            _require_external_refs(getattr(self, name), name)


@dataclass(frozen=True)
class AdversarialReviewRequest:
    """References for the independent pre-T12 adversarial review."""

    request_id: str
    candidate_ref: str
    t0_t11_trace_ref: str
    evidence_ledger_ref: str
    independence_report_ref: str
    review_scope_ref: str
    run_context_ref: str

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "candidate_ref",
            "t0_t11_trace_ref",
            "evidence_ledger_ref",
            "independence_report_ref",
            "review_scope_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))


@dataclass(frozen=True)
class AdversarialReviewResult:
    """External review outcome; it cannot overwrite Gate results."""

    request_id: str
    review_ref: str
    status: AdversarialReviewStatus
    objections_ref: str
    counter_evidence_refs: tuple[str, ...]
    validation_task_refs: tuple[str, ...]
    critical_unknown_refs: tuple[str, ...]
    run_ref: str

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        for name in (
            "review_ref",
            "objections_ref",
            "run_ref",
        ):
            require_external_reference(getattr(self, name))
        for name in (
            "counter_evidence_refs",
            "validation_task_refs",
            "critical_unknown_refs",
        ):
            _require_external_refs(getattr(self, name), name)


@dataclass(frozen=True)
class EvidenceReadinessRequest:
    """References required to form a pre-T12 readiness decision."""

    request_id: str
    candidate_ref: str
    positive_evidence_refs: tuple[str, ...]
    gate_trace_ref: str
    policy_ref: str
    independence_report_ref: str
    adversarial_review_ref: str
    validation_task_refs: tuple[str, ...]
    run_context_ref: str

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "candidate_ref",
            "gate_trace_ref",
            "policy_ref",
            "independence_report_ref",
            "adversarial_review_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.positive_evidence_refs, "positive_evidence_refs")
        _require_external_refs(self.validation_task_refs, "validation_task_refs")


@dataclass(frozen=True)
class EvidenceReadinessResult:
    """External readiness result; it does not execute T12 or create Opportunity."""

    request_id: str
    candidate_ref: str
    readiness: EvidenceReadiness
    policy_ref: str
    independence_report_ref: str
    adversarial_review_ref: str
    validation_task_refs: tuple[str, ...]
    unresolved_refs: tuple[str, ...]
    run_ref: str

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "candidate_ref",
            "policy_ref",
            "independence_report_ref",
            "adversarial_review_ref",
            "run_ref",
        ):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.validation_task_refs, "validation_task_refs")
        _require_external_refs(self.unresolved_refs, "unresolved_refs")
        if (
            self.readiness is EvidenceReadiness.READY_FOR_T12_DECISION
            and self.validation_task_refs
        ):
            raise ValueError("READY_FOR_T12_DECISION cannot retain validation tasks")


class EvidenceIndependencePort(Protocol):
    def check(
        self, request: EvidenceIndependenceCheckRequest
    ) -> EvidenceIndependenceCheckResult:
        """Check external evidence independence without local processing."""

        ...


class AdversarialReviewPort(Protocol):
    def review(self, request: AdversarialReviewRequest) -> AdversarialReviewResult:
        """Review external references without overwriting Gate results."""

        ...


class EvidenceReadinessPort(Protocol):
    def assess(self, request: EvidenceReadinessRequest) -> EvidenceReadinessResult:
        """Assess policy readiness without executing T12."""

        ...
