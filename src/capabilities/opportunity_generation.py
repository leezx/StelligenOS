"""External Opportunity Generation capability contract.

The capability accepts references to external knowledge and returns references
to externally managed hypotheses. It does not generate or persist records in
StelligenOS.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OpportunityGenerationRequest:
    """Versioned references required by an external generation implementation."""

    request_id: str
    knowledge_scope_ref: str
    target_context_ref: str
    clinical_context_ref: str
    generation_policy_ref: str
    run_context_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for reference in (
            self.request_id,
            self.knowledge_scope_ref,
            self.target_context_ref,
            self.clinical_context_ref,
            self.generation_policy_ref,
            self.run_context_ref,
        ):
            require_external_reference(reference)


@dataclass(frozen=True)
class OpportunityGenerationResult:
    """External result references, never an in-repository opportunity record."""

    request_id: str
    opportunity_refs: tuple[str, ...]
    target_hypothesis_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]
    run_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for reference in (
            *self.opportunity_refs,
            *self.target_hypothesis_refs,
            *self.evidence_refs,
            *self.missing_information_refs,
            self.run_ref,
        ):
            require_external_reference(reference)


class OpportunityGenerationPort(Protocol):
    """Port implemented by an external opportunity-generation runtime."""

    def generate(
        self, request: OpportunityGenerationRequest
    ) -> OpportunityGenerationResult:
        """Generate external references without mutating StelligenOS state."""

        ...


def require_external_reference(reference: str) -> str:
    """Reject local-looking references at the architecture boundary."""

    if not reference.startswith("external:"):
        raise ValueError("Opportunity Generation requires an external reference")
    return reference
