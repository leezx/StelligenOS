"""Data-free StelligenOS boot and architecture smoke boundary."""

from dataclasses import dataclass
from typing import Final

from src.capabilities.binder_adc_routes import ROUTE_IDS
from src.capabilities.gates import GATE_GROUPS


LIFECYCLE_STAGES: Final[tuple[str, ...]] = (
    "opportunity_generation",
    "opportunity_validation",
    "asset_generation",
    "asset_development",
)
CAPABILITY_IDS: Final[tuple[str, ...]] = (
    "opportunity_discovery",
    "knowledge_mining",
    "rule_learning",
    "evidence_extraction",
    "adc_design",
    "binder_engineering",
    "patent_analysis",
    "due_diligence",
    "portfolio_management",
)


def require_external_reference(reference: str) -> str:
    """Accept only references owned by an external workspace."""

    if not reference.startswith("external:"):
        raise ValueError("OS boot requires external workspace references")
    return reference


@dataclass(frozen=True)
class BootRequest:
    """External context needed to start an architecture-only OS run."""

    workspace_ref: str
    run_context_ref: str
    policy_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for reference in (
            self.workspace_ref,
            self.run_context_ref,
            self.policy_ref,
        ):
            require_external_reference(reference)


@dataclass(frozen=True)
class BootReport:
    """The boot plan; it contains references and static architecture only."""

    status: str
    contract_version: str
    lifecycle_stages: tuple[str, ...]
    capability_ids: tuple[str, ...]
    gate_groups: tuple[str, ...]
    route_ids: tuple[str, ...]
    workspace_ref: str
    run_context_ref: str
    policy_ref: str


def boot(request: BootRequest) -> BootReport:
    """Load the frozen architecture without executing or persisting anything."""

    return BootReport(
        status="ready_for_external_runtime",
        contract_version=request.contract_version,
        lifecycle_stages=LIFECYCLE_STAGES,
        capability_ids=CAPABILITY_IDS,
        gate_groups=GATE_GROUPS,
        route_ids=ROUTE_IDS,
        workspace_ref=request.workspace_ref,
        run_context_ref=request.run_context_ref,
        policy_ref=request.policy_ref,
    )
