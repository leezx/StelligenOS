"""EXT-04 stop_rule: Evidence Sufficiency Contracts and stop-condition evaluation.

This extension answers one question the kernel does not: when is evidence for a
Gate sufficient, so that searching stops.

Boundaries enforced here:

- Advisory only. A verdict is a precondition for governed Gate execution. It
  never writes a Gate score, status, threshold or Profile binding, and never
  advances a lifecycle stage.
- ``unknown`` is never negative. Running out of search budget yields
  ``INSUFFICIENT_EXHAUSTED``, which escalates to a human decision. It is never
  converted into ``FAIL``.
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


class StopVerdict(str, Enum):
    """Three-valued outcome of a stop-condition evaluation.

    The third value exists so that exhausting the search budget cannot be
    silently laundered into a negative scientific finding.
    """

    SUFFICIENT = "sufficient"
    INSUFFICIENT_CONTINUE = "insufficient_continue"
    INSUFFICIENT_EXHAUSTED = "insufficient_exhausted"


class CalibrationStatus(str, Enum):
    PROPOSED_BASELINE = "proposed_baseline"
    EXPERT_CALIBRATED = "expert_calibrated"


def _require_external_reference(reference: str, field: str) -> str:
    if not reference.startswith("external:"):
        raise ValueError(f"{field} requires an external reference")
    return reference


@dataclass(frozen=True)
class EvidenceSufficiencyContract:
    """Per-Gate definition of "enough evidence".

    The first four criteria decide whether evidence is sufficient. The fifth,
    ``max_evidence_search_iterations``, decides whether searching may continue.
    They are independent dimensions: sufficiency is about the evidence, budget
    is about the search.
    """

    gate_id: str
    contract_version: str
    min_independent_supporting: int
    max_unresolved_conflicts: int
    min_confidence: float
    require_major_unknown_cleared: bool
    max_evidence_search_iterations: int
    calibration_status: CalibrationStatus
    rationale_ref: str

    def __post_init__(self) -> None:
        if self.gate_id not in GATE_IDS:
            raise ValueError(f"unknown kernel gate_id: {self.gate_id}")
        if not self.contract_version:
            raise ValueError("contract_version is required")
        if self.min_independent_supporting < 1:
            raise ValueError("min_independent_supporting must be at least 1")
        if self.max_unresolved_conflicts < 0:
            raise ValueError("max_unresolved_conflicts must not be negative")
        if not 0.0 < self.min_confidence <= 1.0:
            raise ValueError("min_confidence must fall in (0.0, 1.0]")
        if self.max_evidence_search_iterations < 1:
            raise ValueError("max_evidence_search_iterations must be at least 1")
        _require_external_reference(self.rationale_ref, "rationale_ref")


@dataclass(frozen=True)
class EvidenceLedgerSnapshot:
    """Aggregate view of the external evidence ledger for one Gate.

    Counts only. Evidence statements, sources and results stay in the external
    workspace and appear here solely as ``ledger_ref``.
    """

    gate_id: str
    ledger_ref: str
    independent_supporting_count: int
    opposing_count: int
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
            "opposing_count",
            "unknown_count",
            "unresolved_conflict_count",
            "major_unknown_count",
            "completed_search_iterations",
        ):
            if getattr(self, field) < 0:
                raise ValueError(f"{field} must not be negative")
        if not 0.0 <= self.aggregate_confidence <= 1.0:
            raise ValueError("aggregate_confidence must fall in [0.0, 1.0]")


@dataclass(frozen=True)
class StopDecision:
    """Advisory outcome. Never a Gate result."""

    gate_id: str
    verdict: StopVerdict
    unmet_criteria: tuple[str, ...]
    remaining_search_iterations: int
    requires_human_decision: bool
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


def evaluate_stop_condition(
    contract: EvidenceSufficiencyContract,
    snapshot: EvidenceLedgerSnapshot,
) -> StopDecision:
    """Decide whether evidence collection for one Gate may stop.

    Sufficiency and search budget are evaluated separately, so that a candidate
    which merely ran out of budget is escalated rather than failed.
    """

    if contract.gate_id != snapshot.gate_id:
        raise ValueError("contract and snapshot must describe the same gate_id")

    unmet: list[str] = []
    if snapshot.independent_supporting_count < contract.min_independent_supporting:
        unmet.append("min_independent_supporting")
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
        contract_version=contract.contract_version,
        ledger_ref=snapshot.ledger_ref,
    )


@dataclass(frozen=True)
class SufficiencyBaseline:
    """Proposed, uncalibrated starting point for one gate group.

    These numbers come from external expert feedback, not from calibration
    against outcomes. Every Gate must be reviewed individually before use.
    """

    gate_group: str
    min_independent_supporting: int
    max_unresolved_conflicts: int
    min_confidence: float
    require_major_unknown_cleared: bool
    max_evidence_search_iterations: int

    def __post_init__(self) -> None:
        if self.gate_group not in GATE_GROUPS:
            raise ValueError(f"unknown kernel gate_group: {self.gate_group}")


DEFAULT_SUFFICIENCY_BASELINES: Final[Mapping[str, SufficiencyBaseline]] = {
    "target_opportunity": SufficiencyBaseline(
        gate_group="target_opportunity",
        min_independent_supporting=3,
        max_unresolved_conflicts=0,
        min_confidence=0.8,
        require_major_unknown_cleared=True,
        max_evidence_search_iterations=3,
    ),
    "product_realization": SufficiencyBaseline(
        gate_group="product_realization",
        min_independent_supporting=2,
        max_unresolved_conflicts=0,
        min_confidence=0.7,
        require_major_unknown_cleared=True,
        max_evidence_search_iterations=3,
    ),
    "commercial_executability": SufficiencyBaseline(
        gate_group="commercial_executability",
        min_independent_supporting=2,
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
