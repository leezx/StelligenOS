"""External-only Phase 5 endpoint biology completion port.

This module defines how an external runtime can complete T3-T6 and assemble a
full T0-T11 trace. It does not read evidence, execute Gates or Rules, create
records, run a P-chain, or persist results in StelligenOS.
"""

from dataclasses import dataclass
from typing import Protocol

from .gates import gate_definition
from .opportunity_generation import require_external_reference


T3_T6_GATE_IDS: tuple[str, ...] = (
    "intervention_causality",
    "baseline_coverage_and_escape",
    "treatment_induced_state_response",
    "net_endpoint_benefit",
)
T0_T11_TRACE_GATE_IDS: tuple[str, ...] = (
    "clinical_context_endpoint",
    "endpoint_driving_population",
    "target_population_mapping",
    *T3_T6_GATE_IDS,
    "tumor_cell_surface_availability",
    "intratumoral_antigen_accessibility",
    "antibody_dependent_internalization",
    "antibody_epitope_realizability",
    "on_target_therapeutic_index",
)


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        try:
            require_external_reference(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must contain external references") from exc


@dataclass(frozen=True)
class EndpointBiologyGateTrace:
    """External trace entry for one existing T0-T11 Gate result."""

    gate_id: str
    gate_result_ref: str
    model_ref: str
    historical_rule_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.gate_id not in T0_T11_TRACE_GATE_IDS:
            raise ValueError(f"Gate is outside the T0-T11 trace: {self.gate_id}")
        gate_definition(self.gate_id)
        for name in ("gate_result_ref", "model_ref"):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.historical_rule_refs, "historical_rule_refs")
        _require_external_refs(self.evidence_refs, "evidence_refs")
        _require_external_refs(
            self.missing_information_refs, "missing_information_refs"
        )


@dataclass(frozen=True)
class EndpointBiologyCompletionRequest:
    """External references required to complete endpoint biology."""

    request_id: str
    clinical_frame_ref: str
    target_candidate_refs: tuple[str, ...]
    upstream_t0_t2_refs: tuple[str, ...]
    early_reduction_trace_refs: tuple[str, ...]
    historical_adc_rule_refs: tuple[str, ...]
    gate_model_refs: tuple[str, ...]
    run_context_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "clinical_frame_ref",
            "run_context_ref",
        ):
            require_external_reference(getattr(self, name))
        for name in (
            "target_candidate_refs",
            "upstream_t0_t2_refs",
            "early_reduction_trace_refs",
            "historical_adc_rule_refs",
            "gate_model_refs",
        ):
            _require_external_refs(getattr(self, name), name)
        if not self.target_candidate_refs:
            raise ValueError("target_candidate_refs must not be empty")
        if not self.upstream_t0_t2_refs:
            raise ValueError("upstream_t0_t2_refs must preserve the prior trace")


@dataclass(frozen=True)
class EndpointBiologyCompletionResult:
    """External full T0-T11 trace, never a local Gate result collection."""

    request_id: str
    traces: tuple[EndpointBiologyGateTrace, ...]
    missing_information_refs: tuple[str, ...]
    run_ref: str
    full_trace_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        require_external_reference(self.request_id)
        require_external_reference(self.run_ref)
        require_external_reference(self.full_trace_ref)
        _require_external_refs(
            self.missing_information_refs, "missing_information_refs"
        )
        trace_gate_ids = tuple(trace.gate_id for trace in self.traces)
        if trace_gate_ids != T0_T11_TRACE_GATE_IDS:
            raise ValueError("traces must cover T0-T11 in frozen order")


class EndpointBiologyCompletionPort(Protocol):
    """Port implemented by an external T3-T6/Gate Model runtime."""

    def complete(
        self, request: EndpointBiologyCompletionRequest
    ) -> EndpointBiologyCompletionResult:
        """Assemble external T0-T11 trace without local execution or storage."""

        ...
