"""Frozen input / output contracts for MOD-TGT04.

Runtime Migration PR E12. In-memory contract values handed between the
deterministic Gate-specific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments.

Three invariants this module must never break (frozen PR E11 contract + ChatGPT
AI审核方案 E12):

1. Surface localization is not antigen density. An INDIRECT_STRONG localization
   observation (validated membranous IHC / cell-surface proteomics on CRC
   malignant cells) supports the allowed inference "the antigen is on the cell
   surface" but NEVER a Gate-level proposed Strength; a localization-only
   completed landscape is INCONCLUSIVE / UNKNOWN on the density question.
2. Quantitative values are evidence, not thresholds. A raw
   ``reported_density_value`` / ``reported_density_unit`` /
   ``reported_density_summary`` is an opaque factual string preserved for human
   drill-down and a SYMMETRIC exact-reuse identity key; the Module NEVER coerces
   it to a number, converts a unit, or compares it to any threshold / cutoff /
   invented "clinically effective range". Density plausibility arrives only as an
   auditable upstream ``density_plausibility_status``.
3. A single quantitative NEGLIGIBLE_OR_UNDETECTABLE observation is a DIRECT-class
   OPPOSES_DENSITY_PLAUSIBILITY observation -- NOT yet a NEGATIVE / DIRECT
   proposal and NOT a reproducible fatal pattern. Only a reproducible (Route A /
   Route B) quantitative NEGLIGIBLE_OR_UNDETECTABLE surface antigen on CRC
   MALIGNANT CELLS may surface a machine-local ``fatal_review =
   POTENTIAL_FATAL_PATTERN``; a well-matched CRC model observation may drive an
   ordinary DIRECT Direction but is NEVER a fatal contributor. LOW_BUT_PRESENT is
   never fatal and never automatically NEGATIVE. ``assay_method`` is an OPEN
   factual type while ``measurement_validation_status`` is CLOSED; no numeric or
   ranking score anywhere; the Module never decides fatality or ADC efficacy.
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

from .completion import SurfaceAvailabilityCompletion

# --- identity ---------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT04"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-04"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
#: The fixed Instantiation's frozen scientific context (PR D
#: crc_adc_target_gateset.yaml context_id / context_version). The Module must not
#: run against any other context (E11 item 10: no implicit default context). This
#: canonical context_id is a SEPARATE namespace from the LOCAL
#: ``surface_context_id`` on each observation (E10 identity-namespace gene).
CONTEXT_ID: Final[str] = "CTX-CRC-REFRACTORY-MCRC"
CONTEXT_VERSION: Final[int] = 1
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-04 contract. Reproduced only by the PROPOSAL
#: layer -- never stamped onto a Gate-neutral EvidencePackage.
TGT04_EVIDENCE_CEILING: Final[str] = (
    "quantitative cell-surface antigen density on CRC malignant cells; surface "
    "localization alone does not reach it"
)
TGT04_GATE_QUESTION: Final[str] = (
    "Is the target present on the cell surface of CRC malignant cells at a "
    "density plausibly adequate for ADC payload delivery?"
)

_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ----------------------------------------------------------------

#: What a normalized surface observation IS. The provider supplies normalized
#: upstream facts only -- it never sets a rung, a direction, or a
#: density-implication (E12-2).
OBSERVATION_KIND_VALUES: Final[tuple[str, ...]] = (
    "QUANTITATIVE_SURFACE_DENSITY",
    "MEMBRANOUS_IHC",
    "SURFACE_PROTEOMICS",
    "SUBCELLULAR_LOCALIZATION",
    "TOPOLOGY_OR_GO_PREDICTION",
    "NON_CRC_SURFACE_EVIDENCE",
    "RNA_SURFACE_PROXY",
    "SEARCH_COMPLETION_AUDIT",
)
#: The only kind that can carry a DIRECT-rung observation.
_DIRECT_KIND: Final[str] = "QUANTITATIVE_SURFACE_DENSITY"
#: The kinds that can carry an INDIRECT_STRONG localization observation.
_INDIRECT_STRONG_KINDS: Final[tuple[str, ...]] = ("MEMBRANOUS_IHC", "SURFACE_PROTEOMICS")
#: The kinds that are WEAK-only, whatever they measure.
_WEAK_KINDS: Final[tuple[str, ...]] = (
    "SUBCELLULAR_LOCALIZATION",
    "TOPOLOGY_OR_GO_PREDICTION",
    "NON_CRC_SURFACE_EVIDENCE",
    "RNA_SURFACE_PROXY",
)

MOLECULAR_LAYER_VALUES: Final[tuple[str, ...]] = ("", "PROTEIN", "TRANSCRIPT", "BOTH")

#: The measurement-validation PREDICATE that lets a quantitative surface-density
#: observation drive DIRECT. CLOSED enum -- STRICTLY {QUALIFIED, NOT_ESTABLISHED}
#: with no invented blank state; a non-density / audit observation carries
#: NOT_ESTABLISHED. ``assay_method`` itself stays an OPEN factual type -- there is
#: no closed assay whitelist -- but a DIRECT-rung density observation still needs
#: a non-empty factual ``assay_method``.
MEASUREMENT_VALIDATION_STATUS_VALUES: Final[tuple[str, ...]] = (
    "QUALIFIED",
    "NOT_ESTABLISHED",
)

#: The qualified surface context of an observation (E11 item 06). The "or
#: well-matched CRC models" permission is DIRECT-only; an INDIRECT_STRONG
#: localization rung requires CRC_MALIGNANT_CELLS.
SURFACE_CONTEXT_CLASS_VALUES: Final[tuple[str, ...]] = (
    "",
    "CRC_MALIGNANT_CELLS",
    "WELL_MATCHED_CRC_MODEL",
    "NON_CRC_MODEL",
    "UNRESOLVED",
)
#: surface_context_class values that CAN carry a DIRECT rung (E12-3 + tightening 1).
_DIRECT_CONTEXT_CLASSES: Final[tuple[str, ...]] = (
    "CRC_MALIGNANT_CELLS",
    "WELL_MATCHED_CRC_MODEL",
)

CONTEXT_ADEQUACY_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")
MALIGNANT_ATTRIBUTION_VALUES: Final[tuple[str, ...]] = (
    "MALIGNANT",
    "NON_MALIGNANT",
    "UNRESOLVED",
)

#: The typed localization fact (E11 item 06). NEVER an antigen-density claim.
SURFACE_LOCALIZATION_STATUS_VALUES: Final[tuple[str, ...]] = (
    "",
    "SURFACE_LOCALIZED",
    "NOT_SURFACE_LOCALIZED",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
)

#: The upstream-qualified factual density-plausibility state (E11 item 06). NEVER
#: computed by the Module from a molecules-per-cell value, an ABC value or an
#: H-score.
DENSITY_PLAUSIBILITY_STATUS_VALUES: Final[tuple[str, ...]] = (
    "",
    "PLAUSIBLY_ADEQUATE",
    "NOT_PLAUSIBLY_ADEQUATE",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
)
DENSITY_PLAUSIBILITY_BASIS_VALUES: Final[tuple[str, ...]] = (
    "",
    "SOURCE_REPORTED",
    "HUMAN_REVIEWED_NORMALIZATION",
)

#: The factual antigen-level class, frozen SEPARATELY for the fatal path so
#: LOW_BUT_PRESENT is never silently equated with NOT_PLAUSIBLY_ADEQUATE
#: (E11 item 06).
SURFACE_ANTIGEN_LEVEL_VALUES: Final[tuple[str, ...]] = (
    "",
    "QUANTITATIVELY_PRESENT",
    "LOW_BUT_PRESENT",
    "NEGLIGIBLE_OR_UNDETECTABLE",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
)
_NEGLIGIBLE = "NEGLIGIBLE_OR_UNDETECTABLE"

REPRODUCIBILITY_STATUS_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")

#: The Evidence-Ladder rung the Module maps an observation to (frozen PR D).
EVIDENCE_RUNG_VALUES: Final[tuple[str, ...]] = ("", "DIRECT", "INDIRECT_STRONG", "WEAK")

#: Module-assigned Gate-relative reading of a rung-classed observation. A
#: qualifying INDIRECT_STRONG localization observation is CONTEXTUAL -- it never
#: gets a directional density_implication (E12-3).
DENSITY_IMPLICATION_VALUES: Final[tuple[str, ...]] = (
    "",
    "SUPPORTS_DENSITY_PLAUSIBILITY",
    "OPPOSES_DENSITY_PLAUSIBILITY",
    "CONTEXTUAL",
)

FATAL_REVIEW_STATUS_VALUES: Final[tuple[str, ...]] = ("", "POTENTIAL_FATAL_PATTERN")

CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

#: The only Direction x Strength pairs MOD-TGT04 may propose (frozen E11 item 06 --
#: exactly 5). TGT-04 is a TWO-TIER evidence architecture with a SINGLE-TIER
#: grading authority: only a qualifying DIRECT quantitative antigen-density
#: observation grants a graded Direction; INDIRECT_STRONG never becomes a proposed
#: Strength, and there is NO INCONCLUSIVE / WEAK.
LEGAL_DIRECTION_STRENGTH_PAIRS: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("POSITIVE", "DIRECT"),
        ("NEGATIVE", "DIRECT"),
        ("CONFLICTING", "DIRECT"),
        ("INCONCLUSIVE", "DIRECT"),
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


# --- provider output: normalized surface observation ---------------------

@dataclass(frozen=True)
class NormalizedSurfaceObservation:
    """One already-normalized, primary/repository-source-resolved TGT-04
    surface-availability observation. NORMALIZED UPSTREAM FACTS only -- the
    provider never sets a rung, a direction, or a density implication (E12-2).
    ``assay_method`` is an OPEN factual type; ``measurement_validation_status`` is
    the CLOSED predicate. ``reported_density_value`` / ``reported_density_unit`` /
    ``reported_density_summary`` are OPAQUE factual strings (empty = absent) --
    never coerced to a number (E12 tightening 4)."""

    observation_id: str
    target_identity: str
    context_key: str
    landscape_as_of: str
    observation_kind: str
    molecular_layer: str
    assay_method: str
    measurement_validation_status: str
    measurement_validation_basis: str
    crc_specific: bool
    surface_context_class: str
    surface_context_basis: str
    context_adequacy_status: str
    context_adequacy_basis: str
    malignant_cell_attribution: str
    malignant_attribution_basis: str
    surface_localization_status: str
    surface_localization_basis: str
    density_plausibility_status: str
    density_plausibility_basis: str
    surface_antigen_level: str
    surface_antigen_level_basis: str
    reproducibility_status: str
    reproducibility_basis: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    primary_or_repository_source_resolved: bool
    surface_context_id: str = ""
    surface_context_ids: tuple[str, ...] = ()
    declared_multi_context_analysis: bool = False
    reported_density_value: str = ""
    reported_density_unit: str = ""
    reported_density_summary: str = ""
    # --- SEARCH_COMPLETION_AUDIT-specific structured snapshot (E12-5 gene) ----
    #  the snapshot field names ARE the typed completion's field names.
    audit_search_scope: str = ""
    audit_sources_searched: tuple[str, ...] = ()
    audit_landscape_as_of: str = ""
    audit_public_surface_search_complete: bool = False
    audit_quantitative_surface_density_search_complete: bool = False
    audit_membranous_ihc_search_complete: bool = False
    audit_surface_proteomics_search_complete: bool = False
    audit_subcellular_localization_search_complete: bool = False
    audit_unresolved_item_keys: tuple[str, ...] = ()
    audit_qualifying_direct_surface_context_ids: tuple[str, ...] = ()
    audit_qualifying_indirect_surface_context_ids: tuple[str, ...] = ()

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
            self.measurement_validation_status,
            MEASUREMENT_VALIDATION_STATUS_VALUES,
            "measurement_validation_status",
        )
        _text(
            self.measurement_validation_basis,
            "measurement_validation_basis",
            allow_empty=True,
        )
        _bool(self.crc_specific, "crc_specific")
        _choice(self.surface_context_class, SURFACE_CONTEXT_CLASS_VALUES, "surface_context_class")
        _text(self.surface_context_basis, "surface_context_basis", allow_empty=True)
        _choice(self.context_adequacy_status, CONTEXT_ADEQUACY_VALUES, "context_adequacy_status")
        _text(self.context_adequacy_basis, "context_adequacy_basis", allow_empty=True)
        _choice(
            self.malignant_cell_attribution,
            MALIGNANT_ATTRIBUTION_VALUES,
            "malignant_cell_attribution",
        )
        _text(self.malignant_attribution_basis, "malignant_attribution_basis", allow_empty=True)
        _choice(
            self.surface_localization_status,
            SURFACE_LOCALIZATION_STATUS_VALUES,
            "surface_localization_status",
        )
        _text(self.surface_localization_basis, "surface_localization_basis", allow_empty=True)
        _choice(
            self.density_plausibility_status,
            DENSITY_PLAUSIBILITY_STATUS_VALUES,
            "density_plausibility_status",
        )
        _choice(
            self.density_plausibility_basis,
            DENSITY_PLAUSIBILITY_BASIS_VALUES,
            "density_plausibility_basis",
        )
        _choice(self.surface_antigen_level, SURFACE_ANTIGEN_LEVEL_VALUES, "surface_antigen_level")
        _text(self.surface_antigen_level_basis, "surface_antigen_level_basis", allow_empty=True)
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
        _text(self.surface_context_id, "surface_context_id", allow_empty=True)
        _str_tuple(
            self.surface_context_ids, "surface_context_ids"
        ) if self.surface_context_ids else None
        _bool(self.declared_multi_context_analysis, "declared_multi_context_analysis")
        # --- raw density facts: OPAQUE strings, never coerced (E12 tightening 4)
        _text(self.reported_density_value, "reported_density_value", allow_empty=True)
        _text(self.reported_density_unit, "reported_density_unit", allow_empty=True)
        _text(self.reported_density_summary, "reported_density_summary", allow_empty=True)

        # --- local surface-context namespace shape (E10 identity-namespace gene;
        #     E12 tightening 2) ------------------------------------------------
        if self.surface_context_ids and not self.declared_multi_context_analysis:
            raise ValueError(
                "surface_context_ids is only set on a declared multi-context "
                "analysis (declared_multi_context_analysis must be true)"
            )
        if self.declared_multi_context_analysis:
            if len(set(self.surface_context_ids)) < 2:
                raise ValueError(
                    "a declared multi-context analysis names at least two distinct "
                    "auditable surface_context_ids"
                )
            if self.surface_context_id.strip():
                raise ValueError(
                    "a declared multi-context analysis carries surface_context_ids, "
                    "not a single surface_context_id"
                )
        # a LOCAL surface-context identity may NEVER be the canonical Instantiation
        # context_id -- collapsing the two namespaces is a HARD identity failure
        # (surfaced as a whole-run reject in module.py, but a provider that hands
        # one in at all is malformed).
        for cid in (self.surface_context_id, *self.surface_context_ids):
            if cid.strip() == CONTEXT_ID:
                raise ValueError(
                    "a local surface_context_id must never be the canonical "
                    f"Instantiation context_id {CONTEXT_ID!r} (namespace collapse)"
                )

        kind = self.observation_kind

        # --- cross-field shape by observation kind ---------------------------
        if kind == _DIRECT_KIND:
            if self.molecular_layer not in ("PROTEIN", "BOTH"):
                raise ValueError(
                    "a QUANTITATIVE_SURFACE_DENSITY observation is at the PROTEIN molecular layer"
                )
        elif kind in _INDIRECT_STRONG_KINDS:
            if self.molecular_layer not in ("PROTEIN", "BOTH"):
                raise ValueError(f"a {kind} observation is at the PROTEIN molecular layer")
        elif kind == "RNA_SURFACE_PROXY":
            if self.molecular_layer != "TRANSCRIPT":
                raise ValueError("an RNA_SURFACE_PROXY observation is at the TRANSCRIPT layer")
        elif kind in ("SUBCELLULAR_LOCALIZATION", "TOPOLOGY_OR_GO_PREDICTION", "NON_CRC_SURFACE_EVIDENCE"):
            if self.molecular_layer not in ("", "PROTEIN", "TRANSCRIPT", "BOTH"):
                raise ValueError(f"a {kind} observation carries a molecular layer or none")
        elif kind == "SEARCH_COMPLETION_AUDIT":
            if self.assay_method != "SEARCH_AUDIT":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries assay_method SEARCH_AUDIT"
                )
            if self.molecular_layer != "":
                raise ValueError("a SEARCH_COMPLETION_AUDIT observation has no molecular layer")

        # --- raw density facts only accompany a QUANTITATIVE_SURFACE_DENSITY obs
        if kind != _DIRECT_KIND and (
            self.reported_density_value.strip()
            or self.reported_density_unit.strip()
            or self.reported_density_summary.strip()
        ):
            raise ValueError(
                "reported_density_value / reported_density_unit / "
                "reported_density_summary are only carried by a "
                "QUANTITATIVE_SURFACE_DENSITY observation"
            )

        # --- factual-coherence guard (E12 tightening 1): a qualified CRC / model
        #     surface context can only be asserted for a crc_specific observation.
        #     crc_specific TRUE never grants a rung by itself -- this only stops a
        #     provider emitting mutually contradictory typed facts.
        if self.surface_context_class in _DIRECT_CONTEXT_CLASSES and not self.crc_specific:
            raise ValueError(
                f"surface_context_class {self.surface_context_class!r} requires "
                "crc_specific == true (typed-fact coherence)"
            )

        # --- qualification-basis hygiene (E11 item 06 / 13; E12-2 basis hygiene)
        if self.measurement_validation_status == "QUALIFIED" and not self.measurement_validation_basis.strip():
            raise ValueError(
                "a QUALIFIED measurement_validation_status carries a non-empty "
                "auditable measurement_validation_basis"
            )
        if self.measurement_validation_basis.strip() and self.measurement_validation_status == "NOT_ESTABLISHED":
            raise ValueError(
                "a measurement_validation_basis without a QUALIFIED "
                "measurement_validation_status is drift"
            )
        if self.context_adequacy_status == "QUALIFIED" and (
            not self.context_adequacy_basis.strip() or not self.surface_context_basis.strip()
        ):
            raise ValueError(
                "a QUALIFIED context_adequacy_status carries an auditable "
                "surface_context_basis AND context_adequacy_basis"
            )
        if self.context_adequacy_basis.strip() and self.context_adequacy_status == "NOT_ESTABLISHED":
            raise ValueError(
                "a context_adequacy_basis without a QUALIFIED context_adequacy_status is drift"
            )
        if self.malignant_cell_attribution == "MALIGNANT" and not self.malignant_attribution_basis.strip():
            raise ValueError(
                "a MALIGNANT malignant_cell_attribution carries an auditable "
                "malignant_attribution_basis"
            )
        # every asserted (non-sentinel) surface_localization_status carries a basis.
        if (
            self.surface_localization_status in ("SURFACE_LOCALIZED", "NOT_SURFACE_LOCALIZED", "MIXED_OR_UNRESOLVED")
            and not self.surface_localization_basis.strip()
        ):
            raise ValueError(
                "an asserted surface_localization_status carries an auditable surface_localization_basis"
            )
        if self.surface_localization_basis.strip() and self.surface_localization_status in ("", "NOT_ESTABLISHED"):
            raise ValueError(
                "a surface_localization_basis without an asserted surface_localization_status is drift"
            )
        # every asserted (non-sentinel) density_plausibility_status carries a
        # typed basis; it is NEVER computed by the Module from a number.
        if self.density_plausibility_status in ("PLAUSIBLY_ADEQUATE", "NOT_PLAUSIBLY_ADEQUATE", "MIXED_OR_UNRESOLVED"):
            if self.density_plausibility_basis not in ("SOURCE_REPORTED", "HUMAN_REVIEWED_NORMALIZATION"):
                raise ValueError(
                    "an asserted density_plausibility_status carries a typed "
                    "density_plausibility_basis (SOURCE_REPORTED / HUMAN_REVIEWED_NORMALIZATION)"
                )
        if self.density_plausibility_basis and self.density_plausibility_status in ("", "NOT_ESTABLISHED"):
            raise ValueError(
                "a density_plausibility_basis without an asserted density_plausibility_status is drift"
            )
        # every asserted (non-sentinel) surface_antigen_level carries a basis.
        if (
            self.surface_antigen_level in (
                "QUANTITATIVELY_PRESENT", "LOW_BUT_PRESENT", "NEGLIGIBLE_OR_UNDETECTABLE", "MIXED_OR_UNRESOLVED",
            )
            and not self.surface_antigen_level_basis.strip()
        ):
            raise ValueError(
                "an asserted surface_antigen_level carries an auditable surface_antigen_level_basis"
            )
        if self.surface_antigen_level_basis.strip() and self.surface_antigen_level in ("", "NOT_ESTABLISHED"):
            raise ValueError(
                "a surface_antigen_level_basis without an asserted surface_antigen_level is drift"
            )
        if self.reproducibility_status == "QUALIFIED" and not self.reproducibility_basis.strip():
            raise ValueError(
                "a QUALIFIED reproducibility_status carries an auditable reproducibility_basis"
            )
        if self.reproducibility_basis.strip() and self.reproducibility_status == "NOT_ESTABLISHED":
            raise ValueError(
                "a reproducibility_basis without a QUALIFIED reproducibility_status is drift"
            )

        # --- audit-snapshot shape (E12-5 gene) ---------------------------
        _text(self.audit_search_scope, "audit_search_scope", allow_empty=True)
        for name in (
            "audit_sources_searched",
            "audit_unresolved_item_keys",
            "audit_qualifying_direct_surface_context_ids",
            "audit_qualifying_indirect_surface_context_ids",
        ):
            _str_tuple(getattr(self, name), name) if getattr(self, name) else None
        _text(self.audit_landscape_as_of, "audit_landscape_as_of", allow_empty=True)
        for name in (
            "audit_public_surface_search_complete",
            "audit_quantitative_surface_density_search_complete",
            "audit_membranous_ihc_search_complete",
            "audit_surface_proteomics_search_complete",
            "audit_subcellular_localization_search_complete",
        ):
            _bool(getattr(self, name), name)
        _any_audit_field = (
            bool(self.audit_search_scope.strip())
            or bool(self.audit_sources_searched)
            or bool(self.audit_landscape_as_of.strip())
            or self.audit_public_surface_search_complete
            or self.audit_quantitative_surface_density_search_complete
            or self.audit_membranous_ihc_search_complete
            or self.audit_surface_proteomics_search_complete
            or self.audit_subcellular_localization_search_complete
            or bool(self.audit_unresolved_item_keys)
            or bool(self.audit_qualifying_direct_surface_context_ids)
            or bool(self.audit_qualifying_indirect_surface_context_ids)
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
    def surface_context_identities(self) -> tuple[str, ...]:
        """Every distinct auditable LOCAL surface-context identity this
        observation represents: its ``surface_context_ids`` ONLY when it declares
        a multi-context analysis, else its single ``surface_context_id``. A LOCAL
        namespace, never the canonical Instantiation context_id."""

        if self.declared_multi_context_analysis and self.surface_context_ids:
            seen: list[str] = []
            for cid in self.surface_context_ids:
                if cid not in seen:
                    seen.append(cid)
            return tuple(seen)
        return (self.surface_context_id,) if self.surface_context_id.strip() else ()

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
    def is_measurement_qualified(self) -> bool:
        return self.measurement_validation_status == "QUALIFIED"

    @property
    def is_surface_localized(self) -> bool:
        return self.surface_localization_status == "SURFACE_LOCALIZED"

    @property
    def is_negligible_antigen(self) -> bool:
        return self.surface_antigen_level == _NEGLIGIBLE

    @property
    def is_reproducibility_qualified(self) -> bool:
        return (
            self.reproducibility_status == "QUALIFIED"
            and bool(self.reproducibility_basis.strip())
        )


# --- classification ------------------------------------------------------

@dataclass(frozen=True)
class ClassifiedSurfaceObservation:
    """A provider observation placed into a FROZEN TGT-04 Evidence-Ladder rung
    and given a Module-owned Gate-relative density-implication reading. The
    provider never sets ``evidence_rung`` or ``density_implication``.
    ``qualifying_for_direct`` / ``qualifying_for_indirect`` are RUNG-SPECIFIC. A
    qualifying INDIRECT_STRONG localization observation is CONTEXTUAL -- it never
    gets a directional density_implication and never contributes to a Gate-level
    Direction or Strength (E12-3 / E12-4)."""

    observation: NormalizedSurfaceObservation
    admissible: bool
    rejection_reason: str
    rejection_severity: str  # "" when admissible; else "HARD" | "SOFT"
    evidence_rung: str       # "" | DIRECT | INDIRECT_STRONG | WEAK
    density_implication: str  # "" | SUPPORTS_DENSITY_PLAUSIBILITY | OPPOSES_DENSITY_PLAUSIBILITY | CONTEXTUAL
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
                self.density_implication,
                DENSITY_IMPLICATION_VALUES,
                "density_implication",
            )
            if self.qualifying_for_direct and self.evidence_rung != "DIRECT":
                raise ValueError("qualifying_for_direct requires evidence_rung DIRECT")
            if self.qualifying_for_indirect and self.evidence_rung != "INDIRECT_STRONG":
                raise ValueError("qualifying_for_indirect requires evidence_rung INDIRECT_STRONG")
            if self.qualifying_for_direct and self.qualifying_for_indirect:
                raise ValueError("an observation qualifies for at most one rung")
            # a qualifying INDIRECT_STRONG localization observation never carries
            # a directional density_implication (E12-3).
            if self.qualifying_for_indirect and self.density_implication in (
                "SUPPORTS_DENSITY_PLAUSIBILITY",
                "OPPOSES_DENSITY_PLAUSIBILITY",
            ):
                raise ValueError(
                    "a qualifying INDIRECT_STRONG localization observation is "
                    "CONTEXTUAL -- it never carries a directional density_implication"
                )
            # a directional density_implication only exists on a qualifying DIRECT
            # quantitative antigen-density observation.
            if self.density_implication in (
                "SUPPORTS_DENSITY_PLAUSIBILITY",
                "OPPOSES_DENSITY_PLAUSIBILITY",
            ) and not self.qualifying_for_direct:
                raise ValueError(
                    "a directional density_implication requires a qualifying DIRECT "
                    "quantitative antigen-density observation"
                )
        else:
            _choice(self.rejection_severity, ("HARD", "SOFT"), "rejection_severity")
            if not self.rejection_reason:
                raise ValueError("a rejected observation must state a rejection_reason")
            if self.evidence_rung or self.density_implication:
                raise ValueError("a rejected observation has no rung or density implication")
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
        return self.admissible and self.density_implication in (
            "SUPPORTS_DENSITY_PLAUSIBILITY",
            "OPPOSES_DENSITY_PLAUSIBILITY",
        )

    @property
    def is_qualifying(self) -> bool:
        return self.qualifying_for_direct or self.qualifying_for_indirect


# --- emitted evidence (one observation -> one canonical EP) --------------

@dataclass(frozen=True)
class EmittedEvidence:
    classified: ClassifiedSurfaceObservation
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedSurfaceObservation):
            raise ValueError("classified must be a ClassifiedSurfaceObservation")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")

    @property
    def observation(self) -> NormalizedSurfaceObservation:
        return self.classified.observation


# --- fatal review (E11 item 08 / 12): a machine review TRIGGER ----------

@dataclass(frozen=True)
class FatalReviewRecord:
    """Non-canonical, module-local, on the run result only. NOT a proposal
    field, NOT a CandidateGateAssessment field, NOT a core object, NOT a
    Decision, NOT a Gate fatal flag. ``status`` has ONE non-empty value; the
    machine NEVER emits PUBLIC_FATAL_SIGNAL_ESTABLISHED / a canonical fatal flag
    / KILL / HOLD / Decision, and NEVER decides whether the pattern is a real
    fatal signal -- that is human review + the GateSet fatal policy.

    ``required`` is true iff, on a completed audited landscape, one or more
    eligible DIRECT-class quantitative CRC-MALIGNANT-CELL
    NEGLIGIBLE_OR_UNDETECTABLE observations meet Route A (an auditable explicit
    reproducibility qualification) OR Route B (>= 2 independent qualified CRC
    malignant-cell surface-context identities)."""

    required: bool
    status: str  # "" | POTENTIAL_FATAL_PATTERN
    evidence_ids: tuple[str, ...]
    surface_context_ids: tuple[str, ...]
    antigen_level_class: tuple[str, ...]
    context_qualification_basis_refs: tuple[str, ...]
    measurement_validation_basis_refs: tuple[str, ...]
    reproducibility_basis_refs: tuple[str, ...]
    landscape_as_of: str
    surface_search_scope: str

    def __post_init__(self) -> None:
        _bool(self.required, "required")
        _choice(self.status, FATAL_REVIEW_STATUS_VALUES, "status")
        if self.required != (self.status == "POTENTIAL_FATAL_PATTERN"):
            raise ValueError("required is true iff status == POTENTIAL_FATAL_PATTERN")
        for evidence_id in self.evidence_ids:
            _pattern(evidence_id, _EP_ID, "fatal_review.evidence_ids[]")
        for name in (
            "surface_context_ids",
            "antigen_level_class",
            "context_qualification_basis_refs",
            "measurement_validation_basis_refs",
            "reproducibility_basis_refs",
        ):
            for item in getattr(self, name):
                _text(item, f"fatal_review.{name}[]")
        _text(self.landscape_as_of, "fatal_review.landscape_as_of", allow_empty=not self.required)
        _text(
            self.surface_search_scope,
            "fatal_review.surface_search_scope",
            allow_empty=not self.required,
        )
        if self.required:
            if not self.evidence_ids:
                raise ValueError("a POTENTIAL_FATAL_PATTERN carries its contributing evidence")
            for c in self.antigen_level_class:
                _choice(c, (_NEGLIGIBLE,), "fatal_review.antigen_level_class[]")
            if not self.antigen_level_class:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the NEGLIGIBLE_OR_UNDETECTABLE class"
                )
            if not self.context_qualification_basis_refs or not self.measurement_validation_basis_refs:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the context-qualification and "
                    "measurement-validation basis refs"
                )
            # Route A OR Route B: at least two independent surface-context
            # identities (Route B), OR a reproducibility_basis_ref (Route A).
            if len(set(self.surface_context_ids)) < 2 and not self.reproducibility_basis_refs:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN needs Route A (a reproducibility_basis_ref) "
                    "OR Route B (>= 2 independent surface_context_ids)"
                )
        else:
            for name in (
                "evidence_ids",
                "surface_context_ids",
                "antigen_level_class",
                "context_qualification_basis_refs",
                "measurement_validation_basis_refs",
                "reproducibility_basis_refs",
            ):
                if getattr(self, name):
                    raise ValueError(f"fatal_review.{name} is empty when required is false")

    @staticmethod
    def none() -> "FatalReviewRecord":
        return FatalReviewRecord(False, "", (), (), (), (), (), (), "", "")


# --- module input --------------------------------------------------------

@dataclass(frozen=True)
class Tgt04ModuleInput:
    """Everything the module needs to run one (candidate, TGT-04) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the SINGLE
    authoritative identity (MOD-TGT01 / PR E2 gene). There is no second
    drift-prone target argument and no implicit default scientific context
    (E11 item 10). ``context_id`` is the CANONICAL Instantiation context -- a
    SEPARATE namespace from each observation's LOCAL surface_context_id."""

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
    surface_search_scope: str
    existing_evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _text(self.candidate_name, "candidate_name")
        _text(self.target_identity, "target_identity")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        if self.instantiation_id != INSTANTIATION_ID:
            raise ValueError(f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT04")
        _pattern(self.context_id, _CTX_ID, "context_id")
        if self.context_id != CONTEXT_ID:
            raise ValueError(
                f"context_id must be {CONTEXT_ID!r} for the fixed TGT-04 Instantiation "
                "-- there is no implicit default scientific context (E11 item 10)"
            )
        _positive_int(self.context_version, "context_version")
        if self.context_version != CONTEXT_VERSION:
            raise ValueError(
                f"context_version must be {CONTEXT_VERSION} for the fixed TGT-04 Instantiation"
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
            raise ValueError("evidence_regime must be PUBLIC_ONLY for the current TGT-04 instantiation")
        _text(self.run_id, "run_id")
        _text(self.code_commit, "code_commit", allow_empty=True)
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError(
                "landscape_as_of must start with an ISO date -- a landscape with no as_of "
                "is not admissible"
            )
        _text(self.surface_search_scope, "surface_search_scope")
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


# --- proposal envelope (E11 item 12) ------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Carries the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` AND any TGT-02 /
    TGT-03 / TGT-06 conclusion AND any fatal flag (the potential-fatal-pattern
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
                "is not a legal TGT-04 pair (only POSITIVE/DIRECT, NEGATIVE/DIRECT, "
                "CONFLICTING/DIRECT, INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN -- "
                "INDIRECT_STRONG never becomes a proposed Strength)"
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
        if self.evidence_ceiling != TGT04_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-04 ceiling verbatim")

        roles = {r for _, r in self.evidence_refs}
        d, s = self.proposed_direction, self.proposed_strength
        if d == "POSITIVE" and "SUPPORTING" not in roles:
            raise ValueError("a POSITIVE proposal needs >= 1 SUPPORTING evidence_ref")
        if d == "NEGATIVE" and "CONTRADICTING" not in roles:
            raise ValueError("a NEGATIVE proposal needs >= 1 CONTRADICTING evidence_ref")
        if d == "CONFLICTING" and not {"SUPPORTING", "CONTRADICTING"} <= roles:
            raise ValueError("a CONFLICTING proposal needs >= 1 SUPPORTING and >= 1 CONTRADICTING ref")
        if d == "INCONCLUSIVE" and s == "DIRECT":
            if "CONTEXTUAL" not in roles or not self.evidence_refs:
                raise ValueError("a graded INCONCLUSIVE / DIRECT proposal carries CONTEXTUAL evidence_refs")
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
class Tgt04ModuleRunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]  # newly created only
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    surface_completion: SurfaceAvailabilityCompletion
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
        if not isinstance(self.surface_completion, SurfaceAvailabilityCompletion):
            raise ValueError("surface_completion must be a SurfaceAvailabilityCompletion")
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


def density_implication(observation: NormalizedSurfaceObservation) -> str:
    """The frozen E11 item-06 ``density_direction_mapping``. Applied ONLY to a
    qualifying DIRECT quantitative antigen-density observation, evaluated in this
    order. The Module never parses basis prose and never coerces a raw density
    value to a number."""

    if observation.surface_antigen_level == _NEGLIGIBLE:
        return "OPPOSES_DENSITY_PLAUSIBILITY"
    if observation.density_plausibility_status == "PLAUSIBLY_ADEQUATE":
        return "SUPPORTS_DENSITY_PLAUSIBILITY"
    if observation.density_plausibility_status == "NOT_PLAUSIBLY_ADEQUATE":
        return "OPPOSES_DENSITY_PLAUSIBILITY"
    # MIXED_OR_UNRESOLVED / NOT_ESTABLISHED / unqualified
    return "CONTEXTUAL"
