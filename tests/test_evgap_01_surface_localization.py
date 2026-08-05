"""Verify docs/pools/evgap_01_surface_localization_extraction.yaml.

The extraction contract freezes how one pinned database version would map onto
LOCK-01's RQ-01/RQ-02/RQ-03. It does not admit that database: admission needs its
own review, tracked as SRCADM-01. These tests check internal consistency and
agreement with the merged Level 01 contracts. They never read the external
database, so the recorded checksums are integrity pins, not verification.
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
        # The extraction is frozen but not yet authorised: SRCADM-01 blocks it.
        self.assertIs(head["authorises_extraction_run"], False)
        self.assertIs(head["authorises_level_01_execution"], False)
        self.assertIs(head["requires_followup_binding_pr"], True)

    def test_database_admission_is_deferred_to_its_own_approval(self) -> None:
        """Blocker 1: a derived database cannot be admitted by self-declaration."""

        dep = self.doc["source_admission_dependency"]
        self.assertEqual(dep["id"], "SRCADM-01")
        self.assertIs(dep["is_derived_database"], True)
        self.assertIs(dep["previously_approved"], False)
        self.assertEqual(dep["admission_status"], "pending_separate_admission_pr")
        self.assertIsNone(dep["admission_record_ref"])
        self.assertIs(dep["admission_record_required"], True)
        # The extraction must be blocked while the admission is pending.
        head = self.doc["extraction"]
        self.assertIs(head["authorises_extraction_run"], False)
        self.assertIn("SRCADM-01", head["extraction_blocked_by"])
        # Admitting the database is explicitly outside this contract.
        not_authorised = " ".join(self.doc["not_authorised"])
        self.assertIn("SRCADM-01", not_authorised)
        self.assertIn("纳入已批准来源", not_authorised)

    def test_admission_audit_covers_more_than_hashes(self) -> None:
        dep = self.doc["source_admission_dependency"]
        items = {a["id"]: a["item"] for a in dep["required_audit_items"]}
        self.assertGreaterEqual(len(items), 9)
        joined = " ".join(items.values())
        for topic in ("builder", "raw manifest", "license", "去重",
                      "discordance_flags", "回溯", "复现"):
            with self.subTest(topic=topic):
                self.assertIn(topic, joined)
        # Independence of the evidence families must be audited, not assumed.
        self.assertIn("独立性", joined)

    def test_self_declared_guards_are_claims_not_verification(self) -> None:
        dep = self.doc["source_admission_dependency"]
        self.assertIs(dep["self_declared_guards_are_claims_not_verification"], True)
        guards = dep["self_declared_guards"]
        self.assertGreaterEqual(len(guards), 6)
        for guard in guards:
            with self.subTest(guard=guard["guard"]):
                self.assertEqual(guard["status"], "claim_pending_audit")
                self.assertTrue(guard["relates_to_repo_rule"].strip())
        names = {g["guard"] for g in guards}
        for required in ("absence_is_negative_evidence",
                         "membrane_topology_is_independent_surface_localization"):
            self.assertIn(required, names)

    def test_checksums_are_integrity_pins_not_approval(self) -> None:
        dep = self.doc["source_admission_dependency"]
        pinned = dep["files_pinned_for_integrity_only"]
        self.assertEqual(len(pinned), 4)
        for item in pinned:
            with self.subTest(path=item["path"]):
                digest = item["sha256"]
                self.assertEqual(len(digest), 64, digest)
                self.assertTrue(all(c in "0123456789abcdef" for c in digest))

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
        self.assertTrue(paths["ECD-b"]["rationale_note"].strip())
        self.assertEqual(len(paths["ECD-b"]["measured_targets"]),
                         paths["ECD-b"]["eligible_via_path_count"])
        self.assertIs(rq2["luminal_domain_is_not_extracellular"], True)
        self.assertIn("LAMP1", rq2["luminal_domain_note"])

    def test_path_satisfaction_is_not_confused_with_eligibility(self) -> None:
        """Blocker 2: satisfying an ECD path is not the same as being eligible."""

        rq2 = self.doc["rq_02_extracellular_domain"]
        by_id = {r["id"]: r for r in self.doc["derivation_rules"]}
        for path in rq2["paths"]:
            with self.subTest(path=path["path_id"]):
                # Both counts must exist and eligibility cannot exceed satisfaction.
                self.assertIn("measured_path_satisfied_count", path)
                self.assertIn("eligible_via_path_count", path)
                self.assertLessEqual(
                    path["eligible_via_path_count"],
                    path["measured_path_satisfied_count"],
                )
        # eligible_via_path must sum to E1-01, not to the satisfied totals.
        self.assertEqual(
            sum(p["eligible_via_path_count"] for p in rq2["paths"]),
            by_id["E1-01"]["expected_count"],
        )
        satisfied = sum(p["measured_path_satisfied_count"] for p in rq2["paths"])
        self.assertEqual(satisfied - rq2["measured_path_overlap"],
                         rq2["rq_02_positive_decomposition"]["total"])

    def test_rq_02_positive_decomposition_holds(self) -> None:
        rq2 = self.doc["rq_02_extracellular_domain"]
        decomposition = rq2["rq_02_positive_decomposition"]
        by_id = {r["id"]: r for r in self.doc["derivation_rules"]}
        self.assertEqual(
            decomposition["final_eligible"]
            + decomposition["hold_insufficient_localization_families"]
            + decomposition["hold_discordance"],
            decomposition["total"],
        )
        self.assertEqual(decomposition["final_eligible"], by_id["E1-01"]["expected_count"])
        self.assertEqual(
            decomposition["hold_insufficient_localization_families"],
            by_id["E1-02"]["expected_count"],
        )
        # RQ-02 positives must outnumber the eligible set: holds exist downstream.
        self.assertGreater(decomposition["total"], decomposition["final_eligible"])
        self.assertTrue(decomposition["identity"].strip())

    def test_rq_03_requires_protein_level_provenance(self) -> None:
        rq3 = self.doc["rq_03_protein_level_provenance"]
        self.assertIs(rq3["rna_derived_rows_admissible"], False)
        covered = rq3["covered_rows"]
        for field in ("source_id", "source_release", "source_url", "license"):
            self.assertIn(field, covered["required_fields"])
        allowed = set(self.doc["allowed_fields"]["from_source_evidence"])
        self.assertTrue(set(covered["required_fields"]) <= allowed)

    def test_reference_absent_rows_need_absence_provenance_not_fabrication(self) -> None:
        """Blocker 3: absent targets have no source rows and must not invent any."""

        rq3 = self.doc["rq_03_protein_level_provenance"]
        absent = rq3["absent_rows"]
        self.assertIsNone(absent["requires_rows_in"])
        self.assertIs(absent["source_provenance_fields_may_be_empty"], True)
        self.assertIs(absent["fabricating_source_evidence_forbidden"], True)
        self.assertIs(rq3["never_present_absence_as_source_supported"], True)
        for field in ("reference_dataset_id", "reference_dataset_version",
                      "reference_snapshot_id", "target_axis_ref",
                      "absence_reason", "lookup_at"):
            with self.subTest(field=field):
                self.assertIn(field, absent["required_absence_fields"])
        # The absence path must not reuse the covered-row requirement.
        self.assertEqual(
            set(absent["required_absence_fields"])
            & set(rq3["covered_rows"]["required_fields"]),
            set(),
        )
        # Validation must carry all three provenance rules.
        ids = {r["id"] for r in self.doc["output_validation"]}
        for rule_id in ("VAL-E05", "VAL-E05b", "VAL-E05c"):
            self.assertIn(rule_id, ids)
        columns = set(self.doc["output_schema"]["per_target_columns"])
        for column in ("provenance_kind", "absence_reason", "target_axis_ref", "lookup_at"):
            with self.subTest(column=column):
                self.assertIn(column, columns)

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

    def test_precedence_is_frozen_and_covers_every_rule(self) -> None:
        """Blocker 4: the five conditions are not naturally mutually exclusive."""

        precedence = self.doc["derivation_precedence"]
        rule_ids = [r["id"] for r in self.doc["derivation_rules"]]
        self.assertEqual(set(precedence), set(rule_ids))
        self.assertEqual(len(precedence), len(set(precedence)))
        # Absence first, then conflict, then the RQ checks, eligible last.
        self.assertEqual(precedence[0], "E1-05")
        self.assertEqual(precedence[1], "E1-04")
        self.assertEqual(precedence[-1], "E1-01")
        self.assertTrue(self.doc["precedence_rationale"].strip())
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-E11", ids)

    def _assign(self, target: dict) -> str:
        """Reference implementation of the frozen precedence."""

        conditions = {
            "E1-05": target["absent"],
            "E1-04": not target["absent"] and target["conflict"],
            "E1-04b": not target["absent"] and not target["rq3"],
            "E1-03": not target["absent"] and not target["rq2"],
            "E1-02": not target["absent"] and target["families"] < 2,
            "E1-01": True,
        }
        for rule_id in self.doc["derivation_precedence"]:
            if conditions[rule_id]:
                return rule_id
        raise AssertionError("precedence did not cover the target")

    def test_precedence_gives_one_and_only_one_rule_per_target(self) -> None:
        floor = self.doc["rq_01_plasma_membrane_localization"][
            "minimum_independent_families"
        ]
        # Cases chosen to exercise every overlap the reviewer named.
        cases = [
            ({"absent": True, "conflict": False, "rq2": False, "rq3": False, "families": 0}, "E1-05"),
            ({"absent": True, "conflict": True, "rq2": False, "rq3": False, "families": 0}, "E1-05"),
            ({"absent": False, "conflict": True, "rq2": True, "rq3": True, "families": 3}, "E1-04"),
            ({"absent": False, "conflict": True, "rq2": True, "rq3": True, "families": 1}, "E1-04"),
            ({"absent": False, "conflict": True, "rq2": False, "rq3": True, "families": 0}, "E1-04"),
            # discordance outranks a provenance failure.
            ({"absent": False, "conflict": True, "rq2": True, "rq3": False, "families": 3}, "E1-04"),
            # The gap the reviewer found: RQ-01 and RQ-02 hold, no conflict, RQ-03 fails.
            ({"absent": False, "conflict": False, "rq2": True, "rq3": False, "families": 3}, "E1-04b"),
            ({"absent": False, "conflict": False, "rq2": False, "rq3": False, "families": 3}, "E1-04b"),
            ({"absent": False, "conflict": False, "rq2": True, "rq3": False, "families": 1}, "E1-04b"),
            ({"absent": False, "conflict": False, "rq2": False, "rq3": True, "families": 3}, "E1-03"),
            ({"absent": False, "conflict": False, "rq2": False, "rq3": True, "families": 1}, "E1-03"),
            ({"absent": False, "conflict": False, "rq2": True, "rq3": True, "families": 1}, "E1-02"),
            ({"absent": False, "conflict": False, "rq2": True, "rq3": True, "families": floor}, "E1-01"),
        ]
        for target, expected in cases:
            with self.subTest(**target):
                self.assertEqual(self._assign(target), expected)

    def test_provenance_failure_on_a_covered_target_has_its_own_rule(self) -> None:
        """Blocker 1: RQ-03 failure on a covered target must land somewhere."""

        rules = {r["id"]: r for r in self.doc["derivation_rules"]}
        self.assertIn("E1-04b", rules)
        rule = rules["E1-04b"]
        self.assertEqual(rule["lock_01_outcome"], "possible_surface_target")
        self.assertEqual(rule["disposition"], CandidateDisposition.DEFER.value)
        self.assertEqual(rule["resulting_state"], "hold")
        # Vacuous on this snapshot, but it must be declared and justified.
        self.assertEqual(rule["expected_count"], 0)
        self.assertIs(rule["vacuous_this_run"], True)
        self.assertTrue(rule["vacuous_reason"].strip())
        # It must sit in the precedence, after discordance.
        precedence = self.doc["derivation_precedence"]
        self.assertIn("E1-04b", precedence)
        self.assertLess(precedence.index("E1-04"), precedence.index("E1-04b"))
        self.assertLess(precedence.index("E1-04b"), precedence.index("E1-01"))
        # RQ-03 must name this rule as the failure route.
        rq3 = self.doc["rq_03_protein_level_provenance"]
        self.assertEqual(rq3["covered_row_failure_rule"], "E1-04b")
        self.assertEqual(
            rq3["covered_row_failure_disposition"], CandidateDisposition.DEFER.value
        )
        self.assertEqual(rq3["measured_covered_targets_failing_rq_03"], 0)
        self.assertEqual(
            rq3["measured_covered_targets_satisfying_rq_03"],
            self.doc["scope"]["measured_coverage_in_reference"],
        )

    def test_absence_fields_are_all_present_in_the_output_schema(self) -> None:
        """Blocker 2: VAL-E05b cannot demand columns the schema does not have."""

        required = set(
            self.doc["rq_03_protein_level_provenance"]["absent_rows"][
                "required_absence_fields"
            ]
        )
        columns = set(self.doc["output_schema"]["per_target_columns"])
        self.assertTrue(required <= columns, f"missing columns: {required - columns}")
        for field in ("reference_dataset_id", "reference_dataset_version",
                      "reference_snapshot_id"):
            with self.subTest(field=field):
                self.assertIn(field, columns)

    def test_conditional_columns_pin_the_admission_snapshot(self) -> None:
        blocks = {
            b["when_provenance_kind"]: b
            for b in self.doc["output_schema"]["conditionally_required_columns"]
        }
        self.assertEqual(set(blocks), {"reference_absent", "source_supported"})
        absent = blocks["reference_absent"]
        required = set(
            self.doc["rq_03_protein_level_provenance"]["absent_rows"][
                "required_absence_fields"
            ]
        )
        self.assertEqual(set(absent["required_columns"]), required)
        for field in ("source_ids", "source_releases", "source_urls", "licenses"):
            self.assertIn(field, absent["may_be_empty_columns"])
        # The three reference columns must equal the admission snapshot, not be free text.
        dep = self.doc["source_admission_dependency"]
        pinned = absent["pinned_to_admission_snapshot"]
        self.assertEqual(pinned["reference_dataset_id"], dep["dataset_id"])
        self.assertEqual(str(pinned["reference_dataset_version"]), str(dep["dataset_version"]))
        self.assertEqual(pinned["reference_snapshot_id"], dep["snapshot_id"])
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-E05d", ids)
        # And source-supported rows must still carry real source provenance.
        supported = blocks["source_supported"]
        for field in ("source_ids", "source_releases", "source_urls", "licenses"):
            self.assertIn(field, supported["required_columns"])

    def test_multi_condition_targets_resolve_to_the_higher_rule(self) -> None:
        recorded = self.doc["measured_multi_condition_targets"]
        self.assertTrue(recorded)
        precedence = self.doc["derivation_precedence"]
        by_id = {r["id"]: r for r in self.doc["derivation_rules"]}
        for item in recorded:
            with self.subTest(target=item["gene_symbol"]):
                matched = item["conditions_matched"]
                self.assertGreater(len(matched), 1, "not a multi-condition target")
                winner = min(matched, key=precedence.index)
                self.assertEqual(item["resolved_to"], winner)
                # The recorded resolution must match where the rule counts it.
                self.assertIn(
                    item["gene_symbol"], by_id[item["resolved_to"]]["measured_targets"]
                )
                # And it must NOT be counted under a suppressed condition.
                for suppressed in matched:
                    if suppressed == winner:
                        continue
                    self.assertNotIn(
                        item["gene_symbol"],
                        by_id[suppressed].get("measured_targets", []),
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
