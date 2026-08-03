"""EXT-03 asset_search_engine: shell only.

Registers the ADC asset search axes and the generators attached to each, so
that axes currently served by standard-platform defaults stay visibly deferred
rather than silently permanent.

This is a shell. All generator outputs are declared to flow into the existing
Product Realization Gates; no second evaluation path is introduced. The port
method bodies are ``...`` on purpose.

Dependency direction is extension -> kernel. Nothing under ``src/`` may import
this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Protocol


EXTENSION_ID: Final[str] = "EXT-03"
EXTENSION_VERSION: Final[str] = "0.1.0"
EXECUTION_POLICY: Final[str] = "disabled"


SEARCH_AXES: Final[tuple[str, ...]] = (
    "binder",
    "payload",
    "linker",
    "dar",
    "conjugation_site",
    "fc_design",
    "half_life",
    "affinity_tuning",
    "epitope_shifting",
    "internalization_enhancement",
)


class GeneratorStatus(str, Enum):
    """Why an axis is or is not being searched.

    ``STANDARD_PLATFORM_DEFAULT`` records an interim compromise explicitly, so
    that it remains reviewable instead of becoming an unexamined default.
    """

    KERNEL_IMPLEMENTED = "kernel_implemented"
    STANDARD_PLATFORM_DEFAULT = "standard_platform_default"
    NOT_IMPLEMENTED = "not_implemented"


@dataclass(frozen=True)
class GeneratorSpec:
    """One generator on one search axis."""

    generator_id: str
    search_axis: str
    status: GeneratorStatus
    kernel_route_id: str | None = None

    def __post_init__(self) -> None:
        if not self.generator_id:
            raise ValueError("generator_id is required")
        if self.search_axis not in SEARCH_AXES:
            raise ValueError(f"unknown search_axis: {self.search_axis}")
        if self.status is GeneratorStatus.KERNEL_IMPLEMENTED and not self.kernel_route_id:
            raise ValueError(
                "a kernel_implemented generator must name its kernel_route_id"
            )
        if self.status is not GeneratorStatus.KERNEL_IMPLEMENTED and self.kernel_route_id:
            raise ValueError(
                "only a kernel_implemented generator may name a kernel_route_id"
            )


GENERATOR_REGISTRY: Final[tuple[GeneratorSpec, ...]] = (
    GeneratorSpec(
        generator_id="existing_binder_engineering",
        search_axis="binder",
        status=GeneratorStatus.KERNEL_IMPLEMENTED,
        kernel_route_id="existing_binder_asset_engineering",
    ),
    GeneratorSpec(
        generator_id="epitope_conditioned_de_novo",
        search_axis="binder",
        status=GeneratorStatus.KERNEL_IMPLEMENTED,
        kernel_route_id="epitope_conditioned_de_novo_antibody_discovery",
    ),
    GeneratorSpec(
        generator_id="payload_selection",
        search_axis="payload",
        status=GeneratorStatus.STANDARD_PLATFORM_DEFAULT,
    ),
    GeneratorSpec(
        generator_id="linker_selection",
        search_axis="linker",
        status=GeneratorStatus.STANDARD_PLATFORM_DEFAULT,
    ),
    GeneratorSpec(
        generator_id="dar_optimization",
        search_axis="dar",
        status=GeneratorStatus.STANDARD_PLATFORM_DEFAULT,
    ),
    GeneratorSpec(
        generator_id="site_specific_conjugation",
        search_axis="conjugation_site",
        status=GeneratorStatus.STANDARD_PLATFORM_DEFAULT,
    ),
    GeneratorSpec(
        generator_id="fc_engineering",
        search_axis="fc_design",
        status=GeneratorStatus.NOT_IMPLEMENTED,
    ),
    GeneratorSpec(
        generator_id="half_life_tuning",
        search_axis="half_life",
        status=GeneratorStatus.NOT_IMPLEMENTED,
    ),
    GeneratorSpec(
        generator_id="affinity_tuning",
        search_axis="affinity_tuning",
        status=GeneratorStatus.NOT_IMPLEMENTED,
    ),
    GeneratorSpec(
        generator_id="epitope_shifting",
        search_axis="epitope_shifting",
        status=GeneratorStatus.NOT_IMPLEMENTED,
    ),
    GeneratorSpec(
        generator_id="internalization_enhancement",
        search_axis="internalization_enhancement",
        status=GeneratorStatus.NOT_IMPLEMENTED,
    ),
)

DEFERRED_AXES: Final[tuple[str, ...]] = tuple(
    axis
    for axis in SEARCH_AXES
    if not any(
        spec.search_axis == axis and spec.status is GeneratorStatus.KERNEL_IMPLEMENTED
        for spec in GENERATOR_REGISTRY
    )
)


class AssetGeneratorPort(Protocol):
    """External implementation boundary. Not implemented in this repository.

    Every generator output is evaluated by the existing Product Realization
    Gates. This extension adds search capability, never a second set of
    evaluation criteria.
    """

    def generate(self, request_ref: str) -> tuple[str, ...]: ...
