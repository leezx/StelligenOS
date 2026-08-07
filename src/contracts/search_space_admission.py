"""Early sponsor-relative search-space routing contract.

This module validates externally adjudicated routes in memory. It deliberately
does not calculate a score, evaluate scientific evidence, execute a Gate, or
persist an admission record.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class SearchSpaceRoute(StrEnum):
    ACTIVE_SEARCH = "ACTIVE_SEARCH"
    WATCHLIST = "WATCHLIST"
    PARTNER_ONLY = "PARTNER_ONLY"
    OUT_OF_MANDATE = "OUT_OF_MANDATE"


class CriterionStatus(StrEnum):
    SATISFIED = "SATISFIED"
    UNKNOWN = "UNKNOWN"
    UNSATISFIED = "UNSATISFIED"


SEARCH_SPACE_CRITERIA: Final[tuple[str, ...]] = (
    "clinical_value_exists",
    "competitive_position_not_locked",
    "asymmetric_evidence_advantage",
    "key_uncertainty_addressable",
    "differentiation_visible_preclinical",
    "defensible_ip_path",
    "plausible_buyer_partner_map",
    "time_window_compatible",
)


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_external_ref(value: str, field_name: str) -> None:
    _require_text(value, field_name)
    if not value.startswith("external:"):
        raise ValueError(f"{field_name} must use the external: scheme")


@dataclass(frozen=True)
class SearchSpaceCriterionResult:
    """One externally supported admission criterion observation."""

    criterion_id: str
    status: CriterionStatus
    evidence_ref: str

    def __post_init__(self) -> None:
        if self.criterion_id not in SEARCH_SPACE_CRITERIA:
            raise ValueError(f"Unsupported search-space criterion: {self.criterion_id}")
        if not isinstance(self.status, CriterionStatus):
            raise ValueError("status must be a CriterionStatus")
        _require_external_ref(self.evidence_ref, "evidence_ref")


@dataclass(frozen=True)
class SearchSpaceAdmission:
    """External route declaration before formal evidence extraction."""

    admission_id: str
    opportunity_ref: str
    sponsor_profile_ref: str
    program_thesis_ref: str
    criterion_results: tuple[SearchSpaceCriterionResult, ...]
    route: SearchSpaceRoute
    route_policy_ref: str
    rationale_ref: str
    source_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.admission_id, "admission_id")
        for field_name in (
            "opportunity_ref",
            "sponsor_profile_ref",
            "program_thesis_ref",
            "route_policy_ref",
            "rationale_ref",
        ):
            _require_external_ref(getattr(self, field_name), field_name)
        if not isinstance(self.route, SearchSpaceRoute):
            raise ValueError("route must be a SearchSpaceRoute")
        if not isinstance(self.criterion_results, tuple):
            raise ValueError("criterion_results must be a tuple")
        if len(self.criterion_results) != len(SEARCH_SPACE_CRITERIA):
            raise ValueError("exactly eight criterion results are required")
        criterion_ids = tuple(result.criterion_id for result in self.criterion_results)
        if set(criterion_ids) != set(SEARCH_SPACE_CRITERIA):
            raise ValueError("criterion_results must cover each criterion exactly once")
        if any(not isinstance(result, SearchSpaceCriterionResult) for result in self.criterion_results):
            raise ValueError("criterion_results must contain SearchSpaceCriterionResult values")
        if not isinstance(self.source_refs, tuple):
            raise ValueError("source_refs must be a tuple")
        for index, source_ref in enumerate(self.source_refs):
            _require_external_ref(source_ref, f"source_refs[{index}]")
