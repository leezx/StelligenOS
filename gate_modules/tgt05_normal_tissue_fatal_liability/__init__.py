"""MOD-TGT05 -- primary Evidence Production Module for Gate TGT-05
(Normal-Tissue Fatal Liability) under ADC_TARGET_GATESET@1.0 /
INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E4, strictly against the frozen E3 construction
contract (src/contracts/gate_modules/tgt05_normal_tissue_fatal_liability.yaml).
The module owns Gate-specific deterministic interpretation only: normalized
TGT-05 observations -> source / identity QC -> frozen Evidence-Ladder mapping ->
Gate-neutral EvidencePackages -> vital-organ coverage state -> Direction x
Strength -> a machine-local ``fatal_review`` review TRIGGER -> stop-rule
acceptance -> one non-canonical assessment proposal envelope.

Web / atlas / clinical retrieval, the source registry, the reusable Evidence
Library, persistence, human target-attribution adjudication, the human
materially-distinct / truly-target-mediated judgement, the fatal decision,
CandidateGateAssessment approval, GateSet Decision / KILL and any
therapeutic-window prediction are all OUTSIDE this module (injected ports or
downstream layers).

TGT-05 is a ONE-WAY normal-tissue liability detector: absence of risk evidence
is never NEGATIVE / safe, and ``fatal_review`` is a machine-generated review
trigger, never a machine-generated fatal conclusion.
"""

from __future__ import annotations

from .contracts import (
    CANONICAL_ONLY_FIELDS,
    COVERAGE_RESULT_VALUES,
    EVIDENCE_FUNCTION_VALUES,
    FATAL_REVIEW_STATUS_VALUES,
    GATE_ID,
    GATE_VERSION,
    GATESET_ID,
    GATESET_VERSION,
    INSTANTIATION_ID,
    MODULE_ID,
    MODULE_VERSION,
    OBSERVATION_KIND_VALUES,
    TGT05_EVIDENCE_CEILING,
    TGT05_GATE_QUESTION,
    VITAL_ORGAN_CLASSES,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClassifiedLiability,
    CoverageMapRecord,
    EmittedEvidence,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedLiabilityRecord,
    Tgt05ModuleInput,
    Tgt05ModuleRunResult,
    Tgt05SweepCompletionRecord,
    VitalOrganCoverageState,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt05LiabilityProviderPort,
)
from .module import run

__all__ = [
    "MODULE_ID",
    "MODULE_VERSION",
    "GATE_ID",
    "GATE_VERSION",
    "GATESET_ID",
    "GATESET_VERSION",
    "INSTANTIATION_ID",
    "TGT05_EVIDENCE_CEILING",
    "TGT05_GATE_QUESTION",
    "EVIDENCE_FUNCTION_VALUES",
    "OBSERVATION_KIND_VALUES",
    "COVERAGE_RESULT_VALUES",
    "FATAL_REVIEW_STATUS_VALUES",
    "VITAL_ORGAN_CLASSES",
    "CANONICAL_ONLY_FIELDS",
    "NormalizedLiabilityRecord",
    "CanonicalSourceRecord",
    "Tgt05ModuleInput",
    "ClassifiedLiability",
    "EmittedEvidence",
    "VitalOrganCoverageState",
    "Tgt05SweepCompletionRecord",
    "CoverageMapRecord",
    "FatalReviewRecord",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "Tgt05ModuleRunResult",
    "Tgt05LiabilityProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceResolverPort",
    "ExistingEvidenceLibraryPort",
    "run",
]
