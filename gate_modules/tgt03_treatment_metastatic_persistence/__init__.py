"""MOD-TGT03 -- primary Evidence Production Module for Gate TGT-03
(Treatment / Metastatic Persistence) under ADC_TARGET_GATESET@1.0 /
INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E10, strictly against the frozen E9 construction
contract (src/contracts/gate_modules/tgt03_treatment_metastatic_persistence.yaml).
The module owns Gate-specific deterministic interpretation only: normalized
upstream persistence facts -> source / identity QC -> frozen Evidence-Ladder rung
mapping -> Gate-neutral EvidencePackages -> one typed
ClinicalPersistenceCompletion (with the E6 / E8 completion-audit
snapshot-parity gene) -> a proposed Direction x Strength strictly per the frozen
E9 truth table (overall Strength is the HIGHEST qualifying evidence class;
NEGATIVE is reachable and a genuine scientific finding; a WEAK-only public
landscape is INCONCLUSIVE / UNKNOWN, never INCONCLUSIVE / WEAK) -> a machine-local
fatal_review review TRIGGER (Route A OR Route B reproducibility) -> machine
acceptance -> one non-canonical assessment proposal envelope.

Three invariants:

* Baseline expression is not persistence. Only explicitly qualified
  treatment / metastasis-context evidence can drive TGT-03.
* A single observation is evidence, never a Direction; grading requires the
  completed and audited persistence landscape, and NEGATIVE remains a scientific
  persistence judgement -- not fatal and not KILL.
* Only reproducible DIRECT-class protein near / marked loss may surface
  POTENTIAL_FATAL_PATTERN; reproducibility is Route A or Route B, remains
  human-reviewable, and the Module never decides fatality.

Live retrieval, extractors, normalizers, runners, persistence, and any GateSet
Decision / KILL are OUTSIDE this module (injected ports or downstream layers).
There is NO normalizer inside this package -- persistence qualifications are
given upstream by the provider.
"""

from __future__ import annotations

from .completion import (
    PERSISTENCE_UNRESOLVED_KIND_VALUES,
    ClinicalPersistenceCompletion,
    PersistenceUnresolvedItem,
)
from .contracts import (
    CANONICAL_ONLY_FIELDS,
    CLINICAL_CONTEXT_VALUES,
    CONTEXT_ADEQUACY_VALUES,
    EVIDENCE_RUNG_VALUES,
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
    PERSISTENCE_IMPLICATION_VALUES,
    PERSISTENCE_PATTERN_BASIS_VALUES,
    PERSISTENCE_PATTERN_VALUES,
    PROTEIN_MEASUREMENT_VALIDATION_STATUS_VALUES,
    REPRODUCIBILITY_STATUS_VALUES,
    RESIDUAL_TARGET_PRESENCE_STATUS_VALUES,
    TGT03_EVIDENCE_CEILING,
    TGT03_GATE_QUESTION,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClassifiedPersistenceObservation,
    EmittedEvidence,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedPersistenceObservation,
    Tgt03ModuleInput,
    Tgt03ModuleRunResult,
    overall_strength,
    pattern_to_implication,
)
from .module import run
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt03PersistenceProviderPort,
)

__all__ = [
    "MODULE_ID",
    "MODULE_VERSION",
    "GATE_ID",
    "GATE_VERSION",
    "GATESET_ID",
    "GATESET_VERSION",
    "INSTANTIATION_ID",
    "TGT03_EVIDENCE_CEILING",
    "TGT03_GATE_QUESTION",
    "OBSERVATION_KIND_VALUES",
    "MOLECULAR_LAYER_VALUES",
    "PROTEIN_MEASUREMENT_VALIDATION_STATUS_VALUES",
    "CLINICAL_CONTEXT_VALUES",
    "CONTEXT_ADEQUACY_VALUES",
    "MALIGNANT_ATTRIBUTION_VALUES",
    "PERSISTENCE_PATTERN_VALUES",
    "PERSISTENCE_PATTERN_BASIS_VALUES",
    "RESIDUAL_TARGET_PRESENCE_STATUS_VALUES",
    "REPRODUCIBILITY_STATUS_VALUES",
    "EVIDENCE_RUNG_VALUES",
    "PERSISTENCE_IMPLICATION_VALUES",
    "FATAL_REVIEW_STATUS_VALUES",
    "PERSISTENCE_UNRESOLVED_KIND_VALUES",
    "LEGAL_DIRECTION_STRENGTH_PAIRS",
    "CANONICAL_ONLY_FIELDS",
    "CanonicalSourceRecord",
    "NormalizedPersistenceObservation",
    "PersistenceUnresolvedItem",
    "ClinicalPersistenceCompletion",
    "Tgt03ModuleInput",
    "ClassifiedPersistenceObservation",
    "EmittedEvidence",
    "FatalReviewRecord",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "Tgt03ModuleRunResult",
    "overall_strength",
    "pattern_to_implication",
    "Tgt03PersistenceProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceResolverPort",
    "ExistingEvidenceLibraryPort",
    "run",
]
