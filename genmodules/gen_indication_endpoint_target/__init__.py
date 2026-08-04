"""Data-free contracts for constrained ADC opportunity generation.

This package defines boundaries only. Candidate generation, evidence
collection, evaluation, ranking, and persistence remain external.
"""

from .contracts import (
    AdversarialReview,
    AnchorClinicalContext,
    BiomarkerHypothesis,
    CandidateLifecycle,
    CandidateDisposition,
    CandidateFilterResult,
    ClinicalFrame,
    ClinicalHypothesis,
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
)

__all__ = [
    "AdversarialReview",
    "AnchorClinicalContext",
    "BiomarkerHypothesis",
    "CandidateLifecycle",
    "CandidateDisposition",
    "CandidateFilterResult",
    "ClinicalFrame",
    "ClinicalHypothesis",
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
]
