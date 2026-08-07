"""External-only value inflection planning contract.

The contract describes the next evidence boundary that should increase an
opportunity's transfer value. It does not estimate cost, execute work, or
advance a lifecycle stage.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class TargetTransactionType(StrEnum):
    PARTNERSHIP = "PARTNERSHIP"
    OPTION_DEAL = "OPTION_DEAL"
    LICENSE = "LICENSE"
    CO_DEVELOPMENT = "CO_DEVELOPMENT"
    NEWCO = "NEWCO"
    DATA_PACKAGE_TRANSFER = "DATA_PACKAGE_TRANSFER"


class LifecycleStage(StrEnum):
    OPPORTUNITY = "OPPORTUNITY"
    TARGET_OPPORTUNITY = "TARGET_OPPORTUNITY"
    TARGET_ANTIBODY_HYPOTHESIS = "TARGET_ANTIBODY_HYPOTHESIS"
    CONJUGATE_PROTOTYPE = "CONJUGATE_PROTOTYPE"
    TRANSLATIONAL_POC = "TRANSLATIONAL_POC"
    PARTNERABLE_PACKAGE = "PARTNERABLE_PACKAGE"


TRANSACTION_TYPES: Final[tuple[str, ...]] = tuple(
    transaction_type.value for transaction_type in TargetTransactionType
)


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_external_ref(value: str, field_name: str) -> None:
    _require_text(value, field_name)
    if not value.startswith("external:"):
        raise ValueError(f"{field_name} must use the external: scheme")


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    if not isinstance(values, tuple) or not values:
        raise ValueError(f"{field_name} must be a non-empty tuple")
    for index, value in enumerate(values):
        _require_external_ref(value, f"{field_name}[{index}]")


@dataclass(frozen=True)
class ValueInflectionPlan:
    """Human-approved plan for buying the next value-transfer boundary."""

    plan_id: str
    program_thesis_ref: str
    program_commitment_review_ref: str
    current_stage: LifecycleStage
    target_inflection_stage: LifecycleStage
    target_transaction_type: TargetTransactionType
    critical_uncertainty_refs: tuple[str, ...]
    planned_evidence_package_refs: tuple[str, ...]
    minimum_success_criteria_refs: tuple[str, ...]
    stop_condition_refs: tuple[str, ...]
    estimated_cost_band_ref: str
    estimated_duration_band_ref: str
    required_capability_refs: tuple[str, ...]
    capability_source_refs: tuple[str, ...]
    expected_buyer_type_refs: tuple[str, ...]
    buyer_requirement_refs: tuple[str, ...]
    fallback_route_ref: str
    human_approval_ref: str
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.plan_id, "plan_id")
        for field_name in (
            "program_thesis_ref",
            "program_commitment_review_ref",
            "estimated_cost_band_ref",
            "estimated_duration_band_ref",
            "fallback_route_ref",
            "human_approval_ref",
        ):
            _require_external_ref(getattr(self, field_name), field_name)
        for field_name in (
            "critical_uncertainty_refs",
            "planned_evidence_package_refs",
            "minimum_success_criteria_refs",
            "stop_condition_refs",
            "required_capability_refs",
            "capability_source_refs",
            "expected_buyer_type_refs",
            "buyer_requirement_refs",
            "source_refs",
        ):
            _require_external_refs(getattr(self, field_name), field_name)
        if not isinstance(self.current_stage, LifecycleStage):
            raise ValueError("current_stage must be a LifecycleStage")
        if not isinstance(self.target_inflection_stage, LifecycleStage):
            raise ValueError("target_inflection_stage must be a LifecycleStage")
        if not isinstance(self.target_transaction_type, TargetTransactionType):
            raise ValueError(
                "target_transaction_type must be a TargetTransactionType"
            )
