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
        valid = {o["outcome"]: o for o in lock_03["outcomes"]}
        for rule in rules["rules"]:
            with self.subTest(rule=rule["id"]):
                self.assertIn(rule["outcome"], valid)
                self.assertIn(
                    rule["disposition"],
                    {CandidateDisposition.RETAIN.value, CandidateDisposition.DEFER.value},
                )
                self.assertEqual(
                    rule["resulting_state"], valid[rule["outcome"]]["resulting_state"]
                )
        self.assertEqual(
            rules["evidence_granularity"], "disease_level_not_subgroup_level"
        )

    def test_vacuous_linkage_bases_must_block_execution(self) -> None:
        """If no linkage basis qualifies, the binding must not authorise a run."""

        bases = self.binding["lock_03_linkage_rules"]["accepted_linkage_bases"]
        self.assertGreaterEqual(len(bases), 2)
        ids = [b["basis_id"] for b in bases]
        self.assertEqual(len(ids), len(set(ids)))
        for basis in bases:
            with self.subTest(basis=basis["basis_id"]):
                self.assertEqual(basis["required_direction"], "supporting")
                # Vacuity is decided by QUALIFYING units, not merely supporting
                # ones: pan-cancer precedent is supporting but does not qualify.
                self.assertIsInstance(basis["measured_qualifying_units"], int)
                self.assertEqual(
                    basis["vacuous_this_run"], basis["measured_qualifying_units"] == 0
                )
        live = [b for b in bases if not b["vacuous_this_run"]]
        if not live:
            self.assertIs(self.binding["binding"]["authorises_level_01_execution"], False)

    def test_pan_cancer_precedent_cannot_establish_crc_linkage(self) -> None:
        basis = next(
            b for b in self.binding["lock_03_linkage_rules"]["accepted_linkage_bases"]
            if b["basis_id"] == "LB-precedent"
        )
        self.assertIs(basis["requires_source_level_crc_indication"], True)
        self.assertIs(basis["indication_fit_may_substitute"], False)
        self.assertEqual(basis["other_cancer_precedent_disposition"], "metadata_only_hold")
        for field in ("precedent_indication", "source_locator"):
            self.assertIn(field, basis["required_recorded_fields"])
        # Supporting-but-not-qualifying must be visible, not collapsed.
        self.assertGreater(basis["measured_supporting_units"], 0)
        self.assertEqual(basis["measured_qualifying_units"], 0)
        self.assertTrue(basis["measurement_trap"].strip())

        rules = {r["id"]: r for r in self.binding["lock_03_linkage_rules"]["rules"]}
        for rule_id in ("LNK-02b", "LNK-02c"):
            with self.subTest(rule=rule_id):
                self.assertEqual(
                    rules[rule_id]["disposition"], CandidateDisposition.DEFER.value
                )
                self.assertEqual(rules[rule_id]["resulting_state"], "hold")

    def test_transmembrane_topology_alone_cannot_retain(self) -> None:
        derivation = self.binding["lock_01_derivation"]
        self.assertIs(derivation["retain_requirements_satisfiable_by_approved_inputs"], False)
        required = {r["requirement_id"] for r in derivation["retain_requirements"]}
        self.assertEqual(required, {"RQ-01", "RQ-02", "RQ-03"})
        self.assertEqual(set(derivation["retain_requires_all_of"]), required)
        claims = {r["requirement_id"]: r for r in derivation["retain_requirements"]}
        self.assertEqual(claims["RQ-01"]["claim"], "plasma_membrane_localization")
        self.assertEqual(claims["RQ-02"]["claim"], "extracellular_domain_or_topology")
        for requirement in derivation["retain_requirements"]:
            self.assertIs(requirement["must_be_protein_level"], True)

        rules = {r["id"]: r for r in derivation["rules"]}
        # The transmembrane-only rule must defer, and the RETAIN rule must
        # demand all three requirements rather than a bare locator.
        tm_rule = rules["L1-02"]
        self.assertIn("transmembrane_segment_count", tm_rule["condition"])
        self.assertEqual(tm_rule["disposition"], CandidateDisposition.DEFER.value)
        self.assertEqual(tm_rule["resulting_state"], "hold")
        retain = rules["L1-01"]
        self.assertEqual(retain["disposition"], CandidateDisposition.RETAIN.value)
        for requirement_id in required:
            self.assertIn(requirement_id, retain["condition"])
        self.assertNotIn("transmembrane_segment_count", retain["condition"])

    def test_organelle_or_conflicting_localization_defers(self) -> None:
        rules = {r["id"]: r for r in self.binding["lock_01_derivation"]["rules"]}
        organelle = rules["L1-04"]
        self.assertEqual(organelle["disposition"], CandidateDisposition.DEFER.value)
        self.assertEqual(organelle["resulting_state"], "hold")
        self.assertEqual(organelle["outcome"], "possible_surface_target")

    def test_evidence_gaps_block_execution_and_name_their_next_run(self) -> None:
        gaps = {g["id"]: g for g in self.binding["evidence_gaps"]}
        self.assertEqual(set(gaps), {"EVGAP-01", "EVGAP-02"})
        self.assertEqual(
            set(self.binding["binding"]["level_01_execution_blocked_by"]), set(gaps)
        )
        self.assertEqual(
            self.binding["binding"]["scope_of_authorisation"], "raw_axis_binding_only"
        )
        self.assertIs(self.binding["binding"]["authorises_level_01_execution"], False)
        self.assertIs(self.binding["predicted_result_shape"]["is_authorised_to_execute"], False)
        for gap in gaps.values():
            with self.subTest(gap=gap["id"]):
                self.assertIn(gap["blocks"], {"LOCK-01", "LOCK-03"})
                for field in ("missing", "measured", "consequence", "required_next_run"):
                    self.assertTrue(str(gap[field]).strip())
        not_authorised = " ".join(self.binding["not_authorised"])
        self.assertIn("执行 Level 01", not_authorised)

    def test_predicted_shape_reconciles_with_the_counting_identities(self) -> None:
        shape = self.binding["predicted_result_shape"]
        scope = self.binding["scope_consequences"]
        ctx, tgt = shape["context_eligibility"], shape["target_eligibility"]
        pool = shape["pool_level_01"]

        # CNT-01
        self.assertEqual(shape["raw_enumeration_matrix"], scope["raw_enumeration_matrix_pairs"])
        # CNT-04 and CNT-05
        self.assertEqual(
            ctx["eligible"] + ctx["hold"] + ctx["superseded"], scope["raw_clinical_contexts"]
        )
        self.assertEqual(
            tgt["eligible"] + tgt["hold"] + tgt["killed"], scope["raw_targets"]
        )
        # CNT-02
        self.assertEqual(
            shape["eligible_universe_index"], ctx["eligible"] * tgt["eligible"]
        )
        # CNT-03
        self.assertEqual(
            pool["active"] + pool["hold"] + pool["reactivation_eligible"],
            shape["eligible_universe_index"],
        )
        # Consistent with the LOCK-01 derivation and the LOCK-02 ceiling.
        self.assertEqual(tgt["eligible"], self.binding["lock_01_derivation"]["coverage"]["eligible"])
        self.assertEqual(tgt["hold"], self.binding["lock_01_derivation"]["coverage"]["hold"])
        self.assertEqual(tgt["killed"], 0)
        # An empty universe must not be presented as an authorised run.
        if shape["eligible_universe_index"] == 0:
            self.assertIs(shape["is_authorised_to_execute"], False)
            self.assertTrue(shape["conclusion"].strip())
        calibrated = [
            e for e in self.binding["lock_02_status_ceiling"]
            if e["calibration"] == "calibrated"
        ]
        self.assertEqual(ctx["eligible"], sum(e["count"] for e in calibrated))
        self.assertTrue(shape["derivation_note"].strip())

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

    # ---- Blocker 1: LOCK-01 must be derivable without free judgement ----

    def test_lock_01_derivation_maps_every_outcome_uniquely(self) -> None:
        derivation = self.binding["lock_01_derivation"]
        lock_01 = next(l for l in self.level["locks"] if l["lock_id"] == "LOCK-01")
        declared = {o["outcome"]: o for o in lock_01["outcomes"]}

        produced = {r["outcome"] for r in derivation["rules"]}
        unavailable = {u["outcome"] for u in derivation["unavailable_outcomes"]}
        # Every outcome the level declares is either produced or explicitly barred.
        self.assertEqual(produced | unavailable, set(declared))
        self.assertEqual(produced & unavailable, set())

        for rule in derivation["rules"]:
            with self.subTest(rule=rule["id"]):
                outcome = declared[rule["outcome"]]
                self.assertEqual(rule["disposition"], outcome["disposition"])
                self.assertEqual(rule["resulting_state"], outcome["resulting_state"])
        for barred in derivation["unavailable_outcomes"]:
            with self.subTest(outcome=barred["outcome"]):
                self.assertTrue(barred["reason"].strip())

    def test_lock_01_rna_evidence_can_never_retain(self) -> None:
        derivation = self.binding["lock_01_derivation"]
        self.assertIs(derivation["rna_derived_locators_may_retain"], False)
        retaining = [
            r for r in derivation["rules"]
            if r["disposition"] == CandidateDisposition.RETAIN.value
        ]
        self.assertTrue(retaining)
        for rule in retaining:
            with self.subTest(rule=rule["id"]):
                # RETAIN must rest on localization plus extracellular topology,
                # never on a bare annotation basis.
                self.assertEqual(
                    rule["evidence_basis"],
                    "plasma_membrane_localization_and_extracellular_topology",
                )
        # Any rule whose reason invokes RNA must defer.
        for rule in derivation["rules"]:
            if "RNA" in rule.get("reason", ""):
                self.assertEqual(rule["disposition"], CandidateDisposition.DEFER.value)

    def test_lock_01_missing_or_conflicting_evidence_never_excludes(self) -> None:
        derivation = self.binding["lock_01_derivation"]
        for rule in derivation["rules"]:
            with self.subTest(rule=rule["id"]):
                self.assertNotEqual(
                    rule["disposition"], CandidateDisposition.EXCLUDE.value
                )
        self.assertIn(
            "not_surface_target",
            {u["outcome"] for u in derivation["unavailable_outcomes"]},
        )
        self.assertEqual(derivation["coverage"]["killed"], 0)

    def test_lock_01_cannot_read_prior_dispositions_or_gate_labels(self) -> None:
        derivation = self.binding["lock_01_derivation"]
        barred = set(derivation["barred_fields"])
        for field in ("disposition", "gate_score_status", "gate_pass_status"):
            self.assertIn(field, barred)
        # The decisive field must not itself be a barred field.
        self.assertNotIn(derivation["decisive_field"], barred)
        semantics = self.binding["lock_01_input_semantics"]
        self.assertIs(semantics["may_be_inherited_as_lock_01_outcome"], False)

    def test_lock_01_coverage_accounts_for_every_target(self) -> None:
        derivation = self.binding["lock_01_derivation"]
        coverage = derivation["coverage"]
        self.assertEqual(
            coverage["eligible"] + coverage["hold"] + coverage["killed"],
            coverage["total_targets"],
        )
        self.assertEqual(
            coverage["total_targets"],
            self.binding["scope_consequences"]["raw_targets"],
        )
        self.assertIs(coverage["determinate_without_free_judgement"], True)
        # Non-vacuous rules must carry an expected count, and those must reconcile.
        counted = sum(
            r["expected_count"] for r in derivation["rules"] if "expected_count" in r
        )
        self.assertEqual(counted, coverage["total_targets"])
        for rule in derivation["rules"]:
            if "expected_count" not in rule:
                with self.subTest(rule=rule["id"]):
                    self.assertIs(rule["vacuous_this_run"], True)
                    self.assertTrue(rule["vacuous_reason"].strip())

    # ---- Blocker 2: the context projection must be deterministic ----

    def _project(self, rows: list[dict]) -> dict:
        """Reference implementation of the declared projection rules."""

        projection = self.binding["clinical_context_projection"]
        key_fields = projection["determinism"]["dedupe_key"]
        deduped = {tuple(row[f] for f in key_fields): row for row in rows}
        ordered = sorted(
            deduped.values(),
            key=lambda r: tuple(r[f] for f in projection["determinism"]["sort_rows_by"]),
        )
        groups: dict[str, list[dict]] = {}
        for row in ordered:
            groups.setdefault(row[projection["group_by"]], []).append(row)

        contexts = {}
        for indication_id, members in sorted(groups.items()):
            constant = projection["context_level_fields_required_constant"]
            conflicted = any(
                len({m[field] for m in members}) != 1 for field in constant
            )
            roles = {m["endpoint_role"] for m in members}
            incomplete = roles != set(
                projection["endpoint_handling"]["required_endpoint_roles"]
            )
            contexts[indication_id] = {
                "clinical_context_ref": projection["context_ref_template"].format(
                    indication_id=indication_id
                ),
                "endpoint_candidates": [
                    (m["endpoint_role"], m["endpoint"]) for m in members
                ],
                "endpoint_maturity": projection["endpoint_handling"][
                    "endpoint_maturity_value"
                ],
                "source_row_keys": [
                    tuple(m[f] for f in projection["provenance"]["source_row_key_fields"])
                    for m in members
                ],
                "outcome": "undefined_context" if (conflicted or incomplete) else None,
            }
        return contexts

    @staticmethod
    def _fixture() -> list[dict]:
        """Synthetic rows mirroring the approved file's schema. Not real data."""

        roles = (
            ("regulatory_ultimate", "OS"),
            ("pivotal_supporting", "PFS"),
            ("early_adc_proof", "ORR"),
            ("supportive_exploratory", "DCR"),
        )
        rows = []
        for n in range(1, 10):
            for role, endpoint in roles:
                rows.append(
                    {
                        "indication_id": f"ctx_{n:02d}",
                        "label": f"context {n}",
                        "status": "derived_strategy",
                        "source": "pilot",
                        "clinical_need": "need",
                        "confidence": "not_calibrated",
                        "priority": str(n),
                        "endpoint_role": role,
                        "endpoint": endpoint,
                        "rationale": f"rationale {role}",
                    }
                )
        return rows

    def test_projection_turns_36_rows_into_exactly_9_contexts(self) -> None:
        projection = self.binding["clinical_context_projection"]
        self.assertEqual(projection["input_rows"], 36)
        self.assertEqual(
            projection["output_contexts"],
            self.binding["scope_consequences"]["raw_clinical_contexts"],
        )
        rows = self._fixture()
        self.assertEqual(len(rows), projection["input_rows"])
        contexts = self._project(rows)
        self.assertEqual(len(contexts), projection["output_contexts"])
        self.assertTrue(all(c["outcome"] is None for c in contexts.values()))

    def test_projection_is_independent_of_input_row_order(self) -> None:
        rows = self._fixture()
        forward = self._project(rows)
        backward = self._project(list(reversed(rows)))
        # Deterministic: reversing the input changes nothing, including provenance.
        self.assertEqual(forward, backward)
        rotated = self._project(rows[7:] + rows[:7])
        self.assertEqual(forward, rotated)

    def test_duplicate_endpoint_rows_do_not_change_context_identity(self) -> None:
        rows = self._fixture()
        baseline = self._project(rows)
        with_dupes = self._project(rows + rows[:5])
        self.assertEqual(baseline, with_dupes)
        self.assertEqual(
            self.binding["clinical_context_projection"]["determinism"][
                "measured_duplicate_role_pairs"
            ],
            0,
        )

    def test_conflicting_or_incomplete_rows_defer_and_never_exclude(self) -> None:
        projection = self.binding["clinical_context_projection"]
        for rule in projection["conflict_handling"]:
            with self.subTest(rule=rule["id"]):
                self.assertEqual(rule["disposition"], CandidateDisposition.DEFER.value)
                self.assertEqual(rule["resulting_state"], "hold")
                self.assertEqual(rule["outcome"], "undefined_context")

        # A varying context-level field must take the conflict path.
        rows = self._fixture()
        rows[0] = dict(rows[0], confidence="calibrated")
        conflicted = self._project(rows)
        self.assertEqual(conflicted["ctx_01"]["outcome"], "undefined_context")

        # A missing endpoint role must take the same path.
        rows = [r for r in self._fixture() if not (
            r["indication_id"] == "ctx_02" and r["endpoint_role"] == "early_adc_proof"
        )]
        incomplete = self._project(rows)
        self.assertEqual(incomplete["ctx_02"]["outcome"], "undefined_context")
        self.assertIsNone(incomplete["ctx_01"]["outcome"])

    def test_every_input_row_is_traceable_to_its_context(self) -> None:
        projection = self.binding["clinical_context_projection"]
        self.assertIs(projection["provenance"]["every_input_row_must_be_referenced"], True)
        rows = self._fixture()
        contexts = self._project(rows)
        referenced = [key for c in contexts.values() for key in c["source_row_keys"]]
        expected = [
            tuple(r[f] for f in projection["provenance"]["source_row_key_fields"])
            for r in rows
        ]
        self.assertEqual(sorted(referenced), sorted(expected))
        self.assertEqual(len(referenced), len(set(referenced)), "row referenced twice")

    def test_context_identity_excludes_endpoint_and_endpoint_stays_unlocked(self) -> None:
        projection = self.binding["clinical_context_projection"]
        self.assertEqual(projection["identity_fields"], ["indication_id"])
        self.assertEqual(projection["context_ref_depends_only_on"], "indication_id")
        handling = projection["endpoint_handling"]
        self.assertIs(handling["endpoint_locked"], False)
        for dropped in ("endpoint", "endpoint_role"):
            self.assertIn(dropped, handling["dropped_from_context_identity"])
        self.assertEqual(handling["endpoint_maturity_value"], "not_locked_at_level_01")
        # Changing an endpoint value must not change any context ref.
        rows = self._fixture()
        baseline = self._project(rows)
        rows[1] = dict(rows[1], endpoint="EFS")
        altered = self._project(rows)
        self.assertEqual(
            {k: v["clinical_context_ref"] for k, v in baseline.items()},
            {k: v["clinical_context_ref"] for k, v in altered.items()},
        )

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
