"""Runtime Migration PR B: the two-rule-layer Gate system contracts.

Asserts:
* the ``src/contracts/gate_contracts.yaml`` registry and the
  ``src/objects/gate_model.py`` dataclasses agree;
* ``Decision`` is a byte-for-byte mirror of the frozen
  ``src/contracts/data_layout/decision.schema.json``;
* ``Gate`` / ``GateSet`` stay consistent with the frozen disk binding schema
  ``src/contracts/data_layout/gate_binding.schema.yaml`` where they overlap;
* the legacy 45-gate topology and ``GateModelOutput`` are untouched;
* deep immutability holds, exactly as in PR A.
"""

import dataclasses
import json
import unittest
from pathlib import Path

import yaml

from src.capabilities.gates import GATE_CATALOG, GATE_GROUPS, GATE_IDS, GateModelOutput
from src.objects import gate_model as gm
from src.objects.decision_model import CANDIDATE_LEVELS, CANONICAL_REVIEW_STATUS
from src.objects.gate_model import (
    CANONICAL_GATESET_IDS,
    DECISION_VALUES,
    DOMINANT_EVIDENCE_REGIMES,
    LADDER_GRADES,
    Decision,
    EvidenceLadder,
    Gate,
    GateSet,
    GateSetMember,
    LadderRung,
    TriggeredBy,
)
from src.objects.legacy_gate_map import (
    LEGACY_GATE_SYSTEM,
    LEGACY_GATECHAIN_CROSSWALK,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "gate_contracts.yaml"
DATA_LAYOUT = ROOT / "src" / "contracts" / "data_layout"


def _load(path: Path):
    text = path.read_text()
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def _required_dataclass_fields(cls) -> set[str]:
    return {
        f.name
        for f in dataclasses.fields(cls)
        if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
    }


# --- valid instance factories -------------------------------------------

def make_ladder(**overrides) -> EvidenceLadder:
    base = dict(
        gate_id="TGT-04",
        gate_version="1.0",
        rungs=(
            LadderRung("DIRECT", ("quantitative surface density",), "establishes density"),
            LadderRung("INDIRECT_STRONG", ("IHC membranous",), "surface plausibility only"),
            LadderRung("WEAK", ("bulk RNA expression",), "no surface claim"),
        ),
        evidence_ceiling="quantitative antigen density",
    )
    base.update(overrides)
    return EvidenceLadder(**base)


def make_gate(**overrides) -> Gate:
    base = dict(
        gate_id="TGT-04",
        gate_version="1.0",
        gateset_id="ADC_TARGET_GATESET",
        candidate_level="L04",
        gate_question="Is quantitative surface antigen density adequate for an ADC?",
        dominant_evidence_regime="PUBLIC_HYBRID",
        evidence_required=("surface proteomics", "quantitative IHC"),
        evidence_ladder_ref="external:ladder/TGT-04@v1",
        assessment_rule_ref="external:rule/TGT-04@v1",
        primary_module_id="MOD-TGT04",
        primary_module_version="0.1.0",
    )
    base.update(overrides)
    return Gate(**base)


def make_gateset(**overrides) -> GateSet:
    base = dict(
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        candidate_level="L04",
        gates=(GateSetMember("TGT-04", "1.0"), GateSetMember("TGT-05", "1.0")),
        decision_rule_ref="external:gs/ADC_TARGET_GATESET/decision_rule@v1",
        fatal_gate_policy_ref="external:gs/ADC_TARGET_GATESET/fatal@v1",
        required_gate_policy_ref="external:gs/ADC_TARGET_GATESET/required@v1",
        unknown_policy_ref="external:gs/ADC_TARGET_GATESET/unknown@v1",
    )
    base.update(overrides)
    return GateSet(**base)


_REVIEW = {"status": "HUMAN_APPROVED", "reviewer": "human", "reviewed_at": "2026-08-27"}


def make_decision(**overrides) -> Decision:
    base = dict(
        decision_id="DEC-0001",
        instantiation_id="INST-CRC-REFRACTORY-ADC-TARGET-v1",
        candidate_id="CAND-L04-000001",
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        decision="MORE_EVIDENCE",
        triggered_by=(TriggeredBy("TGT-04", "ASMT-000001", 1, "density EXPERIMENT_REQUIRED"),),
        assessment_snapshot={
            "TGT-04": {"assessment_id": "ASMT-000001", "assessment_version": 1, "cell": "POSITIVE/INDIRECT_STRONG"},
            "TGT-01": "NOT_EVALUATED",
        },
        decision_rule_ref="external:gateset/ADC_TARGET_GATESET/decision_rule@v1",
        review=dict(_REVIEW),
    )
    base.update(overrides)
    return Decision(**base)


# --- 1. contract YAML shape --------------------------------------------

class ContractRegistryTests(unittest.TestCase):
    def setUp(self):
        self.doc = _load(CONTRACT_PATH)

    def test_version_and_contract_set(self):
        self.assertEqual(self.doc["version"], "0.1.0")
        self.assertEqual(
            set(self.doc["contracts"]),
            {"EvidenceLadder", "Gate", "GateSet", "Decision"},
        )
        for name, body in self.doc["contracts"].items():
            self.assertEqual(body["contract_id"], f"{name}@0.1.0")

    def test_migration_block_defers_engine_and_concrete_content(self):
        migration = self.doc["migration"]
        self.assertEqual(migration["pr"], "runtime_migration_pr_b")
        self.assertIn("decision_engine", migration["deferred"])
        self.assertIn("concrete_evidence_ladders", migration["deferred"])
        self.assertTrue(self.doc["repository_policy"]["decision_engine_in_repository"] == "forbidden"
                        or self.doc["repository_policy"]["decision_engine_in_repository"] is False)

    def test_crc_specialization_is_not_a_new_gateset_id(self):
        deferred = self.doc["migration"]["deferred"]
        self.assertIn("crc_adc_target_specialization_of_ADC_TARGET_GATESET", deferred)
        self.assertNotIn("concrete_gateset_CRC_ADC_TARGET_GATESET_v1", deferred)
        text = deferred["crc_adc_target_specialization_of_ADC_TARGET_GATESET"]
        self.assertIn("NOT a new canonical gateset_id", text)

    def test_legacy_block_marks_frozen(self):
        legacy = self.doc["legacy_gate_system"]
        self.assertEqual(legacy["gate_count"], 45)
        self.assertEqual(legacy["status"], "FROZEN_LEGACY")


# --- 2. registry <-> Python parity ------------------------------------

_CONTRACT_TO_CLASS = {
    "EvidenceLadder": EvidenceLadder,
    "Gate": Gate,
    "GateSet": GateSet,
    "Decision": Decision,
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
        self.assertEqual(tuple(v["decision_values"]), DECISION_VALUES)
        self.assertEqual(
            tuple(v["dominant_evidence_regimes"]), DOMINANT_EVIDENCE_REGIMES
        )
        self.assertEqual(tuple(v["ladder_grades"]), LADDER_GRADES)
        self.assertEqual(v["assessment_snapshot_cell_regex"], gm._CELL.pattern)
        self.assertEqual(
            {k: v2 for k, v2 in v["canonical_gateset_ids"].items()},
            dict(CANONICAL_GATESET_IDS),
        )

    def test_decision_forbidden_fields_match(self):
        self.assertEqual(
            set(self.doc["contracts"]["Decision"]["forbidden_fields"]),
            set(gm.DECISION_FORBIDDEN_FIELDS),
        )


# --- 3. Decision exact parity with decision.schema.json --------------

class DecisionSchemaParityTests(unittest.TestCase):
    def setUp(self):
        self.schema = _load(DATA_LAYOUT / "decision.schema.json")

    def test_required_array_matches(self):
        self.assertEqual(
            set(self.schema["required"]), _required_dataclass_fields(Decision)
        )

    def test_decision_enum_matches(self):
        self.assertEqual(
            tuple(self.schema["properties"]["decision"]["enum"]), DECISION_VALUES
        )

    def test_triggered_by_shape_matches(self):
        item = self.schema["properties"]["triggered_by"]["items"]
        self.assertFalse(item["additionalProperties"])
        self.assertEqual(
            set(item["required"]), _required_dataclass_fields(TriggeredBy)
        )
        self.assertEqual(
            set(item["properties"]), _required_dataclass_fields(TriggeredBy)
        )

    def test_assessment_snapshot_oneof_shape_matches(self):
        oneof = self.schema["properties"]["assessment_snapshot"]["additionalProperties"]["oneOf"]
        consts = [b for b in oneof if b.get("const") == "NOT_EVALUATED"]
        objs = [b for b in oneof if b.get("type") == "object"]
        self.assertEqual(len(consts), 1)
        self.assertEqual(len(objs), 1)
        self.assertFalse(objs[0]["additionalProperties"])
        self.assertEqual(set(objs[0]["required"]), set(gm._SNAPSHOT_REF_KEYS))
        self.assertEqual(objs[0]["properties"]["cell"]["pattern"], gm._CELL.pattern)

    def test_review_closed_and_human_approved(self):
        review = self.schema["properties"]["review"]
        self.assertFalse(review["additionalProperties"])
        self.assertEqual(set(review["properties"]), set(gm._REVIEW_KEYS))
        self.assertEqual(review["properties"]["status"]["const"], CANONICAL_REVIEW_STATUS)

    def test_not_anyof_and_additionalproperties(self):
        forbidden = {e["required"][0] for e in self.schema["not"]["anyOf"]}
        self.assertEqual(forbidden, set(gm.DECISION_FORBIDDEN_FIELDS))
        self.assertFalse(self.schema["additionalProperties"])
        declared = {f.name for f in dataclasses.fields(Decision)}
        self.assertEqual(declared & set(gm.DECISION_FORBIDDEN_FIELDS), set())

    def test_id_patterns_match(self):
        props = self.schema["properties"]
        self.assertEqual(props["decision_id"]["pattern"], gm._DECISION_ID.pattern)
        self.assertEqual(
            props["supersedes_decision_id"]["pattern"], gm._DECISION_ID.pattern
        )
        self.assertEqual(
            props["triggered_by"]["items"]["properties"]["assessment_id"]["pattern"],
            gm._ASSESSMENT_ID.pattern,
        )


# --- 4. Gate / GateSet consistency with the disk binding schema ------

class GateBindingConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.binding = _load(DATA_LAYOUT / "gate_binding.schema.yaml")
        self.gate_binding = self.binding["$defs"]["gate_binding"]["properties"]
        self.gateset_binding = self.binding["$defs"]["gateset_binding"]

    def test_shared_enums_and_patterns_agree(self):
        self.assertEqual(
            tuple(self.gate_binding["dominant_evidence_regime"]["enum"]),
            DOMINANT_EVIDENCE_REGIMES,
        )
        self.assertEqual(
            self.gate_binding["gateset_id"]["pattern"], gm._GATESET_ID.pattern
        )
        self.assertEqual(
            self.gate_binding["primary_module_id"]["pattern"], gm._MODULE_ID.pattern
        )
        self.assertEqual(
            tuple(self.gate_binding["candidate_level"]["enum"]), CANDIDATE_LEVELS
        )

    def test_disk_gateset_policy_refs_are_a_subset_of_the_contract(self):
        disk_required = set(self.gateset_binding["required"])
        disk_policy_refs = {r for r in disk_required if r.endswith("_ref")}
        self.assertEqual(
            disk_policy_refs,
            {"decision_rule_ref", "fatal_gate_policy_ref", "required_gate_policy_ref"},
        )
        self.assertTrue(disk_policy_refs <= _required_dataclass_fields(GateSet))
        # the contract adds the fourth policy ref from CURRENT_SYSTEM v5 6.1
        self.assertIn("unknown_policy_ref", _required_dataclass_fields(GateSet))


# --- 5. per-object accept / reject ------------------------------------

class EvidenceLadderTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual([r.grade for r in make_ladder().rungs], list(LADDER_GRADES))

    def test_rungs_must_be_exact_order(self):
        with self.assertRaises(ValueError):
            make_ladder(
                rungs=(
                    LadderRung("WEAK", ("x",), "c"),
                    LadderRung("DIRECT", ("y",), "c"),
                    LadderRung("INDIRECT_STRONG", ("z",), "c"),
                )
            )
        with self.assertRaises(ValueError):
            make_ladder(rungs=(LadderRung("DIRECT", ("x",), "c"),))

    def test_rung_rejects(self):
        with self.assertRaises(ValueError):
            LadderRung("STRONG", ("x",), "c")
        with self.assertRaises(ValueError):
            LadderRung("DIRECT", (), "c")
        with self.assertRaises(ValueError):
            LadderRung("DIRECT", ("x",), "")
        with self.assertRaises(ValueError):
            LadderRung("DIRECT", ("",), "c")


class GateTests(unittest.TestCase):
    def test_valid(self):
        g = make_gate()
        self.assertEqual(g.fatal_conditions, ())

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_gate(gateset_id="ADC_TARGET")
        with self.assertRaises(ValueError):
            make_gate(dominant_evidence_regime="PUBLIC")
        with self.assertRaises(ValueError):
            make_gate(candidate_level="L99")
        with self.assertRaises(ValueError):
            make_gate(evidence_required=())
        with self.assertRaises(ValueError):
            make_gate(evidence_ladder_ref="ladder/TGT-04")
        with self.assertRaises(ValueError):
            make_gate(primary_module_id="MODULE-TGT04")

    def test_has_no_score_field(self):
        self.assertNotIn("score", {f.name for f in dataclasses.fields(Gate)})

    def test_gateset_id_must_be_canonical_for_the_level(self):
        with self.assertRaises(ValueError):  # ADC_TARGET_GATESET is L04, not L05
            make_gate(candidate_level="L05")
        with self.assertRaises(ValueError):  # wrong canonical id for L04
            make_gate(gateset_id="ADC_EPITOPE_GATESET")
        # the canonical pairing for L05 is fine
        g = make_gate(candidate_level="L05", gateset_id="ADC_EPITOPE_GATESET")
        self.assertEqual(g.candidate_level, "L05")


class GateSetTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(len(make_gateset().gates), 2)

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_gateset(gates=())
        with self.assertRaises(ValueError):
            make_gateset(gateset_id="adc_target_gateset")
        with self.assertRaises(ValueError):
            make_gateset(candidate_level="L99")
        with self.assertRaises(ValueError):
            make_gateset(unknown_policy_ref="gs/unknown")

    def test_gateset_id_must_be_canonical_for_the_level(self):
        with self.assertRaises(ValueError):
            make_gateset(candidate_level="L05")  # id is ADC_TARGET_GATESET (L04)
        ok = make_gateset(candidate_level="L05", gateset_id="ADC_EPITOPE_GATESET")
        self.assertEqual(ok.gateset_id, "ADC_EPITOPE_GATESET")

    def test_member_gate_ids_must_be_unique(self):
        with self.assertRaises(ValueError):
            make_gateset(gates=(GateSetMember("TGT-04", "1.0"), GateSetMember("TGT-04", "2.0")))

    def test_has_no_decision_policy_body(self):
        # only *_ref fields, never an inline policy body
        names = {f.name for f in dataclasses.fields(GateSet)}
        self.assertTrue(all(
            n.endswith("_ref") or n in {"gateset_id", "gateset_version", "candidate_level", "gates"}
            for n in names
        ))


class DecisionTests(unittest.TestCase):
    def test_valid(self):
        d = make_decision()
        self.assertEqual(d.decision, "MORE_EVIDENCE")
        self.assertEqual(d.supersedes_decision_id, "")

    def test_rejects(self):
        with self.assertRaises(ValueError):
            make_decision(decision_id="DEC-1")
        with self.assertRaises(ValueError):
            make_decision(decision="PROCEED")
        with self.assertRaises(ValueError):
            make_decision(gateset_id="ADC_TARGET")
        with self.assertRaises(ValueError):
            make_decision(review={"status": "MACHINE_PROPOSED", "reviewer": "b", "reviewed_at": "2026-08-27"})
        with self.assertRaises(ValueError):
            make_decision(review={"status": "HUMAN_APPROVED", "reviewer": "", "reviewed_at": "2026-08-27"})
        with self.assertRaises(ValueError):
            make_decision(supersedes_decision_id="DEC-1")

    def test_triggered_by_rejects(self):
        with self.assertRaises(ValueError):
            TriggeredBy("TGT-04", "ASMT-1", 1, "r")
        with self.assertRaises(ValueError):
            TriggeredBy("TGT-04", "ASMT-000001", 0, "r")

    def test_assessment_snapshot_shapes(self):
        d = make_decision(triggered_by=(), assessment_snapshot={"TGT-01": "NOT_EVALUATED"})
        self.assertEqual(d.assessment_snapshot["TGT-01"], "NOT_EVALUATED")
        with self.assertRaises(ValueError):  # bad cell
            make_decision(triggered_by=(), assessment_snapshot={
                "TGT-04": {"assessment_id": "ASMT-000001", "assessment_version": 1, "cell": "GOOD"}
            })
        with self.assertRaises(ValueError):  # extra key in ref
            make_decision(triggered_by=(), assessment_snapshot={
                "TGT-04": {"assessment_id": "ASMT-000001", "assessment_version": 1, "cell": "UNKNOWN", "x": 1}
            })
        with self.assertRaises(ValueError):  # bad assessment_id
            make_decision(triggered_by=(), assessment_snapshot={
                "TGT-04": {"assessment_id": "ASMT-1", "assessment_version": 1, "cell": "UNKNOWN"}
            })
        with self.assertRaises(ValueError):  # version 0
            make_decision(triggered_by=(), assessment_snapshot={
                "TGT-04": {"assessment_id": "ASMT-000001", "assessment_version": 0, "cell": "UNKNOWN"}
            })
        # accepts the NOT_APPLICABLE / UNKNOWN cell literals
        ok = make_decision(triggered_by=(), assessment_snapshot={
            "TGT-08": {"assessment_id": "ASMT-000008", "assessment_version": 2, "cell": "NOT_APPLICABLE"}
        })
        self.assertEqual(ok.assessment_snapshot["TGT-08"]["cell"], "NOT_APPLICABLE")

    def test_gateset_id_must_be_canonical_for_the_candidate_level(self):
        with self.assertRaises(ValueError):
            make_decision(candidate_id="CAND-L05-000001")  # id stays ADC_TARGET_GATESET
        ok = make_decision(
            candidate_id="CAND-L05-000001",
            gateset_id="ADC_EPITOPE_GATESET",
            triggered_by=(),
            assessment_snapshot={"EPI-01": "NOT_EVALUATED"},
        )
        self.assertEqual(ok.gateset_id, "ADC_EPITOPE_GATESET")


# --- 5b. Decision triggered_by <-> assessment_snapshot provenance ----

class DecisionProvenanceConsistencyTests(unittest.TestCase):
    def test_trigger_gate_absent_from_snapshot_is_invalid(self):
        with self.assertRaises(ValueError):
            make_decision(triggered_by=(TriggeredBy("TGT-99", "ASMT-000001", 1, "r"),))

    def test_trigger_gate_not_evaluated_in_snapshot_is_invalid(self):
        with self.assertRaises(ValueError):
            make_decision(triggered_by=(TriggeredBy("TGT-01", "ASMT-000001", 1, "r"),))

    def test_trigger_assessment_id_or_version_must_match_the_snapshot_pin(self):
        with self.assertRaises(ValueError):  # id mismatch
            make_decision(triggered_by=(TriggeredBy("TGT-04", "ASMT-000009", 1, "r"),))
        with self.assertRaises(ValueError):  # version mismatch
            make_decision(triggered_by=(TriggeredBy("TGT-04", "ASMT-000001", 3, "r"),))

    def test_snapshot_may_hold_gates_not_in_triggered_by(self):
        d = make_decision(
            triggered_by=(TriggeredBy("TGT-04", "ASMT-000001", 1, "decisive"),),
            assessment_snapshot={
                "TGT-04": {"assessment_id": "ASMT-000001", "assessment_version": 1, "cell": "POSITIVE/INDIRECT_STRONG"},
                "TGT-05": {"assessment_id": "ASMT-000005", "assessment_version": 2, "cell": "CONFLICTING/DIRECT"},
                "TGT-08": "NOT_EVALUATED",
            },
        )
        self.assertEqual(len(d.assessment_snapshot), 3)
        self.assertEqual(len(d.triggered_by), 1)


# --- 5c. persistence-shape parity vs runtime tightening -------------

class SchemaRuntimeRelationshipTests(unittest.TestCase):
    def test_contract_declares_the_true_relationship_not_exact_parity(self):
        doc = _load(CONTRACT_PATH)["migration"]["parity"]["Decision"]
        self.assertEqual(doc["kind"], "schema_shape_exact_runtime_semantics_stricter")
        self.assertIn("relationship", doc)
        self.assertIn("rule", doc)
        self.assertNotEqual(doc["kind"], "exact")

    def test_runtime_is_a_strict_subset_of_schema_valid(self):
        schema = _load(DATA_LAYOUT / "decision.schema.json")
        # schema-valid: assessment_snapshot has no minProperties, so {} is allowed
        self.assertNotIn("minProperties", schema["properties"]["assessment_snapshot"])
        # runtime-invalid: the object rejects an empty snapshot
        with self.assertRaises(ValueError):
            make_decision(triggered_by=(), assessment_snapshot={})
        # schema-valid: gateset_version is just a string (empty passes the schema)
        self.assertEqual(schema["properties"]["gateset_version"]["type"], "string")
        with self.assertRaises(ValueError):
            make_decision(gateset_version="")

    def test_gateset_identity_block_present_and_canonical(self):
        block = _load(CONTRACT_PATH)["gateset_identity"]
        self.assertIn("canonical", block["rule"].lower())
        self.assertIn("member_uniqueness", block)
        self.assertEqual(
            block["candidate_level_source"]["Decision"],
            "parsed from candidate_id (CAND-Lnn-nnnnnn -> Lnn)",
        )


# --- 6. deep immutability -------------------------------------------

class DeepImmutabilityTests(unittest.TestCase):
    def test_external_dict_mutation_does_not_reach_decision(self):
        review = {"status": "HUMAN_APPROVED", "reviewer": "human", "reviewed_at": "2026-08-27"}
        d = make_decision(review=review)
        review["status"] = "MACHINE_PROPOSED"
        self.assertEqual(d.review["status"], "HUMAN_APPROVED")

        snap = {"TGT-04": {"assessment_id": "ASMT-000001", "assessment_version": 1, "cell": "UNKNOWN"}}
        d2 = make_decision(assessment_snapshot=snap)
        snap["TGT-04"]["cell"] = "POSITIVE/DIRECT"
        self.assertEqual(d2.assessment_snapshot["TGT-04"]["cell"], "UNKNOWN")

    def test_nested_values_cannot_be_mutated_through_the_object(self):
        d = make_decision()
        with self.assertRaises(TypeError):
            d.review["status"] = "x"
        with self.assertRaises(TypeError):
            d.assessment_snapshot["TGT-04"]["cell"] = "x"

    def test_module_maps_are_read_only(self):
        with self.assertRaises(TypeError):
            CANONICAL_GATESET_IDS["L04"] = "X"
        with self.assertRaises(TypeError):
            LEGACY_GATECHAIN_CROSSWALK["target_opportunity"] = None


# --- 7. legacy 45-gate topology untouched ---------------------------

class LegacyTopologyUntouchedTests(unittest.TestCase):
    def test_kernel_still_has_45_gates_in_three_groups(self):
        self.assertEqual(len(GATE_IDS), 45)
        self.assertEqual(
            GATE_GROUPS,
            ("target_opportunity", "product_realization", "commercial_executability"),
        )
        counts: dict[str, int] = {}
        for d in GATE_CATALOG:
            counts[d.group] = counts.get(d.group, 0) + 1
        self.assertEqual(counts, {"target_opportunity": 13, "product_realization": 16, "commercial_executability": 16})

    def test_gate_system_yaml_unchanged(self):
        doc = _load(ROOT / "src" / "contracts" / "gate_system.yaml")
        self.assertEqual(doc["contract"]["topology"]["gate_count"], 45)
        self.assertEqual(doc["contract"]["topology"]["architecture_version"], "0.2.0")
        self.assertEqual(
            doc["contract"]["topology"]["topology_change_policy"],
            "frozen_until_explicit_unfreeze",
        )

    def test_legacy_gatemodel_output_still_has_score(self):
        names = {f.name for f in dataclasses.fields(GateModelOutput)}
        self.assertIn("score", names)
        self.assertIn("status", names)

    def test_legacy_gate_system_descriptor_matches_kernel(self):
        self.assertEqual(LEGACY_GATE_SYSTEM.gate_count, len(GATE_IDS))
        self.assertEqual(LEGACY_GATE_SYSTEM.status, "FROZEN_LEGACY")
        self.assertEqual(set(LEGACY_GATECHAIN_CROSSWALK), set(GATE_GROUPS))
        for chain, entry in LEGACY_GATECHAIN_CROSSWALK.items():
            self.assertLessEqual(
                set(entry.canonical_gatesets), set(CANONICAL_GATESET_IDS.values())
            )

    def test_gatechain_crosswalk_matches_contract_yaml(self):
        doc = _load(CONTRACT_PATH)["legacy_gatechain_crosswalk"]["entries"]
        for chain, entry in LEGACY_GATECHAIN_CROSSWALK.items():
            self.assertEqual(
                tuple(doc[chain]["canonical_gatesets"]), entry.canonical_gatesets
            )
            self.assertEqual(doc[chain]["legacy_gate_count"], entry.legacy_gate_count)


# --- 8. canonical gateset ids -------------------------------------

class CanonicalGateSetIdsTests(unittest.TestCase):
    def test_one_per_level_and_well_formed(self):
        self.assertEqual(set(CANONICAL_GATESET_IDS), set(CANDIDATE_LEVELS))
        for gsid in CANONICAL_GATESET_IDS.values():
            self.assertRegex(gsid, gm._GATESET_ID.pattern)
        self.assertEqual(CANONICAL_GATESET_IDS["L04"], "ADC_TARGET_GATESET")


if __name__ == "__main__":
    unittest.main()
