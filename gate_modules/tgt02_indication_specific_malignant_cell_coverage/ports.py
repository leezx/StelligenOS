"""Injected ports for MOD-TGT02.

``module.py`` may call ONLY these. It never opens a network connection, spawns a
subprocess, touches the filesystem, derives an id from existing files, or runs
an LLM / embedding model. Live GEO / HPA / CPTAC / single-cell / spatial / TMA
retrieval, entity resolution, the source registry and the reusable Evidence
Library are shared infrastructure (CURRENT_SYSTEM v5 section 6.5) handed in
through these Protocols. Tests supply deterministic fakes. This package declares
its OWN ports -- it does not import MOD-TGT01 / MOD-TGT05 / MOD-TGT08 ports.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from src.objects.decision_model import EvidencePackage

from .completion import CrcCohortCoverageCompletion
from .contracts import CanonicalSourceRecord, NormalizedCoverageObservation


@runtime_checkable
class Tgt02CoverageProviderPort(Protocol):
    """Supplies already-normalized, primary/repository-source-resolved TGT-02
    malignant-cell coverage observations plus the one typed completion contract.

    Every observation carries an ``observation_kind``, a typed ``assay_method``
    and FACTS only -- it never sets an Evidence-Ladder rung, a Direction, or a
    coverage-support implication (SUPPORTS_COVERAGE / OPPOSES_COVERAGE /
    CONTEXTUAL). Repository / atlas / TMA normalisation, malignant-compartment
    resolution and the upstream ``expression_pattern`` qualification are the
    provider's job; the module does the deterministic rung mapping and the
    Gate-relative interpretation. The provider may state a source / workflow
    status fact (``CoverageUnresolvedItem.kind``) but never the final
    critical-unknown resolution.
    """

    def fetch_observations(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Sequence[NormalizedCoverageObservation]:
        ...

    def coverage_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> CrcCohortCoverageCompletion:
        ...


@runtime_checkable
class EvidenceIdAllocatorPort(Protocol):
    """Allocates canonical ``EP-nnnnnnnn`` ids from the upstream identity
    service. The module never scans the filesystem for ``max id + 1``."""

    def next_evidence_id(self) -> str:
        ...


@runtime_checkable
class SourceResolverPort(Protocol):
    """Resolves a ``provenance.source_id`` to its canonical PR C SourceIndex
    record. Returns ``None`` for an unregistered id. The module uses the
    resolved metadata (not the provider's raw fields) and rejects an observation
    whose provider metadata disagrees with the canonical record."""

    def resolve(self, source_id: str) -> CanonicalSourceRecord | None:
        ...


@runtime_checkable
class ExistingEvidenceLibraryPort(Protocol):
    """Read-only lookup into the PR C reusable Evidence Library. Given an
    ``observation_id``, returns the EXACT canonical ``EvidencePackage`` that
    already represents this observation, or ``None``. The module reuses that
    package unchanged -- no allocator call, no new body. A returned package
    incompatible with the current observation on any classification-driving
    field is a HARD identity integrity failure."""

    def resolve(self, observation_id: str) -> EvidencePackage | None:
        ...
