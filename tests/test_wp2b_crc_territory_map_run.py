import pathlib
import unittest

import yaml

from src.contracts.opportunity_territory import (
    OpportunityTerritory,
    OpportunityTerritoryMap,
)
from src.contracts.search_space_admission import SEARCH_SPACE_CRITERIA

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "pools" / "wp2b_crc_territory_map_run.yaml"
CONTRACT = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))


class RunAuthorisationTests(unittest.TestCase):
    """Approving this contract must not, by itself, let the run start."""

    def test_the_run_is_not_authorised(self):
        run = CONTRACT["run"]
        self.assertFalse(run["authorises_run"])
        self.assertEqual(run["authorises_run_count"], 0)
        self.assertEqual(run["execution_status"], "not_authorized_not_executed")
        self.assertTrue(run["approval_does_not_authorise_execution"])

    def test_both_blockers_are_declared_and_uncleared(self):
        self.assertEqual(CONTRACT["run"]["blocked_by"], ["BLOCK-01", "BLOCK-02"])
        blockers = {blocker["id"]: blocker for blocker in CONTRACT["blockers"]}
        self.assertEqual(set(blockers), {"BLOCK-01", "BLOCK-02"})
        for blocker_id, blocker in blockers.items():
            with self.subTest(blocker=blocker_id):
                self.assertFalse(blocker["cleared"])
                self.assertTrue(blocker["must_be_frozen_before_run"])
                self.assertTrue(blocker["why"].strip())
                self.assertTrue(blocker["cleared_by"].strip())

    def test_blocker_one_covers_the_sponsor_profile_instance(self):
        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-01")
        self.assertEqual(blocker["must_be"], "external_instance")
        self.assertIn("sponsor_evidence_advantage_ref", blocker["blocks"])

    def test_blocker_two_covers_the_route_policy(self):
        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-02")
        self.assertEqual(blocker["must_be"], "external_auditable_policy")
        self.assertIn("search_space_admission_ref", blocker["blocks"])
        self.assertEqual(len(blocker["must_define"]), 4)

    def test_a_result_pr_is_required(self):
        self.assertTrue(CONTRACT["run"]["requires_result_pr"])


class ScopeTests(unittest.TestCase):
    def test_the_territory_count_band_is_frozen(self):
        band = CONTRACT["scope"]["territory_count_band"]
        self.assertEqual((band["min"], band["max"]), (15, 30))

    def test_the_active_band_is_a_reconciliation_reference_not_a_target(self):
        """A quota would turn routing into a number-hitting exercise."""

        band = CONTRACT["scope"]["expected_active_band"]
        self.assertFalse(band["is_a_target"])
        self.assertTrue(band["is_a_reconciliation_reference"])

    def test_territory_granularity_must_be_decidable(self):
        scope = CONTRACT["scope"]
        self.assertTrue(scope["territory_granularity_must_be_decidable"])
        self.assertTrue(scope["territory_granularity_rule"].strip())


class LegacyPipelineTests(unittest.TestCase):
    """The old 369-pair axis is neither consumed nor destroyed."""

    def test_the_legacy_axis_may_not_be_read_or_cited(self):
        legacy = CONTRACT["relationship_to_legacy_level_01"]
        self.assertFalse(legacy["may_read_legacy_axis"])
        self.assertFalse(legacy["may_cite_legacy_axis_as_evidence"])

    def test_the_legacy_axis_stays_frozen_but_is_not_deleted(self):
        legacy = CONTRACT["relationship_to_legacy_level_01"]
        self.assertTrue(legacy["legacy_axis_remains_frozen"])
        self.assertTrue(legacy["legacy_axis_not_deleted"])

    def test_the_run_replaces_the_candidate_generation_order(self):
        self.assertTrue(
            CONTRACT["relationship_to_legacy_level_01"][
                "replaces_candidate_generation_order"
            ]
        )


class SourcePolicyTests(unittest.TestCase):
    def test_derived_databases_are_barred(self):
        policy = CONTRACT["source_policy"]
        self.assertTrue(policy["tier_1_primary_public_permitted"])
        self.assertFalse(policy["tier_2_derived_databases_permitted"])

    def test_both_quarantined_runs_stay_barred(self):
        barred = {entry["pr"]: entry for entry in CONTRACT["source_policy"]["barred_sources"]}
        self.assertEqual(set(barred), {53, 54})
        for pr, entry in barred.items():
            with self.subTest(pr=pr):
                self.assertEqual(entry["status"], "UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED")
                self.assertTrue(entry["barred_content"].strip())
        self.assertTrue(CONTRACT["source_policy"]["barred_sources_must_be_declared_unused"])

    def test_model_knowledge_alone_cannot_support_a_field(self):
        policy = CONTRACT["source_policy"]
        self.assertTrue(policy["model_domain_knowledge_alone_is_insufficient"])
        self.assertTrue(policy["every_field_requires_source_ref"])


class EvidenceStandardTests(unittest.TestCase):
    def test_every_territory_field_group_has_a_standard(self):
        covered = set()
        for group in CONTRACT["evidence_standards"]:
            covered.update(group["fields"])
        schema_fields = set(OpportunityTerritory.__dataclass_fields__)
        # identity, routing provenance and provenance are governed elsewhere in
        # this contract, not by a field-group evidence standard.
        exempt = {
            "territory_id",
            "search_space_admission_ref",
            "source_refs",
        }
        self.assertEqual(covered, schema_fields - exempt)

    def test_clinical_definition_may_not_be_unknown(self):
        group = next(
            g for g in CONTRACT["evidence_standards"] if g["field_group"] == "clinical_definition"
        )
        self.assertFalse(group["unknown_permitted"])

    def test_empty_competition_must_be_distinguishable_from_uninvestigated(self):
        group = next(
            g for g in CONTRACT["evidence_standards"] if g["field_group"] == "competition"
        )
        self.assertTrue(group["empty_permitted"])
        self.assertTrue(group["empty_must_be_distinguishable_from_uninvestigated"])

    def test_sponsor_advantage_unknown_stays_unknown(self):
        group = next(
            g for g in CONTRACT["evidence_standards"] if g["field_group"] == "sponsor"
        )
        self.assertTrue(group["unknown_permitted"])
        self.assertIn("不转为", group["unknown_rule"])

    def test_known_target_biology_is_constrained_to_background_intelligence(self):
        """Carried forward from the PR #77 review."""

        group = next(
            g for g in CONTRACT["evidence_standards"] if g["field_group"] == "availability"
        )
        constraint = group["known_target_biology_constraint"]
        self.assertIn("不是 target candidate", constraint)
        self.assertIn("WP3", constraint)


class OutputTests(unittest.TestCase):
    def test_output_stays_outside_the_repository(self):
        output = CONTRACT["output"]
        self.assertEqual(output["location"], "external_workspace")
        self.assertEqual(output["location_in_repository"], "forbidden")

    def test_output_conforms_to_the_merged_schema(self):
        output = CONTRACT["output"]
        self.assertEqual(output["conforms_to"], "OpportunityTerritory@0.1.0")
        self.assertEqual(output["map_conforms_to"], "OpportunityTerritoryMap@0.1.0")
        self.assertEqual(CONTRACT["run"]["produces"], "OpportunityTerritoryMap@0.1.0")

    def test_the_route_stays_out_of_the_territory(self):
        """Carried forward from the PR #77 blocker."""

        output = CONTRACT["output"]
        self.assertTrue(output["territory_must_not_carry_route_state"])
        self.assertTrue(output["route_lives_only_in_admission"])
        self.assertTrue(output["every_territory_requires_admission"])

    def test_packaging_rules_are_carried_forward(self):
        """Established by the PR #60 round-two ruling."""

        output = CONTRACT["output"]
        self.assertTrue(output["packaging_required"])
        self.assertEqual(len(output["packaging_rules"]), 4)
        self.assertIn("verify_package.py", output["required_artifacts"])
        self.assertIn("source_manifest.json", output["required_artifacts"])


class ValidationRuleTests(unittest.TestCase):
    def test_validation_rule_ids_are_unique_and_contiguous(self):
        ids = [rule["id"] for rule in CONTRACT["validation_rules"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            ids, [f"VAL-T{index:02d}" for index in range(1, len(ids) + 1)]
        )

    def test_every_validation_rule_has_a_rule_body(self):
        for rule in CONTRACT["validation_rules"]:
            with self.subTest(rule=rule["id"]):
                self.assertTrue(rule["rule"].strip())

    def test_the_admission_criteria_count_matches_the_frozen_contract(self):
        rule = next(r for r in CONTRACT["validation_rules"] if r["id"] == "VAL-T06")
        self.assertIn("八个条件", rule["rule"])
        self.assertEqual(len(SEARCH_SPACE_CRITERIA), 8)

    def test_the_defects_this_project_already_paid_for_are_all_covered(self):
        bodies = " ".join(rule["rule"] for rule in CONTRACT["validation_rules"])
        for expected in (
            "territory_id 全局唯一",          # duplicate keys, SRCADM-01
            "路由状态字段",                    # the PR #77 mirror
            "target、gene、pair",              # territory is not a candidate
            "score 或 rank",
            "barred",                          # the quarantined runs
            "9×41×369",                        # the legacy axis
            "Tier 2",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, bodies)


class NotAuthorisedTests(unittest.TestCase):
    def test_the_run_itself_heads_the_not_authorised_list(self):
        self.assertIn("执行本运行", CONTRACT["not_authorised"][0])

    def test_downstream_work_is_not_authorised(self):
        joined = " ".join(CONTRACT["not_authorised"])
        for expected in (
            "program wedge",
            "target",
            "Gate",
            "EVGAP-01",
            "EVGAP-02",
            "GAP-P07",
            "9×41×369",
            "在仓库内保存",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, joined)

    def test_active_search_is_not_a_target_generation_authorisation(self):
        joined = " ".join(CONTRACT["not_authorised"])
        self.assertIn("ACTIVE_SEARCH 当作靶点生成授权", joined)


class RepositoryBoundaryTests(unittest.TestCase):
    def test_the_contract_carries_no_territory_content(self):
        """A run contract freezes how, never what."""

        text = CONTRACT_PATH.read_text(encoding="utf-8")
        for banned in ("MSS", "HER2", "TROP2", "KRAS", "BRAF", "G12C", "MSI"):
            with self.subTest(term=banned):
                self.assertNotIn(banned, text)
        self.assertNotIn("territories:", text)

    def test_the_map_schema_is_reachable_and_unchanged_by_this_contract(self):
        self.assertIn("territories", OpportunityTerritoryMap.__dataclass_fields__)
        self.assertNotIn("territory_status", OpportunityTerritory.__dataclass_fields__)


if __name__ == "__main__":
    unittest.main()
