"""Verify docs/pools/adc_pool_gate_usage.yaml against the frozen Gate topology.

The registry records which criteria each ADC Pool level uses. These tests keep
that record from drifting away from the 45-Gate catalogue and from the
CandidateFilterResult semantics. They assert nothing about candidates, which
are data and live outside this repository.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from genmodules.gen_indication_endpoint_target.contracts import (
    CandidateDisposition,
    EvaluationStatus,
)
from src.capabilities.gates import GATE_IDS


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "docs" / "pools" / "adc_pool_gate_usage.yaml"
GATE_CATALOG_ROOT = (
    REPO_ROOT / "genmodules" / "assetgenos_catalog" / "gates" / "adc" / "v0.2"
)

# Fields the source document requires every pool candidate row to preserve.
# Source: Asset-Generation-OS-architecture.md#ADC pool漏斗gating, section 6.
REQUIRED_SNAPSHOT_FIELDS = (
    "pair_id",
    "clinical_context_ref",
    "target_ref",
    "pool_entry_level",
    "current_pool_level",
    "decision",
    "decision_reason_refs",
    "fatal_flags",
    "material_risks",
    "unknowns",
    "conflicts",
    "next_required_evidence",
    "last_assessed_at",
    "policy_version",
)

REQUIRED_STATE_VOCABULARIES = {
    "clinical_context_level": frozenset({"eligible", "hold", "superseded"}),
    "target_level": frozenset({"eligible", "hold", "killed"}),
    "pair_level": frozenset({"active", "hold", "reactivation-eligible"}),
}

# Evidence states that mean the evidence is simply not there yet. These must
# never exclude. "Searched completely and found nothing" is a separate state.
ABSENT_EVIDENCE_STATES = frozenset({"not_assessed", "absent_incomplete_search"})
COMPLETE_SEARCH_ABSENCE_STATE = "absent_after_complete_search"

REQUIRED_SEARCH_FIELDS = frozenset(
    {
        "search_complete",
        "search_policy_ref",
        "source_coverage_ref",
        "search_scope",
        "searched_at",
        "search_policy_version",
    }
)


def _load_registry() -> dict:
    with REGISTRY_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _catalog_cost_tiers() -> dict[str, str]:
    tiers: dict[str, str] = {}
    for path in sorted(GATE_CATALOG_ROOT.glob("*/*/*/gate.yaml")):
        with path.open(encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
        gate = document["gate"]
        tiers[gate["gate_id"]] = gate["runtime"]["cost_tier"]
    return tiers


class ADCPoolGateUsageRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = _load_registry()
        cls.levels = {entry["level"]: entry for entry in cls.registry["levels"]}

    def test_registry_binds_to_the_frozen_topology_without_changing_it(self) -> None:
        header = self.registry["registry"]
        self.assertEqual(header["gate_count"], len(GATE_IDS))
        self.assertEqual(header["gate_count"], 45)
        self.assertEqual(header["topology_change"], "none")
        self.assertEqual(header["modality"], "ADC")

    def test_declared_levels_match_the_level_entries(self) -> None:
        self.assertEqual(
            list(self.registry["registry"]["defined_levels"]), list(self.levels)
        )
        self.assertEqual(len(self.levels), len(self.registry["levels"]))

    def test_level_01_executes_no_gate_and_produces_no_gate_result(self) -> None:
        level = self.levels["01"]
        self.assertEqual(level["gates_executed"], [])
        self.assertEqual(level["gates_executed_count"], 0)
        self.assertEqual(level["result_contract"], "CandidateFilterResult")
        self.assertIs(level["result_is_gate_result"], False)
        self.assertEqual(level["gate_scores_written"], "none")

    def test_level_01_lists_every_gate_as_not_run(self) -> None:
        not_run = self.levels["01"]["gates_not_run"]
        self.assertEqual(len(not_run), len(set(not_run)), "duplicate gate id")
        self.assertEqual(set(not_run), set(GATE_IDS))

    def test_level_01_preserves_the_full_evaluation_status_domain(self) -> None:
        preserved = self.levels["01"]["evaluation_status_preserved"]
        self.assertEqual(
            set(preserved), {status.value for status in EvaluationStatus}
        )

    def test_borrowed_gate_responsibilities_are_real_gates_and_not_passes(self) -> None:
        tiers = _catalog_cost_tiers()
        self.assertEqual(len(tiers), len(GATE_IDS))
        for level in self.registry["levels"]:
            for lock in level["locks"]:
                gate_id = lock["gate_responsibility_borrowed"]
                with self.subTest(lock=lock["lock_id"]):
                    self.assertIn(gate_id, GATE_IDS)
                    self.assertIs(lock["constitutes_gate_pass"], False)
                    self.assertEqual(
                        lock["borrowed_gate_cost_tier"], tiers[gate_id]
                    )

    def test_lock_states_are_scoped_to_their_granularity(self) -> None:
        valid_dispositions = {item.value for item in CandidateDisposition}
        for level in self.registry["levels"]:
            vocabularies = level["state_vocabularies"]
            self.assertEqual(
                {key: frozenset(value) for key, value in vocabularies.items()},
                REQUIRED_STATE_VOCABULARIES,
            )
            for lock in level["locks"]:
                allowed = set(vocabularies[lock["granularity"]])
                for outcome in lock["outcomes"]:
                    with self.subTest(outcome=outcome["outcome"]):
                        self.assertIn(outcome["disposition"], valid_dispositions)
                        self.assertIn(outcome["resulting_state"], allowed)

    def test_every_exclusion_declares_its_basis(self) -> None:
        for level in self.registry["levels"]:
            for lock in level["locks"]:
                for outcome in lock["outcomes"]:
                    if outcome["disposition"] != CandidateDisposition.EXCLUDE.value:
                        continue
                    with self.subTest(outcome=outcome["outcome"]):
                        self.assertTrue(outcome.get("exclusion_basis"))
                        self.assertTrue(outcome.get("disposition_semantics"))

    def test_missing_or_unassessed_evidence_can_never_exclude(self) -> None:
        """Blocker 1: absent evidence defers; it must not shrink the pool."""

        for level in self.registry["levels"]:
            standard = level["evidence_standard"]
            self.assertEqual(
                set(standard["absent_evidence_states"]), ABSENT_EVIDENCE_STATES
            )
            for lock in level["locks"]:
                for outcome in lock["outcomes"]:
                    if outcome["evidence_state"] not in ABSENT_EVIDENCE_STATES:
                        continue
                    with self.subTest(outcome=outcome["outcome"]):
                        self.assertEqual(
                            outcome["disposition"], CandidateDisposition.DEFER.value
                        )
                        self.assertEqual(outcome["resulting_state"], "hold")

    def test_only_a_completed_search_may_remove_a_pair_from_the_active_pool(
        self,
    ) -> None:
        """Blocker 1: EXCLUDE on absence requires a completeness record."""

        for level in self.registry["levels"]:
            standard = level["evidence_standard"]
            self.assertEqual(
                standard["complete_search_absence_state"],
                COMPLETE_SEARCH_ABSENCE_STATE,
            )
            self.assertEqual(
                standard["complete_search_absence_semantics"],
                "EXCLUDE_FROM_ACTIVE_POOL",
            )
            self.assertIs(
                standard["complete_search_absence_is_scientific_disproof"], False
            )
            self.assertIs(standard["complete_search_requires_completeness_record"], True)

            absence_exclusions = [
                outcome
                for lock in level["locks"]
                for outcome in lock["outcomes"]
                if outcome["evidence_state"] == COMPLETE_SEARCH_ABSENCE_STATE
            ]
            self.assertTrue(absence_exclusions, "no complete-search outcome declared")
            for outcome in absence_exclusions:
                with self.subTest(outcome=outcome["outcome"]):
                    self.assertEqual(
                        outcome["disposition"], CandidateDisposition.EXCLUDE.value
                    )
                    self.assertEqual(
                        outcome["disposition_semantics"], "EXCLUDE_FROM_ACTIVE_POOL"
                    )
                    self.assertIs(outcome["is_scientific_disproof"], False)
                    self.assertIs(outcome["is_killed"], False)
                    self.assertEqual(outcome["resulting_state"], "reactivation-eligible")
                    self.assertIs(outcome["requires_search_completeness_record"], True)
                    self.assertEqual(
                        set(outcome["required_search_fields"]), REQUIRED_SEARCH_FIELDS
                    )

    def test_completeness_fields_are_carried_by_the_snapshot(self) -> None:
        columns = set(self.levels["01"]["snapshot_columns"])
        for field in REQUIRED_SEARCH_FIELDS:
            with self.subTest(field=field):
                self.assertIn(f"lock_03_{field}", columns)

    def test_definitional_exclusions_are_never_reactivation_eligible(self) -> None:
        pair_states = set(
            self.registry["levels"][0]["state_vocabularies"]["pair_level"]
        )
        self.assertIn("reactivation-eligible", pair_states)
        for level in self.registry["levels"]:
            for lock in level["locks"]:
                for outcome in lock["outcomes"]:
                    if (
                        outcome.get("disposition_semantics")
                        != "EXCLUDE_DEFINITIONALLY_INELIGIBLE"
                    ):
                        continue
                    with self.subTest(outcome=outcome["outcome"]):
                        self.assertNotEqual(
                            outcome["resulting_state"], "reactivation-eligible"
                        )
                        self.assertIn(outcome["resulting_state"], {"killed", "superseded"})

    def test_locks_run_cheapest_granularity_first(self) -> None:
        granularity_order = self.registry["ordering_principle"]["granularity_order"]
        for level in self.registry["levels"]:
            locks = sorted(level["locks"], key=lambda lock: lock["run_order"])
            self.assertEqual(
                [lock["run_order"] for lock in locks],
                list(range(1, len(locks) + 1)),
                "run_order must be a permutation of 1..n",
            )
            indices = [granularity_order.index(lock["granularity"]) for lock in locks]
            self.assertEqual(indices, sorted(indices), "granularity must not regress")

    def test_rna_evidence_never_satisfies_the_surface_protein_lock(self) -> None:
        standard = self.levels["01"]["evidence_standard"]
        self.assertIn("LOCK-01", standard["rna_may_not_satisfy"])
        self.assertNotIn("LOCK-01", standard["rna_may_satisfy"])
        self.assertIs(standard["public_evidence_only"], True)
        self.assertIs(standard["model_domain_knowledge_alone_admits_pair"], False)

    def test_absent_evidence_defers_and_never_excludes(self) -> None:
        standard = self.levels["01"]["evidence_standard"]
        self.assertEqual(
            standard["absent_evidence_disposition"], CandidateDisposition.DEFER.value
        )
        self.assertIs(standard["absent_evidence_may_exclude"], False)
        self.assertIs(standard["null_is_not_zero"], True)

    def test_snapshot_preserves_every_required_history_field(self) -> None:
        columns = self.levels["01"]["snapshot_columns"]
        self.assertEqual(len(columns), len(set(columns)), "duplicate column")
        for field in REQUIRED_SNAPSHOT_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, columns)

    def test_level_01_is_recorded_as_not_yet_authorized(self) -> None:
        level = self.levels["01"]
        self.assertEqual(level["execution_status"], "not_authorized_not_executed")
        self.assertTrue(level["execution_blockers"])
        for blocker in level["execution_blockers"]:
            self.assertTrue(blocker["statement"].strip())

    def test_pool_objects_separate_eligibility_audit_from_pair_states(self) -> None:
        """Blocker 2: only pair-level objects may carry a pair state."""

        objects = {item["id"]: item for item in self.levels["01"]["pool_objects"]}
        self.assertEqual(
            set(objects),
            {
                "raw_enumeration_matrix",
                "context_eligibility_audit",
                "target_eligibility_audit",
                "eligible_universe_index",
                "pool_level_01_snapshot",
            },
        )
        for name in ("raw_enumeration_matrix", "context_eligibility_audit",
                     "target_eligibility_audit"):
            self.assertIs(objects[name]["assigns_pair_state"], False)
        for name in ("eligible_universe_index", "pool_level_01_snapshot"):
            self.assertIs(objects[name]["assigns_pair_state"], True)
        self.assertEqual(
            set(self.levels["01"]["excluded_from_pair_reconciliation"]),
            {"killed", "superseded"},
        )

    def test_counting_identities_are_consistent_on_a_worked_example(self) -> None:
        """Blocker 2: the declared identities must yield one denominator."""

        identities = {item["id"]: item for item in self.levels["01"]["counting_identities"]}
        self.assertEqual(set(identities), {f"CNT-0{n}" for n in range(1, 6)})

        counts = {
            "raw_contexts": 10,
            "eligible_contexts": 6,
            "hold_contexts": 3,
            "superseded_contexts": 1,
            "raw_targets": 100,
            "eligible_targets": 70,
            "hold_targets": 20,
            "killed_targets": 10,
            "raw_matrix": 1000,
            "eligible_universe_index": 420,
            "active": 120,
            "hold_pairs": 200,
            "reactivation_eligible_pairs": 100,
        }
        self._assert_identities_hold(identities, counts)

    def test_superseding_a_context_removes_exactly_one_column(self) -> None:
        """Blocker 2: how the universe changes when a context is superseded."""

        identities = {item["id"]: item for item in self.levels["01"]["counting_identities"]}
        before = {
            "raw_contexts": 10, "eligible_contexts": 6, "hold_contexts": 3,
            "superseded_contexts": 1, "raw_targets": 100, "eligible_targets": 70,
            "hold_targets": 20, "killed_targets": 10, "raw_matrix": 1000,
            "eligible_universe_index": 420, "active": 120, "hold_pairs": 200,
            "reactivation_eligible_pairs": 100,
        }
        after = dict(before)
        after["eligible_contexts"] -= 1
        after["superseded_contexts"] += 1
        after["eligible_universe_index"] = (
            after["eligible_contexts"] * after["eligible_targets"]
        )
        after["hold_pairs"] -= before["eligible_targets"]

        self.assertEqual(
            before["eligible_universe_index"] - after["eligible_universe_index"],
            before["eligible_targets"],
        )
        # The raw matrix is unchanged: superseding is audit history, not deletion.
        self.assertEqual(after["raw_matrix"], before["raw_matrix"])
        self.assertEqual(after["raw_contexts"], before["raw_contexts"])
        self._assert_identities_hold(identities, after)

    def test_killing_a_target_removes_exactly_one_row(self) -> None:
        """Blocker 2: how the universe changes when a target is killed."""

        identities = {item["id"]: item for item in self.levels["01"]["counting_identities"]}
        before = {
            "raw_contexts": 10, "eligible_contexts": 6, "hold_contexts": 3,
            "superseded_contexts": 1, "raw_targets": 100, "eligible_targets": 70,
            "hold_targets": 20, "killed_targets": 10, "raw_matrix": 1000,
            "eligible_universe_index": 420, "active": 120, "hold_pairs": 200,
            "reactivation_eligible_pairs": 100,
        }
        after = dict(before)
        after["eligible_targets"] -= 1
        after["killed_targets"] += 1
        after["eligible_universe_index"] = (
            after["eligible_contexts"] * after["eligible_targets"]
        )
        after["hold_pairs"] -= before["eligible_contexts"]

        self.assertEqual(
            before["eligible_universe_index"] - after["eligible_universe_index"],
            before["eligible_contexts"],
        )
        self.assertEqual(after["raw_matrix"], before["raw_matrix"])
        self.assertEqual(after["raw_targets"], before["raw_targets"])
        self._assert_identities_hold(identities, after)

    def test_pair_reconciliation_excludes_killed_and_superseded(self) -> None:
        """Blocker 2: killed/superseded must not enter the pair-state sum."""

        cnt3 = next(
            item
            for item in self.levels["01"]["counting_identities"]
            if item["id"] == "CNT-03"
        )
        self.assertEqual(cnt3["lhs"], "eligible_universe_index")
        summands = set(cnt3["rhs_sum"])
        self.assertEqual(summands, {"active", "hold_pairs", "reactivation_eligible_pairs"})
        for forbidden in ("killed_targets", "superseded_contexts", "killed", "superseded"):
            self.assertNotIn(forbidden, summands)

    def _assert_identities_hold(self, identities: dict, counts: dict) -> None:
        for identity_id, identity in sorted(identities.items()):
            with self.subTest(identity=identity_id):
                lhs = counts[identity["lhs"]]
                if "rhs_product" in identity:
                    rhs = 1
                    for name in identity["rhs_product"]:
                        rhs *= counts[name]
                else:
                    rhs = sum(counts[name] for name in identity["rhs_sum"])
                self.assertEqual(lhs, rhs, identity["identity"])

    def test_recorded_gaps_are_not_silently_resolved(self) -> None:
        gaps = self.registry["recorded_gaps"]
        self.assertTrue(gaps)
        ids = [gap["id"] for gap in gaps]
        self.assertEqual(len(ids), len(set(ids)), "duplicate gap id")
        known_levels = set(self.levels) | {"02", "03"}
        for gap in gaps:
            with self.subTest(gap=gap["id"]):
                self.assertTrue(gap["statement"].strip())
                self.assertIn(gap["affects_level"], known_levels)


if __name__ == "__main__":
    unittest.main()
