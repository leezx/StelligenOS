"""Formal sponsor-fit assessment contract (Decision 3 / Stage 6).

This is the evidence-bearing sponsor-relative assessment that sits between
scientific opportunity qualification and the capital authorisation recorded by
`ProgramCommitmentReview@0.1.0`. It answers "is this sponsor the right one to
carry this program, and by which route", not "is the opportunity sound".

The module validates externally adjudicated assessments in memory. It computes
no aggregate score, evaluates no scientific evidence, executes no Gate, and
persists nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class SponsorFitRoute(StrEnum):
    """Route recommendation.

    Deliberately the same six values as `ProgramCommitmentDecision`. The source
    architecture note writes Decision 3's outputs as `PARTNER_BEFORE_CONJUGATION`
    and `WATCH`; those are natural-language descriptions, and Phase 3 already
    converged them to `PARTNER_NOW` and `MONITOR` to stop machine IDs drifting.
    Reusing one vocabulary keeps a recommendation and the commitment that
    consumes it comparable.
    """

    SELF_DEVELOP = "SELF_DEVELOP"
    CO_DEVELOP = "CO_DEVELOP"
    DATA_PACKAGE_ONLY = "DATA_PACKAGE_ONLY"
    PARTNER_NOW = "PARTNER_NOW"
    MONITOR = "MONITOR"
    STOP_FOR_SPONSOR = "STOP_FOR_SPONSOR"


class QuestionStatus(StrEnum):
    SATISFIED = "SATISFIED"
    UNKNOWN = "UNKNOWN"
    UNSATISFIED = "UNSATISFIED"


class CapabilityAvailability(StrEnum):
    OWNED = "owned"
    COLLABORATIVE = "collaborative"
    CRO_ACCESSIBLE = "cro_accessible"
    LICENSE_REQUIRED = "license_required"
    UNAVAILABLE = "unavailable"


SPONSOR_FIT_QUESTIONS: Final[tuple[str, ...]] = (
    "evidence_advantage",
    "capability_fit",
    "capital_fit",
    "time_fit",
    "differentiation_visibility",
    "ip_capture",
    "partnerability",
)

ASSET_DIRECTED_ROUTES: Final[tuple[SponsorFitRoute, ...]] = (
    SponsorFitRoute.SELF_DEVELOP,
    SponsorFitRoute.CO_DEVELOP,
)


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_external_ref(value: str, field_name: str) -> None:
    _require_text(value, field_name)
    if not value.startswith("external:"):
        raise ValueError(f"{field_name} must use the external: scheme")


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    if not isinstance(values, tuple):
        raise ValueError(f"{field_name} must be a tuple")
    for index, value in enumerate(values):
        _require_external_ref(value, f"{field_name}[{index}]")


@dataclass(frozen=True)
class SponsorFitQuestionResult:
    """One of the seven mandatory questions, with its external evidence."""

    question_id: str
    status: QuestionStatus
    evidence_ref: str

    def __post_init__(self) -> None:
        if self.question_id not in SPONSOR_FIT_QUESTIONS:
            raise ValueError(f"Unsupported sponsor-fit question: {self.question_id}")
        if not isinstance(self.status, QuestionStatus):
            raise ValueError("status must be a QuestionStatus")
        _require_external_ref(self.evidence_ref, "evidence_ref")


@dataclass(frozen=True)
class CapabilityMapEntry:
    """Where one required capability would have to come from."""

    capability_id: str
    availability: CapabilityAvailability
    evidence_ref: str

    def __post_init__(self) -> None:
        _require_text(self.capability_id, "capability_id")
        if not isinstance(self.availability, CapabilityAvailability):
            raise ValueError("availability must be a CapabilityAvailability")
        _require_external_ref(self.evidence_ref, "evidence_ref")


@dataclass(frozen=True)
class ResourceMapEntry:
    """One key uncertainty and what it would cost to resolve.

    `cost_band_ref` is a reference to an external estimate band. It is not a
    number, not a budget, and nothing in this module computes with it.
    """

    uncertainty_ref: str
    experiment_ref: str
    decision_changed_ref: str
    cost_band_ref: str
    capability_source: CapabilityAvailability
    failure_consequence_ref: str

    def __post_init__(self) -> None:
        for field_name in (
            "uncertainty_ref",
            "experiment_ref",
            "decision_changed_ref",
            "cost_band_ref",
            "failure_consequence_ref",
        ):
            _require_external_ref(getattr(self, field_name), field_name)
        if not isinstance(self.capability_source, CapabilityAvailability):
            raise ValueError("capability_source must be a CapabilityAvailability")


@dataclass(frozen=True)
class SponsorFitAssessment:
    """Externally adjudicated sponsor-fit assessment for one program thesis."""

    assessment_id: str
    program_thesis_ref: str
    sponsor_profile_ref: str
    scientific_opportunity_ref: str
    question_results: tuple[SponsorFitQuestionResult, ...]
    capability_map: tuple[CapabilityMapEntry, ...]
    resource_map: tuple[ResourceMapEntry, ...]
    differentiation_requires_phase_3: bool
    route: SponsorFitRoute
    route_policy_ref: str
    rationale_ref: str
    human_decision_ref: str
    source_refs: tuple[str, ...]
    asymmetric_advantage_waiver_ref: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.assessment_id, "assessment_id")
        for field_name in (
            "program_thesis_ref",
            "sponsor_profile_ref",
            "scientific_opportunity_ref",
            "route_policy_ref",
            "rationale_ref",
            "human_decision_ref",
        ):
            _require_external_ref(getattr(self, field_name), field_name)
        if not isinstance(self.route, SponsorFitRoute):
            raise ValueError("route must be a SponsorFitRoute")
        if not isinstance(self.differentiation_requires_phase_3, bool):
            raise ValueError("differentiation_requires_phase_3 must be a bool")
        _require_external_refs(self.source_refs, "source_refs")

        if not isinstance(self.question_results, tuple):
            raise ValueError("question_results must be a tuple")
        if any(
            not isinstance(result, SponsorFitQuestionResult)
            for result in self.question_results
        ):
            raise ValueError(
                "question_results must contain SponsorFitQuestionResult values"
            )
        question_ids = tuple(result.question_id for result in self.question_results)
        if len(question_ids) != len(SPONSOR_FIT_QUESTIONS) or set(question_ids) != set(
            SPONSOR_FIT_QUESTIONS
        ):
            raise ValueError(
                "question_results must answer each of the seven questions exactly once"
            )

        if not isinstance(self.capability_map, tuple) or not self.capability_map:
            raise ValueError("capability_map must be a non-empty tuple")
        if any(
            not isinstance(entry, CapabilityMapEntry) for entry in self.capability_map
        ):
            raise ValueError("capability_map must contain CapabilityMapEntry values")

        if not isinstance(self.resource_map, tuple) or not self.resource_map:
            raise ValueError("resource_map must be a non-empty tuple")
        if any(not isinstance(entry, ResourceMapEntry) for entry in self.resource_map):
            raise ValueError("resource_map must contain ResourceMapEntry values")

        statuses = {result.question_id: result.status for result in self.question_results}

        # Differentiation that only a phase 3 could show is not visible
        # differentiation, so it may not be recorded as SATISFIED.
        if (
            self.differentiation_requires_phase_3
            and statuses["differentiation_visibility"] is QuestionStatus.SATISFIED
        ):
            raise ValueError(
                "differentiation requiring phase 3 cannot be SATISFIED "
                "differentiation_visibility"
            )

        # Without an asymmetric evidence advantage a program normally cannot be
        # self-developed. "Normally" is encoded as an explicit external waiver
        # rather than as silence.
        if self.route is SponsorFitRoute.SELF_DEVELOP:
            if statuses["evidence_advantage"] is not QuestionStatus.SATISFIED:
                if self.asymmetric_advantage_waiver_ref is None:
                    raise ValueError(
                        "SELF_DEVELOP without a SATISFIED evidence_advantage requires "
                        "an explicit asymmetric_advantage_waiver_ref"
                    )
                _require_external_ref(
                    self.asymmetric_advantage_waiver_ref,
                    "asymmetric_advantage_waiver_ref",
                )
        elif self.asymmetric_advantage_waiver_ref is not None:
            raise ValueError(
                "asymmetric_advantage_waiver_ref applies only to SELF_DEVELOP"
            )

        if self.route in ASSET_DIRECTED_ROUTES and any(
            status is QuestionStatus.UNSATISFIED for status in statuses.values()
        ):
            raise ValueError(
                "an UNSATISFIED question cannot support an asset-directed route"
            )
