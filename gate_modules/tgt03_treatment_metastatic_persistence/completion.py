"""The run-level clinical-persistence-search completeness authority for MOD-TGT03.

Runtime Migration PR E10. ``ClinicalPersistenceCompletion`` is a module-local
frozen dataclass -- a run record, NOT a seventh core object, NOT an
EvidencePackage, Assessment or Decision. The provider states search facts; this
module derives whether the mandatory public clinical-persistence landscape is
complete and audited, and HARD-checks three invariants (frozen E9 contract +
ChatGPT AI审核方案 E10-5):

1. completeness consistency -- ``public_persistence_search_complete`` must equal
   ``all`` of the four declared mandatory component searches (refractory /
   prior-treated, metastatic lesion, paired pre / post, resistance model). A
   provider that claims the umbrella flag while a component is still false is a
   completion integrity contradiction and rejects the whole run (never a soft
   UNKNOWN).
2. audit presence -- an ``attempted`` completion must be certified by EXACTLY
   ONE ``SEARCH_COMPLETION_AUDIT`` observation whose ``observation_id`` equals
   ``audit_observation_id`` and whose structured snapshot matches this typed
   completion field-for-field. The snapshot field names ARE the typed
   completion's field names (same namespace). No audit, two audits, or any
   snapshot drift is a HARD run-level integrity failure.
3. qualifying context-set parity -- ``qualifying_direct_persistence_context_ids``
   / ``qualifying_indirect_persistence_context_ids`` must equal (as sets) the
   LOCAL persistence-context identities of the observations the Module actually
   classified as qualifying DIRECT / qualifying INDIRECT_STRONG. These are a
   LOCAL evidence-context namespace, never the canonical Instantiation
   ``context_id`` (CTX-CRC-REFRACTORY-MCRC).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")

#: A declared unresolved public-search item. ``kind`` drives the deterministic
#: critical-unknown resolution (E10-5): a known-but-unfetched public dataset or an
#: incomplete public search is PUBLIC_RESOLVABLE; an existing source whose access
#: / annotation currently prevents resolution is CURRENTLY_UNRESOLVABLE.
PERSISTENCE_UNRESOLVED_KIND_VALUES: tuple[str, ...] = (
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
class PersistenceUnresolvedItem:
    """One declared unresolved public-search item. Internal type of
    ``ClinicalPersistenceCompletion.unresolved_items`` only -- not a core object
    and it does not change the E9 conceptual shape."""

    description: str
    kind: str

    def __post_init__(self) -> None:
        _text(self.description, "description")
        if self.kind not in PERSISTENCE_UNRESOLVED_KIND_VALUES:
            raise ValueError(
                f"kind must be one of {PERSISTENCE_UNRESOLVED_KIND_VALUES}, got {self.kind!r}"
            )

    @property
    def resolution(self) -> str:
        return _UNRESOLVED_KIND_TO_RESOLUTION[self.kind]

    @property
    def snapshot_key(self) -> str:
        """The stable string an audit EP snapshot mirrors."""
        return f"{self.kind}::{self.description}"


@dataclass(frozen=True)
class ClinicalPersistenceCompletion:
    """Module-local run record for the mandatory public clinical-persistence
    landscape (E9 item 09 / E10-5). NOT a seventh core object. The four component
    searches are the frozen E9 item-09 ``declared_mandatory_search_components``;
    the umbrella ``public_persistence_search_complete`` is their conjunction and
    a provider contradiction is a HARD integrity failure, never a soft UNKNOWN.
    "mandatory" is search-space completeness, not evidence prerequisites -- a
    component searched / exhausted with zero qualifying records still counts
    complete."""

    attempted: bool
    landscape_as_of: str
    search_scope: str
    sources_searched: tuple[str, ...]
    public_persistence_search_complete: bool
    refractory_prior_treated_search_complete: bool
    metastatic_lesion_search_complete: bool
    paired_pre_post_search_complete: bool
    resistance_model_search_complete: bool
    unresolved_items: tuple[PersistenceUnresolvedItem, ...]
    qualifying_direct_persistence_context_ids: tuple[str, ...]
    qualifying_indirect_persistence_context_ids: tuple[str, ...]
    audit_observation_id: str

    def __post_init__(self) -> None:
        _bool(self.attempted, "attempted")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _text(self.search_scope, "search_scope", allow_empty=not self.attempted)
        _str_tuple(self.sources_searched, "sources_searched") if self.sources_searched else None
        for name in (
            "public_persistence_search_complete",
            "refractory_prior_treated_search_complete",
            "metastatic_lesion_search_complete",
            "paired_pre_post_search_complete",
            "resistance_model_search_complete",
        ):
            _bool(getattr(self, name), name)
        if not isinstance(self.unresolved_items, tuple) or not all(
            isinstance(x, PersistenceUnresolvedItem) for x in self.unresolved_items
        ):
            raise ValueError("unresolved_items must be a tuple of PersistenceUnresolvedItem")
        _str_tuple(
            self.qualifying_direct_persistence_context_ids,
            "qualifying_direct_persistence_context_ids",
        ) if self.qualifying_direct_persistence_context_ids else None
        _str_tuple(
            self.qualifying_indirect_persistence_context_ids,
            "qualifying_indirect_persistence_context_ids",
        ) if self.qualifying_indirect_persistence_context_ids else None
        # An attempted persistence search -- complete or not -- MUST be certified
        # by exactly one SEARCH_COMPLETION_AUDIT observation (E10-5 invariant 2).
        _text(self.audit_observation_id, "audit_observation_id", allow_empty=not self.attempted)
        if self.attempted:
            if not _OBS_ID.match(self.audit_observation_id):
                raise ValueError(
                    "an attempted clinical-persistence landscape names its audit_observation_id"
                )
            if not self.sources_searched:
                raise ValueError(
                    "an attempted clinical-persistence landscape lists the sources searched"
                )
        if not self.attempted:
            for name in (
                "public_persistence_search_complete",
                "refractory_prior_treated_search_complete",
                "metastatic_lesion_search_complete",
                "paired_pre_post_search_complete",
                "resistance_model_search_complete",
            ):
                if getattr(self, name):
                    raise ValueError(f"an unattempted persistence landscape cannot be {name}")
            if (
                self.sources_searched
                or self.qualifying_direct_persistence_context_ids
                or self.qualifying_indirect_persistence_context_ids
            ):
                raise ValueError(
                    "an unattempted persistence landscape has no searched sources / qualifying ids"
                )

    # --- E10-5 invariant 1: completeness consistency -----------------------
    @property
    def _component_searches(self) -> tuple[bool, ...]:
        return (
            self.refractory_prior_treated_search_complete,
            self.metastatic_lesion_search_complete,
            self.paired_pre_post_search_complete,
            self.resistance_model_search_complete,
        )

    @property
    def landscape_complete(self) -> bool:
        """The audited state that unlocks a graded Direction (E9 item 16). Only
        true when the umbrella flag is set AND every mandatory component is
        complete -- a contradiction between them is caught by
        :func:`completeness_contradiction` and rejects the run."""

        return (
            self.attempted
            and self.public_persistence_search_complete
            and all(self._component_searches)
        )

    @property
    def resolution_of_unresolved(self) -> str:
        """The single deterministic critical-unknown resolution implied by the
        declared unresolved items: CURRENTLY_UNRESOLVABLE if any item is
        access / annotation blocked, else PUBLIC_RESOLVABLE."""

        if any(i.kind == "ACCESS_OR_ANNOTATION_BLOCKED" for i in self.unresolved_items):
            return "CURRENTLY_UNRESOLVABLE"
        return "PUBLIC_RESOLVABLE"


def completeness_contradiction(completion: ClinicalPersistenceCompletion) -> str:
    """E10-5 invariant 1. Return "" when the completion is self-consistent, else a
    HARD-integrity reason. ``public_persistence_search_complete`` MUST equal the
    conjunction of the four declared mandatory component searches."""

    umbrella = completion.public_persistence_search_complete
    components_all = all(completion._component_searches)
    if umbrella != components_all:
        return (
            "ClinicalPersistenceCompletion integrity contradiction: "
            f"public_persistence_search_complete={umbrella} but "
            "all(refractory / metastatic-lesion / paired-pre-post / resistance-model "
            f"component searches)={components_all}"
        )
    return ""


def audit_snapshot_mismatch(observation, completion: ClinicalPersistenceCompletion) -> str:
    """E10-5 invariant 2 (the E6 / E8 completion-audit snapshot-parity gene).
    ``observation`` is a ``SEARCH_COMPLETION_AUDIT`` normalized persistence
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
            observation.audit_public_persistence_search_complete,
            completion.public_persistence_search_complete,
            "audit_public_persistence_search_complete",
        ),
        (
            observation.audit_refractory_prior_treated_search_complete,
            completion.refractory_prior_treated_search_complete,
            "audit_refractory_prior_treated_search_complete",
        ),
        (
            observation.audit_metastatic_lesion_search_complete,
            completion.metastatic_lesion_search_complete,
            "audit_metastatic_lesion_search_complete",
        ),
        (
            observation.audit_paired_pre_post_search_complete,
            completion.paired_pre_post_search_complete,
            "audit_paired_pre_post_search_complete",
        ),
        (
            observation.audit_resistance_model_search_complete,
            completion.resistance_model_search_complete,
            "audit_resistance_model_search_complete",
        ),
        (
            set(observation.audit_unresolved_item_keys),
            {i.snapshot_key for i in completion.unresolved_items},
            "audit_unresolved_item_keys",
        ),
        (
            set(observation.audit_qualifying_direct_persistence_context_ids),
            set(completion.qualifying_direct_persistence_context_ids),
            "audit_qualifying_direct_persistence_context_ids",
        ),
        (
            set(observation.audit_qualifying_indirect_persistence_context_ids),
            set(completion.qualifying_indirect_persistence_context_ids),
            "audit_qualifying_indirect_persistence_context_ids",
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
    completion: ClinicalPersistenceCompletion,
    *,
    direct_context_ids: set[str],
    indirect_context_ids: set[str],
) -> str:
    """E10-5 invariant 3. Return "" when the completion's qualifying
    persistence-context id sets equal the LOCAL persistence-context identities
    the Module actually classified as qualifying DIRECT / qualifying
    INDIRECT_STRONG, else a drift reason (HARD)."""

    if set(completion.qualifying_direct_persistence_context_ids) != direct_context_ids:
        return (
            "ClinicalPersistenceCompletion.qualifying_direct_persistence_context_ids "
            f"{sorted(completion.qualifying_direct_persistence_context_ids)} != the "
            "persistence-context identities of the qualifying DIRECT protein "
            f"observations {sorted(direct_context_ids)}"
        )
    if set(completion.qualifying_indirect_persistence_context_ids) != indirect_context_ids:
        return (
            "ClinicalPersistenceCompletion.qualifying_indirect_persistence_context_ids "
            f"{sorted(completion.qualifying_indirect_persistence_context_ids)} != the "
            "persistence-context identities of the qualifying INDIRECT_STRONG "
            f"observations {sorted(indirect_context_ids)}"
        )
    return ""


def audit_presence_failure(
    completion: ClinicalPersistenceCompletion, audit_observation_ids: list[str]
) -> str:
    """E10-5 invariant 2 (presence half). ``audit_observation_ids`` is every
    admissible ``SEARCH_COMPLETION_AUDIT`` observation id at the NORMALIZED
    identity layer (before any dedup -- a second audit must not be hidden). An
    ``attempted`` completion -- complete OR not -- needs EXACTLY ONE, and it must
    be ``audit_observation_id``. An unattempted completion carries none. Return
    "" when satisfied, else a HARD reason. Snapshot drift is checked separately
    by :func:`audit_snapshot_mismatch`."""

    if not completion.attempted:
        if audit_observation_ids:
            return (
                "an unattempted clinical-persistence landscape carries "
                f"{len(audit_observation_ids)} SEARCH_COMPLETION_AUDIT observation(s)"
            )
        return ""
    matching = [oid for oid in audit_observation_ids if oid == completion.audit_observation_id]
    if not matching:
        return (
            "the attempted clinical-persistence landscape has no SEARCH_COMPLETION_AUDIT "
            f"observation certifying it (expected {completion.audit_observation_id!r})"
        )
    if len(audit_observation_ids) != 1 or len(matching) != 1:
        return (
            "the attempted clinical-persistence landscape must be certified by EXACTLY ONE "
            f"SEARCH_COMPLETION_AUDIT observation; got {sorted(audit_observation_ids)}"
        )
    return ""
