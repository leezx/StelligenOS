"""MOD-TGT04 -- primary Evidence Production Module for Gate TGT-04
(Tumor Surface Availability / Density Plausibility) under ADC_TARGET_GATESET@1.0 /
INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E12, strictly against the frozen PR E11 construction
contract (src/contracts/gate_modules/tgt04_tumor_surface_availability_density_plausibility.yaml).
The module owns Gate-specific deterministic interpretation only: normalized
upstream surface facts -> source / identity QC -> frozen Evidence-Ladder rung
mapping -> Gate-neutral EvidencePackages -> one typed SurfaceAvailabilityCompletion
(with the E6 / E8 / E10 completion-audit snapshot-parity gene, on BOTH the
qualifying-DIRECT and qualifying-INDIRECT surface-context sets) -> a proposed
Direction x Strength via the TGT-04 TWO-TIER / SINGLE-TIER grading authority (only
a qualifying DIRECT quantitative antigen-density observation grants a graded
Direction; a localization-only completed landscape is INCONCLUSIVE / UNKNOWN; the
legal pairs are exactly POSITIVE/DIRECT, NEGATIVE/DIRECT, CONFLICTING/DIRECT,
INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN) -> a machine-local fatal_review review
TRIGGER (Route A OR Route B reproducibility, CRC malignant-cell only) -> machine
acceptance -> one non-canonical assessment proposal envelope.

Three invariants:

* Surface localization is not antigen density. INDIRECT_STRONG localization
  evidence supports "the antigen is on the cell surface" but never a Gate-level
  proposed Strength.
* Quantitative values are evidence, not thresholds. A raw
  reported_density_value / unit / summary is an opaque factual string and a
  symmetric exact-reuse identity key -- never coerced to a number, never compared
  to any threshold / cutoff / invented range.
* A single quantitative NEGLIGIBLE_OR_UNDETECTABLE observation is a DIRECT-class
  OPPOSES observation, not yet a NEGATIVE / DIRECT proposal and not a
  reproducible fatal pattern; only a reproducible (Route A / Route B)
  quantitative NEGLIGIBLE_OR_UNDETECTABLE surface antigen on CRC malignant cells
  may surface POTENTIAL_FATAL_PATTERN; LOW_BUT_PRESENT is never fatal; the Module
  never decides fatality or ADC efficacy.

Live retrieval, extractors, normalizers, runners, persistence, and any GateSet
Decision / KILL are OUTSIDE this module (injected ports or downstream layers).
There is NO normalizer inside this package -- surface qualifications are given
upstream by the provider.
"""

from __future__ import annotations

from .completion import (
    SURFACE_UNRESOLVED_KIND_VALUES,
    SurfaceAvailabilityCompletion,
    SurfaceUnresolvedItem,
)
from .contracts import (
    CANONICAL_ONLY_FIELDS,
    CONTEXT_ADEQUACY_VALUES,
    DENSITY_IMPLICATION_VALUES,
    DENSITY_PLAUSIBILITY_BASIS_VALUES,
    DENSITY_PLAUSIBILITY_STATUS_VALUES,
    EVIDENCE_RUNG_VALUES,
    FATAL_REVIEW_STATUS_VALUES,
    GATE_ID,
    GATE_VERSION,
    GATESET_ID,
    GATESET_VERSION,
    INSTANTIATION_ID,
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    MALIGNANT_ATTRIBUTION_VALUES,
    MEASUREMENT_VALIDATION_STATUS_VALUES,
    MODULE_ID,
    MODULE_VERSION,
    MOLECULAR_LAYER_VALUES,
    OBSERVATION_KIND_VALUES,
    REPRODUCIBILITY_STATUS_VALUES,
    SURFACE_ANTIGEN_LEVEL_VALUES,
    SURFACE_CONTEXT_CLASS_VALUES,
    SURFACE_LOCALIZATION_STATUS_VALUES,
    TGT04_EVIDENCE_CEILING,
    TGT04_GATE_QUESTION,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClassifiedSurfaceObservation,
    EmittedEvidence,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedSurfaceObservation,
    Tgt04ModuleInput,
    Tgt04ModuleRunResult,
    density_implication,
)
from .module import run
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt04SurfaceAvailabilityProviderPort,
)

__all__ = [
    "MODULE_ID",
    "MODULE_VERSION",
    "GATE_ID",
    "GATE_VERSION",
    "GATESET_ID",
    "GATESET_VERSION",
    "INSTANTIATION_ID",
    "TGT04_EVIDENCE_CEILING",
    "TGT04_GATE_QUESTION",
    "OBSERVATION_KIND_VALUES",
    "MOLECULAR_LAYER_VALUES",
    "MEASUREMENT_VALIDATION_STATUS_VALUES",
    "SURFACE_CONTEXT_CLASS_VALUES",
    "CONTEXT_ADEQUACY_VALUES",
    "MALIGNANT_ATTRIBUTION_VALUES",
    "SURFACE_LOCALIZATION_STATUS_VALUES",
    "DENSITY_PLAUSIBILITY_STATUS_VALUES",
    "DENSITY_PLAUSIBILITY_BASIS_VALUES",
    "SURFACE_ANTIGEN_LEVEL_VALUES",
    "REPRODUCIBILITY_STATUS_VALUES",
    "EVIDENCE_RUNG_VALUES",
    "DENSITY_IMPLICATION_VALUES",
    "FATAL_REVIEW_STATUS_VALUES",
    "SURFACE_UNRESOLVED_KIND_VALUES",
    "LEGAL_DIRECTION_STRENGTH_PAIRS",
    "CANONICAL_ONLY_FIELDS",
    "CanonicalSourceRecord",
    "NormalizedSurfaceObservation",
    "SurfaceUnresolvedItem",
    "SurfaceAvailabilityCompletion",
    "Tgt04ModuleInput",
    "ClassifiedSurfaceObservation",
    "EmittedEvidence",
    "FatalReviewRecord",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "Tgt04ModuleRunResult",
    "density_implication",
    "Tgt04SurfaceAvailabilityProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceResolverPort",
    "ExistingEvidenceLibraryPort",
    "run",
]
