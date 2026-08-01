"""External-only Phase 7 T12 decision and opportunity ranking ports.

The repository defines the integration boundary only. It does not execute
T12, rank candidates, create Opportunity records, or persist handoffs.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .opportunity_generation import require_external_reference


class T12DecisionDisposition(str, Enum):
    PROVISIONAL_ADVANCE = "PROVISIONAL_ADVANCE"
    EXPLORATION = "EXPLORATION"
    HOLD = "HOLD"
    FAIL = "FAIL"


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        try:
            require_external_reference(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must contain external references") from exc


@dataclass(frozen=True)
class T12DecisionRequest:
    """External inputs for the formal T12 integrator."""

    request_id: str
    candidate_ref: str
    readiness_ref: str
    t0_t11_trace_ref: str
    decision_policy_ref: str
    run_context_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "candidate_ref",
            "readiness_ref",
            "t0_t11_trace_ref",
            "decision_policy_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))


@dataclass(frozen=True)
class OpportunityHandoffPackage:
    """External handoff references; asset generation remains disabled."""

    opportunity_ref: str
    decision_ref: str
    rationale_ref: str
    required_next_evidence_refs: tuple[str, ...]
    cheapest_decisive_experiment_ref: str
    eligible_for_asset_generation: bool = False

    def __post_init__(self) -> None:
        for name in (
            "opportunity_ref",
            "decision_ref",
            "rationale_ref",
            "cheapest_decisive_experiment_ref",
        ):
            require_external_reference(getattr(self, name))
        _require_external_refs(
            self.required_next_evidence_refs, "required_next_evidence_refs"
        )
        if self.eligible_for_asset_generation:
            raise ValueError("asset generation remains disabled in Phase 7")


@dataclass(frozen=True)
class T12DecisionResult:
    """External T12 result and handoff package, never a local Opportunity."""

    request_id: str
    disposition: T12DecisionDisposition
    t12_result_ref: str
    hard_failure_refs: tuple[str, ...]
    unresolved_refs: tuple[str, ...]
    handoff: OpportunityHandoffPackage
    run_ref: str

    def __post_init__(self) -> None:
        for name in ("request_id", "t12_result_ref", "run_ref"):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.hard_failure_refs, "hard_failure_refs")
        _require_external_refs(self.unresolved_refs, "unresolved_refs")


@dataclass(frozen=True)
class OpportunityRankingRequest:
    """External T12 decisions supplied to the non-Gate ranking stage."""

    request_id: str
    eligible_decision_refs: tuple[str, ...]
    excluded_decision_refs: tuple[str, ...]
    ranking_policy_ref: str
    run_context_ref: str

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        require_external_reference(self.ranking_policy_ref)
        require_external_reference(self.run_context_ref)
        _require_external_refs(self.eligible_decision_refs, "eligible_decision_refs")
        _require_external_refs(self.excluded_decision_refs, "excluded_decision_refs")
        if not self.eligible_decision_refs:
            raise ValueError("eligible_decision_refs must not be empty")


@dataclass(frozen=True)
class OpportunityRankingResult:
    """External ranking references that cannot override T12 or Hard Gate state."""

    request_id: str
    ranked_opportunity_refs: tuple[str, ...]
    held_opportunity_refs: tuple[str, ...]
    rejected_opportunity_refs: tuple[str, ...]
    ranking_trace_ref: str
    run_ref: str

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        require_external_reference(self.ranking_trace_ref)
        require_external_reference(self.run_ref)
        for name in (
            "ranked_opportunity_refs",
            "held_opportunity_refs",
            "rejected_opportunity_refs",
        ):
            _require_external_refs(getattr(self, name), name)


class T12DecisionPort(Protocol):
    def decide(self, request: T12DecisionRequest) -> T12DecisionResult:
        """Run T12 externally without local decision or Opportunity state."""

        ...


class OpportunityRankingPort(Protocol):
    def rank(self, request: OpportunityRankingRequest) -> OpportunityRankingResult:
        """Rank external decision references without changing Gate semantics."""

        ...
