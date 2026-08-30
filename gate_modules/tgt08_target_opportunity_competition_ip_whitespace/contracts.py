"""Frozen input / output contracts for MOD-TGT08.

Runtime Migration PR E6. In-memory contract values handed between the
deterministic Gate-specific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments.

Three invariants this module must never break (ChatGPT AI审核方案 E6):

1. Empty results are not whitespace. Only an AUDITED completion (attempted +
   coverage_complete + a provenance-bearing SEARCH_COMPLETION_AUDIT observation
   + qualifying set == 0) can support an absence inference. Never ``if not
   records: supports_opportunity = True``.
2. TGT-08 NEGATIVE is a Gate-relative opportunity judgement -- current public
   opportunity evidence weighs against a differentiated entry. It is never a
   KILL, STOP_FOR_SPONSOR, OUT_OF_MANDATE, a scientific verdict on the target,
   or an FTO-blocked finding.
3. ``sponsor_review`` is a review TRIGGER. The machine detects a pattern; the
   sponsor decides what it means. The machine never asserts "dominant",
   "well protected", "no differentiation path", or "this sponsor should stop".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields
from typing import Final

from src.objects.decision_model import (
    CRITICAL_UNKNOWN_RESOLUTIONS,
    DIRECTION_VALUES,
    EVIDENCE_ROLE_VALUES,
    SOURCE_TYPE_VALUES,
    STRENGTH_VALUES,
    EvidencePackage,
)

# --- identity ---------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT08"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-08"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-08 contract. Reproduced only by the PROPOSAL
#: layer -- never stamped onto a Gate-neutral EvidencePackage.
TGT08_EVIDENCE_CEILING: Final[str] = (
    "primary-source competitive and regulatory landscape for the target in mCRC "
    "plus a composition-level patent-landscape review"
)
TGT08_GATE_QUESTION: Final[str] = (
    "Is there a differentiated opportunity for this target in refractory mCRC: "
    "unmet need, competitive landscape, and IP whitespace signals?"
)

_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ----------------------------------------------------------------

#: Which of the frozen E5 evidence axes a normalized record belongs to.
EVIDENCE_AXIS_VALUES: Final[tuple[str, ...]] = ("COMPETITIVE", "PATENT", "UNMET_NEED")

#: What a normalized record IS. The provider supplies facts only -- it never
#: sets a rung, a direction, or an opportunity implication.
OBSERVATION_KIND_VALUES: Final[tuple[str, ...]] = (
    "COMPETITOR_PROGRAM",
    "PATENT_CLAIM",
    "UNMET_NEED_CONTEXT",
    "SEARCH_COMPLETION_AUDIT",
)

#: Factual provenance authority the provider normalizes to; the module maps it
#: to an axis authority ceiling deterministically (E6-2 / E6-3).
SOURCE_AUTHORITY_KIND_VALUES: Final[tuple[str, ...]] = (
    "TRIAL_REGISTRY",
    "REGULATORY_SOURCE",
    "COMPANY_PRIMARY_DISCLOSURE",
    "PRIMARY_CLINICAL_PUBLICATION",
    "PIPELINE_DATABASE",
    "PATENT_PUBLICATION",
    "OFFICIAL_PATENT_STATUS",
    "PATENT_SEARCH_INDEX",
    "INDICATION_OUTCOME_SOURCE",
    "SEARCH_AUDIT",
)

#: Primary-source authority for the competitive axis; a PIPELINE_DATABASE row is
#: an index only and caps the axis at INDIRECT_STRONG (E5 item 09).
_COMPETITIVE_PRIMARY_AUTHORITIES: Final[tuple[str, ...]] = (
    "TRIAL_REGISTRY",
    "REGULATORY_SOURCE",
    "COMPANY_PRIMARY_DISCLOSURE",
    "PRIMARY_CLINICAL_PUBLICATION",
)
_PATENT_PRIMARY_AUTHORITIES: Final[tuple[str, ...]] = (
    "PATENT_PUBLICATION",
    "OFFICIAL_PATENT_STATUS",
)

MODALITY_VALUES: Final[tuple[str, ...]] = (
    "",
    "ADC",
    "CAR_T",
    "T_CELL_ENGAGER",
    "NAKED_ANTIBODY",
    "RADIOLIGAND",
    "BISPECIFIC",
    "SMALL_MOLECULE",
    "OTHER",
)
PROGRAM_STAGE_VALUES: Final[tuple[str, ...]] = (
    "",
    "APPROVED",
    "REGISTRATIONAL",
    "ACTIVE_CLINICAL",
    "EARLY_CLINICAL",
    "PRECLINICAL",
)
PROGRAM_STATUS_VALUES: Final[tuple[str, ...]] = (
    "",
    "ACTIVE",
    "COMPLETED",
    "DISCONTINUED",
    "FAILED",
    "UNKNOWN",
)
#: Competitor stages that oppose a differentiated opportunity (E6-4).
_OPPOSING_STAGES: Final[tuple[str, ...]] = ("APPROVED", "REGISTRATIONAL", "ACTIVE_CLINICAL")
#: A dead program status makes a competitor CONTEXTUAL regardless of stage.
_DEAD_STATUSES: Final[tuple[str, ...]] = ("DISCONTINUED", "FAILED")

LEGAL_STATUS_VALUES: Final[tuple[str, ...]] = (
    "",
    "LIVE",
    "PENDING",
    "EXPIRED",
    "ABANDONED",
    "CANCELLED",
    "LAPSED",
    "UNKNOWN",
)
_LIVE_LEGAL_STATUSES: Final[tuple[str, ...]] = ("LIVE", "PENDING")
_DEAD_LEGAL_STATUSES: Final[tuple[str, ...]] = ("EXPIRED", "ABANDONED", "CANCELLED", "LAPSED")

CLAIM_CATEGORY_VALUES: Final[tuple[str, ...]] = (
    "",
    "ADC_COMPOSITION",
    "ANTIBODY",
    "LINKER",
    "PAYLOAD",
    "CONJUGATE",
    "FORMULATION",
    "TARGET_BINDING",
    "METHOD_OF_USE",
    "OTHER",
    "IRRELEVANT",
)
#: Claim categories that count as a composition-level ADC claim.
_ADC_COMPOSITION_CLAIM_CATEGORIES: Final[tuple[str, ...]] = (
    "ADC_COMPOSITION",
    "ANTIBODY",
    "LINKER",
    "PAYLOAD",
    "CONJUGATE",
    "FORMULATION",
    "TARGET_BINDING",
)

#: Module-assigned Gate-relative interpretation of an atomic landscape fact.
OPPORTUNITY_IMPLICATION_VALUES: Final[tuple[str, ...]] = (
    "",
    "SUPPORTS_OPPORTUNITY",
    "OPPOSES_OPPORTUNITY",
    "CONTEXTUAL",
)
_IMPLICATION_TO_ROLE: Final[dict[str, str]] = {
    "SUPPORTS_OPPORTUNITY": "SUPPORTING",
    "OPPOSES_OPPORTUNITY": "CONTRADICTING",
    "CONTEXTUAL": "CONTEXTUAL",
}

#: Per-axis authority ceiling the module derives from a completion state.
AXIS_CEILING_VALUES: Final[tuple[str, ...]] = ("DIRECT", "INDIRECT_STRONG", "NOT_EVALUABLE")

SPONSOR_REVIEW_STATUS_VALUES: Final[tuple[str, ...]] = ("", "POTENTIAL_SPONSOR_FATAL_PATTERN")

CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

#: The only Direction x Strength pairs MOD-TGT08 may propose (E6-3).
LEGAL_DIRECTION_STRENGTH_PAIRS: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("POSITIVE", "DIRECT"),
        ("POSITIVE", "INDIRECT_STRONG"),
        ("NEGATIVE", "DIRECT"),
        ("NEGATIVE", "INDIRECT_STRONG"),
        ("CONFLICTING", "DIRECT"),
        ("CONFLICTING", "INDIRECT_STRONG"),
        ("INCONCLUSIVE", "DIRECT"),
        ("INCONCLUSIVE", "INDIRECT_STRONG"),
        ("INCONCLUSIVE", "WEAK"),
        ("INCONCLUSIVE", "UNKNOWN"),
    }
)

_CEILING_RANK: Final[dict[str, int]] = {
    "DIRECT": 2,
    "INDIRECT_STRONG": 1,
    "NOT_EVALUABLE": 0,
}


# --- tiny local validators -----------------------------------------------------

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


def _str_tuple(value: object, name: str) -> None:
    if not isinstance(value, tuple) or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f"{name} must be a tuple of non-empty strings")


# --- canonical source record ------------------------------------------------

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


# --- provider output: normalized landscape fact ----------------------------

@dataclass(frozen=True)
class NormalizedOpportunityRecord:
    """One already-normalized, primary/official-source-resolved TGT-08
    landscape observation. FACTS only -- the provider never sets an axis
    ceiling, a direction, or an opportunity implication (E6-2)."""

    observation_id: str
    target_identity: str
    evidence_axis: str
    observation_kind: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    source_authority_kind: str
    primary_or_official_source_resolved: bool
    context_key: str
    landscape_as_of: str
    # competitive-specific
    program_id: str = ""
    modality: str = ""
    program_stage: str = ""
    program_status: str = ""
    indication_context_key: str = ""
    failure_reason_disclosed: str = ""
    # patent-specific
    patent_family_id: str = ""
    patent_publication_id: str = ""
    assignee: str = ""
    jurisdiction: str = ""
    claim_category: str = ""
    legal_status: str = ""
    composition_level: bool = False

    def __post_init__(self) -> None:
        _pattern(self.observation_id, _OBS_ID, "observation_id")
        _text(self.target_identity, "target_identity")
        _choice(self.evidence_axis, EVIDENCE_AXIS_VALUES, "evidence_axis")
        _choice(self.observation_kind, OBSERVATION_KIND_VALUES, "observation_kind")
        _text(self.claim, "claim")
        _pattern(self.source_id, _SRC_ID, "source_id")
        _choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _text(self.source_identifier, "source_identifier")
        _text(self.locator, "locator", allow_empty=True)
        _text(self.retrieved_at, "retrieved_at")
        if not _ISO_DATE_PREFIX.match(self.retrieved_at):
            raise ValueError("retrieved_at must start with an ISO date")
        _choice(self.source_authority_kind, SOURCE_AUTHORITY_KIND_VALUES, "source_authority_kind")
        _bool(self.primary_or_official_source_resolved, "primary_or_official_source_resolved")
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _choice(self.modality, MODALITY_VALUES, "modality")
        _choice(self.program_stage, PROGRAM_STAGE_VALUES, "program_stage")
        _choice(self.program_status, PROGRAM_STATUS_VALUES, "program_status")
        _choice(self.claim_category, CLAIM_CATEGORY_VALUES, "claim_category")
        _choice(self.legal_status, LEGAL_STATUS_VALUES, "legal_status")
        _bool(self.composition_level, "composition_level")
        for name in ("program_id", "indication_context_key", "failure_reason_disclosed",
                     "patent_family_id", "patent_publication_id", "assignee",
                     "jurisdiction"):
            _text(getattr(self, name), name, allow_empty=True)

        # cross-field shape by observation kind
        if self.observation_kind == "COMPETITOR_PROGRAM":
            if self.evidence_axis != "COMPETITIVE":
                raise ValueError("a COMPETITOR_PROGRAM record is on the COMPETITIVE axis")
            for req in ("program_id", "modality", "program_stage", "program_status",
                        "indication_context_key"):
                if not getattr(self, req).strip():
                    raise ValueError(f"COMPETITOR_PROGRAM record needs a non-empty {req}")
        elif self.observation_kind == "PATENT_CLAIM":
            if self.evidence_axis != "PATENT":
                raise ValueError("a PATENT_CLAIM record is on the PATENT axis")
            for req in ("patent_family_id", "patent_publication_id", "jurisdiction",
                        "claim_category", "legal_status"):
                if not getattr(self, req).strip():
                    raise ValueError(f"PATENT_CLAIM record needs a non-empty {req}")
        elif self.observation_kind == "UNMET_NEED_CONTEXT":
            if self.evidence_axis != "UNMET_NEED":
                raise ValueError("an UNMET_NEED_CONTEXT record is on the UNMET_NEED axis")
        elif self.observation_kind == "SEARCH_COMPLETION_AUDIT":
            if self.evidence_axis not in ("COMPETITIVE", "PATENT"):
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT record is on the COMPETITIVE or PATENT axis"
                )
            if self.source_authority_kind != "SEARCH_AUDIT":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT record carries source_authority_kind SEARCH_AUDIT"
                )

    # --- factual predicates (field reads only, no interpretation) -----------
    @property
    def is_same_indication_context(self) -> bool:
        return bool(self.indication_context_key.strip()) and (
            self.indication_context_key.strip() == self.context_key.strip()
        )

    @property
    def is_adc(self) -> bool:
        return self.modality == "ADC"

    @property
    def competitor_stage_opposes(self) -> bool:
        return self.program_stage in _OPPOSING_STAGES

    @property
    def competitor_status_dead(self) -> bool:
        return self.program_status in _DEAD_STATUSES

    @property
    def patent_is_live(self) -> bool:
        return self.legal_status in _LIVE_LEGAL_STATUSES

    @property
    def patent_is_dead(self) -> bool:
        return self.legal_status in _DEAD_LEGAL_STATUSES

    @property
    def patent_is_composition_level_adc_claim(self) -> bool:
        return (
            self.composition_level
            and self.claim_category in _ADC_COMPOSITION_CLAIM_CATEGORIES
        )

    @property
    def competitive_axis_primary_authority(self) -> bool:
        return self.source_authority_kind in _COMPETITIVE_PRIMARY_AUTHORITIES

    @property
    def patent_axis_primary_authority(self) -> bool:
        return self.source_authority_kind in _PATENT_PRIMARY_AUTHORITIES


# --- module-local typed completion states (E6-3) --------------------------

@dataclass(frozen=True)
class CompetitiveLandscapeCompletion:
    """A module-local run record -- NOT a core object, EvidencePackage,
    Assessment or Decision. The provider states search facts; the module
    derives the axis authority ceiling and hard-checks consistency against the
    emitted competitor evidence."""

    attempted: bool
    coverage_complete: bool
    primary_source_landscape_complete: bool
    pipeline_inventory_complete: bool
    landscape_as_of: str
    search_scope: str
    sources_searched: tuple[str, ...]
    unresolved_items: tuple[str, ...]
    qualifying_program_ids: tuple[str, ...]
    audit_observation_id: str

    def __post_init__(self) -> None:
        _bool(self.attempted, "attempted")
        _bool(self.coverage_complete, "coverage_complete")
        _bool(self.primary_source_landscape_complete, "primary_source_landscape_complete")
        _bool(self.pipeline_inventory_complete, "pipeline_inventory_complete")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _text(self.search_scope, "search_scope", allow_empty=not self.attempted)
        if not isinstance(self.sources_searched, tuple) or not all(
            isinstance(x, str) and x for x in self.sources_searched
        ):
            raise ValueError("sources_searched must be a tuple of non-empty strings")
        if not isinstance(self.unresolved_items, tuple) or not all(
            isinstance(x, str) and x for x in self.unresolved_items
        ):
            raise ValueError("unresolved_items must be a tuple of non-empty strings")
        if not isinstance(self.qualifying_program_ids, tuple) or not all(
            isinstance(x, str) and x for x in self.qualifying_program_ids
        ):
            raise ValueError("qualifying_program_ids must be a tuple of non-empty strings")
        _text(self.audit_observation_id, "audit_observation_id", allow_empty=not self.attempted)
        if self.attempted and self.audit_observation_id:
            _pattern(self.audit_observation_id, _OBS_ID, "audit_observation_id")
        if not self.attempted:
            for name in ("coverage_complete", "primary_source_landscape_complete",
                         "pipeline_inventory_complete"):
                if getattr(self, name):
                    raise ValueError(f"an unattempted competitive axis cannot be {name}")
            if self.sources_searched or self.qualifying_program_ids:
                raise ValueError("an unattempted competitive axis has no searched sources / qualifying ids")
        if self.attempted and self.coverage_complete and not self.audit_observation_id:
            raise ValueError(
                "a coverage-complete competitive axis needs a SEARCH_COMPLETION_AUDIT observation"
            )
        if self.coverage_complete and not self.sources_searched:
            raise ValueError("a coverage-complete competitive axis lists the sources searched")

    @property
    def axis_ceiling(self) -> str:
        if not (self.attempted and self.coverage_complete):
            return "NOT_EVALUABLE"
        if self.primary_source_landscape_complete:
            return "DIRECT"
        if self.pipeline_inventory_complete:
            return "INDIRECT_STRONG"
        return "NOT_EVALUABLE"

    @property
    def evaluable(self) -> bool:
        return self.axis_ceiling in ("DIRECT", "INDIRECT_STRONG")


@dataclass(frozen=True)
class PatentLandscapeCompletion:
    """Module-local run record for the composition-level patent axis (E6-3)."""

    attempted: bool
    coverage_complete: bool
    composition_level_review_complete: bool
    target_level_search_complete: bool
    landscape_as_of: str
    patent_scope: str
    jurisdictions: tuple[str, ...]
    sources_searched: tuple[str, ...]
    unresolved_items: tuple[str, ...]
    qualifying_patent_family_ids: tuple[str, ...]
    audit_observation_id: str

    def __post_init__(self) -> None:
        _bool(self.attempted, "attempted")
        _bool(self.coverage_complete, "coverage_complete")
        _bool(self.composition_level_review_complete, "composition_level_review_complete")
        _bool(self.target_level_search_complete, "target_level_search_complete")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _text(self.patent_scope, "patent_scope", allow_empty=not self.attempted)
        for name in ("jurisdictions", "sources_searched", "unresolved_items",
                     "qualifying_patent_family_ids"):
            v = getattr(self, name)
            if not isinstance(v, tuple) or not all(isinstance(x, str) and x for x in v):
                raise ValueError(f"{name} must be a tuple of non-empty strings")
        _text(self.audit_observation_id, "audit_observation_id", allow_empty=not self.attempted)
        if self.attempted and self.audit_observation_id:
            _pattern(self.audit_observation_id, _OBS_ID, "audit_observation_id")
        if not self.attempted:
            for name in ("coverage_complete", "composition_level_review_complete",
                         "target_level_search_complete"):
                if getattr(self, name):
                    raise ValueError(f"an unattempted patent axis cannot be {name}")
            if self.sources_searched or self.qualifying_patent_family_ids:
                raise ValueError("an unattempted patent axis has no searched sources / qualifying ids")
        if self.attempted and self.coverage_complete and not self.audit_observation_id:
            raise ValueError(
                "a coverage-complete patent axis needs a SEARCH_COMPLETION_AUDIT observation"
            )
        if self.coverage_complete and not self.sources_searched:
            raise ValueError("a coverage-complete patent axis lists the sources searched")
        if self.composition_level_review_complete and not self.jurisdictions:
            raise ValueError("a composition-level patent review declares its jurisdictions")

    @property
    def axis_ceiling(self) -> str:
        if not (self.attempted and self.coverage_complete):
            return "NOT_EVALUABLE"
        if self.composition_level_review_complete:
            return "DIRECT"
        if self.target_level_search_complete:
            return "INDIRECT_STRONG"
        return "NOT_EVALUABLE"

    @property
    def evaluable(self) -> bool:
        return self.axis_ceiling in ("DIRECT", "INDIRECT_STRONG")


# --- module input --------------------------------------------------------

@dataclass(frozen=True)
class Tgt08ModuleInput:
    """Everything the module needs to run one (candidate, TGT-08) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the
    SINGLE authoritative identity (MOD-TGT01 / PR E2 gene). TGT-08 is
    time-dependent: ``landscape_as_of`` is mandatory and there is no implicit
    default context (E5 item 10)."""

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
    context_key: str
    landscape_as_of: str
    retrieval_scope: str
    patent_scope: str
    jurisdictions: tuple[str, ...] = field(default_factory=tuple)
    existing_evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _text(self.candidate_name, "candidate_name")
        _text(self.target_identity, "target_identity")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        if self.instantiation_id != INSTANTIATION_ID:
            raise ValueError(f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT08")
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
            raise ValueError("evidence_regime must be PUBLIC_ONLY for TGT-08")
        _text(self.run_id, "run_id")
        _text(self.code_commit, "code_commit", allow_empty=True)
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date -- a landscape with no as_of is not admissible")
        _text(self.retrieval_scope, "retrieval_scope")
        _text(self.patent_scope, "patent_scope")
        if not isinstance(self.jurisdictions, tuple) or not all(
            isinstance(x, str) and x for x in self.jurisdictions
        ):
            raise ValueError("jurisdictions must be a tuple of non-empty strings")
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


# --- classification ------------------------------------------------------

@dataclass(frozen=True)
class ClassifiedOpportunity:
    """A provider record placed into a frozen TGT-08 evidence class and given
    a Module-owned Gate-relative opportunity implication (E6-4). The provider
    never sets ``opportunity_implication``."""

    record: NormalizedOpportunityRecord
    admissible: bool
    rejection_reason: str
    rejection_severity: str  # "" when admissible; else "HARD" | "SOFT"
    evidence_class: str
    opportunity_implication: str  # "" for rejected / audit; else SUPPORTS/OPPOSES/CONTEXTUAL
    qualifying_for_axis: bool     # a qualifying live competitor / live composition patent

    def __post_init__(self) -> None:
        _bool(self.admissible, "admissible")
        _text(self.rejection_reason, "rejection_reason", allow_empty=True)
        _bool(self.qualifying_for_axis, "qualifying_for_axis")
        if self.admissible:
            _choice(self.rejection_severity, ("",), "rejection_severity")
            _text(self.evidence_class, "evidence_class")
            _choice(
                self.opportunity_implication,
                OPPORTUNITY_IMPLICATION_VALUES,
                "opportunity_implication",
            )
        else:
            _choice(self.rejection_severity, ("HARD", "SOFT"), "rejection_severity")
            if not self.rejection_reason:
                raise ValueError("a rejected record must state a rejection_reason")
            if self.opportunity_implication:
                raise ValueError("a rejected record has no opportunity implication")
            if self.qualifying_for_axis:
                raise ValueError("a rejected record is not qualifying for an axis")

    @property
    def observation_id(self) -> str:
        return self.record.observation_id

    @property
    def evidence_axis(self) -> str:
        return self.record.evidence_axis

    @property
    def observation_kind(self) -> str:
        return self.record.observation_kind

    @property
    def is_directional(self) -> bool:
        return self.admissible and self.opportunity_implication in (
            "SUPPORTS_OPPORTUNITY",
            "OPPOSES_OPPORTUNITY",
        )


# --- emitted evidence (one observation -> one canonical EP) --------------

@dataclass(frozen=True)
class EmittedEvidence:
    classified: ClassifiedOpportunity
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedOpportunity):
            raise ValueError("classified must be a ClassifiedOpportunity")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")


# --- sponsor review (E6-5): a machine review TRIGGER --------------------

@dataclass(frozen=True)
class SponsorReviewRecord:
    """Non-canonical, module-local, on the run result only. NOT a proposal
    field, NOT a CandidateGateAssessment field, NOT a core object, NOT a
    Decision, NOT a Gate fatal flag. ``status`` has ONE non-empty value; the
    machine NEVER emits a canonical fatal flag / KILL / STOP_FOR_SPONSOR /
    OUT_OF_MANDATE, and NEVER asserts dominant / well-protected / no
    differentiation path."""

    required: bool
    status: str  # "" | POTENTIAL_SPONSOR_FATAL_PATTERN
    evidence_ids: tuple[str, ...]
    competitor_program_ids: tuple[str, ...]
    patent_family_ids: tuple[str, ...]
    landscape_as_of: str
    patent_scope: str

    def __post_init__(self) -> None:
        _bool(self.required, "required")
        _choice(self.status, SPONSOR_REVIEW_STATUS_VALUES, "status")
        if self.required != (self.status == "POTENTIAL_SPONSOR_FATAL_PATTERN"):
            raise ValueError("required is true iff status == POTENTIAL_SPONSOR_FATAL_PATTERN")
        for evidence_id in self.evidence_ids:
            _pattern(evidence_id, _EP_ID, "sponsor_review.evidence_ids[]")
        for name in ("competitor_program_ids", "patent_family_ids"):
            for item in getattr(self, name):
                _text(item, f"sponsor_review.{name}[]")
        _text(self.landscape_as_of, "sponsor_review.landscape_as_of", allow_empty=not self.required)
        _text(self.patent_scope, "sponsor_review.patent_scope", allow_empty=not self.required)
        if self.required:
            if not self.competitor_program_ids or not self.patent_family_ids:
                raise ValueError(
                    "a POTENTIAL_SPONSOR_FATAL_PATTERN carries >= 1 competitor program "
                    "and >= 1 patent family"
                )
            if not self.evidence_ids:
                raise ValueError("a POTENTIAL_SPONSOR_FATAL_PATTERN carries its contributing evidence")
        else:
            for name in ("evidence_ids", "competitor_program_ids", "patent_family_ids"):
                if getattr(self, name):
                    raise ValueError(f"sponsor_review.{name} is empty when required is false")

    @staticmethod
    def none() -> "SponsorReviewRecord":
        return SponsorReviewRecord(False, "", (), (), (), "", "")


# --- proposal envelope (E5 item 12) ------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Carries the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` AND any FTO / legal /
    "no differentiation path" conclusion AND any fatal flag / KILL /
    STOP_FOR_SPONSOR / OUT_OF_MANDATE (the potential-sponsor-fatal-pattern signal
    lives in the module-local sponsor_review record)."""

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
        if (self.proposed_direction, self.proposed_strength) not in LEGAL_DIRECTION_STRENGTH_PAIRS:
            raise ValueError(
                f"Direction x Strength {(self.proposed_direction, self.proposed_strength)} "
                "is not a legal TGT-08 pair"
            )
        seen: set[str] = set()
        for evidence_id, role in self.evidence_refs:
            _pattern(evidence_id, _EP_ID, "evidence_refs.evidence_id")
            _choice(role, EVIDENCE_ROLE_VALUES, "evidence_refs.role")
            if evidence_id in seen:
                raise ValueError(f"evidence_ref {evidence_id} appears more than once")
            seen.add(evidence_id)
        _text(self.aggregation_rationale, "aggregation_rationale")
        for unknown, resolution in self.critical_unknowns:
            _text(unknown, "critical_unknowns.unknown")
            _choice(resolution, CRITICAL_UNKNOWN_RESOLUTIONS, "critical_unknowns.resolution")
            if resolution == "EXPERIMENT_REQUIRED":
                raise ValueError("TGT-08 never uses EXPERIMENT_REQUIRED -- FTO is not an experiment")
        if self.evidence_ceiling != TGT08_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-08 ceiling verbatim")

        roles = {r for _, r in self.evidence_refs}
        d, s = self.proposed_direction, self.proposed_strength
        if d == "POSITIVE" and "SUPPORTING" not in roles:
            raise ValueError("a POSITIVE proposal needs >= 1 SUPPORTING evidence_ref")
        if d == "NEGATIVE" and "CONTRADICTING" not in roles:
            raise ValueError("a NEGATIVE proposal needs >= 1 CONTRADICTING evidence_ref")
        if d == "CONFLICTING" and not {"SUPPORTING", "CONTRADICTING"} <= roles:
            raise ValueError("a CONFLICTING proposal needs >= 1 SUPPORTING and >= 1 CONTRADICTING ref")
        if d == "INCONCLUSIVE" and s in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            if "CONTEXTUAL" not in roles or not self.evidence_refs:
                raise ValueError(
                    "a graded / WEAK INCONCLUSIVE proposal carries CONTEXTUAL evidence_refs"
                )
        if d == "INCONCLUSIVE" and s == "UNKNOWN" and self.evidence_refs:
            raise ValueError("the UNKNOWN state carries no evidence_refs")

    @classmethod
    def field_names(cls) -> tuple[str, ...]:
        return tuple(f.name for f in fields(cls))


@dataclass(frozen=True)
class MachineAcceptanceRecord:
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


# --- run result -------------------------------------------------------

@dataclass(frozen=True)
class Tgt08ModuleRunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]  # newly created only
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    competitive_completion: CompetitiveLandscapeCompletion
    patent_completion: PatentLandscapeCompletion
    sponsor_review: SponsorReviewRecord
    rejected_records: tuple[tuple[str, str], ...]
    hard_integrity_failures: tuple[tuple[str, str], ...]

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
            if reused in ep_ids:
                raise ValueError(
                    "a reused_evidence_id must NOT also appear as a re-created body"
                )
        resolvable = set(ep_ids) | set(self.reused_evidence_ids)
        if not isinstance(self.competitive_completion, CompetitiveLandscapeCompletion):
            raise ValueError("competitive_completion must be a CompetitiveLandscapeCompletion")
        if not isinstance(self.patent_completion, PatentLandscapeCompletion):
            raise ValueError("patent_completion must be a PatentLandscapeCompletion")
        if not isinstance(self.sponsor_review, SponsorReviewRecord):
            raise ValueError("sponsor_review must be a SponsorReviewRecord")
        for pid, reason in self.hard_integrity_failures:
            _text(pid, "hard_integrity_failures.id")
            _text(reason, "hard_integrity_failures.reason")
        for pid, reason in self.rejected_records:
            _text(pid, "rejected_records.id")
            _text(reason, "rejected_records.reason")
        if self.proposal_envelope is not None and not isinstance(
            self.proposal_envelope, AssessmentProposalEnvelope
        ):
            raise ValueError("proposal_envelope must be an AssessmentProposalEnvelope")
        if self.proposal_envelope is not None and not self.machine_acceptance.accepted:
            raise ValueError("a proposal envelope requires an accepted machine record")
        if self.proposal_envelope is None and self.machine_acceptance.accepted:
            raise ValueError("an accepted machine record must carry a proposal envelope")
        if self.hard_integrity_failures and (
            self.machine_acceptance.accepted or self.proposal_envelope is not None
        ):
            raise ValueError(
                "a hard integrity failure must reject the run (no proposal envelope)"
            )
        # sponsor_review handoff eligibility: only an accepted run's trigger is
        # actionable (E6-5).
        if self.sponsor_review.required and not self.machine_acceptance.accepted:
            raise ValueError(
                "a sponsor_review trigger on the run result requires an accepted run"
            )
        if self.proposal_envelope is not None:
            for evidence_id, _ in self.proposal_envelope.evidence_refs:
                if evidence_id not in resolvable:
                    raise ValueError(
                        "proposal evidence_ref does not resolve to an emitted or reused package"
                    )


def overall_strength(competitive_ceiling: str, patent_ceiling: str) -> str:
    """The weaker required axis ceiling (E6-3). Returns "DIRECT" /
    "INDIRECT_STRONG" / "NOT_EVALUABLE"."""

    rank = min(_CEILING_RANK[competitive_ceiling], _CEILING_RANK[patent_ceiling])
    for name, value in _CEILING_RANK.items():
        if value == rank:
            return name
    return "NOT_EVALUABLE"
