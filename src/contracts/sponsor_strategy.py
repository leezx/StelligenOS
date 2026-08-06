"""Sponsor-relative strategy contract types.

These types validate contract-shaped requests in memory. They do not persist
profiles, program theses, decisions, data, or runtime results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


DEVELOPMENT_PATHS: Final[tuple[str, ...]] = (
    "full_asset_development",
    "partnerable_asset_option",
    "data_package_only",
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
        raise ValueError(f"{field_name} must be a tuple of references")
    for index, value in enumerate(values):
        _require_external_ref(value, f"{field_name}[{index}]")


@dataclass(frozen=True)
class DevelopmentSponsorProfile:
    """Sponsor context used for relative executability assessment."""

    sponsor_id: str
    company_stage: str
    therapeutic_focus: tuple[str, ...]
    disease_advantage: tuple[str, ...]
    modality_scope: tuple[str, ...]
    owned_capabilities: tuple[str, ...]
    partnered_capabilities: tuple[str, ...]
    unavailable_capabilities: tuple[str, ...]
    accessible_data: tuple[str, ...]
    accessible_patient_samples: tuple[str, ...]
    accessible_models: tuple[str, ...]
    capital_envelope: str
    time_horizon: str
    maximum_self_funded_stage: str
    preferred_transaction_stage: str
    acceptable_program_count: str
    risk_tolerance: str
    geographic_scope: tuple[str, ...]
    ip_strategy: str

    def __post_init__(self) -> None:
        _require_text(self.sponsor_id, "sponsor_id")
        for field_name in (
            "company_stage",
            "maximum_self_funded_stage",
            "preferred_transaction_stage",
            "risk_tolerance",
        ):
            _require_text(getattr(self, field_name), field_name)
        for field_name in (
            "therapeutic_focus",
            "disease_advantage",
            "modality_scope",
            "owned_capabilities",
            "partnered_capabilities",
            "unavailable_capabilities",
            "geographic_scope",
        ):
            values = getattr(self, field_name)
            if not isinstance(values, tuple) or not all(
                isinstance(value, str) and value.strip() for value in values
            ):
                raise ValueError(f"{field_name} must contain non-empty strings")
        for field_name in (
            "accessible_data",
            "accessible_patient_samples",
            "accessible_models",
        ):
            _require_external_refs(getattr(self, field_name), field_name)
        for field_name in (
            "capital_envelope",
            "time_horizon",
            "acceptable_program_count",
            "ip_strategy",
        ):
            _require_external_ref(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class ProgramThesis:
    """External program framing before sponsor-relative commitment."""

    thesis_id: str
    opportunity_ref: str
    clinical_hypothesis_ref: str
    intended_product_position_ref: str
    sponsor_profile_ref: str
    current_lifecycle_stage: str
    target_transfer_milestone_ref: str
    development_path: str
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.thesis_id, "thesis_id")
        for field_name in (
            "opportunity_ref",
            "clinical_hypothesis_ref",
            "intended_product_position_ref",
            "sponsor_profile_ref",
            "target_transfer_milestone_ref",
        ):
            _require_external_ref(getattr(self, field_name), field_name)
        _require_text(self.current_lifecycle_stage, "current_lifecycle_stage")
        if self.development_path not in DEVELOPMENT_PATHS:
            raise ValueError(
                f"development_path must be one of {DEVELOPMENT_PATHS}"
            )
        _require_external_refs(self.source_refs, "source_refs")
