"""Data-free contracts for constrained ADC opportunity generation.

This package defines boundaries only. Candidate generation, evidence
collection, evaluation, ranking, and persistence remain external.
"""

from .contracts import (
    AdversarialReview,
    AnchorClinicalContext,
    BiomarkerHypothesis,
    BiomarkerCutoffStatus,
    CDxStatus,
    CandidateLifecycle,
    CandidateDisposition,
    CandidateFilterResult,
    ClinicalFrame,
    ClinicalHypothesis,
    ClinicalHypothesisEntryMode,
    ClinicalLockState,
    EvaluationStatus,
    EvidenceDirection,
    EvidenceRecord,
    IntendedBenefitHypothesis,
    OpportunitySearchScope,
    ReviewStatus,
    TargetCandidate,
    TargetOpportunityHandoff,
    ProductHypothesis,
    can_transition_clinical_lock,
)

__all__ = [
    "AdversarialReview",
    "AnchorClinicalContext",
    "BiomarkerHypothesis",
    "BiomarkerCutoffStatus",
    "CDxStatus",
    "CandidateLifecycle",
    "CandidateDisposition",
    "CandidateFilterResult",
    "ClinicalFrame",
    "ClinicalHypothesis",
    "ClinicalHypothesisEntryMode",
    "ClinicalLockState",
    "EvaluationStatus",
    "EvidenceDirection",
    "EvidenceRecord",
    "IntendedBenefitHypothesis",
    "OpportunitySearchScope",
    "ReviewStatus",
    "TargetCandidate",
    "TargetOpportunityHandoff",
    "ProductHypothesis",
    "can_transition_clinical_lock",
]
