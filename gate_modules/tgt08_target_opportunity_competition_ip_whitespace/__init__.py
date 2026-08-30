"""MOD-TGT08 -- primary Evidence Production Module for Gate TGT-08
(Target Opportunity / Competition / IP Whitespace) under ADC_TARGET_GATESET@1.0
/ INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E6, strictly against the frozen E5 construction
contract (src/contracts/gate_modules/tgt08_target_opportunity_competition_ip_whitespace.yaml).
The module owns Gate-specific deterministic interpretation only: normalized
public-landscape facts -> source / identity QC -> frozen evidence-class mapping
-> Gate-neutral EvidencePackages -> two typed completion states -> weaker-axis
Direction x Strength (frozen truth table) -> a machine-local sponsor_review
review TRIGGER -> machine acceptance -> one non-canonical assessment proposal
envelope.

Three invariants:

* Empty results are not whitespace. Only an AUDITED completion can support an
  absence inference.
* TGT-08 NEGATIVE is a Gate-relative opportunity judgement, not a scientific
  KILL and not a sponsor decision.
* sponsor_review is a review trigger. The machine detects a pattern; the sponsor
  decides what it means.

Live ClinicalTrials / FDA / company / patent retrieval, Lens / PATENTSCOPE /
Google Patents adapters, an FTO engine, a legal opinion, sponsor routing /
Decision runtime, persistence, and any GateSet Decision / KILL are OUTSIDE this
module (injected ports or downstream layers).
"""

from __future__ import annotations

from .contracts import (
    CANONICAL_ONLY_FIELDS,
    EVIDENCE_AXIS_VALUES,
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    OBSERVATION_KIND_VALUES,
    OPPORTUNITY_IMPLICATION_VALUES,
    SOURCE_AUTHORITY_KIND_VALUES,
    SPONSOR_REVIEW_STATUS_VALUES,
    GATE_ID,
    GATE_VERSION,
    GATESET_ID,
    GATESET_VERSION,
    INSTANTIATION_ID,
    MODULE_ID,
    MODULE_VERSION,
    TGT08_EVIDENCE_CEILING,
    TGT08_GATE_QUESTION,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClassifiedOpportunity,
    CompetitiveLandscapeCompletion,
    EmittedEvidence,
    MachineAcceptanceRecord,
    NormalizedOpportunityRecord,
    PatentLandscapeCompletion,
    SponsorReviewRecord,
    Tgt08ModuleInput,
    Tgt08ModuleRunResult,
    overall_strength,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt08OpportunityProviderPort,
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
    "TGT08_EVIDENCE_CEILING",
    "TGT08_GATE_QUESTION",
    "EVIDENCE_AXIS_VALUES",
    "OBSERVATION_KIND_VALUES",
    "SOURCE_AUTHORITY_KIND_VALUES",
    "OPPORTUNITY_IMPLICATION_VALUES",
    "SPONSOR_REVIEW_STATUS_VALUES",
    "LEGAL_DIRECTION_STRENGTH_PAIRS",
    "CANONICAL_ONLY_FIELDS",
    "NormalizedOpportunityRecord",
    "CanonicalSourceRecord",
    "CompetitiveLandscapeCompletion",
    "PatentLandscapeCompletion",
    "Tgt08ModuleInput",
    "ClassifiedOpportunity",
    "EmittedEvidence",
    "SponsorReviewRecord",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "Tgt08ModuleRunResult",
    "overall_strength",
    "Tgt08OpportunityProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceResolverPort",
    "ExistingEvidenceLibraryPort",
    "run",
]
