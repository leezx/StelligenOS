"""Verify docs/pools/adc_pool_level_01_input_binding.yaml.

The binding pins Level 01's inputs to externally stored, separately approved
run artefacts. These tests check the binding's internal consistency and its
agreement with the merged Level 01 contract. They never read the external
artefacts: those live outside the repository, so the checksums recorded here
are audit metadata, not something this suite can or should resolve.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from genmodules.gen_indication_endpoint_target.contracts import CandidateDisposition


REPO_ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = REPO_ROOT / "docs" / "pools" / "adc_pool_level_01_input_binding.yaml"
LEVEL_CONTRACT_PATH = REPO_ROOT / "docs" / "pools" / "adc_pool_gate_usage.yaml"

QUARANTINED_STATUS = "UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED"
# Targets that exist only in the quarantined 2026-08-04 run.
QUARANTINE_ONLY_TARGETS = ("GPA33", "LY6G6D", "TNFRSF12A", "CEACAM6")


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class InputBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding = _load(BINDING_PATH)
        cls.level = {
            entry["level"]: entry for entry in _load(LEVEL_CONTRACT_PATH)["levels"]
        }["01"]

    def test_binding_targets_the_merged_level_01_contract(self) -> None:
        header = self.binding["binding"]
        self.assertEqual(header["level"], "01")
        self.assertEqual(
            header["level_contract_ref"], "docs/pools/adc_pool_gate_usage.yaml"
        )
        self.assertTrue(LEVEL_CONTRACT_PATH.exists())
        self.assertEqual(header["execution_status"], "not_authorized_not_executed")
        self.assertIs(header["requires_new_enumeration_run"], False)

    def test_every_accepted_source_names_its_approval(self) -> None:
        sources = self.binding["accepted_sources"]
        self.assertTrue(sources)
        for source in sources:
            with self.subTest(source=source["source_id"]):
                self.assertEqual(source["decision"], "APPROVE")
                self.assertIsInstance(source["authorising_pr"], int)
                record = REPO_ROOT / source["authorising_record"]
                self.assertTrue(record.exists(), f"missing record: {record}")
                self.assertIn("APPROVE", record.read_text(encoding="utf-8"))
                self.assertTrue(source["run_dir"].startswith("external:"))

    def test_every_pinned_file_has_a_sha256(self) -> None:
        for source in self.binding["accepted_sources"]:
            for item in source["files"]:
                with self.subTest(path=item["path"]):
                    digest = item["sha256"]
                    self.assertEqual(len(digest), 64, digest)
                    self.assertTrue(
                        all(c in "0123456789abcdef" for c in digest), digest
                    )

    def test_quarantined_runs_are_barred_not_merely_unlisted(self) -> None:
        barred = self.binding["barred_sources"]
        self.assertEqual(len(barred), 2)
        accepted_dirs = {s["run_dir"] for s in self.binding["accepted_sources"]}
        for source in barred:
            with self.subTest(source=source["source_id"]):
                self.assertEqual(source["status"], QUARANTINED_STATUS)
                self.assertTrue(source["barred_content"])
                self.assertNotIn(source["run_dir"], accepted_dirs)
        self.assertEqual({s["related_pr"] for s in barred}, {53, 54})

    def test_scope_consequence_arithmetic_is_stated_and_correct(self) -> None:
        scope = self.binding["scope_consequences"]
        self.assertEqual(
            scope["raw_enumeration_matrix_pairs"],
            scope["raw_clinical_contexts"] * scope["raw_targets"],
        )
        enumeration = next(
            s
            for s in self.binding["accepted_sources"]
            if s["source_id"] == "crc_enumeration_20260802"
        )
        universe = next(
            f for f in enumeration["files"]
            if f["path"] == "indication_endpoint_universe.tsv"
        )
        catalog = next(
            f for f in enumeration["files"]
            if f["path"] == "target_evidence_catalog.tsv"
        )
        self.assertEqual(scope["raw_clinical_contexts"], universe["distinct_indications"])
        self.assertEqual(scope["raw_targets"], catalog["rows"])

    def test_lock_02_ceiling_covers_every_context_and_forbids_upgrades(self) -> None:
        ceiling = self.binding["lock_02_status_ceiling"]
        self.assertEqual(
            sum(entry["count"] for entry in ceiling),
            self.binding["scope_consequences"]["raw_clinical_contexts"],
        )
        outcomes = {
            outcome["outcome"]: outcome
            for lock in self.level["locks"]
            if lock["lock_id"] == "LOCK-02"
            for outcome in lock["outcomes"]
        }
        for entry in ceiling:
            with self.subTest(status=entry["source_status"]):
                self.assertIn(entry["max_outcome"], outcomes)
                # Anything not calibrated must be forced to DEFER, never RETAIN.
                if entry["calibration"] != "calibrated":
                    self.assertEqual(
                        entry["forced_disposition"], CandidateDisposition.DEFER.value
                    )
                    self.assertEqual(
                        outcomes[entry["max_outcome"]]["disposition"],
                        CandidateDisposition.DEFER.value,
                    )
        calibrated = [e for e in ceiling if e["calibration"] == "calibrated"]
        self.assertEqual(len(calibrated), 1)
        self.assertEqual(calibrated[0]["max_outcome"], "validated_unmet_context")

    def test_prior_disposition_labels_are_not_reusable_as_lock_01_output(self) -> None:
        semantics = self.binding["lock_01_input_semantics"]
        self.assertIs(semantics["catalog_disposition_is_candidate_filter_result"], False)
        self.assertIs(semantics["may_be_inherited_as_lock_01_outcome"], False)
        # The prior labels must not collide with CandidateDisposition values.
        prior = {v.lower() for v in semantics["catalog_disposition_values"]}
        contract = {item.value.lower() for item in CandidateDisposition}
        self.assertEqual(prior & contract, set())

    def test_linkage_rules_never_exclude(self) -> None:
        rules = self.binding["lock_03_linkage_rules"]
        lock_03 = next(l for l in self.level["locks"] if l["lock_id"] == "LOCK-03")
        valid_outcomes = {o["outcome"] for o in lock_03["outcomes"]}
        for rule in rules["rules"]:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["outcome"], valid_outcomes)
                self.assertIn(
                    rule["disposition"],
                    {CandidateDisposition.RETAIN.value, CandidateDisposition.DEFER.value},
                )
        self.assertEqual(
            rules["evidence_granularity"], "disease_level_not_subgroup_level"
        )

    def test_complete_search_exclusion_is_unavailable_with_this_input(self) -> None:
        rules = self.binding["lock_03_linkage_rules"]
        self.assertIs(rules["no_known_linkage_after_complete_search_available"], False)
        self.assertTrue(rules["no_known_linkage_unavailable_reason"].strip())
        forbidding = [
            r for r in self.binding["output_validation"]["additional_rules"]
            if "no_known_linkage_after_complete_search" in r["rule"]
        ]
        self.assertTrue(forbidding, "no validation rule forbids the outcome")

    def test_unreviewed_evidence_may_enter_level_01_but_not_advance(self) -> None:
        rules = self.binding["lock_03_linkage_rules"]
        self.assertIs(rules["machine_extracted_evidence_satisfies_existence"], True)
        self.assertIs(rules["requires_review_status_column"], True)
        constraint = rules["carry_forward_constraint"]
        self.assertIn("Level 02", constraint)
        self.assertTrue(constraint.strip())

    def test_measured_limits_of_the_evidence_package_are_recorded(self) -> None:
        evidence = next(
            s
            for s in self.binding["accepted_sources"]
            if s["source_id"] == "crc_target_evidence_20260801"
        )
        limits = evidence["measured_limits"]
        self.assertEqual(limits["granularity"], "target_level_only")
        self.assertIs(limits["has_clinical_context_column"], False)
        self.assertEqual(
            limits["all_units_review_status"],
            "machine_extracted_requires_human_review",
        )
        self.assertLess(
            limits["expert_review_batches_passed"],
            limits["expert_review_batches_total"],
        )

    def test_authorisation_scope_is_explicit_and_bounded(self) -> None:
        self.assertTrue(self.binding["authorises"])
        not_authorised = " ".join(self.binding["not_authorised"])
        for phrase in ("枚举", "Gate", "Level 02", "endpoint"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, not_authorised)

    def test_validation_rules_bar_quarantine_only_targets(self) -> None:
        rules = " ".join(
            r["rule"] for r in self.binding["output_validation"]["additional_rules"]
        )
        for target in QUARANTINE_ONLY_TARGETS:
            with self.subTest(target=target):
                self.assertIn(target, rules)
        ids = [r["id"] for r in self.binding["output_validation"]["additional_rules"]]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
