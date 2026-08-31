"""MOD-TGT06 -- primary Evidence Production Module for Gate TGT-06
(Internalization / Trafficking Addressability) under ADC_TARGET_GATESET@1.0 /
INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E14, strictly against the frozen PR E13 construction
contract (src/contracts/gate_modules/tgt06_internalization_trafficking_addressability.yaml).
The module owns Gate-specific deterministic interpretation only: normalized
upstream internalization / trafficking facts -> source / identity QC -> frozen
Evidence-Ladder rung mapping -> Gate-neutral EvidencePackages -> one typed
InternalizationEvidenceCompletion (with the E6 / E8 / E10 / E12 completion-audit
exact-identity + snapshot-parity gene, and the UNION-of-projection
qualifying-DIRECT-configuration set) -> a proposed Direction x Strength via the
TGT-06 HIGHEST-QUALIFYING-RUNG grading authority under an EXISTENCE-PROOF
frozen_evaluation_order (one CLEAN productive DIRECT configuration is
POSITIVE / DIRECT; a same-configuration productive-vs-failure pair is
CONFLICTING / DIRECT with NO machine conflict resolver; >= 2 independent
DIRECT-quality failure configurations is NEGATIVE / DIRECT; exactly one is
INCONCLUSIVE / DIRECT, never NEGATIVE; a qualifying INDIRECT_STRONG landscape with
no DIRECT is POSITIVE / INDIRECT_STRONG; the legal pairs are exactly
POSITIVE/DIRECT, POSITIVE/INDIRECT_STRONG, NEGATIVE/DIRECT, CONFLICTING/DIRECT,
INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN) -> a machine-local fatal_review review
TRIGGER (Route A OR Route B multiple-independent-configuration failure, cancelled
by any qualifying productive DIRECT) -> machine acceptance -> one non-canonical
assessment proposal envelope.

Four invariants:

* Internalization is configuration-specific, not a target-intrinsic constant. A
  DIRECT rung is an EXISTENCE PROOF -- ONE qualifying disease-relevant
  antibody / epitope configuration with antibody-induced internalization AND
  lysosomal delivery, in ONE integrated observation. A single non-internalizing
  configuration never establishes target-wide non-internalization.
* INDIRECT_STRONG evidence is genuine positive addressability support and
  propagates to POSITIVE / INDIRECT_STRONG (highest-qualifying-rung authority,
  NOT the TGT-04 single-tier exception).
* Quantitative values are evidence, not thresholds. A source-reported numeric
  assay fact lives in the neutral claim and is never coerced or compared to a
  threshold / cutoff / invented "ADC-effective internalization rate". There is NO
  dedicated raw numeric field and NO raw-value reuse-parity branch.
* A single DIRECT-quality productive-internalization / trafficking failure is a
  DIRECT-class OPPOSES observation, not yet a NEGATIVE / DIRECT proposal and not a
  reproducible fatal pattern; only a Route A / Route B
  multiple-independent-configuration failure pattern, with NO qualifying
  productive DIRECT existence proof, may surface POTENTIAL_FATAL_PATTERN; the
  Module never decides fatality or ADC efficacy.

Live retrieval, extractors, normalizers, runners, persistence, and any GateSet
Decision / KILL are OUTSIDE this module (injected ports or downstream layers).
There is NO normalizer inside this package -- internalization qualifications are
given upstream by the provider.
"""

from __future__ import annotations

from .aggregate import AggregationOutcome
from .completion import (
    INTERNALIZATION_UNRESOLVED_KIND_VALUES,
    InternalizationEvidenceCompletion,
    InternalizationUnresolvedItem,
)
from .contracts import (
    ADDRESSABILITY_IMPLICATION_VALUES,
    ASSAY_VALIDATION_STATUS_VALUES,
    CANDIDATE_LEVEL,
    CANONICAL_ONLY_FIELDS,
    CONFIGURATION_IDENTITY_STATES,
    CONTEXT_ADEQUACY_VALUES,
    CONTEXT_ID,
    CONTEXT_VERSION,
    EVIDENCE_RUNG_VALUES,
    FATAL_REVIEW_STATUS_VALUES,
    GATE_ID,
    GATE_VERSION,
    GATESET_ID,
    GATESET_VERSION,
    INSTANTIATION_ID,
    INTERNALIZATION_OUTCOME_VALUES,
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    MODULE_ID,
    MODULE_VERSION,
    OBSERVATION_KIND_VALUES,
    REPRODUCIBILITY_STATUS_VALUES,
    SURFACE_CONTEXT_CLASS_VALUES,
    TGT06_EVIDENCE_CEILING,
    TGT06_GATE_QUESTION,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClassifiedInternalizationObservation,
    EmittedEvidence,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedInternalizationObservation,
    Tgt06ModuleInput,
    Tgt06ModuleRunResult,
    configuration_identity_projection,
    internalization_direction,
)
from .module import run
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt06InternalizationEvidenceProviderPort,
)

__all__ = [
    "MODULE_ID",
    "MODULE_VERSION",
    "GATE_ID",
    "GATE_VERSION",
    "GATESET_ID",
    "GATESET_VERSION",
    "INSTANTIATION_ID",
    "CONTEXT_ID",
    "CONTEXT_VERSION",
    "CANDIDATE_LEVEL",
    "TGT06_EVIDENCE_CEILING",
    "TGT06_GATE_QUESTION",
    "OBSERVATION_KIND_VALUES",
    "ASSAY_VALIDATION_STATUS_VALUES",
    "SURFACE_CONTEXT_CLASS_VALUES",
    "CONTEXT_ADEQUACY_VALUES",
    "INTERNALIZATION_OUTCOME_VALUES",
    "REPRODUCIBILITY_STATUS_VALUES",
    "EVIDENCE_RUNG_VALUES",
    "ADDRESSABILITY_IMPLICATION_VALUES",
    "FATAL_REVIEW_STATUS_VALUES",
    "CONFIGURATION_IDENTITY_STATES",
    "INTERNALIZATION_UNRESOLVED_KIND_VALUES",
    "LEGAL_DIRECTION_STRENGTH_PAIRS",
    "CANONICAL_ONLY_FIELDS",
    "CanonicalSourceRecord",
    "NormalizedInternalizationObservation",
    "InternalizationUnresolvedItem",
    "InternalizationEvidenceCompletion",
    "Tgt06ModuleInput",
    "ClassifiedInternalizationObservation",
    "EmittedEvidence",
    "FatalReviewRecord",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "AggregationOutcome",
    "Tgt06ModuleRunResult",
    "configuration_identity_projection",
    "internalization_direction",
    "Tgt06InternalizationEvidenceProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceResolverPort",
    "ExistingEvidenceLibraryPort",
    "run",
]
