"""External cross-cutting contracts for IP/FTO, due diligence, and portfolio.

These ports coordinate references to external evidence and decisions. They do
not provide legal analysis, diligence records, portfolio storage, or capital
allocation logic.
"""

from dataclasses import dataclass
from typing import Final, Protocol


DUE_DILIGENCE_STAGES: Final[tuple[str, ...]] = (
    "opportunity_generation",
    "opportunity_validation",
    "asset_generation",
    "asset_development",
)


@dataclass(frozen=True)
class IPFTORequest:
    asset_ref: str
    jurisdiction_scope_ref: str
    claim_scope_ref: str
    evidence_scope_ref: str
    run_context_ref: str

    def __post_init__(self) -> None:
        _require_external(self.asset_ref, self.jurisdiction_scope_ref,
                          self.claim_scope_ref, self.evidence_scope_ref,
                          self.run_context_ref)


@dataclass(frozen=True)
class DueDiligenceRequest:
    asset_ref: str
    lifecycle_stage: str
    question_set_ref: str
    evidence_scope_ref: str
    run_context_ref: str

    def __post_init__(self) -> None:
        if self.lifecycle_stage not in DUE_DILIGENCE_STAGES:
            raise ValueError("Unknown lifecycle stage for due diligence")
        _require_external(self.asset_ref, self.question_set_ref,
                          self.evidence_scope_ref, self.run_context_ref)


@dataclass(frozen=True)
class PortfolioRequest:
    asset_refs: tuple[str, ...]
    decision_policy_ref: str
    capital_context_ref: str
    risk_context_ref: str
    run_context_ref: str

    def __post_init__(self) -> None:
        _require_external(*self.asset_refs, self.decision_policy_ref,
                          self.capital_context_ref, self.risk_context_ref,
                          self.run_context_ref)


@dataclass(frozen=True)
class ExternalDecisionPackage:
    decision_ref: str
    evidence_refs: tuple[str, ...]
    unresolved_risk_refs: tuple[str, ...]
    next_action_ref: str

    def __post_init__(self) -> None:
        _require_external(self.decision_ref, *self.evidence_refs,
                          *self.unresolved_risk_refs, self.next_action_ref)


class IPFTOPort(Protocol):
    def assess(self, request: IPFTORequest) -> ExternalDecisionPackage:
        """Assess externally without storing legal or FTO conclusions here."""

        ...


class DueDiligencePort(Protocol):
    def assess(self, request: DueDiligenceRequest) -> ExternalDecisionPackage:
        """Assess externally using a stage-specific question set."""

        ...


class PortfolioPort(Protocol):
    def assess(self, request: PortfolioRequest) -> ExternalDecisionPackage:
        """Assess externally without storing portfolio or capital decisions."""

        ...


def _require_external(*references: str) -> None:
    if any(not reference.startswith("external:") for reference in references):
        raise ValueError("Cross-cutting services require external references")
