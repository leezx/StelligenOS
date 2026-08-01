"""External end-to-end closure contract for a demonstration asset."""

from dataclasses import dataclass
from typing import Final, Protocol


DEMO_ASSET_REF: Final[str] = "external:demo/tweakr"
CLOSURE_STAGES: Final[tuple[str, ...]] = (
    "opportunity_generation", "opportunity_validation", "asset_generation", "asset_development"
)


@dataclass(frozen=True)
class ClosureRequest:
    demo_asset_ref: str
    stage_input_refs: tuple[str, ...]
    decision_refs: tuple[str, ...]
    run_context_ref: str

    def __post_init__(self) -> None:
        _require_external(self.demo_asset_ref, *self.stage_input_refs, *self.decision_refs, self.run_context_ref)


@dataclass(frozen=True)
class ClosureResult:
    demo_asset_ref: str
    completed_stage_refs: tuple[str, ...]
    unresolved_risk_refs: tuple[str, ...]
    final_decision_ref: str

    def __post_init__(self) -> None:
        _require_external(self.demo_asset_ref, *self.completed_stage_refs, *self.unresolved_risk_refs, self.final_decision_ref)


class EndToEndClosurePort(Protocol):
    def close(self, request: ClosureRequest) -> ClosureResult:
        """Close an external demonstration run without repository persistence."""
        ...


def _require_external(*references: str) -> None:
    if any(not reference.startswith("external:") for reference in references):
        raise ValueError("End-to-end closure requires external references")
