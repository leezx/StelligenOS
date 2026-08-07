import unittest
from pathlib import Path

import yaml

from src.contracts.search_space_admission import (
    SEARCH_SPACE_CRITERIA,
    CriterionStatus,
    SearchSpaceAdmission,
    SearchSpaceCriterionResult,
    SearchSpaceRoute,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "search_space_admission.yaml"


def criterion_results() -> tuple[SearchSpaceCriterionResult, ...]:
    return tuple(
        SearchSpaceCriterionResult(
            criterion_id=criterion,
            status=CriterionStatus.UNKNOWN,
            evidence_ref=f"external:evidence/{criterion}",
        )
        for criterion in SEARCH_SPACE_CRITERIA
    )


class SearchSpaceAdmissionContractTests(unittest.TestCase):
    def test_contract_freezes_four_routes_and_eight_criteria(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        self.assertEqual(document["contract"]["contract_id"], "SearchSpaceAdmission@0.1.0")
        self.assertEqual(
            document["route_values"],
            ["ACTIVE_SEARCH", "WATCHLIST", "PARTNER_ONLY", "OUT_OF_MANDATE"],
        )
        self.assertEqual(document["criteria"], list(SEARCH_SPACE_CRITERIA))
        self.assertIn("unknown_is_not_kill", document["contract"]["invariants"])

    def test_unknown_is_preserved_and_route_is_not_a_gate_result(self):
        admission = SearchSpaceAdmission(
            admission_id="admission-1",
            opportunity_ref="external:opportunity/1",
            sponsor_profile_ref="external:sponsor-profile/1",
            program_thesis_ref="external:program-thesis/1",
            criterion_results=criterion_results(),
            route=SearchSpaceRoute.WATCHLIST,
            route_policy_ref="external:policy/search-space/1",
            rationale_ref="external:rationale/1",
            source_refs=("external:source/1",),
        )
        self.assertEqual(admission.route, SearchSpaceRoute.WATCHLIST)
        self.assertTrue(
            all(result.status is CriterionStatus.UNKNOWN for result in admission.criterion_results)
        )
        self.assertNotIn("KILL", SearchSpaceRoute.__members__)

    def test_all_criteria_are_required_exactly_once(self):
        results = criterion_results()
        with self.assertRaises(ValueError):
            SearchSpaceAdmission(
                admission_id="missing-criterion",
                opportunity_ref="external:opportunity/1",
                sponsor_profile_ref="external:sponsor-profile/1",
                program_thesis_ref="external:program-thesis/1",
                criterion_results=results[:-1],
                route=SearchSpaceRoute.ACTIVE_SEARCH,
                route_policy_ref="external:policy/1",
                rationale_ref="external:rationale/1",
                source_refs=("external:source/1",),
            )
        with self.assertRaises(ValueError):
            SearchSpaceCriterionResult(
                criterion_id="not-a-criterion",
                status=CriterionStatus.SATISFIED,
                evidence_ref="external:evidence/invalid",
            )

    def test_cross_boundary_refs_must_be_external(self):
        with self.assertRaises(ValueError):
            SearchSpaceAdmission(
                admission_id="local-ref",
                opportunity_ref="local:opportunity/1",
                sponsor_profile_ref="external:sponsor-profile/1",
                program_thesis_ref="external:program-thesis/1",
                criterion_results=criterion_results(),
                route=SearchSpaceRoute.PARTNER_ONLY,
                route_policy_ref="external:policy/1",
                rationale_ref="external:rationale/1",
                source_refs=("external:source/1",),
            )

    def test_admission_does_not_execute_downstream_work(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        invariants = document["contract"]["invariants"]
        self.assertIn("route_does_not_delete_or_mutate_the_candidate", invariants)
        self.assertIn("route_does_not_authorise_gate_or_asset_generation_execution", invariants)


if __name__ == "__main__":
    unittest.main()
