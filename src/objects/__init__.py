"""Core object contracts for StelligenOS.

``core`` is the legacy ``core_objects@1.1`` registry (eight object types),
retained during the runtime migration. ``decision_model`` is the Blueprint v1.3
decision-layer object set introduced by Runtime Migration PR A;
``legacy_adapters`` maps the former to the latter.
"""

from .core import CORE_OBJECT_TYPES, CoreObject
from .decision_model import (
    CANDIDATE_LEVELS,
    CANONICAL_REVIEW_STATUS,
    DECISION_OBJECTS,
    DIRECTION_VALUES,
    EVIDENCE_REGIME_VALUES,
    EVIDENCE_ROLE_VALUES,
    GRADED_STRENGTHS,
    STRENGTH_VALUES,
    Candidate,
    CandidateGateAssessment,
    Context,
    EvidencePackage,
    EvidenceRef,
    Instantiation,
    field_names,
)
from .legacy_adapters import (
    LEGACY_CROSSWALK,
    ONE_TO_ONE_LEGACY_TYPES,
    LegacyCrosswalkEntry,
    adapt_core_object_to_candidate,
)

__all__ = [
    "CORE_OBJECT_TYPES",
    "CoreObject",
    "CANDIDATE_LEVELS",
    "CANONICAL_REVIEW_STATUS",
    "DECISION_OBJECTS",
    "DIRECTION_VALUES",
    "EVIDENCE_REGIME_VALUES",
    "EVIDENCE_ROLE_VALUES",
    "GRADED_STRENGTHS",
    "STRENGTH_VALUES",
    "Candidate",
    "CandidateGateAssessment",
    "Context",
    "EvidencePackage",
    "EvidenceRef",
    "Instantiation",
    "field_names",
    "LEGACY_CROSSWALK",
    "ONE_TO_ONE_LEGACY_TYPES",
    "LegacyCrosswalkEntry",
    "adapt_core_object_to_candidate",
]
