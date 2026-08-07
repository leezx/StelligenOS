"""Opportunity territory map schema (Pool 00 / Stage 1).

A territory is a clinical water: a disease stage, molecular subtype, treatment
line, prior therapy and metastatic site, together with what currently fails
there, who is already in it, and what data the sponsor can reach. It is a map,
**not a candidate pool**. No target is named here and none is generated here.

This module defines the shape only. Territory instances — including every
disease-specific one — live in an external workspace, so the repository holds
no CRC content.

The routing decision is neither restated nor mirrored here. A territory records
only `search_space_admission_ref`, the provenance of its routing;
`SearchSpaceAdmission@0.1.0` holds the route and remains the sole authority.

There is deliberately no `territory_status` field. This module never
dereferences the admission, so it could not verify that a local copy of the
route still matched the admission it claims to come from — and a copy that
cannot be checked but can be filtered on is a second source of truth waiting to
drift. Downstream work must consume a territory together with its admission, not
a local mirror of the route.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

TERRITORY_SINGLE_REFERENCE_FIELDS: Final[tuple[str, ...]] = (
    "disease_ref",
    "clinical_population_ref",
    "molecular_subtype_ref",
    "treatment_line_ref",
    "current_soc_ref",
    "clinical_failure_mode_ref",
    "patient_size_band_ref",
    "position_occupancy_ref",
    "sponsor_evidence_advantage_ref",
    "window_closure_risk_ref",
    "search_space_admission_ref",
)

TERRITORY_REFERENCE_LIST_FIELDS: Final[tuple[str, ...]] = (
    "prior_therapy_refs",
    "metastatic_site_refs",
    "current_competitor_refs",
    "leading_asset_refs",
    "expected_readout_refs",
    "known_target_biology_refs",
    "available_patient_data_refs",
    "available_model_refs",
    "source_refs",
)

# A territory with no competitors, no expected readouts or no known target
# biology is a real and interesting state, so those lists may be empty. Only
# provenance is always required.
TERRITORY_NON_EMPTY_LIST_FIELDS: Final[tuple[str, ...]] = ("source_refs",)


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


EXTERNAL_SCHEME: Final[str] = "external:"


def _require_external_ref(value: str, field_name: str) -> None:
    _require_text(value, field_name)
    if not value.startswith(EXTERNAL_SCHEME):
        raise ValueError(f"{field_name} must use the external: scheme")
    if not value[len(EXTERNAL_SCHEME) :].strip():
        raise ValueError(f"{field_name} must not be a bare external: scheme")


@dataclass(frozen=True)
class OpportunityTerritory:
    """One row of the opportunity territory map."""

    territory_id: str
    disease_ref: str
    clinical_population_ref: str
    molecular_subtype_ref: str
    treatment_line_ref: str
    prior_therapy_refs: tuple[str, ...]
    metastatic_site_refs: tuple[str, ...]
    current_soc_ref: str
    clinical_failure_mode_ref: str
    patient_size_band_ref: str
    current_competitor_refs: tuple[str, ...]
    leading_asset_refs: tuple[str, ...]
    expected_readout_refs: tuple[str, ...]
    position_occupancy_ref: str
    known_target_biology_refs: tuple[str, ...]
    available_patient_data_refs: tuple[str, ...]
    available_model_refs: tuple[str, ...]
    sponsor_evidence_advantage_ref: str
    window_closure_risk_ref: str
    search_space_admission_ref: str
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.territory_id, "territory_id")
        for field_name in TERRITORY_SINGLE_REFERENCE_FIELDS:
            _require_external_ref(getattr(self, field_name), field_name)
        for field_name in TERRITORY_REFERENCE_LIST_FIELDS:
            values = getattr(self, field_name)
            if not isinstance(values, tuple):
                raise ValueError(f"{field_name} must be a tuple")
            if field_name in TERRITORY_NON_EMPTY_LIST_FIELDS and not values:
                raise ValueError(f"{field_name} must not be empty")
            for index, value in enumerate(values):
                _require_external_ref(value, f"{field_name}[{index}]")


@dataclass(frozen=True)
class OpportunityTerritoryMap:
    """The territory map as a whole.

    Duplicate territory ids are rejected here rather than downstream. A
    duplicate key silently collapsing two clinical waters into one is the class
    of defect that the SRCADM-01 audit had to go looking for after the fact.
    """

    map_id: str
    disease_scope_ref: str
    sponsor_profile_ref: str
    territories: tuple[OpportunityTerritory, ...]
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.map_id, "map_id")
        for field_name in ("disease_scope_ref", "sponsor_profile_ref"):
            _require_external_ref(getattr(self, field_name), field_name)
        if not isinstance(self.territories, tuple):
            raise ValueError("territories must be a tuple")
        if any(
            not isinstance(territory, OpportunityTerritory)
            for territory in self.territories
        ):
            raise ValueError("territories must contain OpportunityTerritory values")
        territory_ids = [territory.territory_id for territory in self.territories]
        duplicates = sorted(
            {
                territory_id
                for territory_id in territory_ids
                if territory_ids.count(territory_id) > 1
            }
        )
        if duplicates:
            raise ValueError(f"duplicate territory ids: {', '.join(duplicates)}")
        if not isinstance(self.source_refs, tuple) or not self.source_refs:
            raise ValueError("source_refs must be a non-empty tuple")
        for index, value in enumerate(self.source_refs):
            _require_external_ref(value, f"source_refs[{index}]")
