"""Adapters from the legacy ``core_objects@1.1`` types to the Blueprint v1.3
decision-layer objects.

Legacy support is retained: ``src/objects/core.py`` and
``src/contracts/core_objects.yaml`` are unchanged, and ``CoreObject`` keeps
working exactly as before. This module only adds a migration path.

Only three legacy types map one-to-one to a ``Candidate``
(``TargetHypothesis`` -> L04, ``BinderCandidate`` -> L06,
``DevelopmentCandidate`` -> L13). The other five are composites or wrappers
whose decomposition is not settled; adapting them raises ``NotImplementedError``
that points at the crosswalk. The full mapping is in ``LEGACY_CROSSWALK`` and,
verbatim in prose, in
``docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md``
section 4.5 and ``docs/architecture/contract.zh-CN.md`` section 3.4.3.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping

from src.objects.core import CORE_OBJECT_TYPES, CoreObject
from src.objects.decision_model import CANDIDATE_LEVELS, Candidate


@dataclass(frozen=True)
class LegacyCrosswalkEntry:
    """One legacy object type's migration disposition."""

    legacy_type: str
    disposition: str  # candidate | composite | wrapper | non_candidate
    one_to_one: bool
    target_summary: str
    candidate_type: str | None = None
    level: str | None = None


_DISPOSITIONS: Final[frozenset[str]] = frozenset(
    {"candidate", "composite", "wrapper", "non_candidate"}
)


_LEGACY_CROSSWALK: Final[dict[str, LegacyCrosswalkEntry]] = {
    "Opportunity": LegacyCrosswalkEntry(
        legacy_type="Opportunity",
        disposition="wrapper",
        one_to_one=False,
        target_summary=(
            "Instantiation intent + Context seed + candidate-generation request; "
            "not any Candidate Level."
        ),
    ),
    "ClinicalHypothesis": LegacyCrosswalkEntry(
        legacy_type="ClinicalHypothesis",
        disposition="composite",
        one_to_one=False,
        target_summary=(
            "clinical/patient/endpoint dimensions -> Context; target identity -> "
            "Candidate/reference; biomarker hypothesis -> Biomarker candidate/"
            "reference; product hypothesis -> downstream candidate/context "
            "reference; lock state -> Context maturity (the ClinicalLockState "
            "ladder in src/lifecycle/clinical_lock.py, CURRENT_SYSTEM v5 section 4.6)."
        ),
    ),
    "TargetHypothesis": LegacyCrosswalkEntry(
        legacy_type="TargetHypothesis",
        disposition="candidate",
        one_to_one=True,
        target_summary="Candidate, candidate_type = ADC Target, level = L04.",
        candidate_type="ADC_TARGET",
        level="L04",
    ),
    "BinderCandidate": LegacyCrosswalkEntry(
        legacy_type="BinderCandidate",
        disposition="candidate",
        one_to_one=True,
        target_summary="Candidate, candidate_type = Antibody / Binder, level = L06.",
        candidate_type="ANTIBODY_BINDER",
        level="L06",
    ),
    "ADCConstruct": LegacyCrosswalkEntry(
        legacy_type="ADCConstruct",
        disposition="composite",
        one_to_one=False,
        target_summary=(
            "Composite spanning L09 ADC Design / L10 ADC Hit; needs a stage/type "
            "discriminator or distinct Candidate objects before it can be adapted."
        ),
    ),
    "LeadSeries": LegacyCrosswalkEntry(
        legacy_type="LeadSeries",
        disposition="composite",
        one_to_one=False,
        target_summary=(
            "Series/container around L11 ADC Lead candidates; exact decomposition "
            "pending migration."
        ),
    ),
    "DevelopmentCandidate": LegacyCrosswalkEntry(
        legacy_type="DevelopmentCandidate",
        disposition="candidate",
        one_to_one=True,
        target_summary="Candidate, candidate_type = Development Candidate, level = L13.",
        candidate_type="DEVELOPMENT_CANDIDATE",
        level="L13",
    ),
    "Asset": LegacyCrosswalkEntry(
        legacy_type="Asset",
        disposition="non_candidate",
        one_to_one=False,
        target_summary=(
            "Outward commercial/transaction representation of an L11-L13 candidate "
            "after a NOMINATE / COMMIT Decision; not a new Candidate Level."
        ),
    ),
}


def _check_crosswalk_covers_legacy_registry() -> None:
    if set(_LEGACY_CROSSWALK) != set(CORE_OBJECT_TYPES):
        raise RuntimeError(
            "LEGACY_CROSSWALK must cover exactly the legacy CORE_OBJECT_TYPES"
        )
    for entry in _LEGACY_CROSSWALK.values():
        if entry.disposition not in _DISPOSITIONS:
            raise RuntimeError(f"unknown disposition: {entry.disposition}")
        if entry.one_to_one != (entry.disposition == "candidate"):
            raise RuntimeError(
                f"{entry.legacy_type}: one_to_one must match a 'candidate' disposition"
            )
        if entry.one_to_one and (entry.candidate_type is None or entry.level is None):
            raise RuntimeError(
                f"{entry.legacy_type}: one-to-one entry needs candidate_type and level"
            )


_check_crosswalk_covers_legacy_registry()


#: Read-only view. ``LegacyCrosswalkEntry`` is already a frozen dataclass, so the
#: whole structure is immutable at runtime, not just to a type checker.
LEGACY_CROSSWALK: Final[Mapping[str, LegacyCrosswalkEntry]] = MappingProxyType(
    _LEGACY_CROSSWALK
)


ONE_TO_ONE_LEGACY_TYPES: Final[tuple[str, ...]] = tuple(
    name for name, entry in LEGACY_CROSSWALK.items() if entry.one_to_one
)


#: Candidate Types that ``core_objects@1.1`` lacks and the migration must add.
#: This is exactly the set of Candidate Levels NOT covered by a clean one-to-one
#: legacy mapping (L04 / L06 / L13); together with those three it is the full
#: L00-L14 ontology. ``tests/test_decision_model.py`` locks that completeness.
_ONE_TO_ONE_LEVELS: Final[frozenset[str]] = frozenset(
    entry.level for entry in _LEGACY_CROSSWALK.values() if entry.level is not None
)

MISSING_CANDIDATE_TYPES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "L00": "INDICATION",
        "L01": "PATIENT_TERRITORY",
        "L02": "ENDPOINT",
        "L03": "MODALITY",
        "L05": "ADC_EPITOPE",
        "L07": "LINKER",
        "L08": "PAYLOAD",
        "L09": "ADC_DESIGN",
        "L10": "ADC_HIT",
        "L11": "ADC_LEAD",
        "L12": "BIOMARKER",
        "L14": "CLINICAL_REGIMEN",
    }
)


def _check_missing_candidate_types_are_complete() -> None:
    covered = set(MISSING_CANDIDATE_TYPES) | set(_ONE_TO_ONE_LEVELS)
    if covered != set(CANDIDATE_LEVELS):
        raise RuntimeError(
            "MISSING_CANDIDATE_TYPES plus the one-to-one levels must be exactly "
            f"L00-L14; got {sorted(covered)}"
        )
    if set(MISSING_CANDIDATE_TYPES) & set(_ONE_TO_ONE_LEVELS):
        raise RuntimeError(
            "MISSING_CANDIDATE_TYPES must not overlap the one-to-one legacy levels"
        )


_check_missing_candidate_types_are_complete()


def adapt_core_object_to_candidate(
    core_object: CoreObject,
    *,
    candidate_id: str,
    canonical_name: str,
    created_at: str,
    provenance_ref: str,
    status: str = "ACTIVE",
    version: int = 1,
    parent_candidate_id: str = "",
) -> Candidate:
    """Map a legacy ``CoreObject`` to a ``Candidate``.

    Works only for the three legacy types that map one-to-one. The identity
    values that the legacy object does not carry (``candidate_id``,
    ``canonical_name``, ``created_at``, ``provenance_ref``) are supplied by the
    caller and validated by ``Candidate``. Composite and wrapper legacy types
    raise ``NotImplementedError`` naming their crosswalk target.
    """

    entry = LEGACY_CROSSWALK.get(core_object.object_type)
    if entry is None:
        raise ValueError(f"unknown legacy object type: {core_object.object_type}")
    if not entry.one_to_one:
        raise NotImplementedError(
            f"{core_object.object_type} does not map one-to-one to a Candidate. "
            f"Migration target: {entry.target_summary} "
            "Decompose it per contract.zh-CN.md section 3.4.3 in a later PR."
        )
    assert entry.candidate_type is not None and entry.level is not None
    return Candidate(
        candidate_id=candidate_id,
        candidate_type=entry.candidate_type,
        level=entry.level,
        canonical_name=canonical_name,
        status=status,
        version=version,
        created_at=created_at,
        provenance_ref=provenance_ref,
        parent_candidate_id=parent_candidate_id,
    )
