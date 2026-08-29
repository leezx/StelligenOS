"""Injected ports for MOD-TGT01.

The module orchestration in ``module.py`` may call *only* these. It never opens
a network connection, spawns a subprocess, touches the filesystem, or derives an
id from existing files. Shared retrieval / entity-resolution / source-registry /
evidence-library infrastructure lives outside the repository (v5 section 6.5)
and is handed in through these Protocols. Tests supply deterministic fakes.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from .contracts import (
    CanonicalSourceRecord,
    NormalizedPrecedentRecord,
    SweepCompletionRecord,
)


@runtime_checkable
class Tgt01PrecedentProviderPort(Protocol):
    """Supplies already-normalized, primary-source-resolved precedent records
    for one target, plus the two stop-rule completion flags.

    An ADCdb-class inventory is a discovery / entity-resolution / index layer
    *behind* this port: by the time a record reaches the module it must already
    be resolved to its underlying primary disclosure. An unresolved
    database-only lead is not returned as a rung-establishing record (its
    ``primary_source_resolved`` is ``False`` and the module rejects it).
    """

    def fetch_precedents(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Sequence[NormalizedPrecedentRecord]:
        ...

    def sweep_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> SweepCompletionRecord:
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
    resolved metadata (not the provider's raw fields) and rejects a record
    whose provider metadata disagrees with the canonical record."""

    def resolve(self, source_id: str) -> CanonicalSourceRecord | None:
        ...


@runtime_checkable
class ExistingEvidenceLibraryPort(Protocol):
    """Read-only lookup into the PR C reusable Evidence Library. Given an
    ``observation_id``, returns the ``EP-nnnnnnnn`` id of the canonical
    EvidencePackage that already represents this observation, or ``None`` if it
    has never been recorded. The module reuses an existing id; it never copies
    or re-creates a canonical package."""

    def resolve(self, observation_id: str) -> str | None:
        ...
