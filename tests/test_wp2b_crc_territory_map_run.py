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
    """The run stays unauthorised while any blocker is uncleared."""

    def test_the_run_is_not_authorised(self):
        run = CONTRACT["run"]
        self.assertFalse(run["authorises_run"])
        self.assertEqual(run["authorises_run_count"], 0)
        self.assertEqual(run["execution_status"], "not_authorized_not_executed")
        self.assertTrue(run["approval_does_not_authorise_execution"])

    def test_an_uncleared_blocker_stays_in_blocked_by(self):
        blocked = CONTRACT["run"]["blocked_by"]
        uncleared = [b["id"] for b in CONTRACT["blockers"] if not b["cleared"]]
        self.assertEqual(sorted(blocked), sorted(uncleared))

    def test_a_cleared_blocker_names_what_cleared_it(self):
        """Clearing must be traceable, not merely a flipped flag."""

        cleared = {e["blocker"]: e for e in CONTRACT["run"]["blocked_by_cleared"]}
        for blocker in CONTRACT["blockers"]:
            with self.subTest(blocker=blocker["id"]):
                if not blocker["cleared"]:
                    self.assertNotIn(blocker["id"], cleared)
                    continue
                self.assertIn(blocker["id"], cleared)
                self.assertTrue(str(blocker["cleared_evidence"]).strip())

    def test_block_01_requires_human_approval_not_only_machine_validation(self):
        """Generated and machine-validated is not the same as human-approved.

        A sponsor profile encodes subjective commitments - capital boundary,
        resource control, capacity, transaction stage, IP strategy. A script can
        check the shape; it cannot check that the values are ones the human lead
        accepts.
        """

        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-01")
        self.assertEqual(
            blocker["clearing_conditions"],
            [
                "machine_validation == PASS",
                "human_approval_ref exists",
                "approved_instance_sha256 == frozen instance sha256",
            ],
        )
        self.assertTrue(blocker["clearing_conditions_are_conjunctive"])

        machine_ok = blocker["machine_validation"] == "PASS"
        human_ok = bool(blocker["human_approval_ref"])
        hash_ok = bool(blocker["approved_instance_sha256"])
        self.assertEqual(blocker["cleared"], machine_ok and human_ok and hash_ok)

    def test_machine_validation_alone_never_clears_block_01(self):
        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-01")
        if blocker["machine_validation"] == "PASS" and not blocker["human_approval_ref"]:
            self.assertFalse(
                blocker["cleared"],
                "BLOCK-01 cleared on machine validation with no human approval",
            )
            self.assertTrue(blocker["not_yet_cleared_because"].strip())

    def test_a_candidate_instance_is_not_an_approved_instance(self):
        """A profile can exist, validate, and still not be approved."""

        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-01")
        self.assertTrue(blocker["candidate_instance_sha256"].strip())
        self.assertTrue(blocker["candidate_is_not_approved"])
        if not blocker["human_approval_ref"]:
            self.assertIsNone(
                blocker["approved_instance_sha256"],
                "a candidate SHA-256 must not be promoted to an approved one",
            )
            self.assertNotEqual(
                blocker["candidate_instance_sha256"],
                blocker["approved_instance_sha256"],
            )

    def test_a_withdrawn_candidate_can_never_become_the_approved_instance(self):
        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-01")
        withdrawn = blocker["withdrawn_candidates"]
        self.assertTrue(withdrawn, "the withdrawn v0.1.0 artifact must stay recorded")
        for entry in withdrawn:
            with self.subTest(package=entry["package"]):
                self.assertTrue(entry["withdrawn_because"].strip())
                self.assertTrue(entry["must_never_be_approved_instance_sha256"])
                self.assertNotEqual(
                    entry["instance_sha256"], blocker["approved_instance_sha256"]
                )
                self.assertNotEqual(
                    entry["instance_sha256"], blocker["candidate_instance_sha256"]
                )
                self.assertNotIn(entry["package"], blocker["machine_validation_evidence"])

    def test_human_approval_needs_an_artifact_not_only_a_yes(self):
        """Six recorded fields, so a later version has an audit chain to compare."""

        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-01")
        self.assertEqual(
            blocker["human_approval_artifact_must_record"],
            [
                "approved_profile_version",
                "approved_instance_sha256",
                "approval_timestamp_utc",
                "approving_role",
                "acknowledges_operating_assumptions",
                "acknowledges_no_institutional_resource_ownership",
            ],
        )
        self.assertTrue(blocker["human_approval_artifact_rationale"].strip())

    def test_every_blocker_states_why_and_how_it_clears(self):
        blockers = {blocker["id"]: blocker for blocker in CONTRACT["blockers"]}
        self.assertEqual(set(blockers), {"BLOCK-01", "BLOCK-02"})
        for blocker_id, blocker in blockers.items():
            with self.subTest(blocker=blocker_id):
                self.assertTrue(blocker["must_be_frozen_before_run"])
                self.assertTrue(blocker["why"].strip())
                self.assertTrue(blocker["cleared_by"].strip())

    def test_the_run_count_names_its_consumption_point_honestly(self):  # noqa: D401
        """Carried forward from the PR #66 note on a declarative counter."""

        run = CONTRACT["run"]
        self.assertEqual(run["run_count_consumed_by"], "result_pr")
        self.assertTrue(
            run["run_count_consumption_is_process_enforced_not_code_enforced"],
            "the counter must not claim an enforcement the repository lacks",
        )

    def test_a_second_run_is_still_not_authorised(self):
        self.assertIn(
            "在 authorises_run_count 归零后再次执行本运行",
            CONTRACT["not_authorised"],
        )

    def test_blocker_one_treats_the_profile_as_an_upstream_input(self):
        """The profile is a baseline, not the advantage evidence itself."""

        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-01")
        self.assertEqual(blocker["must_be"], "external_instance")
        self.assertEqual(
            blocker["role"], "upstream_input_not_the_advantage_evidence_itself"
        )

    def test_blocker_two_covers_the_route_policy(self):
        blocker = next(b for b in CONTRACT["blockers"] if b["id"] == "BLOCK-02")
        self.assertEqual(blocker["must_be"], "external_auditable_policy")
        self.assertIn("search_space_admission_ref", blocker["blocks"])
        self.assertEqual(len(blocker["must_define"]), 4)

    def test_a_result_pr_is_required(self):
        self.assertTrue(CONTRACT["run"]["requires_result_pr"])


class ScopeTests(unittest.TestCase):
    def test_the_count_band_is_planning_capacity_not_a_validity_criterion(self):
        """Shaping the funnel first and making knowledge fit it is the failure."""

        band = CONTRACT["scope"]["territory_count_band"]
        self.assertEqual((band["min"], band["max"]), (15, 30))
        self.assertFalse(band["is_a_target"])
        self.assertTrue(band["is_a_reconciliation_reference"])
        self.assertTrue(band["out_of_band_is_not_a_failure"])
        self.assertTrue(band["out_of_band_requires_reconciliation_note"])

    def test_the_count_rule_records_rather_than_gates(self):
        rule = next(r for r in CONTRACT["validation_rules"] if r["id"] == "VAL-T01")
        self.assertIn("不构成失败", rule["rule"])
        self.assertIn("reconciliation note", rule["rule"])

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


class SponsorAdvantageSemanticsTests(unittest.TestCase):
    """A profile reference is a company bio, not evidence of a local advantage."""

    def test_the_profile_is_a_baseline_not_the_evidence(self):
        semantics = CONTRACT["sponsor_evidence_advantage_semantics"]
        self.assertTrue(semantics["profile_is_a_baseline_not_the_evidence"])
        self.assertTrue(semantics["ref_must_not_point_directly_at_the_profile"])
        self.assertEqual(
            semantics["ref_points_to"],
            "territory_specific_external_evidence_or_assessment",
        )

    def test_the_shared_reference_failure_mode_is_named(self):
        semantics = CONTRACT["sponsor_evidence_advantage_semantics"]
        self.assertTrue(semantics["ref_must_not_be_shared_across_territories"])
        self.assertIn("公司简介引用", semantics["shared_ref_failure_mode"])

    def test_the_derivation_chain_is_recorded(self):
        semantics = CONTRACT["sponsor_evidence_advantage_semantics"]
        self.assertEqual(len(semantics["derivation"]), 4)

    def test_no_new_formal_contract_is_required_now(self):
        semantics = CONTRACT["sponsor_evidence_advantage_semantics"]
        self.assertFalse(semantics["formal_contract_required_now"])

    def test_validation_enforces_the_semantics(self):
        rules = {r["id"]: r["rule"] for r in CONTRACT["validation_rules"]}
        self.assertIn("不直接指向 DevelopmentSponsorProfile", rules["VAL-T19"])
        self.assertIn("不得共用同一个", rules["VAL-T20"])
        self.assertIn("不得仅由 DevelopmentSponsorProfile 支撑", rules["VAL-T21"])

    def test_the_advantage_artifact_is_required_in_the_package(self):
        self.assertIn(
            "sponsor_evidence_advantage.json", CONTRACT["output"]["required_artifacts"]
        )


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
            g
            for g in CONTRACT["evidence_standards"]
            if g["field_group"] == "sponsor_fit_context"
        )
        self.assertTrue(group["unknown_permitted"])
        self.assertIn("不转为", group["unknown_rule"])
        self.assertTrue(group["profile_alone_is_insufficient"])

    def test_sponsor_context_and_timing_are_separate_groups(self):
        """Window closure risk is competition timing, not a sponsor attribute."""

        groups = {g["field_group"]: g for g in CONTRACT["evidence_standards"]}
        self.assertEqual(
            groups["sponsor_fit_context"]["fields"], ["sponsor_evidence_advantage_ref"]
        )
        self.assertEqual(groups["timing"]["fields"], ["window_closure_risk_ref"])
        timing = groups["timing"]
        self.assertTrue(timing["profile_alone_is_insufficient"])
        self.assertIn("time_fit", timing["downstream_note"])

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
        self.assertIn("BLOCK-01", CONTRACT["not_authorised"][0])

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

        # Structural, not substring: a key literally named "territories" would
        # mean the contract had started carrying territory content. Matching on
        # the text alone trips over keys that merely end in the word.
        def keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield key
                    yield from keys(value)
            elif isinstance(node, list):
                for item in node:
                    yield from keys(item)

        self.assertNotIn("territories", set(keys(CONTRACT)))

    def test_the_map_schema_is_reachable_and_unchanged_by_this_contract(self):
        self.assertIn("territories", OpportunityTerritoryMap.__dataclass_fields__)
        self.assertNotIn("territory_status", OpportunityTerritory.__dataclass_fields__)


if __name__ == "__main__":
    unittest.main()
