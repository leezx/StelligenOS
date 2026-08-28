"""Blueprint v1.3 decision-layer object contracts (runtime side).

These frozen dataclasses validate contract-shaped instances in memory. They do
not persist records, hold data, or execute anything. Disk instances live in the
external runtime workspace defined by
``docs/protocols/STELLIGENOS_DATA_LAYOUT_SPEC.v1.0.md``; the field sets, enums,
nested shapes and the direction x strength matrix here are kept in step with
``src/contracts/data_layout/*.schema.*`` by ``tests/test_decision_model.py``.

Immutability is deep: every nested mapping is snapshotted and wrapped in a
``MappingProxyType`` and every nested sequence becomes a ``tuple`` in
``__post_init__`` *before* validation, so a caller cannot mutate the dict it
passed in and thereby move a validated instance into an invalid state.

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
from types import MappingProxyType
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


# --- Deep freeze -----------------------------------------------------------

def _deep_freeze(value):
    """Return a deeply-immutable snapshot: mappings -> MappingProxyType over a
    fresh copy, sequences -> tuple, recursively. Strings/bytes are scalars."""

    if isinstance(value, Mapping):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)) and not isinstance(value, (str, bytes)):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _freeze_attr(instance, name: str) -> None:
    object.__setattr__(instance, name, _deep_freeze(getattr(instance, name)))


# --- Shared validators --------------------------------------------------------

def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_str(value, field_name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must not be empty")


def _require_str_tuple(value, field_name: str) -> None:
    if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a sequence of strings")


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
    if not _is_int(value) or value < 1:
        raise ValueError(f"{field_name} must be an integer >= 1")


def _require_choice(value: str, allowed: Sequence[str], field_name: str) -> None:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {tuple(allowed)}")


def _check_block(
    block,
    *,
    name: str,
    required: Sequence[str],
    allowed: Sequence[str] | None = None,
    closed: bool = True,
) -> None:
    """Enforce a nested object's key set the way the frozen schema does.

    ``closed`` mirrors ``additionalProperties: false`` (exact key set); when
    ``False`` extra keys are permitted (``additionalProperties: true``).
    """

    if not isinstance(block, Mapping):
        raise ValueError(f"{name} must be a mapping")
    keys = set(block)
    missing = [key for key in required if key not in keys]
    if missing:
        raise ValueError(f"{name} is missing required keys: {missing}")
    if closed:
        permitted = set(allowed) if allowed is not None else set(required)
        extra = keys - permitted
        if extra:
            raise ValueError(
                f"{name} has keys the frozen schema forbids: {sorted(extra)}"
            )


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
        _freeze_attr(self, "dimensions")

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

_MEASUREMENT_KEYS: Final[tuple[str, ...]] = ("type", "analyte", "readout", "result", "unit")
_STUDY_CONTEXT_REQUIRED: Final[tuple[str, ...]] = (
    "indication",
    "treatment_state",
    "sample_type",
)
_PROVENANCE_KEYS: Final[tuple[str, ...]] = (
    "source_id",
    "source_type",
    "source_identifier",
    "locator",
    "retrieved_at",
)
_INTERPRETATION_KEYS: Final[tuple[str, ...]] = (
    "directly_supports",
    "does_not_support",
    "limitations",
    "evidence_ceiling",
)
_DERIVATION_KEYS: Final[tuple[str, ...]] = ("module_run_id", "code_commit")


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
        for name in (
            "measurement",
            "candidate_refs",
            "study_context",
            "provenance",
            "interpretation_boundary",
            "derivation",
        ):
            _freeze_attr(self, name)

        _require_pattern(self.evidence_id, _EVIDENCE_ID, "evidence_id")
        _require_positive_int(self.schema_version, "schema_version")
        _require_text(self.claim, "claim")

        # measurement (additionalProperties: false; scalars minLength 1, unit str)
        _check_block(
            self.measurement,
            name="measurement",
            required=_MEASUREMENT_KEYS[:4],
            allowed=_MEASUREMENT_KEYS,
        )
        for key in _MEASUREMENT_KEYS[:4]:
            _require_str(self.measurement[key], f"measurement.{key}")
        if "unit" in self.measurement:
            _require_str(self.measurement["unit"], "measurement.unit", allow_empty=True)

        # candidate_refs (array of CAND ids; may be empty)
        if not isinstance(self.candidate_refs, tuple) or not all(
            isinstance(ref, str) and _CANDIDATE_ID.match(ref)
            for ref in self.candidate_refs
        ):
            raise ValueError("candidate_refs must be a sequence of CAND-Lnn-nnnnnn ids")

        # study_context (additionalProperties: true)
        _check_block(
            self.study_context,
            name="study_context",
            required=_STUDY_CONTEXT_REQUIRED,
            closed=False,
        )
        for key in _STUDY_CONTEXT_REQUIRED:
            _require_str(self.study_context[key], f"study_context.{key}", allow_empty=True)
        if "n" in self.study_context and not (
            _is_int(self.study_context["n"]) or isinstance(self.study_context["n"], str)
        ):
            raise ValueError("study_context.n must be an integer or a string")
        for key in ("model", "assay"):
            if key in self.study_context:
                _require_str(
                    self.study_context[key], f"study_context.{key}", allow_empty=True
                )

        # provenance (additionalProperties: false)
        _check_block(self.provenance, name="provenance", required=_PROVENANCE_KEYS)
        _require_pattern(
            self.provenance["source_id"], _SOURCE_ID, "provenance.source_id"
        )
        _require_choice(
            self.provenance["source_type"], SOURCE_TYPE_VALUES, "provenance.source_type"
        )
        _require_str(
            self.provenance["source_identifier"], "provenance.source_identifier"
        )
        _require_str(self.provenance["locator"], "provenance.locator", allow_empty=True)
        _require_str(self.provenance["retrieved_at"], "provenance.retrieved_at")
        if not _ISO_DATE_PREFIX.match(self.provenance["retrieved_at"]):
            raise ValueError("provenance.retrieved_at must start with an ISO date")

        # interpretation_boundary (additionalProperties: false)
        _check_block(
            self.interpretation_boundary,
            name="interpretation_boundary",
            required=_INTERPRETATION_KEYS,
        )
        for key in _INTERPRETATION_KEYS[:3]:
            _require_str_tuple(
                self.interpretation_boundary[key], f"interpretation_boundary.{key}"
            )
        _require_str(
            self.interpretation_boundary["evidence_ceiling"],
            "interpretation_boundary.evidence_ceiling",
        )

        # derivation (additionalProperties: false)
        _check_block(self.derivation, name="derivation", required=_DERIVATION_KEYS)
        for key in _DERIVATION_KEYS:
            _require_str(self.derivation[key], f"derivation.{key}", allow_empty=True)

        if self.supersedes_evidence_id:
            _require_pattern(
                self.supersedes_evidence_id, _EVIDENCE_ID, "supersedes_evidence_id"
            )


# --- CandidateGateAssessment -------------------------------------------------

_REVIEW_KEYS: Final[tuple[str, ...]] = ("status", "reviewer", "reviewed_at")
_CRITICAL_UNKNOWN_KEYS: Final[tuple[str, ...]] = ("unknown", "resolution")


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
        for name in (
            "evidence_refs",
            "critical_unknowns",
            "review",
            "key_supporting_evidence",
            "key_contradicting_evidence",
        ):
            _freeze_attr(self, name)

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
            raise ValueError("evidence_refs must be a sequence of EvidenceRef")

        _require_text(self.aggregation_rationale, "aggregation_rationale")

        if not isinstance(self.critical_unknowns, tuple):
            raise ValueError("critical_unknowns must be a sequence")
        for index, unknown in enumerate(self.critical_unknowns):
            _check_block(
                unknown,
                name=f"critical_unknowns[{index}]",
                required=_CRITICAL_UNKNOWN_KEYS,
            )
            _require_str(unknown["unknown"], f"critical_unknowns[{index}].unknown")
            _require_choice(
                unknown["resolution"],
                CRITICAL_UNKNOWN_RESOLUTIONS,
                f"critical_unknowns[{index}].resolution",
            )

        _require_str(self.evidence_ceiling, "evidence_ceiling")

        _check_block(self.review, name="review", required=_REVIEW_KEYS)
        if self.review["status"] != CANONICAL_REVIEW_STATUS:
            raise ValueError(
                f"canonical assessment review.status must be {CANONICAL_REVIEW_STATUS!r}"
            )
        _require_str(self.review["reviewer"], "review.reviewer")
        _require_str(self.review["reviewed_at"], "review.reviewed_at")
        if not _ISO_DATE_PREFIX.match(self.review["reviewed_at"]):
            raise ValueError("review.reviewed_at must start with an ISO date")

        for name in ("key_supporting_evidence", "key_contradicting_evidence"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or not all(
                isinstance(item, Mapping) for item in value
            ):
                raise ValueError(f"{name} must be a sequence of mappings")

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
