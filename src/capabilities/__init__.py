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

__all__ = [
    "GATE_CATALOG",
    "GATE_GROUPS",
    "GATE_IDS",
    "ExternalGate",
    "GateDefinition",
    "GateInputEnvelope",
    "GateModelOutput",
    "gate_definition",
]
