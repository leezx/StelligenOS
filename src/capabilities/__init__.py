"""Capability contracts exposed by StelligenOS."""

from .gates import (
    GATE_CATALOG,
    GATE_GROUPS,
    GATE_IDS,
    ExternalGate,
    GateDefinition,
    GateInputEnvelope,
    GateModelOutput,
    gate_definition,
)
from .opportunity_generation import (
    OpportunityGenerationPort,
    OpportunityGenerationRequest,
    OpportunityGenerationResult,
    require_external_reference,
)

__all__ = [
    "GATE_CATALOG",
    "GATE_GROUPS",
    "GATE_IDS",
    "ExternalGate",
    "GateDefinition",
    "GateInputEnvelope",
    "GateModelOutput",
    "gate_definition",
    "OpportunityGenerationPort",
    "OpportunityGenerationRequest",
    "OpportunityGenerationResult",
    "require_external_reference",
]
