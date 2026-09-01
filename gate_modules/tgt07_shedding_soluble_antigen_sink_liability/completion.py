"""The run-level soluble-antigen-evidence-search completeness authority for MOD-TGT07.

Runtime Migration PR E16. ``SolubleAntigenEvidenceCompletion`` is a module-local
frozen dataclass -- a run record, NOT a seventh core object, NOT an
EvidencePackage, Assessment or Decision. The provider states search facts; this
module derives whether the mandatory public soluble-antigen-evidence landscape is
complete and audited, and HARD-checks three invariants (frozen PR E15 contract +
ChatGPT AI审核方案 E16):

1. completeness consistency -- ``public_soluble_antigen_search_complete`` must
   equal ``all`` of the FOUR declared mandatory component searches
   (soluble-antigen quantitation, sheddase processing, secreted isoform, same-target
   PK / PD or target-mediated-disposition analysis). AND (E16 tightening 4) the
   quantitation axis is a strict conjunction of TWO typed subspace audit facts:
   ``soluble_antigen_quantitation_search_complete == (
   crc_patient_quantitation_subspace_search_complete AND
   healthy_donor_quantitation_subspace_search_complete)``. A provider that claims a
   completion axis while a component (or a quantitation subspace) is still false
   rejects the whole run -- never a soft UNKNOWN. The components are FLAT booleans,
   not sub-objects.
2. audit presence + exact audit identity (E6 / E8 / E10 / E14 gene) -- an
   ``attempted`` completion must be certified by EXACTLY ONE
   ``SEARCH_COMPLETION_AUDIT`` observation whose ``observation_id`` equals
   ``audit_observation_id`` and whose structured snapshot matches this typed
   completion field-for-field, INCLUDING the two quantitation subspace facts. The
   snapshot field names ARE the typed completion's field names. No audit, two
   audits, an id mismatch, or any snapshot drift is a HARD run-level integrity
   failure. ``attempted == False`` is a frozen strict-empty state.
3. qualifying-context-set parity -- ``qualifying_direct_evidence_context_ids`` must
   equal (as a set) the UNION of the single-string ``sink_exposure_context_id`` of
   every observation the Module actually classified as qualifying DIRECT-rung
   (material-sink DIRECT, no-material-sink DIRECT, or DIRECT-quality MIXED),
   evaluated ONLY over a completed landscape. There is deliberately NO
   ``qualifying_indirect_evidence_context_ids`` set.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ISO_DATE_PREFIX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")
_OBS_ID = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")

#: A declared unresolved public-search item. ``kind`` drives the deterministic
#: critical-unknown resolution: a known-but-unfetched public dataset or an
#: incomplete public search is PUBLIC_RESOLVABLE; an existing source whose access
#: / annotation currently prevents resolution is CURRENTLY_UNRESOLVABLE.
SOLUBLE_ANTIGEN_UNRESOLVED_KIND_VALUES: tuple[str, ...] = (
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
class SolubleAntigenUnresolvedItem:
    """One declared unresolved public-search item. Internal type of
    ``SolubleAntigenEvidenceCompletion.unresolved_items`` only -- not a core
    object and it does not change the E15 conceptual shape."""

    description: str
    kind: str

    def __post_init__(self) -> None:
        _text(self.description, "description")
        if self.kind not in SOLUBLE_ANTIGEN_UNRESOLVED_KIND_VALUES:
            raise ValueError(
                f"kind must be one of {SOLUBLE_ANTIGEN_UNRESOLVED_KIND_VALUES}, "
                f"got {self.kind!r}"
            )

    @property
    def resolution(self) -> str:
        return _UNRESOLVED_KIND_TO_RESOLUTION[self.kind]

    @property
    def snapshot_key(self) -> str:
        """The stable string an audit EP snapshot mirrors."""
        return f"{self.kind}::{self.description}"


@dataclass(frozen=True)
class SolubleAntigenEvidenceCompletion:
    """Module-local run record for the mandatory public soluble-antigen-evidence
    landscape (E15 item 09 / E16 tightening 4). NOT a seventh core object. The four
    component searches are the frozen E15 item-09 ``declared_mandatory_search_components``;
    the umbrella ``public_soluble_antigen_search_complete`` is their conjunction and
    a provider contradiction is a HARD integrity failure, never a soft UNKNOWN.
    "mandatory" is search-space completeness, not evidence prerequisites and not
    grading axes -- a component searched / exhausted with zero qualifying records
    still counts complete. The quantitation axis is true ONLY when BOTH the
    CRC-patient serum / plasma subspace AND the healthy-donor serum / plasma
    subspace have been searched / exhausted (frozen PR D evidence_required is
    "in CRC patients AND in healthy donors")."""

    attempted: bool
    landscape_as_of: str
    search_scope: str
    sources_searched: tuple[str, ...]
    public_soluble_antigen_search_complete: bool
    soluble_antigen_quantitation_search_complete: bool
    crc_patient_quantitation_subspace_search_complete: bool
    healthy_donor_quantitation_subspace_search_complete: bool
    sheddase_processing_search_complete: bool
    secreted_isoform_search_complete: bool
    same_target_pk_pd_or_tmdd_search_complete: bool
    unresolved_items: tuple[SolubleAntigenUnresolvedItem, ...]
    qualifying_direct_evidence_context_ids: tuple[str, ...]
    audit_observation_id: str

    def __post_init__(self) -> None:
        _bool(self.attempted, "attempted")
        _text(self.landscape_as_of, "landscape_as_of")
        if not _ISO_DATE_PREFIX.match(self.landscape_as_of):
            raise ValueError("landscape_as_of must start with an ISO date")
        _text(self.search_scope, "search_scope", allow_empty=not self.attempted)
        if self.sources_searched:
            _str_tuple(self.sources_searched, "sources_searched")
        for name in (
            "public_soluble_antigen_search_complete",
            "soluble_antigen_quantitation_search_complete",
            "crc_patient_quantitation_subspace_search_complete",
            "healthy_donor_quantitation_subspace_search_complete",
            "sheddase_processing_search_complete",
            "secreted_isoform_search_complete",
            "same_target_pk_pd_or_tmdd_search_complete",
        ):
            _bool(getattr(self, name), name)
        if not isinstance(self.unresolved_items, tuple) or not all(
            isinstance(x, SolubleAntigenUnresolvedItem) for x in self.unresolved_items
        ):
            raise ValueError(
                "unresolved_items must be a tuple of SolubleAntigenUnresolvedItem"
            )
        if self.qualifying_direct_evidence_context_ids:
            _str_tuple(
                self.qualifying_direct_evidence_context_ids,
                "qualifying_direct_evidence_context_ids",
            )
        _text(
            self.audit_observation_id,
            "audit_observation_id",
            allow_empty=not self.attempted,
        )
        if self.attempted:
            if not _OBS_ID.match(self.audit_observation_id):
                raise ValueError(
                    "an attempted soluble-antigen landscape names its audit_observation_id"
                )
            if not self.sources_searched:
                raise ValueError(
                    "an attempted soluble-antigen landscape lists the sources searched"
                )
        # --- attempted == False frozen strict-empty state (E14-5 gene) --------
        if not self.attempted:
            for name in (
                "public_soluble_antigen_search_complete",
                "soluble_antigen_quantitation_search_complete",
                "crc_patient_quantitation_subspace_search_complete",
                "healthy_donor_quantitation_subspace_search_complete",
                "sheddase_processing_search_complete",
                "secreted_isoform_search_complete",
                "same_target_pk_pd_or_tmdd_search_complete",
            ):
                if getattr(self, name):
                    raise ValueError(
                        f"an unattempted soluble-antigen landscape cannot be {name}"
                    )
            if (
                self.sources_searched
                or self.qualifying_direct_evidence_context_ids
                or self.search_scope.strip()
                or self.audit_observation_id.strip()
            ):
                raise ValueError(
                    "an unattempted soluble-antigen landscape has no search_scope / "
                    "searched sources / qualifying ids / audit_observation_id"
                )

    # --- invariant 1: completeness consistency --------------------------
    @property
    def _component_searches(self) -> tuple[bool, ...]:
        return (
            self.soluble_antigen_quantitation_search_complete,
            self.sheddase_processing_search_complete,
            self.secreted_isoform_search_complete,
            self.same_target_pk_pd_or_tmdd_search_complete,
        )

    @property
    def _quantitation_axis_matches_subspaces(self) -> bool:
        return self.soluble_antigen_quantitation_search_complete == (
            self.crc_patient_quantitation_subspace_search_complete
            and self.healthy_donor_quantitation_subspace_search_complete
        )

    @property
    def landscape_complete(self) -> bool:
        """The audited state that unlocks a graded Direction (E15 item 16). Only
        true when the umbrella flag is set AND every mandatory component is
        complete AND the quantitation axis equals the AND of its two subspace
        facts -- a contradiction is caught by :func:`completeness_contradiction`
        and rejects the run."""

        return (
            self.attempted
            and self.public_soluble_antigen_search_complete
            and all(self._component_searches)
            and self._quantitation_axis_matches_subspaces
        )

    @property
    def resolution_of_unresolved(self) -> str:
        """The single deterministic critical-unknown resolution implied by the
        declared unresolved items: CURRENTLY_UNRESOLVABLE if any item is
        access / annotation blocked, else PUBLIC_RESOLVABLE."""

        if any(
            i.kind == "ACCESS_OR_ANNOTATION_BLOCKED" for i in self.unresolved_items
        ):
            return "CURRENTLY_UNRESOLVABLE"
        return "PUBLIC_RESOLVABLE"


def completeness_contradiction(completion: SolubleAntigenEvidenceCompletion) -> str:
    """Invariant 1. Return "" when the completion is self-consistent, else a
    HARD-integrity reason. ``public_soluble_antigen_search_complete`` MUST equal
    the conjunction of the four declared mandatory component searches, AND the
    quantitation axis MUST equal the AND of its two typed subspace facts
    (E16 tightening 4)."""

    umbrella = completion.public_soluble_antigen_search_complete
    components_all = all(completion._component_searches)
    if umbrella != components_all:
        return (
            "SolubleAntigenEvidenceCompletion integrity contradiction: "
            f"public_soluble_antigen_search_complete={umbrella} but "
            "all(soluble-antigen-quantitation / sheddase-processing / "
            "secreted-isoform / same-target-PK-PD-or-TMDD component searches)"
            f"={components_all}"
        )
    if not completion._quantitation_axis_matches_subspaces:
        return (
            "SolubleAntigenEvidenceCompletion integrity contradiction: "
            "soluble_antigen_quantitation_search_complete="
            f"{completion.soluble_antigen_quantitation_search_complete} but "
            "(crc_patient_quantitation_subspace_search_complete="
            f"{completion.crc_patient_quantitation_subspace_search_complete} AND "
            "healthy_donor_quantitation_subspace_search_complete="
            f"{completion.healthy_donor_quantitation_subspace_search_complete})"
        )
    return ""


def audit_snapshot_mismatch(
    observation, completion: SolubleAntigenEvidenceCompletion
) -> str:
    """Invariant 2 (the E6 / E8 / E10 / E14 completion-audit snapshot-parity gene).
    ``observation`` is a ``SEARCH_COMPLETION_AUDIT`` normalized soluble-antigen
    observation. Return "" when its structured snapshot matches ``completion``
    field-for-field (or it is not the certificate for this completion), else a
    drift reason. A non-empty return is a HARD run-level integrity failure. The
    two quantitation subspace facts are part of the parity (E16 tightening 4)."""

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
            observation.audit_public_soluble_antigen_search_complete,
            completion.public_soluble_antigen_search_complete,
            "audit_public_soluble_antigen_search_complete",
        ),
        (
            observation.audit_soluble_antigen_quantitation_search_complete,
            completion.soluble_antigen_quantitation_search_complete,
            "audit_soluble_antigen_quantitation_search_complete",
        ),
        (
            observation.audit_crc_patient_quantitation_subspace_search_complete,
            completion.crc_patient_quantitation_subspace_search_complete,
            "audit_crc_patient_quantitation_subspace_search_complete",
        ),
        (
            observation.audit_healthy_donor_quantitation_subspace_search_complete,
            completion.healthy_donor_quantitation_subspace_search_complete,
            "audit_healthy_donor_quantitation_subspace_search_complete",
        ),
        (
            observation.audit_sheddase_processing_search_complete,
            completion.sheddase_processing_search_complete,
            "audit_sheddase_processing_search_complete",
        ),
        (
            observation.audit_secreted_isoform_search_complete,
            completion.secreted_isoform_search_complete,
            "audit_secreted_isoform_search_complete",
        ),
        (
            observation.audit_same_target_pk_pd_or_tmdd_search_complete,
            completion.same_target_pk_pd_or_tmdd_search_complete,
            "audit_same_target_pk_pd_or_tmdd_search_complete",
        ),
        (
            set(observation.audit_unresolved_item_keys),
            {i.snapshot_key for i in completion.unresolved_items},
            "audit_unresolved_item_keys",
        ),
        (
            set(observation.audit_qualifying_direct_evidence_context_ids),
            set(completion.qualifying_direct_evidence_context_ids),
            "audit_qualifying_direct_evidence_context_ids",
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
    completion: SolubleAntigenEvidenceCompletion,
    *,
    direct_context_ids: set[str],
) -> str:
    """Invariant 3. Return "" when the completion's qualifying-context id set
    equals the UNION of the single-string ``sink_exposure_context_id`` over every
    observation the Module classified as qualifying DIRECT-rung (material-sink
    DIRECT, no-material-sink DIRECT, or DIRECT-quality MIXED), evaluated ONLY over
    a completed landscape, else a drift reason (HARD). There is deliberately NO
    qualifying_indirect_evidence_context_ids set."""

    if set(completion.qualifying_direct_evidence_context_ids) != direct_context_ids:
        return (
            "SolubleAntigenEvidenceCompletion.qualifying_direct_evidence_context_ids "
            f"{sorted(completion.qualifying_direct_evidence_context_ids)} != the union "
            "of the sink_exposure_context_id of the qualifying DIRECT-rung "
            f"observations {sorted(direct_context_ids)}"
        )
    return ""


def audit_presence_failure(
    completion: SolubleAntigenEvidenceCompletion, audit_observation_ids: list[str]
) -> str:
    """Invariant 2 (presence half). ``audit_observation_ids`` is every admissible
    ``SEARCH_COMPLETION_AUDIT`` observation id at the NORMALIZED identity layer
    (before any dedup -- a second audit must not be hidden). An ``attempted``
    completion -- complete OR not -- needs EXACTLY ONE, and it must be
    ``audit_observation_id``. An unattempted completion carries none. Return ""
    when satisfied, else a HARD reason. Snapshot drift is checked separately by
    :func:`audit_snapshot_mismatch`."""

    if not completion.attempted:
        if audit_observation_ids:
            return (
                "an unattempted soluble-antigen landscape carries "
                f"{len(audit_observation_ids)} SEARCH_COMPLETION_AUDIT observation(s)"
            )
        return ""
    matching = [
        oid for oid in audit_observation_ids if oid == completion.audit_observation_id
    ]
    if not matching:
        return (
            "the attempted soluble-antigen landscape has no SEARCH_COMPLETION_AUDIT "
            f"observation certifying it (expected {completion.audit_observation_id!r})"
        )
    if len(audit_observation_ids) != 1 or len(matching) != 1:
        return (
            "the attempted soluble-antigen landscape must be certified by EXACTLY ONE "
            f"SEARCH_COMPLETION_AUDIT observation; got {sorted(audit_observation_ids)}"
        )
    return ""
