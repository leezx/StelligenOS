"""Runtime Migration PR A: Blueprint v1.3 decision-layer object contracts.

Asserts three kinds of thing:

* the ``src/contracts/decision_objects.yaml`` registry and the
  ``src/objects/decision_model.py`` dataclasses agree;
* those dataclasses agree, field for field and enum for enum, with the frozen
  ``src/contracts/data_layout/*.schema.*`` disk schemas, so the runtime contract
  cannot drift from the Data Layout Spec v1.0;
* the legacy ``core_objects@1.1`` path still works unchanged and the crosswalk
  covers it.
"""

import dataclasses
import json
import unittest
from pathlib import Path

import yaml

from src.objects import decision_model as dm
from src.objects.core import CORE_OBJECT_TYPES, CoreObject
from src.objects.decision_model import (
    Candidate,
    CandidateGateAssessment,
    Context,
    EvidencePackage,
    EvidenceRef,
    Instantiation,
)
from src.objects.legacy_adapters import (
    LEGACY_CROSSWALK,
    ONE_TO_ONE_LEGACY_TYPES,
    adapt_core_object_to_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "decision_objects.yaml"
DATA_LAYOUT = ROOT / "src" / "contracts" / "data_layout"


def _load(path: Path):
    text = path.read_text()
    if path.suffix == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def _required_dataclass_fields(cls) -> set[str]:
    required = set()
    for f in dataclasses.fields(cls):
        if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING:
            required.add(f.name)
    return required


def _schema_forbidden(schema: dict) -> set[str]:
    return {entry["required"][0] for entry in schema["not"]["anyOf"]}


# --- valid instance factories ---------------------------------------------

def make_candidate(**overrides) -> Candidate:
    base = dict(
        candidate_id="CAND-L04-000001",
        candidate_type="ADC_TARGET",
        level="L04",
        canonical_name="CEACAM5",
        status="ACTIVE",
        version=1,
        created_at="2026-08-28",
        provenance_ref="external:ADCdb/target/CEACAM5@v3",
    )
    base.update(overrides)
    return Candidate(**base)


def make_context(**overrides) -> Context:
    base = dict(
        context_id="CTX-CRC-REFRACTORY-MSSPMMR",
        context_version=1,
        canonical_name="Refractory MSS/pMMR metastatic colorectal cancer",
        dimensions={"indication": "colorectal cancer", "anatomical_site": None},
        status="ACTIVE",
        created_at="2026-08-28",
    )
    base.update(overrides)
    return Context(**base)


def make_evidence_package(**overrides) -> EvidencePackage:
    base = dict(
        evidence_id="EP-00000123",
        schema_version=1,
        claim="Target X protein detected on malignant epithelial membranes.",
        measurement={
            "type": "IHC",
            "analyte": "Target X protein",
            "readout": "membranous staining",
            "result": "68% positive tumors",
        },
        candidate_refs=("CAND-L04-000001",),
        study_context={
            "indication": "colorectal cancer",
            "treatment_state": "mixed",
            "sample_type": "primary tumor",
        },
        provenance={
            "source_id": "SRC-00000881",
            "source_type": "PMID",
            "source_identifier": "12345678",
            "locator": "Figure 2",
            "retrieved_at": "2026-08-27",
        },
        interpretation_boundary={
            "directly_supports": ["membrane protein detectable"],
            "does_not_support": ["quantitative antigen density"],
            "limitations": ["semiquantitative IHC"],
            "evidence_ceiling": "protein-level surface plausibility",
        },
        derivation={"module_run_id": "RUN-TGT04-20260827-001", "code_commit": "abc123"},
    )
    base.update(overrides)
    return EvidencePackage(**base)


_REVIEW = {"status": "HUMAN_APPROVED", "reviewer": "human", "reviewed_at": "2026-08-27"}


def make_assessment(**overrides) -> CandidateGateAssessment:
    base = dict(
        assessment_id="ASMT-000001",
        assessment_version=1,
        instantiation_id="INST-CRC-REFRACTORY-ADC-TARGET-v1",
        candidate_id="CAND-L04-000001",
        context_id="CTX-CRC-REFRACTORY-MSSPMMR",
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-04",
        gate_version="1.0",
        direction="POSITIVE",
        strength="INDIRECT_STRONG",
        evidence_refs=(EvidenceRef("EP-00000123", "SUPPORTING"),),
        aggregation_rationale="Concordant surface-availability evidence.",
        critical_unknowns=(
            {"unknown": "Quantitative antigen density", "resolution": "EXPERIMENT_REQUIRED"},
        ),
        evidence_ceiling="Surface availability, not quantitative density.",
        review=dict(_REVIEW),
    )
    base.update(overrides)
    return CandidateGateAssessment(**base)


def make_instantiation(**overrides) -> Instantiation:
    base = dict(
        instantiation_id="INST-CRC-REFRACTORY-ADC-TARGET-v1",
        candidate_type="ADC_TARGET",
        candidate_level="L04",
        context_id="CTX-CRC-REFRACTORY-MSSPMMR",
        context_version=1,
        modality="ADC",
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        status="ACTIVE",
        version=1,
        created_at="2026-08-28",
    )
    base.update(overrides)
    return Instantiation(**base)


# --- 1. contract YAML shape ---------------------------------------------------

class ContractRegistryTests(unittest.TestCase):
    def setUp(self):
        self.doc = _load(CONTRACT_PATH)

    def test_version_and_contract_set(self):
        self.assertEqual(self.doc["version"], "0.1.0")
        self.assertEqual(
            set(self.doc["contracts"]),
            {"Candidate", "Context", "EvidencePackage", "CandidateGateAssessment", "Instantiation"},
        )
        for name, body in self.doc["contracts"].items():
            self.assertEqual(body["contract_id"], f"{name}@0.1.0")

    def test_migration_block_defers_the_rest(self):
        migration = self.doc["migration"]
        self.assertEqual(migration["pr"], "runtime_migration_pr_a")
        deferred = migration["deferred"]
        self.assertIn("Decision", deferred)
        self.assertIn("canonical_gateset_contracts", deferred)

    def test_registry_does_not_touch_legacy_core_objects(self):
        legacy = _load(ROOT / "src" / "contracts" / "core_objects.yaml")
        self.assertEqual(legacy["version"], "1.1")
        self.assertEqual(len(legacy["objects"]), 8)


# --- 2. YAML registry <-> Python parity ------------------------------------

_CONTRACT_TO_CLASS = {
    "Candidate": Candidate,
    "Context": Context,
    "EvidencePackage": EvidencePackage,
    "CandidateGateAssessment": CandidateGateAssessment,
    "Instantiation": Instantiation,
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

    def test_forbidden_fields_match_module_tuples(self):
        cases = {
            "Candidate": dm.CANDIDATE_FORBIDDEN_FIELDS,
            "Context": dm.CONTEXT_FORBIDDEN_FIELDS,
            "EvidencePackage": dm.EVIDENCE_PACKAGE_FORBIDDEN_FIELDS,
            "CandidateGateAssessment": dm.ASSESSMENT_FORBIDDEN_FIELDS,
            "Instantiation": dm.INSTANTIATION_FORBIDDEN_FIELDS,
        }
        for name, tup in cases.items():
            with self.subTest(contract=name):
                self.assertEqual(
                    set(self.doc["contracts"][name]["forbidden_fields"]), set(tup)
                )

    def test_allowed_values_match_vocabularies(self):
        contracts = self.doc["contracts"]
        self.assertEqual(
            tuple(contracts["Candidate"]["allowed_values"]["level"]), dm.CANDIDATE_LEVELS
        )
        self.assertEqual(
            tuple(contracts["Candidate"]["allowed_values"]["status"]),
            dm.CANDIDATE_STATUS_VALUES,
        )
        adir = contracts["CandidateGateAssessment"]["allowed_values"]
        self.assertEqual(tuple(adir["direction"]), dm.DIRECTION_VALUES)
        self.assertEqual(tuple(adir["strength"]), dm.STRENGTH_VALUES)
        self.assertEqual(tuple(adir["evidence_ref_role"]), dm.EVIDENCE_ROLE_VALUES)
        self.assertEqual(
            tuple(adir["critical_unknown_resolution"]), dm.CRITICAL_UNKNOWN_RESOLUTIONS
        )
        self.assertEqual(tuple(adir["review_status"]), (dm.CANONICAL_REVIEW_STATUS,))
        inst = contracts["Instantiation"]["allowed_values"]
        self.assertEqual(tuple(inst["evidence_regime"]), dm.EVIDENCE_REGIME_VALUES)
        self.assertEqual(tuple(inst["status"]), dm.INSTANTIATION_STATUS_VALUES)

    def test_candidate_levels_match_registry_table(self):
        table = tuple(row["level"] for row in self.doc["candidate_levels"])
        self.assertEqual(table, dm.CANDIDATE_LEVELS)


# --- 3. data_layout schema <-> Python parity -----------------------------

class DataLayoutSchemaParityTests(unittest.TestCase):
    """The runtime contract must not drift from the frozen Data Layout Spec v1.0."""

    SCHEMA = {
        "Candidate": "candidate.schema.json",
        "Context": "context.schema.yaml",
        "EvidencePackage": "evidence_package.schema.json",
        "CandidateGateAssessment": "assessment.schema.json",
        "Instantiation": "instantiation.schema.yaml",
    }

    def _schema(self, name: str) -> dict:
        return _load(DATA_LAYOUT / self.SCHEMA[name])

    def test_required_arrays_match_required_dataclass_fields(self):
        for name, cls in _CONTRACT_TO_CLASS.items():
            with self.subTest(object=name):
                self.assertEqual(
                    set(self._schema(name)["required"]),
                    _required_dataclass_fields(cls),
                )

    def test_not_anyof_forbidden_fields_match_and_are_absent(self):
        cases = {
            "Candidate": (Candidate, dm.CANDIDATE_FORBIDDEN_FIELDS),
            "Context": (Context, dm.CONTEXT_FORBIDDEN_FIELDS),
            "EvidencePackage": (EvidencePackage, dm.EVIDENCE_PACKAGE_FORBIDDEN_FIELDS),
            "CandidateGateAssessment": (CandidateGateAssessment, dm.ASSESSMENT_FORBIDDEN_FIELDS),
            "Instantiation": (Instantiation, dm.INSTANTIATION_FORBIDDEN_FIELDS),
        }
        for name, (cls, tup) in cases.items():
            with self.subTest(object=name):
                self.assertEqual(_schema_forbidden(self._schema(name)), set(tup))
                declared = {f.name for f in dataclasses.fields(cls)}
                self.assertEqual(declared & set(tup), set())

    def test_enums_match_vocabularies(self):
        cand = self._schema("Candidate")["properties"]
        self.assertEqual(tuple(cand["level"]["enum"]), dm.CANDIDATE_LEVELS)
        self.assertEqual(tuple(cand["status"]["enum"]), dm.CANDIDATE_STATUS_VALUES)

        ctx = self._schema("Context")["properties"]
        self.assertEqual(tuple(ctx["status"]["enum"]), dm.CONTEXT_STATUS_VALUES)

        asmt = self._schema("CandidateGateAssessment")["properties"]
        self.assertEqual(tuple(asmt["direction"]["enum"]), dm.DIRECTION_VALUES)
        self.assertEqual(tuple(asmt["strength"]["enum"]), dm.STRENGTH_VALUES)
        self.assertEqual(
            tuple(asmt["evidence_refs"]["items"]["properties"]["role"]["enum"]),
            dm.EVIDENCE_ROLE_VALUES,
        )
        self.assertEqual(
            tuple(
                asmt["critical_unknowns"]["items"]["properties"]["resolution"]["enum"]
            ),
            dm.CRITICAL_UNKNOWN_RESOLUTIONS,
        )
        self.assertEqual(
            asmt["review"]["properties"]["status"]["const"], dm.CANONICAL_REVIEW_STATUS
        )

        ep = self._schema("EvidencePackage")["properties"]
        self.assertEqual(
            tuple(ep["provenance"]["properties"]["source_type"]["enum"]),
            dm.SOURCE_TYPE_VALUES,
        )

        inst = self._schema("Instantiation")["properties"]
        self.assertEqual(
            tuple(inst["evidence_regime"]["enum"]), dm.EVIDENCE_REGIME_VALUES
        )
        self.assertEqual(tuple(inst["status"]["enum"]), dm.INSTANTIATION_STATUS_VALUES)
        self.assertEqual(
            tuple(inst["candidate_level"]["enum"]), dm.CANDIDATE_LEVELS
        )

    def test_nested_required_keys_match_registry(self):
        ep_schema = self._schema("EvidencePackage")["properties"]
        registry = _load(CONTRACT_PATH)["contracts"]["EvidencePackage"]["nested_required_keys"]
        for block, keys in registry.items():
            with self.subTest(block=block):
                self.assertEqual(
                    set(ep_schema[block]["required"]), set(keys)
                )

    def test_id_patterns_match(self):
        cand = self._schema("Candidate")["properties"]
        self.assertEqual(cand["candidate_id"]["pattern"], dm._CANDIDATE_ID.pattern)
        inst = self._schema("Instantiation")["properties"]
        self.assertEqual(inst["instantiation_id"]["pattern"], dm._INSTANTIATION_ID.pattern)
        asmt = self._schema("CandidateGateAssessment")["properties"]
        self.assertEqual(asmt["assessment_id"]["pattern"], dm._ASSESSMENT_ID.pattern)
        self.assertEqual(asmt["gateset_id"]["pattern"], dm._GATESET_ID.pattern)


# --- 4. per-object accept / reject --------------------------------------

class CandidateTests(unittest.TestCase):
    def test_valid(self):
        c = make_candidate()
        self.assertEqual(c.level, "L04")
        self.assertEqual(c.parent_candidate_id, "")

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_candidate(candidate_id="CEACAM5")
        with self.assertRaises(ValueError):
            make_candidate(level="L99")
        with self.assertRaises(ValueError):
            make_candidate(status="DEAD")
        with self.assertRaises(ValueError):
            make_candidate(version=0)
        with self.assertRaises(ValueError):
            make_candidate(created_at="2026/08/28")
        with self.assertRaises(ValueError):
            make_candidate(provenance_ref="ADCdb/CEACAM5")
        with self.assertRaises(ValueError):
            make_candidate(parent_candidate_id="not-an-id")

    def test_has_no_context_or_verdict_field(self):
        names = {f.name for f in dataclasses.fields(Candidate)}
        self.assertEqual(names & set(dm.CANDIDATE_FORBIDDEN_FIELDS), set())


class ContextTests(unittest.TestCase):
    def test_valid_and_optional(self):
        c = make_context(provenance_ref="external:guidelines/nccn@2026", supersedes_version=1)
        self.assertEqual(c.context_version, 1)

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_context(context_id="crc-refractory")
        with self.assertRaises(ValueError):
            make_context(dimensions={})
        with self.assertRaises(ValueError):
            make_context(dimensions={"indication": 5})
        with self.assertRaises(ValueError):
            make_context(status="OPEN")
        with self.assertRaises(ValueError):
            make_context(provenance_ref="local:x")
        with self.assertRaises(ValueError):
            make_context(supersedes_version=0)

    def test_has_no_candidate_or_verdict_field(self):
        names = {f.name for f in dataclasses.fields(Context)}
        self.assertEqual(names & set(dm.CONTEXT_FORBIDDEN_FIELDS), set())


class EvidencePackageTests(unittest.TestCase):
    def test_valid(self):
        ep = make_evidence_package()
        self.assertEqual(ep.schema_version, 1)
        self.assertEqual(ep.supersedes_evidence_id, "")

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_evidence_package(evidence_id="EP-123")
        with self.assertRaises(ValueError):
            make_evidence_package(schema_version=0)
        with self.assertRaises(ValueError):
            make_evidence_package(measurement={"type": "IHC"})
        with self.assertRaises(ValueError):
            make_evidence_package(candidate_refs=("TARGET-X",))
        with self.assertRaises(ValueError):
            make_evidence_package(
                provenance={
                    "source_id": "SRC-1",
                    "source_type": "PMID",
                    "source_identifier": "1",
                    "locator": "x",
                    "retrieved_at": "2026-08-27",
                }
            )
        with self.assertRaises(ValueError):
            make_evidence_package(
                provenance={
                    "source_id": "SRC-00000881",
                    "source_type": "BLOG",
                    "source_identifier": "1",
                    "locator": "x",
                    "retrieved_at": "2026-08-27",
                }
            )
        with self.assertRaises(ValueError):
            make_evidence_package(supersedes_evidence_id="EP-1")

    def test_carries_no_grade(self):
        names = {f.name for f in dataclasses.fields(EvidencePackage)}
        self.assertEqual(names & set(dm.EVIDENCE_PACKAGE_FORBIDDEN_FIELDS), set())


class InstantiationTests(unittest.TestCase):
    def test_valid(self):
        i = make_instantiation()
        self.assertEqual(i.gateset_id, "ADC_TARGET_GATESET")

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_instantiation(instantiation_id="INST-CRC-ADC-TARGET")
        with self.assertRaises(ValueError):
            make_instantiation(gateset_id="ADC_TARGET")
        with self.assertRaises(ValueError):
            make_instantiation(evidence_regime="PRIVATE")
        with self.assertRaises(ValueError):
            make_instantiation(status="DONE")
        with self.assertRaises(ValueError):
            make_instantiation(candidate_level="L99")

    def test_is_not_a_seventh_core_object(self):
        names = {f.name for f in dataclasses.fields(Instantiation)}
        self.assertEqual(names & set(dm.INSTANTIATION_FORBIDDEN_FIELDS), set())


# --- 5. direction x strength matrix ------------------------------------

class DirectionStrengthMatrixTests(unittest.TestCase):
    def test_positive_negative_need_grade_and_evidence(self):
        self.assertEqual(make_assessment(direction="NEGATIVE", strength="DIRECT").direction, "NEGATIVE")
        with self.assertRaises(ValueError):
            make_assessment(direction="POSITIVE", strength="UNKNOWN")
        with self.assertRaises(ValueError):
            make_assessment(direction="POSITIVE", strength="DIRECT", evidence_refs=())

    def test_conflicting_needs_both_sides_and_key_arrays(self):
        ok = make_assessment(
            direction="CONFLICTING",
            strength="DIRECT",
            evidence_refs=(
                EvidenceRef("EP-00000123", "SUPPORTING"),
                EvidenceRef("EP-00000140", "CONTRADICTING"),
            ),
            key_supporting_evidence=({"ref": "EP-00000123"},),
            key_contradicting_evidence=({"ref": "EP-00000140"},),
        )
        self.assertEqual(ok.direction, "CONFLICTING")
        with self.assertRaises(ValueError):  # only one side
            make_assessment(
                direction="CONFLICTING",
                strength="DIRECT",
                evidence_refs=(EvidenceRef("EP-00000123", "SUPPORTING"),),
                key_supporting_evidence=({"ref": "EP-00000123"},),
                key_contradicting_evidence=({"ref": "EP-00000140"},),
            )
        with self.assertRaises(ValueError):  # missing key arrays
            make_assessment(
                direction="CONFLICTING",
                strength="DIRECT",
                evidence_refs=(
                    EvidenceRef("EP-00000123", "SUPPORTING"),
                    EvidenceRef("EP-00000140", "CONTRADICTING"),
                ),
            )
        with self.assertRaises(ValueError):  # strength UNKNOWN under CONFLICTING
            make_assessment(
                direction="CONFLICTING",
                strength="UNKNOWN",
                evidence_refs=(
                    EvidenceRef("EP-00000123", "SUPPORTING"),
                    EvidenceRef("EP-00000140", "CONTRADICTING"),
                ),
                key_supporting_evidence=({"ref": "EP-00000123"},),
                key_contradicting_evidence=({"ref": "EP-00000140"},),
            )

    def test_inconclusive_two_shapes(self):
        unknown_state = make_assessment(
            direction="INCONCLUSIVE", strength="UNKNOWN", evidence_refs=()
        )
        self.assertEqual(unknown_state.strength, "UNKNOWN")
        qualified = make_assessment(direction="INCONCLUSIVE", strength="WEAK")
        self.assertEqual(qualified.strength, "WEAK")
        with self.assertRaises(ValueError):  # UNKNOWN but has evidence
            make_assessment(
                direction="INCONCLUSIVE",
                strength="UNKNOWN",
                evidence_refs=(EvidenceRef("EP-00000123", "CONTEXTUAL"),),
            )

    def test_not_applicable_is_strict(self):
        na = make_assessment(direction="NOT_APPLICABLE", strength="UNKNOWN", evidence_refs=())
        self.assertEqual(na.direction, "NOT_APPLICABLE")
        with self.assertRaises(ValueError):
            make_assessment(direction="NOT_APPLICABLE", strength="DIRECT", evidence_refs=())

    def test_review_status_must_be_human_approved(self):
        with self.assertRaises(ValueError):
            make_assessment(
                review={"status": "MACHINE_PROPOSED", "reviewer": "bot", "reviewed_at": "2026-08-27"}
            )

    def test_bad_critical_unknown_resolution(self):
        with self.assertRaises(ValueError):
            make_assessment(
                critical_unknowns=({"unknown": "x", "resolution": "MAYBE_LATER"},)
            )

    def test_assessment_carries_no_decision_or_score(self):
        names = {f.name for f in dataclasses.fields(CandidateGateAssessment)}
        self.assertEqual(names & set(dm.ASSESSMENT_FORBIDDEN_FIELDS), set())


class EvidenceRefTests(unittest.TestCase):
    def test_accept_reject(self):
        self.assertEqual(EvidenceRef("EP-00000123", "SUPPORTING").role, "SUPPORTING")
        with self.assertRaises(ValueError):
            EvidenceRef("EP-123", "SUPPORTING")
        with self.assertRaises(ValueError):
            EvidenceRef("EP-00000123", "NEUTRAL")


# --- 6. legacy path retained + crosswalk --------------------------------

class LegacyRetainedTests(unittest.TestCase):
    def test_core_object_types_unchanged(self):
        self.assertEqual(
            CORE_OBJECT_TYPES,
            (
                "Opportunity",
                "ClinicalHypothesis",
                "TargetHypothesis",
                "BinderCandidate",
                "ADCConstruct",
                "LeadSeries",
                "DevelopmentCandidate",
                "Asset",
            ),
        )
        self.assertEqual(CoreObject("Opportunity", "x", "1.0").object_type, "Opportunity")

    def test_crosswalk_covers_exactly_the_legacy_registry(self):
        self.assertEqual(set(LEGACY_CROSSWALK), set(CORE_OBJECT_TYPES))

    def test_one_to_one_entries_are_the_three_clean_candidates(self):
        self.assertEqual(
            set(ONE_TO_ONE_LEGACY_TYPES),
            {"TargetHypothesis", "BinderCandidate", "DevelopmentCandidate"},
        )
        self.assertEqual(LEGACY_CROSSWALK["TargetHypothesis"].candidate_type, "ADC_TARGET")
        self.assertEqual(LEGACY_CROSSWALK["TargetHypothesis"].level, "L04")
        self.assertEqual(LEGACY_CROSSWALK["BinderCandidate"].level, "L06")
        self.assertEqual(LEGACY_CROSSWALK["DevelopmentCandidate"].level, "L13")

    def test_adapt_one_to_one(self):
        legacy = CoreObject("TargetHypothesis", "external:legacy/th/1", "1.0")
        cand = adapt_core_object_to_candidate(
            legacy,
            candidate_id="CAND-L04-000001",
            canonical_name="CEACAM5",
            created_at="2026-08-28",
            provenance_ref="external:legacy/th/1",
        )
        self.assertIsInstance(cand, Candidate)
        self.assertEqual((cand.candidate_type, cand.level), ("ADC_TARGET", "L04"))

    def test_adapt_composites_and_wrappers_raise(self):
        for legacy_type in ("Opportunity", "ClinicalHypothesis", "ADCConstruct", "LeadSeries", "Asset"):
            with self.subTest(legacy_type=legacy_type):
                legacy = CoreObject(legacy_type, "x", "1.0")
                with self.assertRaises(NotImplementedError):
                    adapt_core_object_to_candidate(
                        legacy,
                        candidate_id="CAND-L04-000001",
                        canonical_name="x",
                        created_at="2026-08-28",
                        provenance_ref="external:legacy/x",
                    )

    def test_crosswalk_matches_contract_prose_dispositions(self):
        expected = {
            "Opportunity": "wrapper",
            "ClinicalHypothesis": "composite",
            "TargetHypothesis": "candidate",
            "BinderCandidate": "candidate",
            "ADCConstruct": "composite",
            "LeadSeries": "composite",
            "DevelopmentCandidate": "candidate",
            "Asset": "non_candidate",
        }
        got = {k: v.disposition for k, v in LEGACY_CROSSWALK.items()}
        self.assertEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
