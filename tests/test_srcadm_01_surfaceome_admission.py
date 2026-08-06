"""Verify docs/pools/srcadm_01_surfaceome_admission.yaml.

The audit record must cover every scope item PR #59 froze, must not grant
admission by itself, and must keep every conclusion tied to a stated,
recheckable basis. These tests read no external database: the audit already ran
and its evidence is recorded in the file under test.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
POOLS = REPO_ROOT / "docs" / "pools"
AUDIT_PATH = POOLS / "srcadm_01_surfaceome_admission.yaml"
EVGAP_01_PATH = POOLS / "evgap_01_surface_localization_extraction.yaml"

VERDICTS = frozenset({"PASS", "PASS_WITH_FINDING", "FAIL"})


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class Srcadm01AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load(AUDIT_PATH)
        cls.evgap = _load(EVGAP_01_PATH)
        cls.findings = {f["id"]: f for f in cls.doc["audit_findings"]}

    def test_audit_targets_the_dependency_evgap_01_registered(self) -> None:
        head = self.doc["admission"]
        dep = self.evgap["source_admission_dependency"]
        self.assertEqual(head["admission_id"], dep["id"])
        self.assertEqual(head["dataset_id"], dep["dataset_id"])
        self.assertEqual(str(head["dataset_version"]), str(dep["dataset_version"]))
        self.assertEqual(head["snapshot_id"], dep["snapshot_id"])
        self.assertEqual(head["audit_scope_frozen_by_pr"], 59)

    def test_every_frozen_scope_item_is_answered(self) -> None:
        required = {item["id"] for item in
                    self.evgap["source_admission_dependency"]["required_audit_items"]}
        self.assertEqual(set(self.findings), required)
        self.assertEqual(self.doc["admission"]["audit_scope_items"], len(required))
        for fid, finding in sorted(self.findings.items()):
            with self.subTest(item=fid):
                self.assertIn(finding["verdict"], VERDICTS)
                self.assertTrue(finding["item"].strip())

    def test_no_scope_item_failed_outright(self) -> None:
        failed = [f for f in self.findings.values() if f["verdict"] == "FAIL"]
        self.assertEqual(failed, [], f"failed items: {[f['id'] for f in failed]}")

    def test_every_finding_states_a_recheckable_basis(self) -> None:
        """A verdict with no evidence and no finding is an assertion, not an audit."""

        for fid, finding in sorted(self.findings.items()):
            with self.subTest(item=fid):
                basis = [k for k in ("evidence", "finding", "integrity_verified")
                         if str(finding.get(k, "")).strip()]
                self.assertTrue(basis, f"{fid} records no basis")
                if finding["verdict"] == "PASS_WITH_FINDING":
                    self.assertTrue(str(finding.get("finding", "")).strip(),
                                    f"{fid} is PASS_WITH_FINDING but names no finding")

    def test_admission_comes_from_the_record_not_from_this_file(self) -> None:
        """The audit is approved, but this file still grants nothing by itself:
        the grant lives in the review record it points at."""

        head = self.doc["admission"]
        self.assertEqual(head["status"], "approved")
        self.assertIs(head["grants_admission_by_itself"], False)
        self.assertIs(head["admission_granted"], True)
        self.assertEqual(head["admission_granted_by_pr"], 63)
        ref = head["admission_record_ref"]
        self.assertTrue(ref)
        self.assertTrue((REPO_ROOT / ref).is_file(), f"missing record: {ref}")
        # EVGAP-01 must cite the very same record, not a second one.
        dep = self.evgap["source_admission_dependency"]
        self.assertEqual(dep["admission_record_ref"], ref)
        self.assertEqual(dep["admission_status"], "admitted_with_conditions")
        # The recommendation was conditional, so the grant must be too.
        self.assertEqual(head["recommendation"], "admissible_with_conditions")
        self.assertIs(dep["admission_is_conditional"], True)
        self.assertEqual(dep["admission_conditions"],
                         [c["id"] for c in self.doc["admission_conditions"]])

    def test_the_grant_reaches_extraction_but_stops_there(self) -> None:
        """Admission authorises one EVGAP-01 run. It must not reach Level 01."""

        extraction = self.evgap["extraction"]
        self.assertIs(extraction["authorises_extraction_run"], True)
        self.assertEqual(extraction["authorises_extraction_run_count"], 1)
        self.assertIs(extraction["authorises_level_01_execution"], False)
        self.assertIs(extraction["requires_followup_binding_pr"], True)
        # The audit still disclaims the things it never covered.
        not_authorised = " ".join(self.doc["not_authorised"])
        for phrase in ("Level 01", "其他版本", "字段白名单"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, not_authorised)

    def test_recommendation_is_conditional_and_the_conditions_exist(self) -> None:
        self.assertEqual(self.doc["admission"]["recommendation"],
                         "admissible_with_conditions")
        conditions = {c["id"]: c for c in self.doc["admission_conditions"]}
        self.assertGreaterEqual(len(conditions), 4)
        for cid, cond in sorted(conditions.items()):
            with self.subTest(condition=cid):
                self.assertTrue(cond["condition"].strip())
                self.assertTrue(cond["detail"].strip())

    def test_family_independence_is_the_load_bearing_pass(self) -> None:
        """AUD-05 is the item the reviewer singled out; it must not be hand-waved."""

        aud = self.findings["AUD-05"]
        self.assertEqual(aud["verdict"], "PASS")
        self.assertIs(aud["counting_requires_support"], True)
        for key in ("same_origin_pair_handled", "counting_requires_support_evidence",
                    "structural_guarantee"):
            with self.subTest(key=key):
                self.assertTrue(str(aud[key]).strip())
        # The same-origin pair must be named, not merely alluded to.
        text = aud["same_origin_pair_handled"]
        self.assertIn("goa_human", text)
        self.assertIn("uniprot_reviewed_human", text)
        # The counterexample check must cite a measured count, and it must state
        # the denominator. "11,334 genes with plasma_membrane=false" is ambiguous
        # on its own: 18,534 consensus rows carry that value, most because HPA
        # never covered the gene at all. Both figures must appear so the reader
        # cannot conflate them.
        counterexample = aud["counting_requires_support_evidence"]
        for figure in ("13,597", "11,334", "18,534"):
            with self.subTest(figure=figure):
                self.assertIn(figure, counterexample)
        self.assertIn("从未被 HPA 覆盖", counterexample)

    def test_the_audit_ships_a_bundle_that_can_be_recomputed(self) -> None:
        """Tests on this file prove only internal consistency. The external facts
        need an external, re-runnable bundle."""

        bundle = self.doc["audit_bundle"]
        self.assertIs(bundle["read_only"], True)
        self.assertIs(bundle["grants_admission"], False)
        self.assertTrue(bundle["reverification_command"].strip())
        self.assertEqual(bundle["recomputed_result"], "all_match")
        self.assertGreaterEqual(bundle["recomputed_checks"], 40)
        # A 64-hex package digest, so a swapped package is detectable.
        digest = bundle["package_sha256"]
        self.assertEqual(len(digest), 64, digest)
        self.assertTrue(all(c in "0123456789abcdef" for c in digest))
        # Every scope item must be served by at least one shipped file. The
        # literal "all" marks the verifier and its report, which serve every
        # item; it is not itself a scope item, so drop it before comparing.
        served = {item for entry in bundle["contents"] for item in entry["serves"]}
        self.assertIn("all", served, "no file is declared as serving every item")
        served.discard("all")
        required = {item["id"] for item in
                    self.evgap["source_admission_dependency"]["required_audit_items"]}
        self.assertEqual(required - served, set(),
                         f"scope items with no bundle file: {sorted(required - served)}")

    def test_the_bundle_states_what_it_cannot_prove(self) -> None:
        """A bundle that implies everything is recomputable would be worse than
        no bundle."""

        bundle = self.doc["audit_bundle"]
        # Full tables, not representative rows — otherwise the counts are
        # unverifiable and the reviewer is back to trusting the narrative.
        self.assertIs(bundle["processed_tables_subset"], False)
        self.assertTrue(bundle["processed_tables_subset_reason"].strip())
        limits = bundle["not_independently_recomputable_in_bundle"]
        self.assertTrue(limits)
        raw_limit = next(item for item in limits if "AUD-09" in item["item"])
        self.assertTrue(raw_limit["reason"].strip())
        self.assertTrue(raw_limit["what_is_provided"].strip())
        # The limitation must be the one the conditions already declare, not a
        # new and unrecorded one.
        self.assertEqual(raw_limit["already_stated_as"], "COND-03")
        conditions = {c["id"] for c in self.doc["admission_conditions"]}
        self.assertIn("COND-03", conditions)

    def test_license_ambiguity_is_bounded_by_the_field_whitelist(self) -> None:
        aud = self.findings["AUD-04"]
        self.assertEqual(aud["verdict"], "PASS_WITH_FINDING")
        self.assertTrue(aud["decisive_check"].strip())
        self.assertTrue(aud["load_bearing_boundary"].strip())
        # The barred field the conclusion depends on must actually be barred there.
        barred = {item["field"] for item in self.evgap["barred_fields"]}
        self.assertIn("cci_receptor_role", barred)
        # And the dependency must be recorded as a condition, not just prose.
        conditions = {c["id"]: c for c in self.doc["admission_conditions"]}
        whitelist_conditions = [c for c in conditions.values()
                                if "白名单" in c["condition"] + c["detail"]]
        self.assertTrue(whitelist_conditions)

    def test_reproducibility_limit_is_stated_not_glossed(self) -> None:
        aud = self.findings["AUD-09"]
        self.assertEqual(aud["verdict"], "PASS_WITH_FINDING")
        self.assertTrue(aud["integrity_verified"].strip())
        self.assertTrue(aud["determinism"].strip())
        # The finding must name both un-pinned sources and say what that costs,
        # not merely mention the phrase somewhere in the paragraph.
        finding = aud["finding"]
        for token in ("current_at_download", "uniprot_reviewed_human", "goa_human",
                      "逐字节"):
            with self.subTest(token=token):
                self.assertIn(token, finding)
        # AUD-03 must carry the same limitation rather than contradicting it.
        aud_03 = self.findings["AUD-03"]["finding"]
        for token in ("current_at_download", "uniprot_reviewed_human", "goa_human"):
            with self.subTest(item="AUD-03", token=token):
                self.assertIn(token, aud_03)
        conditions = " ".join(c["detail"] for c in self.doc["admission_conditions"])
        self.assertIn("current_at_download", conditions)

    def test_dedup_finding_bounds_its_own_impact(self) -> None:
        aud = self.findings["AUD-06"]
        self.assertEqual(aud["verdict"], "PASS_WITH_FINDING")
        bound = aud["bounded_impact"]
        self.assertTrue(bound.strip())
        # The bound must exclude the target axis explicitly and name the genes it
        # affects, so weakening it to a vague phrase fails.
        self.assertIn("没有一个属于", bound)
        self.assertIn("41 个靶点", bound)
        for gene in ("HERC3", "NRXN1", "SIRPB1"):
            with self.subTest(gene=gene):
                self.assertIn(gene, bound)

    def test_raw_manifest_digest_was_recomputed_not_copied(self) -> None:
        aud = self.findings["AUD-02"]
        self.assertEqual(aud["verdict"], "PASS")
        self.assertEqual(aud["verification_method"], "recomputed")
        # The digest must be the same one EVGAP-01's AUD-02 item points at, and it
        # must appear in the evidence as a recomputed value rather than a citation.
        item = next(a["item"] for a in
                    self.evgap["source_admission_dependency"]["required_audit_items"]
                    if a["id"] == "AUD-02")
        prefix = "884f4191"
        self.assertIn(prefix, item)
        self.assertIn(prefix, aud["evidence"])
        digest = next(w.strip(" ,.;，。") for w in aud["evidence"].split()
                      if w.startswith(prefix))
        self.assertEqual(len(digest), 64, digest)
        self.assertTrue(all(c in "0123456789abcdef" for c in digest))

    def test_traceback_names_the_targets_it_traced(self) -> None:
        aud = self.findings["AUD-08"]
        self.assertEqual(aud["verdict"], "PASS")
        traced = aud["targets_traced"]
        self.assertGreaterEqual(len(traced), 3)
        for gene in traced:
            with self.subTest(gene=gene):
                self.assertIn(gene, aud["evidence"])
        # GUCY2C is the case that contradicts the earlier consensus; keep it visible.
        self.assertIn("GUCY2C", traced)

    def test_discordance_rules_only_defer_and_never_retain(self) -> None:
        aud = self.findings["AUD-07"]
        self.assertEqual(aud["verdict"], "PASS")
        self.assertEqual(len(aud["rules"]), 4)
        self.assertIn("DEFER", aud["relevance_to_evgap_01"])
        # The EVGAP-01 rule it relies on must in fact defer on discordance.
        rule = next(r for r in self.evgap["derivation_rules"] if r["id"] == "E1-04")
        self.assertEqual(rule["disposition"], "DEFER")


if __name__ == "__main__":
    unittest.main()
