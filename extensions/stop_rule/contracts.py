"""EXT-04 stop_rule: Evidence Sufficiency Contracts and stop-condition evaluation.

This extension answers one question the kernel does not: when is evidence for a
Gate sufficient, so that searching stops.

Boundaries enforced here:

- Advisory only. A verdict is a precondition for governed Gate execution. It
  never writes a Gate score, status, threshold or Profile binding, and never
  advances a lifecycle stage.
- Direction-neutral. Sufficiency asks whether enough independent evidence
  exists to make a judgment, not whether that judgment is positive. Sufficient
  opposing evidence ends the search just as sufficient supporting evidence
  does; which way the Gate then rules is the Gate's business.
- ``unknown`` is never negative. Running out of search budget yields
  ``INSUFFICIENT_EXHAUSTED``, which escalates to a human decision. It is never
  converted into ``FAIL``.
- Uncalibrated contracts are never actionable. A ``PROPOSED_BASELINE`` contract
  can report sufficiency, but ``StopDecision.actionable`` stays ``False`` until
  the contract is expert-calibrated.
- Ungoverned extensions are never actionable. Expert calibration is a scientific
  review of thresholds; it is not the governance approval that
  ``extensions/README.md`` requires before an extension may be used for real.
  Both gates must be open, and while EXT-04 itself is ``active_design`` the
  second one cannot be.
- Data-free. Snapshots carry aggregate counts and ``external:`` references only.

Dependency direction is extension -> kernel. Nothing under ``src/`` may import
this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Mapping, Protocol

from src.capabilities.gates import GATE_GROUPS, GATE_IDS


EXTENSION_ID: Final[str] = "EXT-04"
EXTENSION_VERSION: Final[str] = "0.1.0"
EXECUTION_POLICY: Final[str] = "advisory_only"

#: Mirrors ``extension.yaml``'s ``status``. Promotion happens there and here
#: together, only via a separate approved governance task. A test asserts the
#: two never drift.
EXTENSION_STATUS: Final[str] = "active_design"

#: The only extension status under which a decision may be acted upon.
GOVERNED_EXTENSION_STATUS: Final[str] = "governed"


class StopVerdict(str, Enum):
    """Three-valued outcome of a stop-condition evaluation.

    The third value exists so that exhausting the search budget cannot be
    silently laundered into a negative scientific finding.
    """

    SUFFICIENT = "sufficient"
    INSUFFICIENT_CONTINUE = "insufficient_continue"
    INSUFFICIENT_EXHAUSTED = "insufficient_exhausted"


class CalibrationStatus(str, Enum):
    """Whether the thresholds have had a scientific review."""

    PROPOSED_BASELINE = "proposed_baseline"
    EXPERT_CALIBRATED = "expert_calibrated"


class GovernanceStatus(str, Enum):
    """Whether use of this contract has had a governance approval.

    Orthogonal to calibration. Correct numbers reviewed by a domain expert still
    do not authorise real use until the governance gate in
    ``extensions/README.md`` has been passed.
    """

    NOT_GOVERNED = "not_governed"
    GOVERNED = "governed"


def is_actionable(
    *,
    verdict: StopVerdict,
    calibration_status: CalibrationStatus,
    governance_status: GovernanceStatus,
    extension_status: str = EXTENSION_STATUS,
) -> bool:
    """Whether a decision may justify proceeding to Gate scoring.

    Three independent gates, all of which must be open:

    1. the evidence is sufficient,
    2. the thresholds are expert-calibrated,
    3. both this contract and EXT-04 itself are governed.

    Kept a pure function so every combination is testable without mutating
    module state.
    """

    return (
        verdict is StopVerdict.SUFFICIENT
        and calibration_status is CalibrationStatus.EXPERT_CALIBRATED
        and governance_status is GovernanceStatus.GOVERNED
        and extension_status == GOVERNED_EXTENSION_STATUS
    )


def _require_external_reference(reference: str, field: str) -> str:
    if not reference.startswith("external:"):
        raise ValueError(f"{field} requires an external reference")
    return reference


def _validate_thresholds(
    *,
    min_independent_evidence: int,
    max_unresolved_conflicts: int,
    min_confidence: float,
    max_evidence_search_iterations: int,
) -> None:
    """Numeric constraints shared by contracts and baselines.

    Both carry the same thresholds, so both must reject the same nonsense.
    """

    if min_independent_evidence < 1:
        raise ValueError("min_independent_evidence must be at least 1")
    if max_unresolved_conflicts < 0:
        raise ValueError("max_unresolved_conflicts must not be negative")
    if not 0.0 < min_confidence <= 1.0:
        raise ValueError("min_confidence must fall in (0.0, 1.0]")
    if max_evidence_search_iterations < 1:
        raise ValueError("max_evidence_search_iterations must be at least 1")


@dataclass(frozen=True)
class EvidenceSufficiencyContract:
    """Per-Gate definition of "enough evidence".

    The first four criteria decide whether evidence is sufficient. The fifth,
    ``max_evidence_search_iterations``, decides whether searching may continue.
    They are independent dimensions: sufficiency is about the evidence, budget
    is about the search.

    ``min_independent_evidence`` is direction-neutral. It is met when either
    direction independently reaches the threshold.
    """

    gate_id: str
    contract_version: str
    min_independent_evidence: int
    max_unresolved_conflicts: int
    min_confidence: float
    require_major_unknown_cleared: bool
    max_evidence_search_iterations: int
    calibration_status: CalibrationStatus
    rationale_ref: str
    governance_status: GovernanceStatus = GovernanceStatus.NOT_GOVERNED
    governance_approval_ref: str | None = None

    def __post_init__(self) -> None:
        if self.gate_id not in GATE_IDS:
            raise ValueError(f"unknown kernel gate_id: {self.gate_id}")
        if not self.contract_version:
            raise ValueError("contract_version is required")
        _validate_thresholds(
            min_independent_evidence=self.min_independent_evidence,
            max_unresolved_conflicts=self.max_unresolved_conflicts,
            min_confidence=self.min_confidence,
            max_evidence_search_iterations=self.max_evidence_search_iterations,
        )
        _require_external_reference(self.rationale_ref, "rationale_ref")
        if self.governance_status is GovernanceStatus.GOVERNED:
            if self.governance_approval_ref is None:
                raise ValueError(
                    "a governed contract must cite its governance_approval_ref"
                )
            _require_external_reference(
                self.governance_approval_ref, "governance_approval_ref"
            )
        elif self.governance_approval_ref is not None:
            raise ValueError(
                "only a governed contract may carry a governance_approval_ref"
            )

    @property
    def is_expert_calibrated(self) -> bool:
        return self.calibration_status is CalibrationStatus.EXPERT_CALIBRATED

    @property
    def is_governed(self) -> bool:
        return self.governance_status is GovernanceStatus.GOVERNED


@dataclass(frozen=True)
class EvidenceLedgerSnapshot:
    """Aggregate view of the external evidence ledger for one Gate.

    Counts only. Evidence statements, sources and results stay in the external
    workspace and appear here solely as ``ledger_ref``.

    Supporting and opposing counts are both independence-qualified, so that
    sufficiency can be assessed symmetrically.
    """

    gate_id: str
    ledger_ref: str
    independent_supporting_count: int
    independent_opposing_count: int
    unknown_count: int
    unresolved_conflict_count: int
    major_unknown_count: int
    aggregate_confidence: float
    completed_search_iterations: int

    def __post_init__(self) -> None:
        if self.gate_id not in GATE_IDS:
            raise ValueError(f"unknown kernel gate_id: {self.gate_id}")
        _require_external_reference(self.ledger_ref, "ledger_ref")
        for field in (
            "independent_supporting_count",
            "independent_opposing_count",
            "unknown_count",
            "unresolved_conflict_count",
            "major_unknown_count",
            "completed_search_iterations",
        ):
            if getattr(self, field) < 0:
                raise ValueError(f"{field} must not be negative")
        if not 0.0 <= self.aggregate_confidence <= 1.0:
            raise ValueError("aggregate_confidence must fall in [0.0, 1.0]")

    @property
    def strongest_direction_count(self) -> int:
        """Independent evidence available in whichever direction is better served.

        Deliberately does not report *which* direction. Naming a direction here
        would turn an advisory sufficiency check into a verdict.
        """

        return max(
            self.independent_supporting_count, self.independent_opposing_count
        )


@dataclass(frozen=True)
class StopDecision:
    """Advisory outcome. Never a Gate result.

    ``actionable`` is the only field a caller may use to justify proceeding to
    Gate scoring. A sufficient verdict from an uncalibrated or ungoverned
    contract is informational.

    ``extension_status`` records which EXT-04 status the decision was computed
    under, so an archived decision stays auditable after EXT-04 is promoted.
    """

    gate_id: str
    verdict: StopVerdict
    unmet_criteria: tuple[str, ...]
    remaining_search_iterations: int
    requires_human_decision: bool
    actionable: bool
    calibration_status: CalibrationStatus
    governance_status: GovernanceStatus
    extension_status: str
    contract_version: str
    ledger_ref: str

    def __post_init__(self) -> None:
        if self.remaining_search_iterations < 0:
            raise ValueError("remaining_search_iterations must not be negative")
        if self.verdict is StopVerdict.SUFFICIENT and self.unmet_criteria:
            raise ValueError("a sufficient verdict must not carry unmet criteria")
        if self.verdict is not StopVerdict.SUFFICIENT and not self.unmet_criteria:
            raise ValueError("an insufficient verdict must name its unmet criteria")
        if (
            self.verdict is StopVerdict.INSUFFICIENT_EXHAUSTED
            and not self.requires_human_decision
        ):
            raise ValueError("an exhausted verdict must require a human decision")
        # One biconditional replaces a list of one-way checks, so actionability
        # can be neither forged nor hidden.
        expected = is_actionable(
            verdict=self.verdict,
            calibration_status=self.calibration_status,
            governance_status=self.governance_status,
            extension_status=self.extension_status,
        )
        if self.actionable != expected:
            raise ValueError(
                "actionable must equal the sufficiency, calibration and "
                "governance gates taken together"
            )


def evaluate_stop_condition(
    contract: EvidenceSufficiencyContract,
    snapshot: EvidenceLedgerSnapshot,
) -> StopDecision:
    """Decide whether evidence collection for one Gate may stop.

    Sufficiency and search budget are evaluated separately, so that a candidate
    which merely ran out of budget is escalated rather than failed. Sufficiency
    itself is direction-neutral, so that a decisively negative target stops the
    search instead of being searched forever.
    """

    if contract.gate_id != snapshot.gate_id:
        raise ValueError("contract and snapshot must describe the same gate_id")

    unmet: list[str] = []
    if snapshot.strongest_direction_count < contract.min_independent_evidence:
        unmet.append("min_independent_evidence")
    if snapshot.unresolved_conflict_count > contract.max_unresolved_conflicts:
        unmet.append("max_unresolved_conflicts")
    if snapshot.aggregate_confidence < contract.min_confidence:
        unmet.append("min_confidence")
    if contract.require_major_unknown_cleared and snapshot.major_unknown_count > 0:
        unmet.append("require_major_unknown_cleared")

    remaining = max(
        0,
        contract.max_evidence_search_iterations - snapshot.completed_search_iterations,
    )

    if not unmet:
        verdict = StopVerdict.SUFFICIENT
        requires_human_decision = False
    elif remaining > 0:
        verdict = StopVerdict.INSUFFICIENT_CONTINUE
        requires_human_decision = False
    else:
        verdict = StopVerdict.INSUFFICIENT_EXHAUSTED
        requires_human_decision = True

    return StopDecision(
        gate_id=contract.gate_id,
        verdict=verdict,
        unmet_criteria=tuple(unmet),
        remaining_search_iterations=remaining,
        requires_human_decision=requires_human_decision,
        actionable=is_actionable(
            verdict=verdict,
            calibration_status=contract.calibration_status,
            governance_status=contract.governance_status,
        ),
        calibration_status=contract.calibration_status,
        governance_status=contract.governance_status,
        extension_status=EXTENSION_STATUS,
        contract_version=contract.contract_version,
        ledger_ref=snapshot.ledger_ref,
    )


@dataclass(frozen=True)
class SufficiencyBaseline:
    """Proposed, uncalibrated starting point for one gate group.

    These numbers come from external expert feedback, not from calibration
    against outcomes. Every Gate must be reviewed individually before use, and
    a contract built from a baseline stays non-actionable until it is.
    """

    gate_group: str
    min_independent_evidence: int
    max_unresolved_conflicts: int
    min_confidence: float
    require_major_unknown_cleared: bool
    max_evidence_search_iterations: int

    def __post_init__(self) -> None:
        if self.gate_group not in GATE_GROUPS:
            raise ValueError(f"unknown kernel gate_group: {self.gate_group}")
        _validate_thresholds(
            min_independent_evidence=self.min_independent_evidence,
            max_unresolved_conflicts=self.max_unresolved_conflicts,
            min_confidence=self.min_confidence,
            max_evidence_search_iterations=self.max_evidence_search_iterations,
        )


DEFAULT_SUFFICIENCY_BASELINES: Final[Mapping[str, SufficiencyBaseline]] = {
    "target_opportunity": SufficiencyBaseline(
        gate_group="target_opportunity",
        min_independent_evidence=3,
        max_unresolved_conflicts=0,
        min_confidence=0.8,
        require_major_unknown_cleared=True,
        max_evidence_search_iterations=3,
    ),
    "product_realization": SufficiencyBaseline(
        gate_group="product_realization",
        min_independent_evidence=2,
        max_unresolved_conflicts=0,
        min_confidence=0.7,
        require_major_unknown_cleared=True,
        max_evidence_search_iterations=3,
    ),
    "commercial_executability": SufficiencyBaseline(
        gate_group="commercial_executability",
        min_independent_evidence=2,
        max_unresolved_conflicts=1,
        min_confidence=0.6,
        require_major_unknown_cleared=False,
        max_evidence_search_iterations=2,
    ),
}


class StopRulePort(Protocol):
    """External implementation boundary.

    An implementation resolves the governed contract for a Gate and evaluates a
    snapshot. It must not execute the Gate itself.
    """

    def contract_for(self, gate_id: str) -> EvidenceSufficiencyContract: ...

    def evaluate(
        self, snapshot: EvidenceLedgerSnapshot
    ) -> StopDecision: ...
