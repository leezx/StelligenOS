"""Data-free contracts for constrained ADC opportunity generation.

This package defines boundaries only. Candidate generation, evidence
collection, evaluation, ranking, and persistence remain external.
"""

from .contracts import (
    AdversarialReview,
    CandidateLifecycle,
    CandidateDisposition,
    CandidateFilterResult,
    ClinicalFrame,
    EvaluationStatus,
    EvidenceDirection,
    EvidenceRecord,
    OpportunitySearchScope,
    ReviewStatus,
    TargetCandidate,
    TargetOpportunityHandoff,
)

__all__ = [
    "AdversarialReview",
    "CandidateLifecycle",
    "CandidateDisposition",
    "CandidateFilterResult",
    "ClinicalFrame",
    "EvaluationStatus",
    "EvidenceDirection",
    "EvidenceRecord",
    "OpportunitySearchScope",
    "ReviewStatus",
    "TargetCandidate",
    "TargetOpportunityHandoff",
]
