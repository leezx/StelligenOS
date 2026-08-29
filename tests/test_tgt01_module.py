"""Runtime Migration PR E2: MOD-TGT01 deterministic scientific core.

Synthetic, in-memory only -- no network, no real ADC data, no persistence. The
target is ``TARGET_A`` and programs are ``PROGRAM_A`` .. ``PROGRAM_D``.

Covers the E2 acceptance scenarios:
DIRECT / INDIRECT_STRONG / WEAK positives; no evidence -> UNKNOWN; a single
failed ADC is never fatal; two independent consistent target-mediated failures
-> adverse pattern; positive + adverse pattern -> CONFLICTING; an unresolved
ADCdb-only lead never establishes a rung; an unresolved source_id is rejected;
an incomplete failure sweep rejects the run; a duplicate (source, claim) is
dropped; the proposal envelope carries every identity pin and no canonical
assessment id / version / review; the module builds no CandidateGateAssessment
or Decision.
"""

from __future__ import annotations

import unittest

from src.objects.decision_model import CandidateGateAssessment, EvidencePackage

from gate_modules.tgt01_adc_modality_precedent import (
    AssessmentProposalEnvelope,
    NormalizedPrecedentRecord,
    Tgt01ModuleInput,
    Tgt01ModuleRunResult,
    run,
)
from gate_modules.tgt01_adc_modality_precedent.contracts import (
    CANONICAL_ONLY_FIELDS,
    TGT01_EVIDENCE_CEILING,
    SweepCompletionRecord,
)


# --- deterministic fakes ----------------------------------------------------

class FakeAllocator:
    def __init__(self) -> None:
        self._n = 0

    def next_evidence_id(self) -> str:
        self._n += 1
        return f"EP-{self._n:08d}"


class FakeSourceRegistry:
    def __init__(self, unresolved: set[str] | None = None) -> None:
        self._unresolved = unresolved or set()

    def is_registered_primary_source(self, source_id: str) -> bool:
        return source_id not in self._unresolved


class FakeProvider:
    def __init__(
        self,
        records: list[NormalizedPrecedentRecord],
        sweep: SweepCompletionRecord,
    ) -> None:
        self._records = records
        self._sweep = sweep

    def fetch_precedents(self, **_: object) -> list[NormalizedPrecedentRecord]:
        return list(self._records)

    def sweep_completion(self, **_: object) -> SweepCompletionRecord:
        return self._sweep


_SWEEP_OK = SweepCompletionRecord(
    same_target_program_inventory_complete=True,
    failure_reason_sweep_complete=True,
)


def _input(**overrides: object) -> Tgt01ModuleInput:
    base: dict[str, object] = dict(
        candidate_id="CAND-L04-000123",
        candidate_name="TARGET_A",
        instantiation_id="INST-CRC-REFRACTORY-ADC-TARGET-v1",
        context_id="CTX-CRC-REFRACTORY-ADC",
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-01",
        gate_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        run_id="RUN-TEST",
        code_commit="0" * 12,
    )
    base.update(overrides)
    return Tgt01ModuleInput(**base)  # type: ignore[arg-type]


def _record(**overrides: object) -> NormalizedPrecedentRecord:
    base: dict[str, object] = dict(
        program_id="PROGRAM_A",
        target_relation="SAME_TARGET",
        program_stage="APPROVED",
        program_status="ACTIVE",
        clinical_activity_disclosed=True,
        claim="An ADC against TARGET_A with disclosed clinical activity",
        source_id="SRC-00000001",
        source_type="REGULATORY",
        source_identifier="FDA-BLA-0001",
        locator="",
        retrieved_at="2026-01-15",
        primary_source_resolved=True,
    )
    base.update(overrides)
    return NormalizedPrecedentRecord(**base)  # type: ignore[arg-type]


def _run(records, sweep=_SWEEP_OK, *, unresolved=None, module_input=None):
    return run(
        module_input or _input(),
        provider=FakeProvider(records, sweep),
        evidence_id_allocator=FakeAllocator(),
        source_registry=FakeSourceRegistry(unresolved),
        target_identity="TARGET_A",
    )


# --- positive rungs -------------------------------------------------------

class PositiveRungTests(unittest.TestCase):
    def test_direct_positive_from_an_approved_same_target_adc(self) -> None:
        res = _run([_record(program_stage="APPROVED", clinical_activity_disclosed=True)])
        self.assertTrue(res.machine_acceptance.accepted)
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "POSITIVE")
        self.assertEqual(env.proposed_strength, "DIRECT")
        self.assertEqual(len(res.evidence_packages), 1)
        self.assertEqual(env.evidence_refs, ((res.evidence_packages[0].evidence_id, "SUPPORTING"),))
        self.assertEqual(env.evidence_ceiling, TGT01_EVIDENCE_CEILING)

    def test_indirect_strong_from_a_phase_1_same_target_adc(self) -> None:
        res = _run([_record(program_stage="PHASE_1", clinical_activity_disclosed=False,
                            source_id="SRC-00000002", source_type="NCT",
                            source_identifier="NCT00000002")])
        self.assertEqual(res.proposal_envelope.proposed_direction, "POSITIVE")
        self.assertEqual(res.proposal_envelope.proposed_strength, "INDIRECT_STRONG")

    def test_weak_from_a_clinical_stage_adjacent_target_adc(self) -> None:
        res = _run([_record(target_relation="ADJACENT_TARGET", program_stage="APPROVED",
                            source_id="SRC-00000003")])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "POSITIVE")
        self.assertEqual(env.proposed_strength, "WEAK")
        # a WEAK-only positive flags that a same-target clinical precedent would lift it
        self.assertTrue(any("raise the strength" in u for u, _ in env.critical_unknowns))

    def test_strength_never_exceeds_the_strongest_rung_actually_met(self) -> None:
        # preclinical-only same-target -> WEAK, never DIRECT
        res = _run([_record(program_stage="PRECLINICAL", clinical_activity_disclosed=False,
                            source_type="DOI", source_identifier="10.x/preclin")])
        self.assertEqual(res.proposal_envelope.proposed_strength, "WEAK")
        checks = dict(res.machine_acceptance.checks)
        self.assertTrue(checks["proposed_strength_within_the_strongest_rung_met"])


# --- UNKNOWN and the single-failure rule --------------------------------------

class UnknownAndFatalPatternTests(unittest.TestCase):
    def test_no_admissible_evidence_is_the_unknown_state_not_kill(self) -> None:
        res = _run([])
        env = res.proposal_envelope
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(env.proposed_direction, "INCONCLUSIVE")
        self.assertEqual(env.proposed_strength, "UNKNOWN")
        self.assertEqual(env.evidence_refs, ())

    def test_a_single_failed_adc_is_never_negative_or_fatal(self) -> None:
        failed = _record(
            program_id="PROGRAM_A",
            program_status="DISCONTINUED",
            clinical_activity_disclosed=False,
            failure_reason="on-target GI toxicity",
            failure_attribution="TARGET_MEDIATED",
            failure_attribution_from_primary_source=True,
        )
        res = _run([failed])
        env = res.proposal_envelope
        self.assertNotEqual(env.proposed_direction, "NEGATIVE")
        self.assertEqual(env.proposed_direction, "INCONCLUSIVE")
        # its EP is present but contextual, not contradicting
        self.assertEqual(len(res.evidence_packages), 1)
        self.assertEqual({r for _, r in env.evidence_refs}, {"CONTEXTUAL"})

    def test_two_independent_consistent_target_mediated_failures_are_an_adverse_pattern(self) -> None:
        a = _record(program_id="PROGRAM_A", program_status="DISCONTINUED",
                    clinical_activity_disclosed=False, failure_reason="on-target tox",
                    failure_attribution="TARGET_MEDIATED",
                    failure_attribution_from_primary_source=True,
                    source_id="SRC-00000001")
        b = _record(program_id="PROGRAM_B", program_status="DISCONTINUED",
                    clinical_activity_disclosed=False, failure_reason="on-target tox",
                    failure_attribution="TARGET_MEDIATED",
                    failure_attribution_from_primary_source=True,
                    source_id="SRC-00000002", source_identifier="FDA-BLA-0002",
                    claim="A second same-target ADC discontinued for on-target toxicity")
        res = _run([a, b])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "NEGATIVE")
        self.assertEqual({r for _, r in env.evidence_refs}, {"CONTRADICTING"})

    def test_construct_specific_failures_do_not_form_a_pattern(self) -> None:
        a = _record(program_id="PROGRAM_A", program_status="DISCONTINUED",
                    failure_reason="linker instability",
                    failure_attribution="CONSTRUCT_SPECIFIC", source_id="SRC-00000001")
        b = _record(program_id="PROGRAM_B", program_status="DISCONTINUED",
                    failure_reason="payload manufacturing",
                    failure_attribution="CONSTRUCT_SPECIFIC", source_id="SRC-00000002",
                    claim="Second same-target ADC halted for a manufacturing reason")
        res = _run([a, b])
        self.assertEqual(res.proposal_envelope.proposed_direction, "INCONCLUSIVE")
        self.assertNotEqual(res.proposal_envelope.proposed_strength, "UNKNOWN")

    def test_positive_precedent_plus_adverse_pattern_is_conflicting(self) -> None:
        good = _record(program_id="PROGRAM_C", program_stage="APPROVED",
                       clinical_activity_disclosed=True, source_id="SRC-00000003",
                       claim="Approved same-target ADC with disclosed activity")
        f1 = _record(program_id="PROGRAM_A", program_status="DISCONTINUED",
                     failure_attribution="TARGET_MEDIATED",
                     failure_attribution_from_primary_source=True,
                     failure_reason="on-target tox", source_id="SRC-00000001",
                     claim="Same-target ADC 1 discontinued for on-target toxicity")
        f2 = _record(program_id="PROGRAM_B", program_status="DISCONTINUED",
                     failure_attribution="TARGET_MEDIATED",
                     failure_attribution_from_primary_source=True,
                     failure_reason="on-target tox", source_id="SRC-00000002",
                     claim="Same-target ADC 2 discontinued for on-target toxicity")
        res = _run([good, f1, f2])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "CONFLICTING")
        roles = {r for _, r in env.evidence_refs}
        self.assertIn("SUPPORTING", roles)
        self.assertIn("CONTRADICTING", roles)


# --- rejection paths --------------------------------------------------------

class RejectionTests(unittest.TestCase):
    def test_unresolved_adcdb_only_lead_never_establishes_a_rung(self) -> None:
        lead = _record(primary_source_resolved=False,
                       claim="ADCdb inventory row, not yet resolved to a primary source")
        res = _run([lead])
        self.assertEqual(len(res.evidence_packages), 0)
        self.assertEqual(res.proposal_envelope.proposed_direction, "INCONCLUSIVE")
        self.assertEqual(res.proposal_envelope.proposed_strength, "UNKNOWN")
        self.assertTrue(any("unresolved primary source" in why for _, why in res.rejected_records))

    def test_unresolved_source_id_is_rejected(self) -> None:
        res = _run([_record(source_id="SRC-00000009")], unresolved={"SRC-00000009"})
        self.assertEqual(len(res.evidence_packages), 0)
        self.assertTrue(
            any("not a registered" in why for _, why in res.rejected_records)
        )

    def test_incomplete_failure_sweep_rejects_the_run(self) -> None:
        for sweep in (
            SweepCompletionRecord(True, False),
            SweepCompletionRecord(False, True),
            SweepCompletionRecord(False, False),
        ):
            res = _run([_record()], sweep=sweep)
            self.assertFalse(res.machine_acceptance.accepted)
            self.assertIsNone(res.proposal_envelope)
            self.assertTrue(res.machine_acceptance.reasons)

    def test_a_positive_ceiling_does_not_bypass_the_sweep_prerequisite(self) -> None:
        # a DIRECT positive is present, but the sweep is incomplete -> still rejected
        res = _run([_record(program_stage="APPROVED", clinical_activity_disclosed=True)],
                   sweep=SweepCompletionRecord(True, False))
        self.assertFalse(res.machine_acceptance.accepted)

    def test_duplicate_source_and_claim_is_dropped(self) -> None:
        one = _record(program_id="PROGRAM_A", source_id="SRC-00000001",
                      claim="Identical observation")
        two = _record(program_id="PROGRAM_A2", source_id="SRC-00000001",
                      claim="Identical observation")
        res = _run([one, two])
        self.assertEqual(len(res.evidence_packages), 1)
        self.assertTrue(any("duplicate" in why for _, why in res.rejected_records))

    def test_target_mediated_attribution_requires_a_primary_source_disclosure(self) -> None:
        with self.assertRaises(ValueError):
            _record(
                program_status="DISCONTINUED",
                failure_attribution="TARGET_MEDIATED",
                failure_attribution_from_primary_source=False,
            )


# --- input contract -------------------------------------------------------

class InputContractTests(unittest.TestCase):
    def test_no_implicit_default_scientific_context(self) -> None:
        for bad in (
            dict(gate_id="TGT-02"),
            dict(gateset_id="SOME_OTHER_GATESET"),
            dict(evidence_regime="PUBLIC_PLUS_EXPERIMENTAL"),
            dict(instantiation_id="INST-OTHER-v1"),
            dict(candidate_id="CAND-L03-000001"),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    _input(**bad)


# --- proposal / canonical boundary -----------------------------------------

class ProposalEnvelopeBoundaryTests(unittest.TestCase):
    def test_envelope_carries_every_identity_pin(self) -> None:
        env = _run([_record()]).proposal_envelope
        for pin in (
            "candidate_id", "instantiation_id", "context_id", "context_version",
            "gateset_id", "gateset_version", "gate_id", "gate_version",
        ):
            self.assertIn(pin, AssessmentProposalEnvelope.field_names())
            self.assertTrue(getattr(env, pin) not in (None, ""))

    def test_envelope_carries_no_canonical_assessment_id_version_or_review(self) -> None:
        names = set(AssessmentProposalEnvelope.field_names())
        for forbidden in CANONICAL_ONLY_FIELDS:
            self.assertNotIn(forbidden, names)

    def test_module_builds_no_canonical_assessment_or_decision(self) -> None:
        res = _run([_record()])
        self.assertIsInstance(res, Tgt01ModuleRunResult)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertNotIsInstance(res.proposal_envelope, CandidateGateAssessment)
        self.assertTrue(all(isinstance(ep, EvidencePackage) for ep in res.evidence_packages))
        for attr in ("decision", "assessment", "candidate_gate_assessment", "kill"):
            self.assertFalse(hasattr(res, attr))

    def test_the_run_result_is_in_memory_only(self) -> None:
        # every member is a frozen value / tuple; nothing here is a path or handle
        res = _run([_record()])
        import dataclasses

        self.assertTrue(dataclasses.is_dataclass(res))
        self.assertIsInstance(res.evidence_packages, tuple)
        self.assertIsInstance(res.rejected_records, tuple)


if __name__ == "__main__":
    unittest.main()
