"""Pure contracts for the ``gen_indication_endpoint_target`` module.

Instances are in-memory contract values. They are not records, database
models, evidence stores, or executable Gate/Rule/Model evaluators.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final


EXTERNAL_PREFIX: Final[str] = "external:"


def _require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _require_external(value: str, field_name: str) -> str:
    _require_non_empty(value, field_name)
    if not value.startswith(EXTERNAL_PREFIX):
        raise ValueError(f"{field_name} must be an external reference")
    return value


def _require_ids(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        _require_non_empty(value, field_name)


def _require_external_ids(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        _require_external(value, field_name)


class EvaluationStatus(str, Enum):
    """Status values that preserve unknown or unevaluated domains."""

    EVALUATED = "EVALUATED"
    NOT_EVALUATED = "NOT_EVALUATED"
    UNRESOLVED = "UNRESOLVED"


class CandidateDisposition(str, Enum):
    """Early filter disposition; this enum is explicitly not a Gate result."""

    RETAIN = "RETAIN"
    EXCLUDE = "EXCLUDE"
    DEFER = "DEFER"


class EvidenceDirection(str, Enum):
    SUPPORTS = "SUPPORTS"
    OPPOSES = "OPPOSES"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class ReviewStatus(str, Enum):
    UNREVIEWED = "UNREVIEWED"
    REVIEWED = "REVIEWED"
    DISPUTED = "DISPUTED"


class ClinicalLockState(str, Enum):
    """Progressive maturity of the clinical/product hypothesis."""

    EXPLORATORY = "exploratory"
    PROVISIONAL = "provisional"
    ANCHORED = "anchored"
    PRODUCT_LOCKED = "product-locked"
    PROTOCOL_LOCKED = "protocol-locked"
    REGULATORY_LOCKED = "regulatory-locked"


class ClinicalHypothesisEntryMode(str, Enum):
    MATURE_TARGET_FIRST = "mature-target-first"
    TARGET_CONTEXT_COSELECTION = "target-context-co-selection"
    CLINICAL_PROBLEM_FIRST = "clinical-problem-first"


class BiomarkerCutoffStatus(str, Enum):
    DEFERRED = "deferred"
    EXPLORATORY = "exploratory"
    PROVISIONAL = "provisional"
    LOCKED = "locked"
    NOT_REQUIRED = "not_required"


class CDxStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    CONCEPT = "concept"
    VALIDATING = "validating"
    LOCKED = "locked"


_LOCK_ORDER: Final[tuple[ClinicalLockState, ...]] = (
    ClinicalLockState.EXPLORATORY,
    ClinicalLockState.PROVISIONAL,
    ClinicalLockState.ANCHORED,
    ClinicalLockState.PRODUCT_LOCKED,
    ClinicalLockState.PROTOCOL_LOCKED,
    ClinicalLockState.REGULATORY_LOCKED,
)


def can_transition_clinical_lock(
    current: ClinicalLockState, target: ClinicalLockState
) -> bool:
    """Allow only monotonic, single-step maturity transitions."""

    if not isinstance(current, ClinicalLockState) or not isinstance(target, ClinicalLockState):
        return False
    return _LOCK_ORDER.index(target) == _LOCK_ORDER.index(current) + 1


@dataclass(frozen=True)
class AnchorClinicalContext:
    """Design context used before a final indication label exists."""

    context_id: str
    anchor_indication: str
    disease_setting: str
    line_of_therapy: str
    treatment_context: str
    patient_population: str
    comparator: str
    expansion_indications: tuple[str, ...]
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "context_id", "anchor_indication", "disease_setting",
            "line_of_therapy", "treatment_context", "patient_population",
            "comparator",
        ):
            _require_non_empty(getattr(self, name), name)
        _require_ids(self.expansion_indications, "expansion_indications")
        _require_external_ids(self.source_refs, "source_refs")


@dataclass(frozen=True)
class IntendedBenefitHypothesis:
    """Early clinical value direction, separate from measured results."""

    benefit_id: str
    benefit_class: str
    rationale: str
    endpoint_class: str
    source_refs: tuple[str, ...]
    endpoint_measurement_plan_ref: str | None = None
    protocol_endpoint_ref: str | None = None
    observed_endpoint_performance_ref: str | None = None

    def __post_init__(self) -> None:
        for name in ("benefit_id", "benefit_class", "rationale", "endpoint_class"):
            _require_non_empty(getattr(self, name), name)
        for name in (
            "endpoint_measurement_plan_ref",
            "protocol_endpoint_ref",
            "observed_endpoint_performance_ref",
        ):
            value = getattr(self, name)
            if value is not None:
                _require_external(value, name)
        _require_external_ids(self.source_refs, "source_refs")


@dataclass(frozen=True)
class BiomarkerHypothesis:
    """Early biology and assay feasibility; cutoff and CDx remain deferred."""

    biomarker_id: str
    biological_feature: str
    specimen_type: str
    assay_method: str
    measurement_scale: str
    heterogeneity_risk: str
    assay_feasibility: str
    source_refs: tuple[str, ...]
    final_cutoff_deferred: bool = True
    cutoff_status: BiomarkerCutoffStatus = BiomarkerCutoffStatus.DEFERRED
    final_cutoff_ref: str | None = None
    cdx_status: CDxStatus = CDxStatus.NOT_REQUIRED
    cdx_ref: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "biomarker_id", "biological_feature", "specimen_type", "assay_method",
            "measurement_scale", "heterogeneity_risk", "assay_feasibility",
        ):
            _require_non_empty(getattr(self, name), name)
        _require_external_ids(self.source_refs, "source_refs")
        if not isinstance(self.cutoff_status, BiomarkerCutoffStatus):
            raise ValueError("cutoff_status must be a BiomarkerCutoffStatus")
        if not isinstance(self.cdx_status, CDxStatus):
            raise ValueError("cdx_status must be a CDxStatus")
        if self.final_cutoff_ref is not None:
            _require_external(self.final_cutoff_ref, "final_cutoff_ref")
        if self.cdx_ref is not None:
            _require_external(self.cdx_ref, "cdx_ref")
        if self.cutoff_status == BiomarkerCutoffStatus.LOCKED and self.final_cutoff_ref is None:
            raise ValueError("locked cutoff status requires final_cutoff_ref")
        if self.cdx_status == CDxStatus.LOCKED and self.cdx_ref is None:
            raise ValueError("locked CDx status requires cdx_ref")


@dataclass(frozen=True)
class ProductHypothesis:
    """ADC design constraints derived from the clinical context."""

    product_id: str
    modality: str
    payload_class: str
    linker_profile: str
    bystander_requirement: str
    desired_internalization_profile: str
    acceptable_toxicity_envelope: str
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "product_id", "modality", "payload_class", "linker_profile",
            "bystander_requirement", "desired_internalization_profile",
            "acceptable_toxicity_envelope",
        ):
            _require_non_empty(getattr(self, name), name)
        if self.modality != "ADC":
            raise ValueError("ProductHypothesis requires modality=ADC")
        _require_external_ids(self.source_refs, "source_refs")


@dataclass(frozen=True)
class ClinicalHypothesis:
    """The v5 development unit: target x anchor context x intended benefit."""

    hypothesis_id: str
    target_ref: str | None = None
    anchor_context_ref: str | None = None
    intended_benefit_ref: str | None = None
    biomarker_hypothesis_ref: str | None = None
    product_hypothesis_ref: str | None = None
    lock_state: ClinicalLockState = ClinicalLockState.EXPLORATORY
    source_refs: tuple[str, ...] = ()
    entry_mode: ClinicalHypothesisEntryMode = ClinicalHypothesisEntryMode.TARGET_CONTEXT_COSELECTION
    protocol_endpoint_ref: str | None = None
    final_indication_ref: str | None = None
    registrational_endpoint_ref: str | None = None
    biomarker_cutoff_ref: str | None = None
    cdx_ref: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.hypothesis_id, "hypothesis_id")
        if not isinstance(self.lock_state, ClinicalLockState):
            raise ValueError("lock_state must be a ClinicalLockState")
        if not isinstance(self.entry_mode, ClinicalHypothesisEntryMode):
            raise ValueError("entry_mode must be a ClinicalHypothesisEntryMode")
        for name in (
            "target_ref", "anchor_context_ref", "intended_benefit_ref",
            "biomarker_hypothesis_ref", "product_hypothesis_ref",
        ):
            value = getattr(self, name)
            if value is not None:
                _require_external(value, name)
        _require_external_ids(self.source_refs, "source_refs")
        for name in (
            "protocol_endpoint_ref", "final_indication_ref",
            "registrational_endpoint_ref", "biomarker_cutoff_ref", "cdx_ref",
        ):
            value = getattr(self, name)
            if value is not None:
                _require_external(value, name)
        required_by_state = {
            ClinicalLockState.EXPLORATORY: (),
            ClinicalLockState.PROVISIONAL: ("target_ref", "anchor_context_ref", "intended_benefit_ref"),
            ClinicalLockState.ANCHORED: ("target_ref", "anchor_context_ref", "intended_benefit_ref", "biomarker_hypothesis_ref"),
            ClinicalLockState.PRODUCT_LOCKED: ("target_ref", "anchor_context_ref", "intended_benefit_ref", "biomarker_hypothesis_ref", "product_hypothesis_ref"),
            ClinicalLockState.PROTOCOL_LOCKED: (
                "target_ref", "anchor_context_ref", "intended_benefit_ref",
                "biomarker_hypothesis_ref", "product_hypothesis_ref",
                "protocol_endpoint_ref",
            ),
            ClinicalLockState.REGULATORY_LOCKED: (
                "target_ref", "anchor_context_ref", "intended_benefit_ref",
                "biomarker_hypothesis_ref", "product_hypothesis_ref",
                "protocol_endpoint_ref", "final_indication_ref",
                "registrational_endpoint_ref", "biomarker_cutoff_ref", "cdx_ref",
            ),
        }
        for name in required_by_state.get(self.lock_state, ()):
            if getattr(self, name) is None:
                raise ValueError(f"{self.lock_state.value} requires {name}")
        if self.entry_mode == ClinicalHypothesisEntryMode.MATURE_TARGET_FIRST and self.target_ref is None:
            raise ValueError("mature-target-first requires target_ref")
        if self.entry_mode == ClinicalHypothesisEntryMode.CLINICAL_PROBLEM_FIRST and self.intended_benefit_ref is None:
            raise ValueError("clinical-problem-first requires intended_benefit_ref")
        if (
            self.entry_mode == ClinicalHypothesisEntryMode.TARGET_CONTEXT_COSELECTION
            and not any((self.target_ref, self.anchor_context_ref, self.intended_benefit_ref))
        ):
            raise ValueError("target-context-co-selection requires a target, anchor, or benefit seed")


class CandidateLifecycle(str, Enum):
    SCOPE_DEFINED = "SCOPE_DEFINED"
    CLINICAL_FRAME_GENERATED = "CLINICAL_FRAME_GENERATED"
    CLINICAL_FRAME_RETAINED = "CLINICAL_FRAME_RETAINED"
    TARGET_CANDIDATE_GENERATED = "TARGET_CANDIDATE_GENERATED"
    UNDER_T_GATE_EVALUATION = "UNDER_T_GATE_EVALUATION"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    CONDITIONALLY_RETAINED = "CONDITIONALLY_RETAINED"
    REJECTED = "REJECTED"
    READY_FOR_ADVERSARIAL_REVIEW = "READY_FOR_ADVERSARIAL_REVIEW"
    READY_FOR_T12_DECISION = "READY_FOR_T12_DECISION"
    OPPORTUNITY_RETAINED = "OPPORTUNITY_RETAINED"
    OPPORTUNITY_ON_HOLD = "OPPORTUNITY_ON_HOLD"
    OPPORTUNITY_REJECTED = "OPPORTUNITY_REJECTED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class OpportunitySearchScope:
    """The immutable search boundary supplied by an external workspace."""

    scope_id: str
    version: str
    indication: str | None = None
    disease_setting: str | None = None
    line_of_therapy: str | None = None
    treatment_context: str | None = None
    comparator: str | None = None
    patient_segment_constraints: tuple[str, ...] = ()
    endpoint_definition: str | None = None
    endpoint_time_horizon: str | None = None
    clinical_success_condition: str | None = None
    modality: str = "ADC"
    evidence_cutoff_date: str = ""
    candidate_budget: int = 1
    source_policy_id: str = ""
    evaluation_plan_id: str = ""
    clinical_hypothesis_seed_ref: str | None = None
    entry_mode: ClinicalHypothesisEntryMode = ClinicalHypothesisEntryMode.TARGET_CONTEXT_COSELECTION

    def __post_init__(self) -> None:
        for name in (
            "scope_id",
            "version",
            "modality",
        ):
            value = getattr(self, name)
            if value is not None:
                _require_non_empty(value, name)
        _require_ids(self.patient_segment_constraints, "patient_segment_constraints")
        for name in ("source_policy_id", "evaluation_plan_id", "clinical_hypothesis_seed_ref"):
            value = getattr(self, name)
            if value:
                _require_external(value, name)
        if not isinstance(self.entry_mode, ClinicalHypothesisEntryMode):
            raise ValueError("entry_mode must be a ClinicalHypothesisEntryMode")
        if self.clinical_hypothesis_seed_ref is None:
            for name in (
                "indication", "disease_setting", "line_of_therapy", "treatment_context",
                "comparator", "endpoint_definition", "endpoint_time_horizon",
                "clinical_success_condition", "evidence_cutoff_date", "source_policy_id",
                "evaluation_plan_id",
            ):
                _require_non_empty(getattr(self, name), name)
        else:
            for name in (
                "indication", "disease_setting", "line_of_therapy", "treatment_context",
                "comparator", "endpoint_definition", "endpoint_time_horizon",
                "clinical_success_condition", "evidence_cutoff_date", "source_policy_id",
                "evaluation_plan_id",
            ):
                value = getattr(self, name)
                if value:
                    _require_non_empty(value, name)
        if self.modality != "ADC":
            raise ValueError("gen_indication_endpoint_target requires modality=ADC")
        if self.candidate_budget < 1:
            raise ValueError("candidate_budget must be positive")


@dataclass(frozen=True)
class ClinicalFrame:
    """A constrained clinical frame produced by T0/T1 work."""

    frame_id: str
    scope_id: str
    indication: str | None = None
    disease_setting: str | None = None
    line_of_therapy: str | None = None
    treatment_context: str | None = None
    comparator: str | None = None
    endpoint_definition: str | None = None
    endpoint_time_horizon: str | None = None
    endpoint_driving_population: str | None = None
    source_evidence_ids: tuple[str, ...] = ()
    t0_gate_result_ref: str = ""
    t1_gate_result_ref: str = ""
    status: EvaluationStatus = EvaluationStatus.EVALUATED
    clinical_hypothesis_ref: str | None = None
    lock_state: ClinicalLockState = ClinicalLockState.PROVISIONAL
    endpoint_class: str | None = None
    protocol_endpoint_ref: str | None = None
    observed_endpoint_performance_ref: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "frame_id",
            "scope_id",
            "indication",
            "disease_setting",
            "line_of_therapy",
            "treatment_context",
            "comparator",
            "endpoint_definition",
            "endpoint_time_horizon",
            "endpoint_driving_population",
        ):
            value = getattr(self, name)
            if value is not None:
                _require_non_empty(value, name)
        _require_external_ids(self.source_evidence_ids, "source_evidence_ids")
        for name in ("t0_gate_result_ref", "t1_gate_result_ref", "clinical_hypothesis_ref", "protocol_endpoint_ref", "observed_endpoint_performance_ref"):
            value = getattr(self, name)
            if value:
                _require_external(value, name)
        if self.clinical_hypothesis_ref is None:
            for name in ("indication", "endpoint_definition", "t0_gate_result_ref", "t1_gate_result_ref"):
                _require_non_empty(getattr(self, name), name)
        if not isinstance(self.lock_state, ClinicalLockState):
            raise ValueError("lock_state must be a ClinicalLockState")


@dataclass(frozen=True)
class TargetCandidate:
    """A target hypothesis candidate with an auditable clinical identity."""

    candidate_id: str
    clinical_frame_id: str
    indication: str | None = None
    patient_population: str | None = None
    clinical_endpoint: str | None = None
    adc_target: str | None = None
    disease_setting: str | None = None
    line_of_therapy: str | None = None
    treatment_context: str | None = None
    comparator: str | None = None
    endpoint_time_horizon: str | None = None
    biological_hypothesis: str | None = None
    adc_hypothesis: str | None = None
    generation_method: str | None = None
    source_run_ref: str = ""
    positive_evidence_ids: tuple[str, ...] = ()
    negative_evidence_ids: tuple[str, ...] = ()
    unknown_claims: tuple[str, ...] = ()
    lifecycle: CandidateLifecycle = CandidateLifecycle.TARGET_CANDIDATE_GENERATED
    clinical_hypothesis_ref: str | None = None
    lock_state: ClinicalLockState = ClinicalLockState.PROVISIONAL
    legacy_compatibility: bool = False

    def __post_init__(self) -> None:
        for name in ("candidate_id", "clinical_frame_id"):
            _require_non_empty(getattr(self, name), name)
        if self.clinical_hypothesis_ref is None:
            if not self.legacy_compatibility:
                raise ValueError("legacy candidate path requires legacy_compatibility=True")
            for name in (
                "indication", "patient_population", "clinical_endpoint", "adc_target",
                "disease_setting", "line_of_therapy", "treatment_context", "comparator",
                "endpoint_time_horizon",
            ):
                _require_non_empty(getattr(self, name), name)
        else:
            _require_external(self.clinical_hypothesis_ref, "clinical_hypothesis_ref")
            for name in (
                "indication", "patient_population", "clinical_endpoint", "adc_target",
                "disease_setting", "line_of_therapy", "treatment_context", "comparator",
                "endpoint_time_horizon",
            ):
                value = getattr(self, name)
                if value is not None:
                    _require_non_empty(value, name)
        for name in ("biological_hypothesis", "adc_hypothesis", "generation_method"):
            _require_non_empty(getattr(self, name), name)
        _require_external(self.source_run_ref, "source_run_ref")
        _require_external_ids(self.positive_evidence_ids, "positive_evidence_ids")
        _require_external_ids(self.negative_evidence_ids, "negative_evidence_ids")
        _require_ids(self.unknown_claims, "unknown_claims")
        if not isinstance(self.lock_state, ClinicalLockState):
            raise ValueError("lock_state must be a ClinicalLockState")

    @property
    def opportunity_identity(self) -> tuple[str, str, str, str]:
        """Return the required indication/population/endpoint/target identity."""

        return (
            self.indication,
            self.patient_population,
            self.clinical_endpoint,
            self.adc_target,
        )


@dataclass(frozen=True)
class CandidateFilterResult:
    """Non-Gate early filtering result that preserves insufficient evidence."""

    filter_id: str
    candidate_id: str
    disposition: CandidateDisposition
    status: EvaluationStatus
    reason_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    filter_policy_ref: str = ""

    def __post_init__(self) -> None:
        for name in ("filter_id", "candidate_id"):
            _require_non_empty(getattr(self, name), name)
        _require_ids(self.reason_codes, "reason_codes")
        _require_external_ids(self.evidence_ids, "evidence_ids")
        if self.filter_policy_ref:
            _require_external(self.filter_policy_ref, "filter_policy_ref")


@dataclass(frozen=True)
class EvidenceRecord:
    """Minimum provenance contract for an externally managed evidence claim."""

    evidence_id: str
    claim_id: str
    candidate_id: str
    clinical_frame_id: str
    gate_id: str
    rule_id: str
    model_id: str
    evidence_type: str
    direction: EvidenceDirection
    source_type: str
    source_reference: str
    source_date: str
    access_date: str
    extraction_method: str
    raw_observation: str
    normalized_claim: str
    confidence: float
    limitations: tuple[str, ...]
    independence_group: str
    review_status: ReviewStatus

    def __post_init__(self) -> None:
        for name in (
            "evidence_id",
            "claim_id",
            "candidate_id",
            "clinical_frame_id",
            "gate_id",
            "rule_id",
            "model_id",
            "evidence_type",
            "source_type",
            "source_date",
            "access_date",
            "extraction_method",
            "raw_observation",
            "normalized_claim",
            "independence_group",
        ):
            _require_non_empty(getattr(self, name), name)
        _require_external(self.source_reference, "source_reference")
        _require_ids(self.limitations, "limitations")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class AdversarialReview:
    """Review record; it is not a Gate and cannot create a Gate result."""

    review_id: str
    candidate_id: str
    objections: tuple[str, ...]
    counter_evidence_ids: tuple[str, ...]
    alternative_explanations: tuple[str, ...]
    critical_unknowns: tuple[str, ...]
    validation_tasks: tuple[str, ...]
    reviewer_ref: str
    status: EvaluationStatus

    def __post_init__(self) -> None:
        _require_non_empty(self.review_id, "review_id")
        _require_non_empty(self.candidate_id, "candidate_id")
        _require_ids(self.objections, "objections")
        _require_external_ids(self.counter_evidence_ids, "counter_evidence_ids")
        _require_ids(self.alternative_explanations, "alternative_explanations")
        _require_ids(self.critical_unknowns, "critical_unknowns")
        _require_ids(self.validation_tasks, "validation_tasks")
        _require_external(self.reviewer_ref, "reviewer_ref")


@dataclass(frozen=True)
class TargetOpportunityHandoff:
    """T12 handoff contract that returns references, never local records."""

    handoff_id: str
    candidate_id: str
    opportunity_ref: str
    target_hypothesis_ref: str
    t12_gate_result_ref: str
    evidence_refs: tuple[str, ...]
    adversarial_review_ref: str
    lifecycle: CandidateLifecycle
    readiness: EvaluationStatus
    clinical_hypothesis_ref: str | None = None
    clinical_lock_state: ClinicalLockState | None = None
    anchor_context_ref: str | None = None
    legacy_compatibility: bool = False

    def __post_init__(self) -> None:
        _require_non_empty(self.handoff_id, "handoff_id")
        _require_non_empty(self.candidate_id, "candidate_id")
        for name in (
            "opportunity_ref",
            "target_hypothesis_ref",
            "t12_gate_result_ref",
            "adversarial_review_ref",
        ):
            _require_external(getattr(self, name), name)
        _require_external_ids(self.evidence_refs, "evidence_refs")
        for name in ("clinical_hypothesis_ref", "anchor_context_ref"):
            value = getattr(self, name)
            if value is not None:
                _require_external(value, name)
        if self.clinical_hypothesis_ref is None:
            if not self.legacy_compatibility:
                raise ValueError("legacy T12 path requires legacy_compatibility=True")
            if self.clinical_lock_state is not None:
                raise ValueError("legacy T12 path cannot carry clinical_lock_state")
        elif self.clinical_lock_state is None:
            raise ValueError("v5 T12 path requires clinical_hypothesis_ref and clinical_lock_state")
        if self.clinical_lock_state is not None and not isinstance(self.clinical_lock_state, ClinicalLockState):
            raise ValueError("clinical_lock_state must be a ClinicalLockState")
