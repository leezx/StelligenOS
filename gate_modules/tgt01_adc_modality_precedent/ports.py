"""Injected ports for MOD-TGT01.

The module orchestration in ``module.py`` may call *only* these. It never opens
a network connection, spawns a subprocess, touches the filesystem, or derives an
id from existing files. Shared retrieval / entity-resolution / source-registry /
persistence infrastructure lives outside the repository (v5 section 6.5) and is
handed in through these Protocols. Tests supply deterministic fakes.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from .contracts import NormalizedPrecedentRecord, SweepCompletionRecord


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
class SourceRegistryPort(Protocol):
    """Resolves whether a ``provenance.source_id`` is a registered primary
    source. An unresolved id cannot establish a ladder rung."""

    def is_registered_primary_source(self, source_id: str) -> bool:
        ...
