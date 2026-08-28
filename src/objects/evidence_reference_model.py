"""Blueprint v1.3 Matrix view + reusable-evidence reference contracts (runtime side).

Runtime Migration PR C. Frozen dataclasses that validate contract-shaped
instances in memory -- no data, no persistence, no engine. The shared
validators, deep-freeze and identity patterns are reused verbatim from
``src/objects/decision_model.py`` (PR A); the canonical-GateSet check is reused
from ``src/objects/gate_model.py`` (PR B), so the three contract layers cannot
diverge on how they validate.

* ``MatrixView`` / ``MatrixRow`` -- the Candidate x Gate Matrix for one
  Instantiation as a *derived, rebuildable projection*: rows are Candidates,
  columns are the member Gates of the canonical GateSet, cells are the frozen
  wide-view state strings, the trailing ``decision`` comes from ``DEC-*.json``.
  It has no id and is never a persisted object (Data Layout Spec section 4.2 /
  Appendix B).
* ``EvidenceIndexEntry`` / ``EvidenceLibraryIndex`` -- rows of the global
  ``30_EVIDENCE_LIBRARY/evidence_index.csv``. This mutable/derived index is the
  ONLY place a forward ``status`` / ``superseded_by`` lives; the canonical
  ``evidence.json`` (PR A ``EvidencePackage``) carries neither.
* ``SourceIndexEntry`` / ``SourceIndex`` -- rows of the global
  ``30_EVIDENCE_LIBRARY/source_index.csv``. One source, many EvidencePackages.
* ``GateEvidenceIndexEntry`` / ``GateEvidenceIndex`` -- rows of a per-gate
  ``TGT-NN/CURRENT/evidence_index.csv``: a reference, not a copy.

``check_evidence_library_against_sources`` / ``check_gate_index_against_library``
/ ``check_matrix_cells_are_backed`` walk the reference layer for referential
integrity (the provenance-walk invariant). They compute no direction, strength
or decision.

PR A (``decision_objects.yaml`` / ``decision_model.py`` / ``legacy_adapters.py``)
and PR B (``gate_contracts.yaml`` / ``gate_model.py`` / ``legacy_gate_map.py``)
are imported only, never modified.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields
from typing import Final, Mapping

from src.objects.decision_model import (
    CANDIDATE_LEVELS,
    EVIDENCE_ROLE_VALUES,
    SOURCE_TYPE_VALUES,
    _ASSESSMENT_ID,
    _CANDIDATE_ID,
    _EVIDENCE_ID,
    _GATESET_ID,
    _INSTANTIATION_ID,
    _ISO_DATE_PREFIX,
    _SOURCE_ID,
    _freeze_attr,
    _is_int,
    _require_choice,
    _require_external_ref,
    _require_pattern,
    _require_positive_int,
    _require_str,
    _require_str_tuple,
    _require_text,
)
from src.objects.gate_model import DECISION_VALUES, _require_canonical_gateset


# --- Controlled vocabularies (parity: src/contracts/evidence_reference.yaml
#     and, for the headers, src/contracts/data_layout/csv_headers.yaml) ---------

EVIDENCE_INDEX_STATUS_VALUES: Final[tuple[str, ...]] = (
    "ACTIVE",
    "SUPERSEDED",
    "RETRACTED",
)

#: The frozen wide-view Matrix cell states (Data Layout Spec section 4.1):
#: every graded <DIRECTION>/<STRENGTH>, plus the three single-value states.
#: ``NOT_EVALUATED`` is a wide-view state ("no HUMAN_APPROVED record"), distinct
#: from the assessment_snapshot literal used inside a Decision.
_MATRIX_GRADED_DIRECTIONS: Final[tuple[str, ...]] = (
    "POSITIVE",
    "NEGATIVE",
    "CONFLICTING",
    "INCONCLUSIVE",
)
_MATRIX_GRADED_STRENGTHS: Final[tuple[str, ...]] = (
    "DIRECT",
    "INDIRECT_STRONG",
    "WEAK",
)
MATRIX_CELL_STATES: Final[tuple[str, ...]] = tuple(
    f"{direction}/{strength}"
    for direction in _MATRIX_GRADED_DIRECTIONS
    for strength in _MATRIX_GRADED_STRENGTHS
) + ("UNKNOWN", "NOT_APPLICABLE", "NOT_EVALUATED")

#: Cell states that do NOT require an EvidencePackage backing them.
_UNBACKED_CELL_STATES: Final[frozenset[str]] = frozenset(
    {"UNKNOWN", "NOT_APPLICABLE", "NOT_EVALUATED"}
)

_MATRIX_CELL = re.compile(
    r"^((POSITIVE|NEGATIVE|CONFLICTING|INCONCLUSIVE)/(DIRECT|INDIRECT_STRONG|WEAK)"
    r"|UNKNOWN|NOT_APPLICABLE|NOT_EVALUATED)$"
)

#: Wide Matrix header = these + the member gate ids + the trailing column.
MATRIX_WIDE_FIXED_COLUMNS: Final[tuple[str, ...]] = ("candidate_id", "name")
MATRIX_WIDE_TRAILING_COLUMN: Final[str] = "decision"

#: Long (machine-friendly) Matrix header, verbatim from csv_headers.yaml.
MATRIX_LONG_COLUMNS: Final[tuple[str, ...]] = (
    "candidate_id",
    "gate_id",
    "direction",
    "strength",
    "assessment_id",
    "assessment_version",
    "evidence_count",
    "review_status",
    "last_updated_at",
)

#: DECISIONS view header, verbatim from csv_headers.yaml.
DECISIONS_VIEW_COLUMNS: Final[tuple[str, ...]] = (
    "decision_id",
    "candidate_id",
    "gateset_id",
    "gateset_version",
    "decision",
    "triggered_by_gates",
    "review_status",
    "decided_at",
)

_YEAR = re.compile(r"^[0-9]{4}$")


def _require_year(value, field_name: str) -> None:
    """A 4-digit year as int or string, or the empty string when unknown."""

    if _is_int(value):
        if 1800 <= value <= 2200:
            return
        raise ValueError(f"{field_name} out of range")
    if isinstance(value, str) and (value == "" or _YEAR.match(value)):
        return
    raise ValueError(f"{field_name} must be a 4-digit year (int or str) or ''")


# --- Matrix view (derived projection; not a persisted object) --------------

@dataclass(frozen=True)
class MatrixRow:
    """One Candidate's row: one cell per member Gate plus the decision column."""

    candidate_id: str
    name: str
    cells: Mapping[str, str]
    decision: str

    def __post_init__(self) -> None:
        _freeze_attr(self, "cells")
        _require_pattern(self.candidate_id, _CANDIDATE_ID, "candidate_id")
        _require_text(self.name, "name")
        if not isinstance(self.cells, Mapping) or not self.cells:
            raise ValueError("cells must be a non-empty mapping of gate_id -> state")
        for gate_id, state in self.cells.items():
            if not isinstance(gate_id, str) or not gate_id.strip():
                raise ValueError("cells keys must be non-empty gate ids")
            if not isinstance(state, str) or not _MATRIX_CELL.match(state):
                raise ValueError(
                    f"cells[{gate_id!r}] {state!r} is not a frozen Matrix cell state"
                )
        if self.decision != "NOT_EVALUATED" and self.decision not in DECISION_VALUES:
            raise ValueError(
                "decision must be a decision value or the literal 'NOT_EVALUATED'"
            )


@dataclass(frozen=True)
class MatrixView:
    """The Candidate x Gate Matrix for one Instantiation, as a rebuildable view.

    No id. Never hand-edited: it is rebuilt losslessly from every Candidate's
    ``ASSESSMENTS/<cand>/latest.json`` plus ``DECISIONS/DEC-*.json``.
    """

    instantiation_id: str
    gateset_id: str
    candidate_level: str
    member_gate_ids: tuple[str, ...]
    rows: tuple[MatrixRow, ...]

    def __post_init__(self) -> None:
        _freeze_attr(self, "member_gate_ids")
        _freeze_attr(self, "rows")

        _require_pattern(self.instantiation_id, _INSTANTIATION_ID, "instantiation_id")
        _require_pattern(self.gateset_id, _GATESET_ID, "gateset_id")
        _require_choice(self.candidate_level, CANDIDATE_LEVELS, "candidate_level")
        _require_canonical_gateset(
            self.candidate_level, self.gateset_id, "MatrixView"
        )

        _require_str_tuple(self.member_gate_ids, "member_gate_ids")
        if not self.member_gate_ids or not all(
            gid.strip() for gid in self.member_gate_ids
        ):
            raise ValueError("member_gate_ids must be a non-empty tuple of gate ids")
        if len(self.member_gate_ids) != len(set(self.member_gate_ids)):
            raise ValueError("member_gate_ids must be unique")

        if not isinstance(self.rows, tuple) or not all(
            isinstance(row, MatrixRow) for row in self.rows
        ):
            raise ValueError("rows must be a sequence of MatrixRow")
        member_set = set(self.member_gate_ids)
        seen_candidates: set[str] = set()
        for row in self.rows:
            if row.candidate_id in seen_candidates:
                raise ValueError(f"duplicate row for {row.candidate_id}")
            seen_candidates.add(row.candidate_id)
            if set(row.cells) != member_set:
                raise ValueError(
                    f"row {row.candidate_id} must have exactly one cell per member "
                    f"gate ({sorted(member_set)})"
                )

    def wide_columns(self) -> tuple[str, ...]:
        """The wide CSV header this view serialises to."""

        return (
            MATRIX_WIDE_FIXED_COLUMNS
            + tuple(self.member_gate_ids)
            + (MATRIX_WIDE_TRAILING_COLUMN,)
        )

    def traced_cells(self) -> tuple[tuple[str, str, str], ...]:
        """``(candidate_id, gate_id, state)`` for every cell that must resolve to
        at least one EvidencePackage (i.e. not UNKNOWN / NOT_APPLICABLE /
        NOT_EVALUATED)."""

        out: list[tuple[str, str, str]] = []
        for row in self.rows:
            for gate_id in self.member_gate_ids:
                state = row.cells[gate_id]
                if state not in _UNBACKED_CELL_STATES:
                    out.append((row.candidate_id, gate_id, state))
        return tuple(out)


# --- Reusable-evidence reference layer ------------------------------------

@dataclass(frozen=True)
class EvidenceIndexEntry:
    """One row of ``30_EVIDENCE_LIBRARY/evidence_index.csv``.

    Field order matches the frozen ``library_evidence_index`` header exactly.
    """

    evidence_id: str
    schema_version: int
    claim_short: str
    measurement_type: str
    primary_source_id: str
    candidate_refs: tuple[str, ...]
    created_at: str
    status: str
    superseded_by: str = ""

    def __post_init__(self) -> None:
        _freeze_attr(self, "candidate_refs")

        _require_pattern(self.evidence_id, _EVIDENCE_ID, "evidence_id")
        _require_positive_int(self.schema_version, "schema_version")
        _require_text(self.claim_short, "claim_short")
        _require_text(self.measurement_type, "measurement_type")
        _require_pattern(self.primary_source_id, _SOURCE_ID, "primary_source_id")

        if not isinstance(self.candidate_refs, tuple) or not all(
            isinstance(ref, str) and _CANDIDATE_ID.match(ref)
            for ref in self.candidate_refs
        ):
            raise ValueError(
                "candidate_refs must be a tuple of CAND-Lnn-nnnnnn ids (may be empty)"
            )

        _require_str(self.created_at, "created_at")
        if not _ISO_DATE_PREFIX.match(self.created_at):
            raise ValueError("created_at must start with an ISO date")

        _require_choice(self.status, EVIDENCE_INDEX_STATUS_VALUES, "status")

        if self.superseded_by:
            _require_pattern(self.superseded_by, _EVIDENCE_ID, "superseded_by")
            if self.superseded_by == self.evidence_id:
                raise ValueError("superseded_by must not point at the entry itself")
            if self.status != "SUPERSEDED":
                raise ValueError(
                    "superseded_by is set, so status must be SUPERSEDED"
                )
        elif self.status == "SUPERSEDED":
            raise ValueError("status SUPERSEDED requires a superseded_by pointer")


@dataclass(frozen=True)
class EvidenceLibraryIndex:
    """The whole ``evidence_index.csv``: rows with global integrity checks."""

    entries: tuple[EvidenceIndexEntry, ...]

    def __post_init__(self) -> None:
        _freeze_attr(self, "entries")
        if not isinstance(self.entries, tuple) or not all(
            isinstance(entry, EvidenceIndexEntry) for entry in self.entries
        ):
            raise ValueError("entries must be a sequence of EvidenceIndexEntry")

        by_id: dict[str, EvidenceIndexEntry] = {}
        for entry in self.entries:
            if entry.evidence_id in by_id:
                raise ValueError(f"duplicate evidence_id {entry.evidence_id}")
            by_id[entry.evidence_id] = entry

        for entry in self.entries:
            if not entry.superseded_by:
                continue
            # every forward pointer resolves within the index and forms no cycle
            seen = {entry.evidence_id}
            cursor = entry.superseded_by
            while cursor:
                if cursor not in by_id:
                    raise ValueError(
                        f"{entry.evidence_id}.superseded_by -> {cursor} is not in the index"
                    )
                if cursor in seen:
                    raise ValueError(
                        f"supersession cycle through {cursor}"
                    )
                seen.add(cursor)
                cursor = by_id[cursor].superseded_by

    def by_evidence_id(self, evidence_id: str) -> EvidenceIndexEntry | None:
        for entry in self.entries:
            if entry.evidence_id == evidence_id:
                return entry
        return None


@dataclass(frozen=True)
class SourceIndexEntry:
    """One row of ``30_EVIDENCE_LIBRARY/source_index.csv``."""

    source_id: str
    source_type: str
    external_id: str
    title: str
    year: object
    external_ref: str

    def __post_init__(self) -> None:
        _require_pattern(self.source_id, _SOURCE_ID, "source_id")
        _require_choice(self.source_type, SOURCE_TYPE_VALUES, "source_type")
        _require_text(self.external_id, "external_id")
        _require_str(self.title, "title", allow_empty=True)
        _require_year(self.year, "year")
        _require_external_ref(self.external_ref, "external_ref")


@dataclass(frozen=True)
class SourceIndex:
    """The whole ``source_index.csv``: rows with a unique-id check."""

    entries: tuple[SourceIndexEntry, ...]

    def __post_init__(self) -> None:
        _freeze_attr(self, "entries")
        if not isinstance(self.entries, tuple) or not all(
            isinstance(entry, SourceIndexEntry) for entry in self.entries
        ):
            raise ValueError("entries must be a sequence of SourceIndexEntry")
        source_ids = [entry.source_id for entry in self.entries]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_index entries must have unique source_id")

    def by_source_id(self, source_id: str) -> SourceIndexEntry | None:
        for entry in self.entries:
            if entry.source_id == source_id:
                return entry
        return None


@dataclass(frozen=True)
class GateEvidenceIndexEntry:
    """One row of a per-gate ``TGT-NN/CURRENT/evidence_index.csv`` -- a reference,
    not a copy. Field order matches the frozen ``gate_evidence_index`` header."""

    evidence_id: str
    candidate_id: str
    role: str
    assessment_id: str

    def __post_init__(self) -> None:
        _require_pattern(self.evidence_id, _EVIDENCE_ID, "evidence_id")
        _require_pattern(self.candidate_id, _CANDIDATE_ID, "candidate_id")
        _require_choice(self.role, EVIDENCE_ROLE_VALUES, "role")
        _require_pattern(self.assessment_id, _ASSESSMENT_ID, "assessment_id")


@dataclass(frozen=True)
class GateEvidenceIndex:
    """One Gate's ``CURRENT/evidence_index.csv``. The ``gate_id`` is
    folder-implicit on disk and carried here so the object is self-describing."""

    gate_id: str
    entries: tuple[GateEvidenceIndexEntry, ...]

    def __post_init__(self) -> None:
        _freeze_attr(self, "entries")
        _require_text(self.gate_id, "gate_id")
        if not isinstance(self.entries, tuple) or not all(
            isinstance(entry, GateEvidenceIndexEntry) for entry in self.entries
        ):
            raise ValueError("entries must be a sequence of GateEvidenceIndexEntry")

    def candidate_ids(self) -> frozenset[str]:
        return frozenset(entry.candidate_id for entry in self.entries)


# --- Provenance walk: referential integrity across the reference layer -----

def check_evidence_library_against_sources(
    library: EvidenceLibraryIndex, sources: SourceIndex
) -> None:
    """Every EvidencePackage's ``primary_source_id`` must exist in the source
    index. Raises ``ValueError`` on the first dangling reference."""

    known = {entry.source_id for entry in sources.entries}
    for entry in library.entries:
        if entry.primary_source_id not in known:
            raise ValueError(
                f"{entry.evidence_id}.primary_source_id {entry.primary_source_id} "
                "is not in the source index"
            )


def check_gate_index_against_library(
    gate_index: GateEvidenceIndex, library: EvidenceLibraryIndex
) -> None:
    """Every per-gate evidence reference must resolve to a library
    EvidencePackage. Raises ``ValueError`` on the first dangling reference."""

    known = {entry.evidence_id for entry in library.entries}
    for entry in gate_index.entries:
        if entry.evidence_id not in known:
            raise ValueError(
                f"gate {gate_index.gate_id}: evidence reference {entry.evidence_id} "
                "is not in the evidence library index"
            )


def check_matrix_cells_are_backed(
    matrix_view: MatrixView, gate_indexes: Mapping[str, GateEvidenceIndex]
) -> None:
    """Every Matrix cell that is not UNKNOWN / NOT_APPLICABLE / NOT_EVALUATED
    must have at least one per-gate evidence reference for that Candidate.
    ``gate_indexes`` is keyed by ``gate_id``. Raises ``ValueError`` on the first
    unbacked cell."""

    for candidate_id, gate_id, state in matrix_view.traced_cells():
        gate_index = gate_indexes.get(gate_id)
        if gate_index is None or candidate_id not in gate_index.candidate_ids():
            raise ValueError(
                f"Matrix cell ({candidate_id}, {gate_id})={state} has no backing "
                "evidence reference"
            )


# --- Introspection helpers (used by the parity test) -----------------------

EVIDENCE_REFERENCE_OBJECTS: Final[tuple[type, ...]] = (
    MatrixView,
    MatrixRow,
    EvidenceIndexEntry,
    EvidenceLibraryIndex,
    SourceIndexEntry,
    SourceIndex,
    GateEvidenceIndexEntry,
    GateEvidenceIndex,
)


def field_names(object_type: type) -> tuple[str, ...]:
    """Return the declared field names of an evidence-reference dataclass."""

    return tuple(f.name for f in fields(object_type))
