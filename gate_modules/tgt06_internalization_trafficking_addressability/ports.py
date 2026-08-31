"""Injected ports for MOD-TGT06.

``module.py`` may call ONLY these. It never opens a network connection, spawns a
subprocess, touches the filesystem, derives an id from existing files, or runs an
LLM / embedding model. Live live-cell-imaging / pH-sensitive-dye /
surface-decay-flow / lysosomal-co-localization / recycling-vs-degradation /
same-target-ADC retrieval, entity resolution, the source registry and the
reusable Evidence Library are shared infrastructure (CURRENT_SYSTEM v5 section
6.5) handed in through these Protocols. Tests supply deterministic fakes. This
package declares its OWN ports -- it does not import MOD-TGT01 / MOD-TGT02 /
MOD-TGT03 / MOD-TGT04 / MOD-TGT05 / MOD-TGT08 ports.
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

from src.objects.decision_model import EvidencePackage

from .completion import InternalizationEvidenceCompletion
from .contracts import CanonicalSourceRecord, NormalizedInternalizationObservation


@runtime_checkable
class Tgt06InternalizationEvidenceProviderPort(Protocol):
    """Supplies already-normalized, primary/repository-source-resolved TGT-06
    internalization / trafficking observations plus the one typed completion
    contract.

    Every observation carries an ``observation_kind`` and NORMALIZED UPSTREAM
    FACTS only -- it never sets an Evidence-Ladder rung, a Direction, an
    addressability implication (SUPPORTS_ADDRESSABILITY / OPPOSES_ADDRESSABILITY /
    CONTEXTUAL) or a fatal trigger, and it never emits DIRECT / INDIRECT_STRONG /
    WEAK / POSITIVE / NEGATIVE / POTENTIAL_FATAL_PATTERN. External retrieval /
    extraction / normalization -- including the upstream
    ``assay_validation_status`` / ``surface_context_class`` /
    ``context_adequacy_status`` / ``internalization_outcome`` /
    ``reproducibility_status`` qualifications and the
    ``declared_multi_configuration_analysis`` / configuration-identity state -- are
    the provider's job; the module does the deterministic rung mapping and the
    Gate-relative interpretation. There is NO normalizer inside this package. A
    ``SAME_TARGET_ADC_DELIVERY_PRECEDENT`` observation kind ITSELF means upstream
    already confirmed a genuine functional success -- the Module never
    semantic-parses company prose for success. The provider may state a source /
    workflow status fact (``InternalizationUnresolvedItem.kind``) but never the
    final critical-unknown resolution.
    """

    def fetch_observations(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> Sequence[NormalizedInternalizationObservation]:
        ...

    def internalization_completion(
        self, *, candidate_id: str, target_identity: str, run_id: str
    ) -> InternalizationEvidenceCompletion:
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
    -- including ``internalization_outcome`` and the
    antibody / epitope / affinity / conjugation factual identity fields -- is a
    HARD identity integrity failure."""

    def resolve(self, observation_id: str) -> EvidencePackage | None:
        ...
