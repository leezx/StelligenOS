"""Frozen input / output contracts for MOD-TGT03.

Runtime Migration PR E10. In-memory contract values handed between the
deterministic Gate-specific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments.

Three invariants this module must never break (frozen E9 contract + ChatGPT
AI审核方案 E10):

1. Baseline expression is not persistence. Only explicitly qualified treatment /
   metastasis-context evidence can drive TGT-03. Treatment-naive primary CRC
   coverage (that is TGT-02) is admissible here ONLY as the frozen WEAK class and
   never above WEAK.
2. A single observation is evidence, never a Direction; grading requires the
   completed and audited persistence landscape, and NEGATIVE remains a scientific
   persistence judgement -- not fatal and not KILL. A reproducible protein-level
   near / marked loss is surfaced at most as a machine-local ``fatal_review =
   POTENTIAL_FATAL_PATTERN``.
3. Only reproducible DIRECT-class protein near / marked loss may surface
   POTENTIAL_FATAL_PATTERN; reproducibility is Route A (an auditable explicit
   reproducibility qualification) or Route B (convergent NEAR_LOSS_OR_MARKED_LOSS
   across at least two independent qualified persistence-context identities),
   remains human-reviewable, and the Module never decides fatality. No numeric or
   ranking score anywhere; ``assay_method`` is an OPEN factual type while the
   ``protein_measurement_validation_status`` predicate is CLOSED.
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

from .completion import ClinicalPersistenceCompletion

# --- identity ---------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT03"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-03"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
#: The fixed Instantiation's frozen scientific context (PR D
#: crc_adc_target_gateset.yaml context_id / context_version). The Module must not
#: run against any other context (E9 item 10: no implicit default context). This
#: canonical context_id is a SEPARATE namespace from the LOCAL
#: ``persistence_context_id`` on each observation (E9 blocker-2 gene).
CONTEXT_ID: Final[str] = "CTX-CRC-REFRACTORY-MCRC"
CONTEXT_VERSION: Final[int] = 1
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-03 contract. Reproduced only by the PROPOSAL
#: layer -- never stamped onto a Gate-neutral EvidencePackage.
TGT03_EVIDENCE_CEILING: Final[str] = (
    "protein-level target retention in refractory / prior-treated and/or "
    "metastatic CRC with malignant-cell attribution"
)
TGT03_GATE_QUESTION: Final[str] = (
    "Does target expression persist in the actual clinical setting: refractory / "
    "prior-treated and/or metastatic CRC (including colorectal liver metastases)?"
)

_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ----------------------------------------------------------------

#: What a normalized persistence observation IS. The provider supplies normalized
#: upstream facts only -- it never sets a rung, a direction, or a
#: persistence-implication (E10-2).
OBSERVATION_KIND_VALUES: Final[tuple[str, ...]] = (
    "REFRACTORY_OR_PRIOR_TREATED_PROTEIN",
    "METASTATIC_LESION_PROTEIN",
    "PAIRED_PRE_POST_PROTEIN",
    "TREATED_METASTATIC_TRANSCRIPT",
    "RESISTANCE_MODEL",
    "TREATMENT_NAIVE_PRIMARY",
    "DIFFERENT_TUMOR_TYPE",
    "SEARCH_COMPLETION_AUDIT",
)
#: The clinical protein kinds that can carry a DIRECT-rung observation.
_CLINICAL_PROTEIN_KINDS: Final[tuple[str, ...]] = (
    "REFRACTORY_OR_PRIOR_TREATED_PROTEIN",
    "METASTATIC_LESION_PROTEIN",
    "PAIRED_PRE_POST_PROTEIN",
)

MOLECULAR_LAYER_VALUES: Final[tuple[str, ...]] = ("", "PROTEIN", "TRANSCRIPT", "BOTH")

#: The measurement-validation PREDICATE that lets a protein observation drive
#: DIRECT. CLOSED enum (E9 blocker-3 gene). ``assay_method`` itself stays an OPEN
#: factual type -- there is no closed assay whitelist.
PROTEIN_MEASUREMENT_VALIDATION_STATUS_VALUES: Final[tuple[str, ...]] = (
    "",
    "QUALIFIED",
    "NOT_ESTABLISHED",
)

#: The qualified clinical-persistence context of an observation. Must match the
#: observation kind for a rung-bearing kind.
CLINICAL_CONTEXT_VALUES: Final[tuple[str, ...]] = (
    "",
    "REFRACTORY_OR_PRIOR_TREATED",
    "METASTATIC_CRC",
    "PAIRED_PRE_POST",
    "RESISTANCE_MODEL",
    "TREATMENT_NAIVE_PRIMARY",
    "DIFFERENT_TUMOR_TYPE",
)
_CLINICAL_PROTEIN_CONTEXTS: Final[tuple[str, ...]] = (
    "REFRACTORY_OR_PRIOR_TREATED",
    "METASTATIC_CRC",
    "PAIRED_PRE_POST",
)
_KIND_TO_CONTEXT: Final[dict[str, str]] = {
    "REFRACTORY_OR_PRIOR_TREATED_PROTEIN": "REFRACTORY_OR_PRIOR_TREATED",
    "METASTATIC_LESION_PROTEIN": "METASTATIC_CRC",
    "PAIRED_PRE_POST_PROTEIN": "PAIRED_PRE_POST",
    "TREATED_METASTATIC_TRANSCRIPT": "METASTATIC_CRC",
    "RESISTANCE_MODEL": "RESISTANCE_MODEL",
    "TREATMENT_NAIVE_PRIMARY": "TREATMENT_NAIVE_PRIMARY",
    "DIFFERENT_TUMOR_TYPE": "DIFFERENT_TUMOR_TYPE",
}

CONTEXT_ADEQUACY_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")
MALIGNANT_ATTRIBUTION_VALUES: Final[tuple[str, ...]] = (
    "MALIGNANT",
    "NON_MALIGNANT",
    "UNRESOLVED",
)

#: The upstream-qualified factual persistence state (E9 item 06). NEVER computed
#: by the Module from a fold-change, a percent-positive value or an H-score.
PERSISTENCE_PATTERN_VALUES: Final[tuple[str, ...]] = (
    "",
    "RETAINED",
    "NEAR_LOSS_OR_MARKED_LOSS",
    "TRANSIENT_OR_MINOR_DOWNREGULATION",
    "MIXED_OR_UNRESOLVED",
)
_LOSS_PATTERN = "NEAR_LOSS_OR_MARKED_LOSS"
_TRANSIENT_PATTERN = "TRANSIENT_OR_MINOR_DOWNREGULATION"
_BASIS_REQUIRED_PATTERNS: Final[tuple[str, ...]] = (_LOSS_PATTERN, _TRANSIENT_PATTERN)

PERSISTENCE_PATTERN_BASIS_VALUES: Final[tuple[str, ...]] = (
    "",
    "SOURCE_REPORTED",
    "HUMAN_REVIEWED_NORMALIZATION",
)

#: The typed fact that decides the TRANSIENT_OR_MINOR_DOWNREGULATION
#: SUPPORTING-vs-CONTEXTUAL branch (E9 blocker-1 gene). The branch is decided
#: ONLY by this field, never by free-text parsing of the basis prose.
RESIDUAL_TARGET_PRESENCE_STATUS_VALUES: Final[tuple[str, ...]] = ("", "PRESENT", "UNRESOLVED")

REPRODUCIBILITY_STATUS_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")

#: The Evidence-Ladder rung the Module maps an observation to (frozen PR D).
EVIDENCE_RUNG_VALUES: Final[tuple[str, ...]] = ("", "DIRECT", "INDIRECT_STRONG", "WEAK")

#: Module-assigned Gate-relative reading of a rung-classed observation.
PERSISTENCE_IMPLICATION_VALUES: Final[tuple[str, ...]] = (
    "",
    "SUPPORTS_PERSISTENCE",
    "OPPOSES_PERSISTENCE",
    "CONTEXTUAL",
)
_IMPLICATION_TO_ROLE: Final[dict[str, str]] = {
    "SUPPORTS_PERSISTENCE": "SUPPORTING",
    "OPPOSES_PERSISTENCE": "CONTRADICTING",
    "CONTEXTUAL": "CONTEXTUAL",
}

FATAL_REVIEW_STATUS_VALUES: Final[tuple[str, ...]] = ("", "POTENTIAL_FATAL_PATTERN")

CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

#: The only Direction x Strength pairs MOD-TGT03 may propose (frozen E9 item 06
#: truth table + E10-8). There is NO ``INCONCLUSIVE / WEAK`` -- a WEAK-only public
#: landscape is INCONCLUSIVE / UNKNOWN.
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


# --- provider output: normalized persistence observation ------------------

@dataclass(frozen=True)
class NormalizedPersistenceObservation:
    """One already-normalized, primary/repository-source-resolved TGT-03
    clinical-persistence observation. NORMALIZED UPSTREAM FACTS only -- the
    provider never sets a rung, a direction, or a persistence implication
    (E10-2). ``assay_method`` is an OPEN factual type;
    ``protein_measurement_validation_status`` is the CLOSED predicate."""

    observation_id: str
    target_identity: str
    context_key: str
    landscape_as_of: str
    observation_kind: str
    molecular_layer: str
    assay_method: str
    protein_measurement_validation_status: str
    protein_measurement_validation_basis: str
    crc_specific: bool
    clinical_context: str
    clinical_context_basis: str
    context_adequacy_status: str
    context_adequacy_basis: str
    malignant_cell_attribution: str
    malignant_attribution_basis: str
    persistence_pattern: str
    persistence_pattern_basis: str
    residual_target_presence_status: str
    residual_target_presence_basis: str
    reproducibility_status: str
    reproducibility_basis: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    primary_or_repository_source_resolved: bool
    persistence_context_id: str = ""
    persistence_context_ids: tuple[str, ...] = ()
    declared_multi_context_analysis: bool = False
    # --- SEARCH_COMPLETION_AUDIT-specific structured snapshot (E10-5 gene) ----
    #  the snapshot field names ARE the typed completion's field names.
    audit_search_scope: str = ""
    audit_sources_searched: tuple[str, ...] = ()
    audit_landscape_as_of: str = ""
    audit_public_persistence_search_complete: bool = False
    audit_refractory_prior_treated_search_complete: bool = False
    audit_metastatic_lesion_search_complete: bool = False
    audit_paired_pre_post_search_complete: bool = False
    audit_resistance_model_search_complete: bool = False
    audit_unresolved_item_keys: tuple[str, ...] = ()
    audit_qualifying_direct_persistence_context_ids: tuple[str, ...] = ()
    audit_qualifying_indirect_persistence_context_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _pattern(self.observation_id, _OBS_ID, "observation_id")
        _text(self.target_identity, "target_identity")
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _choice(self.observation_kind, OBSERVATION_KIND_VALUES, "observation_kind")
        _choice(self.molecular_layer, MOLECULAR_LAYER_VALUES, "molecular_layer")
        _text(self.assay_method, "assay_method", allow_empty=True)
        _choice(
            self.protein_measurement_validation_status,
            PROTEIN_MEASUREMENT_VALIDATION_STATUS_VALUES,
            "protein_measurement_validation_status",
        )
        _text(
            self.protein_measurement_validation_basis,
            "protein_measurement_validation_basis",
            allow_empty=True,
        )
        _bool(self.crc_specific, "crc_specific")
        _choice(self.clinical_context, CLINICAL_CONTEXT_VALUES, "clinical_context")
        _text(self.clinical_context_basis, "clinical_context_basis", allow_empty=True)
        _choice(self.context_adequacy_status, CONTEXT_ADEQUACY_VALUES, "context_adequacy_status")
        _text(self.context_adequacy_basis, "context_adequacy_basis", allow_empty=True)
        _choice(
            self.malignant_cell_attribution,
            MALIGNANT_ATTRIBUTION_VALUES,
            "malignant_cell_attribution",
        )
        _text(self.malignant_attribution_basis, "malignant_attribution_basis", allow_empty=True)
        _choice(self.persistence_pattern, PERSISTENCE_PATTERN_VALUES, "persistence_pattern")
        _choice(
            self.persistence_pattern_basis,
            PERSISTENCE_PATTERN_BASIS_VALUES,
            "persistence_pattern_basis",
        )
        _choice(
            self.residual_target_presence_status,
            RESIDUAL_TARGET_PRESENCE_STATUS_VALUES,
            "residual_target_presence_status",
        )
        _text(
            self.residual_target_presence_basis,
            "residual_target_presence_basis",
            allow_empty=True,
        )
        _choice(self.reproducibility_status, REPRODUCIBILITY_STATUS_VALUES, "reproducibility_status")
        _text(self.reproducibility_basis, "reproducibility_basis", allow_empty=True)
        _text(self.claim, "claim")
        _pattern(self.source_id, _SRC_ID, "source_id")
        _choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _text(self.source_identifier, "source_identifier")
        _text(self.locator, "locator", allow_empty=True)
        _text(self.retrieved_at, "retrieved_at")
        if not _ISO_DATE_PREFIX.match(self.retrieved_at):
            raise ValueError("retrieved_at must start with an ISO date")
        _bool(self.primary_or_repository_source_resolved, "primary_or_repository_source_resolved")
        _text(self.persistence_context_id, "persistence_context_id", allow_empty=True)
        _str_tuple(
            self.persistence_context_ids, "persistence_context_ids"
        ) if self.persistence_context_ids else None
        _bool(self.declared_multi_context_analysis, "declared_multi_context_analysis")

        # --- local persistence-context namespace shape (E9 blocker-2 gene) ---
        # persistence_context_ids is the auditable context set of ONE declared
        # multi-context analysis -- it is only cross-context when the observation
        # itself declares the analysis.
        if self.persistence_context_ids and not self.declared_multi_context_analysis:
            raise ValueError(
                "persistence_context_ids is only set on a declared multi-context "
                "analysis (declared_multi_context_analysis must be true)"
            )
        if self.declared_multi_context_analysis:
            if len(set(self.persistence_context_ids)) < 2:
                raise ValueError(
                    "a declared multi-context analysis names at least two distinct "
                    "auditable persistence_context_ids"
                )
            if self.persistence_context_id.strip():
                raise ValueError(
                    "a declared multi-context analysis carries persistence_context_ids, "
                    "not a single persistence_context_id"
                )

        kind = self.observation_kind

        # --- cross-field shape by observation kind ---------------------------
        if kind in _CLINICAL_PROTEIN_KINDS:
            if self.molecular_layer not in ("PROTEIN", "BOTH"):
                raise ValueError(f"a {kind} observation is at the PROTEIN molecular layer")
        elif kind == "TREATED_METASTATIC_TRANSCRIPT":
            if self.molecular_layer != "TRANSCRIPT":
                raise ValueError(
                    "a TREATED_METASTATIC_TRANSCRIPT observation is at the TRANSCRIPT layer"
                )
        elif kind == "RESISTANCE_MODEL":
            if self.molecular_layer not in ("PROTEIN", "TRANSCRIPT", "BOTH"):
                raise ValueError("a RESISTANCE_MODEL observation carries a molecular layer")
        elif kind in ("TREATMENT_NAIVE_PRIMARY", "DIFFERENT_TUMOR_TYPE"):
            if self.molecular_layer not in ("PROTEIN", "TRANSCRIPT", "BOTH"):
                raise ValueError(f"a {kind} observation carries a molecular layer")
        elif kind == "SEARCH_COMPLETION_AUDIT":
            if self.assay_method != "SEARCH_AUDIT":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries assay_method SEARCH_AUDIT"
                )
            if self.molecular_layer != "":
                raise ValueError("a SEARCH_COMPLETION_AUDIT observation has no molecular layer")

        # a rung-bearing kind's clinical_context, when set, must match its kind.
        if kind in _KIND_TO_CONTEXT and self.clinical_context:
            if self.clinical_context != _KIND_TO_CONTEXT[kind]:
                raise ValueError(
                    f"a {kind} observation's clinical_context must be "
                    f"{_KIND_TO_CONTEXT[kind]!r}, got {self.clinical_context!r}"
                )

        # --- qualification-basis hygiene (E9 item 06 / 13) -----------------
        if self.malignant_cell_attribution == "MALIGNANT" and not self.malignant_attribution_basis.strip():
            raise ValueError(
                "a MALIGNANT malignant_cell_attribution carries an auditable "
                "malignant_attribution_basis"
            )
        if self.context_adequacy_status == "QUALIFIED" and (
            not self.context_adequacy_basis.strip() or not self.clinical_context_basis.strip()
        ):
            raise ValueError(
                "a QUALIFIED context_adequacy_status carries an auditable "
                "clinical_context_basis AND context_adequacy_basis"
            )
        if self.protein_measurement_validation_status == "QUALIFIED" and not self.protein_measurement_validation_basis.strip():
            raise ValueError(
                "a QUALIFIED protein_measurement_validation_status carries a non-empty "
                "auditable protein_measurement_validation_basis"
            )
        if self.persistence_pattern in _BASIS_REQUIRED_PATTERNS and not self.persistence_pattern_basis:
            raise ValueError(
                "a NEAR_LOSS_OR_MARKED_LOSS / TRANSIENT_OR_MINOR_DOWNREGULATION "
                "persistence_pattern carries a persistence_pattern_basis "
                "(SOURCE_REPORTED / HUMAN_REVIEWED_NORMALIZATION)"
            )
        if self.persistence_pattern_basis and not self.persistence_pattern:
            raise ValueError("a persistence_pattern_basis without a persistence_pattern is drift")

        # --- the transient / minor branch fact (E9 blocker-1 gene) --------
        if self.persistence_pattern == _TRANSIENT_PATTERN:
            if self.residual_target_presence_status not in ("PRESENT", "UNRESOLVED"):
                raise ValueError(
                    "a TRANSIENT_OR_MINOR_DOWNREGULATION observation carries "
                    "residual_target_presence_status in {PRESENT, UNRESOLVED}"
                )
            if self.residual_target_presence_status == "PRESENT" and not self.residual_target_presence_basis.strip():
                raise ValueError(
                    "residual_target_presence_status == PRESENT carries an auditable "
                    "residual_target_presence_basis"
                )
        elif self.residual_target_presence_status:
            raise ValueError(
                "residual_target_presence_status is set only on a "
                "TRANSIENT_OR_MINOR_DOWNREGULATION observation (drift otherwise)"
            )

        if self.reproducibility_status == "QUALIFIED" and not self.reproducibility_basis.strip():
            raise ValueError(
                "a QUALIFIED reproducibility_status carries an auditable reproducibility_basis"
            )

        # --- audit-snapshot shape (E10-5 gene) ---------------------------
        _text(self.audit_search_scope, "audit_search_scope", allow_empty=True)
        for name in (
            "audit_sources_searched",
            "audit_unresolved_item_keys",
            "audit_qualifying_direct_persistence_context_ids",
            "audit_qualifying_indirect_persistence_context_ids",
        ):
            _str_tuple(getattr(self, name), name) if getattr(self, name) else None
        _text(self.audit_landscape_as_of, "audit_landscape_as_of", allow_empty=True)
        for name in (
            "audit_public_persistence_search_complete",
            "audit_refractory_prior_treated_search_complete",
            "audit_metastatic_lesion_search_complete",
            "audit_paired_pre_post_search_complete",
            "audit_resistance_model_search_complete",
        ):
            _bool(getattr(self, name), name)
        _any_audit_field = (
            bool(self.audit_search_scope.strip())
            or bool(self.audit_sources_searched)
            or bool(self.audit_landscape_as_of.strip())
            or self.audit_public_persistence_search_complete
            or self.audit_refractory_prior_treated_search_complete
            or self.audit_metastatic_lesion_search_complete
            or self.audit_paired_pre_post_search_complete
            or self.audit_resistance_model_search_complete
            or bool(self.audit_unresolved_item_keys)
            or bool(self.audit_qualifying_direct_persistence_context_ids)
            or bool(self.audit_qualifying_indirect_persistence_context_ids)
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
    def persistence_context_identities(self) -> tuple[str, ...]:
        """Every distinct auditable LOCAL persistence-context identity this
        observation represents: its ``persistence_context_ids`` ONLY when it
        declares a multi-context analysis, else its single
        ``persistence_context_id``. A LOCAL namespace, never the canonical
        Instantiation context_id."""

        if self.declared_multi_context_analysis and self.persistence_context_ids:
            seen: list[str] = []
            for cid in self.persistence_context_ids:
                if cid not in seen:
                    seen.append(cid)
            return tuple(seen)
        return (self.persistence_context_id,) if self.persistence_context_id.strip() else ()

    @property
    def is_protein_layer(self) -> bool:
        return self.molecular_layer in ("PROTEIN", "BOTH")

    @property
    def is_malignant_attributed(self) -> bool:
        return self.malignant_cell_attribution == "MALIGNANT"

    @property
    def is_context_qualified(self) -> bool:
        return self.context_adequacy_status == "QUALIFIED"

    @property
    def is_protein_measurement_qualified(self) -> bool:
        return self.protein_measurement_validation_status == "QUALIFIED"

    @property
    def is_loss_pattern(self) -> bool:
        return self.persistence_pattern == _LOSS_PATTERN

    @property
    def is_reproducibility_qualified(self) -> bool:
        return (
            self.reproducibility_status == "QUALIFIED"
            and bool(self.reproducibility_basis.strip())
        )


# --- classification ------------------------------------------------------

@dataclass(frozen=True)
class ClassifiedPersistenceObservation:
    """A provider observation placed into a FROZEN TGT-03 Evidence-Ladder rung
    and given a Module-owned Gate-relative persistence-implication reading. The
    provider never sets ``evidence_rung`` or ``persistence_implication``.
    ``qualifying_for_direct`` / ``qualifying_for_indirect`` are RUNG-SPECIFIC
    (E9 item 06 ``qualifying_is_rung_specific``)."""

    observation: NormalizedPersistenceObservation
    admissible: bool
    rejection_reason: str
    rejection_severity: str  # "" when admissible; else "HARD" | "SOFT"
    evidence_rung: str       # "" | DIRECT | INDIRECT_STRONG | WEAK
    persistence_implication: str  # "" | SUPPORTS_PERSISTENCE | OPPOSES_PERSISTENCE | CONTEXTUAL
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
            _choice(
                self.persistence_implication,
                PERSISTENCE_IMPLICATION_VALUES,
                "persistence_implication",
            )
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
            if self.evidence_rung or self.persistence_implication:
                raise ValueError("a rejected observation has no rung or persistence implication")
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
        return self.admissible and self.persistence_implication in (
            "SUPPORTS_PERSISTENCE",
            "OPPOSES_PERSISTENCE",
        )

    @property
    def is_qualifying(self) -> bool:
        return self.qualifying_for_direct or self.qualifying_for_indirect


# --- emitted evidence (one observation -> one canonical EP) --------------

@dataclass(frozen=True)
class EmittedEvidence:
    classified: ClassifiedPersistenceObservation
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedPersistenceObservation):
            raise ValueError("classified must be a ClassifiedPersistenceObservation")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")

    @property
    def observation(self) -> NormalizedPersistenceObservation:
        return self.classified.observation


# --- fatal review (E9 item 08 / 12): a machine review TRIGGER -----------

@dataclass(frozen=True)
class FatalReviewRecord:
    """Non-canonical, module-local, on the run result only. NOT a proposal
    field, NOT a CandidateGateAssessment field, NOT a core object, NOT a
    Decision, NOT a Gate fatal flag. ``status`` has ONE non-empty value; the
    machine NEVER emits PUBLIC_FATAL_SIGNAL_ESTABLISHED / a canonical fatal flag
    / KILL / HOLD / Decision, and NEVER decides whether the pattern is a real
    fatal signal -- that is human review + the GateSet fatal policy.

    ``required`` is true iff, on a completed audited landscape, one or more
    eligible DIRECT-class protein NEAR_LOSS_OR_MARKED_LOSS observations meet
    Route A (an auditable explicit reproducibility qualification) OR Route B
    (>= 2 independent qualified persistence-context identities)."""

    required: bool
    status: str  # "" | POTENTIAL_FATAL_PATTERN
    evidence_ids: tuple[str, ...]
    persistence_context_ids: tuple[str, ...]
    persistence_class: tuple[str, ...]
    context_qualification_basis_refs: tuple[str, ...]
    persistence_pattern_basis_refs: tuple[str, ...]
    reproducibility_basis_refs: tuple[str, ...]
    landscape_as_of: str
    persistence_search_scope: str

    def __post_init__(self) -> None:
        _bool(self.required, "required")
        _choice(self.status, FATAL_REVIEW_STATUS_VALUES, "status")
        if self.required != (self.status == "POTENTIAL_FATAL_PATTERN"):
            raise ValueError("required is true iff status == POTENTIAL_FATAL_PATTERN")
        for evidence_id in self.evidence_ids:
            _pattern(evidence_id, _EP_ID, "fatal_review.evidence_ids[]")
        for name in (
            "persistence_context_ids",
            "persistence_class",
            "context_qualification_basis_refs",
            "persistence_pattern_basis_refs",
            "reproducibility_basis_refs",
        ):
            for item in getattr(self, name):
                _text(item, f"fatal_review.{name}[]")
        _text(self.landscape_as_of, "fatal_review.landscape_as_of", allow_empty=not self.required)
        _text(
            self.persistence_search_scope,
            "fatal_review.persistence_search_scope",
            allow_empty=not self.required,
        )
        if self.required:
            if not self.evidence_ids:
                raise ValueError("a POTENTIAL_FATAL_PATTERN carries its contributing evidence")
            for c in self.persistence_class:
                _choice(c, (_LOSS_PATTERN,), "fatal_review.persistence_class[]")
            if not self.persistence_class:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the NEAR_LOSS_OR_MARKED_LOSS class"
                )
            if not self.context_qualification_basis_refs or not self.persistence_pattern_basis_refs:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the context-qualification and "
                    "persistence-pattern basis refs"
                )
            # Route A OR Route B: at least two independent persistence-context
            # identities (Route B), OR a reproducibility_basis_ref (Route A).
            if len(set(self.persistence_context_ids)) < 2 and not self.reproducibility_basis_refs:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN needs Route A (a reproducibility_basis_ref) "
                    "OR Route B (>= 2 independent persistence_context_ids)"
                )
        else:
            for name in (
                "evidence_ids",
                "persistence_context_ids",
                "persistence_class",
                "context_qualification_basis_refs",
                "persistence_pattern_basis_refs",
                "reproducibility_basis_refs",
            ):
                if getattr(self, name):
                    raise ValueError(f"fatal_review.{name} is empty when required is false")

    @staticmethod
    def none() -> "FatalReviewRecord":
        return FatalReviewRecord(False, "", (), (), (), (), (), (), "", "")


# --- module input --------------------------------------------------------

@dataclass(frozen=True)
class Tgt03ModuleInput:
    """Everything the module needs to run one (candidate, TGT-03) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the SINGLE
    authoritative identity (MOD-TGT01 / PR E2 gene). There is no second
    drift-prone target argument and no implicit default scientific context
    (E9 item 10). ``context_id`` is the CANONICAL Instantiation context -- a
    SEPARATE namespace from each observation's LOCAL persistence_context_id."""

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
    persistence_search_scope: str
    existing_evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _text(self.candidate_name, "candidate_name")
        _text(self.target_identity, "target_identity")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        if self.instantiation_id != INSTANTIATION_ID:
            raise ValueError(f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT03")
        _pattern(self.context_id, _CTX_ID, "context_id")
        if self.context_id != CONTEXT_ID:
            raise ValueError(
                f"context_id must be {CONTEXT_ID!r} for the fixed TGT-03 Instantiation "
                "-- there is no implicit default scientific context (E9 item 10)"
            )
        _positive_int(self.context_version, "context_version")
        if self.context_version != CONTEXT_VERSION:
            raise ValueError(
                f"context_version must be {CONTEXT_VERSION} for the fixed TGT-03 Instantiation"
            )
        if self.gateset_id != GATESET_ID:
            raise ValueError(f"gateset_id must be {GATESET_ID!r}")
        if self.gateset_version != GATESET_VERSION:
            raise ValueError(f"gateset_version must be {GATESET_VERSION!r}")
        if self.gate_id != GATE_ID:
            raise ValueError(f"gate_id must be {GATE_ID!r}")
        if self.gate_version != GATE_VERSION:
            raise ValueError(f"gate_version must be {GATE_VERSION!r}")
        if self.evidence_regime != "PUBLIC_ONLY":
            raise ValueError("evidence_regime must be PUBLIC_ONLY for the current TGT-03 instantiation")
        _text(self.run_id, "run_id")
        _text(self.code_commit, "code_commit", allow_empty=True)
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError(
                "landscape_as_of must start with an ISO date -- a landscape with no as_of "
                "is not admissible"
            )
        _text(self.persistence_search_scope, "persistence_search_scope")
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


# --- proposal envelope (E9 item 12) ------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Carries the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` AND any TGT-02 /
    TGT-04 conclusion AND any fatal flag (the potential-fatal-pattern signal
    lives in the module-local ``fatal_review`` record)."""

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
        if self.context_id != CONTEXT_ID:
            raise ValueError(
                f"context_id must be the canonical Instantiation context {CONTEXT_ID!r}"
            )
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
                "is not a legal TGT-03 pair (note: there is no INCONCLUSIVE / WEAK)"
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
        if self.evidence_ceiling != TGT03_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-03 ceiling verbatim")

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
class Tgt03ModuleRunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]  # newly created only
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    persistence_completion: ClinicalPersistenceCompletion
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
        if not isinstance(self.persistence_completion, ClinicalPersistenceCompletion):
            raise ValueError("persistence_completion must be a ClinicalPersistenceCompletion")
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
        # actionable (E6 / E8 / E10 gene).
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
    """The HIGHEST qualifying frozen evidence class actually met (E9 item 06
    ``strength_is_the_highest_qualifying_evidence_class``). There is NO E6-style
    two-axis weaker-ceiling rule. Returns "DIRECT" / "INDIRECT_STRONG" / ""."""

    if qualifying_direct:
        return "DIRECT"
    if qualifying_indirect:
        return "INDIRECT_STRONG"
    return ""


def pattern_to_implication(observation: NormalizedPersistenceObservation) -> str:
    """The frozen E9 item-06 mapping. The TRANSIENT_OR_MINOR_DOWNREGULATION
    SUPPORTING-vs-CONTEXTUAL branch is decided ONLY by
    ``residual_target_presence_status`` -- never by free-text parsing."""

    pattern = observation.persistence_pattern
    if pattern == "RETAINED":
        return "SUPPORTS_PERSISTENCE"
    if pattern == _LOSS_PATTERN:
        return "OPPOSES_PERSISTENCE"
    if pattern == _TRANSIENT_PATTERN:
        if observation.residual_target_presence_status == "PRESENT":
            return "SUPPORTS_PERSISTENCE"
        return "CONTEXTUAL"
    # MIXED_OR_UNRESOLVED or unqualified
    return "CONTEXTUAL"
