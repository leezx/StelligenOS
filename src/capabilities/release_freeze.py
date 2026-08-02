"""Phase 9 architecture freeze and release contract.

This module freezes software architecture metadata only. It does not modify
the Gate Registry, publish data, execute a pilot, or approve Gate Extensions.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .gates import GATE_IDS
from .opportunity_generation import require_external_reference


class ReleaseStatus(str, Enum):
    READY = "READY"
    DO_NOT_PROCEED = "DO_NOT_PROCEED"


def _require_external_refs(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        try:
            require_external_reference(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must contain external references") from exc


@dataclass(frozen=True)
class ArchitectureFreezeRequest:
    """External references describing the frozen v1.0 architecture."""

    request_id: str
    module_id: str
    release_version: str
    gate_registry_version: str
    gate_ids_digest_ref: str
    tpc_profile_refs: tuple[str, ...]
    dependency_graph_ref: str
    phase_manifest_refs: tuple[str, ...]
    archived_prompt_refs: tuple[str, ...]
    gate_extension_proposal_refs: tuple[str, ...]
    unresolved_issue_refs: tuple[str, ...]
    gate_count: int = len(GATE_IDS)
    contract_version: str = "0.1.0"

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "gate_ids_digest_ref",
            "dependency_graph_ref",
        ):
            require_external_reference(getattr(self, name))
        for name in (
            "tpc_profile_refs",
            "phase_manifest_refs",
            "archived_prompt_refs",
            "gate_extension_proposal_refs",
            "unresolved_issue_refs",
        ):
            _require_external_refs(getattr(self, name), name)
        if self.module_id != "gen_indication_endpoint_target":
            raise ValueError("release contract is scoped to gen_indication_endpoint_target")
        if self.release_version != "1.0.0":
            raise ValueError("Phase 9 release version must be 1.0.0")
        if self.gate_count != len(GATE_IDS):
            raise ValueError("release must preserve the frozen 45-Gate topology")
        if not self.tpc_profile_refs:
            raise ValueError("tpc_profile_refs must be external")
        if not self.phase_manifest_refs:
            raise ValueError("phase_manifest_refs must cover the phase manifests")
        if self.gate_extension_proposal_refs:
            raise ValueError("unapproved Gate Extension proposals block release")


@dataclass(frozen=True)
class ArchitectureFreezeResult:
    """External release decision; no local package or registry mutation."""

    request_id: str
    status: ReleaseStatus
    release_manifest_ref: str
    immutable_contract_refs: tuple[str, ...]
    future_extension_scope_ref: str
    run_ref: str

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "release_manifest_ref",
            "future_extension_scope_ref",
            "run_ref",
        ):
            require_external_reference(getattr(self, name))
        _require_external_refs(self.immutable_contract_refs, "immutable_contract_refs")


class ArchitectureFreezePort(Protocol):
    def freeze(self, request: ArchitectureFreezeRequest) -> ArchitectureFreezeResult:
        """Freeze external architecture metadata without local side effects."""

        ...
