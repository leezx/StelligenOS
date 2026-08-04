"""Architecture-level Gate contracts.

This module describes how an external Gate implementation is called. It does
not execute a Gate, persist an input envelope, or contain domain records.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final, Mapping, Protocol


GATE_GROUPS: Final[tuple[str, ...]] = (
    "target_opportunity",
    "product_realization",
    "commercial_executability",
)

_TARGET_GATES: Final[tuple[str, ...]] = (
    "clinical_context_endpoint",
    "endpoint_driving_population",
    "target_population_mapping",
    "intervention_causality",
    "baseline_coverage_and_escape",
    "treatment_induced_state_response",
    "net_endpoint_benefit",
    "tumor_cell_surface_availability",
    "intratumoral_antigen_accessibility",
    "antibody_dependent_internalization",
    "antibody_epitope_realizability",
    "on_target_therapeutic_index",
    "target_opportunity_decision",
)
_PRODUCT_GATES: Final[tuple[str, ...]] = (
    "product_design_objective",
    "epitope_landscape",
    "epitope_function",
    "binding_geometry_kinetics",
    "antibody_format_fc_design",
    "antibody_sequence_developability",
    "productive_internalization_trafficking",
    "conjugation_platform_site",
    "dar_molecular_property_balance",
    "payload_cell_state_match",
    "linker_release_match",
    "bystander_tumor_coverage",
    "integrated_pk_stability_exposure",
    "construct_therapeutic_index",
    "biomarker_clinical_assay_codesign",
    "integrated_adc_product_decision",
)
_COMMERCIAL_GATES: Final[tuple[str, ...]] = (
    "commercial_opportunity_threshold",
    "regulatory_development_path",
    "competitive_position_entry_window",
    "product_claim_decomposition",
    "patent_landscape",
    "preliminary_technical_fto",
    "blocking_claim_severity",
    "design_around_opportunity",
    "access_strategy",
    "fto_product_configuration",
    "own_ip_inventive_concept",
    "patentability_enablement",
    "claim_architecture_patent_estate",
    "disclosure_filing_strategy",
    "lifecycle_exclusivity_strategy",
    "transaction_readiness",
)

GATE_IDS: Final[tuple[str, ...]] = _TARGET_GATES + _PRODUCT_GATES + _COMMERCIAL_GATES


class ClinicalLockState(str, Enum):
    EXPLORATORY = "exploratory"
    PROVISIONAL = "provisional"
    ANCHORED = "anchored"
    PRODUCT_LOCKED = "product-locked"
    PROTOCOL_LOCKED = "protocol-locked"
    REGULATORY_LOCKED = "regulatory-locked"


def _require_external_ref(value: str | None, field_name: str) -> None:
    if value is not None and (not value.startswith("external:") or not value[9:]):
        raise ValueError(f"{field_name} must be an external reference")


@dataclass(frozen=True)
class GateDefinition:
    """Immutable identity and topology metadata for one Gate."""

    gate_id: str
    group: str
    sequence: int

    def __post_init__(self) -> None:
        if self.gate_id not in GATE_IDS:
            raise ValueError(f"Unknown Gate: {self.gate_id}")
        if self.group not in GATE_GROUPS:
            raise ValueError(f"Unknown Gate group: {self.group}")
        if self.sequence < 0 or self.sequence >= len(GATE_IDS):
            raise ValueError("Gate sequence is outside the frozen topology")


GATE_CATALOG: Final[tuple[GateDefinition, ...]] = tuple(
    GateDefinition(gate_id, group, sequence)
    for group, offset, gates in (
        ("target_opportunity", 0, _TARGET_GATES),
        ("product_realization", len(_TARGET_GATES), _PRODUCT_GATES),
        (
            "commercial_executability",
            len(_TARGET_GATES) + len(_PRODUCT_GATES),
            _COMMERCIAL_GATES,
        ),
    )
    for sequence, gate_id in enumerate(gates, start=offset)
)


@dataclass(frozen=True)
class GateInputEnvelope:
    """References and version metadata supplied by an external workspace."""

    candidate_ref: str
    target_opportunity_ref: str
    adc_product_candidate_ref: str
    commercial_execution_context_ref: str
    evidence_refs: tuple[str, ...]
    upstream_result_refs: Mapping[str, str]
    graph_context_ref: str
    run_context_ref: str
    # T0 is progressive: these refs do not imply a final label or endpoint.
    contract_version: str = "2.1.0"
    clinical_hypothesis_ref: str | None = None
    anchor_clinical_context_ref: str | None = None
    intended_benefit_ref: str | None = None
    biomarker_hypothesis_ref: str | None = None
    product_hypothesis_ref: str | None = None
    clinical_lock_state: ClinicalLockState | None = None

    def __post_init__(self) -> None:
        for name in (
            "clinical_hypothesis_ref", "anchor_clinical_context_ref",
            "intended_benefit_ref", "biomarker_hypothesis_ref",
            "product_hypothesis_ref",
        ):
            _require_external_ref(getattr(self, name), name)
        if self.clinical_lock_state is not None and not isinstance(self.clinical_lock_state, ClinicalLockState):
            raise ValueError("clinical_lock_state must be a ClinicalLockState")
        if self.clinical_lock_state is not None and self.clinical_hypothesis_ref is None:
            raise ValueError("clinical_lock_state requires clinical_hypothesis_ref")


@dataclass(frozen=True)
class GateModelOutput:
    """External Gate result envelope; values are never persisted here."""

    gate_id: str
    model_ref: str
    score: float | None
    confidence: float | None
    status: str
    rationale_ref: str | None
    evidence_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]
    recommended_validation_refs: tuple[str, ...]
    details_ref: str | None
    contract_version: str = "2.1.0"
    resulting_clinical_hypothesis_ref: str | None = None
    resulting_clinical_lock_state: ClinicalLockState | None = None

    def __post_init__(self) -> None:
        _require_external_ref(
            self.resulting_clinical_hypothesis_ref,
            "resulting_clinical_hypothesis_ref",
        )
        if (
            self.resulting_clinical_lock_state is not None
            and not isinstance(self.resulting_clinical_lock_state, ClinicalLockState)
        ):
            raise ValueError("resulting_clinical_lock_state must be a ClinicalLockState")
        if (
            self.resulting_clinical_lock_state is not None
            and self.resulting_clinical_hypothesis_ref is None
        ):
            raise ValueError(
                "resulting_clinical_lock_state requires resulting_clinical_hypothesis_ref"
            )


class ExternalGate(Protocol):
    """Port implemented by an external Gate runtime."""

    def evaluate(self, envelope: GateInputEnvelope) -> GateModelOutput:
        """Evaluate one envelope without creating repository state."""

        ...


def gate_definition(gate_id: str) -> GateDefinition:
    """Return frozen topology metadata for a Gate identifier."""

    for definition in GATE_CATALOG:
        if definition.gate_id == gate_id:
            return definition
    raise KeyError(gate_id)
