"""MOD-TGT02 -- primary Evidence Production Module for Gate TGT-02
(Indication-Specific Malignant-Cell Coverage) under ADC_TARGET_GATESET@1.0 /
INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E8, strictly against the frozen E7 construction
contract (src/contracts/gate_modules/tgt02_indication_specific_malignant_cell_coverage.yaml).
The module owns Gate-specific deterministic interpretation only: normalized
public coverage facts -> source / identity QC -> frozen Evidence-Ladder rung
mapping -> Gate-neutral EvidencePackages -> one typed CrcCohortCoverageCompletion
(with the E6 completion-audit snapshot-parity gene, hardened) -> a proposed
Direction x Strength strictly per the frozen E7 truth table (overall Strength is
the HIGHEST qualifying evidence class; NEGATIVE is reachable and a genuine
scientific finding; a WEAK-only public landscape is INCONCLUSIVE / UNKNOWN,
never INCONCLUSIVE / WEAK) -> a machine-local fatal_review review TRIGGER ->
machine acceptance -> one non-canonical assessment proposal envelope.

Three invariants:

* A single observation is never a Direction. Only aggregate, over a COMPLETED
  audited CRC coverage landscape, produces the proposed Direction x Strength.
* TGT-02 NEGATIVE is a Gate-relative SCIENTIFIC coverage judgement -- it is
  never a fatal flag and never a KILL. A cross-cohort protein-level
  negative-coverage pattern is surfaced at most as a fatal_review =
  POTENTIAL_FATAL_PATTERN.
* "rare and highly heterogeneous" is upstream-qualified -- the Module consumes
  it, never computes it from a percent-positive value, an H-score or a cohort n.

Live GEO / HPA / CPTAC / single-cell / spatial / TMA retrieval, extractors,
normalizers, runners, persistence, and any GateSet Decision / KILL are OUTSIDE
this module (injected ports or downstream layers).
"""

from __future__ import annotations

from .completion import (
    COVERAGE_UNRESOLVED_KIND_VALUES,
    CoverageUnresolvedItem,
    CrcCohortCoverageCompletion,
)
from .contracts import (
    ASSAY_METHOD_VALUES,
    CANONICAL_ONLY_FIELDS,
    COHORT_ADEQUACY_VALUES,
    COVERAGE_SUPPORT_VALUES,
    EVIDENCE_RUNG_VALUES,
    EXPRESSION_PATTERN_BASIS_VALUES,
    EXPRESSION_PATTERN_VALUES,
    FATAL_REVIEW_STATUS_VALUES,
    GATE_ID,
    GATE_VERSION,
    GATESET_ID,
    GATESET_VERSION,
    INSTANTIATION_ID,
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    MALIGNANT_ATTRIBUTION_VALUES,
    MODULE_ID,
    MODULE_VERSION,
    MOLECULAR_LAYER_VALUES,
    OBSERVATION_KIND_VALUES,
    TGT02_EVIDENCE_CEILING,
    TGT02_GATE_QUESTION,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClassifiedCoverage,
    EmittedEvidence,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedCoverageObservation,
    Tgt02ModuleInput,
    Tgt02ModuleRunResult,
    overall_strength,
)
from .module import run
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt02CoverageProviderPort,
)

__all__ = [
    "MODULE_ID",
    "MODULE_VERSION",
    "GATE_ID",
    "GATE_VERSION",
    "GATESET_ID",
    "GATESET_VERSION",
    "INSTANTIATION_ID",
    "TGT02_EVIDENCE_CEILING",
    "TGT02_GATE_QUESTION",
    "OBSERVATION_KIND_VALUES",
    "MOLECULAR_LAYER_VALUES",
    "ASSAY_METHOD_VALUES",
    "MALIGNANT_ATTRIBUTION_VALUES",
    "COHORT_ADEQUACY_VALUES",
    "EXPRESSION_PATTERN_VALUES",
    "EXPRESSION_PATTERN_BASIS_VALUES",
    "EVIDENCE_RUNG_VALUES",
    "COVERAGE_SUPPORT_VALUES",
    "FATAL_REVIEW_STATUS_VALUES",
    "COVERAGE_UNRESOLVED_KIND_VALUES",
    "LEGAL_DIRECTION_STRENGTH_PAIRS",
    "CANONICAL_ONLY_FIELDS",
    "CanonicalSourceRecord",
    "NormalizedCoverageObservation",
    "CoverageUnresolvedItem",
    "CrcCohortCoverageCompletion",
    "Tgt02ModuleInput",
    "ClassifiedCoverage",
    "EmittedEvidence",
    "FatalReviewRecord",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "Tgt02ModuleRunResult",
    "overall_strength",
    "Tgt02CoverageProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceResolverPort",
    "ExistingEvidenceLibraryPort",
    "run",
]
