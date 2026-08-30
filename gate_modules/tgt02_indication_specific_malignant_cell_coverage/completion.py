"""The run-level CRC cohort coverage-completeness authority for MOD-TGT02.

Runtime Migration PR E8. ``CrcCohortCoverageCompletion`` is a module-local
frozen dataclass -- a run record, NOT a seventh core object, NOT an
EvidencePackage, Assessment or Decision. The provider states search facts; this
module derives whether the mandatory public CRC coverage landscape is complete
and audited, and HARD-checks three invariants (ChatGPT AI审核方案 E8):

1. completeness consistency -- ``public_crc_coverage_search_complete`` must equal
   ``all`` of the four declared mandatory component searches. A provider that
   claims the umbrella flag while a component is still false is a completion
   integrity contradiction and rejects the whole run (never a soft UNKNOWN).
2. audit presence -- an ``attempted`` completion must be certified by EXACTLY
   ONE ``SEARCH_COMPLETION_AUDIT`` observation whose ``observation_id`` equals
   ``audit_observation_id`` and whose structured snapshot matches this typed
   completion field-for-field. No audit, two audits, or any snapshot drift is a
   HARD run-level integrity failure. The typed completion is what grants the
   Module the authority to grade a Direction at the population level, so a
   completion that cannot be audited is worth nothing.
3. qualifying cohort-set parity -- ``qualifying_protein_cohort_ids`` /
   ``qualifying_indirect_cohort_ids`` must equal (as sets) the cohort identities
   of the observations the Module actually classified as qualifying DIRECT /
   qualifying INDIRECT_STRONG. A completion that "qualifies" a cohort the
   evidence does not, or omits one it does, is a HARD integrity failure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")

#: A declared unresolved public-search item. ``kind`` drives the deterministic
#: critical-unknown resolution (E8-7): a known-but-unfetched public dataset or an
#: incomplete public cohort search is PUBLIC_RESOLVABLE; an existing source whose
#: access / annotation currently prevents resolution is CURRENTLY_UNRESOLVABLE.
COVERAGE_UNRESOLVED_KIND_VALUES: tuple[str, ...] = (
    "KNOWN_PUBLIC_NOT_YET_RESOLVED",
    "ACCESS_OR_ANNOTATION_BLOCKED",
)
_UNRESOLVED_KIND_TO_RESOLUTION: dict[str, str] = {
    "KNOWN_PUBLIC_NOT_YET_RESOLVED": "PUBLIC_RESOLVABLE",
    "ACCESS_OR_ANNOTATION_BLOCKED": "CURRENTLY_UNRESOLVABLE",
}


def _text(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{name} must be a non-empty string")


def _bool(value: object, name: str) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a bool")


def _str_tuple(value: object, name: str) -> None:
    if not isinstance(value, tuple) or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f"{name} must be a tuple of non-empty strings")


@dataclass(frozen=True)
class CoverageUnresolvedItem:
    """One declared unresolved public-search item. Internal type of
    ``CrcCohortCoverageCompletion.unresolved_items`` only -- not a core object
    and it does not change the E7 conceptual shape."""

    description: str
    kind: str

    def __post_init__(self) -> None:
        _text(self.description, "description")
        if self.kind not in COVERAGE_UNRESOLVED_KIND_VALUES:
            raise ValueError(
                f"kind must be one of {COVERAGE_UNRESOLVED_KIND_VALUES}, got {self.kind!r}"
            )

    @property
    def resolution(self) -> str:
        return _UNRESOLVED_KIND_TO_RESOLUTION[self.kind]

    @property
    def snapshot_key(self) -> str:
        """The stable string an audit EP snapshot mirrors."""
        return f"{self.kind}::{self.description}"


@dataclass(frozen=True)
class CrcCohortCoverageCompletion:
    """Module-local run record for the mandatory public CRC coverage landscape
    (E7-5 / E8-5). NOT a seventh core object. The four component searches are the
    frozen E7 item-09 ``declared_mandatory_search_components``; the umbrella
    ``public_crc_coverage_search_complete`` is their conjunction and a provider
    contradiction is a HARD integrity failure, never a soft UNKNOWN."""

    attempted: bool
    landscape_as_of: str
    search_scope: str
    sources_searched: tuple[str, ...]
    public_crc_coverage_search_complete: bool
    protein_cohort_search_complete: bool
    malignant_compartment_sc_spatial_search_complete: bool
    tma_concordance_search_complete: bool
    matched_normal_tumor_search_complete: bool
    unresolved_items: tuple[CoverageUnresolvedItem, ...]
    qualifying_protein_cohort_ids: tuple[str, ...]
    qualifying_indirect_cohort_ids: tuple[str, ...]
    audit_observation_id: str

    def __post_init__(self) -> None:
        _bool(self.attempted, "attempted")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _text(self.search_scope, "search_scope", allow_empty=not self.attempted)
        _str_tuple(self.sources_searched, "sources_searched")
        for name in (
            "public_crc_coverage_search_complete",
            "protein_cohort_search_complete",
            "malignant_compartment_sc_spatial_search_complete",
            "tma_concordance_search_complete",
            "matched_normal_tumor_search_complete",
        ):
            _bool(getattr(self, name), name)
        if not isinstance(self.unresolved_items, tuple) or not all(
            isinstance(x, CoverageUnresolvedItem) for x in self.unresolved_items
        ):
            raise ValueError("unresolved_items must be a tuple of CoverageUnresolvedItem")
        _str_tuple(self.qualifying_protein_cohort_ids, "qualifying_protein_cohort_ids")
        _str_tuple(self.qualifying_indirect_cohort_ids, "qualifying_indirect_cohort_ids")
        # An attempted CRC coverage search -- complete or not -- MUST be certified
        # by exactly one SEARCH_COMPLETION_AUDIT observation (E8-5 invariant 2).
        # An incomplete audit records where the search got to; it does not grant
        # grading authority (that still needs ``landscape_complete``).
        _text(self.audit_observation_id, "audit_observation_id", allow_empty=not self.attempted)
        if self.attempted:
            if not _OBS_ID.match(self.audit_observation_id):
                raise ValueError("an attempted CRC coverage landscape names its audit_observation_id")

        if not self.attempted:
            for name in (
                "public_crc_coverage_search_complete",
                "protein_cohort_search_complete",
                "malignant_compartment_sc_spatial_search_complete",
                "tma_concordance_search_complete",
                "matched_normal_tumor_search_complete",
            ):
                if getattr(self, name):
                    raise ValueError(f"an unattempted coverage landscape cannot be {name}")
            if (
                self.sources_searched
                or self.qualifying_protein_cohort_ids
                or self.qualifying_indirect_cohort_ids
            ):
                raise ValueError(
                    "an unattempted coverage landscape has no searched sources / qualifying ids"
                )
        if self.attempted and not self.sources_searched:
            raise ValueError("an attempted CRC coverage landscape lists the sources searched")

    # --- E8-5 invariant 1: completeness consistency ----------------------------
    @property
    def _component_searches(self) -> tuple[bool, ...]:
        return (
            self.protein_cohort_search_complete,
            self.malignant_compartment_sc_spatial_search_complete,
            self.tma_concordance_search_complete,
            self.matched_normal_tumor_search_complete,
        )

    @property
    def landscape_complete(self) -> bool:
        """The audited state that unlocks a graded Direction (E7 item 16). Only
        true when the umbrella flag is set AND every mandatory component is
        complete -- a contradiction between them is caught by
        :func:`completeness_contradiction` and rejects the run."""

        return self.attempted and self.public_crc_coverage_search_complete and all(
            self._component_searches
        )

    @property
    def resolution_of_unresolved(self) -> str:
        """The single deterministic critical-unknown resolution implied by the
        declared unresolved items: CURRENTLY_UNRESOLVABLE if any item is
        access / annotation blocked, else PUBLIC_RESOLVABLE."""

        if any(i.kind == "ACCESS_OR_ANNOTATION_BLOCKED" for i in self.unresolved_items):
            return "CURRENTLY_UNRESOLVABLE"
        return "PUBLIC_RESOLVABLE"


def completeness_contradiction(completion: CrcCohortCoverageCompletion) -> str:
    """E8-5 invariant 1. Return "" when the completion is self-consistent, else a
    HARD-integrity reason. ``public_crc_coverage_search_complete`` MUST equal the
    conjunction of the four declared mandatory component searches."""

    umbrella = completion.public_crc_coverage_search_complete
    components_all = all(completion._component_searches)
    if umbrella != components_all:
        return (
            "CrcCohortCoverageCompletion integrity contradiction: "
            f"public_crc_coverage_search_complete={umbrella} but "
            f"all(protein / sc-spatial / tma / matched-normal component searches)"
            f"={components_all}"
        )
    return ""


def audit_snapshot_mismatch(observation, completion: CrcCohortCoverageCompletion) -> str:
    """E8-5 invariant 2 (the E6 completion-audit snapshot-parity gene, hardened).
    ``observation`` is a ``SEARCH_COMPLETION_AUDIT`` normalized coverage
    observation. Return "" when its structured snapshot matches ``completion``
    field-for-field (or it is not the certificate for this completion), else a
    drift reason. A non-empty return is a HARD run-level integrity failure."""

    if not completion.attempted:
        return ""
    if completion.audit_observation_id != observation.observation_id:
        return ""
    pairs = (
        (observation.audit_search_scope, completion.search_scope, "audit_search_scope"),
        (
            set(observation.audit_sources_searched),
            set(completion.sources_searched),
            "audit_sources_searched",
        ),
        (
            observation.audit_landscape_as_of,
            completion.landscape_as_of,
            "audit_landscape_as_of",
        ),
        (
            observation.audit_public_crc_coverage_search_complete,
            completion.public_crc_coverage_search_complete,
            "audit_public_crc_coverage_search_complete",
        ),
        (
            observation.audit_protein_cohort_search_complete,
            completion.protein_cohort_search_complete,
            "audit_protein_cohort_search_complete",
        ),
        (
            observation.audit_malignant_compartment_sc_spatial_search_complete,
            completion.malignant_compartment_sc_spatial_search_complete,
            "audit_malignant_compartment_sc_spatial_search_complete",
        ),
        (
            observation.audit_tma_concordance_search_complete,
            completion.tma_concordance_search_complete,
            "audit_tma_concordance_search_complete",
        ),
        (
            observation.audit_matched_normal_tumor_search_complete,
            completion.matched_normal_tumor_search_complete,
            "audit_matched_normal_tumor_search_complete",
        ),
        (
            set(observation.audit_unresolved_item_keys),
            {i.snapshot_key for i in completion.unresolved_items},
            "audit_unresolved_item_keys",
        ),
        (
            set(observation.audit_qualifying_protein_cohort_ids),
            set(completion.qualifying_protein_cohort_ids),
            "audit_qualifying_protein_cohort_ids",
        ),
        (
            set(observation.audit_qualifying_indirect_cohort_ids),
            set(completion.qualifying_indirect_cohort_ids),
            "audit_qualifying_indirect_cohort_ids",
        ),
    )
    for got, want, name in pairs:
        if got != want:
            return (
                f"SEARCH_COMPLETION_AUDIT snapshot field {name} = {got!r} disagrees "
                f"with the typed completion state {want!r}"
            )
    return ""


def qualifying_set_mismatch(
    completion: CrcCohortCoverageCompletion,
    *,
    direct_cohort_ids: set[str],
    indirect_cohort_ids: set[str],
) -> str:
    """E8-5 invariant 3. Return "" when the completion's qualifying cohort id
    sets equal the cohort identities the Module actually classified as
    qualifying DIRECT / qualifying INDIRECT_STRONG, else a drift reason (HARD)."""

    if set(completion.qualifying_protein_cohort_ids) != direct_cohort_ids:
        return (
            "CrcCohortCoverageCompletion.qualifying_protein_cohort_ids "
            f"{sorted(completion.qualifying_protein_cohort_ids)} != the cohort "
            f"identities of the qualifying DIRECT protein-cohort observations "
            f"{sorted(direct_cohort_ids)}"
        )
    if set(completion.qualifying_indirect_cohort_ids) != indirect_cohort_ids:
        return (
            "CrcCohortCoverageCompletion.qualifying_indirect_cohort_ids "
            f"{sorted(completion.qualifying_indirect_cohort_ids)} != the cohort "
            f"identities of the qualifying INDIRECT_STRONG observations "
            f"{sorted(indirect_cohort_ids)}"
        )
    return ""


def audit_presence_failure(
    completion: CrcCohortCoverageCompletion, audit_observation_ids: list[str]
) -> str:
    """E8-5 invariant 2 (presence half). ``audit_observation_ids`` is every
    admissible ``SEARCH_COMPLETION_AUDIT`` observation id at the NORMALIZED
    identity layer (before any (source_id, claim) dedup -- a second audit must
    not be hidden by dedup). An ``attempted`` completion -- complete OR not --
    needs EXACTLY ONE, and it must be ``audit_observation_id``. An unattempted
    completion carries none. Return "" when satisfied, else a HARD reason.
    Snapshot drift is checked separately by :func:`audit_snapshot_mismatch`."""

    if not completion.attempted:
        if audit_observation_ids:
            return (
                "an unattempted CRC coverage landscape carries "
                f"{len(audit_observation_ids)} SEARCH_COMPLETION_AUDIT observation(s)"
            )
        return ""
    matching = [oid for oid in audit_observation_ids if oid == completion.audit_observation_id]
    if not matching:
        return (
            "the attempted CRC coverage landscape has no SEARCH_COMPLETION_AUDIT "
            f"observation certifying it (expected {completion.audit_observation_id!r})"
        )
    if len(audit_observation_ids) != 1 or len(matching) != 1:
        return (
            "the attempted CRC coverage landscape must be certified by EXACTLY ONE "
            f"SEARCH_COMPLETION_AUDIT observation; got {sorted(audit_observation_ids)}"
        )
    return ""
