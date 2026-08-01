"""External-only Phase 2 T0-T1 clinical frame pipeline port.

This module defines the call boundary. It does not read clinical unmet need
data, execute Gates, create ClinicalFrame records, or persist results.
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
class ClinicalFramePipelineRequest:
    """External references required to call the T0-T1 pipeline."""

    request_id: str
    search_scope_ref: str
    clinical_unmet_need_ref: str
    t0_input_ref: str
    t1_input_ref: str
    generation_policy_ref: str
    run_context_ref: str
    candidate_budget: int
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "search_scope_ref",
            "clinical_unmet_need_ref",
            "t0_input_ref",
            "t1_input_ref",
            "generation_policy_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))
        if self.candidate_budget < 1:
            raise ValueError("candidate_budget must be positive")


@dataclass(frozen=True)
class ClinicalFramePipelineResult:
    """External references returned by a T0-T1 pipeline implementation."""

    request_id: str
    clinical_frame_refs: tuple[str, ...]
    t0_result_ref: str
    t1_result_ref: str
    evidence_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]
    run_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        require_external_reference(self.t0_result_ref)
        require_external_reference(self.t1_result_ref)
        require_external_reference(self.run_ref)
        _require_external_refs(self.clinical_frame_refs, "clinical_frame_refs")
        _require_external_refs(self.evidence_refs, "evidence_refs")
        _require_external_refs(
            self.missing_information_refs, "missing_information_refs"
        )


class ClinicalFramePipelinePort(Protocol):
    """Port implemented by an external clinical frame runtime."""

    def run(self, request: ClinicalFramePipelineRequest) -> ClinicalFramePipelineResult:
        """Call external unmet-need, T0, and T1 processing."""

        ...

