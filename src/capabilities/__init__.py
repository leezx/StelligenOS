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
from .binder_adc_routes import (
    BinderAdcRoutePort,
    BinderAdcRouteRequest,
    BinderAdcRouteResult,
    EPITOPE_DE_NOVO_ROUTE,
    EXISTING_BINDER_ROUTE,
    ROUTE_IDS,
    route_stages,
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
    "BinderAdcRoutePort",
    "BinderAdcRouteRequest",
    "BinderAdcRouteResult",
    "EPITOPE_DE_NOVO_ROUTE",
    "EXISTING_BINDER_ROUTE",
    "ROUTE_IDS",
    "route_stages",
]
