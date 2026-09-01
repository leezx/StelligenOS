"""Frozen input / output contracts for MOD-TGT07.

Runtime Migration PR E16. In-memory contract values handed between the
deterministic Gate-specific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments.

Frozen invariants this module must never break (frozen PR E15 contract + ChatGPT
AI审核方案 E16 -- the 7 required implementation tightenings):

1. A measurable soluble form is not the same thing as a material antigen sink.
   Quantified circulating soluble target, documented sheddase processing or a
   validated secreted isoform may support the presence of a soluble-antigen
   sink-liability class at INDIRECT_STRONG, but materiality requires DIRECT
   evidence from a documented same-target PK / PD sink effect or a qualified
   quantitative TMDD analysis. A concentration value -- including a low or
   below-assay-limit value -- is never converted by the Module into a universal
   material-sink threshold. The typed classification drivers are the CLOSED enums
   ``circulating_soluble_target_status`` and ``sink_materiality_outcome`` -- never
   a number. There is NO dedicated typed raw numeric field and therefore NO
   TGT-04-style symmetric raw-value reuse-parity branch.
2. Soluble-antigen materiality is exposure-context dependent. DIRECT observations
   are bound to an auditable local ``sink_exposure_context_id`` (a SEPARATE
   namespace from the canonical Instantiation context_id). One clean DIRECT
   material-sink context is sufficient for POSITIVE / DIRECT; a canonical
   NEGATIVE / DIRECT requires a qualified intended-ADC TMDD analysis demonstrating
   no material soluble sink. Opposite DIRECT conclusions are CONFLICTING only when
   they refer to the SAME sink-exposure context; the machine has NO conflict
   resolver in v1.
3. DIRECT qualification is kind-specific and lives in ``classify.py`` alone
   (E16 tightening 1 / 3): clinical DIRECT needs same-target-therapeutic match +
   soluble-antigen attribution + analysis validation all QUALIFIED; TMDD DIRECT
   needs TMDD input adequacy + analysis validation QUALIFIED. ``aggregate.py`` and
   ``fatal_review.py`` consume the classified result and never re-judge a typed
   status. ``MIXED_OR_UNRESOLVED`` may be a DIRECT-quality CONTEXTUAL analysis;
   ``NOT_ESTABLISHED`` is NEVER a qualifying DIRECT-rung observation
   (E16 tightening 2).
4. The TGT-07 potential-fatal signal is a strict subset of POSITIVE / DIRECT, not
   a convergence rule. One qualifying DIRECT observation whose
   ``sink_materiality_outcome == MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE``
   that satisfies the clinical source path OR the TMDD source path (intended-ADC
   exposure) may surface a machine-local ``fatal_review = POTENTIAL_FATAL_PATTERN``.
   Clinical and TMDD are alternative source paths, NOT a Route A / Route B
   convergence pair; there is NO mandatory ``reproducibility_status`` predicate;
   there is NO global cancellation precondition. ``reproducibility_status`` is
   OPTIONAL factual metadata only -- never a classification / fatal /
   machine-acceptance predicate. The Module never decides fatality, KILL, HOLD,
   therapeutic efficacy or the Candidate-level consequence.
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

from .completion import SolubleAntigenEvidenceCompletion

# --- identity ---------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT07"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-07"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
#: The fixed Instantiation's frozen scientific context (PR D
#: crc_adc_target_gateset.yaml context_id / context_version). The Module must not
#: run against any other context (E15 item 10: no implicit default context). This
#: canonical context_id is a SEPARATE namespace from the LOCAL
#: ``sink_exposure_context_id`` on each observation (E10 identity-namespace gene).
CONTEXT_ID: Final[str] = "CTX-CRC-REFRACTORY-MCRC"
CONTEXT_VERSION: Final[int] = 1
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-07 contract (item 05 evidence_ceiling).
#: Reproduced only by the PROPOSAL layer -- never stamped onto a Gate-neutral
#: EvidencePackage.
TGT07_EVIDENCE_CEILING: Final[str] = (
    "a documented antigen-sink PK/PD effect, or quantitative soluble-target data "
    "plus a target-mediated-disposition analysis, for the same target"
)
#: Verbatim from src/contracts/crc_adc_target_gateset.yaml
#: gate_contracts.TGT-07.gate_question (E15 item 03).
TGT07_GATE_QUESTION: Final[str] = (
    "Is there a circulating soluble form of the target (shed ectodomain or "
    "secreted isoform) that acts as an antigen sink or alters PK / biodistribution?"
)

_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ----------------------------------------------------------------

#: What a normalized soluble-antigen observation IS. The provider supplies
#: normalized upstream facts only -- it never sets a rung, a direction, a
#: sink-liability implication or a fatal trigger. The eight kinds (E15 item 09 /
#: E15-8).
OBSERVATION_KIND_VALUES: Final[tuple[str, ...]] = (
    "CLINICAL_ANTIGEN_SINK_PK_EFFECT",
    "SOLUBLE_ANTIGEN_TMDD_ANALYSIS",
    "SOLUBLE_ANTIGEN_QUANTITATION",
    "SHEDDASE_SUBSTRATE_STATUS",
    "SECRETED_ISOFORM",
    "PREDICTED_CLEAVAGE_SITE_INFERENCE",
    "FAMILY_ANALOGY_SHEDDING_INFERENCE",
    "SEARCH_COMPLETION_AUDIT",
)
#: The two DIRECT-authority kinds -- a clinical antigen-sink PK / PD effect and a
#: soluble-antigen TMDD analysis. Only these can carry a qualifying DIRECT
#: observation (E15 item 05 / 06; E16 tightening 1).
_DIRECT_AUTHORITY_KINDS: Final[tuple[str, ...]] = (
    "CLINICAL_ANTIGEN_SINK_PK_EFFECT",
    "SOLUBLE_ANTIGEN_TMDD_ANALYSIS",
)
#: The frozen INDIRECT_STRONG classes -- all positive sink-liability support.
#: SOLUBLE_ANTIGEN_QUANTITATION only reaches INDIRECT_STRONG for a CRC-patient
#: serum QUANTIFIED_PRESENT observation (checked in classify).
_INDIRECT_STRONG_KINDS: Final[tuple[str, ...]] = (
    "SOLUBLE_ANTIGEN_QUANTITATION",
    "SHEDDASE_SUBSTRATE_STATUS",
    "SECRETED_ISOFORM",
)
#: The frozen WEAK-only inference kinds -- hypothesis / context only.
_WEAK_KINDS: Final[tuple[str, ...]] = (
    "PREDICTED_CLEAVAGE_SITE_INFERENCE",
    "FAMILY_ANALOGY_SHEDDING_INFERENCE",
)

#: The CLOSED typed soluble-antigen materiality classifier (E15 item 06 / E15-8).
#: NEVER computed by the Module from a number. The first two are "material sink"
#: outcomes; the second one means "material sink established, clinically achievable
#: exposure compromise NOT yet established".
SINK_MATERIALITY_OUTCOME_VALUES: Final[tuple[str, ...]] = (
    "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE",
    "MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE",
    "NO_MATERIAL_SOLUBLE_SINK",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
)
_MATERIAL_WITH_COMPROMISE = "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE"
_MATERIAL_WITHOUT_COMPROMISE = (
    "MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE"
)
_NO_MATERIAL_SINK = "NO_MATERIAL_SOLUBLE_SINK"
_MIXED_OR_UNRESOLVED = "MIXED_OR_UNRESOLVED"
_MATERIAL_SINK_OUTCOMES: Final[tuple[str, ...]] = (
    _MATERIAL_WITH_COMPROMISE,
    _MATERIAL_WITHOUT_COMPROMISE,
)

#: NEW CLOSED typed circulating-soluble-target status (E15-8 / tightening 2). Lets
#: E16 deterministically distinguish a measurable soluble target from below the
#: assay limit -- without ever converting a number to a threshold.
CIRCULATING_SOLUBLE_TARGET_STATUS_VALUES: Final[tuple[str, ...]] = (
    "",
    "QUANTIFIED_PRESENT",
    "BELOW_DETECTION_OR_QUANTITATION_LIMIT",
    "MIXED_OR_UNRESOLVED",
    "NOT_ESTABLISHED",
)

#: The cohort the observation was measured in (E15-8).
COHORT_CLASS_VALUES: Final[tuple[str, ...]] = (
    "",
    "CRC_PATIENT_SERUM",
    "HEALTHY_DONOR_SERUM",
    "SAME_TARGET_THERAPEUTIC_PK",
    "WELL_MATCHED_MODEL",
    "NON_CRC_CONTEXT",
    "UNRESOLVED",
)

#: The exposure scenario a TMDD analysis addresses (E15-8). A canonical
#: NEGATIVE / DIRECT (NO_MATERIAL_SOLUBLE_SINK) is authoritative ONLY for a
#: SOLUBLE_ANTIGEN_TMDD_ANALYSIS whose exposure_scenario_class is
#: INTENDED_ADC_EXPOSURE.
EXPOSURE_SCENARIO_CLASS_VALUES: Final[tuple[str, ...]] = (
    "",
    "INTENDED_ADC_EXPOSURE",
    "SAME_TARGET_THERAPEUTIC_ANALOGUE",
    "UNRESOLVED",
)

#: {QUALIFIED, NOT_ESTABLISHED} typed predicates (E15-8). Each is "does this input
#: / match / attribution / analysis qualify to enter DIRECT / fatal" -- QUALIFIED
#: is NOT a positive sink-liability conclusion.
TMDD_INPUT_ADEQUACY_STATUS_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")
ANALYSIS_VALIDATION_STATUS_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")
SAME_TARGET_THERAPEUTIC_MATCH_STATUS_VALUES: Final[tuple[str, ...]] = (
    "QUALIFIED",
    "NOT_ESTABLISHED",
)
SOLUBLE_ANTIGEN_ATTRIBUTION_STATUS_VALUES: Final[tuple[str, ...]] = (
    "QUALIFIED",
    "NOT_ESTABLISHED",
)
#: OPTIONAL factual metadata ONLY (E15 review round-1; E16 tightening 5). Never a
#: classification / fatal / machine-acceptance predicate.
REPRODUCIBILITY_STATUS_VALUES: Final[tuple[str, ...]] = ("QUALIFIED", "NOT_ESTABLISHED")

#: The Evidence-Ladder rung the Module maps an observation to (frozen PR D).
EVIDENCE_RUNG_VALUES: Final[tuple[str, ...]] = ("", "DIRECT", "INDIRECT_STRONG", "WEAK")

#: Module-assigned Gate-relative reading of a rung-classed observation
#: (sink_materiality_direction_mapping, E15 item 06).
SINK_LIABILITY_IMPLICATION_VALUES: Final[tuple[str, ...]] = (
    "",
    "SUPPORTS_SINK_LIABILITY",
    "OPPOSES_SINK_LIABILITY",
    "CONTEXTUAL",
)

FATAL_REVIEW_STATUS_VALUES: Final[tuple[str, ...]] = ("", "POTENTIAL_FATAL_PATTERN")
FATAL_SOURCE_PATH_VALUES: Final[tuple[str, ...]] = ("CLINICAL", "TMDD")

CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

#: The only Direction x Strength pairs MOD-TGT07 may propose (frozen E15 item 06 --
#: exactly SIX). Option A: a qualifying INDIRECT_STRONG soluble-antigen landscape
#: with no DIRECT sink-exposure context propagates to POSITIVE / INDIRECT_STRONG.
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


# --- provider output: normalized soluble-antigen observation ---------------

@dataclass(frozen=True)
class NormalizedSolubleAntigenObservation:
    """One already-normalized, primary/repository-source-resolved TGT-07
    soluble-antigen observation. NORMALIZED UPSTREAM FACTS only -- the provider
    never sets a rung, a direction, a sink-liability implication or a fatal
    trigger. ``analysis_method`` is an OPEN factual type; every classification
    driver is a CLOSED typed enum, never a number. A source-reported numeric fact
    ("serum soluble target 18 ng/mL", "below assay LLOQ", "K_D 2 nM") lives inside
    ``claim`` and is never coerced (E16 tightening 1 / 6).

    ``reproducibility_status`` / ``reproducibility_basis`` are OPTIONAL factual
    metadata only -- carried when an upstream source states it, shown to the human
    reviewer, NEVER a classification / fatal / machine-acceptance predicate
    (E15 review round-1; E16 tightening 5). Canonical representation: QUALIFIED
    requires a non-empty basis; NOT_ESTABLISHED requires an empty basis."""

    observation_id: str
    target_identity: str
    context_key: str
    landscape_as_of: str
    observation_kind: str
    analysis_method: str
    circulating_soluble_target_status: str
    circulating_soluble_target_basis: str
    cohort_class: str
    cohort_class_basis: str
    sink_materiality_outcome: str
    sink_materiality_outcome_basis: str
    analysis_validation_status: str
    analysis_validation_basis: str
    tmdd_input_adequacy_status: str
    tmdd_input_adequacy_basis: str
    same_target_therapeutic_match_status: str
    same_target_therapeutic_match_basis: str
    same_target_therapeutic_ref: str
    soluble_antigen_attribution_status: str
    soluble_antigen_attribution_basis: str
    exposure_scenario_class: str
    exposure_scenario_basis: str
    documents_clinical_exposure_compromise: bool
    reproducibility_status: str
    reproducibility_basis: str
    sink_exposure_context_id: str
    sink_exposure_context_basis: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    primary_or_repository_source_resolved: bool
    # --- SEARCH_COMPLETION_AUDIT-specific structured snapshot (E14-5 gene) ----
    #  the snapshot field names ARE the typed completion's field names.
    audit_search_scope: str = ""
    audit_sources_searched: tuple[str, ...] = ()
    audit_landscape_as_of: str = ""
    audit_public_soluble_antigen_search_complete: bool = False
    audit_soluble_antigen_quantitation_search_complete: bool = False
    audit_crc_patient_quantitation_subspace_search_complete: bool = False
    audit_healthy_donor_quantitation_subspace_search_complete: bool = False
    audit_sheddase_processing_search_complete: bool = False
    audit_secreted_isoform_search_complete: bool = False
    audit_same_target_pk_pd_or_tmdd_search_complete: bool = False
    audit_unresolved_item_keys: tuple[str, ...] = ()
    audit_qualifying_direct_evidence_context_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _pattern(self.observation_id, _OBS_ID, "observation_id")
        _text(self.target_identity, "target_identity")
        _text(self.context_key, "context_key")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _choice(self.observation_kind, OBSERVATION_KIND_VALUES, "observation_kind")
        _text(self.analysis_method, "analysis_method", allow_empty=True)
        _choice(
            self.circulating_soluble_target_status,
            CIRCULATING_SOLUBLE_TARGET_STATUS_VALUES,
            "circulating_soluble_target_status",
        )
        _text(
            self.circulating_soluble_target_basis,
            "circulating_soluble_target_basis",
            allow_empty=True,
        )
        _choice(self.cohort_class, COHORT_CLASS_VALUES, "cohort_class")
        _text(self.cohort_class_basis, "cohort_class_basis", allow_empty=True)
        _choice(
            self.sink_materiality_outcome,
            SINK_MATERIALITY_OUTCOME_VALUES,
            "sink_materiality_outcome",
        )
        _text(
            self.sink_materiality_outcome_basis,
            "sink_materiality_outcome_basis",
            allow_empty=True,
        )
        _choice(
            self.analysis_validation_status,
            ANALYSIS_VALIDATION_STATUS_VALUES,
            "analysis_validation_status",
        )
        _text(
            self.analysis_validation_basis, "analysis_validation_basis", allow_empty=True
        )
        _choice(
            self.tmdd_input_adequacy_status,
            TMDD_INPUT_ADEQUACY_STATUS_VALUES,
            "tmdd_input_adequacy_status",
        )
        _text(
            self.tmdd_input_adequacy_basis, "tmdd_input_adequacy_basis", allow_empty=True
        )
        _choice(
            self.same_target_therapeutic_match_status,
            SAME_TARGET_THERAPEUTIC_MATCH_STATUS_VALUES,
            "same_target_therapeutic_match_status",
        )
        _text(
            self.same_target_therapeutic_match_basis,
            "same_target_therapeutic_match_basis",
            allow_empty=True,
        )
        _text(
            self.same_target_therapeutic_ref,
            "same_target_therapeutic_ref",
            allow_empty=True,
        )
        _choice(
            self.soluble_antigen_attribution_status,
            SOLUBLE_ANTIGEN_ATTRIBUTION_STATUS_VALUES,
            "soluble_antigen_attribution_status",
        )
        _text(
            self.soluble_antigen_attribution_basis,
            "soluble_antigen_attribution_basis",
            allow_empty=True,
        )
        _choice(
            self.exposure_scenario_class,
            EXPOSURE_SCENARIO_CLASS_VALUES,
            "exposure_scenario_class",
        )
        _text(self.exposure_scenario_basis, "exposure_scenario_basis", allow_empty=True)
        _bool(
            self.documents_clinical_exposure_compromise,
            "documents_clinical_exposure_compromise",
        )
        _choice(
            self.reproducibility_status,
            REPRODUCIBILITY_STATUS_VALUES,
            "reproducibility_status",
        )
        _text(self.reproducibility_basis, "reproducibility_basis", allow_empty=True)
        _text(
            self.sink_exposure_context_id,
            "sink_exposure_context_id",
            allow_empty=True,
        )
        _text(
            self.sink_exposure_context_basis,
            "sink_exposure_context_basis",
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
        _bool(
            self.primary_or_repository_source_resolved,
            "primary_or_repository_source_resolved",
        )

        kind = self.observation_kind

        # --- local sink-exposure namespace ---------------------------------
        # a LOCAL sink_exposure_context_id may NEVER be the canonical
        # Instantiation context_id -- collapsing the two namespaces is a HARD
        # identity failure (E10 identity-namespace gene).
        if self.sink_exposure_context_id.strip() == CONTEXT_ID:
            raise ValueError(
                "a local sink_exposure_context_id must never be the canonical "
                f"Instantiation context_id {CONTEXT_ID!r} (namespace collapse)"
            )
        # a sink_exposure_context_id is REQUIRED on a would-be qualifying DIRECT
        # observation kind and MUST be empty on every other kind. (Whether an
        # observation actually reaches DIRECT is classify's job; the normalized
        # factual shape rule is simply: only the two DIRECT-authority kinds may
        # carry a sink-exposure context.)
        if self.sink_exposure_context_id.strip() and kind not in _DIRECT_AUTHORITY_KINDS:
            raise ValueError(
                f"a {kind!r} observation must carry sink_exposure_context_id == '' "
                "-- only a CLINICAL_ANTIGEN_SINK_PK_EFFECT / "
                "SOLUBLE_ANTIGEN_TMDD_ANALYSIS observation carries a sink-exposure context"
            )
        if bool(self.sink_exposure_context_id.strip()) != bool(
            self.sink_exposure_context_basis.strip()
        ):
            raise ValueError(
                "sink_exposure_context_id and sink_exposure_context_basis are set together"
            )

        # --- reproducibility_status canonical representation (E16 tightening 5)
        if self.reproducibility_status == "QUALIFIED" and not self.reproducibility_basis.strip():
            raise ValueError(
                "a QUALIFIED reproducibility_status carries a reproducibility_basis "
                "(optional factual metadata only -- never a gate)"
            )
        if self.reproducibility_basis.strip() and self.reproducibility_status == "NOT_ESTABLISHED":
            raise ValueError(
                "a reproducibility_basis without a QUALIFIED reproducibility_status is drift"
            )

        # --- classification-driving basis hygiene (E10 / E12 gene) --------
        for status, basis, sname, bname in (
            (
                self.circulating_soluble_target_status,
                self.circulating_soluble_target_basis,
                "circulating_soluble_target_status",
                "circulating_soluble_target_basis",
            ),
            (self.cohort_class, self.cohort_class_basis, "cohort_class", "cohort_class_basis"),
            (
                self.sink_materiality_outcome,
                self.sink_materiality_outcome_basis,
                "sink_materiality_outcome",
                "sink_materiality_outcome_basis",
            ),
            (
                self.exposure_scenario_class,
                self.exposure_scenario_basis,
                "exposure_scenario_class",
                "exposure_scenario_basis",
            ),
        ):
            asserted = status not in ("", "NOT_ESTABLISHED", "UNRESOLVED")
            if asserted and not basis.strip():
                raise ValueError(f"an asserted {sname} carries an auditable {bname}")
            if basis.strip() and not asserted:
                raise ValueError(f"a {bname} without an asserted {sname} is drift")
        for status, basis, sname, bname in (
            (
                self.analysis_validation_status,
                self.analysis_validation_basis,
                "analysis_validation_status",
                "analysis_validation_basis",
            ),
            (
                self.tmdd_input_adequacy_status,
                self.tmdd_input_adequacy_basis,
                "tmdd_input_adequacy_status",
                "tmdd_input_adequacy_basis",
            ),
            (
                self.same_target_therapeutic_match_status,
                self.same_target_therapeutic_match_basis,
                "same_target_therapeutic_match_status",
                "same_target_therapeutic_match_basis",
            ),
            (
                self.soluble_antigen_attribution_status,
                self.soluble_antigen_attribution_basis,
                "soluble_antigen_attribution_status",
                "soluble_antigen_attribution_basis",
            ),
        ):
            if status == "QUALIFIED" and not basis.strip():
                raise ValueError(f"a QUALIFIED {sname} carries an auditable {bname}")
            if basis.strip() and status == "NOT_ESTABLISHED":
                raise ValueError(f"a {bname} without a QUALIFIED {sname} is drift")

        # --- cross-field shape by observation kind ------------------------
        if kind == "SEARCH_COMPLETION_AUDIT":
            if self.analysis_method != "SEARCH_AUDIT":
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries analysis_method SEARCH_AUDIT"
                )
            for status_name, expect in (
                ("circulating_soluble_target_status", ""),
                ("cohort_class", ""),
                ("sink_materiality_outcome", "NOT_ESTABLISHED"),
                ("analysis_validation_status", "NOT_ESTABLISHED"),
                ("tmdd_input_adequacy_status", "NOT_ESTABLISHED"),
                ("same_target_therapeutic_match_status", "NOT_ESTABLISHED"),
                ("soluble_antigen_attribution_status", "NOT_ESTABLISHED"),
                ("exposure_scenario_class", ""),
                ("reproducibility_status", "NOT_ESTABLISHED"),
            ):
                if getattr(self, status_name) != expect:
                    raise ValueError(
                        f"a SEARCH_COMPLETION_AUDIT observation carries "
                        f"{status_name} {expect!r}"
                    )
            if self.sink_exposure_context_id.strip():
                raise ValueError(
                    "a SEARCH_COMPLETION_AUDIT observation carries no sink-exposure context"
                )
        elif kind in _INDIRECT_STRONG_KINDS or kind in _WEAK_KINDS:
            # an INDIRECT_STRONG / WEAK observation makes no materiality or
            # analysis-validation claim.
            for status_name, expect in (
                ("sink_materiality_outcome", "NOT_ESTABLISHED"),
                ("analysis_validation_status", "NOT_ESTABLISHED"),
                ("tmdd_input_adequacy_status", "NOT_ESTABLISHED"),
                ("exposure_scenario_class", ""),
            ):
                if getattr(self, status_name) != expect:
                    raise ValueError(
                        f"a {kind!r} observation carries {status_name} {expect!r}"
                    )
        if kind == "SOLUBLE_ANTIGEN_QUANTITATION":
            if self.circulating_soluble_target_status == "":
                raise ValueError(
                    "a SOLUBLE_ANTIGEN_QUANTITATION observation carries a "
                    "circulating_soluble_target_status"
                )
            if self.cohort_class == "":
                raise ValueError(
                    "a SOLUBLE_ANTIGEN_QUANTITATION observation carries a cohort_class"
                )
        if kind == "SOLUBLE_ANTIGEN_TMDD_ANALYSIS" and self.exposure_scenario_class == "":
            raise ValueError(
                "a SOLUBLE_ANTIGEN_TMDD_ANALYSIS observation carries an exposure_scenario_class"
            )

        # --- audit-snapshot shape (E14-5 gene) ---------------------------
        _text(self.audit_search_scope, "audit_search_scope", allow_empty=True)
        for name in (
            "audit_sources_searched",
            "audit_unresolved_item_keys",
            "audit_qualifying_direct_evidence_context_ids",
        ):
            if getattr(self, name):
                _str_tuple(getattr(self, name), name)
        _text(self.audit_landscape_as_of, "audit_landscape_as_of", allow_empty=True)
        _audit_bools = (
            "audit_public_soluble_antigen_search_complete",
            "audit_soluble_antigen_quantitation_search_complete",
            "audit_crc_patient_quantitation_subspace_search_complete",
            "audit_healthy_donor_quantitation_subspace_search_complete",
            "audit_sheddase_processing_search_complete",
            "audit_secreted_isoform_search_complete",
            "audit_same_target_pk_pd_or_tmdd_search_complete",
        )
        for name in _audit_bools:
            _bool(getattr(self, name), name)
        _any_audit_field = (
            bool(self.audit_search_scope.strip())
            or bool(self.audit_sources_searched)
            or bool(self.audit_landscape_as_of.strip())
            or any(getattr(self, n) for n in _audit_bools)
            or bool(self.audit_unresolved_item_keys)
            or bool(self.audit_qualifying_direct_evidence_context_ids)
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
    def is_analysis_validation_qualified(self) -> bool:
        return (
            self.analysis_validation_status == "QUALIFIED"
            and bool(self.analysis_validation_basis.strip())
            and bool(self.analysis_method.strip())
        )

    @property
    def is_tmdd_input_adequate(self) -> bool:
        return (
            self.tmdd_input_adequacy_status == "QUALIFIED"
            and bool(self.tmdd_input_adequacy_basis.strip())
        )

    @property
    def is_same_target_match_qualified(self) -> bool:
        return (
            self.same_target_therapeutic_match_status == "QUALIFIED"
            and bool(self.same_target_therapeutic_match_basis.strip())
            and bool(self.same_target_therapeutic_ref.strip())
        )

    @property
    def is_soluble_antigen_attribution_qualified(self) -> bool:
        return (
            self.soluble_antigen_attribution_status == "QUALIFIED"
            and bool(self.soluble_antigen_attribution_basis.strip())
        )

    @property
    def has_sink_exposure_context(self) -> bool:
        return bool(self.sink_exposure_context_id.strip()) and bool(
            self.sink_exposure_context_basis.strip()
        )

    @property
    def is_material_sink_outcome(self) -> bool:
        return self.sink_materiality_outcome in _MATERIAL_SINK_OUTCOMES

    @property
    def is_material_with_clinical_exposure_compromise(self) -> bool:
        return self.sink_materiality_outcome == _MATERIAL_WITH_COMPROMISE


def sink_materiality_direction(
    observation: NormalizedSolubleAntigenObservation,
) -> str:
    """The frozen E15 item-06 ``sink_materiality_direction_mapping``. Applied ONLY
    to a qualifying DIRECT observation (classify's DIRECT predicate met). The
    Module never parses basis prose and never coerces a source-reported number.

      MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE       -> SUPPORTS
      MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE -> SUPPORTS
      NO_MATERIAL_SOLUBLE_SINK (from a qualified intended-ADC TMDD)  -> OPPOSES
      NO_MATERIAL_SOLUBLE_SINK (otherwise)                          -> CONTEXTUAL
      MIXED_OR_UNRESOLVED / NOT_ESTABLISHED                         -> CONTEXTUAL
    """

    if observation.sink_materiality_outcome in _MATERIAL_SINK_OUTCOMES:
        return "SUPPORTS_SINK_LIABILITY"
    if observation.sink_materiality_outcome == _NO_MATERIAL_SINK:
        if (
            observation.observation_kind == "SOLUBLE_ANTIGEN_TMDD_ANALYSIS"
            and observation.exposure_scenario_class == "INTENDED_ADC_EXPOSURE"
            and observation.is_tmdd_input_adequate
        ):
            return "OPPOSES_SINK_LIABILITY"
        return "CONTEXTUAL"
    return "CONTEXTUAL"


# --- classification ------------------------------------------------------

@dataclass(frozen=True)
class ClassifiedSolubleAntigenObservation:
    """A provider observation placed into a FROZEN TGT-07 Evidence-Ladder rung and
    given a Module-owned Gate-relative sink-liability reading. The provider never
    sets ``evidence_rung`` or ``sink_liability_implication``.

    ``qualifying_direct_material_sink`` -- a DIRECT material-sink observation
    (sink_materiality_outcome in {MATERIAL_*}).
    ``qualifying_direct_no_material_sink`` -- a DIRECT canonical NEGATIVE
    observation (a SOLUBLE_ANTIGEN_TMDD_ANALYSIS, intended-ADC exposure, TMDD
    input adequacy QUALIFIED, NO_MATERIAL_SOLUBLE_SINK).
    ``qualifying_direct_mixed`` -- a DIRECT-quality analysis whose
    sink_materiality_outcome is MIXED_OR_UNRESOLVED.
    ``qualifying_indirect`` -- a positive INDIRECT_STRONG sink-liability
    observation. A rejected observation carries none."""

    observation: NormalizedSolubleAntigenObservation
    admissible: bool
    rejection_reason: str
    rejection_severity: str  # "" when admissible; else "HARD" | "SOFT"
    evidence_rung: str       # "" | DIRECT | INDIRECT_STRONG | WEAK
    sink_liability_implication: str  # "" | SUPPORTS_SINK_LIABILITY | OPPOSES_SINK_LIABILITY | CONTEXTUAL
    qualifying_direct_material_sink: bool
    qualifying_direct_no_material_sink: bool
    qualifying_direct_mixed: bool
    qualifying_indirect: bool

    def __post_init__(self) -> None:
        _bool(self.admissible, "admissible")
        _text(self.rejection_reason, "rejection_reason", allow_empty=True)
        _bool(self.qualifying_direct_material_sink, "qualifying_direct_material_sink")
        _bool(
            self.qualifying_direct_no_material_sink, "qualifying_direct_no_material_sink"
        )
        _bool(self.qualifying_direct_mixed, "qualifying_direct_mixed")
        _bool(self.qualifying_indirect, "qualifying_indirect")
        if self.admissible:
            _choice(self.rejection_severity, ("",), "rejection_severity")
            _choice(self.evidence_rung, EVIDENCE_RUNG_VALUES, "evidence_rung")
            _choice(
                self.sink_liability_implication,
                SINK_LIABILITY_IMPLICATION_VALUES,
                "sink_liability_implication",
            )
            n_qualifying = (
                int(self.qualifying_direct_material_sink)
                + int(self.qualifying_direct_no_material_sink)
                + int(self.qualifying_direct_mixed)
                + int(self.qualifying_indirect)
            )
            if n_qualifying > 1:
                raise ValueError("an observation qualifies for at most one rung role")
            if self.is_qualifying_direct and self.evidence_rung != "DIRECT":
                raise ValueError("a qualifying DIRECT-rung role requires evidence_rung DIRECT")
            if self.qualifying_indirect and self.evidence_rung != "INDIRECT_STRONG":
                raise ValueError("qualifying_indirect requires evidence_rung INDIRECT_STRONG")
            if self.qualifying_direct_material_sink and self.sink_liability_implication != "SUPPORTS_SINK_LIABILITY":
                raise ValueError(
                    "a qualifying material-sink DIRECT observation is SUPPORTS_SINK_LIABILITY"
                )
            if self.qualifying_direct_no_material_sink and self.sink_liability_implication != "OPPOSES_SINK_LIABILITY":
                raise ValueError(
                    "a qualifying no-material-sink DIRECT observation is OPPOSES_SINK_LIABILITY"
                )
            if self.qualifying_direct_mixed and self.sink_liability_implication != "CONTEXTUAL":
                raise ValueError(
                    "a qualifying DIRECT-quality MIXED observation is CONTEXTUAL"
                )
            if self.qualifying_indirect and self.sink_liability_implication != "SUPPORTS_SINK_LIABILITY":
                raise ValueError(
                    "a qualifying INDIRECT_STRONG observation is SUPPORTS_SINK_LIABILITY"
                )
            if self.sink_liability_implication in (
                "SUPPORTS_SINK_LIABILITY",
                "OPPOSES_SINK_LIABILITY",
            ) and not self.is_qualifying:
                raise ValueError(
                    "a directional sink_liability_implication requires a qualifying "
                    "DIRECT-rung or INDIRECT_STRONG observation"
                )
        else:
            _choice(self.rejection_severity, ("HARD", "SOFT"), "rejection_severity")
            if not self.rejection_reason:
                raise ValueError("a rejected observation must state a rejection_reason")
            if self.evidence_rung or self.sink_liability_implication:
                raise ValueError(
                    "a rejected observation has no rung or sink-liability implication"
                )
            if self.is_qualifying:
                raise ValueError("a rejected observation is not qualifying for a rung")

    @property
    def observation_id(self) -> str:
        return self.observation.observation_id

    @property
    def observation_kind(self) -> str:
        return self.observation.observation_kind

    @property
    def sink_exposure_context_id(self) -> str:
        return self.observation.sink_exposure_context_id

    @property
    def is_qualifying_direct(self) -> bool:
        return (
            self.qualifying_direct_material_sink
            or self.qualifying_direct_no_material_sink
            or self.qualifying_direct_mixed
        )

    @property
    def is_qualifying(self) -> bool:
        return self.is_qualifying_direct or self.qualifying_indirect


# --- emitted evidence (one observation -> one canonical EP) --------------

@dataclass(frozen=True)
class EmittedEvidence:
    classified: ClassifiedSolubleAntigenObservation
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedSolubleAntigenObservation):
            raise ValueError("classified must be a ClassifiedSolubleAntigenObservation")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")

    @property
    def observation(self) -> NormalizedSolubleAntigenObservation:
        return self.classified.observation

    @property
    def sink_exposure_context_id(self) -> str:
        return self.observation.sink_exposure_context_id


# --- fatal review (E15 item 08 / 12): a machine review TRIGGER ----------

@dataclass(frozen=True)
class FatalReviewRecord:
    """Non-canonical, module-local, on the run result only. NOT a proposal field,
    NOT a CandidateGateAssessment field, NOT a core object, NOT a Decision, NOT a
    Gate fatal flag. ``status`` has ONE non-empty value; the machine NEVER emits
    PUBLIC_FATAL_SIGNAL_ESTABLISHED / a canonical fatal flag / KILL / HOLD /
    Decision, and NEVER decides whether the pattern is a real fatal signal.

    ``required`` is true iff, on a completed audited landscape, there is at least
    one classified qualifying DIRECT observation whose sink_materiality_outcome ==
    MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE and that observation
    satisfies the clinical source path OR the TMDD source path. One observation on
    EITHER path is sufficient -- NOT a convergence pair, NO mandatory
    reproducibility predicate, NO global cancellation precondition."""

    required: bool
    status: str  # "" | POTENTIAL_FATAL_PATTERN
    evidence_ids: tuple[str, ...]
    sink_exposure_context_ids: tuple[str, ...]
    sink_materiality_outcome_class: tuple[str, ...]
    source_path: tuple[str, ...]
    analysis_validation_basis_refs: tuple[str, ...]
    clinical_attribution_basis_refs: tuple[str, ...]
    tmdd_input_adequacy_basis_refs: tuple[str, ...]
    landscape_as_of: str
    soluble_antigen_search_scope: str

    def __post_init__(self) -> None:
        _bool(self.required, "required")
        _choice(self.status, FATAL_REVIEW_STATUS_VALUES, "status")
        if self.required != (self.status == "POTENTIAL_FATAL_PATTERN"):
            raise ValueError("required is true iff status == POTENTIAL_FATAL_PATTERN")
        for evidence_id in self.evidence_ids:
            _pattern(evidence_id, _EP_ID, "fatal_review.evidence_ids[]")
        for name in (
            "sink_exposure_context_ids",
            "analysis_validation_basis_refs",
            "clinical_attribution_basis_refs",
            "tmdd_input_adequacy_basis_refs",
        ):
            for item in getattr(self, name):
                _text(item, f"fatal_review.{name}[]")
        for c in self.source_path:
            _choice(c, FATAL_SOURCE_PATH_VALUES, "fatal_review.source_path[]")
        _text(
            self.landscape_as_of,
            "fatal_review.landscape_as_of",
            allow_empty=not self.required,
        )
        _text(
            self.soluble_antigen_search_scope,
            "fatal_review.soluble_antigen_search_scope",
            allow_empty=not self.required,
        )
        if self.required:
            if not self.evidence_ids:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries its contributing evidence"
                )
            for c in self.sink_materiality_outcome_class:
                _choice(
                    c,
                    (_MATERIAL_WITH_COMPROMISE,),
                    "fatal_review.sink_materiality_outcome_class[]",
                )
            if not self.sink_materiality_outcome_class:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the "
                    "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE class"
                )
            if not self.source_path:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries its CLINICAL / TMDD source path(s)"
                )
            if not self.sink_exposure_context_ids:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries its qualified sink-exposure context(s)"
                )
            if not self.analysis_validation_basis_refs:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries the analysis-validation basis refs"
                )
        else:
            for name in (
                "evidence_ids",
                "sink_exposure_context_ids",
                "sink_materiality_outcome_class",
                "source_path",
                "analysis_validation_basis_refs",
                "clinical_attribution_basis_refs",
                "tmdd_input_adequacy_basis_refs",
            ):
                if getattr(self, name):
                    raise ValueError(
                        f"fatal_review.{name} is empty when required is false"
                    )

    @staticmethod
    def none() -> "FatalReviewRecord":
        return FatalReviewRecord(False, "", (), (), (), (), (), (), (), "", "")


# --- module input --------------------------------------------------------

@dataclass(frozen=True)
class Tgt07ModuleInput:
    """Everything the module needs to run one (candidate, TGT-07) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the SINGLE
    authoritative identity (MOD-TGT01 / PR E2 gene). There is no second
    drift-prone target argument and no implicit default scientific context
    (E15 item 10). ``context_id`` is the CANONICAL Instantiation context -- a
    SEPARATE namespace from each observation's LOCAL sink_exposure_context_id."""

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
    soluble_antigen_search_scope: str
    existing_evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _pattern(self.candidate_id, _CAND_ID, "candidate_id")
        _text(self.candidate_name, "candidate_name")
        _text(self.target_identity, "target_identity")
        _pattern(self.instantiation_id, _INST_ID, "instantiation_id")
        if self.instantiation_id != INSTANTIATION_ID:
            raise ValueError(f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT07")
        _pattern(self.context_id, _CTX_ID, "context_id")
        if self.context_id != CONTEXT_ID:
            raise ValueError(
                f"context_id must be {CONTEXT_ID!r} for the fixed TGT-07 Instantiation "
                "-- there is no implicit default scientific context (E15 item 10)"
            )
        _positive_int(self.context_version, "context_version")
        if self.context_version != CONTEXT_VERSION:
            raise ValueError(
                f"context_version must be {CONTEXT_VERSION} for the fixed TGT-07 Instantiation"
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
                "evidence_regime must be PUBLIC_ONLY for the current TGT-07 instantiation"
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
        _text(self.soluble_antigen_search_scope, "soluble_antigen_search_scope")
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


# --- proposal envelope (E15 item 12) ------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Carries the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` AND any TGT-01 /
    TGT-02 / TGT-03 / TGT-04 / TGT-05 / TGT-06 / TGT-08 conclusion AND any fatal
    flag (the potential-fatal signal lives in the module-local ``fatal_review``
    record) AND any concentration threshold / sink-ratio cutoff / "material
    soluble-antigen sink concentration range"."""

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
                "is not a legal TGT-07 pair (only POSITIVE/DIRECT, POSITIVE/INDIRECT_STRONG, "
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
        if self.evidence_ceiling != TGT07_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-07 ceiling verbatim")

        roles = {r for _, r in self.evidence_refs}
        d, s = self.proposed_direction, self.proposed_strength
        # proposal-relative EvidenceRole semantics (frozen E15 item 12): a
        # NEGATIVE / DIRECT proposal's intended-ADC no-material-sink TMDD evidence
        # SUPPORTS the NEGATIVE proposal -- it is not CONTRADICTING. CONTRADICTING
        # appears ONLY on a CONFLICTING / DIRECT proposal (the same-context
        # no-material-sink DIRECT half).
        if d == "POSITIVE" and "SUPPORTING" not in roles:
            raise ValueError("a POSITIVE proposal needs >= 1 SUPPORTING evidence_ref")
        if d == "NEGATIVE" and "SUPPORTING" not in roles:
            raise ValueError(
                "a NEGATIVE / DIRECT proposal needs >= 1 SUPPORTING evidence_ref "
                "(its intended-ADC no-material-sink TMDD evidence supports the NEGATIVE proposal)"
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
class Tgt07ModuleRunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]  # newly created only
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    soluble_antigen_completion: SolubleAntigenEvidenceCompletion
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
            self.soluble_antigen_completion, SolubleAntigenEvidenceCompletion
        ):
            raise ValueError(
                "soluble_antigen_completion must be a SolubleAntigenEvidenceCompletion"
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
