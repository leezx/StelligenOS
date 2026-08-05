"""Verify docs/pools/evgap_02_crc_linkage_extraction.yaml.

The contract freezes the four linkage classes, the declared search scope, the
LOCK-03 evaluation precedence and the provenance split for the EVGAP-02
extraction. These tests check internal consistency and agreement with the merged
Level 01 contracts. They read no external source: the extraction has not run.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from genmodules.gen_indication_endpoint_target.contracts import CandidateDisposition


REPO_ROOT = Path(__file__).resolve().parents[1]
POOLS = REPO_ROOT / "docs" / "pools"
CONTRACT_PATH = POOLS / "evgap_02_crc_linkage_extraction.yaml"
BINDING_PATH = POOLS / "adc_pool_level_01_input_binding.yaml"
LEVEL_CONTRACT_PATH = POOLS / "adc_pool_gate_usage.yaml"

LINKAGE_CLASSES = ("A", "B", "C", "D")
# Columns the source document requires for every evidence row.
REQUIRED_EVIDENCE_COLUMNS = (
    "pair_id", "target", "clinical_context_id", "evidence_type", "crc_specific",
    "context_specific", "human_or_model", "protein_or_rna", "source_ref",
    "source_locator", "evidence_direction", "review_status", "linkage_outcome",
)


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class Evgap02LinkageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load(CONTRACT_PATH)
        cls.binding = _load(BINDING_PATH)
        cls.level = {
            entry["level"]: entry for entry in _load(LEVEL_CONTRACT_PATH)["levels"]
        }["01"]
        cls.lock_03 = next(
            lock for lock in cls.level["locks"] if lock["lock_id"] == "LOCK-03"
        )

    # ------------------------------------------------------------ identity
    def test_contract_targets_the_registered_gap(self) -> None:
        head = self.doc["extraction"]
        self.assertEqual(head["discharges_gap"], "EVGAP-02")
        self.assertEqual(head["serves_lock"], "LOCK-03")
        gaps = {g["id"]: g for g in self.binding["evidence_gaps"]}
        self.assertEqual(gaps["EVGAP-02"]["blocks"], "LOCK-03")
        self.assertEqual(head["execution_status"], "not_authorized_not_executed")
        self.assertIs(head["authorises_level_01_execution"], False)
        self.assertIs(head["requires_followup_binding_pr"], True)

    def test_extraction_is_independent_of_evgap_01(self) -> None:
        """The two tracks must be runnable in parallel."""

        head = self.doc["extraction"]
        self.assertEqual(set(head["independent_of"]), {"EVGAP-01", "SRCADM-01"})
        self.assertTrue(head["independence_reason"].strip())
        # Only contract approval may gate it, not another gap.
        self.assertEqual(head["blocked_by"], ["contract_approval"])
        self.assertIs(head["authorises_extraction_run_after_approve"], True)
        scope = self.doc["scope"]
        self.assertIs(scope["does_not_depend_on_lock_01_status"], True)
        self.assertIs(scope["covers_all_pairs"], True)

    # -------------------------------------------------------- source tiers
    def test_primary_sources_are_usable_and_derived_ones_are_not(self) -> None:
        tiers = self.doc["source_tiers"]
        tier1 = tiers["tier_1_primary_public"]
        tier2 = tiers["tier_2_derived_local_databases"]
        self.assertIs(tier1["admissible_without_separate_admission"], True)
        self.assertTrue(tier1["rationale"].strip())
        self.assertIs(tier2["admissible_without_separate_admission"], False)
        self.assertIs(tier2["barred_until_admitted"], True)
        self.assertIs(tier2["used_by_this_extraction"], False)
        # Every pending admission must be unfilled and identified.
        pending = tier2["pending_admissions"]
        self.assertTrue(pending)
        ids = [p["id"] for p in pending]
        self.assertEqual(len(ids), len(set(ids)))
        for item in pending:
            with self.subTest(dataset=item["dataset_id"]):
                self.assertIsNone(item["admission_record_ref"])
                self.assertIn(item["would_serve_linkage_class"], LINKAGE_CLASSES)
        # A validation rule must forbid reading them.
        text = " ".join(r["rule"] for r in self.doc["output_validation"])
        self.assertIn("tier_2", text)

    def test_every_primary_source_class_records_its_provenance(self) -> None:
        for source in self.doc["source_tiers"]["tier_1_primary_public"]["sources"]:
            with self.subTest(source=source["source_class"]):
                self.assertTrue(source["endpoints"])
                self.assertTrue(source["must_record"])

    def test_scope_is_the_full_pair_matrix_from_approved_axes(self) -> None:
        scope = self.doc["scope"]
        self.assertIs(scope["new_targets_allowed"], False)
        self.assertIs(scope["new_contexts_allowed"], False)
        self.assertEqual(
            scope["pair_count"], scope["clinical_context_count"] * scope["target_count"]
        )
        consequences = self.binding["scope_consequences"]
        self.assertEqual(scope["clinical_context_count"], consequences["raw_clinical_contexts"])
        self.assertEqual(scope["target_count"], consequences["raw_targets"])
        self.assertEqual(scope["pair_count"], consequences["raw_enumeration_matrix_pairs"])
        # Searching per target rather than per pair must be stated, not implied.
        granularity = scope["search_granularity"]
        self.assertEqual(granularity["disease_level_search_count"], scope["target_count"])
        self.assertEqual(granularity["context_specific_assessment_count"], scope["pair_count"])

    # ------------------------------------------------------ linkage classes
    def test_four_linkage_classes_are_defined(self) -> None:
        classes = {c["class_id"]: c for c in self.doc["linkage_classes"]}
        self.assertEqual(set(classes), set(LINKAGE_CLASSES))
        for item in classes.values():
            self.assertTrue(item["accepts"])

    def test_rna_supports_linkage_but_never_lock_01(self) -> None:
        klass = next(c for c in self.doc["linkage_classes"] if c["class_id"] == "A")
        self.assertIs(klass["rna_admissible_for_linkage_existence"], True)
        self.assertIs(klass["rna_may_satisfy_lock_01"], False)
        self.assertIs(klass["rna_must_be_labelled"], True)
        self.assertIs(klass["protein_preferred_over_rna"], True)
        # The Level 01 contract must agree that RNA cannot satisfy LOCK-01.
        standard = self.level["evidence_standard"]
        self.assertIn("LOCK-01", standard["rna_may_not_satisfy"])

    def test_other_cancer_precedent_is_not_linkage(self) -> None:
        klass = next(c for c in self.doc["linkage_classes"] if c["class_id"] == "B")
        self.assertIs(klass["other_cancer_only_precedent_counts_as_linkage"], False)
        self.assertEqual(
            klass["other_cancer_only_precedent_disposition"], "metadata_only_hold"
        )
        rule = next(r for r in self.doc["derivation_rules"] if r["id"] == "L3-04")
        self.assertEqual(rule["disposition"], CandidateDisposition.DEFER.value)

    def test_class_c_counts_as_linkage_but_never_as_adc_efficacy(self) -> None:
        klass = next(c for c in self.doc["linkage_classes"] if c["class_id"] == "C")
        self.assertIs(klass["counts_as_linkage_existence"], True)
        self.assertIs(klass["is_adc_efficacy_evidence"], False)
        self.assertIs(klass["must_be_labelled_not_adc_efficacy"], True)
        self.assertTrue(klass["counts_as_linkage_reason"].strip())
        for modality in ("CAR-T", "bispecific", "radioimmunotherapy", "immunotoxin"):
            self.assertIn(modality, klass["accepts"])
        text = " ".join(r["rule"] for r in self.doc["output_validation"])
        self.assertIn("is_adc_efficacy_evidence", text)

    def test_disease_level_evidence_cannot_carry_a_subgroup(self) -> None:
        klass = next(c for c in self.doc["linkage_classes"] if c["class_id"] == "D")
        self.assertIs(klass["disease_level_supports_canonical_only"], True)
        self.assertIs(klass["subgroup_requires_class_d"], True)
        rule = next(r for r in self.doc["derivation_rules"] if r["id"] == "L3-03")
        self.assertEqual(rule["disposition"], CandidateDisposition.DEFER.value)
        self.assertEqual(rule["resulting_state"], "hold")

    # ------------------------------------------------------- search closure
    def test_declared_search_scope_makes_completeness_decidable(self) -> None:
        scope = self.doc["declared_search_scope"]
        self.assertTrue(scope["per_target_required_source_classes"])
        self.assertIs(scope["query_template_required"], True)
        self.assertIs(scope["silent_skip_forbidden"], True)
        self.assertTrue(scope["search_complete_definition"])
        self.assertEqual(
            scope["unreachable_source_consequence"], "search_incomplete_for_that_target"
        )
        # Every required source class must be a declared tier-1 class.
        tier1 = {s["source_class"]
                 for s in self.doc["source_tiers"]["tier_1_primary_public"]["sources"]}
        self.assertTrue(set(scope["per_target_required_source_classes"]) <= tier1)

    def test_complete_search_exclusion_becomes_available_and_stays_reversible(self) -> None:
        """PR #58 barred this outcome; freezing the scope is what unlocks it."""

        rule = next(r for r in self.doc["derivation_rules"] if r["id"] == "L3-05")
        outcomes = {o["outcome"]: o for o in self.lock_03["outcomes"]}
        self.assertEqual(rule["lock_03_outcome"], "no_known_linkage_after_complete_search")
        self.assertIn(rule["lock_03_outcome"], outcomes)
        self.assertEqual(rule["disposition"], CandidateDisposition.EXCLUDE.value)
        self.assertEqual(rule["disposition_semantics"], "EXCLUDE_FROM_ACTIVE_POOL")
        self.assertIs(rule["is_scientific_disproof"], False)
        self.assertIs(rule["is_killed"], False)
        self.assertEqual(rule["resulting_state"], "reactivation-eligible")
        self.assertIs(rule["requires_search_completeness_record"], True)
        # The six completeness fields must match the Level 01 contract's demand.
        declared = set(outcomes[rule["lock_03_outcome"]]["required_search_fields"])
        self.assertEqual(set(rule["required_search_fields"]), declared)

    # ------------------------------------------------------------ precedence
    def _assign(self, pair: dict) -> str:
        """Reference implementation of the frozen precedence."""

        conditions = {
            "L3-01": not pair["search_complete"],
            "L3-02": pair["crc_specific"] and (
                pair["canonical"] or pair["class_d"]),
            "L3-03": pair["crc_specific"] and not pair["canonical"]
            and not pair["class_d"],
            "L3-04": not pair["crc_specific"] and pair["other_cancer"],
            "L3-05": True,
        }
        for rule_id in self.doc["derivation_precedence"]:
            if conditions[rule_id]:
                return rule_id
        raise AssertionError("precedence did not cover the pair")

    def test_precedence_covers_every_rule_and_starts_with_completeness(self) -> None:
        precedence = self.doc["derivation_precedence"]
        rule_ids = [r["id"] for r in self.doc["derivation_rules"]]
        self.assertEqual(set(precedence), set(rule_ids))
        self.assertEqual(len(precedence), len(set(precedence)))
        self.assertEqual(precedence[0], "L3-01")
        self.assertEqual(precedence[-1], "L3-05")
        self.assertTrue(self.doc["precedence_rationale"].strip())

    def test_every_combination_resolves_to_exactly_one_rule(self) -> None:
        cases = [
            # Incomplete search always wins, whatever else is true.
            ({"search_complete": False, "crc_specific": True, "canonical": True,
              "class_d": True, "other_cancer": True}, "L3-01"),
            ({"search_complete": False, "crc_specific": False, "canonical": False,
              "class_d": False, "other_cancer": False}, "L3-01"),
            # CRC-specific evidence on the canonical context retains.
            ({"search_complete": True, "crc_specific": True, "canonical": True,
              "class_d": False, "other_cancer": False}, "L3-02"),
            # A subgroup retains only with class D enrichment.
            ({"search_complete": True, "crc_specific": True, "canonical": False,
              "class_d": True, "other_cancer": False}, "L3-02"),
            ({"search_complete": True, "crc_specific": True, "canonical": False,
              "class_d": False, "other_cancer": False}, "L3-03"),
            ({"search_complete": True, "crc_specific": True, "canonical": False,
              "class_d": False, "other_cancer": True}, "L3-03"),
            # Other-cancer precedent only.
            ({"search_complete": True, "crc_specific": False, "canonical": True,
              "class_d": False, "other_cancer": True}, "L3-04"),
            # Nothing at all, search closed.
            ({"search_complete": True, "crc_specific": False, "canonical": True,
              "class_d": False, "other_cancer": False}, "L3-05"),
            ({"search_complete": True, "crc_specific": False, "canonical": False,
              "class_d": False, "other_cancer": False}, "L3-05"),
        ]
        for pair, expected in cases:
            with self.subTest(**pair):
                self.assertEqual(self._assign(pair), expected)

    def test_precedence_is_total_over_the_whole_condition_space(self) -> None:
        seen = set()
        for search_complete in (True, False):
            for crc_specific in (True, False):
                for canonical in (True, False):
                    for class_d in (True, False):
                        for other_cancer in (True, False):
                            pair = dict(search_complete=search_complete,
                                        crc_specific=crc_specific,
                                        canonical=canonical, class_d=class_d,
                                        other_cancer=other_cancer)
                            seen.add(self._assign(pair))
        self.assertEqual(seen, set(self.doc["derivation_precedence"]))

    def test_only_the_complete_search_rule_may_exclude(self) -> None:
        """L3-02 retains, L3-05 excludes from the active pool, the rest defer."""

        for rule in self.doc["derivation_rules"]:
            with self.subTest(rule=rule["id"]):
                if rule["id"] == "L3-05":
                    self.assertEqual(rule["disposition"], CandidateDisposition.EXCLUDE.value)
                elif rule["id"] == "L3-02":
                    self.assertEqual(rule["disposition"], CandidateDisposition.RETAIN.value)
                    self.assertEqual(rule["resulting_state"], "active")
                else:
                    self.assertEqual(rule["disposition"], CandidateDisposition.DEFER.value)
                    self.assertEqual(rule["resulting_state"], "hold")
        # Exactly one rule may retain and exactly one may exclude.
        dispositions = [r["disposition"] for r in self.doc["derivation_rules"]]
        self.assertEqual(dispositions.count(CandidateDisposition.RETAIN.value), 1)
        self.assertEqual(dispositions.count(CandidateDisposition.EXCLUDE.value), 1)

    def test_rules_agree_with_the_level_01_outcome_vocabulary(self) -> None:
        outcomes = {o["outcome"]: o for o in self.lock_03["outcomes"]}
        for rule in self.doc["derivation_rules"]:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["lock_03_outcome"], outcomes)
                declared = outcomes[rule["lock_03_outcome"]]
                self.assertEqual(rule["disposition"], declared["disposition"])
                self.assertEqual(rule["resulting_state"], declared["resulting_state"])

    # ------------------------------------------------------------ no prediction
    def test_no_result_shape_is_predicted_for_a_discovery_run(self) -> None:
        predicted = self.doc["predicted_result_shape"]
        self.assertIs(predicted["provided"], False)
        self.assertTrue(predicted["reason"].strip())
        self.assertTrue(predicted["what_is_frozen_instead"])
        for key in ("declared_search_scope", "derivation_precedence"):
            self.assertIn(key, predicted["what_is_frozen_instead"])
        # No count may be smuggled in under another name.
        for key in ("eligible", "active", "hold", "counts", "totals"):
            self.assertNotIn(key, predicted)

    # ------------------------------------------------------------- provenance
    def test_required_columns_all_exist_in_the_output_schema(self) -> None:
        schema = self.doc["output_schema"]
        columns = set(schema["evidence_columns"]) | set(schema["disposition_columns"])
        for column in REQUIRED_EVIDENCE_COLUMNS:
            with self.subTest(column=column):
                self.assertIn(column, schema["evidence_columns"])
        for block in schema["conditionally_required_columns"]:
            with self.subTest(kind=block["when_provenance_kind"]):
                missing = set(block["required_columns"]) - columns
                self.assertEqual(missing, set(), f"missing columns: {missing}")
                self.assertIn(block["when_provenance_kind"], schema["provenance_kinds"])

    def test_pairs_without_evidence_may_not_fabricate_provenance(self) -> None:
        schema = self.doc["output_schema"]
        blocks = {b["when_provenance_kind"]: b
                  for b in schema["conditionally_required_columns"]}
        self.assertEqual(set(blocks), set(schema["provenance_kinds"]))
        for kind in ("no_evidence_found_after_complete_search", "search_incomplete"):
            with self.subTest(kind=kind):
                block = blocks[kind]
                self.assertIs(block["fabricating_source_evidence_forbidden"], True)
                for column in ("source_ref", "source_locator"):
                    self.assertIn(column, block["may_be_empty_columns"])
        supported = blocks["source_supported"]
        for column in ("source_ref", "source_locator", "retrieved_at"):
            self.assertIn(column, supported["required_columns"])

    def test_completeness_fields_are_carried_by_the_disposition_table(self) -> None:
        rule = next(r for r in self.doc["derivation_rules"] if r["id"] == "L3-05")
        columns = set(self.doc["output_schema"]["disposition_columns"])
        for field in rule["required_search_fields"]:
            with self.subTest(field=field):
                self.assertIn(field, columns)

    # ------------------------------------------------------------ boundaries
    def test_validation_rules_are_unique_and_cover_the_hard_limits(self) -> None:
        rules = self.doc["output_validation"]
        ids = [r["id"] for r in rules]
        self.assertEqual(len(ids), len(set(ids)))
        text = " ".join(r["rule"] for r in rules)
        for phrase in ("SHA-256", "Gate", "RNA", "369"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_retain_does_not_promote_to_level_02(self) -> None:
        columns = set(self.doc["output_schema"]["disposition_columns"])
        self.assertIn("may_advance_to_level_02", columns)
        self.assertIn("provisional_only", columns)
        findings = {f["id"]: f["finding"] for f in self.doc["mandatory_findings"]}
        self.assertIn("MF-L04", findings)
        self.assertIn("EVGAP-01", findings["MF-L04"])
        self.assertIn("Level 02", findings["MF-L04"])

    def test_mandatory_findings_keep_the_uncomfortable_qualifiers(self) -> None:
        findings = {f["id"]: f["finding"] for f in self.doc["mandatory_findings"]}
        self.assertEqual(set(findings), {"MF-L01", "MF-L02", "MF-L03", "MF-L04"})
        # RETAIN must never be read as ADC suitability or efficacy.
        self.assertIn("ADC", findings["MF-L01"])
        self.assertIn("ADC", findings["MF-L02"])
        for text in findings.values():
            self.assertTrue(text.strip())

    def test_authorisation_stops_short_of_level_01_and_other_gaps(self) -> None:
        not_authorised = " ".join(self.doc["not_authorised"])
        for phrase in ("执行 Level 01", "EVGAP-01", "tier_2", "T7", "Gate"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, not_authorised)
        # Level 01 itself must remain unauthorised.
        self.assertIs(self.binding["binding"]["authorises_level_01_execution"], False)


if __name__ == "__main__":
    unittest.main()
