"""External-only Phase 4 early T-Gate candidate reduction port.

This module defines scheduling and decision envelopes only. It does not
evaluate Gates, read evidence, create candidate records, run T12, or persist
results in StelligenOS.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .gates import gate_definition
from .opportunity_generation import require_external_reference


EARLY_REDUCTION_GATE_IDS: tuple[str, ...] = (
    "target_population_mapping",
    "tumor_cell_surface_availability",
    "intratumoral_antigen_accessibility",
    "antibody_dependent_internalization",
    "antibody_epitope_realizability",
    "on_target_therapeutic_index",
)
PRIORITY_GATE_IDS: tuple[str, ...] = EARLY_REDUCTION_GATE_IDS[:2]


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        try:
            require_external_reference(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must contain external references") from exc


class EarlyReductionDisposition(str, Enum):
    """Early reduction states; absence of evidence is represented by HOLD."""

    PROVISIONAL_ADVANCE = "PROVISIONAL_ADVANCE"
    HOLD = "HOLD"
    EXCLUDE = "EXCLUDE"


@dataclass(frozen=True)
class EarlyReductionSchedule:
    """Existing target Gates scheduled without creating a new Gate."""

    gate_ids: tuple[str, ...] = PRIORITY_GATE_IDS
    allow_dependent_gate_progression: bool = True

    def __post_init__(self) -> None:
        if not self.gate_ids:
            raise ValueError("gate_ids must not be empty")
        if self.gate_ids[:2] != PRIORITY_GATE_IDS:
            raise ValueError("T2 and T7 priority Gates must be scheduled first")
        for gate_id in self.gate_ids:
            if gate_id not in EARLY_REDUCTION_GATE_IDS:
                raise ValueError(f"Gate is outside the Phase 4 schedule: {gate_id}")
            gate_definition(gate_id)
        if "target_opportunity_decision" in self.gate_ids:
            raise ValueError("Phase 4 must not schedule T12")


@dataclass(frozen=True)
class CandidateReductionDecision:
    """External decision envelope preserving HOLD and exclusion reasons."""

    candidate_ref: str
    disposition: EarlyReductionDisposition
    reason_codes: tuple[str, ...]
    gate_result_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        require_external_reference(self.candidate_ref)
        _require_external_refs(self.gate_result_refs, "gate_result_refs")
        _require_external_refs(self.evidence_refs, "evidence_refs")
        _require_external_refs(
            self.missing_information_refs, "missing_information_refs"
        )
        if not self.reason_codes:
            raise ValueError("reason_codes must preserve the reduction rationale")
        if (
            self.disposition is EarlyReductionDisposition.HOLD
            and not self.missing_information_refs
            and not self.evidence_refs
        ):
            raise ValueError("HOLD must identify missing information or evidence")


@dataclass(frozen=True)
class EarlyTGateReductionRequest:
    """References required for external early T-Gate reduction."""

    request_id: str
    clinical_frame_ref: str
    target_candidate_refs: tuple[str, ...]
    schedule: EarlyReductionSchedule
    gate_input_scope_ref: str
    run_context_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "clinical_frame_ref",
            "gate_input_scope_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.target_candidate_refs, "target_candidate_refs")
        if not self.target_candidate_refs:
            raise ValueError("target_candidate_refs must not be empty")


@dataclass(frozen=True)
class EarlyTGateReductionResult:
    """External reduction decisions; no local candidate or Gate records."""

    request_id: str
    decisions: tuple[CandidateReductionDecision, ...]
    run_ref: str
    trace_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        require_external_reference(self.run_ref)
        require_external_reference(self.trace_ref)
        if not self.decisions:
            raise ValueError("decisions must preserve every candidate outcome")


class EarlyTGateReductionPort(Protocol):
    """Port implemented by an external early T-Gate reduction runtime."""

    def reduce(
        self, request: EarlyTGateReductionRequest
    ) -> EarlyTGateReductionResult:
        """Reduce external candidates without local Gate execution or storage."""

        ...
