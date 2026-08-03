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
from .registry import CAPABILITY_IDS, CAPABILITY_NAMES
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
    "CAPABILITY_IDS",
    "CAPABILITY_NAMES",
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
