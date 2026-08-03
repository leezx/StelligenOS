"""External-only Phase 8 end-to-end pilot orchestration port.

This module defines the pilot boundary for a restricted external CRC
ClinicalFrame. It does not contain CRC data, run the lifecycle, create assets,
or persist pilot results in StelligenOS.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .opportunity_generation import require_external_reference


class PilotOutcome(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    NO_CANDIDATE_ADVANCED = "NO_CANDIDATE_ADVANCED"


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        try:
            require_external_reference(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must contain external references") from exc


@dataclass(frozen=True)
class EndToEndPilotRequest:
    """External references for one restricted pilot run."""

    request_id: str
    clinical_frame_ref: str
    external_data_bundle_ref: str
    candidate_generation_ref: str
    lifecycle_contract_refs: tuple[str, ...]
    stage_trace_refs: tuple[str, ...]
    candidate_refs: tuple[str, ...]
    selection_policy_ref: str
    pilot_run_context_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "clinical_frame_ref",
            "external_data_bundle_ref",
            "candidate_generation_ref",
            "selection_policy_ref",
            "pilot_run_context_ref",
        ):
            require_external_reference(getattr(self, name))
        for name in (
            "lifecycle_contract_refs",
            "stage_trace_refs",
            "candidate_refs",
        ):
            _require_external_refs(getattr(self, name), name)
        if not self.lifecycle_contract_refs:
            raise ValueError("lifecycle_contract_refs must be external")
        if not self.stage_trace_refs:
            raise ValueError("stage_trace_refs must preserve the pilot trace")
        if not self.candidate_refs:
            raise ValueError("candidate_refs must preserve all pilot candidates")


@dataclass(frozen=True)
class PilotCandidateOutcome:
    """External outcome envelope that does not privilege any named target."""

    candidate_ref: str
    disposition_ref: str
    decision_trace_ref: str

    def __post_init__(self) -> None:
        for name in ("candidate_ref", "disposition_ref", "decision_trace_ref"):
            require_external_reference(getattr(self, name))


@dataclass(frozen=True)
class EndToEndPilotResult:
    """External pilot result with explicit no-advance semantics."""

    request_id: str
    outcome: PilotOutcome
    candidate_outcomes: tuple[PilotCandidateOutcome, ...]
    selected_candidate_refs: tuple[str, ...]
    held_candidate_refs: tuple[str, ...]
    rejected_candidate_refs: tuple[str, ...]
    pilot_trace_ref: str
    pilot_run_ref: str
    asset_generation_enabled: bool = False

    def __post_init__(self) -> None:
        for name in ("request_id", "pilot_trace_ref", "pilot_run_ref"):
            require_external_reference(getattr(self, name))
        for name in (
            "selected_candidate_refs",
            "held_candidate_refs",
            "rejected_candidate_refs",
        ):
            _require_external_refs(getattr(self, name), name)
        if not self.candidate_outcomes:
            raise ValueError("candidate_outcomes must preserve every candidate")
        if self.asset_generation_enabled:
            raise ValueError("Phase 8 pilot cannot enable asset generation")


class EndToEndPilotPort(Protocol):
    def run(self, request: EndToEndPilotRequest) -> EndToEndPilotResult:
        """Run the restricted pilot externally without repository side effects."""

        ...
