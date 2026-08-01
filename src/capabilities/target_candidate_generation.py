"""External-only Phase 3 target candidate generation port.

This module defines the boundary for a future external generator. It does not
read evidence, execute a P-chain, create TargetCandidate records, or persist
results in StelligenOS.
"""

from dataclasses import dataclass
from typing import Protocol

from .opportunity_generation import require_external_reference


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        try:
            require_external_reference(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must contain external references") from exc


@dataclass(frozen=True)
class TargetCandidateGenerationPolicy:
    """Configuration for bounded generation, supplied by an external runtime."""

    maximum_candidates_per_clinical_frame: int
    minimum_distinct_positive_evidence_groups: int
    require_target_identity_resolution: bool = True
    require_relevant_tumor_context_evidence: bool = True
    permit_model_only_generation: bool = False
    permit_rule_only_generation: bool = False

    def __post_init__(self) -> None:
        if self.maximum_candidates_per_clinical_frame < 1:
            raise ValueError("maximum_candidates_per_clinical_frame must be positive")
        if self.minimum_distinct_positive_evidence_groups < 1:
            raise ValueError(
                "minimum_distinct_positive_evidence_groups must be positive"
            )
        if self.permit_model_only_generation or self.permit_rule_only_generation:
            raise ValueError("model-only and rule-only generation are disabled")


@dataclass(frozen=True)
class TargetCandidateGenerationRequest:
    """External references required to generate bounded target hypotheses."""

    request_id: str
    clinical_frame_ref: str
    evidence_scope_refs: tuple[str, ...]
    generation_policy_ref: str
    run_context_ref: str
    candidate_budget: int
    minimum_distinct_positive_evidence_groups: int
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "clinical_frame_ref",
            "generation_policy_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.evidence_scope_refs, "evidence_scope_refs")
        if self.candidate_budget < 1:
            raise ValueError("candidate_budget must be positive")
        if self.minimum_distinct_positive_evidence_groups < 1:
            raise ValueError(
                "minimum_distinct_positive_evidence_groups must be positive"
            )


@dataclass(frozen=True)
class TargetCandidateGenerationResult:
    """External references returned by a target candidate generator."""

    request_id: str
    target_candidate_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]
    run_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        require_external_reference(self.run_ref)
        _require_external_refs(self.target_candidate_refs, "target_candidate_refs")
        _require_external_refs(self.evidence_refs, "evidence_refs")
        _require_external_refs(
            self.missing_information_refs, "missing_information_refs"
        )


class TargetCandidateGenerationPort(Protocol):
    """Port implemented by an external target candidate generation runtime."""

    def generate(
        self, request: TargetCandidateGenerationRequest
    ) -> TargetCandidateGenerationResult:
        """Generate external candidate references without local side effects."""

        ...
