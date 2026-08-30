"""Frozen input / output contracts for MOD-TGT02.

Runtime Migration PR E8. In-memory contract values handed between the
deterministic Gate-specific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments.

Three invariants this module must never break (frozen E7 contract + ChatGPT
AI审核方案 E8):

1. A single observation is NEVER a Direction. The classifier emits a
   Gate-neutral, rung-classed, direction-SUPPORTING observation only; the
   proposed Direction x Strength is produced by ``aggregate`` over a COMPLETED,
   audited CRC coverage landscape. Until then the assessment stays
   INCONCLUSIVE / UNKNOWN.
2. TGT-02 NEGATIVE is a Gate-relative SCIENTIFIC coverage judgement -- current
   admissible evidence shows the malignant compartment lacks adequate
   population-level target coverage. It is never a fatal flag and never a KILL.
   A cross-cohort protein-level negative-coverage pattern is surfaced at most as
   a machine-local ``fatal_review = POTENTIAL_FATAL_PATTERN``.
3. "rare and highly heterogeneous" is an upstream-qualified factual state
   (``expression_pattern`` + ``expression_pattern_basis``). The Module only
   consumes it; it never computes it from a percent-positive value, an H-score
   or a cohort n. No numeric or ranking score anywhere.
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

from .completion import CrcCohortCoverageCompletion

# --- identity ---------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT02"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-02"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-02 contract. Reproduced only by the
#: PROPOSAL layer -- never stamped onto a Gate-neutral EvidencePackage.
TGT02_EVIDENCE_CEILING: Final[str] = (
    "protein-level malignant-cell expression across an adequately powered CRC cohort"
)
TGT02_GATE_QUESTION: Final[str] = (
    "In refractory metastatic colorectal cancer, do malignant cells express the "
    "target at the protein level with adequate cohort-level consistency?"
)

_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ----------------------------------------------------------------

#: What a normalized coverage observation IS. The provider supplies facts only --
#: it never sets a rung, a direction, or a coverage-support implication.
OBSERVATION_KIND_VALUES: Final[tuple[str, ...]] = (
    "PROTEIN_COHORT",
    "MALIGNANT_SC_SPATIAL",
    "TMA_TRANSCRIPT_PROTEIN_CONCORDANCE",
    "BULK_CRC_RNA",
    "PAN_CANCER_UNRESOLVED",
    "MATCHED_NORMAL_TUMOR",
    "SEARCH_COMPLETION_AUDIT",
)

MOLECULAR_LAYER_VALUES: Final[tuple[str, ...]] = ("", "PROTEIN", "TRANSCRIPT", "BOTH")

#: Typed assay method -- a classification-driving fact, NOT free text (E8-2). The
#: DIRECT rung is reachable only through a validated protein assay; a generic /
#: OTHER protein assay never reaches DIRECT.
ASSAY_METHOD_VALUES: Final[tuple[str, ...]] = (
    "",
    "VALIDATED_IHC",
    "QUANTITATIVE_PROTEOMICS",
    "VALIDATED_MULTIPLEX_IF",
    "SINGLE_CELL_RNA",
    "SPATIAL_RNA",
    "TMA_TRANSCRIPT_PROTEIN",
    "BULK_RNA",
    "PAN_CANCER_PANEL",
    "MATCHED_NORMAL_TUMOR_COMPARISON",
    "SEARCH_AUDIT",
    "OTHER",
)
#: The only assays that can carry a DIRECT-rung protein-cohort observation.
_DIRECT_PROTEIN_ASSAYS: Final[tuple[str, ...]] = (
    "VALIDATED_IHC",
    "QUANTITATIVE_PROTEOMICS",
    "VALIDATED_MULTIPLEX_IF",
)
#: The malignant-compartment sc / spatial assays (INDIRECT_STRONG rung).
_SC_SPATIAL_ASSAYS: Final[tuple[str, ...]] = ("SINGLE_CELL_RNA", "SPATIAL_RNA")

MALIGNANT_ATTRIBUTION_VALUES: Final[tuple[str, ...]] = (
    "MALIGNANT",
    "NON_MALIGNANT",
    "UNRESOLVED",
)
COHORT_ADEQUACY_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")

#: The upstream-qualified factual coverage state. ABSENT and
#: RARE_HIGHLY_HETEROGENEOUS are negative-coverage classes and require an
#: auditable ``expression_pattern_basis`` + ``expression_pattern_basis_detail``.
EXPRESSION_PATTERN_VALUES: Final[tuple[str, ...]] = (
    "",
    "PRESENT_CONSISTENT",
    "ABSENT",
    "RARE_HIGHLY_HETEROGENEOUS",
    "MIXED_OR_UNRESOLVED",
)
_NEGATIVE_COVERAGE_PATTERNS: Final[tuple[str, ...]] = ("ABSENT", "RARE_HIGHLY_HETEROGENEOUS")

#: How an ``expression_pattern`` qualification was established. It is never
#: computed by the Module (E7 item 06 ``rare_or_highly_heterogeneous_is_upstream_qualified``).
EXPRESSION_PATTERN_BASIS_VALUES: Final[tuple[str, ...]] = (
    "",
    "SOURCE_REPORTED",
    "HUMAN_REVIEWED_NORMALIZATION",
)

#: The Evidence-Ladder rung the Module maps an observation to (frozen PR D).
EVIDENCE_RUNG_VALUES: Final[tuple[str, ...]] = ("", "DIRECT", "INDIRECT_STRONG", "WEAK")

#: Module-assigned Gate-relative reading of a rung-classed observation.
COVERAGE_SUPPORT_VALUES: Final[tuple[str, ...]] = (
    "",
    "SUPPORTS_COVERAGE",
    "OPPOSES_COVERAGE",
    "CONTEXTUAL",
)
_SUPPORT_TO_ROLE: Final[dict[str, str]] = {
    "SUPPORTS_COVERAGE": "SUPPORTING",
    "OPPOSES_COVERAGE": "CONTRADICTING",
    "CONTEXTUAL": "CONTEXTUAL",
}

FATAL_REVIEW_STATUS_VALUES: Final[tuple[str, ...]] = ("", "POTENTIAL_FATAL_PATTERN")

CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

#: The only Direction x Strength pairs MOD-TGT02 may propose (frozen E7 item 06
#: truth table). There is NO ``INCONCLUSIVE / WEAK`` -- a WEAK-only public
#: landscape is INCONCLUSIVE / UNKNOWN (TGT-02-specific).
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
        ("INCONCLUSIVE", "UNKNOWN"),
    }
)

_RUNG_RANK: Final[dict[str, int]] = {"DIRECT": 2, "INDIRECT_STRONG": 1, "": 0}


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


# --- provider output: normalized coverage observation ----------------------

@dataclass(frozen=True)
class NormalizedCoverageObservation:
    """One already-normalized, primary/repository-source-resolved TGT-02
    malignant-cell coverage observation. FACTS only -- the provider never sets a
    rung, a direction, or a coverage-support implication (E8-2). ``assay_method``
    is a typed classification-driving fact, not free text."""

    observation_id: str
    target_identity: str
    context_key: str
    landscape_as_of: str
    observation_kind: str
    molecular_layer: str
    assay_method: str
    crc_specific: bool
    malignant_cell_attribution: str
    malignant_attribution_basis: str
    cohort_adequacy_status: str
    cohort_adequacy_basis: str
    expression_pattern: str
    expression_pattern_basis: str
    expression_pattern_basis_detail: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    primary_or_repository_source_resolved: bool
    cohort_id: str = ""
    cohort_ids: tuple[str, ...] = ()
    cohort_n: int = 0  # a raw fact only; NEVER enters the rung / threshold logic
    declared_multi_cohort_analysis: bool = False
    # --- SEARCH_COMPLETION_AUDIT-specific structured snapshot (E8-5 gene) -----
    audit_search_scope: str = ""
    audit_sources_searched: tuple[str, ...] = ()
    audit_landscape_as_of: str = ""
    audit_public_crc_coverage_search_complete: bool = False
    audit_protein_cohort_search_complete: bool = False
    audit_malignant_compartment_sc_spatial_search_complete: bool = False
    audit_tma_concordance_search_complete: bool = False
    audit_matched_normal_tumor_search_complete: bool = False
    audit_unresolved_item_keys: tuple[str, ...] = ()
    audit_qualifying_protein_cohort_ids: tuple[str, ...] = ()
    audit_qualifying_indirect_cohort_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _pattern(self.observation_id, _OBS_ID, "observation_id")
        _text(self.target_identity, "target_identity")
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _choice(self.observation_kind, OBSERVATION_KIND_VALUES, "observation_kind")
        _choice(self.molecular_layer, MOLECULAR_LAYER_VALUES, "molecular_layer")
        _choice(self.assay_method, ASSAY_METHOD_VALUES, "assay_method")
        _bool(self.crc_specific, "crc_specific")
        _choice(
            self.malignant_cell_attribution,
            MALIGNANT_ATTRIBUTION_VALUES,
            "malignant_cell_attribution",
        )
        _text(self.malignant_attribution_basis, "malignant_attribution_basis", allow_empty=True)
        _choice(self.cohort_adequacy_status, COHORT_ADEQUACY_VALUES, "cohort_adequacy_status")
        _text(self.cohort_adequacy_basis, "cohort_adequacy_basis", allow_empty=True)
        _choice(self.expression_pattern, EXPRESSION_PATTERN_VALUES, "expression_pattern")
        _choice(
            self.expression_pattern_basis,
            EXPRESSION_PATTERN_BASIS_VALUES,
            "expression_pattern_basis",
        )
        _text(
            self.expression_pattern_basis_detail,
            "expression_pattern_basis_detail",
            allow_empty=True,
        )
        _text(self.claim, "claim")
        _pattern(self.source_id, _SRC_ID, "source_id")
        _choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _text(self.source_identifier, "source_identifier")
        _text(self.locator, "locator", allow_empty=True)
        _text(self.retrieved_at, "retrieved_at")
        if not _ISO_DATE_PREFIX.match(self.retrieved_at):
            raise ValueError("retrieved_at must start with an ISO date")
        _bool(self.primary_or_repository_source_resolved, "primary_or_repository_source_resolved")
        _text(self.cohort_id, "cohort_id", allow_empty=True)
        _str_tuple(self.cohort_ids, "cohort_ids") if self.cohort_ids else None
        if not isinstance(self.cohort_n, int) or isinstance(self.cohort_n, bool) or self.cohort_n < 0:
            raise ValueError("cohort_n must be a non-negative integer (a raw fact only)")
        _bool(self.declared_multi_cohort_analysis, "declared_multi_cohort_analysis")

        # --- cross-field shape by observation kind ---------------------------
        kind = self.observation_kind
        if kind == "PROTEIN_COHORT":
            if self.molecular_layer not in ("PROTEIN", "BOTH"):
                raise ValueError("a PROTEIN_COHORT observation is at the PROTEIN molecular layer")
            if not self.cohort_id.strip() and not self.cohort_ids:
                raise ValueError("a PROTEIN_COHORT observation names its cohort_id / cohort_ids")
        elif kind == "MALIGNANT_SC_SPATIAL":
            if self.molecular_layer != "TRANSCRIPT":
                raise ValueError("a MALIGNANT_SC_SPATIAL observation is at the TRANSCRIPT layer")
        elif kind == "TMA_TRANSCRIPT_PROTEIN_CONCORDANCE":
            if self.molecular_layer != "BOTH":
                raise ValueError(
                    "a TMA_TRANSCRIPT_PROTEIN_CONCORDANCE observation is at the BOTH layer"
                )
        elif kind == "BULK_CRC_RNA":
            if self.molecular_layer != "TRANSCRIPT":
                raise ValueError("a BULK_CRC_RNA observation is at the TRANSCRIPT layer")
        elif kind == "PAN_CANCER_UNRESOLVED":
            if self.molecular_layer not in ("TRANSCRIPT", "PROTEIN", "BOTH"):
                raise ValueError("a PAN_CANCER_UNRESOLVED observation carries a molecular layer")
        elif kind == "MATCHED_NORMAL_TUMOR":
            pass
        elif kind == "SEARCH_COMPLETION_AUDIT":
            if self.assay_method != "SEARCH_AUDIT":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries assay_method SEARCH_AUDIT"
                )
            if self.molecular_layer != "":
                raise ValueError("a SEARCH_COMPLETION_AUDIT observation has no molecular layer")

        # --- qualification-basis hygiene (E7 item 06 / item 13) -------------
        if self.malignant_cell_attribution == "MALIGNANT" and not self.malignant_attribution_basis.strip():
            raise ValueError(
                "a MALIGNANT malignant_cell_attribution carries an auditable "
                "malignant_attribution_basis"
            )
        if self.cohort_adequacy_status == "QUALIFIED" and not self.cohort_adequacy_basis.strip():
            raise ValueError(
                "a QUALIFIED cohort_adequacy_status carries an auditable cohort_adequacy_basis"
            )
        if self.expression_pattern in _NEGATIVE_COVERAGE_PATTERNS:
            if not self.expression_pattern_basis:
                raise ValueError(
                    "an ABSENT / RARE_HIGHLY_HETEROGENEOUS expression_pattern carries an "
                    "expression_pattern_basis (SOURCE_REPORTED / HUMAN_REVIEWED_NORMALIZATION)"
                )
            if not self.expression_pattern_basis_detail.strip():
                raise ValueError(
                    "an ABSENT / RARE_HIGHLY_HETEROGENEOUS expression_pattern carries an "
                    "auditable expression_pattern_basis_detail"
                )
        if self.expression_pattern_basis and not self.expression_pattern:
            raise ValueError("an expression_pattern_basis without an expression_pattern is drift")

        # --- audit-snapshot shape (E8-5 gene) ------------------------------
        _text(self.audit_search_scope, "audit_search_scope", allow_empty=True)
        for name in (
            "audit_sources_searched",
            "audit_unresolved_item_keys",
            "audit_qualifying_protein_cohort_ids",
            "audit_qualifying_indirect_cohort_ids",
        ):
            _str_tuple(getattr(self, name), name) if getattr(self, name) else None
        _text(self.audit_landscape_as_of, "audit_landscape_as_of", allow_empty=True)
        for name in (
            "audit_public_crc_coverage_search_complete",
            "audit_protein_cohort_search_complete",
            "audit_malignant_compartment_sc_spatial_search_complete",
            "audit_tma_concordance_search_complete",
            "audit_matched_normal_tumor_search_complete",
        ):
            _bool(getattr(self, name), name)
        _any_audit_field = (
            bool(self.audit_search_scope.strip())
            or bool(self.audit_sources_searched)
            or bool(self.audit_landscape_as_of.strip())
            or self.audit_public_crc_coverage_search_complete
            or self.audit_protein_cohort_search_complete
            or self.audit_malignant_compartment_sc_spatial_search_complete
            or self.audit_tma_concordance_search_complete
            or self.audit_matched_normal_tumor_search_complete
            or bool(self.audit_unresolved_item_keys)
            or bool(self.audit_qualifying_protein_cohort_ids)
            or bool(self.audit_qualifying_indirect_cohort_ids)
        )
        if kind == "SEARCH_COMPLETION_AUDIT":
            if not self.audit_search_scope.strip():
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries a non-empty audit_search_scope"
                )
            if not self.audit_sources_searched:
                raise ValueError("a SEARCH_COMPLETION_AUDIT observation lists the sources searched")
            if not self.audit_landscape_as_of.strip():
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries an audit_landscape_as_of"
                )
        elif _any_audit_field:
            raise ValueError("only a SEARCH_COMPLETION_AUDIT observation carries an audit snapshot")

    # --- factual predicates (field reads only, no interpretation) -----------
    @property
    def cohort_identities(self) -> tuple[str, ...]:
        """Every distinct auditable cohort identity this observation represents:
        its ``cohort_ids`` for a declared multi-cohort analysis, else its single
        ``cohort_id``."""

        if self.cohort_ids:
            seen: list[str] = []
            for cid in self.cohort_ids:
                if cid not in seen:
                    seen.append(cid)
            return tuple(seen)
        return (self.cohort_id,) if self.cohort_id.strip() else ()

    @property
    def is_protein_layer(self) -> bool:
        return self.molecular_layer in ("PROTEIN", "BOTH")

    @property
    def is_validated_protein_assay(self) -> bool:
        return self.assay_method in _DIRECT_PROTEIN_ASSAYS

    @property
    def is_sc_spatial_assay(self) -> bool:
        return self.assay_method in _SC_SPATIAL_ASSAYS

    @property
    def is_malignant_attributed(self) -> bool:
        return self.malignant_cell_attribution == "MALIGNANT"

    @property
    def is_cohort_qualified(self) -> bool:
        return self.cohort_adequacy_status == "QUALIFIED"

    @property
    def is_negative_coverage_pattern(self) -> bool:
        return self.expression_pattern in _NEGATIVE_COVERAGE_PATTERNS

    @property
    def is_present_pattern(self) -> bool:
        return self.expression_pattern == "PRESENT_CONSISTENT"


# --- classification ------------------------------------------------------

@dataclass(frozen=True)
class ClassifiedCoverage:
    """A provider observation placed into a FROZEN TGT-02 Evidence-Ladder rung
    and given a Module-owned Gate-relative coverage-support reading. The provider
    never sets ``evidence_rung`` or ``coverage_support``. ``qualifying_for_direct``
    / ``qualifying_for_indirect`` are RUNG-SPECIFIC (E7 item 06
    ``qualifying_is_rung_specific``)."""

    observation: NormalizedCoverageObservation
    admissible: bool
    rejection_reason: str
    rejection_severity: str  # "" when admissible; else "HARD" | "SOFT"
    evidence_rung: str       # "" | DIRECT | INDIRECT_STRONG | WEAK
    coverage_support: str     # "" | SUPPORTS_COVERAGE | OPPOSES_COVERAGE | CONTEXTUAL
    qualifying_for_direct: bool
    qualifying_for_indirect: bool

    def __post_init__(self) -> None:
        _bool(self.admissible, "admissible")
        _text(self.rejection_reason, "rejection_reason", allow_empty=True)
        _bool(self.qualifying_for_direct, "qualifying_for_direct")
        _bool(self.qualifying_for_indirect, "qualifying_for_indirect")
        if self.admissible:
            _choice(self.rejection_severity, ("",), "rejection_severity")
            _choice(self.evidence_rung, EVIDENCE_RUNG_VALUES, "evidence_rung")
            _choice(self.coverage_support, COVERAGE_SUPPORT_VALUES, "coverage_support")
            if self.qualifying_for_direct and self.evidence_rung != "DIRECT":
                raise ValueError("qualifying_for_direct requires evidence_rung DIRECT")
            if self.qualifying_for_indirect and self.evidence_rung != "INDIRECT_STRONG":
                raise ValueError("qualifying_for_indirect requires evidence_rung INDIRECT_STRONG")
            if self.qualifying_for_direct and self.qualifying_for_indirect:
                raise ValueError("an observation qualifies for at most one rung")
        else:
            _choice(self.rejection_severity, ("HARD", "SOFT"), "rejection_severity")
            if not self.rejection_reason:
                raise ValueError("a rejected observation must state a rejection_reason")
            if self.evidence_rung or self.coverage_support:
                raise ValueError("a rejected observation has no rung or coverage support")
            if self.qualifying_for_direct or self.qualifying_for_indirect:
                raise ValueError("a rejected observation is not qualifying for a rung")

    @property
    def observation_id(self) -> str:
        return self.observation.observation_id

    @property
    def observation_kind(self) -> str:
        return self.observation.observation_kind

    @property
    def is_directional(self) -> bool:
        return self.admissible and self.coverage_support in (
            "SUPPORTS_COVERAGE",
            "OPPOSES_COVERAGE",
        )

    @property
    def is_qualifying(self) -> bool:
        return self.qualifying_for_direct or self.qualifying_for_indirect


# --- emitted evidence (one observation -> one canonical EP) --------------

@dataclass(frozen=True)
class EmittedEvidence:
    classified: ClassifiedCoverage
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedCoverage):
            raise ValueError("classified must be a ClassifiedCoverage")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")

    @property
    def observation(self) -> NormalizedCoverageObservation:
        return self.classified.observation


# --- fatal review (E7 item 08 / 12): a machine review TRIGGER -----------

@dataclass(frozen=True)
class FatalReviewRecord:
    """Non-canonical, module-local, on the run result only. NOT a proposal
    field, NOT a CandidateGateAssessment field, NOT a core object, NOT a
    Decision, NOT a Gate fatal flag. ``status`` has ONE non-empty value; the
    machine NEVER emits PUBLIC_FATAL_SIGNAL_ESTABLISHED / a canonical fatal flag
    / KILL / HOLD / Decision, and NEVER decides whether the pattern is a real
    fatal signal -- that is human review + the GateSet fatal policy."""

    required: bool
    status: str  # "" | POTENTIAL_FATAL_PATTERN
    evidence_ids: tuple[str, ...]
    cohort_ids: tuple[str, ...]
    coverage_class: tuple[str, ...]
    cohort_adequacy_basis_refs: tuple[str, ...]
    expression_pattern_basis_refs: tuple[str, ...]
    landscape_as_of: str
    crc_coverage_search_scope: str

    def __post_init__(self) -> None:
        _bool(self.required, "required")
        _choice(self.status, FATAL_REVIEW_STATUS_VALUES, "status")
        if self.required != (self.status == "POTENTIAL_FATAL_PATTERN"):
            raise ValueError("required is true iff status == POTENTIAL_FATAL_PATTERN")
        for evidence_id in self.evidence_ids:
            _pattern(evidence_id, _EP_ID, "fatal_review.evidence_ids[]")
        for name in ("cohort_ids", "coverage_class", "cohort_adequacy_basis_refs",
                     "expression_pattern_basis_refs"):
            for item in getattr(self, name):
                _text(item, f"fatal_review.{name}[]")
        _text(self.landscape_as_of, "fatal_review.landscape_as_of", allow_empty=not self.required)
        _text(
            self.crc_coverage_search_scope,
            "fatal_review.crc_coverage_search_scope",
            allow_empty=not self.required,
        )
        if self.required:
            if not self.evidence_ids:
                raise ValueError("a POTENTIAL_FATAL_PATTERN carries its contributing evidence")
            if len(set(self.cohort_ids)) < 2:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries at least two independent cohort_ids"
                )
            for c in self.coverage_class:
                _choice(c, _NEGATIVE_COVERAGE_PATTERNS, "fatal_review.coverage_class[]")
            if not self.cohort_adequacy_basis_refs or not self.expression_pattern_basis_refs:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the cohort-adequacy and "
                    "expression-pattern basis refs"
                )
        else:
            for name in ("evidence_ids", "cohort_ids", "coverage_class",
                         "cohort_adequacy_basis_refs", "expression_pattern_basis_refs"):
                if getattr(self, name):
                    raise ValueError(f"fatal_review.{name} is empty when required is false")

    @staticmethod
    def none() -> "FatalReviewRecord":
        return FatalReviewRecord(False, "", (), (), (), (), (), "", "")


# --- module input --------------------------------------------------------

@dataclass(frozen=True)
class Tgt02ModuleInput:
    """Everything the module needs to run one (candidate, TGT-02) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the
    SINGLE authoritative identity (MOD-TGT01 / PR E2 gene). There is no second
    drift-prone target argument and no implicit default scientific context
    (E7 item 10)."""

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
    crc_coverage_search_scope: str
    existing_evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _text(self.candidate_name, "candidate_name")
        _text(self.target_identity, "target_identity")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        if self.instantiation_id != INSTANTIATION_ID:
            raise ValueError(f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT02")
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
            raise ValueError("evidence_regime must be PUBLIC_ONLY for the current TGT-02 instantiation")
        _text(self.run_id, "run_id")
        _text(self.code_commit, "code_commit", allow_empty=True)
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError(
                "landscape_as_of must start with an ISO date -- a landscape with no as_of "
                "is not admissible"
            )
        _text(self.crc_coverage_search_scope, "crc_coverage_search_scope")
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


# --- proposal envelope (E7 item 12) ------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Carries the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` AND any TGT-03 /
    TGT-04 / TGT-05 conclusion AND any fatal flag (the potential-fatal-pattern
    signal lives in the module-local ``fatal_review`` record)."""

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
                "is not a legal TGT-02 pair (note: there is no INCONCLUSIVE / WEAK)"
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
        if self.evidence_ceiling != TGT02_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-02 ceiling verbatim")

        roles = {r for _, r in self.evidence_refs}
        d, s = self.proposed_direction, self.proposed_strength
        if d == "POSITIVE" and "SUPPORTING" not in roles:
            raise ValueError("a POSITIVE proposal needs >= 1 SUPPORTING evidence_ref")
        if d == "NEGATIVE" and "CONTRADICTING" not in roles:
            raise ValueError("a NEGATIVE proposal needs >= 1 CONTRADICTING evidence_ref")
        if d == "CONFLICTING" and not {"SUPPORTING", "CONTRADICTING"} <= roles:
            raise ValueError("a CONFLICTING proposal needs >= 1 SUPPORTING and >= 1 CONTRADICTING ref")
        if d == "INCONCLUSIVE" and s in ("DIRECT", "INDIRECT_STRONG"):
            if "CONTEXTUAL" not in roles or not self.evidence_refs:
                raise ValueError("a graded INCONCLUSIVE proposal carries CONTEXTUAL evidence_refs")
        if d == "INCONCLUSIVE" and s == "UNKNOWN" and self.evidence_refs:
            raise ValueError("the INCONCLUSIVE / UNKNOWN state carries no evidence_refs")

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
class Tgt02ModuleRunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]  # newly created only
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    coverage_completion: CrcCohortCoverageCompletion
    fatal_review: FatalReviewRecord
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
                raise ValueError("a reused_evidence_id must NOT also appear as a re-created body")
        resolvable = set(ep_ids) | set(self.reused_evidence_ids)
        if not isinstance(self.coverage_completion, CrcCohortCoverageCompletion):
            raise ValueError("coverage_completion must be a CrcCohortCoverageCompletion")
        if not isinstance(self.fatal_review, FatalReviewRecord):
            raise ValueError("fatal_review must be a FatalReviewRecord")
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
            raise ValueError("a hard integrity failure must reject the run (no proposal envelope)")
        # fatal_review handoff eligibility: only an accepted run's trigger is
        # actionable (E6 / E7 gene).
        if self.fatal_review.required and not self.machine_acceptance.accepted:
            raise ValueError(
                "a fatal_review trigger on the run result requires an accepted run"
            )
        if self.proposal_envelope is not None:
            for evidence_id, _ in self.proposal_envelope.evidence_refs:
                if evidence_id not in resolvable:
                    raise ValueError(
                        "proposal evidence_ref does not resolve to an emitted or reused package"
                    )


def overall_strength(qualifying_direct: bool, qualifying_indirect: bool) -> str:
    """The HIGHEST qualifying frozen evidence class actually met (E7 item 06
    ``strength_is_the_highest_qualifying_evidence_class``). There is NO E6-style
    two-axis weaker-ceiling rule. Returns "DIRECT" / "INDIRECT_STRONG" / ""."""

    if qualifying_direct:
        return "DIRECT"
    if qualifying_indirect:
        return "INDIRECT_STRONG"
    return ""
