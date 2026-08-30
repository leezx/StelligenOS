"""Injected ports for MOD-TGT08.

``module.py`` may call ONLY these. It never opens a network connection, spawns a
subprocess, touches the filesystem, derives an id from existing files, or runs
an LLM / embedding commercial-judgement model. Live ClinicalTrials / FDA /
company retrieval, live patent retrieval, Lens / PATENTSCOPE / Google Patents
adapters, entity resolution, the source registry and the reusable Evidence
Library are shared infrastructure (CURRENT_SYSTEM v5 section 6.5) handed in
through these Protocols. Tests supply deterministic fakes.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from src.objects.decision_model import EvidencePackage

from .contracts import (
    CanonicalSourceRecord,
    CompetitiveLandscapeCompletion,
    NormalizedOpportunityRecord,
    PatentLandscapeCompletion,
)


@runtime_checkable
class Tgt08OpportunityProviderPort(Protocol):
    """Supplies already-normalized, primary/official-source-resolved TGT-08
    landscape observations plus the two typed completion contracts.

    Every record carries an ``evidence_axis`` (COMPETITIVE / PATENT /
    UNMET_NEED), an ``observation_kind`` and FACTS only -- it never sets an axis
    ceiling, a direction, or an opportunity implication (SUPPORTS_OPPORTUNITY /
    OPPOSES_OPPORTUNITY / CONTEXTUAL). Trial / regulatory / patent normalisation
    and source-authority keying are the provider's job; the module does the
    deterministic authority mapping and the Gate-relative interpretation.
    """

    def fetch_records(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Sequence[NormalizedOpportunityRecord]:
        ...

    def competitive_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> CompetitiveLandscapeCompletion:
        ...

    def patent_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> PatentLandscapeCompletion:
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
    incompatible with the current observation on any classification / absence
    driving field is a HARD identity integrity failure."""

    def resolve(self, observation_id: str) -> EvidencePackage | None:
        ...
