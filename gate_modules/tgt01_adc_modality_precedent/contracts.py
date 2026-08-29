"""Frozen input / output contracts for MOD-TGT01.

Runtime Migration PR E2. These are in-memory contract values handed between the
deterministic scientific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments. The canonical
``CandidateGateAssessment`` (PR A, ``CANONICAL_REVIEW_STATUS = HUMAN_APPROVED``)
is built only by the human review surface, never here -- so this module emits an
``AssessmentProposalEnvelope`` that carries the canonical assessment *identity
pins* and scientific fields for a deterministic canonicalisation, and omits
``assessment_id`` / ``assessment_version`` / ``review``.

Review round 1 (ChatGPT AI审核方案):
* the candidate's canonical target identity is the single authoritative source;
  a precedent record carries the ADC program's *actual* target antigen and, for
  an adjacent target, an auditable relation basis;
* the frozen item-08 fatal condition has two branches -- target-mediated
  toxicity AND an intrinsically unachievable therapeutic window -- and a pattern
  needs >= 2 independent programs failing for the *same* frozen adverse class;
* an EvidencePackage is Gate-NEUTRAL (observation-level meaning only); the
  TGT-01 ceiling / inference / direction live in the proposal layer;
* an existing canonical EvidencePackage is reused by id, never re-created;
* each observation maps to exactly one EvidencePackage (not keyed by program).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields
from typing import Final

from src.objects.decision_model import (
    CRITICAL_UNKNOWN_RESOLUTIONS,
    DIRECTION_VALUES,
    EVIDENCE_ROLE_VALUES,
    GRADED_STRENGTHS,
    SOURCE_TYPE_VALUES,
    STRENGTH_VALUES,
    EvidencePackage,
)

# --- identity -----------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT01"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-01"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-01 contract. Reproduced by the PROPOSAL
#: layer -- never stamped onto a Gate-neutral EvidencePackage.
TGT01_EVIDENCE_CEILING: Final[str] = (
    "clinical-stage ADC precedent against the same target antigen"
)
TGT01_GATE_QUESTION: Final[str] = (
    "Is there prior precedent that this target (or a biologically adjacent "
    "target in its lineage) is addressable by the ADC modality?"
)

#: PR A identity patterns (parity, not imported private symbols).
_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ------------------------------------------------------------------

TARGET_RELATION_VALUES: Final[tuple[str, ...]] = ("SAME_TARGET", "ADJACENT_TARGET")

#: Ordered strongest -> weakest; used only to pick the highest rung actually met.
PROGRAM_STAGE_VALUES: Final[tuple[str, ...]] = (
    "APPROVED",
    "PHASE_3",
    "PHASE_2",
    "PHASE_1",
    "PRECLINICAL",
    "PATENT_OR_DISCLOSURE",
)
PROGRAM_STATUS_VALUES: Final[tuple[str, ...]] = (
    "ACTIVE",
    "DISCONTINUED",
    "COMPLETED",
    "UNKNOWN",
)
#: The two frozen item-08 TARGET-ATTRIBUTABLE failure branches, plus the
#: non-target-attributable classes. Empty means not a discontinued program.
FAILURE_ATTRIBUTION_VALUES: Final[tuple[str, ...]] = (
    "",
    "TARGET_MEDIATED_TOXICITY",
    "INTRINSIC_THERAPEUTIC_WINDOW",
    "CONSTRUCT_SPECIFIC",
    "NON_TARGET",
    "UNDISCLOSED",
)
#: A fatal / adverse pattern needs >= 2 independent same-target programs that
#: failed for the SAME one of these (frozen item 08). Mixed classes do not form
#: a consistent pattern.
TARGET_ATTRIBUTABLE_FAILURE_CLASSES: Final[frozenset[str]] = frozenset(
    {"TARGET_MEDIATED_TOXICITY", "INTRINSIC_THERAPEUTIC_WINDOW"}
)

#: The proposal envelope must never carry these -- assigned by the human
#: canonicalisation step, not by the module.
CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

LATE_CLINICAL_STAGES: Final[frozenset[str]] = frozenset({"APPROVED", "PHASE_3", "PHASE_2"})


# --- tiny local validators ------------------------------------------------------

def _text(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{name} must be a non-empty string")


def _pattern(value: object, rx: "re.Pattern[str]", name: str) -> None:
    if not isinstance(value, str) or not rx.match(value):
        raise ValueError(f"{name} does not match {rx.pattern}")


def _choice(value: object, allowed: tuple[str, ...], name: str) -> None:
    if value not in allowed:
        raise ValueError(f"{name} must be one of {allowed}, got {value!r}")


def _positive_int(value: object, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def _bool(value: object, name: str) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a bool")


# --- canonical source record (resolved through the SourceResolverPort) --------

@dataclass(frozen=True)
class CanonicalSourceRecord:
    """The authoritative provenance for a ``SRC-nnnnnnnn`` id, resolved from the
    PR C SourceIndex. Its metadata -- not the provider's raw fields -- is what
    the EvidencePackage's provenance block carries."""

    source_id: str
    source_type: str
    source_identifier: str
    locator: str = ""

    def __post_init__(self) -> None:
        _pattern(self.source_id, _SRC_ID, "source_id")
        _choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _text(self.source_identifier, "source_identifier")
        _text(self.locator, "locator", allow_empty=True)


# --- provider output ----------------------------------------------------------

@dataclass(frozen=True)
class NormalizedPrecedentRecord:
    """One already-normalized ADC precedent observation from the provider.

    The provider (not this module) resolved the row to a primary source and
    normalised it. ``failure_attribution`` is one of the frozen classes and may
    be a TARGET-ATTRIBUTABLE class only with an explicit primary-source
    disclosure (``failure_attribution_from_primary_source``). The module never
    runs free-text NLP.
    """

    observation_id: str
    program_id: str
    program_target_identity: str
    target_relation: str
    adjacency_basis: str
    program_stage: str
    program_status: str
    clinical_activity_disclosed: bool
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    primary_source_resolved: bool
    failure_reason: str = ""
    failure_attribution: str = ""
    failure_attribution_from_primary_source: bool = False

    def __post_init__(self) -> None:
        _pattern(self.observation_id, _OBS_ID, "observation_id")
        _text(self.program_id, "program_id")
        _text(self.program_target_identity, "program_target_identity")
        _choice(self.target_relation, TARGET_RELATION_VALUES, "target_relation")
        _text(self.adjacency_basis, "adjacency_basis", allow_empty=True)
        if self.target_relation == "ADJACENT_TARGET" and not self.adjacency_basis.strip():
            raise ValueError(
                "an ADJACENT_TARGET record must carry an auditable adjacency_basis"
            )
        if self.target_relation == "SAME_TARGET" and self.adjacency_basis.strip():
            raise ValueError("a SAME_TARGET record carries no adjacency_basis")
        _choice(self.program_stage, PROGRAM_STAGE_VALUES, "program_stage")
        _choice(self.program_status, PROGRAM_STATUS_VALUES, "program_status")
        _bool(self.clinical_activity_disclosed, "clinical_activity_disclosed")
        _text(self.claim, "claim")
        _pattern(self.source_id, _SRC_ID, "source_id")
        _choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _text(self.source_identifier, "source_identifier")
        _text(self.locator, "locator", allow_empty=True)
        _text(self.retrieved_at, "retrieved_at")
        if not _ISO_DATE_PREFIX.match(self.retrieved_at):
            raise ValueError("retrieved_at must start with an ISO date")
        _bool(self.primary_source_resolved, "primary_source_resolved")
        _text(self.failure_reason, "failure_reason", allow_empty=True)
        _choice(self.failure_attribution, FAILURE_ATTRIBUTION_VALUES, "failure_attribution")
        _bool(
            self.failure_attribution_from_primary_source,
            "failure_attribution_from_primary_source",
        )
        if self.failure_attribution and self.program_status != "DISCONTINUED":
            raise ValueError(
                "failure_attribution is only meaningful for a DISCONTINUED program"
            )
        if (
            self.failure_attribution in TARGET_ATTRIBUTABLE_FAILURE_CLASSES
            and not self.failure_attribution_from_primary_source
        ):
            raise ValueError(
                f"{self.failure_attribution} attribution requires "
                "failure_attribution_from_primary_source=True (an explicit "
                "primary-source disclosure); the module does not infer it"
            )

    @property
    def is_same_target(self) -> bool:
        return self.target_relation == "SAME_TARGET"

    @property
    def is_target_attributable_failure(self) -> bool:
        return (
            self.program_status == "DISCONTINUED"
            and self.failure_attribution in TARGET_ATTRIBUTABLE_FAILURE_CLASSES
            and self.failure_attribution_from_primary_source
        )


# --- module input -----------------------------------------------------------

@dataclass(frozen=True)
class Tgt01ModuleInput:
    """Everything the module needs to run one (candidate, TGT-01) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the
    SINGLE authoritative identity. The provider is queried with it and every
    SAME_TARGET record must match it. No implicit default scientific context.
    """

    candidate_id: str
    candidate_name: str
    target_identity: str
    instantiation_id: str
    context_id: str
    context_version: int
    gateset_id: str
    gateset_version: str
    gate_id: str
    gate_version: str
    evidence_regime: str
    run_id: str
    code_commit: str
    retrieval_window: str = ""
    existing_evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _text(self.candidate_name, "candidate_name")
        _text(self.target_identity, "target_identity")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        if self.instantiation_id != INSTANTIATION_ID:
            raise ValueError(
                f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT01"
            )
        _pattern(self.context_id, _CTX_ID, "context_id")
        _positive_int(self.context_version, "context_version")
        if self.gateset_id != GATESET_ID:
            raise ValueError(f"gateset_id must be {GATESET_ID!r}")
        if self.gateset_version != GATESET_VERSION:
            raise ValueError(f"gateset_version must be {GATESET_VERSION!r}")
        if self.gate_id != GATE_ID:
            raise ValueError(f"gate_id must be {GATE_ID!r}")
        if self.gate_version != GATE_VERSION:
            raise ValueError(f"gate_version must be {GATE_VERSION!r}")
        if self.evidence_regime != "PUBLIC_ONLY":
            raise ValueError("evidence_regime must be PUBLIC_ONLY for TGT-01")
        _text(self.run_id, "run_id")
        _text(self.code_commit, "code_commit", allow_empty=True)
        _text(self.retrieval_window, "retrieval_window", allow_empty=True)
        if not isinstance(self.existing_evidence_ids, tuple) or not all(
            isinstance(x, str) and _EP_ID.match(x) for x in self.existing_evidence_ids
        ):
            raise ValueError("existing_evidence_ids must be a tuple of EP-nnnnnnnn ids")

    @property
    def identity_pins(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "instantiation_id": self.instantiation_id,
            "context_id": self.context_id,
            "context_version": self.context_version,
            "gateset_id": self.gateset_id,
            "gateset_version": self.gateset_version,
            "gate_id": self.gate_id,
            "gate_version": self.gate_version,
        }


# --- classification ---------------------------------------------------------

@dataclass(frozen=True)
class ClassifiedPrecedent:
    """A provider record placed against the frozen TGT-01 Evidence Ladder."""

    record: NormalizedPrecedentRecord
    admissible: bool
    rejection_reason: str
    ladder_rung: str  # "", DIRECT, INDIRECT_STRONG, WEAK
    evidence_class: str
    direction_role: str  # SUPPORTING, ADVERSE_CANDIDATE, CONTEXTUAL
    contributes_adverse_signal: bool
    adverse_class: str  # "" unless ADVERSE_CANDIDATE; then a frozen item-08 class

    def __post_init__(self) -> None:
        _bool(self.admissible, "admissible")
        _text(self.rejection_reason, "rejection_reason", allow_empty=True)
        _choice(
            self.direction_role,
            ("SUPPORTING", "ADVERSE_CANDIDATE", "CONTEXTUAL"),
            "direction_role",
        )
        _bool(self.contributes_adverse_signal, "contributes_adverse_signal")
        if self.admissible:
            if self.ladder_rung not in GRADED_STRENGTHS:
                raise ValueError("an admissible record has a graded directness rung")
            _text(self.evidence_class, "evidence_class")
        elif self.ladder_rung != "":
            raise ValueError("a rejected record has no ladder rung")
        if self.admissible and self.rejection_reason:
            raise ValueError("an admissible record carries no rejection_reason")
        if not self.admissible and not self.rejection_reason:
            raise ValueError("a rejected record must state a rejection_reason")
        if self.contributes_adverse_signal:
            if self.direction_role != "ADVERSE_CANDIDATE":
                raise ValueError(
                    "contributes_adverse_signal is only set on an ADVERSE_CANDIDATE"
                )
            if self.adverse_class not in TARGET_ATTRIBUTABLE_FAILURE_CLASSES:
                raise ValueError(
                    "an ADVERSE_CANDIDATE carries a frozen item-08 adverse_class"
                )
        elif self.adverse_class:
            raise ValueError("adverse_class is set only on an ADVERSE_CANDIDATE")

    @property
    def establishes_precedent(self) -> bool:
        return self.admissible and self.direction_role == "SUPPORTING"


# --- emitted evidence (one observation -> one package) -----------------------

@dataclass(frozen=True)
class EmittedEvidence:
    """A single admissible observation and the EvidencePackage it maps to.

    The mapping is one observation -> one package (never keyed by program_id --
    a program with two distinct primary-source observations gets two packages).
    ``reused`` is True when the id came from the existing Evidence Library
    rather than the allocator.
    """

    classified: ClassifiedPrecedent
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedPrecedent):
            raise ValueError("classified must be a ClassifiedPrecedent")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")


# --- proposal envelope (E1 item 12) ---------------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Mirrors the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` (human only)."""

    candidate_id: str
    instantiation_id: str
    context_id: str
    context_version: int
    gateset_id: str
    gateset_version: str
    gate_id: str
    gate_version: str
    proposed_direction: str
    proposed_strength: str
    evidence_refs: tuple[tuple[str, str], ...]
    aggregation_rationale: str
    critical_unknowns: tuple[tuple[str, str], ...]
    evidence_ceiling: str

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        _pattern(self.context_id, _CTX_ID, "context_id")
        _positive_int(self.context_version, "context_version")
        if self.gateset_id != GATESET_ID:
            raise ValueError(f"gateset_id must be {GATESET_ID!r}")
        _text(self.gateset_version, "gateset_version")
        if self.gate_id != GATE_ID:
            raise ValueError(f"gate_id must be {GATE_ID!r}")
        _text(self.gate_version, "gate_version")
        _choice(self.proposed_direction, DIRECTION_VALUES, "proposed_direction")
        _choice(self.proposed_strength, STRENGTH_VALUES, "proposed_strength")
        seen_refs: set[str] = set()
        for evidence_id, role in self.evidence_refs:
            _pattern(evidence_id, _EP_ID, "evidence_refs.evidence_id")
            _choice(role, EVIDENCE_ROLE_VALUES, "evidence_refs.role")
            if evidence_id in seen_refs:
                raise ValueError(f"evidence_ref {evidence_id} appears more than once")
            seen_refs.add(evidence_id)
        _text(self.aggregation_rationale, "aggregation_rationale")
        for unknown, resolution in self.critical_unknowns:
            _text(unknown, "critical_unknowns.unknown")
            _choice(resolution, CRITICAL_UNKNOWN_RESOLUTIONS, "critical_unknowns.resolution")
        if self.evidence_ceiling != TGT01_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-01 ceiling verbatim")
        if self.proposed_direction in ("POSITIVE", "NEGATIVE") and not self.evidence_refs:
            raise ValueError("POSITIVE / NEGATIVE proposal needs >= 1 evidence_ref")
        if self.proposed_direction == "CONFLICTING":
            roles = {role for _, role in self.evidence_refs}
            if not {"SUPPORTING", "CONTRADICTING"} <= roles:
                raise ValueError(
                    "CONFLICTING proposal needs >= 1 SUPPORTING and >= 1 CONTRADICTING ref"
                )
        if (self.proposed_direction == "INCONCLUSIVE" and self.proposed_strength == "UNKNOWN"
                and self.evidence_refs):
            raise ValueError("the UNKNOWN state carries no evidence_refs")

    @classmethod
    def field_names(cls) -> tuple[str, ...]:
        return tuple(f.name for f in fields(cls))


# --- machine acceptance + stop-rule sweep -------------------------------------

@dataclass(frozen=True)
class SweepCompletionRecord:
    """The two E1 item-16 stop-rule prerequisites, reported by the provider /
    external runtime -- the module does not run a search scheduler."""

    same_target_program_inventory_complete: bool
    failure_reason_sweep_complete: bool

    def __post_init__(self) -> None:
        _bool(
            self.same_target_program_inventory_complete,
            "same_target_program_inventory_complete",
        )
        _bool(self.failure_reason_sweep_complete, "failure_reason_sweep_complete")

    @property
    def mandatory_completion_satisfied(self) -> bool:
        return (
            self.same_target_program_inventory_complete
            and self.failure_reason_sweep_complete
        )


@dataclass(frozen=True)
class MachineAcceptanceRecord:
    """E1 item 13 machine acceptance, plus the item-16 completion prerequisite."""

    accepted: bool
    checks: tuple[tuple[str, bool], ...]
    reasons: tuple[str, ...]
    module_id: str
    module_version: str
    run_id: str

    def __post_init__(self) -> None:
        _bool(self.accepted, "accepted")
        for name, ok in self.checks:
            _text(name, "checks.name")
            _bool(ok, "checks.value")
        for reason in self.reasons:
            _text(reason, "reasons[]")
        if self.module_id != MODULE_ID:
            raise ValueError(f"module_id must be {MODULE_ID!r}")
        if self.module_version != MODULE_VERSION:
            raise ValueError(f"module_version must be {MODULE_VERSION!r}")
        _text(self.run_id, "run_id")
        if self.accepted and self.reasons:
            raise ValueError("an accepted run carries no failure reasons")
        if not self.accepted and not self.reasons:
            raise ValueError("a rejected run must state at least one reason")
        if self.accepted and not all(ok for _, ok in self.checks):
            raise ValueError("an accepted run cannot carry a failing check")


# --- run result -------------------------------------------------------------

@dataclass(frozen=True)
class Tgt01ModuleRunResult:
    """Everything MOD-TGT01 hands to the human review surface. In-memory only;
    no canonical CandidateGateAssessment, no Decision, no persistence."""

    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    sweep_completion: SweepCompletionRecord
    rejected_records: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if self.module_id != MODULE_ID:
            raise ValueError(f"module_id must be {MODULE_ID!r}")
        if self.module_version != MODULE_VERSION:
            raise ValueError(f"module_version must be {MODULE_VERSION!r}")
        if self.gate_id != GATE_ID:
            raise ValueError(f"gate_id must be {GATE_ID!r}")
        _text(self.run_id, "run_id")
        if not all(isinstance(ep, EvidencePackage) for ep in self.evidence_packages):
            raise ValueError("evidence_packages must all be EvidencePackage")
        ep_ids = [ep.evidence_id for ep in self.evidence_packages]
        if len(ep_ids) != len(set(ep_ids)):
            raise ValueError("evidence_packages must not repeat an evidence_id")
        for reused in self.reused_evidence_ids:
            _pattern(reused, _EP_ID, "reused_evidence_ids[]")
            if reused not in ep_ids:
                raise ValueError("a reused_evidence_id must be in evidence_packages")
        if self.proposal_envelope is not None and not isinstance(
            self.proposal_envelope, AssessmentProposalEnvelope
        ):
            raise ValueError("proposal_envelope must be an AssessmentProposalEnvelope")
        if not isinstance(self.machine_acceptance, MachineAcceptanceRecord):
            raise ValueError("machine_acceptance must be a MachineAcceptanceRecord")
        if not isinstance(self.sweep_completion, SweepCompletionRecord):
            raise ValueError("sweep_completion must be a SweepCompletionRecord")
        for program_id, reason in self.rejected_records:
            _text(program_id, "rejected_records.program_id")
            _text(reason, "rejected_records.reason")
        if self.proposal_envelope is not None and not self.machine_acceptance.accepted:
            raise ValueError("a proposal envelope requires an accepted machine record")
        if self.proposal_envelope is None and self.machine_acceptance.accepted:
            raise ValueError("an accepted machine record must carry a proposal envelope")
        # every proposal evidence_ref points at an emitted package
        if self.proposal_envelope is not None:
            for evidence_id, _ in self.proposal_envelope.evidence_refs:
                if evidence_id not in ep_ids:
                    raise ValueError(
                        "proposal evidence_ref does not resolve to an emitted package"
                    )
