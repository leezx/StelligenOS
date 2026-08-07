import ast
import pathlib
import re
import unittest

import yaml

from src.contracts.opportunity_territory import (
    OpportunityTerritory,
    OpportunityTerritoryMap,
    TERRITORY_NON_EMPTY_LIST_FIELDS,
    TERRITORY_REFERENCE_LIST_FIELDS,
    TERRITORY_SINGLE_REFERENCE_FIELDS,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "contracts" / "opportunity_territory.py"
CONTRACT_PATH = ROOT / "src" / "contracts" / "opportunity_territory.yaml"


def _territory(**overrides):
    fields = {
        "territory_id": "TERR-001",
        "disease_ref": "external:disease/1",
        "clinical_population_ref": "external:population/1",
        "molecular_subtype_ref": "external:subtype/1",
        "treatment_line_ref": "external:line/1",
        "prior_therapy_refs": ("external:therapy/1",),
        "metastatic_site_refs": ("external:site/1",),
        "current_soc_ref": "external:soc/1",
        "clinical_failure_mode_ref": "external:failure/1",
        "patient_size_band_ref": "external:size-band/1",
        "current_competitor_refs": ("external:competitor/1",),
        "leading_asset_refs": ("external:asset/1",),
        "expected_readout_refs": ("external:readout/1",),
        "position_occupancy_ref": "external:occupancy/1",
        "known_target_biology_refs": ("external:biology/1",),
        "available_patient_data_refs": ("external:data/1",),
        "available_model_refs": ("external:model/1",),
        "sponsor_evidence_advantage_ref": "external:advantage/1",
        "window_closure_risk_ref": "external:window-risk/1",
        "search_space_admission_ref": "external:search-space-admission/1",
        "source_refs": ("external:source/1",),
    }
    fields.update(overrides)
    return OpportunityTerritory(**fields)


def _map(**overrides):
    fields = {
        "map_id": "MAP-001",
        "disease_scope_ref": "external:disease-scope/1",
        "sponsor_profile_ref": "external:sponsor-profile/1",
        "territories": (_territory(),),
        "source_refs": ("external:source/1",),
    }
    fields.update(overrides)
    return OpportunityTerritoryMap(**fields)


class TerritoryShapeTests(unittest.TestCase):
    def test_a_fully_external_territory_is_accepted(self):
        territory = _territory()
        self.assertEqual(territory.territory_id, "TERR-001")
        self.assertEqual(
            territory.search_space_admission_ref,
            "external:search-space-admission/1",
        )

    def test_the_reference_field_rosters_are_literal(self):
        """Named literally so the parameterised tests cannot self-shrink."""

        self.assertEqual(
            TERRITORY_SINGLE_REFERENCE_FIELDS,
            (
                "disease_ref",
                "clinical_population_ref",
                "molecular_subtype_ref",
                "treatment_line_ref",
                "current_soc_ref",
                "clinical_failure_mode_ref",
                "patient_size_band_ref",
                "position_occupancy_ref",
                "sponsor_evidence_advantage_ref",
                "window_closure_risk_ref",
                "search_space_admission_ref",
            ),
        )
        self.assertEqual(
            TERRITORY_REFERENCE_LIST_FIELDS,
            (
                "prior_therapy_refs",
                "metastatic_site_refs",
                "current_competitor_refs",
                "leading_asset_refs",
                "expected_readout_refs",
                "known_target_biology_refs",
                "available_patient_data_refs",
                "available_model_refs",
                "source_refs",
            ),
        )

    def test_the_search_space_admission_reference_is_mandatory_and_external(self):
        """This one field carries the whole upstream routing binding."""

        for value in ("", "   ", "local:admission/1", "external:", "admission/1"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _territory(search_space_admission_ref=value)
        import dataclasses

        field = OpportunityTerritory.__dataclass_fields__["search_space_admission_ref"]
        self.assertIs(field.default, dataclasses.MISSING)
        self.assertIs(field.default_factory, dataclasses.MISSING)

    def test_every_single_reference_field_must_be_external(self):
        for field in TERRITORY_SINGLE_REFERENCE_FIELDS:
            for value in ("", "local:x/1", "x/1", "external:", "external:   "):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        _territory(**{field: value})

    def test_every_list_field_must_hold_external_references(self):
        for field in TERRITORY_REFERENCE_LIST_FIELDS:
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    _territory(**{field: ("local:x/1",)})
                with self.assertRaises(ValueError):
                    _territory(**{field: ["external:x/1"]})

    def test_only_provenance_is_required_to_be_non_empty(self):
        self.assertEqual(TERRITORY_NON_EMPTY_LIST_FIELDS, ("source_refs",))
        with self.assertRaises(ValueError):
            _territory(source_refs=())

    def test_an_empty_competitor_or_readout_list_is_a_valid_state(self):
        """No competitor and no expected readout is real, and informative."""

        territory = _territory(
            current_competitor_refs=(),
            leading_asset_refs=(),
            expected_readout_refs=(),
            known_target_biology_refs=(),
        )
        self.assertEqual(territory.current_competitor_refs, ())


class TerritoryMapTests(unittest.TestCase):
    def test_a_map_is_accepted(self):
        self.assertEqual(len(_map().territories), 1)

    def test_duplicate_territory_ids_are_rejected(self):
        with self.assertRaises(ValueError) as caught:
            _map(territories=(_territory(), _territory()))
        self.assertIn("TERR-001", str(caught.exception))

    def test_distinct_territory_ids_are_accepted(self):
        territories = (_territory(), _territory(territory_id="TERR-002"))
        self.assertEqual(len(_map(territories=territories).territories), 2)

    def test_the_map_offers_no_route_based_selection_helper(self):
        """A helper filtering on a local route would make a mirror operational."""

        territory_map = _map()
        self.assertFalse(hasattr(territory_map, "with_status"))
        for attribute in dir(territory_map):
            if attribute.startswith("_"):
                continue
            self.assertNotIn("status", attribute)
            self.assertNotIn("route", attribute)
            self.assertNotIn("active", attribute)

    def test_a_map_requires_provenance(self):
        with self.assertRaises(ValueError):
            _map(source_refs=())

    def test_an_empty_map_is_permitted(self):
        """A disease scope may be mapped before any territory is admitted."""

        self.assertEqual(_map(territories=()).territories, ())


class TerritoryBoundaryTests(unittest.TestCase):
    """A map is not a candidate pool."""

    def test_the_territory_carries_no_route_state(self):
        """SearchSpaceAdmission is the sole authority; a mirror would drift."""

        fields = OpportunityTerritory.__dataclass_fields__
        self.assertNotIn("territory_status", fields)
        for field_name in fields:
            self.assertNotIn("status", field_name)
            self.assertNotIn("route", field_name)
        self.assertIn("search_space_admission_ref", fields)
        with self.assertRaises(TypeError):
            _territory(territory_status="ACTIVE_SEARCH")

    def test_the_schema_names_no_target(self):
        for field_name in OpportunityTerritory.__dataclass_fields__:
            self.assertNotIn("target_id", field_name)
            self.assertNotIn("gene", field_name)
            self.assertNotIn("pair", field_name)

    def test_a_territory_exposes_no_generation_or_scoring_behaviour(self):
        territory = _territory()
        for attribute in dir(territory):
            if attribute.startswith("_"):
                continue
            self.assertFalse(callable(getattr(territory, attribute)))
        for field_name in OpportunityTerritory.__dataclass_fields__:
            self.assertFalse(field_name.endswith("_score"))
            self.assertNotIn("rank", field_name)

    def test_no_disease_specific_content_is_hard_coded(self):
        """The repository holds the shape; CRC content stays outside it."""

        source = MODULE_PATH.read_text(encoding="utf-8")
        code = "\n".join(
            line for line in source.splitlines() if not line.strip().startswith("#")
        )
        code = re.sub(r'""".*?"""', "", code, flags=re.DOTALL)
        for banned in ("CRC", "MSS", "HER2", "TROP2", "KRAS", "BRAF", "colorectal"):
            with self.subTest(term=banned):
                self.assertNotIn(banned, code)

    def test_module_imports_only_stdlib_and_the_frozen_route_vocabulary(self):
        modules = set()
        for node in ast.walk(ast.parse(MODULE_PATH.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        self.assertEqual(modules, {"__future__", "dataclasses", "typing"})

    def test_contract_yaml_matches_the_code(self):
        contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["territory_status_field"], "absent")
        self.assertNotIn("territory_status_values", contract)
        territory = contract["contracts"]["OpportunityTerritory"]
        declared = set(territory["required_fields"])
        self.assertEqual(declared, set(OpportunityTerritory.__dataclass_fields__))
        self.assertEqual(
            tuple(territory["non_empty_list_fields"]), TERRITORY_NON_EMPTY_LIST_FIELDS
        )
        self.assertEqual(
            set(contract["contracts"]["OpportunityTerritoryMap"]["required_fields"]),
            set(OpportunityTerritoryMap.__dataclass_fields__),
        )
        self.assertEqual(contract["upstream_relationship"]["binding_status"], "bound")
        self.assertEqual(
            contract["upstream_relationship"]["routed_by"],
            "SearchSpaceAdmission@0.1.0",
        )
        self.assertEqual(
            contract["downstream_relationship"]["consumed_by"], "not_yet_defined"
        )

    def test_contract_declares_the_invariants_that_carry_the_meaning(self):
        contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
        invariants = set(
            contract["contracts"]["OpportunityTerritory"]["invariants"]
        )
        for required in (
            "no_disease_specific_content_in_the_repository",
            "territory_is_a_map_row_not_a_candidate",
            "territory_names_no_target",
            "territory_does_not_generate_targets",
            "routing_decision_is_neither_restated_nor_mirrored_here",
            "search_space_admission_is_the_sole_authoritative_route_decision",
            "territory_records_routing_provenance_without_duplicating_route_state",
            "territory_carries_no_route_state_field",
            "active_search_does_not_authorise_target_generation",
        ):
            self.assertIn(required, invariants)
        map_invariants = contract["contracts"]["OpportunityTerritoryMap"]["invariants"]
        self.assertIn("territory_ids_must_be_unique", map_invariants)
        self.assertIn("map_offers_no_route_based_selection_helper", map_invariants)
        self.assertEqual(
            contract["downstream_relationship"]["downstream_must_not"],
            [
                "filter_territories_on_a_locally_stored_route",
                "treat_a_territory_reference_alone_as_evidence_of_admission",
            ],
        )


if __name__ == "__main__":
    unittest.main()
