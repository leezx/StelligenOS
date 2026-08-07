"""External-only T12 post-review commitment contract.

The contract records an externally adjudicated sponsor-relative decision. It
does not score inputs, run T12, choose a binder route, or start Asset
Generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class ProgramCommitmentDecision(StrEnum):
    SELF_DEVELOP = "SELF_DEVELOP"
    CO_DEVELOP = "CO_DEVELOP"
    DATA_PACKAGE_ONLY = "DATA_PACKAGE_ONLY"
    PARTNER_NOW = "PARTNER_NOW"
    MONITOR = "MONITOR"
    STOP_FOR_SPONSOR = "STOP_FOR_SPONSOR"


class CommitmentStatus(StrEnum):
    COMMITTED = "COMMITTED"
    CONDITIONALLY_COMMITTED = "CONDITIONALLY_COMMITTED"
    NOT_COMMITTED = "NOT_COMMITTED"


class DownstreamStatus(StrEnum):
    BLOCKED_NO_COMMITMENT = "BLOCKED_NO_COMMITMENT"
    EXTERNAL_HANDOFF_REQUIRED = "EXTERNAL_HANDOFF_REQUIRED"


COMMITMENT_DECISIONS: Final[tuple[str, ...]] = tuple(
    decision.value for decision in ProgramCommitmentDecision
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
class ProgramCommitmentReview:
    """Sponsor-relative decision checkpoint after external T12 evidence."""

    review_id: str
    program_thesis_ref: str
    t12_decision_ref: str
    clinical_hypothesis_ref: str
    target_hypothesis_ref: str
    competition_landscape_ref: str
    ip_fto_ref: str
    sponsor_profile_ref: str
    capital_envelope_ref: str
    capability_gap_ref: str
    buyer_map_ref: str
    value_inflection_plan_ref: str
    decision: ProgramCommitmentDecision
    commitment_status: CommitmentStatus
    downstream_status: DownstreamStatus
    decision_rationale_ref: str
    condition_refs: tuple[str, ...]
    source_refs: tuple[str, ...]
    human_decision_ref: str

    def __post_init__(self) -> None:
        _require_text(self.review_id, "review_id")
        for field_name in (
            "program_thesis_ref",
            "t12_decision_ref",
            "clinical_hypothesis_ref",
            "target_hypothesis_ref",
            "competition_landscape_ref",
            "ip_fto_ref",
            "sponsor_profile_ref",
            "capital_envelope_ref",
            "capability_gap_ref",
            "buyer_map_ref",
            "value_inflection_plan_ref",
            "decision_rationale_ref",
            "human_decision_ref",
        ):
            _require_external_ref(getattr(self, field_name), field_name)
        if not isinstance(self.decision, ProgramCommitmentDecision):
            raise ValueError("decision must be a ProgramCommitmentDecision")
        if not isinstance(self.commitment_status, CommitmentStatus):
            raise ValueError("commitment_status must be a CommitmentStatus")
        if not isinstance(self.downstream_status, DownstreamStatus):
            raise ValueError("downstream_status must be a DownstreamStatus")
        _require_external_refs(self.condition_refs, "condition_refs")
        _require_external_refs(self.source_refs, "source_refs")
        if self.decision in (
            ProgramCommitmentDecision.MONITOR,
            ProgramCommitmentDecision.STOP_FOR_SPONSOR,
            ProgramCommitmentDecision.DATA_PACKAGE_ONLY,
        ) and self.downstream_status is not DownstreamStatus.BLOCKED_NO_COMMITMENT:
            raise ValueError(
                "non-asset commitment decisions must block binder/de novo routes"
            )
        if self.decision in (
            ProgramCommitmentDecision.SELF_DEVELOP,
            ProgramCommitmentDecision.CO_DEVELOP,
            ProgramCommitmentDecision.PARTNER_NOW,
        ) and self.downstream_status is not DownstreamStatus.EXTERNAL_HANDOFF_REQUIRED:
            raise ValueError(
                "asset-directed decisions require an external human handoff"
            )
        if self.decision is ProgramCommitmentDecision.STOP_FOR_SPONSOR and self.commitment_status is not CommitmentStatus.NOT_COMMITTED:
            raise ValueError("STOP_FOR_SPONSOR must be NOT_COMMITTED")
