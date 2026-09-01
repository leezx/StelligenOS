"""Injected ports for MOD-TGT07.

``module.py`` may call ONLY these. It never opens a network connection, spawns a
subprocess, touches the filesystem, derives an id from existing files, or runs an
LLM / embedding model. Live serum / plasma soluble-antigen quantitation,
sheddase-substrate annotation, secreted-isoform, clinical-PK / PD and
target-mediated-disposition-analysis retrieval, entity resolution, the source
registry and the reusable Evidence Library are shared infrastructure
(CURRENT_SYSTEM v5 section 6.5) handed in through these Protocols. Tests supply
deterministic fakes. This package declares its OWN ports -- it does not import
MOD-TGT01 / MOD-TGT02 / MOD-TGT03 / MOD-TGT04 / MOD-TGT05 / MOD-TGT06 / MOD-TGT08
ports.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from src.objects.decision_model import EvidencePackage

from .completion import SolubleAntigenEvidenceCompletion
from .contracts import CanonicalSourceRecord, NormalizedSolubleAntigenObservation


@runtime_checkable
class Tgt07SolubleAntigenEvidenceProviderPort(Protocol):
    """Supplies already-normalized, primary/repository-source-resolved TGT-07
    soluble-antigen observations plus the one typed completion contract.

    Every observation carries an ``observation_kind`` and NORMALIZED UPSTREAM
    FACTS only -- it never sets an Evidence-Ladder rung, a Direction, a
    sink-liability implication (SUPPORTS_SINK_LIABILITY / OPPOSES_SINK_LIABILITY /
    CONTEXTUAL) or a fatal trigger, and it never emits DIRECT / INDIRECT_STRONG /
    WEAK / POSITIVE / NEGATIVE / POTENTIAL_FATAL_PATTERN. External retrieval /
    extraction / normalization -- including the upstream
    ``circulating_soluble_target_status`` / ``cohort_class`` /
    ``sink_materiality_outcome`` / ``analysis_validation_status`` /
    ``tmdd_input_adequacy_status`` / ``same_target_therapeutic_match_status`` /
    ``soluble_antigen_attribution_status`` / ``exposure_scenario_class`` typed
    predicates -- are the provider's job; the module does the deterministic rung
    mapping and the Gate-relative interpretation. There is NO normalizer inside
    this package. A ``SHEDDASE_SUBSTRATE_STATUS`` / ``SECRETED_ISOFORM`` kind
    ITSELF means upstream already confirmed a documented / validated fact -- the
    provider must never pass off a predicted / putative record as one of these
    kinds. The provider may state a source / workflow status fact
    (``SolubleAntigenUnresolvedItem.kind``) but never the final critical-unknown
    resolution.
    """

    def fetch_observations(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Sequence[NormalizedSolubleAntigenObservation]:
        ...

    def soluble_antigen_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> SolubleAntigenEvidenceCompletion:
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
    record. Returns ``None`` for an unregistered id. The module uses the resolved
    metadata (not the provider's raw fields) and rejects an observation whose
    provider metadata disagrees with the canonical record."""

    def resolve(self, source_id: str) -> CanonicalSourceRecord | None:
        ...


@runtime_checkable
class ExistingEvidenceLibraryPort(Protocol):
    """Read-only lookup into the PR C reusable Evidence Library. Given an
    ``observation_id``, returns the EXACT canonical ``EvidencePackage`` that
    already represents this observation, or ``None``. The module reuses that
    package unchanged -- no allocator call, no new body. A returned package
    incompatible with the current observation on any classification-driving field
    -- including ``circulating_soluble_target_status`` and
    ``sink_materiality_outcome`` -- is a HARD identity integrity failure. Exact
    string equality only: ``"A"`` and ``"A "`` are NOT the same factual
    representation (E16 tightening 6)."""

    def resolve(self, observation_id: str) -> EvidencePackage | None:
        ...
