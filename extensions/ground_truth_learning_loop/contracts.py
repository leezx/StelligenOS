"""EXT-01 ground_truth_learning_loop: shell only.

Defines how a real-world outcome may propose a change to Rule, Model or Gate
calibration, and what governance level each change class requires.

This is a shell. Nothing here executes, and no proposal can apply itself. The
port method bodies are ``...`` on purpose.

Dependency direction is extension -> kernel. Nothing under ``src/`` may import
this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Mapping, Protocol


EXTENSION_ID: Final[str] = "EXT-01"
EXTENSION_VERSION: Final[str] = "0.1.0"
EXECUTION_POLICY: Final[str] = "disabled"


class OutcomeClass(str, Enum):
    """What kind of real-world result arrived."""

    CLINICAL_TRIAL_RESULT = "clinical_trial_result"
    PRECLINICAL_EXPERIMENT_RESULT = "preclinical_experiment_result"
    PLATFORM_FAILURE = "platform_failure"
    COMPETITOR_OUTCOME = "competitor_outcome"


class ChangeClass(str, Enum):
    """What the outcome is proposed to change.

    ``NO_CHANGE`` is a first-class option so that "we reviewed this and it does
    not move the system" is recorded explicitly, and stays distinguishable from
    "nobody looked".
    """

    EVIDENCE_ONLY = "evidence_only"
    RULE_CALIBRATION = "rule_calibration"
    MODEL_RECALIBRATION = "model_recalibration"
    GATE_THRESHOLD_REVISION = "gate_threshold_revision"
    NO_CHANGE = "no_change"


class GovernanceLevel(str, Enum):
    STANDARD_PR = "standard_pr"
    STANDARD_PR_WITH_EXPERT = "standard_pr_with_expert"
    INDEPENDENT_GOVERNANCE_TASK = "independent_governance_task"
    INDEPENDENT_GOVERNANCE_TASK_WITH_SIGNOFF = (
        "independent_governance_task_with_signoff"
    )


REQUIRED_GOVERNANCE: Final[Mapping[ChangeClass, GovernanceLevel]] = {
    ChangeClass.EVIDENCE_ONLY: GovernanceLevel.STANDARD_PR,
    ChangeClass.NO_CHANGE: GovernanceLevel.STANDARD_PR,
    ChangeClass.RULE_CALIBRATION: GovernanceLevel.STANDARD_PR_WITH_EXPERT,
    ChangeClass.MODEL_RECALIBRATION: GovernanceLevel.INDEPENDENT_GOVERNANCE_TASK,
    ChangeClass.GATE_THRESHOLD_REVISION: (
        GovernanceLevel.INDEPENDENT_GOVERNANCE_TASK_WITH_SIGNOFF
    ),
}


def _require_external_reference(reference: str, field: str) -> str:
    if not reference.startswith("external:"):
        raise ValueError(f"{field} requires an external reference")
    return reference


@dataclass(frozen=True)
class OutcomeRecord:
    """A real-world result, held by reference only."""

    outcome_id: str
    outcome_class: OutcomeClass
    outcome_ref: str
    observed_at: str

    def __post_init__(self) -> None:
        if not self.outcome_id:
            raise ValueError("outcome_id is required")
        if not self.observed_at:
            raise ValueError("observed_at is required")
        _require_external_reference(self.outcome_ref, "outcome_ref")


@dataclass(frozen=True)
class CalibrationProposal:
    """A proposed system change. Carries no ability to apply itself."""

    proposal_id: str
    outcome_id: str
    change_class: ChangeClass
    target_ref: str
    rationale_ref: str

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("proposal_id is required")
        if not self.outcome_id:
            raise ValueError("outcome_id is required")
        _require_external_reference(self.target_ref, "target_ref")
        _require_external_reference(self.rationale_ref, "rationale_ref")

    @property
    def required_governance(self) -> GovernanceLevel:
        return REQUIRED_GOVERNANCE[self.change_class]


class CalibrationEnginePort(Protocol):
    """External implementation boundary. Not implemented in this repository."""

    def ingest(self, outcome: OutcomeRecord) -> tuple[CalibrationProposal, ...]: ...
