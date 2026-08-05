"""Verify docs/pools/evgap_02_crc_linkage_extraction.yaml.

The contract freezes the four linkage classes, the declared search scope, the
LOCK-03 evaluation precedence and the provenance split for the EVGAP-02
extraction. These tests check internal consistency and agreement with the merged
Level 01 contracts. They read no external source.

v0.2.0 adds the layer the first version lacked. v0.1.0 required an
``evidence_direction`` column but no rule ever required it to be resolved, so a
compliant run registered 7,067 search hits with ``evidence_direction=unknown``
and derived 168 RETAIN dispositions from them. The tests below pin the three
properties that failure needed: search hits and assertions live in separate
tables, a disposition may only cite assertions, and an unresolvable symbol can
neither retain nor exclude.
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
# Columns the source document requires for every evidence row. v0.2.0 renames
# evidence_direction to assertion_direction, which may no longer be "unknown".
REQUIRED_EVIDENCE_COLUMNS = (
    "pair_id", "target", "clinical_context_id", "evidence_type", "crc_specific",
    "context_specific", "human_or_model", "protein_or_rna", "source_ref",
    "source_locator", "assertion_direction", "review_status", "linkage_outcome",
)
# The elements that turn a retrieved record into an assertion.
ASSERTION_ELEMENTS = (
    "target_entity_resolved", "crc_entity_resolved", "context_entity_resolved",
    "relationship_type", "assertion_direction", "supporting_text_or_structured_field",
)
# Endpoints whose hit proves only that the entity has a page or an index row.
IDENTITY_ONLY_ENDPOINTS = ("TCGA", "Human Protein Atlas", "GEO")


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
        self.assertIs(head["authorises_level_01_execution"], False)
        self.assertIs(head["requires_followup_binding_pr"], True)

    def test_the_executed_run_is_recorded_as_retrieval_only(self) -> None:
        """The v0.1.0 run happened; it must not read as having discharged the gap."""

        head = self.doc["extraction"]
        self.assertEqual(head["extraction_version"], "0.2.0")
        self.assertEqual(head["supersedes_version"], "0.1.0")
        self.assertEqual(head["amended_after_review_of_pr"], 62)
        self.assertIs(head["gap_discharged"], False)
        self.assertEqual(
            head["execution_status"],
            "retrieval_layer_executed_assertion_layer_not_executed",
        )
        runs = head["executed_runs"]
        self.assertTrue(runs)
        for run in runs:
            with self.subTest(run=run["run_id"]):
                self.assertEqual(run["under_contract_version"], "0.1.0")
                self.assertEqual(run["layers_completed"], ["L-RETRIEVAL"])
                self.assertEqual(set(run["layers_not_completed"]),
                                 {"L-ASSERTION", "L-DISPOSITION"})
                self.assertIs(run["discharges_gap"], False)
                self.assertEqual(run["downgraded_by_review_of_pr"], 62)
        # The amendment must say why, not merely bump the number.
        self.assertTrue(head["amendment_reason"].strip())
        self.assertIn("query", head["amendment_reason"])

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
            "L3-00": not pair["identity_resolved"],
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
        self.assertEqual(precedence[0], "L3-00")
        self.assertEqual(precedence[1], "L3-01")
        self.assertEqual(precedence[-1], "L3-05")
        self.assertTrue(self.doc["precedence_rationale"].strip())

    def test_every_combination_resolves_to_exactly_one_rule(self) -> None:
        cases = [
            # An unresolved symbol outranks everything, including a closed search
            # with zero hits. This is the case v0.1.0 got wrong in both directions.
            ({"identity_resolved": False, "search_complete": True,
              "crc_specific": True, "canonical": True, "class_d": True,
              "other_cancer": True}, "L3-00"),
            ({"identity_resolved": False, "search_complete": True,
              "crc_specific": False, "canonical": True, "class_d": False,
              "other_cancer": False}, "L3-00"),
            # Incomplete search always wins, whatever else is true.
            ({"identity_resolved": True, "search_complete": False,
              "crc_specific": True, "canonical": True,
              "class_d": True, "other_cancer": True}, "L3-01"),
            ({"identity_resolved": True, "search_complete": False,
              "crc_specific": False, "canonical": False,
              "class_d": False, "other_cancer": False}, "L3-01"),
            # CRC-specific evidence on the canonical context retains.
            ({"identity_resolved": True, "search_complete": True,
              "crc_specific": True, "canonical": True,
              "class_d": False, "other_cancer": False}, "L3-02"),
            # A subgroup retains only with class D enrichment.
            ({"identity_resolved": True, "search_complete": True,
              "crc_specific": True, "canonical": False,
              "class_d": True, "other_cancer": False}, "L3-02"),
            ({"identity_resolved": True, "search_complete": True,
              "crc_specific": True, "canonical": False,
              "class_d": False, "other_cancer": False}, "L3-03"),
            ({"identity_resolved": True, "search_complete": True,
              "crc_specific": True, "canonical": False,
              "class_d": False, "other_cancer": True}, "L3-03"),
            # Other-cancer precedent only.
            ({"identity_resolved": True, "search_complete": True,
              "crc_specific": False, "canonical": True,
              "class_d": False, "other_cancer": True}, "L3-04"),
            # Nothing at all, search closed.
            ({"identity_resolved": True, "search_complete": True,
              "crc_specific": False, "canonical": True,
              "class_d": False, "other_cancer": False}, "L3-05"),
            ({"identity_resolved": True, "search_complete": True,
              "crc_specific": False, "canonical": False,
              "class_d": False, "other_cancer": False}, "L3-05"),
        ]
        for pair, expected in cases:
            with self.subTest(**pair):
                self.assertEqual(self._assign(pair), expected)

    def test_precedence_is_total_over_the_whole_condition_space(self) -> None:
        seen = set()
        for identity_resolved in (True, False):
            for search_complete in (True, False):
                for crc_specific in (True, False):
                    for canonical in (True, False):
                        for class_d in (True, False):
                            for other_cancer in (True, False):
                                pair = dict(identity_resolved=identity_resolved,
                                            search_complete=search_complete,
                                            crc_specific=crc_specific,
                                            canonical=canonical, class_d=class_d,
                                            other_cancer=other_cancer)
                                seen.add(self._assign(pair))
        self.assertEqual(seen, set(self.doc["derivation_precedence"]))

    def test_an_unresolved_symbol_can_never_be_excluded(self) -> None:
        """v0.1.0 excluded EDBN for nine pairs because its abbreviation drew zero
        hits. Zero hits from an unresolvable symbol is a resolution failure."""

        for canonical in (True, False):
            for class_d in (True, False):
                pair = dict(identity_resolved=False, search_complete=True,
                            crc_specific=False, canonical=canonical,
                            class_d=class_d, other_cancer=False)
                with self.subTest(**pair):
                    self.assertEqual(self._assign(pair), "L3-00")

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
    def test_required_columns_exist_in_their_own_table(self) -> None:
        """Checking the union of both tables would mask a missing column."""

        schema = self.doc["output_schema"]
        # v0.2.0: the evidence table IS the assertion table.
        self.assertIs(schema["evidence_table_is_assertion_table"], True)
        self.assertEqual(schema["evidence_columns_alias"], "assertion_columns")
        self.assertNotIn("evidence_columns", schema,
                         "a live evidence_columns key would let both versions coexist")
        evidence = set(schema["assertion_columns"])
        disposition = set(schema["disposition_columns"])
        for column in REQUIRED_EVIDENCE_COLUMNS:
            with self.subTest(column=column):
                self.assertIn(column, evidence)
        for block in schema["conditionally_required_columns"]:
            kind = block["when_provenance_kind"]
            with self.subTest(kind=kind):
                self.assertIn(kind, schema["provenance_kinds"])
                # Every conditionally required column must live in a named table,
                # and the block must say which one.
                table = block["table"]
                self.assertIn(table, ("evidence", "disposition"))
                owned = evidence if table == "evidence" else disposition
                missing = set(block["required_columns"]) - owned
                self.assertEqual(missing, set(),
                                 f"{kind}: columns absent from {table}: {missing}")
                may_empty = set(block.get("may_be_empty_columns", []))
                self.assertEqual(may_empty - (evidence | disposition), set())

    def test_evidence_rows_are_individually_addressable(self) -> None:
        """Blocker 2: a disposition must be able to name its supporting rows."""

        schema = self.doc["output_schema"]
        self.assertEqual(schema["evidence_row_key"], "assertion_id")
        self.assertIs(schema["evidence_id_unique"], True)
        self.assertIn("assertion_id", schema["assertion_columns"])
        for column in ("supporting_evidence_refs", "class_d_evidence_refs",
                       "other_cancer_evidence_refs"):
            with self.subTest(column=column):
                self.assertIn(column, schema["disposition_columns"])
        ids = {r["id"] for r in self.doc["output_validation"]}
        for rule_id in ("VAL-L16", "VAL-L17", "VAL-L20"):
            self.assertIn(rule_id, ids)

    def test_every_rule_states_what_it_must_and_must_not_cite(self) -> None:
        requirements = self.doc["output_schema"]["evidence_reference_requirements"]
        rule_ids = {r["id"] for r in self.doc["derivation_rules"]}
        covered = {r["rule_id"] for r in requirements}
        self.assertEqual(covered, rule_ids)
        by_key = {(r["rule_id"], r.get("context_kind")): r for r in requirements}
        # L3-02 must be split by context kind: a subgroup needs class D as well.
        canonical = by_key[("L3-02", "canonical")]
        subgroup = by_key[("L3-02", "subgroup")]
        self.assertEqual(canonical["supporting_evidence_refs"],
                         "at_least_one_of_class_a_b_or_c")
        self.assertEqual(subgroup["supporting_evidence_refs"],
                         "at_least_one_of_class_a_b_or_c")
        self.assertEqual(subgroup["class_d_evidence_refs"], "at_least_one")
        # L3-03 rests on disease-level evidence and must cite no class D.
        l3_03 = by_key[("L3-03", None)]
        self.assertEqual(l3_03["supporting_evidence_refs"],
                         "at_least_one_disease_level_crc_evidence")
        self.assertEqual(l3_03["class_d_evidence_refs"], "must_be_empty")
        # Other-cancer precedent may never be cited as support.
        l3_04 = by_key[("L3-04", None)]
        self.assertEqual(l3_04["supporting_evidence_refs"], "must_be_empty")
        self.assertEqual(l3_04["other_cancer_evidence_refs"], "at_least_one")
        # L3-05 cites nothing but must carry complete search provenance.
        l3_05 = by_key[("L3-05", None)]
        for key in ("supporting_evidence_refs", "class_d_evidence_refs",
                    "other_cancer_evidence_refs"):
            self.assertEqual(l3_05[key], "must_be_empty")
        self.assertEqual(l3_05["search_provenance"], "must_be_complete")
        # L3-01 must not invent references.
        l3_01 = by_key[("L3-01", None)]
        self.assertEqual(l3_01["supporting_evidence_refs"], "must_be_empty")
        self.assertEqual(l3_01["class_d_evidence_refs"], "must_be_empty")

    def test_class_d_completeness_is_pair_level_and_gates_l3_03_and_l3_05(self) -> None:
        """Blocker 1: D-class search must enter search_complete per pair."""

        scope = self.doc["declared_search_scope"]
        block = scope["per_pair_required_class_d_search"]
        self.assertIs(block["required"], True)
        self.assertEqual(block["applies_to"], "all_369_pairs")
        self.assertEqual(block["incomplete_consequence"], "L3-01")
        for field in ("class_d_query_expression", "class_d_executed_at",
                      "class_d_result_count", "class_d_reachable",
                      "class_d_source_coverage_ref", "class_d_search_complete"):
            with self.subTest(field=field):
                self.assertIn(field, block["must_record"])
                # The field must actually be carried by the disposition table.
                self.assertIn(field, self.doc["output_schema"]["disposition_columns"])
        # Completeness must require all four levels, not just the target level.
        self.assertIs(scope["search_complete_requires_all_levels"], True)
        self.assertEqual(set(scope["search_complete_levels"]),
                         {"target_level_identity_resolution",
                          "target_level_source_class_and_endpoint_coverage",
                          "pair_level_class_d_coverage",
                          "pair_level_assertion_extraction_completed"})
        self.assertEqual(scope["unreachable_class_d_consequence"],
                         "search_incomplete_for_that_pair")
        # L3-03 and L3-05 may only fire once the D-class search has closed.
        by_id = {r["id"]: r for r in self.doc["derivation_rules"]}
        for rule_id in ("L3-03", "L3-05"):
            with self.subTest(rule=rule_id):
                self.assertIs(by_id[rule_id]["requires_class_d_search_complete"], True)
        self.assertIs(by_id["L3-01"]["covers_all_completeness_levels"], True)
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-L18", ids)

    def test_endpoint_coverage_is_frozen_not_left_to_the_executor(self) -> None:
        """Blocker 1: covering a source class must mean covering its endpoints."""

        scope = self.doc["declared_search_scope"]
        self.assertEqual(scope["coverage_unit"], "endpoint")
        self.assertTrue(scope["coverage_unit_reason"].strip())
        required = set(scope["per_target_required_source_classes"])
        for source in self.doc["source_tiers"]["tier_1_primary_public"]["sources"]:
            if source["source_class"] not in required:
                continue
            with self.subTest(source=source["source_class"]):
                self.assertIs(source["all_endpoints_required"], True)
                # The minimum set may not be narrower than the declared endpoints.
                self.assertEqual(set(source["minimum_endpoint_set"]),
                                 set(source["endpoints"]))
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-L19", ids)

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
        self.assertEqual(set(findings),
                         {"MF-L01", "MF-L02", "MF-L03", "MF-L04", "MF-L05", "MF-L06"})
        # RETAIN must never be read as ADC suitability or efficacy.
        self.assertIn("ADC", findings["MF-L01"])
        self.assertIn("ADC", findings["MF-L02"])
        # The report must not present candidate counts as evidence counts, and
        # must not fold the unresolved pairs into "no linkage".
        self.assertIn("retrieval_candidate_count", findings["MF-L05"])
        self.assertIn("assertion_count", findings["MF-L05"])
        self.assertIn("L3-00", findings["MF-L06"])
        self.assertIn("L3-05", findings["MF-L06"])
        for text in findings.values():
            self.assertTrue(text.strip())

    # ------------------------------------------------ v0.2.0: the missing layer
    def test_retrieval_and_assertion_are_separate_layers(self) -> None:
        layers = {l["layer_id"]: l for l in self.doc["extraction_layers"]}
        self.assertEqual(set(layers), {"L-RETRIEVAL", "L-ASSERTION", "L-DISPOSITION"})
        retrieval, assertion = layers["L-RETRIEVAL"], layers["L-ASSERTION"]
        # A search hit alone may never support LOCK-03.
        self.assertIs(retrieval["may_support_lock_03"], False)
        self.assertIs(retrieval["may_be_referenced_by_disposition"], False)
        self.assertIs(assertion["may_support_lock_03"], True)
        self.assertEqual(assertion["consumes"], "retrieval_candidates")
        # The disposition layer may only read assertions.
        disposition = layers["L-DISPOSITION"]
        self.assertEqual(disposition["may_only_reference"], "linkage_assertions")
        self.assertIs(disposition["may_reference_retrieval_candidates"], False)
        # The known false-positive modes must be named, not gestured at.
        modes = " ".join(retrieval["known_false_positive_modes"])
        for mode in ("缩写碰撞", "参考文献", "综述", "免责声明"):
            with self.subTest(mode=mode):
                self.assertIn(mode, modes)

    def test_decision_02_is_read_correctly_not_as_a_licence_for_hits(self) -> None:
        """PR #58 allowed machine-extracted evidence — extracted, not retrieved."""

        assertion = next(l for l in self.doc["extraction_layers"]
                         if l["layer_id"] == "L-ASSERTION")
        self.assertIs(assertion["machine_extraction_permitted"], True)
        self.assertIs(assertion["human_review_still_required"], True)
        basis = assertion["machine_extraction_permitted_basis"]
        self.assertIn("DECISION-02", basis)
        self.assertIn("assertion", basis)

    def test_an_assertion_needs_every_element_and_a_resolved_direction(self) -> None:
        req = self.doc["assertion_requirements"]
        elements = {e["element"] for e in req["required_elements"]}
        self.assertEqual(elements, set(ASSERTION_ELEMENTS))
        for entry in req["required_elements"]:
            with self.subTest(element=entry["element"]):
                self.assertTrue(entry["meaning"].strip())
        # The check v0.1.0 lacked.
        self.assertIs(req["direction_must_be_resolved"], True)
        self.assertIs(req["direction_unknown_forbidden_for_lock_03"], True)
        self.assertIs(req["cooccurrence_is_not_an_assertion"], True)
        self.assertTrue(req["relationship_types"])
        self.assertTrue(req["cooccurrence_examples_rejected"])
        # Both a valid and an invalid example must be given, so the boundary is
        # demonstrated rather than asserted.
        self.assertTrue(req["examples_of_valid_assertions"])
        self.assertTrue(req["examples_of_invalid_assertions"])
        # And the schema must forbid the value, not only the prose.
        forbidden = self.doc["output_schema"]["assertion_forbidden_values"]
        self.assertIn("unknown", forbidden["assertion_direction"])

    def test_linkage_class_comes_from_content_not_from_the_query(self) -> None:
        common = self.doc["linkage_class_common_requirements"]
        self.assertIs(common["applies_to_all_classes"], True)
        self.assertIs(common["requires_assertion"], True)
        self.assertEqual(common["classified_by"], "assertion_content")
        self.assertIs(common["classified_by_query_category_forbidden"], True)
        self.assertIs(common["direction_unknown_admissible"], False)
        self.assertTrue(common["classified_by_query_category_forbidden_reason"].strip())
        schema = self.doc["output_schema"]
        # The candidate table records which query found it, and that label is
        # explicitly not a linkage class.
        self.assertIn("query_class_label", schema["retrieval_candidate_columns"])
        self.assertIs(schema["query_class_label_is_not_linkage_class"], True)
        self.assertNotIn("linkage_class", schema["retrieval_candidate_columns"])
        self.assertIn("linkage_class", schema["assertion_columns"])

    def test_candidate_table_marks_itself_unusable_for_lock_03(self) -> None:
        schema = self.doc["output_schema"]
        columns = set(schema["retrieval_candidate_columns"])
        for column in ("record_status", "linkage_validated", "may_support_lock_03",
                       "assertion_extraction_status"):
            with self.subTest(column=column):
                self.assertIn(column, columns)
        fixed = schema["retrieval_candidate_fixed_values"]
        self.assertEqual(fixed["record_status"], "retrieved_candidate")
        self.assertIs(fixed["linkage_validated"], False)
        self.assertIs(fixed["may_support_lock_03"], False)
        # Every assertion must name the candidate it came from.
        self.assertIn("candidate_id", schema["assertion_columns"])
        self.assertIs(schema["assertion_must_cite_its_candidate"], True)

    def test_refs_may_only_point_at_assertions(self) -> None:
        schema = self.doc["output_schema"]
        self.assertEqual(schema["refs_point_to"], "assertion_id")
        self.assertIs(schema["refs_pointing_to_candidate_id_forbidden"], True)
        tables = {t["table"]: t for t in schema["tables"]}
        self.assertIs(tables["retrieval_candidates"]["may_be_referenced_by_disposition"],
                      False)
        self.assertIs(tables["linkage_assertions"]["may_be_referenced_by_disposition"],
                      True)
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-L23", ids)

    def test_identity_resolution_precedes_search_and_blocks_both_verdicts(self) -> None:
        block = self.doc["identity_resolution"]
        self.assertIs(block["required_before_search"], True)
        self.assertIs(block["unresolved_may_not_be_searched"], True)
        self.assertEqual(block["unresolved_lock_03_rule"], "L3-00")
        # The asymmetry that matters: no RETAIN and no EXCLUDE.
        self.assertIs(block["unresolved_may_not_retain"], True)
        self.assertIs(block["unresolved_may_not_exclude"], True)
        reason = block["unresolved_may_not_exclude_reason"]
        self.assertIn("EDBN", reason)
        self.assertIn("FN1", reason)
        for field in ("input_symbol", "resolved_identifier", "resolution_status",
                      "resolution_basis"):
            with self.subTest(field=field):
                self.assertIn(field, block["resolution_must_record"])

    def test_the_four_unresolvable_entities_are_named_with_their_kind(self) -> None:
        """Each was searched as a gene symbol by the v0.1.0 run."""

        block = self.doc["identity_resolution"]
        entities = {e["input_symbol"]: e for e in block["known_unresolved_entities"]}
        self.assertEqual(set(entities),
                         {"Undisclosed", "EDBN", "AG7", "CA19-9"})
        vocabulary = set(block["resolution_status_vocabulary"])
        for symbol, entry in sorted(entities.items()):
            with self.subTest(symbol=symbol):
                self.assertIn(entry["resolution_status"], vocabulary)
                self.assertTrue(entry["note"].strip())
        # The distinctions must be kept: a placeholder is not an abbreviation,
        # and a glycan antigen is resolvable but has no gene symbol.
        self.assertEqual(entities["Undisclosed"]["resolution_status"],
                         "unresolvable_placeholder")
        self.assertEqual(entities["CA19-9"]["resolution_status"],
                         "resolved_as_non_protein_antigen")
        self.assertEqual(entities["EDBN"]["resolution_status"],
                         "unresolvable_ambiguous_abbreviation")
        # Recognising them must not require free judgement.
        self.assertIn("E1-05", block["mechanical_precondition"])

    def test_l3_00_reuses_the_frozen_outcome_vocabulary(self) -> None:
        """LOCK-03 has no identity_unresolved outcome; that belongs to LOCK-01."""

        rule = next(r for r in self.doc["derivation_rules"] if r["id"] == "L3-00")
        outcomes = {o["outcome"]: o for o in self.lock_03["outcomes"]}
        self.assertNotIn("identity_unresolved", outcomes)
        self.assertEqual(rule["lock_03_outcome"], "linkage_evidence_missing")
        self.assertIn(rule["lock_03_outcome"], outcomes)
        self.assertIs(rule["does_not_introduce_new_outcome"], True)
        self.assertEqual(rule["distinguishing_column"], "identity_resolution_status")
        self.assertIn("identity_resolution_status",
                      self.doc["output_schema"]["disposition_columns"])
        self.assertIs(rule["may_never_become_l3_05"], True)
        # L3-05 must carry the matching guard.
        l3_05 = next(r for r in self.doc["derivation_rules"] if r["id"] == "L3-05")
        self.assertIs(l3_05["requires_identity_resolved"], True)
        self.assertIs(l3_05["zero_hits_from_unresolved_symbol_forbidden"], True)
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-L27", ids)

    def test_each_endpoint_declares_what_its_hit_does_not_prove(self) -> None:
        entries = {e["endpoint"]: e for e in self.doc["endpoint_evidence_admissibility"]}
        # Every declared tier-1 endpoint must appear.
        declared = {endpoint
                    for source in self.doc["source_tiers"]["tier_1_primary_public"]["sources"]
                    if source["source_class"] in
                    self.doc["declared_search_scope"]["per_target_required_source_classes"]
                    for endpoint in source["endpoints"]}
        self.assertEqual(set(entries), declared)
        for endpoint, entry in sorted(entries.items()):
            with self.subTest(endpoint=endpoint):
                self.assertTrue(entry["hit_proves"].strip())
                self.assertTrue(entry["hit_does_not_prove"])
        # A gene-index or page-existence hit is never class A evidence.
        for endpoint in IDENTITY_ONLY_ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                self.assertIs(entries[endpoint]["admissible_as_class_a"], False)
        # TCGA's disclaimer must name the four things it cannot show.
        tcga = entries["TCGA"]["hit_does_not_prove"]
        for claim in ("CRC 肿瘤表达", "prevalence", "malignant-cell attribution"):
            with self.subTest(claim=claim):
                self.assertIn(claim, " ".join(tcga))
        # They stay mandatory for coverage even though they prove no linkage.
        handling = self.doc["dataset_endpoint_handling"]
        self.assertEqual(set(handling["dataset_endpoints"]), set(IDENTITY_ONLY_ENDPOINTS))
        self.assertIs(handling["still_required_for_coverage"], True)
        self.assertIs(handling["hits_excluded_from_linkage_classes_hit"], True)
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-L26", ids)

    def test_trial_records_need_structured_fields_and_one_arm(self) -> None:
        entry = next(e for e in self.doc["endpoint_evidence_admissibility"]
                     if e["endpoint"] == "ClinicalTrials.gov")
        for field in ("intervention_name", "intervention_target",
                      "intervention_modality", "conditions", "arm_group_assignment"):
            with self.subTest(field=field):
                self.assertIn(field, entry["required_structured_fields"])
        self.assertIs(entry["same_arm_requirement"], True)
        self.assertIs(entry["requires_assertion_extraction"], True)
        ids = {r["id"] for r in self.doc["output_validation"]}
        self.assertIn("VAL-L28", ids)

    def test_retrieval_alone_does_not_close_the_search(self) -> None:
        scope = self.doc["declared_search_scope"]
        self.assertEqual(scope["scope_version"], "0.2.0")
        self.assertIs(scope["retrieval_alone_is_not_search_complete"], True)
        self.assertTrue(scope["retrieval_alone_is_not_search_complete_reason"].strip())
        definition = " ".join(scope["search_complete_definition"])
        for token in ("identity_resolution", "L-ASSERTION"):
            with self.subTest(token=token):
                self.assertIn(token, definition)
        # The disposition table must carry the per-pair assertion tally, so a
        # zero-assertion pair cannot be presented as a searched-and-empty one.
        columns = set(self.doc["output_schema"]["disposition_columns"])
        for column in ("assertion_extraction_complete", "retrieval_candidate_count",
                       "assertion_count"):
            with self.subTest(column=column):
                self.assertIn(column, columns)

    def test_the_target_axis_defect_is_recorded_not_silently_patched(self) -> None:
        """Fixing the axis inside EVGAP-02 would be an unauthorised axis change."""

        defect = self.doc["upstream_defect"]
        self.assertEqual(defect["id"], "GAP-P07")
        self.assertEqual(set(defect["entities"]),
                         {"Undisclosed", "EDBN", "AG7", "CA19-9"})
        self.assertEqual(defect["frozen_by_pr"], 58)
        self.assertIs(defect["requires_separate_pr"], True)
        self.assertEqual(defect["interim_handling"],
                         "本抽取按 L3-00 处理，全部 DEFER，既不 RETAIN 也不 EXCLUDE")
        self.assertTrue(defect["why_not_fixed_here"].strip())
        # The binding must in fact have declared identity_unresolved unavailable,
        # which is what the record claims.
        unavailable = {o["outcome"] for o in
                       self.doc_binding_lock_01_unavailable_outcomes()}
        self.assertIn("identity_unresolved", unavailable)
        # And this contract must forbid changing the axis.
        not_authorised = " ".join(self.doc["not_authorised"])
        self.assertIn("GAP-P07", not_authorised)
        self.assertIn("新增靶点", not_authorised)

    def doc_binding_lock_01_unavailable_outcomes(self) -> list:
        for key, value in self.binding.items():
            if isinstance(value, dict) and "unavailable_outcomes" in value:
                if any(o["outcome"] == "identity_unresolved"
                       for o in value["unavailable_outcomes"]):
                    return value["unavailable_outcomes"]
        raise AssertionError("binding declares no unavailable identity outcome")

    def test_authorisation_stops_short_of_level_01_and_other_gaps(self) -> None:
        not_authorised = " ".join(self.doc["not_authorised"])
        for phrase in ("执行 Level 01", "EVGAP-01", "tier_2", "T7", "Gate"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, not_authorised)
        # Level 01 itself must remain unauthorised.
        self.assertIs(self.binding["binding"]["authorises_level_01_execution"], False)


if __name__ == "__main__":
    unittest.main()
