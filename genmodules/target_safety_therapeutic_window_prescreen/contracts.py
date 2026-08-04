"""Data-free contracts for target-level ADC safety pre-screening.

The module never reads evidence and never persists a record. Runtime evidence is
represented by external references so an execution service can resolve it from
``DATA`` or another approved workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Final


MODULE_VERSION: Final = "0.3.0"
CONTRACT_VERSION: Final = "0.3.0"
_EXTERNAL_REF = re.compile(r"^external:[^\s]+$")
_GENE_SYMBOL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")


def _external(value: str, label: str) -> None:
    if not isinstance(value, str) or _EXTERNAL_REF.fullmatch(value) is None:
        raise ValueError(f"{label} must use the external:<id> form")


class EvidenceAxis(StrEnum):
    NORMAL_TISSUE_EXPRESSION = "normal_tissue_expression"
    SURFACE_ACCESSIBILITY = "surface_accessibility"
    ANTIGEN_DENSITY = "antigen_density"
    SOLUBLE_SINK = "soluble_antigen_shedding_sink"
    EXISTING_MODALITY_TOXICITY = "existing_modality_toxicity"
    TISSUE_CONSEQUENCE = "tissue_consequence_recoverability"


class EvidenceLevel(StrEnum):
    A = "A"  # Human causal evidence.
    B = "B"  # Human tissue, protein-level, cell-resolved evidence.
    C = "C"  # Multi-omic concordance.
    D = "D"  # Single-source or indirect evidence.
    U = "U"  # Unknown.


class RiskDirection(StrEnum):
    SUPPORTS_SAFETY = "supports_safety"
    SUPPORTS_RISK = "supports_risk"
    CONFLICTING = "conflicting"
    UNKNOWN = "unknown"


class DifferentialStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    UNKNOWN = "unknown"
    NOT_ASSESSED = "not_assessed"


class Criticality(StrEnum):
    NON_CRITICAL = "non_critical"
    REGENERATIVE = "regenerative"
    CRITICAL_REVERSIBLE = "critical_reversible"
    CRITICAL_NON_REGENERATIVE = "critical_non_regenerative"
    UNKNOWN = "unknown"


class Decision(StrEnum):
    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    HOLD = "HOLD"
    KILL = "KILL"


class FatalFlag(StrEnum):
    CRITICAL_SURFACE_HAZARD = "critical_surface_hazard"
    CONFIRMED_ON_TARGET_TOXICITY = "confirmed_severe_on_target_toxicity"
    NORMAL_DENSITY_NOT_LOWER = "normal_density_not_lower_than_tumor"
    CLINICAL_SINK_EXPOSURE_FAILURE = "clinical_sink_exposure_failure"
    NO_EXPLOITABLE_DIFFERENTIAL = "no_exploitable_target_differential"


@dataclass(frozen=True)
class TargetProfile:
    """Target and proposed modality context; no sequence or evidence payload."""

    target_ref: str
    gene_symbol: str
    protein_name: str | None = None
    modality: str = "ADC"
    cancer_context_ref: str | None = None
    payload_class: str | None = None
    epitope_ref: str | None = None

    def __post_init__(self) -> None:
        _external(self.target_ref, "target_ref")
        if not _GENE_SYMBOL.fullmatch(self.gene_symbol):
            raise ValueError("gene_symbol must be a compact gene/protein symbol")
        if self.cancer_context_ref is not None:
            _external(self.cancer_context_ref, "cancer_context_ref")
        if self.epitope_ref is not None:
            _external(self.epitope_ref, "epitope_ref")
        if self.modality != "ADC":
            raise ValueError("this pre-screen currently supports modality=ADC only")


@dataclass(frozen=True)
class EvidenceClaim:
    """One externally stored observation or synthesis claim."""

    claim_ref: str
    axis: EvidenceAxis
    level: EvidenceLevel
    direction: RiskDirection
    source_ref: str
    rationale_ref: str
    tissue: str | None = None
    cell_type: str | None = None
    criticality: Criticality = Criticality.UNKNOWN
    surface_exposed: bool | None = None
    normal_density_relation: str | None = None
    differential_status: DifferentialStatus = DifferentialStatus.NOT_ASSESSED
    differential_assessment_ref: str | None = None
    hazard_context_ref: str | None = None
    mitigates_claim_refs: tuple[str, ...] = ()
    toxicity_attribution: str | None = None
    severe: bool = False
    clinically_demonstrated: bool = False
    unresolved: bool = False
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, label in (
            (self.claim_ref, "claim_ref"),
            (self.source_ref, "source_ref"),
            (self.rationale_ref, "rationale_ref"),
        ):
            _external(value, label)
        if self.normal_density_relation not in {None, "lower", "similar", "higher", "unknown"}:
            raise ValueError("normal_density_relation is invalid")
        if self.toxicity_attribution not in {
            None,
            "confirmed_on_target_on_tissue",
            "probable_on_target",
            "possible_on_target",
            "payload_class_effect",
            "linker_or_conjugation_effect",
            "immune_mechanism",
            "disease_related",
            "off_target",
            "unresolved",
        }:
            raise ValueError("toxicity_attribution is invalid")
        if not isinstance(self.differential_status, DifferentialStatus):
            raise ValueError("differential_status is invalid")
        for value, label in (
            (self.differential_assessment_ref, "differential_assessment_ref"),
            (self.hazard_context_ref, "hazard_context_ref"),
        ):
            if value is not None:
                _external(value, label)
        for value in self.mitigates_claim_refs:
            _external(value, "mitigates_claim_ref")
        if (
            self.differential_status == DifferentialStatus.ABSENT
            and self.differential_assessment_ref is None
        ):
            # A single observation cannot establish a cross-axis absence.
            object.__setattr__(self, "differential_status", DifferentialStatus.UNKNOWN)
        if self.direction == RiskDirection.UNKNOWN and not self.unresolved:
            object.__setattr__(self, "unresolved", True)


@dataclass(frozen=True)
class AssessmentRequest:
    """External runtime input for one target assessment."""

    request_ref: str
    target: TargetProfile
    evidence_refs: tuple[str, ...]
    claims: tuple[EvidenceClaim, ...]
    policy_ref: str
    run_context_ref: str

    def __post_init__(self) -> None:
        _external(self.request_ref, "request_ref")
        _external(self.policy_ref, "policy_ref")
        _external(self.run_context_ref, "run_context_ref")
        for evidence_ref in self.evidence_refs:
            _external(evidence_ref, "evidence_ref")
        claim_refs = {claim.claim_ref for claim in self.claims}
        if claim_refs - set(self.evidence_refs):
            raise ValueError("every claim_ref must be declared in evidence_refs")


@dataclass(frozen=True)
class AxisSummary:
    axis: EvidenceAxis
    claim_count: int
    highest_level: EvidenceLevel
    unresolved: bool
    risk_claim_count: int
    safety_claim_count: int
    conflict_claim_count: int


@dataclass(frozen=True)
class AssessmentResult:
    """Conservative, target-level output; not a product therapeutic-window claim."""

    contract_version: str
    request_ref: str
    target_ref: str
    axis_summaries: tuple[AxisSummary, ...]
    fatal_flags: tuple[FatalFlag, ...]
    unresolved_refs: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    material_risk_refs: tuple[str, ...]
    mitigation_refs: tuple[str, ...]
    next_experiment_refs: tuple[str, ...]
    decision: Decision
    confidence: str
    limitation_ref: str

    def __post_init__(self) -> None:
        if self.contract_version != CONTRACT_VERSION:
            raise ValueError("unsupported assessment result contract version")
        _external(self.request_ref, "request_ref")
        _external(self.target_ref, "target_ref")
        _external(self.limitation_ref, "limitation_ref")
        for ref in (
            *self.unresolved_refs,
            *self.conflict_refs,
            *self.material_risk_refs,
            *self.mitigation_refs,
            *self.next_experiment_refs,
        ):
            _external(ref, "result reference")
        if self.confidence not in {"high", "medium", "low"}:
            raise ValueError("confidence must be high, medium, or low")
