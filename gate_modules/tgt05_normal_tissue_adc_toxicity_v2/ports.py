"""Injected read-only source, coverage and evidence ports for MOD-TGT05 v2."""

from __future__ import annotations

from typing import Protocol, Sequence

from src.objects.decision_model import EvidencePackage

from .contracts import CoverageAudit, ModuleInput, NormalizedObservation, SourceRecord


class ObservationProviderPort(Protocol):
    def fetch_observations(self, request: ModuleInput) -> Sequence[NormalizedObservation]: ...
    def coverage_audit(self, request: ModuleInput) -> CoverageAudit: ...


class SourceResolverPort(Protocol):
    def resolve(self, source_id: str) -> SourceRecord | None: ...


class EvidenceLibraryPort(Protocol):
    def resolve(self, observation_id: str) -> EvidencePackage | None: ...


class EvidenceIdAllocatorPort(Protocol):
    def next_evidence_id(self) -> str: ...
