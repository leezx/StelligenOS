"""Blueprint v1.3 decision-layer object contracts (runtime side).

These frozen dataclasses validate contract-shaped instances in memory. They do
not persist records, hold data, or execute anything. Disk instances live in the
external runtime workspace defined by
``docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md``; the field sets and
vocabularies here are kept byte-for-byte in step with
``src/contracts/data_layout/*.schema.*`` by ``tests/test_decision_model.py``.

Scope is Runtime Migration PR A: ``Candidate``, ``Context``,
``EvidencePackage``, ``CandidateGateAssessment`` and the ``Instantiation``
binding object. The sixth decision-layer object, ``Decision`` (and its
GO/KILL/... vocabulary), lands in PR B with the GateSet decision policy and is
deliberately absent here. The legacy ``core_objects@1.1`` registry
(``src/objects/core.py`` / ``src/contracts/core_objects.yaml``) is untouched;
adapters from it live in ``src/objects/legacy_adapters.py``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields
from typing import Final, Mapping, Sequence


# --- Controlled vocabularies (parity: src/contracts/decision_objects.yaml and
#     src/contracts/data_layout/*.schema.*) --------------------------------------

CANDIDATE_LEVELS: Final[tuple[str, ...]] = (
    "L00", "L01", "L02", "L03", "L04", "L05", "L06", "L07",
    "L08", "L09", "L10", "L11", "L12", "L13", "L14",
)

DIRECTION_VALUES: Final[tuple[str, ...]] = (
    "POSITIVE",
    "NEGATIVE",
    "CONFLICTING",
    "INCONCLUSIVE",
    "NOT_APPLICABLE",
)

STRENGTH_VALUES: Final[tuple[str, ...]] = (
    "DIRECT",
    "INDIRECT_STRONG",
    "WEAK",
    "UNKNOWN",
)

#: The three graded strengths; ``UNKNOWN`` is the absence of a grade, not a grade.
GRADED_STRENGTHS: Final[tuple[str, ...]] = ("DIRECT", "INDIRECT_STRONG", "WEAK")

EVIDENCE_ROLE_VALUES: Final[tuple[str, ...]] = (
    "SUPPORTING",
    "CONTRADICTING",
    "CONTEXTUAL",
)

CANDIDATE_STATUS_VALUES: Final[tuple[str, ...]] = ("ACTIVE", "HOLD", "RETIRED")
CONTEXT_STATUS_VALUES: Final[tuple[str, ...]] = ("ACTIVE", "HOLD", "RETIRED")
INSTANTIATION_STATUS_VALUES: Final[tuple[str, ...]] = (
    "ACTIVE",
    "HOLD",
    "FROZEN",
    "RETIRED",
)

EVIDENCE_REGIME_VALUES: Final[tuple[str, ...]] = (
    "PUBLIC_ONLY",
    "PUBLIC_PLUS_EXPERIMENTAL",
    "DEVELOPMENT",
)

CRITICAL_UNKNOWN_RESOLUTIONS: Final[tuple[str, ...]] = (
    "PUBLIC_RESOLVABLE",
    "EXPERIMENT_REQUIRED",
    "CURRENTLY_UNRESOLVABLE",
)

#: Canonical assessments and canonical decisions are human-approved only;
#: machine proposals never enter the canonical record.
CANONICAL_REVIEW_STATUS: Final[str] = "HUMAN_APPROVED"

SOURCE_TYPE_VALUES: Final[tuple[str, ...]] = (
    "PMID", "PMC", "DOI", "NCT", "GEO", "PATENT",
    "REGULATORY", "COMPANY_DISCLOSURE", "DATASET", "OTHER",
)


# --- Identity patterns (parity: src/contracts/data_layout/*.schema.*) ----------

_CANDIDATE_ID = re.compile(r"^CAND-L[0-9]{2}-[0-9]{6}$")
_PARENT_CANDIDATE_ID = re.compile(r"^(CAND-L[0-9]{2}-[0-9]{6})?$")
_CANDIDATE_TYPE = re.compile(r"^[A-Z0-9_]+$")
_CONTEXT_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INSTANTIATION_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_EVIDENCE_ID = re.compile(r"^EP-[0-9]{8}$")
_ASSESSMENT_ID = re.compile(r"^ASMT-[0-9]{6}$")
_GATESET_ID = re.compile(r"^[A-Z0-9_]+_GATESET$")
_SOURCE_ID = re.compile(r"^SRC-[0-9]{8}$")
_ISO_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")


# --- Fields a schema's ``not/anyOf`` bans; enforced here by structural absence
#     plus the checks in ``tests/test_decision_model.py`` -----------------------

CANDIDATE_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = (
    "context_id",
    "context_version",
    "direction",
    "strength",
    "decision",
    "score",
    "assessment_id",
    "evidence_refs",
    "gate_id",
    "gateset_id",
)
CONTEXT_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = (
    "direction",
    "strength",
    "decision",
    "candidate_id",
    "score",
    "superseded_by",
)
EVIDENCE_PACKAGE_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = (
    "direction",
    "strength",
    "grade",
    "superseded_by",
    "status",
)
ASSESSMENT_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = (
    "decision",
    "score",
    "superseded_by",
)
INSTANTIATION_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = (
    "candidate_id",
    "assessments",
    "evidence_refs",
)


# --- Shared validators --------------------------------------------------------

def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_pattern(value: str, pattern: re.Pattern[str], field_name: str) -> None:
    _require_text(value, field_name)
    if not pattern.match(value):
        raise ValueError(f"{field_name} does not match {pattern.pattern}")


def _require_optional_pattern(
    value: str, pattern: re.Pattern[str], field_name: str
) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string ('' when absent)")
    if not pattern.match(value):
        raise ValueError(f"{field_name} does not match {pattern.pattern}")


def _require_external_ref(value: str, field_name: str) -> None:
    _require_text(value, field_name)
    if not value.startswith("external:"):
        raise ValueError(f"{field_name} must use the external: scheme")


def _require_positive_int(value: int, field_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{field_name} must be an integer >= 1")


def _require_choice(value: str, allowed: Sequence[str], field_name: str) -> None:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {tuple(allowed)}")


def _require_mapping_keys(
    value: Mapping[str, object], required: Sequence[str], field_name: str
) -> None:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    missing = [key for key in required if key not in value]
    if missing:
        raise ValueError(f"{field_name} is missing required keys: {missing}")


def _require_str_tuple(value: tuple[str, ...], field_name: str) -> None:
    if not isinstance(value, tuple) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError(f"{field_name} must be a tuple of non-empty strings")


# --- Candidate --------------------------------------------------------------

@dataclass(frozen=True)
class Candidate:
    """A context-independent search-space member at one Candidate Level."""

    candidate_id: str
    candidate_type: str
    level: str
    canonical_name: str
    status: str
    version: int
    created_at: str
    provenance_ref: str
    parent_candidate_id: str = ""

    def __post_init__(self) -> None:
        _require_pattern(self.candidate_id, _CANDIDATE_ID, "candidate_id")
        _require_pattern(self.candidate_type, _CANDIDATE_TYPE, "candidate_type")
        _require_choice(self.level, CANDIDATE_LEVELS, "level")
        _require_text(self.canonical_name, "canonical_name")
        _require_choice(self.status, CANDIDATE_STATUS_VALUES, "status")
        _require_positive_int(self.version, "version")
        _require_pattern(self.created_at, _ISO_DATE, "created_at")
        _require_external_ref(self.provenance_ref, "provenance_ref")
        _require_optional_pattern(
            self.parent_candidate_id, _PARENT_CANDIDATE_ID, "parent_candidate_id"
        )


# --- Context --------------------------------------------------------------

@dataclass(frozen=True)
class Context:
    """A reusable, versioned scope declaration. Carries no verdict."""

    context_id: str
    context_version: int
    canonical_name: str
    dimensions: Mapping[str, str | None]
    status: str
    created_at: str
    provenance_ref: str = ""
    supersedes_version: int | None = None

    def __post_init__(self) -> None:
        _require_pattern(self.context_id, _CONTEXT_ID, "context_id")
        _require_positive_int(self.context_version, "context_version")
        _require_text(self.canonical_name, "canonical_name")
        if not isinstance(self.dimensions, Mapping) or not self.dimensions:
            raise ValueError("dimensions must be a non-empty mapping")
        for key, value in self.dimensions.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("dimensions keys must be non-empty strings")
            if value is not None and not isinstance(value, str):
                raise ValueError("dimensions values must be a string or None")
        _require_choice(self.status, CONTEXT_STATUS_VALUES, "status")
        _require_pattern(self.created_at, _ISO_DATE, "created_at")
        if self.provenance_ref:
            _require_external_ref(self.provenance_ref, "provenance_ref")
        if self.supersedes_version is not None:
            _require_positive_int(self.supersedes_version, "supersedes_version")


# --- EvidencePackage ------------------------------------------------------

@dataclass(frozen=True)
class EvidencePackage:
    """One atomic, neutral empirical observation. Immutable by id, no grade."""

    evidence_id: str
    schema_version: int
    claim: str
    measurement: Mapping[str, object]
    candidate_refs: tuple[str, ...]
    study_context: Mapping[str, object]
    provenance: Mapping[str, object]
    interpretation_boundary: Mapping[str, object]
    derivation: Mapping[str, object]
    supersedes_evidence_id: str = ""

    def __post_init__(self) -> None:
        _require_pattern(self.evidence_id, _EVIDENCE_ID, "evidence_id")
        _require_positive_int(self.schema_version, "schema_version")
        _require_text(self.claim, "claim")
        _require_mapping_keys(
            self.measurement, ("type", "analyte", "readout", "result"), "measurement"
        )
        if not isinstance(self.candidate_refs, tuple) or not all(
            isinstance(ref, str) and _CANDIDATE_ID.match(ref)
            for ref in self.candidate_refs
        ):
            raise ValueError("candidate_refs must be a tuple of CAND-Lnn-nnnnnn ids")
        _require_mapping_keys(
            self.study_context,
            ("indication", "treatment_state", "sample_type"),
            "study_context",
        )
        _require_mapping_keys(
            self.provenance,
            ("source_id", "source_type", "source_identifier", "locator", "retrieved_at"),
            "provenance",
        )
        _require_pattern(
            str(self.provenance["source_id"]), _SOURCE_ID, "provenance.source_id"
        )
        _require_choice(
            str(self.provenance["source_type"]),
            SOURCE_TYPE_VALUES,
            "provenance.source_type",
        )
        if not _ISO_DATE_PREFIX.match(str(self.provenance["retrieved_at"])):
            raise ValueError("provenance.retrieved_at must start with an ISO date")
        _require_mapping_keys(
            self.interpretation_boundary,
            ("directly_supports", "does_not_support", "limitations", "evidence_ceiling"),
            "interpretation_boundary",
        )
        _require_mapping_keys(
            self.derivation, ("module_run_id", "code_commit"), "derivation"
        )
        if self.supersedes_evidence_id:
            _require_pattern(
                self.supersedes_evidence_id, _EVIDENCE_ID, "supersedes_evidence_id"
            )


# --- CandidateGateAssessment -------------------------------------------------

@dataclass(frozen=True)
class EvidenceRef:
    """One ``{evidence_id, role}`` reference inside an assessment."""

    evidence_id: str
    role: str

    def __post_init__(self) -> None:
        _require_pattern(self.evidence_id, _EVIDENCE_ID, "evidence_id")
        _require_choice(self.role, EVIDENCE_ROLE_VALUES, "role")


@dataclass(frozen=True)
class CandidateGateAssessment:
    """The canonical Candidate x Gate matrix cell. Direction + Strength only."""

    assessment_id: str
    assessment_version: int
    instantiation_id: str
    candidate_id: str
    context_id: str
    context_version: int
    gateset_id: str
    gateset_version: str
    gate_id: str
    gate_version: str
    direction: str
    strength: str
    evidence_refs: tuple[EvidenceRef, ...]
    aggregation_rationale: str
    critical_unknowns: tuple[Mapping[str, str], ...]
    evidence_ceiling: str
    review: Mapping[str, str]
    key_supporting_evidence: tuple[Mapping[str, object], ...] = field(default_factory=tuple)
    key_contradicting_evidence: tuple[Mapping[str, object], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_pattern(self.assessment_id, _ASSESSMENT_ID, "assessment_id")
        _require_positive_int(self.assessment_version, "assessment_version")
        _require_pattern(self.instantiation_id, _INSTANTIATION_ID, "instantiation_id")
        _require_pattern(self.candidate_id, _CANDIDATE_ID, "candidate_id")
        _require_pattern(self.context_id, _CONTEXT_ID, "context_id")
        _require_positive_int(self.context_version, "context_version")
        _require_pattern(self.gateset_id, _GATESET_ID, "gateset_id")
        _require_text(self.gateset_version, "gateset_version")
        _require_text(self.gate_id, "gate_id")
        _require_text(self.gate_version, "gate_version")
        _require_choice(self.direction, DIRECTION_VALUES, "direction")
        _require_choice(self.strength, STRENGTH_VALUES, "strength")
        if not isinstance(self.evidence_refs, tuple) or not all(
            isinstance(ref, EvidenceRef) for ref in self.evidence_refs
        ):
            raise ValueError("evidence_refs must be a tuple of EvidenceRef")
        _require_text(self.aggregation_rationale, "aggregation_rationale")
        if not isinstance(self.critical_unknowns, tuple):
            raise ValueError("critical_unknowns must be a tuple")
        for index, unknown in enumerate(self.critical_unknowns):
            _require_mapping_keys(
                unknown, ("unknown", "resolution"), f"critical_unknowns[{index}]"
            )
            _require_choice(
                str(unknown["resolution"]),
                CRITICAL_UNKNOWN_RESOLUTIONS,
                f"critical_unknowns[{index}].resolution",
            )
        _require_text(self.evidence_ceiling, "evidence_ceiling")
        _require_mapping_keys(
            self.review, ("status", "reviewer", "reviewed_at"), "review"
        )
        if self.review["status"] != CANONICAL_REVIEW_STATUS:
            raise ValueError(
                f"canonical assessment review.status must be {CANONICAL_REVIEW_STATUS!r}"
            )
        self._check_direction_strength_matrix()

    def _check_direction_strength_matrix(self) -> None:
        supporting = sum(
            1 for ref in self.evidence_refs if ref.role == "SUPPORTING"
        )
        contradicting = sum(
            1 for ref in self.evidence_refs if ref.role == "CONTRADICTING"
        )
        count = len(self.evidence_refs)

        if self.direction in ("POSITIVE", "NEGATIVE"):
            if self.strength not in GRADED_STRENGTHS:
                raise ValueError(
                    f"{self.direction} must not use strength {self.strength}"
                )
            if count < 1:
                raise ValueError(f"{self.direction} needs at least one evidence_ref")
        elif self.direction == "CONFLICTING":
            if self.strength not in GRADED_STRENGTHS:
                raise ValueError("CONFLICTING must not use strength UNKNOWN")
            if supporting < 1 or contradicting < 1:
                raise ValueError(
                    "CONFLICTING needs >=1 SUPPORTING and >=1 CONTRADICTING evidence_ref"
                )
            if not self.key_supporting_evidence or not self.key_contradicting_evidence:
                raise ValueError(
                    "CONFLICTING requires non-empty key_supporting_evidence and "
                    "key_contradicting_evidence"
                )
        elif self.direction == "INCONCLUSIVE":
            has_qualified = self.strength in GRADED_STRENGTHS and count >= 1
            is_unknown_state = self.strength == "UNKNOWN" and count == 0
            if not (has_qualified or is_unknown_state):
                raise ValueError(
                    "INCONCLUSIVE must be either (graded strength + >=1 evidence_ref) "
                    "or (strength UNKNOWN + no evidence_refs)"
                )
        elif self.direction == "NOT_APPLICABLE":
            if self.strength != "UNKNOWN" or count != 0:
                raise ValueError(
                    "NOT_APPLICABLE must use strength UNKNOWN with no evidence_refs"
                )


# --- Instantiation (binding only; NOT a seventh core object) ----------------

@dataclass(frozen=True)
class Instantiation:
    """Binds candidate_type + level + context + modality to a versioned GateSet."""

    instantiation_id: str
    candidate_type: str
    candidate_level: str
    context_id: str
    context_version: int
    modality: str
    gateset_id: str
    gateset_version: str
    evidence_regime: str
    status: str
    version: int
    created_at: str

    def __post_init__(self) -> None:
        _require_pattern(self.instantiation_id, _INSTANTIATION_ID, "instantiation_id")
        _require_pattern(self.candidate_type, _CANDIDATE_TYPE, "candidate_type")
        _require_choice(self.candidate_level, CANDIDATE_LEVELS, "candidate_level")
        _require_pattern(self.context_id, _CONTEXT_ID, "context_id")
        _require_positive_int(self.context_version, "context_version")
        _require_text(self.modality, "modality")
        _require_pattern(self.gateset_id, _GATESET_ID, "gateset_id")
        _require_text(self.gateset_version, "gateset_version")
        _require_choice(
            self.evidence_regime, EVIDENCE_REGIME_VALUES, "evidence_regime"
        )
        _require_choice(self.status, INSTANTIATION_STATUS_VALUES, "status")
        _require_positive_int(self.version, "version")
        _require_pattern(self.created_at, _ISO_DATE, "created_at")


# --- Introspection helpers (used by the parity test) -----------------------

DECISION_OBJECTS: Final[tuple[type, ...]] = (
    Candidate,
    Context,
    EvidencePackage,
    CandidateGateAssessment,
    Instantiation,
)


def field_names(object_type: type) -> tuple[str, ...]:
    """Return the declared field names of a decision-model dataclass."""

    return tuple(f.name for f in fields(object_type))
