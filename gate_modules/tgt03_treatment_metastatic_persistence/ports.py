"""Injected ports for MOD-TGT03.

``module.py`` may call ONLY these. It never opens a network connection, spawns a
subprocess, touches the filesystem, derives an id from existing files, or runs an
LLM / embedding model. Live GEO / HPA / CPTAC / single-cell / spatial / TMA /
paired-biopsy / resistance-model retrieval, entity resolution, the source
registry and the reusable Evidence Library are shared infrastructure
(CURRENT_SYSTEM v5 section 6.5) handed in through these Protocols. Tests supply
deterministic fakes. This package declares its OWN ports -- it does not import
MOD-TGT01 / MOD-TGT02 / MOD-TGT05 / MOD-TGT08 ports.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from src.objects.decision_model import EvidencePackage

from .completion import ClinicalPersistenceCompletion
from .contracts import CanonicalSourceRecord, NormalizedPersistenceObservation


@runtime_checkable
class Tgt03PersistenceProviderPort(Protocol):
    """Supplies already-normalized, primary/repository-source-resolved TGT-03
    clinical-persistence observations plus the one typed completion contract.

    Every observation carries an ``observation_kind`` and NORMALIZED UPSTREAM
    FACTS only -- it never sets an Evidence-Ladder rung, a Direction, or a
    persistence implication (SUPPORTS_PERSISTENCE / OPPOSES_PERSISTENCE /
    CONTEXTUAL). External retrieval / extraction / normalization -- including the
    upstream ``persistence_pattern`` / ``residual_target_presence_status`` /
    ``protein_measurement_validation_status`` / ``context_adequacy_status`` /
    ``reproducibility_status`` qualifications -- are the provider's job; the
    module does the deterministic rung mapping and the Gate-relative
    interpretation. There is NO normalizer inside this package. The provider may
    state a source / workflow status fact
    (``PersistenceUnresolvedItem.kind``) but never the final critical-unknown
    resolution.
    """

    def fetch_observations(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Sequence[NormalizedPersistenceObservation]:
        ...

    def persistence_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> ClinicalPersistenceCompletion:
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
