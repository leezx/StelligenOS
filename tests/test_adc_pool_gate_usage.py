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

REQUIRED_POOL_STATES = frozenset(
    {"active", "hold", "killed", "superseded", "reactivation-eligible"}
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

    def test_lock_dispositions_and_pool_states_stay_inside_the_contracts(self) -> None:
        valid_dispositions = {item.value for item in CandidateDisposition}
        for level in self.registry["levels"]:
            declared_states = set(level["pool_states"])
            self.assertEqual(declared_states, REQUIRED_POOL_STATES)
            for lock in level["locks"]:
                for outcome in lock["outcomes"]:
                    with self.subTest(outcome=outcome["outcome"]):
                        self.assertIn(outcome["disposition"], valid_dispositions)
                        self.assertIn(outcome["pool_state"], declared_states)

    def test_every_exclusion_declares_its_basis(self) -> None:
        for level in self.registry["levels"]:
            for lock in level["locks"]:
                for outcome in lock["outcomes"]:
                    if outcome["disposition"] != CandidateDisposition.EXCLUDE.value:
                        continue
                    with self.subTest(outcome=outcome["outcome"]):
                        self.assertTrue(outcome.get("exclusion_basis"))

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
