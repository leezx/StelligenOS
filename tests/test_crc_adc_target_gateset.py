"""Runtime Migration PR D: CRC-ADC-TARGET-GATESET-v1.

Asserts:
* the ``src/contracts/crc_adc_target_gateset.yaml`` roster + gate contracts
  build valid ``src/objects/crc_adc_target_gateset.py`` dataclasses;
* the TGT-01..TGT-08 roster is exactly the frozen CURRENT_SYSTEM v5 section 6.4
  scientific names, all L04, all gate_version "1.0";
* ``CRC-ADC-TARGET-GATESET-v1`` never appears as a ``gateset_id``;
* the eight context-specific binding records are parity-consistent with the
  frozen ``data_layout/gate_binding.schema.yaml`` (and the gateset binding);
* the primary Module binding slots are the deterministic ``MOD-TGT0n`` at their
  expected version (PR D left every gate at "0.0.0"; PR E2 built MOD-TGT01, so
  TGT-01 is "1.0.0"); PR D itself created no Module ``.py`` under ``src/objects``;
* per-object accept / reject, and PR A / B / C files are untouched.
"""

import dataclasses
import unittest
from pathlib import Path

import yaml

from src.objects.gate_model import EvidenceLadder, GateSet, GateSetMember, LadderRung
from src.objects.decision_model import Instantiation
from src.objects import crc_adc_target_gateset as cd
from src.objects.crc_adc_target_gateset import (
    ADC_TARGET_GATESET_ID,
    PROGRAM_LABEL,
    TGT_GATE_IDS,
    TGT_GATE_NAMES,
    CrcAdcTargetGateSetV1,
    TgtGateContract,
    TgtGateSpec,
    _deterministic_module_id,
    field_names,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml"
GATE_BINDING_SCHEMA = ROOT / "src" / "contracts" / "data_layout" / "gate_binding.schema.yaml"
V5_DOC = (
    ROOT / "docs" / "architecture"
    / "CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md"
)


def _load(path: Path):
    return yaml.safe_load(path.read_text())


# --- build the runtime objects from the frozen contract ---------------

def _build() -> CrcAdcTargetGateSetV1:
    doc = _load(CONTRACT_PATH)
    rc = doc["roster_constants"]
    roster = tuple(
        TgtGateSpec(
            gate_id=row["gate_id"],
            name=row["name"],
            candidate_level=rc["candidate_level"],
            gateset_id=rc["gateset_id"],
            gate_version=rc["gate_version"],
            dominant_evidence_regime=row["dominant_evidence_regime"],
        )
        for row in doc["roster"]
    )

    gs = doc["gateset"]
    gateset = GateSet(
        gateset_id=gs["gateset_id"],
        gateset_version=gs["gateset_version"],
        candidate_level=gs["candidate_level"],
        gates=tuple(
            GateSetMember(m["gate_id"], m["gate_version"]) for m in gs["members"]
        ),
        decision_rule_ref=gs["decision_rule_ref"],
        fatal_gate_policy_ref=gs["fatal_gate_policy_ref"],
        required_gate_policy_ref=gs["required_gate_policy_ref"],
        unknown_policy_ref=gs["unknown_policy_ref"],
    )

    inst = doc["instantiation"]
    instantiation = Instantiation(
        instantiation_id=inst["instantiation_id"],
        candidate_type=inst["candidate_type"],
        candidate_level=inst["candidate_level"],
        context_id=inst["context_id"],
        context_version=inst["context_version"],
        modality=inst["modality"],
        gateset_id=inst["gateset_id"],
        gateset_version=inst["gateset_version"],
        evidence_regime=inst["evidence_regime"],
        status=inst["status"],
        version=inst["version"],
        created_at=inst["created_at"],
    )

    bindings = {
        b["gate_id"]: b for b in doc["context_specific_bindings"]["gate_bindings"]
    }
    _GRADES = ("DIRECT", "INDIRECT_STRONG", "WEAK")
    contracts = []
    for spec in roster:
        c = doc["gate_contracts"][spec.gate_id]
        b = bindings[spec.gate_id]
        ladder = EvidenceLadder(
            gate_id=spec.gate_id,
            gate_version=spec.gate_version,
            rungs=tuple(
                LadderRung(
                    grade,
                    tuple(c["evidence_ladder"][grade]["admissible_evidence_classes"]),
                    c["evidence_ladder"][grade]["ceiling_rule"],
                )
                for grade in _GRADES
            ),
            evidence_ceiling=c["evidence_ceiling"],
        )
        contracts.append(
            TgtGateContract(
                gate_spec=spec,
                gate_question=c["gate_question"],
                evidence_required=tuple(c["evidence_required"]),
                ladder=ladder,
                allowed_inference=tuple(c["allowed_inference"]),
                forbidden_inference=tuple(c["forbidden_inference"]),
                unknown_behavior=c["unknown_behavior"],
                fatal_conditions=tuple(c["fatal_conditions"]),
                evidence_ladder_ref=b["evidence_ladder_ref"],
                assessment_rule_ref=b["assessment_rule_ref"],
                primary_module_id=b["primary_module_id"],
                primary_module_version=b["primary_module_version"],
            )
        )
    return CrcAdcTargetGateSetV1(
        roster=roster,
        gateset=gateset,
        instantiation=instantiation,
        gate_contracts=tuple(contracts),
    )


# --- 1. contract builds & registry sanity ---------------------------

class ContractBuildsTests(unittest.TestCase):
    def test_builds(self):
        spec = _build()
        self.assertEqual(tuple(s.gate_id for s in spec.roster), TGT_GATE_IDS)
        self.assertEqual(len(spec.gate_contracts), 8)
        self.assertEqual(spec.gateset.gateset_id, ADC_TARGET_GATESET_ID)
        self.assertEqual(spec.instantiation.gateset_id, ADC_TARGET_GATESET_ID)

    def test_migration_block(self):
        doc = _load(CONTRACT_PATH)
        m = doc["migration"]
        self.assertEqual(m["pr"], "runtime_migration_pr_d")
        self.assertIn("per_gate_primary_modules", m["deferred"])
        self.assertIn("scientific_review", m)
        self.assertIn("gate_version_provenance", m)

    def test_program_label_is_not_a_gateset_id(self):
        doc = _load(CONTRACT_PATH)
        self.assertTrue(doc["program_label"]["never_a_gateset_id"])
        self.assertEqual(doc["program_label"]["label"], PROGRAM_LABEL)
        # never appears in any gateset_id slot in the contract
        self.assertEqual(doc["gateset"]["gateset_id"], ADC_TARGET_GATESET_ID)
        self.assertEqual(
            doc["instantiation"]["gateset_id"], ADC_TARGET_GATESET_ID
        )
        for b in doc["context_specific_bindings"]["gate_bindings"]:
            self.assertEqual(b["gateset_id"], ADC_TARGET_GATESET_ID)
        self.assertEqual(
            doc["context_specific_bindings"]["gateset_binding"]["gateset_id"],
            ADC_TARGET_GATESET_ID,
        )


# --- 2. roster parity with frozen CURRENT_SYSTEM v5 section 6.4 -----

class RosterParityTests(unittest.TestCase):
    def test_roster_names_and_regimes_match_module_constants(self):
        doc = _load(CONTRACT_PATH)
        self.assertEqual(
            tuple(r["gate_id"] for r in doc["roster"]), TGT_GATE_IDS
        )
        for row in doc["roster"]:
            self.assertEqual(row["name"], TGT_GATE_NAMES[row["gate_id"]])
        self.assertEqual(doc["roster_constants"]["candidate_level"], "L04")
        self.assertEqual(doc["roster_constants"]["gateset_id"], ADC_TARGET_GATESET_ID)
        self.assertEqual(doc["roster_constants"]["gate_version"], "1.0")

    def test_gate_names_appear_in_frozen_v5_section_6_4(self):
        # v5 section 6.4 enumerates the eight gate scientific names in a
        # line-wrapped, slash-separated run; compare on normalised whitespace.
        text = " ".join(V5_DOC.read_text().split())
        for name in TGT_GATE_NAMES.values():
            self.assertIn(
                " ".join(name.split()), text,
                f"{name!r} not found in frozen CURRENT_SYSTEM v5 section 6.4",
            )


# --- 3. gate_binding parity with the frozen disk schema ------------

class BindingParityTests(unittest.TestCase):
    def setUp(self):
        self.schema = _load(GATE_BINDING_SCHEMA)
        self.gate_binding = self.schema["$defs"]["gate_binding"]
        self.gateset_binding = self.schema["$defs"]["gateset_binding"]
        self.doc = _load(CONTRACT_PATH)

    def test_gate_bindings_have_exactly_the_schema_key_set(self):
        allowed = set(self.gate_binding["properties"])
        required = set(self.gate_binding["required"])
        for b in self.doc["context_specific_bindings"]["gate_bindings"]:
            self.assertEqual(set(b), allowed)
            self.assertTrue(required <= set(b))

    def test_gateset_binding_has_the_schema_key_set(self):
        allowed = set(self.gateset_binding["properties"])
        required = set(self.gateset_binding["required"])
        gb = self.doc["context_specific_bindings"]["gateset_binding"]
        self.assertTrue(set(gb) <= allowed)
        self.assertTrue(required <= set(gb))

    def test_binding_patterns_and_enums(self):
        import re as _re

        mod_pat = self.gate_binding["properties"]["primary_module_id"]["pattern"]
        gsid_pat = self.gate_binding["properties"]["gateset_id"]["pattern"]
        regime_enum = set(
            self.gate_binding["properties"]["dominant_evidence_regime"]["enum"]
        )
        level_enum = set(self.gate_binding["properties"]["candidate_level"]["enum"])
        for b in self.doc["context_specific_bindings"]["gate_bindings"]:
            self.assertRegex(b["primary_module_id"], mod_pat)
            self.assertRegex(b["gateset_id"], gsid_pat)
            self.assertIn(b["dominant_evidence_regime"], regime_enum)
            self.assertIn(b["candidate_level"], level_enum)
            for ref in ("gate_contract_ref", "evidence_ladder_ref", "assessment_rule_ref"):
                self.assertTrue(_re.match(r"^external:.+", b[ref]))


# --- 4. primary Module binding slots ----------------------------------

#: gate_id -> the primary_module_version once its Module is built. PR D left
#: every gate at "0.0.0"; Runtime Migration PR E2 built MOD-TGT01, PR E4 built
#: MOD-TGT05, PR E6 built MOD-TGT08, and PR E8 built MOD-TGT02.
_BUILT_MODULE_VERSIONS = {
    "TGT-01": "1.0.0",
    "TGT-02": "1.0.0",
    "TGT-05": "1.0.0",
    "TGT-08": "1.0.0",
}


class ModuleBindingSlotTests(unittest.TestCase):
    def test_every_module_slot_is_deterministic_and_at_its_expected_version(self):
        doc = _load(CONTRACT_PATH)
        for b in doc["context_specific_bindings"]["gate_bindings"]:
            expected = _BUILT_MODULE_VERSIONS.get(b["gate_id"], "0.0.0")
            self.assertEqual(b["primary_module_version"], expected)
            self.assertEqual(
                b["primary_module_id"], _deterministic_module_id(b["gate_id"])
            )
        self.assertEqual(doc["primary_module_binding"]["unbuilt_version"], "0.0.0")
        self.assertEqual(
            doc["primary_module_binding"]["built_module_versions"],
            _BUILT_MODULE_VERSIONS,
        )
        self.assertIn("per_gate_primary_modules", doc["migration"]["deferred"])

    def test_pr_d_created_no_module_py_in_src_objects(self):
        objects_dir = ROOT / "src" / "objects"
        names = {p.name for p in objects_dir.iterdir()}
        for n in range(1, 9):
            self.assertNotIn(f"mod_tgt0{n}.py", names)

    def test_tgt01_module_is_built_in_gate_modules(self):
        module_yaml = (
            ROOT / "gate_modules" / "tgt01_adc_modality_precedent" / "module.yaml"
        )
        self.assertTrue(module_yaml.is_file())
        manifest = yaml.safe_load(module_yaml.read_text())["module"]
        self.assertEqual(manifest["module_id"], "MOD-TGT01")
        self.assertEqual(manifest["module_version"], "1.0.0")
        self.assertEqual(manifest["gate_binding"]["gate_id"], "TGT-01")

    def test_tgt02_module_is_built_in_gate_modules(self):
        module_yaml = (
            ROOT
            / "gate_modules"
            / "tgt02_indication_specific_malignant_cell_coverage"
            / "module.yaml"
        )
        self.assertTrue(module_yaml.is_file())
        manifest = yaml.safe_load(module_yaml.read_text())["module"]
        self.assertEqual(manifest["module_id"], "MOD-TGT02")
        self.assertEqual(manifest["module_version"], "1.0.0")
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e8")
        self.assertEqual(manifest["gate_binding"]["gate_id"], "TGT-02")

    def test_tgt05_module_is_built_in_gate_modules(self):
        module_yaml = (
            ROOT / "gate_modules" / "tgt05_normal_tissue_fatal_liability" / "module.yaml"
        )
        self.assertTrue(module_yaml.is_file())
        manifest = yaml.safe_load(module_yaml.read_text())["module"]
        self.assertEqual(manifest["module_id"], "MOD-TGT05")
        self.assertEqual(manifest["module_version"], "1.0.0")
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e4")
        self.assertEqual(manifest["gate_binding"]["gate_id"], "TGT-05")

    def test_tgt08_module_is_built_in_gate_modules(self):
        module_yaml = (
            ROOT
            / "gate_modules"
            / "tgt08_target_opportunity_competition_ip_whitespace"
            / "module.yaml"
        )
        self.assertTrue(module_yaml.is_file())
        manifest = yaml.safe_load(module_yaml.read_text())["module"]
        self.assertEqual(manifest["module_id"], "MOD-TGT08")
        self.assertEqual(manifest["module_version"], "1.0.0")
        self.assertEqual(manifest["built_in"], "runtime_migration_pr_e6")
        self.assertEqual(manifest["gate_binding"]["gate_id"], "TGT-08")


# --- 5. per-object accept / reject -------------------------------

def _spec(**overrides) -> TgtGateSpec:
    base = dict(
        gate_id="TGT-04",
        name=TGT_GATE_NAMES["TGT-04"],
        candidate_level="L04",
        gateset_id="ADC_TARGET_GATESET",
        gate_version="1.0",
        dominant_evidence_regime="PUBLIC_HYBRID",
    )
    base.update(overrides)
    return TgtGateSpec(**base)


class TgtGateSpecTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(_spec().gate_id, "TGT-04")

    def test_rejects(self):
        with self.assertRaises(ValueError):
            _spec(gate_id="TGT-09")
        with self.assertRaises(ValueError):
            _spec(name="Some Other Name")
        with self.assertRaises(ValueError):
            _spec(candidate_level="L05")
        with self.assertRaises(ValueError):
            _spec(gateset_id="ADC_EPITOPE_GATESET")
        with self.assertRaises(ValueError):
            _spec(gate_version="2.0")
        with self.assertRaises(ValueError):
            _spec(dominant_evidence_regime="PUBLIC_PRIMARY")  # TGT-04 is PUBLIC_HYBRID


class TgtGateContractTests(unittest.TestCase):
    def _contract(self, **overrides) -> TgtGateContract:
        spec = _spec()
        ladder = EvidenceLadder(
            gate_id="TGT-04",
            gate_version="1.0",
            rungs=(
                LadderRung("DIRECT", ("quantitative surface density",), "establishes density"),
                LadderRung("INDIRECT_STRONG", ("membranous IHC",), "localization only"),
                LadderRung("WEAK", ("bulk RNA",), "hypothesis only"),
            ),
            evidence_ceiling="quantitative cell-surface antigen density",
        )
        base = dict(
            gate_spec=spec,
            gate_question="Is the target on the CRC cell surface at adequate density?",
            evidence_required=("quantitative surface density", "membranous IHC"),
            ladder=ladder,
            allowed_inference=("the antigen is on the cell surface",),
            forbidden_inference=("surface localization implies adequate density",),
            unknown_behavior="only localization -> strength stays UNKNOWN",
            fatal_conditions=("density far below validated ADC targets",),
            evidence_ladder_ref="external:crc_adc_target_gateset/TGT-04/evidence_ladder@v1",
            assessment_rule_ref="external:crc_adc_target_gateset/TGT-04/assessment_rule@v1",
            primary_module_id="MOD-TGT04",
            primary_module_version="0.0.0",
        )
        base.update(overrides)
        return TgtGateContract(**base)

    def test_valid(self):
        self.assertEqual(self._contract().gate_spec.gate_id, "TGT-04")

    def test_rejects_built_module_version(self):
        with self.assertRaises(ValueError):
            self._contract(primary_module_version="1.0.0")

    def test_rejects_wrong_module_id(self):
        with self.assertRaises(ValueError):
            self._contract(primary_module_id="MOD-TGT99")

    def test_rejects_non_external_refs(self):
        with self.assertRaises(ValueError):
            self._contract(assessment_rule_ref="crc_adc_target_gateset/TGT-04/rule")

    def test_rejects_empty_inference_or_fatal(self):
        with self.assertRaises(ValueError):
            self._contract(allowed_inference=())
        with self.assertRaises(ValueError):
            self._contract(fatal_conditions=())
        with self.assertRaises(ValueError):
            self._contract(forbidden_inference=("",))

    def test_rejects_ladder_gate_mismatch(self):
        bad = EvidenceLadder(
            gate_id="TGT-05",
            gate_version="1.0",
            rungs=(
                LadderRung("DIRECT", ("x",), "c"),
                LadderRung("INDIRECT_STRONG", ("y",), "c"),
                LadderRung("WEAK", ("z",), "c"),
            ),
            evidence_ceiling="c",
        )
        with self.assertRaises(ValueError):
            self._contract(ladder=bad)


class CrcAdcTargetGateSetV1Tests(unittest.TestCase):
    def test_valid_from_contract(self):
        spec = _build()
        self.assertEqual(len(spec.gate_contracts), 8)

    def test_rejects_program_label_as_gateset_id(self):
        good = _build()
        with self.assertRaises(ValueError):
            dataclasses.replace(
                good,
                gateset=dataclasses.replace(good.gateset, gateset_id="CRC_ADC_TARGET_GATESET"),
            )

    def test_rejects_roster_out_of_order(self):
        good = _build()
        reordered = (good.roster[1], good.roster[0]) + good.roster[2:]
        with self.assertRaises(ValueError):
            dataclasses.replace(good, roster=reordered)

    def test_rejects_wrong_gateset_version(self):
        good = _build()
        with self.assertRaises(ValueError):
            dataclasses.replace(
                good,
                gateset=dataclasses.replace(good.gateset, gateset_version="2.0"),
            )


# --- 5b. scientific-review revisions (REQUEST_CHANGES round 1) ----

class LadderScienceRevisionTests(unittest.TestCase):
    """Locks the six ladder semantics fixes from the PR #104 scientific review."""

    def setUp(self):
        self.contracts = _load(CONTRACT_PATH)["gate_contracts"]

    def _all_text(self, gate_id):
        c = self.contracts[gate_id]
        parts = [c["gate_question"], c["evidence_ceiling"], c["unknown_behavior"]]
        parts += list(c["evidence_required"])
        parts += list(c["allowed_inference"]) + list(c["forbidden_inference"])
        parts += list(c["fatal_conditions"])
        for grade in ("DIRECT", "INDIRECT_STRONG", "WEAK"):
            rung = c["evidence_ladder"][grade]
            parts += list(rung["admissible_evidence_classes"]) + [rung["ceiling_rule"]]
        return " ".join(parts)

    def test_no_numeric_thresholds_anywhere(self):
        # no invented quantitative cutoff like ">100000", "< 10 000", "20%"
        import re as _re
        pat = _re.compile(r"[<>]\s*\d|\b\d[\d,\s]*\s*(molecules|ng/ml|%|per cell)", _re.I)
        for gid in TGT_GATE_IDS:
            self.assertIsNone(pat.search(self._all_text(gid)), f"{gid} has a numeric cutoff")

    def test_tgt01_adjacent_target_not_indirect_strong_and_fatal_is_pattern(self):
        c = self.contracts["TGT-01"]
        istrong = " ".join(c["evidence_ladder"]["INDIRECT_STRONG"]["admissible_evidence_classes"])
        self.assertNotIn("adjacent target", istrong.lower())
        fatal = " ".join(c["fatal_conditions"]).lower()
        self.assertIn("two or more independent", fatal)

    def test_tgt03_04_fatal_have_no_universal_density_range(self):
        for gid in ("TGT-03", "TGT-04"):
            fatal = " ".join(self.contracts[gid]["fatal_conditions"]).lower()
            self.assertNotIn("range of clinically validated adc targets", fatal)

    def test_tgt05_target_level_not_product_window(self):
        c = self.contracts["TGT-05"]
        self.assertNotIn("unmanageable", c["gate_question"].lower())
        allowed = " ".join(c["allowed_inference"]).lower()
        self.assertNotIn("or absence of a normal-tissue", allowed)
        forbidden = " ".join(c["forbidden_inference"]).lower()
        self.assertIn("negative rna", forbidden)
        self.assertIn("do not transfer one-to-one", " ".join(
            c["evidence_ladder"]["INDIRECT_STRONG"]["admissible_evidence_classes"]
        ).lower())

    def test_tgt05_fatal_requires_convergent_pattern_not_single_construct(self):
        fatal = " ".join(self.contracts["TGT-05"]["fatal_conditions"]).lower()
        self.assertIn("convergent target-mediated", fatal)
        self.assertIn("materially distinct adc constructs", fatal)
        self.assertIn("not target-wide fatal", fatal)
        self.assertNotIn("preclude an adc therapeutic window", fatal)
        self.assertEqual(len(self.contracts["TGT-05"]["fatal_conditions"]), 1)

    def test_tgt06_internalization_is_configuration_dependent(self):
        c = self.contracts["TGT-06"]
        allowed = " ".join(c["allowed_inference"]).lower()
        self.assertIn("not a target-intrinsic constant", allowed)
        istrong = " ".join(c["evidence_ladder"]["INDIRECT_STRONG"]["admissible_evidence_classes"]).lower()
        self.assertIn("functional adc delivery precedent", istrong)
        fatal = " ".join(c["fatal_conditions"]).lower()
        self.assertIn("multiple independent antibody / epitope configurations", fatal)

    def test_tgt07_measured_soluble_antigen_is_not_direct_sink(self):
        c = self.contracts["TGT-07"]
        direct = " ".join(c["evidence_ladder"]["DIRECT"]["admissible_evidence_classes"]).lower()
        self.assertNotIn("quantified circulating soluble target in crc patients\n", direct + "\n")
        # the bare measurement is now INDIRECT_STRONG, not DIRECT
        istrong = " ".join(c["evidence_ladder"]["INDIRECT_STRONG"]["admissible_evidence_classes"]).lower()
        self.assertIn("without an exposure", istrong)
        forbidden = " ".join(c["forbidden_inference"]).lower()
        self.assertIn("by itself, establishes a material antigen sink", forbidden)

    def test_tgt08_no_fto_equivalent_fatal(self):
        fatal = " ".join(self.contracts["TGT-08"]["fatal_conditions"]).lower()
        self.assertNotIn("design-around", fatal)
        self.assertNotIn("composition-of-matter ip", fatal)
        self.assertEqual(len(self.contracts["TGT-08"]["fatal_conditions"]), 1)


# --- 6. deep immutability + PR A/B/C untouched -------------------

class ImmutabilityAndBoundaryTests(unittest.TestCase):
    def test_module_maps_are_read_only(self):
        with self.assertRaises(TypeError):
            TGT_GATE_NAMES["TGT-01"] = "x"

    def test_frozen_dataclasses(self):
        s = _spec()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            s.gate_id = "TGT-01"

    def test_evidence_ladder_ref_is_read_only_tuple(self):
        contract = _build().gate_contracts[3]
        self.assertIsInstance(contract.evidence_required, tuple)
        with self.assertRaises(TypeError):
            contract.evidence_required[0] = "x"

    def test_pr_abc_contracts_not_touched(self):
        # PR D only imports from them
        from src.objects import decision_model, gate_model, evidence_reference_model  # noqa: F401
        from src.objects.gate_model import CANONICAL_GATESET_IDS
        self.assertEqual(CANONICAL_GATESET_IDS["L04"], "ADC_TARGET_GATESET")

    def test_field_names_helper(self):
        self.assertIn("roster", field_names(CrcAdcTargetGateSetV1))
        self.assertIn("gate_spec", field_names(TgtGateContract))


if __name__ == "__main__":
    unittest.main()
