"""Frozen input / output contracts for MOD-TGT06.

Runtime Migration PR E14. In-memory contract values handed between the
deterministic Gate-specific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments.

Four invariants this module must never break (frozen PR E13 contract + ChatGPT
AI审核方案 E14):

1. Internalization is configuration-specific, not a target-intrinsic constant. A
   DIRECT rung is an EXISTENCE PROOF -- ONE qualifying disease-relevant
   antibody / epitope configuration achieving antibody-induced internalization
   WITH lysosomal delivery, in ONE upstream-qualified INTEGRATED observation. A
   single non-internalizing configuration NEVER establishes target-wide
   non-internalization.
2. INDIRECT_STRONG evidence (constitutive endocytosis / established
   internalizing-receptor biology / non-CRC antibody-induced internalization / a
   successful same-target ADC functional-delivery precedent) is genuine positive
   addressability support and DOES propagate to a Gate-level Strength
   (POSITIVE / INDIRECT_STRONG). This is the highest-qualifying-rung authority,
   NOT the TGT-04 single-tier exception.
3. Quantitative values are evidence, not thresholds. A source-reported numeric
   assay fact ("65% internalized at 4 h") is a factual measurement that lives in
   the neutral claim string; the Module NEVER coerces it to a number, and NEVER
   compares it to a threshold / cutoff / invented "ADC-effective internalization
   rate". The typed classification driver is ``internalization_outcome`` -- a
   CLOSED enum, never a number. There is NO dedicated typed raw numeric field and
   therefore NO TGT-04-style symmetric raw-value reuse-parity branch (E14-6 /
   E14-7).
4. A single DIRECT-quality productive-internalization / trafficking failure is a
   DIRECT-class OPPOSES_ADDRESSABILITY observation -- NOT yet a NEGATIVE / DIRECT
   proposal and NOT a reproducible fatal pattern. Only productive-internalization
   / trafficking failure across MULTIPLE INDEPENDENT qualified configurations,
   with NO qualifying productive DIRECT existence proof on the completed
   landscape, may surface a machine-local ``fatal_review =
   POTENTIAL_FATAL_PATTERN``. ``assay_method`` is an OPEN factual type while
   ``assay_validation_status`` is CLOSED; no numeric or ranking score anywhere;
   the Module never decides fatality or ADC efficacy.
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

from .completion import InternalizationEvidenceCompletion

# --- identity ---------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT06"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-06"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
#: The fixed Instantiation's frozen scientific context (PR D
#: crc_adc_target_gateset.yaml context_id / context_version). The Module must not
#: run against any other context (E13 item 10: no implicit default context). This
#: canonical context_id is a SEPARATE namespace from the LOCAL
#: ``internalization_configuration_id`` on each observation (E10 identity-namespace
#: gene).
CONTEXT_ID: Final[str] = "CTX-CRC-REFRACTORY-MCRC"
CONTEXT_VERSION: Final[int] = 1
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-06 contract (item 05 evidence_ceiling).
#: Reproduced only by the PROPOSAL layer -- never stamped onto a Gate-neutral
#: EvidencePackage.
TGT06_EVIDENCE_CEILING: Final[str] = (
    "antibody-induced internalization with lysosomal delivery for the target via "
    "at least one antibody / epitope configuration"
)
#: Verbatim from src/contracts/crc_adc_target_gateset.yaml
#: gate_contracts.TGT-06.gate_question (E13 item 03).
TGT06_GATE_QUESTION: Final[str] = (
    "Upon antibody binding, is the target-antibody complex internalized and "
    "trafficked to a compartment compatible with payload release?"
)

_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ----------------------------------------------------------------

#: What a normalized internalization observation IS. The provider supplies
#: normalized upstream facts only -- it never sets a rung, a direction, an
#: addressability implication or a fatal trigger (E14-2). The eight kinds.
OBSERVATION_KIND_VALUES: Final[tuple[str, ...]] = (
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
    "TRAFFICKING_OR_RECYCLING_ONLY",
    "SAME_TARGET_ADC_DELIVERY_PRECEDENT",
    "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
    "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
    "SURFACE_LOCALIZATION_ONLY_INFERENCE",
    "SEARCH_COMPLETION_AUDIT",
)
#: The only kind that can carry a productive DIRECT existence-proof observation --
#: an INTEGRATED antibody-induced internalization + lysosomal delivery observation
#: on the SAME configuration.
_INTEGRATED_KIND: Final[str] = "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING"
#: The three kinds that can carry a DIRECT-quality productive-internalization /
#: trafficking FAILURE observation (item 06 / item 08 machine_detection_criteria).
#: Also the internalization / trafficking "family" -- one of these in a
#: disease-relevant context MUST disclose its configuration identity (SINGLE /
#: IDENTIFIED_MULTI); the IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE state is
#: available to a family kind ONLY in a NON_CRC_CONTEXT (E14 review round-1 blocker 3).
_DIRECT_QUALITY_FAILURE_KINDS: Final[tuple[str, ...]] = (
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
    "TRAFFICKING_OR_RECYCLING_ONLY",
)
#: The observation kinds for which the IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE
#: configuration-identity state is ALWAYS a valid normalized factual shape (the
#: frozen ladder does not require a configuration disclosure for them) -- E13 item
#: 06 configuration_identity_single_vs_multi.
_THIRD_STATE_ALWAYS_ALLOWED_KINDS: Final[tuple[str, ...]] = (
    "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
    "SAME_TARGET_ADC_DELIVERY_PRECEDENT",
    "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
    "SURFACE_LOCALIZATION_ONLY_INFERENCE",
    "SEARCH_COMPLETION_AUDIT",
)
#: The frozen INDIRECT_STRONG classes -- all positive addressability support.
_INDIRECT_STRONG_KINDS: Final[tuple[str, ...]] = (
    "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
    "SAME_TARGET_ADC_DELIVERY_PRECEDENT",
)
#: The frozen WEAK-only inference kinds -- hypothesis / context only.
_WEAK_KINDS: Final[tuple[str, ...]] = (
    "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
    "SURFACE_LOCALIZATION_ONLY_INFERENCE",
)

#: The qualified disease-relevant context of an observation (E13 item 06).
SURFACE_CONTEXT_CLASS_VALUES: Final[tuple[str, ...]] = (
    "",
    "CRC_MALIGNANT_CELLS",
    "WELL_MATCHED_CRC_MODEL",
    "NON_CRC_CONTEXT",
    "UNRESOLVED",
)
#: surface_context_class values that CAN carry a DIRECT rung / a fatal contributor
#: (item 05 / item 08 -- a QUALIFIED well-matched CRC model IS eligible here,
#: unlike TGT-04).
_DIRECT_CONTEXT_CLASSES: Final[tuple[str, ...]] = (
    "CRC_MALIGNANT_CELLS",
    "WELL_MATCHED_CRC_MODEL",
)

CONTEXT_ADEQUACY_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")

#: The assay-validation PREDICATE that lets an integrated configuration
#: observation drive DIRECT. CLOSED enum -- {QUALIFIED, NOT_ESTABLISHED}.
#: QUALIFIED is NOT a positive addressability conclusion, only "this assay
#: qualifies to enter DIRECT". ``assay_method`` itself stays an OPEN factual type.
ASSAY_VALIDATION_STATUS_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")

#: The CLOSED typed internalization classifier (E13 item 06). NEVER computed by
#: the Module from a number.
INTERNALIZATION_OUTCOME_VALUES: Final[tuple[str, ...]] = (
    "PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY",
    "INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED",
    "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
)
_PRODUCTIVE = "PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"
_DELIVERY_UNRESOLVED = "INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED"
_FAILS = "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"

REPRODUCIBILITY_STATUS_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")

#: The Evidence-Ladder rung the Module maps an observation to (frozen PR D).
EVIDENCE_RUNG_VALUES: Final[tuple[str, ...]] = ("", "DIRECT", "INDIRECT_STRONG", "WEAK")

#: Module-assigned Gate-relative reading of a rung-classed observation.
ADDRESSABILITY_IMPLICATION_VALUES: Final[tuple[str, ...]] = (
    "",
    "SUPPORTS_ADDRESSABILITY",
    "OPPOSES_ADDRESSABILITY",
    "CONTEXTUAL",
)

FATAL_REVIEW_STATUS_VALUES: Final[tuple[str, ...]] = ("", "POTENTIAL_FATAL_PATTERN")

#: The three frozen configuration-identity states (item 06
#: configuration_identity_single_vs_multi).
CONFIGURATION_IDENTITY_STATES: Final[tuple[str, ...]] = (
    "SINGLE",
    "IDENTIFIED_MULTI",
    "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE",
)

CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

#: The only Direction x Strength pairs MOD-TGT06 may propose (frozen E13 item 06 --
#: exactly SIX). TGT-06 uses the highest-qualifying-rung grading authority (the
#: TGT-03 precedent): a qualifying INDIRECT_STRONG addressability landscape with
#: no DIRECT configuration is POSITIVE / INDIRECT_STRONG, not INCONCLUSIVE.
LEGAL_DIRECTION_STRENGTH_PAIRS: Final[frozenset[tuple[str, str]]] = frozenset(
    {
        ("POSITIVE", "DIRECT"),
        ("POSITIVE", "INDIRECT_STRONG"),
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


# --- provider output: normalized internalization observation ---------------

@dataclass(frozen=True)
class NormalizedInternalizationObservation:
    """One already-normalized, primary/repository-source-resolved TGT-06
    internalization / trafficking observation. NORMALIZED UPSTREAM FACTS only --
    the provider never sets a rung, a direction, an addressability implication or
    a fatal trigger (E14-2). ``assay_method`` is an OPEN factual type;
    ``assay_validation_status`` is the CLOSED predicate. ``internalization_outcome``
    is a CLOSED typed classifier, never a number. A source-reported numeric assay
    fact lives inside ``claim`` and is never coerced (E14-6 / E14-7).

    ``internalization_configuration_ids`` is canonicalised in ``__post_init__`` to
    ``tuple(sorted(set(...)))`` so ("A","B") and ("B","A") are one configuration
    set (E14-3)."""

    observation_id: str
    target_identity: str
    context_key: str
    landscape_as_of: str
    observation_kind: str
    assay_method: str
    assay_validation_status: str
    assay_validation_basis: str
    crc_specific: bool
    surface_context_class: str
    surface_context_basis: str
    context_adequacy_status: str
    context_adequacy_basis: str
    internalization_outcome: str
    internalization_outcome_basis: str
    reproducibility_status: str
    reproducibility_basis: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    primary_or_repository_source_resolved: bool
    declared_multi_configuration_analysis: bool = False
    internalization_configuration_id: str = ""
    internalization_configuration_ids: tuple[str, ...] = ()
    configuration_identity_basis: str = ""
    antibody_identity: str = ""
    epitope_identity_or_region: str = ""
    affinity_context: str = ""
    conjugation_context: str = ""
    # --- SEARCH_COMPLETION_AUDIT-specific structured snapshot (E14-5 gene) ----
    #  the snapshot field names ARE the typed completion's field names.
    audit_search_scope: str = ""
    audit_sources_searched: tuple[str, ...] = ()
    audit_landscape_as_of: str = ""
    audit_public_internalization_search_complete: bool = False
    audit_antibody_configuration_internalization_search_complete: bool = False
    audit_productive_trafficking_search_complete: bool = False
    audit_same_target_adc_functional_delivery_search_complete: bool = False
    audit_receptor_endocytosis_and_inference_search_complete: bool = False
    audit_unresolved_item_keys: tuple[str, ...] = ()
    audit_qualifying_direct_configuration_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _pattern(self.observation_id, _OBS_ID, "observation_id")
        _text(self.target_identity, "target_identity")
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _choice(self.observation_kind, OBSERVATION_KIND_VALUES, "observation_kind")
        _text(self.assay_method, "assay_method", allow_empty=True)
        _choice(
            self.assay_validation_status,
            ASSAY_VALIDATION_STATUS_VALUES,
            "assay_validation_status",
        )
        _text(self.assay_validation_basis, "assay_validation_basis", allow_empty=True)
        _bool(self.crc_specific, "crc_specific")
        _choice(
            self.surface_context_class,
            SURFACE_CONTEXT_CLASS_VALUES,
            "surface_context_class",
        )
        _text(self.surface_context_basis, "surface_context_basis", allow_empty=True)
        _choice(
            self.context_adequacy_status, CONTEXT_ADEQUACY_VALUES, "context_adequacy_status"
        )
        _text(self.context_adequacy_basis, "context_adequacy_basis", allow_empty=True)
        _choice(
            self.internalization_outcome,
            INTERNALIZATION_OUTCOME_VALUES,
            "internalization_outcome",
        )
        _text(
            self.internalization_outcome_basis,
            "internalization_outcome_basis",
            allow_empty=True,
        )
        _choice(
            self.reproducibility_status,
            REPRODUCIBILITY_STATUS_VALUES,
            "reproducibility_status",
        )
        _text(self.reproducibility_basis, "reproducibility_basis", allow_empty=True)
        _text(self.claim, "claim")
        _pattern(self.source_id, _SRC_ID, "source_id")
        _choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _text(self.source_identifier, "source_identifier")
        _text(self.locator, "locator", allow_empty=True)
        _text(self.retrieved_at, "retrieved_at")
        if not _ISO_DATE_PREFIX.match(self.retrieved_at):
            raise ValueError("retrieved_at must start with an ISO date")
        _bool(
            self.primary_or_repository_source_resolved,
            "primary_or_repository_source_resolved",
        )
        _bool(
            self.declared_multi_configuration_analysis,
            "declared_multi_configuration_analysis",
        )
        _text(
            self.internalization_configuration_id,
            "internalization_configuration_id",
            allow_empty=True,
        )
        if self.internalization_configuration_ids:
            _str_tuple(
                self.internalization_configuration_ids,
                "internalization_configuration_ids",
            )
            # --- E14-3: canonical deterministic representation. ("A","B") and
            #     ("B","A") are the same configuration set; ids are non-empty and
            #     de-duplicated.
            object.__setattr__(
                self,
                "internalization_configuration_ids",
                tuple(sorted(set(self.internalization_configuration_ids))),
            )
        _text(
            self.configuration_identity_basis,
            "configuration_identity_basis",
            allow_empty=True,
        )
        _text(self.antibody_identity, "antibody_identity", allow_empty=True)
        _text(
            self.epitope_identity_or_region,
            "epitope_identity_or_region",
            allow_empty=True,
        )
        _text(self.affinity_context, "affinity_context", allow_empty=True)
        _text(self.conjugation_context, "conjugation_context", allow_empty=True)

        # --- the three frozen configuration-identity states (item 06 /
        #     E14-3) ------------------------------------------------------------
        cid = self.internalization_configuration_id.strip()
        cids = self.internalization_configuration_ids
        basis = self.configuration_identity_basis.strip()
        if self.declared_multi_configuration_analysis:
            if cid or len(set(cids)) < 2 or not basis:
                raise ValueError(
                    "IDENTIFIED_MULTI requires declared_multi_configuration_analysis "
                    "== true, internalization_configuration_id == '', >= 2 distinct "
                    "internalization_configuration_ids and a non-empty "
                    "configuration_identity_basis"
                )
        elif cid:
            if cids or not basis:
                raise ValueError(
                    "SINGLE requires declared_multi_configuration_analysis == false, "
                    "a non-empty internalization_configuration_id, empty "
                    "internalization_configuration_ids and a non-empty "
                    "configuration_identity_basis"
                )
        else:
            if cids or basis:
                raise ValueError(
                    "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE requires "
                    "declared_multi_configuration_analysis == false, empty "
                    "internalization_configuration_id / internalization_configuration_ids "
                    "and an empty configuration_identity_basis"
                )
        # a LOCAL configuration identity may NEVER be the canonical Instantiation
        # context_id -- collapsing the two namespaces is a HARD identity failure
        # (E10 identity-namespace gene).
        for one in (self.internalization_configuration_id, *cids):
            if one.strip() == CONTEXT_ID:
                raise ValueError(
                    "a local internalization_configuration_id must never be the "
                    f"canonical Instantiation context_id {CONTEXT_ID!r} (namespace collapse)"
                )

        kind = self.observation_kind

        # --- IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE allowed-kind boundary
        #     (E14 review round-1 blocker 3). The third state is NOT a generic
        #     fallback for every observation that merely fell short of DIRECT --
        #     it is a normalized factual shape invariant. It is valid for the
        #     five frozen non-configuration ladder kinds, OR for an internalization
        #     / trafficking family kind ONLY when the context is NON_CRC_CONTEXT
        #     (a non-CRC antibody-induced internalization observation whose source
        #     does not disclose the configuration). A family kind in a
        #     disease-relevant / unresolved / unspecified context MUST disclose a
        #     SINGLE or IDENTIFIED_MULTI configuration identity.
        if (
            not cid
            and not cids
            and kind not in _THIRD_STATE_ALWAYS_ALLOWED_KINDS
            and not (
                kind in _DIRECT_QUALITY_FAILURE_KINDS
                and self.surface_context_class == "NON_CRC_CONTEXT"
            )
        ):
            raise ValueError(
                "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE is permitted only for a "
                "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY / "
                "SAME_TARGET_ADC_DELIVERY_PRECEDENT / "
                "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE / "
                "SURFACE_LOCALIZATION_ONLY_INFERENCE / SEARCH_COMPLETION_AUDIT "
                "observation, or a NON_CRC_CONTEXT internalization / trafficking "
                "observation whose source does not disclose the configuration; a "
                f"{kind!r} observation in surface_context_class "
                f"{self.surface_context_class!r} must disclose a SINGLE or "
                "IDENTIFIED_MULTI configuration identity"
            )

        # --- typed-fact coherence (E14-1 tightening / E14-3) ----------------
        # an observation explicitly named INTERNALIZATION_ONLY must not also claim
        # proven lysosomal delivery.
        if (
            kind == "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY"
            and self.internalization_outcome == _PRODUCTIVE
        ):
            raise ValueError(
                "an ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY observation cannot "
                "carry internalization_outcome == "
                "PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY (typed-fact "
                "incoherence -- INTERNALIZATION_ONLY does not prove lysosomal delivery)"
            )

        # --- context / crc_specific coherence (E10 gene) -------------------
        if self.surface_context_class in _DIRECT_CONTEXT_CLASSES and not self.crc_specific:
            raise ValueError(
                f"surface_context_class {self.surface_context_class!r} requires "
                "crc_specific == true (typed-fact coherence)"
            )
        if self.surface_context_class == "NON_CRC_CONTEXT" and self.crc_specific:
            raise ValueError(
                "surface_context_class NON_CRC_CONTEXT requires crc_specific == false"
            )

        # --- cross-field shape by observation kind ------------------------
        if kind == "SEARCH_COMPLETION_AUDIT":
            if self.assay_method != "SEARCH_AUDIT":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries assay_method SEARCH_AUDIT"
                )
            if self.assay_validation_status != "NOT_ESTABLISHED":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries "
                    "assay_validation_status NOT_ESTABLISHED"
                )
            if self.internalization_outcome != "NOT_ESTABLISHED":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries "
                    "internalization_outcome NOT_ESTABLISHED"
                )
            if cid or cids or basis:
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation is in the "
                    "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE state"
                )

        # --- qualification-basis hygiene (E13 item 06 / 13; E14 basis hygiene)
        if (
            self.surface_context_class in ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL", "NON_CRC_CONTEXT")
            and not self.surface_context_basis.strip()
        ):
            raise ValueError(
                "an asserted surface_context_class carries an auditable surface_context_basis"
            )
        if self.surface_context_basis.strip() and self.surface_context_class in ("", "UNRESOLVED"):
            raise ValueError(
                "a surface_context_basis without an asserted surface_context_class is drift"
            )
        if self.context_adequacy_status == "QUALIFIED" and not self.context_adequacy_basis.strip():
            raise ValueError(
                "a QUALIFIED context_adequacy_status carries an auditable context_adequacy_basis"
            )
        if self.context_adequacy_basis.strip() and self.context_adequacy_status == "NOT_ESTABLISHED":
            raise ValueError(
                "a context_adequacy_basis without a QUALIFIED context_adequacy_status is drift"
            )
        if self.assay_validation_status == "QUALIFIED" and not self.assay_validation_basis.strip():
            raise ValueError(
                "a QUALIFIED assay_validation_status carries an auditable assay_validation_basis"
            )
        if self.assay_validation_basis.strip() and self.assay_validation_status == "NOT_ESTABLISHED":
            raise ValueError(
                "an assay_validation_basis without a QUALIFIED assay_validation_status is drift"
            )
        if (
            self.internalization_outcome != "NOT_ESTABLISHED"
            and not self.internalization_outcome_basis.strip()
        ):
            raise ValueError(
                "an asserted internalization_outcome carries an auditable "
                "internalization_outcome_basis"
            )
        if (
            self.internalization_outcome_basis.strip()
            and self.internalization_outcome == "NOT_ESTABLISHED"
        ):
            raise ValueError(
                "an internalization_outcome_basis without an asserted "
                "internalization_outcome is drift"
            )
        if self.reproducibility_status == "QUALIFIED" and not self.reproducibility_basis.strip():
            raise ValueError(
                "a QUALIFIED reproducibility_status carries an auditable reproducibility_basis"
            )
        if self.reproducibility_basis.strip() and self.reproducibility_status == "NOT_ESTABLISHED":
            raise ValueError(
                "a reproducibility_basis without a QUALIFIED reproducibility_status is drift"
            )

        # --- audit-snapshot shape (E14-5 gene) ---------------------------
        _text(self.audit_search_scope, "audit_search_scope", allow_empty=True)
        for name in (
            "audit_sources_searched",
            "audit_unresolved_item_keys",
            "audit_qualifying_direct_configuration_ids",
        ):
            if getattr(self, name):
                _str_tuple(getattr(self, name), name)
        _text(self.audit_landscape_as_of, "audit_landscape_as_of", allow_empty=True)
        for name in (
            "audit_public_internalization_search_complete",
            "audit_antibody_configuration_internalization_search_complete",
            "audit_productive_trafficking_search_complete",
            "audit_same_target_adc_functional_delivery_search_complete",
            "audit_receptor_endocytosis_and_inference_search_complete",
        ):
            _bool(getattr(self, name), name)
        _any_audit_field = (
            bool(self.audit_search_scope.strip())
            or bool(self.audit_sources_searched)
            or bool(self.audit_landscape_as_of.strip())
            or self.audit_public_internalization_search_complete
            or self.audit_antibody_configuration_internalization_search_complete
            or self.audit_productive_trafficking_search_complete
            or self.audit_same_target_adc_functional_delivery_search_complete
            or self.audit_receptor_endocytosis_and_inference_search_complete
            or bool(self.audit_unresolved_item_keys)
            or bool(self.audit_qualifying_direct_configuration_ids)
        )
        if kind == "SEARCH_COMPLETION_AUDIT":
            if not self.audit_search_scope.strip():
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries a non-empty audit_search_scope"
                )
            if not self.audit_sources_searched:
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation lists the sources searched"
                )
            if not self.audit_landscape_as_of.strip():
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries an audit_landscape_as_of"
                )
        elif _any_audit_field:
            raise ValueError(
                "only a SEARCH_COMPLETION_AUDIT observation carries an audit snapshot"
            )

    # --- factual predicates (field reads only, no interpretation) -----------
    @property
    def configuration_identity_state(self) -> str:
        if self.declared_multi_configuration_analysis:
            return "IDENTIFIED_MULTI"
        if self.internalization_configuration_id.strip():
            return "SINGLE"
        return "IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE"

    @property
    def is_configuration_resolved(self) -> bool:
        """SINGLE or IDENTIFIED_MULTI -- a disclosed local configuration identity."""
        return self.configuration_identity_state in ("SINGLE", "IDENTIFIED_MULTI")

    @property
    def is_disease_relevant_context(self) -> bool:
        return (
            self.surface_context_class in _DIRECT_CONTEXT_CLASSES
            and self.context_adequacy_status == "QUALIFIED"
        )

    @property
    def is_assay_qualified(self) -> bool:
        return (
            self.assay_validation_status == "QUALIFIED"
            and bool(self.assay_method.strip())
        )

    @property
    def is_reproducibility_qualified(self) -> bool:
        return (
            self.reproducibility_status == "QUALIFIED"
            and bool(self.reproducibility_basis.strip())
        )

    @property
    def is_productive_outcome(self) -> bool:
        return self.internalization_outcome == _PRODUCTIVE

    @property
    def is_failure_outcome(self) -> bool:
        return self.internalization_outcome == _FAILS

    @property
    def is_delivery_unresolved_outcome(self) -> bool:
        return self.internalization_outcome == _DELIVERY_UNRESOLVED

    @property
    def configuration_identities(self) -> frozenset[str]:
        """The frozen item-06 ``configuration_identity_projection`` -- the ONE
        deterministic helper every configuration-identity operation uses."""
        return configuration_identity_projection(self)


def configuration_identity_projection(
    observation: NormalizedInternalizationObservation,
) -> frozenset[str]:
    """The ONE deterministic configuration-identity helper (frozen E13 item 06 /
    PR E13 review round-2 gene). SINGLE -> {internalization_configuration_id};
    IDENTIFIED_MULTI -> set(internalization_configuration_ids);
    IDENTITY_NOT_DISCLOSED_OR_NOT_APPLICABLE -> {} (the empty set). ALL grouping /
    CLEAN detection / same-configuration conflict detection / DIRECT-quality
    failure counting / the >= 2 independent-failure test / Route B convergence /
    completion.qualifying_direct_configuration_ids operate over THIS projection --
    there is no second interpretation. An IDENTIFIED_MULTI {A, B} observation
    contributes BOTH A and B."""

    state = observation.configuration_identity_state
    if state == "SINGLE":
        return frozenset({observation.internalization_configuration_id})
    if state == "IDENTIFIED_MULTI":
        return frozenset(observation.internalization_configuration_ids)
    return frozenset()


# --- classification ------------------------------------------------------

@dataclass(frozen=True)
class ClassifiedInternalizationObservation:
    """A provider observation placed into a FROZEN TGT-06 Evidence-Ladder rung and
    given a Module-owned Gate-relative addressability-implication reading. The
    provider never sets ``evidence_rung`` or ``addressability_implication``.

    ``qualifying_direct_productive`` -- a CLEAN existence-proof contributor:
    observation_kind ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING classified
    DIRECT with internalization_outcome ==
    PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY.
    ``qualifying_direct_failure`` -- a DIRECT-quality productive-internalization /
    trafficking FAILURE observation (item 06 / item 08).
    ``qualifying_indirect`` -- a positive INDIRECT_STRONG addressability
    observation. A rejected observation carries none."""

    observation: NormalizedInternalizationObservation
    admissible: bool
    rejection_reason: str
    rejection_severity: str  # "" when admissible; else "HARD" | "SOFT"
    evidence_rung: str       # "" | DIRECT | INDIRECT_STRONG | WEAK
    addressability_implication: str  # "" | SUPPORTS_ADDRESSABILITY | OPPOSES_ADDRESSABILITY | CONTEXTUAL
    qualifying_direct_productive: bool
    qualifying_direct_failure: bool
    qualifying_indirect: bool

    def __post_init__(self) -> None:
        _bool(self.admissible, "admissible")
        _text(self.rejection_reason, "rejection_reason", allow_empty=True)
        _bool(self.qualifying_direct_productive, "qualifying_direct_productive")
        _bool(self.qualifying_direct_failure, "qualifying_direct_failure")
        _bool(self.qualifying_indirect, "qualifying_indirect")
        if self.admissible:
            _choice(self.rejection_severity, ("",), "rejection_severity")
            _choice(self.evidence_rung, EVIDENCE_RUNG_VALUES, "evidence_rung")
            _choice(
                self.addressability_implication,
                ADDRESSABILITY_IMPLICATION_VALUES,
                "addressability_implication",
            )
            n_qualifying = (
                int(self.qualifying_direct_productive)
                + int(self.qualifying_direct_failure)
                + int(self.qualifying_indirect)
            )
            if n_qualifying > 1:
                raise ValueError("an observation qualifies for at most one rung role")
            if (self.qualifying_direct_productive or self.qualifying_direct_failure) and self.evidence_rung != "DIRECT":
                raise ValueError("a qualifying DIRECT-rung role requires evidence_rung DIRECT")
            if self.qualifying_indirect and self.evidence_rung != "INDIRECT_STRONG":
                raise ValueError("qualifying_indirect requires evidence_rung INDIRECT_STRONG")
            if self.qualifying_direct_productive and self.addressability_implication != "SUPPORTS_ADDRESSABILITY":
                raise ValueError(
                    "a qualifying productive DIRECT observation is SUPPORTS_ADDRESSABILITY"
                )
            if self.qualifying_direct_failure and self.addressability_implication != "OPPOSES_ADDRESSABILITY":
                raise ValueError(
                    "a qualifying DIRECT-quality failure observation is OPPOSES_ADDRESSABILITY"
                )
            if self.qualifying_indirect and self.addressability_implication != "SUPPORTS_ADDRESSABILITY":
                raise ValueError(
                    "a qualifying INDIRECT_STRONG observation is SUPPORTS_ADDRESSABILITY"
                )
            # a directional implication only ever exists on a qualifying DIRECT-rung
            # observation (E14-3: classifier-owned authority).
            if self.addressability_implication in (
                "SUPPORTS_ADDRESSABILITY",
                "OPPOSES_ADDRESSABILITY",
            ) and not (
                self.qualifying_direct_productive
                or self.qualifying_direct_failure
                or self.qualifying_indirect
            ):
                raise ValueError(
                    "a directional addressability_implication requires a qualifying "
                    "DIRECT-rung or INDIRECT_STRONG observation"
                )
        else:
            _choice(self.rejection_severity, ("HARD", "SOFT"), "rejection_severity")
            if not self.rejection_reason:
                raise ValueError("a rejected observation must state a rejection_reason")
            if self.evidence_rung or self.addressability_implication:
                raise ValueError(
                    "a rejected observation has no rung or addressability implication"
                )
            if (
                self.qualifying_direct_productive
                or self.qualifying_direct_failure
                or self.qualifying_indirect
            ):
                raise ValueError("a rejected observation is not qualifying for a rung")

    @property
    def observation_id(self) -> str:
        return self.observation.observation_id

    @property
    def observation_kind(self) -> str:
        return self.observation.observation_kind

    @property
    def is_qualifying_direct(self) -> bool:
        return self.qualifying_direct_productive or self.qualifying_direct_failure

    @property
    def is_qualifying(self) -> bool:
        return (
            self.qualifying_direct_productive
            or self.qualifying_direct_failure
            or self.qualifying_indirect
        )

    @property
    def configuration_identities(self) -> frozenset[str]:
        return configuration_identity_projection(self.observation)


# --- emitted evidence (one observation -> one canonical EP) --------------

@dataclass(frozen=True)
class EmittedEvidence:
    classified: ClassifiedInternalizationObservation
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedInternalizationObservation):
            raise ValueError("classified must be a ClassifiedInternalizationObservation")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")

    @property
    def observation(self) -> NormalizedInternalizationObservation:
        return self.classified.observation

    @property
    def configuration_identities(self) -> frozenset[str]:
        return configuration_identity_projection(self.observation)


# --- fatal review (E13 item 08 / 12): a machine review TRIGGER ----------

@dataclass(frozen=True)
class FatalReviewRecord:
    """Non-canonical, module-local, on the run result only. NOT a proposal field,
    NOT a CandidateGateAssessment field, NOT a core object, NOT a Decision, NOT a
    Gate fatal flag. ``status`` has ONE non-empty value; the machine NEVER emits
    PUBLIC_FATAL_SIGNAL_ESTABLISHED / a canonical fatal flag / KILL / HOLD /
    Decision, and NEVER decides whether the pattern is a real fatal signal.

    ``required`` is true iff, on a completed audited landscape with NO qualifying
    productive DIRECT configuration, DIRECT-quality productive-internalization /
    trafficking FAILURE observations establish multiple independent configurations
    via Route A (ONE declared multi-configuration analysis observation whose
    projection set has size >= 2 AND reproducibility_status == QUALIFIED + basis)
    OR Route B (>= 2 DISTINCT eligible failure observations AND their projected
    configuration-identity union has size >= 2). A SINGLE IDENTIFIED_MULTI
    observation does NOT satisfy Route B."""

    required: bool
    status: str  # "" | POTENTIAL_FATAL_PATTERN
    evidence_ids: tuple[str, ...]
    configuration_ids: tuple[str, ...]
    internalization_outcome_class: tuple[str, ...]
    context_qualification_basis_refs: tuple[str, ...]
    assay_validation_basis_refs: tuple[str, ...]
    reproducibility_basis_refs: tuple[str, ...]
    landscape_as_of: str
    internalization_search_scope: str

    def __post_init__(self) -> None:
        _bool(self.required, "required")
        _choice(self.status, FATAL_REVIEW_STATUS_VALUES, "status")
        if self.required != (self.status == "POTENTIAL_FATAL_PATTERN"):
            raise ValueError("required is true iff status == POTENTIAL_FATAL_PATTERN")
        for evidence_id in self.evidence_ids:
            _pattern(evidence_id, _EP_ID, "fatal_review.evidence_ids[]")
        for name in (
            "configuration_ids",
            "internalization_outcome_class",
            "context_qualification_basis_refs",
            "assay_validation_basis_refs",
            "reproducibility_basis_refs",
        ):
            for item in getattr(self, name):
                _text(item, f"fatal_review.{name}[]")
        _text(
            self.landscape_as_of,
            "fatal_review.landscape_as_of",
            allow_empty=not self.required,
        )
        _text(
            self.internalization_search_scope,
            "fatal_review.internalization_search_scope",
            allow_empty=not self.required,
        )
        if self.required:
            if not self.evidence_ids:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries its contributing evidence"
                )
            for c in self.internalization_outcome_class:
                _choice(c, (_FAILS,), "fatal_review.internalization_outcome_class[]")
            if not self.internalization_outcome_class:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the "
                    "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING class"
                )
            if len(set(self.configuration_ids)) < 2:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN spans >= 2 independent configuration_ids"
                )
            if not self.context_qualification_basis_refs or not self.assay_validation_basis_refs:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the context-qualification and "
                    "assay-validation basis refs"
                )
        else:
            for name in (
                "evidence_ids",
                "configuration_ids",
                "internalization_outcome_class",
                "context_qualification_basis_refs",
                "assay_validation_basis_refs",
                "reproducibility_basis_refs",
            ):
                if getattr(self, name):
                    raise ValueError(
                        f"fatal_review.{name} is empty when required is false"
                    )

    @staticmethod
    def none() -> "FatalReviewRecord":
        return FatalReviewRecord(False, "", (), (), (), (), (), (), "", "")


# --- module input --------------------------------------------------------

@dataclass(frozen=True)
class Tgt06ModuleInput:
    """Everything the module needs to run one (candidate, TGT-06) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the SINGLE
    authoritative identity (MOD-TGT01 / PR E2 gene). There is no second
    drift-prone target argument and no implicit default scientific context
    (E13 item 10). ``context_id`` is the CANONICAL Instantiation context -- a
    SEPARATE namespace from each observation's LOCAL
    internalization_configuration_id."""

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
    internalization_search_scope: str
    existing_evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _text(self.candidate_name, "candidate_name")
        _text(self.target_identity, "target_identity")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        if self.instantiation_id != INSTANTIATION_ID:
            raise ValueError(f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT06")
        _pattern(self.context_id, _CTX_ID, "context_id")
        if self.context_id != CONTEXT_ID:
            raise ValueError(
                f"context_id must be {CONTEXT_ID!r} for the fixed TGT-06 Instantiation "
                "-- there is no implicit default scientific context (E13 item 10)"
            )
        _positive_int(self.context_version, "context_version")
        if self.context_version != CONTEXT_VERSION:
            raise ValueError(
                f"context_version must be {CONTEXT_VERSION} for the fixed TGT-06 Instantiation"
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
            raise ValueError(
                "evidence_regime must be PUBLIC_ONLY for the current TGT-06 instantiation"
            )
        _text(self.run_id, "run_id")
        _text(self.code_commit, "code_commit", allow_empty=True)
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError(
                "landscape_as_of must start with an ISO date -- a landscape with no "
                "as_of is not admissible"
            )
        _text(self.internalization_search_scope, "internalization_search_scope")
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


# --- proposal envelope (E13 item 12) ------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Carries the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` AND any TGT-02 /
    TGT-03 / TGT-04 conclusion AND any fatal flag (the
    multiple-independent-configuration-failure signal lives in the module-local
    ``fatal_review`` record)."""

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
                "is not a legal TGT-06 pair (only POSITIVE/DIRECT, POSITIVE/INDIRECT_STRONG, "
                "NEGATIVE/DIRECT, CONFLICTING/DIRECT, INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN)"
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
        if self.evidence_ceiling != TGT06_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-06 ceiling verbatim")

        roles = {r for _, r in self.evidence_refs}
        d, s = self.proposed_direction, self.proposed_strength
        # proposal-relative EvidenceRole semantics (E14 review round-1 blocker 2):
        # a NEGATIVE / DIRECT proposal's DIRECT-quality failure evidence SUPPORTS
        # the NEGATIVE proposal -- it is not CONTRADICTING. CONTRADICTING is
        # reserved for the same-configuration failure half of a CONFLICTING pair.
        if d == "POSITIVE" and "SUPPORTING" not in roles:
            raise ValueError("a POSITIVE proposal needs >= 1 SUPPORTING evidence_ref")
        if d == "NEGATIVE" and "SUPPORTING" not in roles:
            raise ValueError(
                "a NEGATIVE / DIRECT proposal needs >= 1 SUPPORTING evidence_ref "
                "(its DIRECT-quality failure evidence supports the NEGATIVE proposal)"
            )
        if d == "CONFLICTING" and not {"SUPPORTING", "CONTRADICTING"} <= roles:
            raise ValueError(
                "a CONFLICTING proposal needs >= 1 SUPPORTING and >= 1 CONTRADICTING ref"
            )
        if d == "INCONCLUSIVE" and s == "DIRECT":
            if "CONTEXTUAL" not in roles or not self.evidence_refs:
                raise ValueError(
                    "a graded INCONCLUSIVE / DIRECT proposal carries CONTEXTUAL evidence_refs"
                )
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
class Tgt06ModuleRunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]  # newly created only
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    internalization_completion: InternalizationEvidenceCompletion
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
                raise ValueError(
                    "a reused_evidence_id must NOT also appear as a re-created body"
                )
        resolvable = set(ep_ids) | set(self.reused_evidence_ids)
        if not isinstance(
            self.internalization_completion, InternalizationEvidenceCompletion
        ):
            raise ValueError(
                "internalization_completion must be an InternalizationEvidenceCompletion"
            )
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
            raise ValueError(
                "a hard integrity failure must reject the run (no proposal envelope)"
            )
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


def internalization_direction(
    observation: NormalizedInternalizationObservation,
) -> str:
    """The frozen E13 item-06 ``internalization_direction_mapping``. Applied ONLY
    to a qualifying integrated antibody / epitope configuration observation
    (DIRECT rung predicate met). Evaluated in this order. The Module never parses
    basis prose and never coerces a source-reported number."""

    if observation.internalization_outcome == _PRODUCTIVE:
        return "SUPPORTS_ADDRESSABILITY"
    if observation.internalization_outcome == _FAILS:
        return "OPPOSES_ADDRESSABILITY"
    # MIXED_OR_UNRESOLVED / NOT_ESTABLISHED / INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED
    return "CONTEXTUAL"
