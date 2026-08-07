"""External contracts for the two Binder/ADC generation routes.

The routes describe orchestration boundaries only. Scientific inputs, tools,
models, observations, candidates, and reports remain in an external workspace.

`BinderAdcRouteRequest@0.2.0` additionally binds the two frozen sponsor-relative
hard controls to the route entry point: no route request can be constructed
without a `ProgramCommitmentReview@0.2.0` reference, a `ValueInflectionPlan@0.1.0`
reference, and an external human authorization reference. The three values are
opaque external references. This module never dereferences, re-adjudicates, or
generates them, and it does not import either contract's classes.
"""

from dataclasses import dataclass
from typing import Final, Protocol

EXTERNAL_REFERENCE_SCHEME: Final[str] = "external:"

SPONSOR_CONTROL_REQUEST_FIELDS: Final[tuple[str, ...]] = (
    "program_commitment_review_ref",
    "value_inflection_plan_ref",
    "asset_generation_authorization_ref",
)

REQUIRED_REQUEST_REFERENCE_FIELDS: Final[tuple[str, ...]] = (
    "input_ref",
    "opportunity_ref",
    "program_commitment_review_ref",
    "value_inflection_plan_ref",
    "asset_generation_authorization_ref",
    "policy_ref",
    "tool_environment_ref",
    "run_context_ref",
)


EXISTING_BINDER_ROUTE: Final[str] = "existing_binder_asset_engineering"
EPITOPE_DE_NOVO_ROUTE: Final[str] = "epitope_conditioned_de_novo_antibody_discovery"
ROUTE_IDS: Final[tuple[str, ...]] = (EXISTING_BINDER_ROUTE, EPITOPE_DE_NOVO_ROUTE)

EXISTING_BINDER_STAGES: Final[tuple[str, ...]] = (
    "binder_intake",
    "sequence_normalization",
    "structural_analysis",
    "liability_analysis",
    "developability_analysis",
    "adc_carrier_phenotype",
    "delivery_cascade",
    "failure_mode_analysis",
    "evidence_graph",
    "pareto_selection",
    "construct_specification",
    "adc_product_matrix",
    "asset_report",
    "run_manifest",
)

EPITOPE_DE_NOVO_STAGES: Final[tuple[str, ...]] = (
    "target_biology",
    "antigen_engineering",
    "epitope_engineering",
    "ip_fto_guided_epitope_selection",
    "structural_preparation",
    "negative_design",
    "epitope_conditioned_de_novo_design",
    "computational_ranking",
    "asset_diversity_optimization",
    "focused_wet_lab_design",
    "structural_validation",
    "affinity_maturation",
    "adc_readiness",
    "patent_package",
    "asset_report",
)


@dataclass(frozen=True)
class BinderAdcRouteRequest:
    """External references needed to run either route.

    The three sponsor-control references have no defaults on purpose: omitting
    any of them must fail at construction time, not at route execution time.
    """

    route_id: str
    input_ref: str
    opportunity_ref: str
    program_commitment_review_ref: str
    value_inflection_plan_ref: str
    asset_generation_authorization_ref: str
    policy_ref: str
    tool_environment_ref: str
    run_context_ref: str
    contract_version: str = "0.2.0"

    def __post_init__(self) -> None:
        if self.route_id not in ROUTE_IDS:
            raise ValueError(f"Unknown Binder/ADC route: {self.route_id}")
        for field_name in REQUIRED_REQUEST_REFERENCE_FIELDS:
            reference = getattr(self, field_name)
            if not isinstance(reference, str) or not reference.startswith(
                EXTERNAL_REFERENCE_SCHEME
            ):
                raise ValueError(
                    f"{field_name} must be a non-empty external: reference"
                )
            if not reference[len(EXTERNAL_REFERENCE_SCHEME) :].strip():
                raise ValueError(
                    f"{field_name} must be a non-empty external: reference"
                )


@dataclass(frozen=True)
class BinderAdcRouteResult:
    """External package references returned by a route runtime."""

    route_id: str
    run_ref: str
    package_ref: str
    candidate_refs: tuple[str, ...]
    report_ref: str
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        if self.route_id not in ROUTE_IDS:
            raise ValueError(f"Unknown Binder/ADC route: {self.route_id}")
        for reference in (
            self.run_ref,
            self.package_ref,
            *self.candidate_refs,
            self.report_ref,
        ):
            if not reference.startswith("external:"):
                raise ValueError("Binder/ADC results require external references")


class BinderAdcRoutePort(Protocol):
    """Port implemented by an external scientific route runtime.

    The port receives the sponsor-control references but is not the authority
    that grants them. Selecting a route remains an explicit external act.
    """

    def run(self, request: BinderAdcRouteRequest) -> BinderAdcRouteResult:
        """Run externally without writing Gate scores or repository state."""

        ...


def route_stages(route_id: str) -> tuple[str, ...]:
    """Return the frozen stage catalog for one route."""

    if route_id == EXISTING_BINDER_ROUTE:
        return EXISTING_BINDER_STAGES
    if route_id == EPITOPE_DE_NOVO_ROUTE:
        return EPITOPE_DE_NOVO_STAGES
    raise KeyError(route_id)
