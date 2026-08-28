"""Blueprint v1.3 two-rule-layer Gate system contracts (runtime side).

Runtime Migration PR B. Frozen dataclasses that validate contract-shaped
instances in memory -- no data, no persistence, no decision engine. The shared
validators, deep-freeze and identity patterns are reused verbatim from
``src/objects/decision_model.py`` (PR A) so the two contract layers cannot
diverge on how they validate.

* ``EvidenceLadder`` -- the shape of one Gate's DIRECT/INDIRECT_STRONG/WEAK
  ladder. Rung *bodies* for real gates are per-GateSet science and land in PR D.
* ``Gate`` -- one scientific question: assessment_rule over an evidence_ladder,
  producing Direction + Strength (the output object is PR A's
  ``CandidateGateAssessment``; there is no new envelope here).
* ``GateSet`` -- a versioned set of Gates for one Candidate Level plus the four
  rule refs (decision_rule / fatal_gate_policy / required_gate_policy /
  unknown_policy) that turn a Candidate's assessments into a ``Decision``.
* ``Decision`` -- the sixth decision-layer object, deferred from PR A. Kept in
  byte parity with ``src/contracts/data_layout/decision.schema.json``.

The legacy ``gate_system@0.1.0`` / 45-gate topology
(``src/capabilities/gates.py`` / ``src/contracts/gate_system.yaml``) is
untouched and stays ``FROZEN_LEGACY``; ``src/objects/legacy_gate_map.py`` holds
the migration reference.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Final, Mapping

from src.objects.decision_model import (
    CANDIDATE_LEVELS,
    CANONICAL_REVIEW_STATUS,
    GRADED_STRENGTHS,
    _ASSESSMENT_ID,
    _CANDIDATE_ID,
    _GATESET_ID,
    _INSTANTIATION_ID,
    _ISO_DATE_PREFIX,
    _check_block,
    _freeze_attr,
    _is_int,
    _require_choice,
    _require_external_ref,
    _require_pattern,
    _require_positive_int,
    _require_str,
    _require_str_tuple,
    _require_text,
)


# --- Controlled vocabularies (parity: src/contracts/gate_contracts.yaml and,
#     for Decision, src/contracts/data_layout/decision.schema.json) -------------

DECISION_VALUES: Final[tuple[str, ...]] = (
    "GO",
    "CONDITIONAL_GO",
    "HOLD",
    "MORE_EVIDENCE",
    "KILL",
    "NOMINATE",
    "COMMIT",
)

DOMINANT_EVIDENCE_REGIMES: Final[tuple[str, ...]] = (
    "PUBLIC_PRIMARY",
    "PUBLIC_HYBRID",
    "EXPERIMENT_PRIMARY",
    "DEVELOPMENT_PRIMARY",
)

#: Evidence Ladder rungs, highest first. ``UNKNOWN`` is not a rung; it is the
#: assessment state when no rung is met.
LADDER_GRADES: Final[tuple[str, ...]] = ("DIRECT", "INDIRECT_STRONG", "WEAK")

_CANONICAL_GATESET_IDS: Final[dict[str, str]] = {
    "L00": "INDICATION_GATESET",
    "L01": "PATIENT_TERRITORY_GATESET",
    "L02": "ENDPOINT_GATESET",
    "L03": "MODALITY_GATESET",
    "L04": "ADC_TARGET_GATESET",
    "L05": "ADC_EPITOPE_GATESET",
    "L06": "ANTIBODY_BINDER_GATESET",
    "L07": "LINKER_GATESET",
    "L08": "PAYLOAD_GATESET",
    "L09": "ADC_DESIGN_GATESET",
    "L10": "ADC_HIT_GATESET",
    "L11": "ADC_LEAD_GATESET",
    "L12": "BIOMARKER_GATESET",
    "L13": "DEVELOPMENT_CANDIDATE_GATESET",
    "L14": "REGIMEN_GATESET",
}

#: Canonical GateSet id per Candidate Level (CURRENT_SYSTEM v5 section 4.3).
CANONICAL_GATESET_IDS: Final[Mapping[str, str]] = MappingProxyType(_CANONICAL_GATESET_IDS)


# --- Identity patterns ----------------------------------------------------

_DECISION_ID = re.compile(r"^DEC-[0-9]{4}$")
_MODULE_ID = re.compile(r"^MOD-[A-Z0-9]+$")
_CELL = re.compile(
    r"^((POSITIVE|NEGATIVE|CONFLICTING|INCONCLUSIVE)/(DIRECT|INDIRECT_STRONG|WEAK)"
    r"|UNKNOWN|NOT_APPLICABLE)$"
)


DECISION_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = ("superseded_by",)

_REVIEW_KEYS: Final[tuple[str, ...]] = ("status", "reviewer", "reviewed_at")
_SNAPSHOT_REF_KEYS: Final[tuple[str, ...]] = ("assessment_id", "assessment_version", "cell")


for _lvl, _gs in _CANONICAL_GATESET_IDS.items():
    if _lvl not in CANDIDATE_LEVELS:
        raise RuntimeError(f"canonical gateset level {_lvl} is not a Candidate Level")
    if not _GATESET_ID.match(_gs):
        raise RuntimeError(f"canonical gateset id {_gs} fails ^[A-Z0-9_]+_GATESET$")
if set(_CANONICAL_GATESET_IDS) != set(CANDIDATE_LEVELS):
    raise RuntimeError("CANONICAL_GATESET_IDS must cover every Candidate Level L00-L14")


# --- EvidenceLadder -----------------------------------------------------

@dataclass(frozen=True)
class LadderRung:
    """One rung: an evidence *class* set that earns a given grade, plus what that
    rung's evidence can and cannot establish."""

    grade: str
    admissible_evidence_classes: tuple[str, ...]
    ceiling_rule: str

    def __post_init__(self) -> None:
        _freeze_attr(self, "admissible_evidence_classes")
        _require_choice(self.grade, LADDER_GRADES, "grade")
        _require_str_tuple(
            self.admissible_evidence_classes, "admissible_evidence_classes"
        )
        if not self.admissible_evidence_classes:
            raise ValueError("admissible_evidence_classes must be non-empty")
        _require_text(self.ceiling_rule, "ceiling_rule")


@dataclass(frozen=True)
class EvidenceLadder:
    """One Gate's ladder shape. Rungs cover DIRECT, INDIRECT_STRONG, WEAK once
    each, highest first. There is no quantity field: type ceiling outranks
    quantity."""

    gate_id: str
    gate_version: str
    rungs: tuple[LadderRung, ...]
    evidence_ceiling: str

    def __post_init__(self) -> None:
        _freeze_attr(self, "rungs")
        _require_text(self.gate_id, "gate_id")
        _require_text(self.gate_version, "gate_version")
        if not isinstance(self.rungs, tuple) or not all(
            isinstance(rung, LadderRung) for rung in self.rungs
        ):
            raise ValueError("rungs must be a sequence of LadderRung")
        if tuple(rung.grade for rung in self.rungs) != LADDER_GRADES:
            raise ValueError(
                "rungs must be exactly DIRECT, INDIRECT_STRONG, WEAK in that order"
            )
        _require_text(self.evidence_ceiling, "evidence_ceiling")


# --- Gate --------------------------------------------------------------

@dataclass(frozen=True)
class Gate:
    """One scientific question with its own assessment_rule and evidence_ladder."""

    gate_id: str
    gate_version: str
    gateset_id: str
    candidate_level: str
    gate_question: str
    dominant_evidence_regime: str
    evidence_required: tuple[str, ...]
    evidence_ladder_ref: str
    assessment_rule_ref: str
    primary_module_id: str
    primary_module_version: str
    fatal_conditions: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _freeze_attr(self, "evidence_required")
        _freeze_attr(self, "fatal_conditions")
        _require_text(self.gate_id, "gate_id")
        _require_text(self.gate_version, "gate_version")
        _require_pattern(self.gateset_id, _GATESET_ID, "gateset_id")
        _require_choice(self.candidate_level, CANDIDATE_LEVELS, "candidate_level")
        _require_text(self.gate_question, "gate_question")
        _require_choice(
            self.dominant_evidence_regime,
            DOMINANT_EVIDENCE_REGIMES,
            "dominant_evidence_regime",
        )
        _require_str_tuple(self.evidence_required, "evidence_required")
        if not self.evidence_required:
            raise ValueError("evidence_required must be non-empty")
        _require_external_ref(self.evidence_ladder_ref, "evidence_ladder_ref")
        _require_external_ref(self.assessment_rule_ref, "assessment_rule_ref")
        _require_pattern(self.primary_module_id, _MODULE_ID, "primary_module_id")
        _require_text(self.primary_module_version, "primary_module_version")
        _require_str_tuple(self.fatal_conditions, "fatal_conditions")


# --- GateSet ---------------------------------------------------------

@dataclass(frozen=True)
class GateSetMember:
    """One ``{gate_id, gate_version}`` entry in a GateSet."""

    gate_id: str
    gate_version: str

    def __post_init__(self) -> None:
        _require_text(self.gate_id, "gate_id")
        _require_text(self.gate_version, "gate_version")


@dataclass(frozen=True)
class GateSet:
    """A versioned set of Gates for one Candidate Level plus the four rule refs
    that turn a Candidate's assessments into a Decision."""

    gateset_id: str
    gateset_version: str
    candidate_level: str
    gates: tuple[GateSetMember, ...]
    decision_rule_ref: str
    fatal_gate_policy_ref: str
    required_gate_policy_ref: str
    unknown_policy_ref: str

    def __post_init__(self) -> None:
        _freeze_attr(self, "gates")
        _require_pattern(self.gateset_id, _GATESET_ID, "gateset_id")
        _require_text(self.gateset_version, "gateset_version")
        _require_choice(self.candidate_level, CANDIDATE_LEVELS, "candidate_level")
        if not isinstance(self.gates, tuple) or not all(
            isinstance(member, GateSetMember) for member in self.gates
        ):
            raise ValueError("gates must be a sequence of GateSetMember")
        if not self.gates:
            raise ValueError("a GateSet must have at least one gate")
        for name in (
            "decision_rule_ref",
            "fatal_gate_policy_ref",
            "required_gate_policy_ref",
            "unknown_policy_ref",
        ):
            _require_external_ref(getattr(self, name), name)


# --- Decision (exact parity: data_layout/decision.schema.json) -------------

@dataclass(frozen=True)
class TriggeredBy:
    """One ``triggered_by[]`` entry on a Decision."""

    gate_id: str
    assessment_id: str
    assessment_version: int
    reason: str

    def __post_init__(self) -> None:
        _require_text(self.gate_id, "gate_id")
        _require_pattern(self.assessment_id, _ASSESSMENT_ID, "assessment_id")
        _require_positive_int(self.assessment_version, "assessment_version")
        _require_text(self.reason, "reason")


@dataclass(frozen=True)
class Decision:
    """GateSet-level Decision over one Candidate's assessments. Never produced by
    a single Gate. Canonical DEC-*.json is HUMAN_APPROVED only and immutable."""

    decision_id: str
    instantiation_id: str
    candidate_id: str
    gateset_id: str
    gateset_version: str
    decision: str
    triggered_by: tuple[TriggeredBy, ...]
    assessment_snapshot: Mapping[str, object]
    decision_rule_ref: str
    review: Mapping[str, str]
    supersedes_decision_id: str = ""

    def __post_init__(self) -> None:
        _freeze_attr(self, "triggered_by")
        _freeze_attr(self, "assessment_snapshot")
        _freeze_attr(self, "review")

        _require_pattern(self.decision_id, _DECISION_ID, "decision_id")
        _require_pattern(self.instantiation_id, _INSTANTIATION_ID, "instantiation_id")
        _require_pattern(self.candidate_id, _CANDIDATE_ID, "candidate_id")
        _require_pattern(self.gateset_id, _GATESET_ID, "gateset_id")
        _require_text(self.gateset_version, "gateset_version")
        _require_choice(self.decision, DECISION_VALUES, "decision")

        if not isinstance(self.triggered_by, tuple) or not all(
            isinstance(item, TriggeredBy) for item in self.triggered_by
        ):
            raise ValueError("triggered_by must be a sequence of TriggeredBy")

        if not isinstance(self.assessment_snapshot, Mapping) or not self.assessment_snapshot:
            raise ValueError("assessment_snapshot must be a non-empty mapping")
        for gate_id, value in self.assessment_snapshot.items():
            if not isinstance(gate_id, str) or not gate_id.strip():
                raise ValueError("assessment_snapshot keys must be non-empty gate ids")
            if value == "NOT_EVALUATED":
                continue
            _check_block(
                value,
                name=f"assessment_snapshot[{gate_id}]",
                required=_SNAPSHOT_REF_KEYS,
            )
            _require_pattern(
                value["assessment_id"], _ASSESSMENT_ID,
                f"assessment_snapshot[{gate_id}].assessment_id",
            )
            if not _is_int(value["assessment_version"]) or value["assessment_version"] < 1:
                raise ValueError(
                    f"assessment_snapshot[{gate_id}].assessment_version must be int >= 1"
                )
            if not _CELL.match(str(value["cell"])):
                raise ValueError(
                    f"assessment_snapshot[{gate_id}].cell does not match {_CELL.pattern}"
                )

        _require_external_ref(self.decision_rule_ref, "decision_rule_ref")

        _check_block(self.review, name="review", required=_REVIEW_KEYS)
        if self.review["status"] != CANONICAL_REVIEW_STATUS:
            raise ValueError(
                f"canonical decision review.status must be {CANONICAL_REVIEW_STATUS!r}"
            )
        _require_str(self.review["reviewer"], "review.reviewer")
        _require_str(self.review["reviewed_at"], "review.reviewed_at")
        if not _ISO_DATE_PREFIX.match(self.review["reviewed_at"]):
            raise ValueError("review.reviewed_at must start with an ISO date")

        if self.supersedes_decision_id:
            _require_pattern(
                self.supersedes_decision_id, _DECISION_ID, "supersedes_decision_id"
            )


# --- Introspection helpers (used by the parity test) -----------------------

GATE_CONTRACT_OBJECTS: Final[tuple[type, ...]] = (
    EvidenceLadder,
    Gate,
    GateSet,
    Decision,
)


def field_names(object_type: type) -> tuple[str, ...]:
    """Return the declared field names of a gate-model dataclass."""

    return tuple(f.name for f in fields(object_type))
