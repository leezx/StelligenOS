"""Prove the route policy table is well formed, total and deterministic.

The evaluator below lives in the test on purpose. The repository must not route
any territory: `src/` contains no route resolver, and this file only applies the
declared table to hypothetical status tuples in order to prove properties of the
table itself. It never touches an admission or a territory instance.
"""

import itertools
import pathlib
import unittest

import yaml

from src.contracts.search_space_admission import (
    SEARCH_SPACE_CRITERIA,
    CriterionStatus,
    SearchSpaceRoute,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "docs" / "pools" / "search_space_route_policy.yaml"
POLICY = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))

RULES = POLICY["routing"]["rules"]
STATUSES = tuple(status.value for status in CriterionStatus)


def resolve(statuses: dict[str, str]) -> tuple[str, str]:
    """Apply the declared table to one hypothetical status tuple."""

    for rule in RULES:
        if all(statuses[key] == value for key, value in rule["when"].items()):
            return rule["route"], rule["id"]
    raise AssertionError("the table is not total")


def all_status_tuples():
    for combination in itertools.product(STATUSES, repeat=len(SEARCH_SPACE_CRITERIA)):
        yield dict(zip(SEARCH_SPACE_CRITERIA, combination))


class PolicyShapeTests(unittest.TestCase):
    def test_the_policy_clears_the_declared_blocker(self):
        policy = POLICY["policy"]
        self.assertEqual(policy["clears_blocker"], "BLOCK-02")
        self.assertEqual(policy["applies_to"], "SearchSpaceAdmission@0.1.0")
        self.assertEqual(
            policy["external_ref_must_resolve_to"],
            f"{policy['policy_id']}@{policy['policy_version']}",
        )

    def test_the_repository_does_not_compute_routes(self):
        self.assertFalse(POLICY["policy"]["repository_computes_routes"])
        self.assertEqual(POLICY["policy"]["aggregate_score"], "forbidden")

    def test_every_frozen_criterion_has_a_standard(self):
        declared = tuple(entry["id"] for entry in POLICY["criteria"])
        self.assertEqual(declared, SEARCH_SPACE_CRITERIA)

    def test_every_criterion_defines_all_three_states(self):
        for entry in POLICY["criteria"]:
            with self.subTest(criterion=entry["id"]):
                for key in ("satisfied_when", "unsatisfied_when", "unknown_when"):
                    self.assertTrue(entry[key].strip())
                self.assertTrue(entry["evidence_from"])

    def test_the_two_criteria_that_cannot_rest_on_the_profile_say_so(self):
        by_id = {entry["id"]: entry for entry in POLICY["criteria"]}
        for criterion in ("asymmetric_evidence_advantage", "time_window_compatible"):
            with self.subTest(criterion=criterion):
                self.assertTrue(
                    by_id[criterion]["must_not_be_supported_by_profile_alone"]
                )

    def test_every_rule_names_a_frozen_route(self):
        routes = {route.value for route in SearchSpaceRoute}
        for rule in RULES:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["route"], routes)
                self.assertTrue(rule["rationale"].strip())
                for key, value in rule["when"].items():
                    self.assertIn(key, SEARCH_SPACE_CRITERIA)
                    self.assertIn(value, STATUSES)

    def test_only_the_last_rule_is_the_catch_all(self):
        self.assertEqual(RULES[-1]["when"], {})
        self.assertTrue(RULES[-1]["is_catch_all"])
        self.assertEqual(RULES[-1]["route"], SearchSpaceRoute.WATCHLIST.value)
        for rule in RULES[:-1]:
            with self.subTest(rule=rule["id"]):
                self.assertNotEqual(rule["when"], {})

    def test_rule_ids_are_unique(self):
        ids = [rule["id"] for rule in RULES]
        self.assertEqual(len(ids), len(set(ids)))


class TableProofTests(unittest.TestCase):
    """Enumerate every reachable status tuple: 3^8 = 6561."""

    def test_the_table_is_total_and_deterministic(self):
        count = 0
        for statuses in all_status_tuples():
            route, _ = resolve(statuses)
            self.assertIn(route, {r.value for r in SearchSpaceRoute})
            count += 1
        self.assertEqual(count, 3 ** len(SEARCH_SPACE_CRITERIA))
        self.assertEqual(count, 6561)

    def test_unknown_never_produces_out_of_mandate(self):
        """"We do not know, therefore drop it" mirrors the error we removed."""

        for statuses in all_status_tuples():
            route, rule_id = resolve(statuses)
            if route == SearchSpaceRoute.OUT_OF_MANDATE.value:
                with self.subTest(rule=rule_id):
                    self.assertIn(
                        CriterionStatus.UNSATISFIED.value,
                        statuses.values(),
                        f"{rule_id} reached OUT_OF_MANDATE with no UNSATISFIED",
                    )

    def test_no_out_of_mandate_rule_keys_on_unknown(self):
        """OUT must be driven by affirmative negatives, never by ignorance.

        Checking only that the resolved tuple contains some UNSATISFIED is too
        weak: a rule could key on UNKNOWN and still be satisfied by an unrelated
        negative elsewhere in the tuple.
        """

        for rule in RULES:
            if rule["route"] != SearchSpaceRoute.OUT_OF_MANDATE.value:
                continue
            with self.subTest(rule=rule["id"]):
                self.assertTrue(rule["when"], "an OUT rule may not be a catch-all")
                for criterion, status in rule["when"].items():
                    self.assertEqual(
                        status,
                        CriterionStatus.UNSATISFIED.value,
                        f"{rule['id']} keys on {criterion}={status}",
                    )

    def test_all_unknown_lands_in_the_watchlist(self):
        statuses = {c: CriterionStatus.UNKNOWN.value for c in SEARCH_SPACE_CRITERIA}
        self.assertEqual(resolve(statuses)[0], SearchSpaceRoute.WATCHLIST.value)

    def test_active_search_requires_all_eight_affirmative_criteria(self):
        """The only route that spends search resource demands every criterion."""

        for statuses in all_status_tuples():
            route, _ = resolve(statuses)
            if route == SearchSpaceRoute.ACTIVE_SEARCH.value:
                for criterion in SEARCH_SPACE_CRITERIA:
                    self.assertEqual(
                        statuses[criterion],
                        CriterionStatus.SATISFIED.value,
                        f"ACTIVE_SEARCH reached with {criterion}={statuses[criterion]}",
                    )

    def test_exactly_one_status_tuple_reaches_active_search(self):
        active = [
            statuses
            for statuses in all_status_tuples()
            if resolve(statuses)[0] == SearchSpaceRoute.ACTIVE_SEARCH.value
        ]
        self.assertEqual(len(active), 1)
        self.assertEqual(
            set(active[0].values()), {CriterionStatus.SATISFIED.value}
        )

    def test_a_declared_negative_on_any_criterion_blocks_active_search(self):
        """The four commercial criteria must be able to block, not just exist."""

        for criterion in SEARCH_SPACE_CRITERIA:
            with self.subTest(criterion=criterion):
                statuses = {
                    c: CriterionStatus.SATISFIED.value for c in SEARCH_SPACE_CRITERIA
                }
                statuses[criterion] = CriterionStatus.UNSATISFIED.value
                self.assertNotEqual(
                    resolve(statuses)[0], SearchSpaceRoute.ACTIVE_SEARCH.value
                )

    def test_an_unsatisfied_commercial_criterion_is_named_explicitly(self):
        """Named one by one so a parameterised loop cannot quietly shrink."""

        for criterion in (
            "differentiation_visible_preclinical",
            "defensible_ip_path",
            "plausible_buyer_partner_map",
            "time_window_compatible",
        ):
            with self.subTest(criterion=criterion):
                statuses = {
                    c: CriterionStatus.SATISFIED.value for c in SEARCH_SPACE_CRITERIA
                }
                statuses[criterion] = CriterionStatus.UNSATISFIED.value
                route, _ = resolve(statuses)
                self.assertNotEqual(route, SearchSpaceRoute.ACTIVE_SEARCH.value)

    def test_any_single_unknown_falls_through_to_the_watchlist(self):
        """UNKNOWN neither kills nor permits."""

        for criterion in SEARCH_SPACE_CRITERIA:
            with self.subTest(criterion=criterion):
                statuses = {
                    c: CriterionStatus.SATISFIED.value for c in SEARCH_SPACE_CRITERIA
                }
                statuses[criterion] = CriterionStatus.UNKNOWN.value
                self.assertEqual(
                    resolve(statuses)[0], SearchSpaceRoute.WATCHLIST.value
                )

    def test_partner_only_always_has_a_partner(self):
        """Otherwise the route name has no basis."""

        for statuses in all_status_tuples():
            route, rule_id = resolve(statuses)
            if route == SearchSpaceRoute.PARTNER_ONLY.value:
                self.assertEqual(
                    statuses["plausible_buyer_partner_map"],
                    CriterionStatus.SATISFIED.value,
                    f"{rule_id} reached PARTNER_ONLY with no partner map",
                )

    def test_every_route_is_reachable(self):
        reached = {resolve(statuses)[0] for statuses in all_status_tuples()}
        self.assertEqual(reached, {route.value for route in SearchSpaceRoute})

    def test_a_locked_position_with_value_and_a_partner_is_not_dropped(self):
        """The HER2/TROP2 case: high entry threshold, not a scientific failure."""

        statuses = {c: CriterionStatus.UNKNOWN.value for c in SEARCH_SPACE_CRITERIA}
        statuses.update(
            clinical_value_exists=CriterionStatus.SATISFIED.value,
            competitive_position_not_locked=CriterionStatus.UNSATISFIED.value,
            plausible_buyer_partner_map=CriterionStatus.SATISFIED.value,
        )
        route, rule_id = resolve(statuses)
        self.assertEqual(route, SearchSpaceRoute.PARTNER_ONLY.value)
        self.assertEqual(rule_id, "PARTNER-01")

    def test_no_asymmetric_advantage_but_partnerable_is_partner_only(self):
        statuses = {c: CriterionStatus.SATISFIED.value for c in SEARCH_SPACE_CRITERIA}
        statuses["asymmetric_evidence_advantage"] = CriterionStatus.UNSATISFIED.value
        route, rule_id = resolve(statuses)
        self.assertEqual(route, SearchSpaceRoute.PARTNER_ONLY.value)
        self.assertEqual(rule_id, "PARTNER-02")

    def test_everything_satisfied_is_active_search(self):
        statuses = {c: CriterionStatus.SATISFIED.value for c in SEARCH_SPACE_CRITERIA}
        self.assertEqual(resolve(statuses)[0], SearchSpaceRoute.ACTIVE_SEARCH.value)


class UnknownHandlingTests(unittest.TestCase):
    def test_the_declared_unknown_semantics_match_the_proven_behaviour(self):
        handling = POLICY["unknown_handling"]
        self.assertTrue(handling["unknown_is_not_failure"])
        self.assertTrue(handling["unknown_never_converts_to_unsatisfied"])
        self.assertTrue(handling["unknown_never_produces_out_of_mandate"])
        self.assertTrue(handling["out_of_mandate_requires_at_least_one_unsatisfied"])
        self.assertTrue(handling["unknown_blocks_active_search"])
        self.assertEqual(
            handling["unknown_blocks_active_search_scope"], "all_eight_criteria"
        )
        self.assertEqual(
            handling["all_unknown_resolves_to"], SearchSpaceRoute.WATCHLIST.value
        )


class ReassessmentTests(unittest.TestCase):
    def test_every_trigger_names_the_criteria_it_affects(self):
        triggers = POLICY["reassessment_triggers"]
        ids = [trigger["id"] for trigger in triggers]
        self.assertEqual(len(ids), len(set(ids)))
        for trigger in triggers:
            with self.subTest(trigger=trigger["id"]):
                self.assertTrue(trigger["trigger"].strip())
                affects = trigger["affects"]
                if affects != "all":
                    for criterion in affects:
                        self.assertIn(criterion, SEARCH_SPACE_CRITERIA)

    def test_every_criterion_has_a_specific_reopening_trigger(self):
        """The catch-all timer is excluded: it would make coverage trivial."""

        reopened = set()
        for trigger in POLICY["reassessment_triggers"]:
            affects = trigger["affects"]
            if affects == "all":
                continue
            reopened.update(affects)
        self.assertEqual(
            reopened,
            set(SEARCH_SPACE_CRITERIA),
            "a criterion is only reopened by the elapsed-time trigger",
        )

    def test_a_time_based_catch_all_trigger_exists(self):
        self.assertIn("all", [t["affects"] for t in POLICY["reassessment_triggers"]])

    def test_reassessment_does_not_rewrite_history(self):
        self.assertTrue(POLICY["reassessment_does_not_invalidate_history"])
        self.assertTrue(POLICY["reassessment_produces_new_admission"])


class BoundaryTests(unittest.TestCase):
    def test_no_route_is_a_scientific_kill(self):
        boundaries = POLICY["boundaries"]
        for key in (
            "policy_is_sponsor_relative_not_scientific",
            "no_route_is_a_scientific_kill",
            "out_of_mandate_is_not_a_kill",
            "partner_only_is_not_a_kill",
            "hot_targets_must_not_be_globally_deleted",
            "policy_does_not_evaluate_scientific_evidence",
            "policy_does_not_execute_a_gate",
            "policy_does_not_generate_targets_or_wedges",
            "policy_does_not_authorise_any_run",
            "active_search_does_not_authorise_target_generation",
        ):
            with self.subTest(key=key):
                self.assertTrue(boundaries[key])

    def test_the_policy_carries_no_disease_content(self):
        """The rules themselves must be disease-agnostic.

        Scoped to the normative sections rather than the whole file: the header
        comment and blocker_source legitimately name the WP2B run contract,
        whose filename contains the disease scope.
        """

        def strings(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield str(key)
                    yield from strings(value)
            elif isinstance(node, list):
                for item in node:
                    yield from strings(item)
            else:
                yield str(node)

        normative = " ".join(
            strings(
                {
                    section: POLICY[section]
                    for section in (
                        "criteria",
                        "routing",
                        "unknown_handling",
                        "reassessment_triggers",
                        "boundaries",
                    )
                }
            )
        )
        for banned in ("CRC", "MSS", "HER2", "TROP2", "KRAS", "BRAF", "colorectal"):
            with self.subTest(term=banned):
                self.assertNotIn(banned, normative)

    def test_src_contains_no_route_resolver(self):
        """The evaluator is test-only; the runtime must not route anything."""

        source = (
            ROOT / "src" / "contracts" / "search_space_admission.py"
        ).read_text(encoding="utf-8")
        for banned in ("def resolve", "def route(", "def derive", "ROUTE_RULES"):
            with self.subTest(term=banned):
                self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
