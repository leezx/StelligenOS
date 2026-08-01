"""Pure identity and applicability contracts for Gate Model Rules.

The module carries no rule instances, case records, datasets, or evaluator.
All evidence and governance records are referenced from an external workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final


MODEL_LIFECYCLE_STANDARD_REF: Final = "ModelLifecycleStandard@1.0.0"
HISTORICAL_RULE_REFERENCE_CONTRACT: Final = "HistoricalADCRuleReference@1.0.0"
RULE_CONFIDENCE_LABELS: Final = frozenset({"high", "medium", "low"})
RULE_TYPES: Final = frozenset(
    {"one_sided_positive", "one_sided_negative", "contrastive", "insufficient_data"}
)
RULE_DIRECTIONS: Final = frozenset({"positive", "negative", "neutral", "unknown"})
APPLICABILITY_VALUES: Final = frozenset({"applies", "does_not_apply", "uncertain"})
REVIEW_STATUSES: Final = frozenset({"draft", "approved", "rejected"})

_SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
_GATE_REF = re.compile(r"^gate:[A-Za-z0-9][A-Za-z0-9_.-]*$")
_EXTERNAL_REF = re.compile(r"^external:[^\s]+$")


def _validate_semver(value: str, label: str) -> None:
    if not isinstance(value, str) or _SEMVER.fullmatch(value) is None:
        raise ValueError(f"{label} must be a SemVer value")


def _validate_external_ref(value: str, label: str) -> None:
    if not isinstance(value, str) or _EXTERNAL_REF.fullmatch(value) is None:
        raise ValueError(f"{label} must be an external reference")


def _validate_gate_id(value: str, label: str) -> None:
    if not _GATE_REF.fullmatch(value):
        raise ValueError(f"{label} must use the gate:<id> form")
    from src.capabilities.gates import gate_definition

    try:
        gate_definition(value.removeprefix("gate:"))
    except KeyError as exc:
        raise ValueError(f"{label} is not in the frozen Gate topology") from exc


@dataclass(frozen=True)
class GateModelRuleRef:
    """Stable external identity for one rule model artifact."""

    model_id: str
    model_version: str
    gate_id: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", self.model_id):
            raise ValueError("model_id contains unsupported characters")
        _validate_semver(self.model_version, "model_version")
        _validate_gate_id(f"gate:{self.gate_id}", "gate_id")

    def as_string(self) -> str:
        return f"{self.model_id}@{self.model_version}"


@dataclass(frozen=True)
class HistoricalRuleDescriptor:
    """Metadata for a human-reviewed rule, never an executable rule."""

    rule_id: str
    gate_ref: str
    rule_type: str
    direction: str
    confidence: str
    source_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    natural_language_predicates_executable: bool = False

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("rule_id must not be empty")
        _validate_gate_id(self.gate_ref, "gate_ref")
        if self.rule_type not in RULE_TYPES:
            raise ValueError(f"unsupported rule_type: {self.rule_type}")
        if self.direction not in RULE_DIRECTIONS:
            raise ValueError(f"unsupported direction: {self.direction}")
        if self.confidence not in RULE_CONFIDENCE_LABELS:
            raise ValueError(f"unsupported confidence: {self.confidence}")
        if self.natural_language_predicates_executable:
            raise ValueError("historical rule predicates cannot be executable")
        for source_ref in self.source_refs:
            _validate_external_ref(source_ref, "source_ref")
        for limitation_ref in self.limitation_refs:
            _validate_external_ref(limitation_ref, "limitation_ref")


@dataclass(frozen=True)
class RuleApplicabilityAssessment:
    """An external review assertion about one candidate and one rule."""

    rule_id: str
    applicability: str
    rationale_ref: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("rule_id must not be empty")
        if self.applicability not in APPLICABILITY_VALUES:
            raise ValueError(f"unsupported applicability: {self.applicability}")
        _validate_external_ref(self.rationale_ref, "rationale_ref")
        for evidence_ref in self.evidence_refs:
            _validate_external_ref(evidence_ref, "evidence_ref")


@dataclass(frozen=True)
class RuleApplicabilityBundle:
    """Review envelope supplied by an external workspace."""

    bundle_version: str
    candidate_ref: str
    gate_ref: str
    reviewer_ref: str
    reviewed_at: str
    review_status: str
    assessments: tuple[RuleApplicabilityAssessment, ...]

    def __post_init__(self) -> None:
        _validate_semver(self.bundle_version, "bundle_version")
        for value, label in (
            (self.candidate_ref, "candidate_ref"),
            (self.reviewer_ref, "reviewer_ref"),
        ):
            _validate_external_ref(value, label)
        _validate_gate_id(self.gate_ref, "gate_ref")
        if not self.reviewed_at:
            raise ValueError("reviewed_at must not be empty")
        if self.review_status not in REVIEW_STATUSES:
            raise ValueError(f"unsupported review_status: {self.review_status}")


def validate_external_ref(value: str) -> None:
    """Validate an external reference without reading the referenced workspace."""

    _validate_external_ref(value, "external_ref")
