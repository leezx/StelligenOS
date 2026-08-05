"""Verify docs/pools/evgap_01_surface_localization_extraction.yaml.

The extraction contract discharges EVGAP-01 by admitting one pinned database
version as an approved source and freezing how its fields map onto LOCK-01's
RQ-01/RQ-02/RQ-03. These tests check internal consistency and agreement with the
merged Level 01 contracts. They never read the external database: it lives
outside the repository, so the recorded checksums are audit metadata.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from genmodules.gen_indication_endpoint_target.contracts import CandidateDisposition


REPO_ROOT = Path(__file__).resolve().parents[1]
POOLS = REPO_ROOT / "docs" / "pools"
EXTRACTION_PATH = POOLS / "evgap_01_surface_localization_extraction.yaml"
BINDING_PATH = POOLS / "adc_pool_level_01_input_binding.yaml"
LEVEL_CONTRACT_PATH = POOLS / "adc_pool_gate_usage.yaml"

# Level 02 / T7 material that must never enter LOCK-01.
FORBIDDEN_FILES = frozenset(
    {
        "tumor_surface_measurement.tsv",
        "tumor_protein_context.tsv",
        "treatment_surface_response.tsv",
        "receptor_evidence.tsv",
    }
)


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class Evgap01ExtractionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load(EXTRACTION_PATH)
        cls.binding = _load(BINDING_PATH)
        cls.level = {
            entry["level"]: entry for entry in _load(LEVEL_CONTRACT_PATH)["levels"]
        }["01"]

    def test_contract_targets_the_registered_gap(self) -> None:
        head = self.doc["extraction"]
        self.assertEqual(head["discharges_gap"], "EVGAP-01")
        self.assertEqual(head["serves_lock"], "LOCK-01")
        gaps = {g["id"]: g for g in self.binding["evidence_gaps"]}
        self.assertIn("EVGAP-01", gaps)
        self.assertEqual(gaps["EVGAP-01"]["blocks"], "LOCK-01")
        self.assertEqual(head["execution_status"], "not_authorized_not_executed")
        self.assertIs(head["authorises_extraction_run"], True)
        self.assertIs(head["authorises_level_01_execution"], False)
        self.assertIs(head["requires_followup_binding_pr"], True)

    def test_source_admission_is_declared_as_not_previously_approved(self) -> None:
        request = self.doc["source_admission_request"]
        self.assertIs(request["previously_approved"], False)
        self.assertTrue(request["previously_approved_evidence"].strip())
        self.assertTrue(request["root"].startswith("external:"))
        self.assertEqual(request["dataset_version"], "0.3.0")
        for item in request["files"]:
            with self.subTest(path=item["path"]):
                digest = item["sha256"]
                self.assertEqual(len(digest), 64, digest)
                self.assertTrue(all(c in "0123456789abcdef" for c in digest))

    def test_inherited_guards_cover_the_repository_rules(self) -> None:
        guards = {g["guard"]: g for g in
                  self.doc["source_admission_request"]["inherited_semantics_guards"]}
        # The two that previous review rounds turned on must be present and false.
        for name in ("absence_is_negative_evidence",
                     "membrane_topology_is_independent_surface_localization"):
            with self.subTest(guard=name):
                self.assertIn(name, guards)
                self.assertIs(guards[name]["value"], False)
                self.assertTrue(guards[name]["matches_repo_rule"].strip())
        self.assertIn("excluded_rna_source", guards)

    def test_scope_is_the_approved_target_axis_only(self) -> None:
        scope = self.doc["scope"]
        self.assertIs(scope["new_targets_allowed"], False)
        self.assertEqual(
            scope["target_count"], self.binding["scope_consequences"]["raw_targets"]
        )
        self.assertEqual(
            scope["target_axis_sha256"],
            next(
                f["sha256"]
                for s in self.binding["accepted_sources"]
                for f in s["files"]
                if f["path"] == "target_evidence_catalog.tsv"
            ),
        )
        self.assertEqual(
            scope["measured_coverage_in_reference"]
            + scope["measured_absent_from_reference"],
            scope["target_count"],
        )
        self.assertEqual(
            len(scope["measured_absent_targets"]), scope["measured_absent_from_reference"]
        )

    def test_level_02_material_is_barred(self) -> None:
        barred = {item["path"] for item in self.doc["barred_files"]}
        self.assertEqual(barred, FORBIDDEN_FILES)
        for item in self.doc["barred_files"]:
            self.assertTrue(item["reason"].strip())
        allowed = set(self.doc["allowed_fields"]["from_surfaceome_consensus"]) | set(
            self.doc["allowed_fields"]["from_source_evidence"]
        )
        for item in self.doc["barred_fields"]:
            with self.subTest(field=item["field"]):
                self.assertNotIn(item["field"], allowed)
                self.assertTrue(item["reason"].strip())
        # Nothing capped for T7 may leak into the field whitelist.
        self.assertNotIn("full_t7_gate_confidence_cap", allowed)

    def test_rq_01_never_counts_topology_or_rna(self) -> None:
        rq1 = self.doc["rq_01_plasma_membrane_localization"]
        self.assertGreaterEqual(rq1["minimum_independent_families"], 2)
        self.assertIs(rq1["topology_counts_as_family"], False)
        self.assertIs(rq1["generic_membrane_counts_as_family"], False)
        self.assertIs(rq1["rna_may_satisfy"], False)
        self.assertEqual(len(rq1["independent_families"]), 3)

    def test_rq_02_has_both_paths_and_excludes_luminal_domains(self) -> None:
        rq2 = self.doc["rq_02_extracellular_domain"]
        paths = {p["path_id"]: p for p in rq2["paths"]}
        self.assertEqual(set(paths), {"ECD-a", "ECD-b"})
        # The GPI path exists to correct a representation artefact, and must say so.
        self.assertTrue(paths["ECD-b"]["rationale_note"].strip())
        self.assertEqual(len(paths["ECD-b"]["measured_targets"]),
                         paths["ECD-b"]["measured_count"])
        self.assertIs(rq2["luminal_domain_is_not_extracellular"], True)
        self.assertIn("LAMP1", rq2["luminal_domain_note"])
        eligible = next(r for r in self.doc["derivation_rules"] if r["id"] == "E1-01")
        self.assertEqual(
            sum(p["measured_count"] for p in rq2["paths"]), eligible["expected_count"]
        )

    def test_rq_03_requires_protein_level_provenance(self) -> None:
        rq3 = self.doc["rq_03_protein_level_provenance"]
        self.assertIs(rq3["rna_derived_rows_admissible"], False)
        for field in ("source_id", "source_release", "source_url", "license"):
            self.assertIn(field, rq3["required_fields"])
        allowed = set(self.doc["allowed_fields"]["from_source_evidence"])
        self.assertTrue(set(rq3["required_fields"]) <= allowed)

    def test_derivation_rules_are_total_and_never_exclude(self) -> None:
        rules = self.doc["derivation_rules"]
        ids = [r["id"] for r in rules]
        self.assertEqual(len(ids), len(set(ids)))
        outcomes = {
            o["outcome"]: o
            for lock in self.level["locks"]
            if lock["lock_id"] == "LOCK-01"
            for o in lock["outcomes"]
        }
        for rule in rules:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["lock_01_outcome"], outcomes)
                self.assertNotEqual(
                    rule["disposition"], CandidateDisposition.EXCLUDE.value
                )
                self.assertEqual(
                    rule["resulting_state"],
                    outcomes[rule["lock_01_outcome"]]["resulting_state"],
                )
        self.assertEqual(
            sum(r["expected_count"] for r in rules), self.doc["scope"]["target_count"]
        )
        # Every rule that names targets must name exactly as many as it counts.
        for rule in rules:
            if "measured_targets" in rule:
                with self.subTest(rule=rule["id"]):
                    self.assertEqual(
                        len(rule["measured_targets"]), rule["expected_count"]
                    )

    def test_exclusion_outcomes_remain_unavailable(self) -> None:
        unavailable = {u["outcome"]: u for u in self.doc["unavailable_outcomes"]}
        self.assertIn("not_surface_target", unavailable)
        self.assertIn("identity_unresolved", unavailable)
        for item in unavailable.values():
            self.assertTrue(item["reason"].strip())
        produced = {r["lock_01_outcome"] for r in self.doc["derivation_rules"]}
        self.assertEqual(produced & set(unavailable), set())
        forbidding = [
            r for r in self.doc["output_validation"]
            if "not_surface_target" in r["rule"]
        ]
        self.assertTrue(forbidding)

    def test_predicted_shape_reconciles_with_the_rules(self) -> None:
        shape = self.doc["predicted_result_shape"]
        self.assertEqual(
            shape["eligible"] + shape["hold"] + shape["killed"], shape["targets_total"]
        )
        self.assertEqual(shape["targets_total"], self.doc["scope"]["target_count"])
        self.assertEqual(shape["killed"], 0)
        by_id = {r["id"]: r for r in self.doc["derivation_rules"]}
        self.assertEqual(by_id["E1-01"]["expected_count"], shape["eligible"])
        breakdown = shape["hold_breakdown"]
        self.assertEqual(sum(breakdown.values()), shape["hold"])
        for key, count in breakdown.items():
            with self.subTest(key=key):
                self.assertEqual(by_id[key.split("_")[0]]["expected_count"], count)
        self.assertEqual(sum(shape["eligible_via_path"].values()), shape["eligible"])

    def test_mandatory_findings_preserve_the_uncomfortable_ones(self) -> None:
        findings = {f["id"]: f["finding"] for f in self.doc["mandatory_findings"]}
        self.assertEqual(set(findings), {"MF-01", "MF-02", "MF-03"})
        # The finding that contradicts the earlier consensus must be kept.
        self.assertIn("GUCY2C", findings["MF-01"])
        deferred = [
            r for r in self.doc["derivation_rules"]
            if "GUCY2C" in r.get("measured_targets", [])
        ]
        self.assertTrue(deferred, "MF-01 claims GUCY2C defers; no rule shows it")
        self.assertEqual(
            deferred[0]["disposition"], CandidateDisposition.DEFER.value
        )
        for text in findings.values():
            self.assertTrue(text.strip())

    def test_output_schema_carries_rule_and_path_provenance(self) -> None:
        columns = self.doc["output_schema"]["per_target_columns"]
        self.assertEqual(len(columns), len(set(columns)))
        for required in ("rule_id", "rq_02_path", "evaluation_status", "row_checksum",
                         "source_urls", "licenses", "dataset_version", "snapshot_id"):
            with self.subTest(column=required):
                self.assertIn(required, columns)

    def test_validation_rules_are_unique_and_bar_the_forbidden_reads(self) -> None:
        rules = self.doc["output_validation"]
        ids = [r["id"] for r in rules]
        self.assertEqual(len(ids), len(set(ids)))
        text = " ".join(r["rule"] for r in rules)
        for phrase in ("SHA-256", "barred_files", "Gate", "mandatory_findings"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_authorisation_stops_short_of_level_01_and_t7(self) -> None:
        not_authorised = " ".join(self.doc["not_authorised"])
        for phrase in ("执行 Level 01", "T7", "Gate"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, not_authorised)
        self.assertIs(
            self.doc["extraction"]["authorises_level_01_execution"], False
        )
        # Level 01 itself must still be unauthorised until the follow-up PR.
        self.assertIs(
            self.binding["binding"]["authorises_level_01_execution"], False
        )


if __name__ == "__main__":
    unittest.main()
