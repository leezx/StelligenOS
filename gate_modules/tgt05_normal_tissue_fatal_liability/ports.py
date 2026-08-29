"""Injected ports for MOD-TGT05.

``module.py`` may call ONLY these. It never opens a network connection, spawns a
subprocess, touches the filesystem, derives an id from existing files, or runs
an ontology / embedding / LLM similarity model. Shared retrieval /
entity-resolution / source-registry / evidence-library infrastructure lives
outside the repository (v5 section 6.5) and is handed in through these
Protocols. Tests supply deterministic fakes.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from src.objects.decision_model import EvidencePackage

from .contracts import (
    CanonicalSourceRecord,
    NormalizedLiabilityRecord,
    Tgt05SweepCompletionRecord,
)


@runtime_checkable
class Tgt05LiabilityProviderPort(Protocol):
    """Supplies already-normalized, primary-source-resolved TGT-05 observations
    plus the typed sweep / coverage completion contract.

    Every record carries an ``evidence_function`` (LIABILITY_RUNG_EVIDENCE /
    ATTRIBUTION_ADJUDICATION / COVERAGE_CONTEXT) and FACTS only -- it never sets
    a ladder rung or a direction. RNA / atlas normalisation, toxicity-phenotype
    keying and target-attribution stances are the provider's job; the module
    only does exact-key comparisons on them.
    """

    def fetch_liability_records(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Sequence[NormalizedLiabilityRecord]:
        ...

    def sweep_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Tgt05SweepCompletionRecord:
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
    resolved metadata (not the provider's raw fields) and rejects a record whose
    provider metadata disagrees with the canonical record."""

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
