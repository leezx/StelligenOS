"""Frozen input / output contracts for MOD-TGT05.

Runtime Migration PR E4. In-memory contract values handed between the
deterministic scientific core and its injected ports. They are not records,
database rows, evidence stores, or canonical assessments.

TGT-05 is a ONE-WAY normal-tissue liability detector, never a safety predictor
(frozen E3 contract). Two rules this module must never break:

* TGT-05's "negative data" is mostly COVERAGE information, not safety evidence --
  a validated atlas NOT_DETECTED proves a tissue was checked, never that the
  target is safe. It is never a NEGATIVE direction and never a WEAK rung.
* ``fatal_review`` is a machine-generated review TRIGGER, not a machine-generated
  fatal CONCLUSION. The machine may emit at most ``POTENTIAL_FATAL_PATTERN``;
  "materially distinct constructs" / "truly target-mediated" / "biologically
  meaningful convergence" are human-review-reserved.
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

# --- identity ---------------------------------------------------------------

MODULE_ID: Final[str] = "MOD-TGT05"
MODULE_VERSION: Final[str] = "1.0.0"
GATE_ID: Final[str] = "TGT-05"
GATE_VERSION: Final[str] = "1.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "1.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v1"
CANDIDATE_LEVEL: Final[str] = "L04"

#: Verbatim from the frozen PR D TGT-05 contract. Reproduced only by the PROPOSAL
#: layer -- never stamped onto a Gate-neutral EvidencePackage.
TGT05_EVIDENCE_CEILING: Final[str] = (
    "clinical (ADC-specific for DIRECT) or protein-level human normal-tissue "
    "expression in vital organs; RNA-only atlases do not reach it"
)
TGT05_GATE_QUESTION: Final[str] = (
    "Is there evidence of accessible normal-human-tissue expression, or observed "
    "target-mediated toxicity, that creates a potentially material "
    "on-target / off-tumor liability for ADC development? (fatal-first gate -- "
    "a target-level public-evidence gate, not a product-specific "
    "therapeutic-window judgement)"
)

_SRC_ID = re.compile(r"^SRC-[0-9]{8}$")
_EP_ID = re.compile(r"^EP-[0-9]{8}$")
_CAND_ID = re.compile(r"^CAND-L04-[0-9]{6}$")
_CTX_ID = re.compile(r"^CTX-[A-Z0-9-]+$")
_INST_ID = re.compile(r"^INST-[A-Z0-9-]+-v[0-9]+$")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_EVT_ID = re.compile(r"^EVT-[A-Za-z0-9._:-]+$")
_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")

# --- enums ----------------------------------------------------------------

#: What a normalized record is allowed to do for TGT-05 (E4-2). The provider
#: never sets a rung or a direction -- those are MOD-TGT05 scientific authority.
EVIDENCE_FUNCTION_VALUES: Final[tuple[str, ...]] = (
    "LIABILITY_RUNG_EVIDENCE",     # A -- establishes DIRECT / INDIRECT_STRONG / WEAK
    "ATTRIBUTION_ADJUDICATION",    # B -- supports / refutes target attribution; may form CONFLICTING; never a NEGATIVE rung
    "COVERAGE_CONTEXT",            # C -- "this tissue was checked"; never a rung, never safety
)
OBSERVATION_KIND_VALUES: Final[tuple[str, ...]] = (
    "ADC_CLINICAL_TOXICITY",
    "NON_ADC_CLINICAL_TOXICITY",
    "HUMAN_NORMAL_EXPRESSION",
    "NHP_TOXICITY",
    "RODENT_NORMAL_OR_TOXICITY",
)
MOLECULAR_LAYER_VALUES: Final[tuple[str, ...]] = ("", "PROTEIN", "RNA", "OTHER")
FINDING_VALUES: Final[tuple[str, ...]] = ("", "DETECTED", "NOT_DETECTED", "NOT_APPLICABLE")
TARGET_ATTRIBUTION_STANCE_VALUES: Final[tuple[str, ...]] = (
    "",
    "SUPPORTS_TARGET_ATTRIBUTION",
    "REFUTES_TARGET_ATTRIBUTION",
    "UNRESOLVED",
)
VITAL_ORGAN_CLASSES: Final[tuple[str, ...]] = (
    "CNS",
    "CARDIAC",
    "HEPATIC",
    "PULMONARY",
    "HEMATOPOIETIC",
    "GASTROINTESTINAL",
)
COVERAGE_RESULT_VALUES: Final[tuple[str, ...]] = (
    "ADMISSIBLE_PROTEIN_DATA_FOUND",
    "PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA",
    "NOT_YET_COMPLETE",
)
FATAL_REVIEW_STATUS_VALUES: Final[tuple[str, ...]] = ("", "POTENTIAL_FATAL_PATTERN")

CANONICAL_ONLY_FIELDS: Final[tuple[str, ...]] = (
    "assessment_id",
    "assessment_version",
    "review",
)

_RANK: Final[dict[str, int]] = {"DIRECT": 3, "INDIRECT_STRONG": 2, "WEAK": 1}


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


# --- provider output ------------------------------------------------------

@dataclass(frozen=True)
class NormalizedLiabilityRecord:
    """One already-normalized, primary-source-resolved TGT-05 observation.

    The provider supplies FACTS only. It never sets ``ladder_rung`` or
    ``direction``. A record's ``evidence_function`` names which of the three
    TGT-05 data flows it belongs to (E4-2). N/A fields carry explicit empty
    values -- semantics are never expressed by omission.
    """

    observation_id: str
    liability_event_id: str
    evidence_function: str
    target_identity: str
    observation_kind: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    primary_source_resolved: bool
    species: str = ""
    modality: str = ""
    molecular_layer: str = ""
    finding: str = ""
    atlas_validated: bool = False
    vital_organ_class: str = ""
    affected_tissue: str = ""
    cell_compartment: str = ""
    program_id: str = ""
    construct_fingerprint: str = ""
    toxicity_phenotype_raw: str = ""
    toxicity_phenotype_key: str = ""
    observed_severity: str = ""
    target_attribution_stance: str = ""
    target_attribution_basis: str = ""
    translational_relevance: bool = False

    def __post_init__(self) -> None:
        _pattern(self.observation_id, _OBS_ID, "observation_id")
        _pattern(self.liability_event_id, _EVT_ID, "liability_event_id")
        _choice(self.evidence_function, EVIDENCE_FUNCTION_VALUES, "evidence_function")
        _text(self.target_identity, "target_identity")
        _choice(self.observation_kind, OBSERVATION_KIND_VALUES, "observation_kind")
        _text(self.claim, "claim")
        _pattern(self.source_id, _SRC_ID, "source_id")
        _choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _text(self.source_identifier, "source_identifier")
        _text(self.locator, "locator", allow_empty=True)
        _text(self.retrieved_at, "retrieved_at")
        if not _ISO_DATE_PREFIX.match(self.retrieved_at):
            raise ValueError("retrieved_at must start with an ISO date")
        _bool(self.primary_source_resolved, "primary_source_resolved")
        for name in ("species", "modality", "affected_tissue", "cell_compartment",
                     "program_id", "construct_fingerprint", "toxicity_phenotype_raw",
                     "toxicity_phenotype_key", "observed_severity",
                     "target_attribution_basis"):
            _text(getattr(self, name), name, allow_empty=True)
        _choice(self.molecular_layer, MOLECULAR_LAYER_VALUES, "molecular_layer")
        _choice(self.finding, FINDING_VALUES, "finding")
        _bool(self.atlas_validated, "atlas_validated")
        _choice(self.vital_organ_class, ("", *VITAL_ORGAN_CLASSES), "vital_organ_class")
        _choice(
            self.target_attribution_stance,
            TARGET_ATTRIBUTION_STANCE_VALUES,
            "target_attribution_stance",
        )
        _bool(self.translational_relevance, "translational_relevance")

        # cross-field shape by observation kind
        if self.observation_kind in ("ADC_CLINICAL_TOXICITY", "NON_ADC_CLINICAL_TOXICITY"):
            for req in ("program_id", "construct_fingerprint", "affected_tissue",
                        "toxicity_phenotype_key"):
                if not getattr(self, req).strip():
                    raise ValueError(
                        f"{self.observation_kind} record needs a non-empty {req}"
                    )
            if not self.target_attribution_stance:
                raise ValueError(
                    f"{self.observation_kind} record needs a target_attribution_stance"
                )
        if self.observation_kind == "HUMAN_NORMAL_EXPRESSION":
            if not self.molecular_layer:
                raise ValueError("HUMAN_NORMAL_EXPRESSION record needs a molecular_layer")
            if not self.finding:
                raise ValueError("HUMAN_NORMAL_EXPRESSION record needs a finding")
            if not self.vital_organ_class:
                raise ValueError("HUMAN_NORMAL_EXPRESSION record needs a vital_organ_class")
        if (
            self.target_attribution_stance == "SUPPORTS_TARGET_ATTRIBUTION"
            and not self.target_attribution_basis.strip()
        ):
            raise ValueError(
                "SUPPORTS_TARGET_ATTRIBUTION needs a non-empty target_attribution_basis"
            )
        # COVERAGE_CONTEXT is exactly a validated human protein NOT_DETECTED
        if self.evidence_function == "COVERAGE_CONTEXT":
            if not (
                self.observation_kind == "HUMAN_NORMAL_EXPRESSION"
                and self.molecular_layer == "PROTEIN"
                and self.atlas_validated
                and self.finding == "NOT_DETECTED"
            ):
                raise ValueError(
                    "a COVERAGE_CONTEXT record is a validated human PROTEIN atlas "
                    "with finding NOT_DETECTED"
                )

    # --- factual predicates (no science, just field reads) --------------------
    @property
    def is_adc_clinical_toxicity(self) -> bool:
        return self.observation_kind == "ADC_CLINICAL_TOXICITY"

    @property
    def attribution_supported(self) -> bool:
        return self.target_attribution_stance == "SUPPORTS_TARGET_ATTRIBUTION"

    @property
    def attribution_refuted(self) -> bool:
        return self.target_attribution_stance == "REFUTES_TARGET_ATTRIBUTION"

    @property
    def is_validated_human_protein_detected(self) -> bool:
        return (
            self.observation_kind == "HUMAN_NORMAL_EXPRESSION"
            and self.molecular_layer == "PROTEIN"
            and self.atlas_validated
            and self.finding == "DETECTED"
        )

    @property
    def is_validated_human_protein_not_detected(self) -> bool:
        return (
            self.observation_kind == "HUMAN_NORMAL_EXPRESSION"
            and self.molecular_layer == "PROTEIN"
            and self.atlas_validated
            and self.finding == "NOT_DETECTED"
        )

    @property
    def is_rna_normal_signal(self) -> bool:
        return (
            self.observation_kind == "HUMAN_NORMAL_EXPRESSION"
            and self.molecular_layer == "RNA"
            and self.finding == "DETECTED"
        )

    @property
    def is_rodent_only(self) -> bool:
        return self.observation_kind == "RODENT_NORMAL_OR_TOXICITY"

    @property
    def is_nhp_translational_toxicity(self) -> bool:
        return (
            self.observation_kind == "NHP_TOXICITY"
            and self.translational_relevance
        )


# --- module input --------------------------------------------------------

@dataclass(frozen=True)
class Tgt05ModuleInput:
    """Everything the module needs to run one (candidate, TGT-05) assessment.

    ``target_identity`` is the candidate's canonical target antigen -- the SINGLE
    authoritative identity (MOD-TGT01 / PR E2 gene). No implicit default
    scientific context.
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
            raise ValueError(f"instantiation_id must be {INSTANTIATION_ID!r} for MOD-TGT05")
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
            raise ValueError("evidence_regime must be PUBLIC_ONLY for TGT-05")
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
class ClassifiedLiability:
    """A provider record placed against the frozen TGT-05 Evidence Ladder and
    the E4-2 three-way evidence-function split."""

    record: NormalizedLiabilityRecord
    admissible: bool
    rejection_reason: str
    rejection_severity: str  # "" when admissible; else "HARD" | "SOFT"
    evidence_function: str   # LIABILITY_RUNG_EVIDENCE / ATTRIBUTION_ADJUDICATION / COVERAGE_CONTEXT
    ladder_rung: str         # "" unless it establishes a rung
    evidence_class: str
    attribution_stance: str  # "" | SUPPORTS_TARGET_ATTRIBUTION | REFUTES_TARGET_ATTRIBUTION
    covered_vital_organ: str  # "" unless COVERAGE_CONTEXT

    def __post_init__(self) -> None:
        _bool(self.admissible, "admissible")
        _text(self.rejection_reason, "rejection_reason", allow_empty=True)
        _choice(self.evidence_function, EVIDENCE_FUNCTION_VALUES, "evidence_function")
        if self.admissible:
            _choice(self.rejection_severity, ("",), "rejection_severity")
            if self.evidence_function == "LIABILITY_RUNG_EVIDENCE":
                if self.ladder_rung not in GRADED_STRENGTHS:
                    raise ValueError("a LIABILITY_RUNG_EVIDENCE record has a graded rung")
                _text(self.evidence_class, "evidence_class")
            else:
                if self.ladder_rung != "":
                    raise ValueError("only LIABILITY_RUNG_EVIDENCE carries a rung")
            if self.evidence_function == "COVERAGE_CONTEXT":
                _choice(self.covered_vital_organ, VITAL_ORGAN_CLASSES, "covered_vital_organ")
            elif self.covered_vital_organ:
                raise ValueError("covered_vital_organ is only set on COVERAGE_CONTEXT")
        else:
            _choice(self.rejection_severity, ("HARD", "SOFT"), "rejection_severity")
            if not self.rejection_reason:
                raise ValueError("a rejected record must state a rejection_reason")
            if self.ladder_rung != "":
                raise ValueError("a rejected record has no ladder rung")
        _choice(
            self.attribution_stance,
            ("", "SUPPORTS_TARGET_ATTRIBUTION", "REFUTES_TARGET_ATTRIBUTION"),
            "attribution_stance",
        )

    @property
    def liability_event_id(self) -> str:
        return self.record.liability_event_id

    @property
    def establishes_rung(self) -> bool:
        return self.admissible and self.evidence_function == "LIABILITY_RUNG_EVIDENCE"


# --- emitted evidence (one observation -> one canonical EP) ----------------

@dataclass(frozen=True)
class EmittedEvidence:
    classified: ClassifiedLiability
    evidence_id: str
    package: EvidencePackage
    reused: bool

    def __post_init__(self) -> None:
        _pattern(self.evidence_id, _EP_ID, "evidence_id")
        if not isinstance(self.classified, ClassifiedLiability):
            raise ValueError("classified must be a ClassifiedLiability")
        if not isinstance(self.package, EvidencePackage):
            raise ValueError("package must be an EvidencePackage")
        if self.package.evidence_id != self.evidence_id:
            raise ValueError("package.evidence_id must equal evidence_id")
        _bool(self.reused, "reused")


# --- coverage + sweep completion (E4-6) ----------------------------------

@dataclass(frozen=True)
class VitalOrganCoverageState:
    search_complete: bool
    coverage_result: str

    def __post_init__(self) -> None:
        _bool(self.search_complete, "search_complete")
        _choice(self.coverage_result, COVERAGE_RESULT_VALUES, "coverage_result")
        if not self.search_complete and self.coverage_result != "NOT_YET_COMPLETE":
            raise ValueError("an incomplete search must carry coverage_result NOT_YET_COMPLETE")
        if self.search_complete and self.coverage_result == "NOT_YET_COMPLETE":
            raise ValueError("a complete search cannot carry NOT_YET_COMPLETE")

    @property
    def exhausted_without_admissible_protein(self) -> bool:
        return (
            self.search_complete
            and self.coverage_result == "PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA"
        )


@dataclass(frozen=True)
class Tgt05SweepCompletionRecord:
    same_target_adc_construct_inventory_complete: bool
    adc_toxicity_attribution_sweep_complete: bool
    non_adc_same_target_toxicity_sweep_complete: bool
    nhp_sweep_complete: bool
    rna_supporting_sweep_complete: bool
    vital_organ_protein_coverage: dict  # {VITAL_ORGAN_CLASS: VitalOrganCoverageState}

    def __post_init__(self) -> None:
        for name in (
            "same_target_adc_construct_inventory_complete",
            "adc_toxicity_attribution_sweep_complete",
            "non_adc_same_target_toxicity_sweep_complete",
            "nhp_sweep_complete",
            "rna_supporting_sweep_complete",
        ):
            _bool(getattr(self, name), name)
        if set(self.vital_organ_protein_coverage) != set(VITAL_ORGAN_CLASSES):
            raise ValueError(
                "vital_organ_protein_coverage must have exactly the six vital organs"
            )
        for organ, state in self.vital_organ_protein_coverage.items():
            if not isinstance(state, VitalOrganCoverageState):
                raise ValueError(f"{organ} coverage must be a VitalOrganCoverageState")

    @property
    def all_vital_organ_searches_complete(self) -> bool:
        return all(
            s.search_complete for s in self.vital_organ_protein_coverage.values()
        )

    @property
    def path_c_sweeps_complete(self) -> bool:
        return (
            self.non_adc_same_target_toxicity_sweep_complete
            and self.nhp_sweep_complete
            and self.rna_supporting_sweep_complete
            and self.all_vital_organ_searches_complete
        )

    @property
    def path_b_sweeps_complete(self) -> bool:
        return (
            self.same_target_adc_construct_inventory_complete
            and self.adc_toxicity_attribution_sweep_complete
        )


@dataclass(frozen=True)
class CoverageMapRecord:
    """The structured vital-organ coverage projection on the run result. Machine
    reads it only for the UNKNOWN branch and for critical_unknowns -- never to
    turn 'no risk found' into safety."""

    by_organ: tuple[tuple[str, str, bool], ...]  # (organ, coverage_result, search_complete)
    supporting_evidence_ids: tuple[tuple[str, tuple[str, ...]], ...]  # (organ, [EP ids])

    def __post_init__(self) -> None:
        organs = [o for o, _, _ in self.by_organ]
        if sorted(organs) != sorted(VITAL_ORGAN_CLASSES):
            raise ValueError("coverage map must cover exactly the six vital organs")
        for organ, result, done in self.by_organ:
            _choice(organ, VITAL_ORGAN_CLASSES, "coverage_map.organ")
            _choice(result, COVERAGE_RESULT_VALUES, "coverage_map.coverage_result")
            _bool(done, "coverage_map.search_complete")
        for organ, ids in self.supporting_evidence_ids:
            _choice(organ, VITAL_ORGAN_CLASSES, "supporting_evidence_ids.organ")
            for evidence_id in ids:
                _pattern(evidence_id, _EP_ID, "supporting_evidence_ids[]")


# --- fatal review (E4-5): a machine-generated review TRIGGER --------------

@dataclass(frozen=True)
class FatalReviewRecord:
    """Non-canonical, module-local, on the run result only. NOT a proposal
    field, NOT a CandidateGateAssessment field, NOT an EvidencePackage field,
    NOT a core object, NOT a Decision. ``status`` has ONE non-empty value; the
    machine NEVER emits PUBLIC_FATAL_SIGNAL_ESTABLISHED."""

    required: bool
    status: str  # "" | POTENTIAL_FATAL_PATTERN
    evidence_ids: tuple[str, ...]
    program_ids: tuple[str, ...]
    construct_fingerprints: tuple[str, ...]
    affected_tissues: tuple[str, ...]
    target_attribution_basis_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _bool(self.required, "required")
        _choice(self.status, FATAL_REVIEW_STATUS_VALUES, "status")
        if self.required != (self.status == "POTENTIAL_FATAL_PATTERN"):
            raise ValueError("required is true iff status == POTENTIAL_FATAL_PATTERN")
        for evidence_id in self.evidence_ids:
            _pattern(evidence_id, _EP_ID, "fatal_review.evidence_ids[]")
        for name in ("program_ids", "construct_fingerprints", "affected_tissues",
                     "target_attribution_basis_refs"):
            for item in getattr(self, name):
                _text(item, f"fatal_review.{name}[]")
        if self.required:
            if len(set(self.program_ids)) < 2:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN needs >= 2 distinct program_ids"
                )
            if not self.evidence_ids or not self.construct_fingerprints:
                raise ValueError(
                    "a POTENTIAL_FATAL_PATTERN carries its contributing evidence and fingerprints"
                )
        else:
            for name in ("evidence_ids", "program_ids", "construct_fingerprints",
                         "affected_tissues", "target_attribution_basis_refs"):
                if getattr(self, name):
                    raise ValueError(f"fatal_review.{name} is empty when required is false")

    @staticmethod
    def none() -> "FatalReviewRecord":
        return FatalReviewRecord(False, "", (), (), (), (), ())


# --- proposal envelope (E3 item 12) --------------------------------------

@dataclass(frozen=True)
class AssessmentProposalEnvelope:
    """Non-canonical, module-local. Carries the canonical assessment identity
    pins + scientific fields for a deterministic canonicalisation; omits
    ``assessment_id`` / ``assessment_version`` / ``review`` AND any fatal flag
    (the potential-fatal-pattern signal lives in the fatal_review record)."""

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
        if self.evidence_ceiling != TGT05_EVIDENCE_CEILING:
            raise ValueError("evidence_ceiling must be the frozen TGT-05 ceiling verbatim")
        # NEGATIVE is essentially unreachable on the public path; the module
        # never proposes it.
        if self.proposed_direction == "NEGATIVE":
            raise ValueError("MOD-TGT05 never proposes NEGATIVE on the public path")
        if self.proposed_direction == "POSITIVE" and not self.evidence_refs:
            raise ValueError("a POSITIVE proposal needs >= 1 evidence_ref")
        if self.proposed_direction == "CONFLICTING":
            roles = {r for _, r in self.evidence_refs}
            if not {"SUPPORTING", "CONTRADICTING"} <= roles:
                raise ValueError(
                    "CONFLICTING needs >= 1 SUPPORTING and >= 1 CONTRADICTING ref"
                )
        if (self.proposed_direction == "INCONCLUSIVE"
                and self.proposed_strength == "UNKNOWN" and self.evidence_refs):
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


# --- run result --------------------------------------------------------

@dataclass(frozen=True)
class Tgt05ModuleRunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]  # newly created only
    reused_evidence_ids: tuple[str, ...]
    proposal_envelope: AssessmentProposalEnvelope | None
    machine_acceptance: MachineAcceptanceRecord
    sweep_completion: Tgt05SweepCompletionRecord
    coverage_map: CoverageMapRecord
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
        if not isinstance(self.fatal_review, FatalReviewRecord):
            raise ValueError("fatal_review must be a FatalReviewRecord")
        if not isinstance(self.coverage_map, CoverageMapRecord):
            raise ValueError("coverage_map must be a CoverageMapRecord")
        for program_id, reason in self.hard_integrity_failures:
            _text(program_id, "hard_integrity_failures.program_id")
            _text(reason, "hard_integrity_failures.reason")
        for program_id, reason in self.rejected_records:
            _text(program_id, "rejected_records.program_id")
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
        if self.proposal_envelope is not None:
            for evidence_id, _ in self.proposal_envelope.evidence_refs:
                if evidence_id not in resolvable:
                    raise ValueError(
                        "proposal evidence_ref does not resolve to an emitted or reused package"
                    )
