"""Runtime Migration PR C: the Matrix view + reusable-evidence reference layer.

Asserts:
* the ``src/contracts/evidence_reference.yaml`` registry and the
  ``src/objects/evidence_reference_model.py`` dataclasses agree;
* ``MatrixView`` / the index rows serialise to the frozen ``csv_headers.yaml``
  headers verbatim (no new JSON Schema is added under data_layout/);
* per-object accept / reject, including the mutable-index forward-pointer rule
  and the global container integrity checks;
* the provenance walk (referential integrity across the reference rows) holds;
* PR A's ``EvidencePackage`` still forbids a forward ``superseded_by`` / ``status``
  (the forward pointer lives only on ``EvidenceIndexEntry``);
* deep immutability holds, exactly as in PR A / PR B.
"""

import dataclasses
import json
import unittest
from pathlib import Path

import yaml

from src.objects.decision_model import EVIDENCE_PACKAGE_FORBIDDEN_FIELDS
from src.objects import evidence_reference_model as erm
from src.objects.evidence_reference_model import (
    DECISIONS_VIEW_COLUMNS,
    EVIDENCE_INDEX_STATUS_VALUES,
    MATRIX_CELL_STATES,
    MATRIX_LONG_COLUMNS,
    EvidenceIndexEntry,
    EvidenceLibraryIndex,
    GateEvidenceIndex,
    GateEvidenceIndexEntry,
    MatrixRow,
    MatrixView,
    SourceIndex,
    SourceIndexEntry,
    check_evidence_library_against_sources,
    check_gate_index_against_library,
    check_matrix_cells_are_backed,
    field_names,
)
from src.objects.gate_model import DECISION_VALUES


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "evidence_reference.yaml"
CSV_HEADERS = ROOT / "src" / "contracts" / "data_layout" / "csv_headers.yaml"
DECISION_OBJECTS_YAML = ROOT / "src" / "contracts" / "decision_objects.yaml"


def _load(path: Path):
    text = path.read_text()
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def _required_dataclass_fields(cls) -> set[str]:
    return {
        f.name
        for f in dataclasses.fields(cls)
        if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
    }


# --- valid instance factories -----------------------------------------

_ADC_TARGET_GATES = tuple(f"TGT-0{n}" for n in range(1, 9))


def make_row(**overrides) -> MatrixRow:
    base = dict(
        candidate_id="CAND-L04-000001",
        name="CEACAM5",
        cells={g: "NOT_EVALUATED" for g in _ADC_TARGET_GATES},
        decision="HOLD",
    )
    base.update(overrides)
    return MatrixRow(**base)


def make_matrix(**overrides) -> MatrixView:
    base = dict(
        instantiation_id="INST-CRC-REFRACTORY-ADC-TARGET-v1",
        gateset_id="ADC_TARGET_GATESET",
        candidate_level="L04",
        member_gate_ids=_ADC_TARGET_GATES,
        rows=(make_row(),),
    )
    base.update(overrides)
    return MatrixView(**base)


def make_evidence_entry(**overrides) -> EvidenceIndexEntry:
    base = dict(
        evidence_id="EP-00000123",
        schema_version=1,
        claim_short="CEACAM5 surface density ~1.2e5/cell in CRC",
        measurement_type="quantitative_surface_density",
        primary_source_id="SRC-00000001",
        candidate_refs=("CAND-L04-000001",),
        created_at="2026-08-27",
        status="ACTIVE",
    )
    base.update(overrides)
    return EvidenceIndexEntry(**base)


def make_source_entry(**overrides) -> SourceIndexEntry:
    base = dict(
        source_id="SRC-00000001",
        source_type="PMID",
        external_id="12345678",
        title="Surface proteomics of colorectal carcinoma",
        year="2025",
        external_ref="external:pmid/12345678",
    )
    base.update(overrides)
    return SourceIndexEntry(**base)


def make_gate_entry(**overrides) -> GateEvidenceIndexEntry:
    base = dict(
        evidence_id="EP-00000123",
        candidate_id="CAND-L04-000001",
        role="SUPPORTING",
        assessment_id="ASMT-000001",
    )
    base.update(overrides)
    return GateEvidenceIndexEntry(**base)


# --- 1. contract YAML shape -----------------------------------------

class ContractRegistryTests(unittest.TestCase):
    def setUp(self):
        self.doc = _load(CONTRACT_PATH)

    def test_version_and_contract_set(self):
        self.assertEqual(self.doc["version"], "0.1.0")
        self.assertEqual(
            set(self.doc["contracts"]),
            {
                "MatrixView",
                "EvidenceIndexEntry",
                "SourceIndexEntry",
                "GateEvidenceIndexEntry",
            },
        )
        for name, body in self.doc["contracts"].items():
            self.assertEqual(body["contract_id"], f"{name}@0.1.0")

    def test_migration_block(self):
        migration = self.doc["migration"]
        self.assertEqual(migration["pr"], "runtime_migration_pr_c")
        self.assertIn("decision_engine", migration["deferred"])
        self.assertIn("crc_adc_target_gateset_v1", migration["deferred"])
        self.assertIn("evidence_independence_definition", migration["open_questions"])

    def test_repository_policy_forbids_persistence_and_engine(self):
        policy = self.doc["repository_policy"]
        self.assertTrue(policy["instances_external_only"])
        self.assertEqual(policy["persistence_in_repository"], "forbidden")
        self.assertEqual(policy["decision_engine_in_repository"], "forbidden")

    def test_reusable_reference_mechanism_is_evidence_refs(self):
        block = self.doc["migration"]["reusable_evidence_reference"]
        self.assertEqual(block["mechanism"], "evidence_refs")
        self.assertIn("evidence_package_ids", block["note"])
        self.assertTrue(block["pr_a_contract_untouched"])

    def test_immutable_record_boundary_declared(self):
        block = self.doc["migration"]["immutable_record_boundary"]
        self.assertIn("forward", block["rule"].lower())
        self.assertEqual(
            block["forward_pointer_home"],
            "EvidenceIndexEntry.status + EvidenceIndexEntry.superseded_by",
        )

    def test_matrix_view_declared_as_derived_no_id(self):
        note = self.doc["migration"]["parity"]["MatrixView"]["note"]
        self.assertIn("rebuildable projection", note)
        self.assertIn("no id", note.lower())


# --- 2. registry <-> Python parity --------------------------------

_CONTRACT_TO_CLASS = {
    "MatrixView": MatrixView,
    "EvidenceIndexEntry": EvidenceIndexEntry,
    "SourceIndexEntry": SourceIndexEntry,
    "GateEvidenceIndexEntry": GateEvidenceIndexEntry,
}


class RegistryPythonParityTests(unittest.TestCase):
    def setUp(self):
        self.doc = _load(CONTRACT_PATH)

    def test_required_fields_match(self):
        for name, cls in _CONTRACT_TO_CLASS.items():
            with self.subTest(contract=name):
                self.assertEqual(
                    set(self.doc["contracts"][name]["required_fields"]),
                    _required_dataclass_fields(cls),
                )

    def test_vocabularies_match(self):
        v = self.doc["vocabularies"]
        self.assertEqual(
            tuple(v["evidence_index_status"]), EVIDENCE_INDEX_STATUS_VALUES
        )
        self.assertEqual(v["matrix_cell_regex"], erm._MATRIX_CELL.pattern)
        self.assertEqual(tuple(v["matrix_long_columns"]), MATRIX_LONG_COLUMNS)
        self.assertEqual(tuple(v["decisions_view_columns"]), DECISIONS_VIEW_COLUMNS)
        self.assertEqual(
            tuple(v["matrix_wide_fixed_columns"]), erm.MATRIX_WIDE_FIXED_COLUMNS
        )
        self.assertEqual(
            v["matrix_wide_trailing_column"], erm.MATRIX_WIDE_TRAILING_COLUMN
        )

    def test_matrix_cell_states_cover_the_regex(self):
        for state in MATRIX_CELL_STATES:
            self.assertRegex(state, erm._MATRIX_CELL.pattern)
        # 4 directions x 3 strengths + 3 single-value states
        self.assertEqual(len(MATRIX_CELL_STATES), 4 * 3 + 3)


# --- 3. frozen csv_headers.yaml parity (no new JSON Schema) ---------

class CsvHeaderParityTests(unittest.TestCase):
    def setUp(self):
        self.headers = _load(CSV_HEADERS)["headers"]

    def test_no_new_schema_files_under_data_layout(self):
        names = {p.name for p in (ROOT / "src" / "contracts" / "data_layout").iterdir()}
        self.assertNotIn("matrix.schema.json", names)
        self.assertNotIn("evidence_index.schema.json", names)
        self.assertNotIn("source_index.schema.json", names)

    def test_library_evidence_index_header_matches_entry_fields(self):
        self.assertEqual(
            tuple(self.headers["library_evidence_index"]),
            field_names(EvidenceIndexEntry),
        )
        # the YAML mirrors the same ordered column list
        doc = _load(CONTRACT_PATH)["contracts"]["EvidenceIndexEntry"]
        self.assertEqual(
            tuple(doc["csv_columns"]), tuple(self.headers["library_evidence_index"])
        )
        self.assertEqual(
            set(doc["required_fields"]) | set(doc["optional_fields"]),
            set(field_names(EvidenceIndexEntry)),
        )

    def test_library_source_index_header_matches_entry_fields(self):
        self.assertEqual(
            tuple(self.headers["library_source_index"]),
            field_names(SourceIndexEntry),
        )

    def test_gate_evidence_index_header_matches_entry_fields(self):
        self.assertEqual(
            tuple(self.headers["gate_evidence_index"]),
            field_names(GateEvidenceIndexEntry),
        )

    def test_wide_matrix_header_rebuilds_the_frozen_adc_target_header(self):
        view = make_matrix()
        self.assertEqual(
            list(view.wide_columns()), self.headers["matrix_adc_target"]
        )

    def test_long_and_decisions_headers_match_module_constants(self):
        self.assertEqual(
            tuple(self.headers["assessments_long"]), MATRIX_LONG_COLUMNS
        )
        self.assertEqual(tuple(self.headers["decisions"]), DECISIONS_VIEW_COLUMNS)


# --- 4. MatrixView / MatrixRow accept / reject --------------------

class MatrixViewTests(unittest.TestCase):
    def test_valid(self):
        view = make_matrix()
        self.assertEqual(len(view.rows), 1)
        self.assertEqual(view.candidate_level, "L04")

    def test_rejects_non_canonical_gateset_for_level(self):
        with self.assertRaises(ValueError):
            make_matrix(candidate_level="L05")  # id is ADC_TARGET_GATESET (L04)
        ok = make_matrix(
            candidate_level="L05",
            gateset_id="ADC_EPITOPE_GATESET",
        )
        self.assertEqual(ok.gateset_id, "ADC_EPITOPE_GATESET")

    def test_rejects_bad_ids(self):
        with self.assertRaises(ValueError):
            make_matrix(instantiation_id="CRC-ADC-TARGET")
        with self.assertRaises(ValueError):
            make_matrix(gateset_id="adc_target_gateset")

    def test_member_gate_ids_must_be_unique_and_non_empty(self):
        with self.assertRaises(ValueError):
            make_matrix(member_gate_ids=())
        with self.assertRaises(ValueError):
            make_matrix(member_gate_ids=("TGT-01", "TGT-01"))

    def test_every_row_has_one_cell_per_member_gate(self):
        with self.assertRaises(ValueError):  # missing a member gate
            make_matrix(rows=(make_row(cells={"TGT-01": "UNKNOWN"}),))
        with self.assertRaises(ValueError):  # cell for a non-member gate
            cells = {g: "NOT_EVALUATED" for g in _ADC_TARGET_GATES}
            cells["TGT-99"] = "UNKNOWN"
            make_matrix(rows=(make_row(cells=cells),))

    def test_duplicate_candidate_row_rejected(self):
        with self.assertRaises(ValueError):
            make_matrix(rows=(make_row(), make_row()))

    def test_row_cell_state_and_decision_validation(self):
        with self.assertRaises(ValueError):
            make_row(cells={g: "POSITIVE" for g in _ADC_TARGET_GATES})
        with self.assertRaises(ValueError):
            make_row(cells={g: "+3" for g in _ADC_TARGET_GATES})
        with self.assertRaises(ValueError):
            make_row(decision="PROCEED")
        ok = make_row(decision="NOT_EVALUATED")
        self.assertEqual(ok.decision, "NOT_EVALUATED")
        for value in DECISION_VALUES:
            self.assertEqual(make_row(decision=value).decision, value)

    def test_traced_cells_skips_unbacked_states(self):
        cells = {g: "NOT_EVALUATED" for g in _ADC_TARGET_GATES}
        cells["TGT-01"] = "POSITIVE/DIRECT"
        cells["TGT-02"] = "UNKNOWN"
        cells["TGT-03"] = "NOT_APPLICABLE"
        view = make_matrix(rows=(make_row(cells=cells),))
        self.assertEqual(
            view.traced_cells(),
            (("CAND-L04-000001", "TGT-01", "POSITIVE/DIRECT"),),
        )


# --- 5. EvidenceIndexEntry / EvidenceLibraryIndex ----------------

class EvidenceIndexEntryTests(unittest.TestCase):
    def test_valid_active(self):
        entry = make_evidence_entry()
        self.assertEqual(entry.status, "ACTIVE")
        self.assertEqual(entry.superseded_by, "")

    def test_superseded_requires_pointer_and_vice_versa(self):
        with self.assertRaises(ValueError):  # SUPERSEDED without pointer
            make_evidence_entry(status="SUPERSEDED")
        with self.assertRaises(ValueError):  # pointer without SUPERSEDED status
            make_evidence_entry(superseded_by="EP-00000200")
        with self.assertRaises(ValueError):  # ACTIVE + pointer
            make_evidence_entry(status="ACTIVE", superseded_by="EP-00000200")
        ok = make_evidence_entry(status="SUPERSEDED", superseded_by="EP-00000200")
        self.assertEqual(ok.superseded_by, "EP-00000200")

    def test_no_self_supersession(self):
        with self.assertRaises(ValueError):
            make_evidence_entry(status="SUPERSEDED", superseded_by="EP-00000123")

    def test_retracted_may_have_no_pointer(self):
        entry = make_evidence_entry(status="RETRACTED")
        self.assertEqual(entry.superseded_by, "")

    def test_rejects_bad_refs(self):
        with self.assertRaises(ValueError):
            make_evidence_entry(primary_source_id="SRC-1")
        with self.assertRaises(ValueError):
            make_evidence_entry(candidate_refs=("CAND-1",))
        with self.assertRaises(ValueError):
            make_evidence_entry(created_at="27-08-2026")

    def test_candidate_refs_may_be_empty(self):
        self.assertEqual(make_evidence_entry(candidate_refs=()).candidate_refs, ())


class EvidenceLibraryIndexTests(unittest.TestCase):
    def test_unique_evidence_id(self):
        with self.assertRaises(ValueError):
            EvidenceLibraryIndex((make_evidence_entry(), make_evidence_entry()))

    def test_superseded_by_must_resolve_within_index(self):
        old = make_evidence_entry(status="SUPERSEDED", superseded_by="EP-00000200")
        with self.assertRaises(ValueError):
            EvidenceLibraryIndex((old,))
        new = make_evidence_entry(evidence_id="EP-00000200")
        idx = EvidenceLibraryIndex((old, new))
        self.assertEqual(idx.by_evidence_id("EP-00000200"), new)

    def test_supersession_cycle_rejected(self):
        a = make_evidence_entry(
            evidence_id="EP-00000001", status="SUPERSEDED", superseded_by="EP-00000002"
        )
        b = make_evidence_entry(
            evidence_id="EP-00000002", status="SUPERSEDED", superseded_by="EP-00000001"
        )
        with self.assertRaises(ValueError):
            EvidenceLibraryIndex((a, b))


# --- 6. SourceIndexEntry / SourceIndex --------------------------

class SourceIndexTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(make_source_entry().source_type, "PMID")

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_source_entry(source_id="SRC-1")
        with self.assertRaises(ValueError):
            make_source_entry(source_type="PREPRINT")
        with self.assertRaises(ValueError):
            make_source_entry(external_ref="pmid/12345678")
        with self.assertRaises(ValueError):
            make_source_entry(year="20xy")

    def test_year_accepts_int_or_empty(self):
        self.assertEqual(make_source_entry(year=2025).year, 2025)
        self.assertEqual(make_source_entry(year="").year, "")

    def test_unique_source_id(self):
        with self.assertRaises(ValueError):
            SourceIndex((make_source_entry(), make_source_entry()))
        idx = SourceIndex(
            (make_source_entry(), make_source_entry(source_id="SRC-00000002"))
        )
        self.assertEqual(idx.by_source_id("SRC-00000002").source_id, "SRC-00000002")


# --- 7. GateEvidenceIndex --------------------------------------

class GateEvidenceIndexTests(unittest.TestCase):
    def test_valid(self):
        gi = GateEvidenceIndex("TGT-04", (make_gate_entry(),))
        self.assertEqual(gi.candidate_ids(), frozenset({"CAND-L04-000001"}))

    def test_row_rejects(self):
        with self.assertRaises(ValueError):
            make_gate_entry(evidence_id="EP-1")
        with self.assertRaises(ValueError):
            make_gate_entry(candidate_id="CAND-1")
        with self.assertRaises(ValueError):
            make_gate_entry(role="PRIMARY")
        with self.assertRaises(ValueError):
            make_gate_entry(assessment_id="ASMT-1")

    def test_container_rejects_empty_gate_id(self):
        with self.assertRaises(ValueError):
            GateEvidenceIndex("", (make_gate_entry(),))


# --- 8. provenance walk (referential integrity) ----------------

class ProvenanceWalkTests(unittest.TestCase):
    def test_library_against_sources(self):
        library = EvidenceLibraryIndex((make_evidence_entry(),))
        good_sources = SourceIndex((make_source_entry(),))
        check_evidence_library_against_sources(library, good_sources)  # no raise
        empty_sources = SourceIndex(())
        with self.assertRaises(ValueError):
            check_evidence_library_against_sources(library, empty_sources)

    def test_gate_index_against_library(self):
        library = EvidenceLibraryIndex((make_evidence_entry(),))
        gi = GateEvidenceIndex("TGT-04", (make_gate_entry(),))
        check_gate_index_against_library(gi, library)  # no raise
        dangling = GateEvidenceIndex(
            "TGT-04", (make_gate_entry(evidence_id="EP-00009999"),)
        )
        with self.assertRaises(ValueError):
            check_gate_index_against_library(dangling, library)

    def test_matrix_cells_are_backed(self):
        cells = {g: "NOT_EVALUATED" for g in _ADC_TARGET_GATES}
        cells["TGT-04"] = "POSITIVE/DIRECT"
        cells["TGT-02"] = "UNKNOWN"  # unbacked state -> no evidence needed
        view = make_matrix(rows=(make_row(cells=cells),))

        backed = {"TGT-04": GateEvidenceIndex("TGT-04", (make_gate_entry(),))}
        check_matrix_cells_are_backed(view, backed)  # no raise

        with self.assertRaises(ValueError):
            check_matrix_cells_are_backed(view, {})
        wrong_candidate = {
            "TGT-04": GateEvidenceIndex(
                "TGT-04", (make_gate_entry(candidate_id="CAND-L04-000009"),)
            )
        }
        with self.assertRaises(ValueError):
            check_matrix_cells_are_backed(view, wrong_candidate)


# --- 9. immutable-record boundary + PR A untouched -------------

class ImmutableBoundaryTests(unittest.TestCase):
    def test_forward_pointer_is_forbidden_on_the_canonical_evidence_package(self):
        # PR A already bans status / superseded_by on EvidencePackage; PR C's
        # index is the only place they may appear.
        self.assertIn("superseded_by", EVIDENCE_PACKAGE_FORBIDDEN_FIELDS)
        self.assertIn("status", EVIDENCE_PACKAGE_FORBIDDEN_FIELDS)
        self.assertIn("superseded_by", field_names(EvidenceIndexEntry))
        self.assertIn("status", field_names(EvidenceIndexEntry))

    def test_decision_objects_yaml_still_defers_pr_c(self):
        deferred = _load(DECISION_OBJECTS_YAML)["migration"]["deferred"]
        self.assertEqual(
            deferred["matrix_and_reusable_evidence_references"], "PR C"
        )


# --- 10. deep immutability -----------------------------------

class DeepImmutabilityTests(unittest.TestCase):
    def test_external_dict_mutation_does_not_reach_matrix_row(self):
        cells = {g: "NOT_EVALUATED" for g in _ADC_TARGET_GATES}
        row = make_row(cells=cells)
        cells["TGT-01"] = "POSITIVE/DIRECT"
        self.assertEqual(row.cells["TGT-01"], "NOT_EVALUATED")

    def test_external_list_mutation_does_not_reach_evidence_entry(self):
        refs = ["CAND-L04-000001"]
        entry = make_evidence_entry(candidate_refs=tuple(refs))
        refs.append("CAND-L04-000002")
        self.assertEqual(entry.candidate_refs, ("CAND-L04-000001",))

    def test_nested_values_cannot_be_mutated_through_the_object(self):
        row = make_row()
        with self.assertRaises(TypeError):
            row.cells["TGT-01"] = "x"
        view = make_matrix()
        with self.assertRaises(AttributeError):
            view.member_gate_ids = ()


if __name__ == "__main__":
    unittest.main()
