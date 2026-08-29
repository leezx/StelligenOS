"""Runtime Migration PR E2: MOD-TGT01 deterministic scientific core.

Synthetic, in-memory only -- no network, no real ADC data, no persistence. The
candidate target is ``TARGET_A``; an adjacent antigen is ``TARGET_B``; programs
are ``PROGRAM_A`` .. ``PROGRAM_D``.

Covers the E2 acceptance scenarios and the review-round-1 blockers:
candidate <-> program target-identity binding (misbinding rejected; adjacent EP
recovers the actual antigen + basis); both frozen item-08 fatal branches
(target-mediated toxicity AND intrinsically unachievable therapeutic window)
with a consistent-class pattern; a single failed ADC never fatal; Gate-neutral
EvidencePackages with reuse by id and canonical-source-resolved provenance; one
package per observation (a program with two observations -> two correct refs).
"""

from __future__ import annotations

import unittest

from src.objects.decision_model import CandidateGateAssessment, EvidencePackage

from gate_modules.tgt01_adc_modality_precedent import (
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    NormalizedPrecedentRecord,
    TGT01_EVIDENCE_CEILING,
    Tgt01ModuleInput,
    Tgt01ModuleRunResult,
    run,
)
from gate_modules.tgt01_adc_modality_precedent.contracts import (
    CANONICAL_ONLY_FIELDS,
    SweepCompletionRecord,
)


# --- deterministic fakes ----------------------------------------------------

class FakeAllocator:
    def __init__(self, start: int = 1) -> None:
        self._n = start - 1
        self.calls = 0

    def next_evidence_id(self) -> str:
        self.calls += 1
        self._n += 1
        return f"EP-{self._n:08d}"


class FakeSourceResolver:
    """Auto-registers every record's provenance as canonical unless told to
    treat a source as unresolved or to hand back mismatched metadata."""

    def __init__(
        self,
        records: list[NormalizedPrecedentRecord],
        *,
        unresolved: set[str] | None = None,
        mismatch: set[str] | None = None,
    ) -> None:
        unresolved = unresolved or set()
        mismatch = mismatch or set()
        self._by_id: dict[str, CanonicalSourceRecord] = {}
        for r in records:
            if r.source_id in unresolved:
                continue
            if r.source_id in mismatch:
                self._by_id[r.source_id] = CanonicalSourceRecord(
                    source_id=r.source_id,
                    source_type=r.source_type,
                    source_identifier=r.source_identifier + "-DIFFERENT",
                    locator=r.locator,
                )
            else:
                self._by_id.setdefault(
                    r.source_id,
                    CanonicalSourceRecord(
                        source_id=r.source_id,
                        source_type=r.source_type,
                        source_identifier=r.source_identifier,
                        locator=r.locator,
                    ),
                )

    def resolve(self, source_id: str) -> CanonicalSourceRecord | None:
        return self._by_id.get(source_id)


class FakeEvidenceLibrary:
    """Maps observation_id -> the EXACT canonical EvidencePackage already recorded."""

    def __init__(self, known: dict[str, EvidencePackage] | None = None) -> None:
        self._known = known or {}

    def resolve(self, observation_id: str) -> EvidencePackage | None:
        return self._known.get(observation_id)


def _canonical_ep(
    evidence_id: str,
    *,
    record: NormalizedPrecedentRecord | None = None,
    claim: str | None = None,
    source_id: str = "SRC-00000001",
    candidate_id: str = "CAND-L04-000123",
    drop_ctx_keys: tuple[str, ...] = (),
    **ctx_overrides: object,
) -> EvidencePackage:
    """A minimal valid PR A EvidencePackage standing in for a library entry.

    When ``record`` is given the classification-driving study_context is taken
    from it; ``ctx_overrides`` then simulate a drift between the canonical EP and
    a later provider record for the same observation_id.
    """

    r = record
    ctx: dict[str, object] = {
        "indication": "na", "treatment_state": "na", "sample_type": "na",
        "program_target_identity": r.program_target_identity if r else "TARGET_A",
        "target_relation": r.target_relation if r else "SAME_TARGET",
        "adjacency_basis": r.adjacency_basis if r else "",
        "program_stage": r.program_stage if r else "APPROVED",
        "program_status": r.program_status if r else "ACTIVE",
        "clinical_activity_disclosed": r.clinical_activity_disclosed if r else True,
        "failure_attribution": r.failure_attribution if r else "",
    }
    ctx.update(ctx_overrides)
    for k in drop_ctx_keys:
        ctx.pop(k, None)
    return EvidencePackage(
        evidence_id=evidence_id,
        schema_version=1,
        claim=claim if claim is not None else (r.claim if r else "canonical claim"),
        measurement={"type": "adc_program_fact_observation", "analyte": "TARGET_A",
                     "readout": "APPROVED/ACTIVE", "result": "fact", "unit": ""},
        candidate_refs=(candidate_id,),
        study_context=ctx,
        provenance={
            "source_id": r.source_id if r else source_id,
            "source_type": "REGULATORY",
            "source_identifier": "FDA-BLA-0001",
            "locator": "",
            "retrieved_at": "2025-06-01",
        },
        interpretation_boundary={
            "directly_supports": ("a prior ADC development fact",),
            "does_not_support": ("anything Gate-relative",),
            "limitations": ("observation-level only",),
            "evidence_ceiling": "an ADC development fact for the named antigen",
        },
        derivation={"module_run_id": "RUN-EARLIER", "code_commit": "cafe"},
    )


_SWEEP_OK = SweepCompletionRecord(
    same_target_program_inventory_complete=True,
    failure_reason_sweep_complete=True,
)


def _input(**overrides: object) -> Tgt01ModuleInput:
    base: dict[str, object] = dict(
        candidate_id="CAND-L04-000123",
        candidate_name="TARGET_A",
        target_identity="TARGET_A",
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


_OBS = iter(range(1, 10_000))


def _record(**overrides: object) -> NormalizedPrecedentRecord:
    base: dict[str, object] = dict(
        observation_id=f"OBS-{next(_OBS):04d}",
        program_id="PROGRAM_A",
        program_target_identity="TARGET_A",
        target_relation="SAME_TARGET",
        adjacency_basis="",
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


def _adverse(program_id: str, source_id: str, cls: str, **overrides: object):
    kwargs: dict[str, object] = dict(
        program_id=program_id,
        source_id=source_id,
        source_identifier=f"NCT-{source_id[-4:]}",
        source_type="NCT",
        program_status="DISCONTINUED",
        clinical_activity_disclosed=False,
        failure_reason="disclosed reason",
        failure_attribution=cls,
        failure_attribution_from_primary_source=True,
        claim=f"{program_id} against TARGET_A discontinued ({cls})",
    )
    kwargs.update(overrides)
    return _record(**kwargs)


def _run_parts(records, sweep=_SWEEP_OK, *, unresolved=None, mismatch=None,
               library=None, module_input=None, allocator=None):
    alloc = allocator or FakeAllocator()
    result = run(
        module_input or _input(),
        provider=_Provider(records, sweep),
        evidence_id_allocator=alloc,
        source_resolver=FakeSourceResolver(
            records, unresolved=unresolved, mismatch=mismatch
        ),
        evidence_library=library or FakeEvidenceLibrary(),
    )
    return result, alloc


def _run(*args, **kwargs):
    return _run_parts(*args, **kwargs)[0]


class _Provider:
    def __init__(self, records, sweep):
        self._records = records
        self._sweep = sweep

    def fetch_precedents(self, **_):
        return list(self._records)

    def sweep_completion(self, **_):
        return self._sweep


# --- positive rungs -------------------------------------------------------

class PositiveRungTests(unittest.TestCase):
    def test_direct_positive_from_an_approved_same_target_adc(self) -> None:
        res = _run([_record(program_stage="APPROVED", clinical_activity_disclosed=True)])
        self.assertTrue(res.machine_acceptance.accepted)
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "POSITIVE")
        self.assertEqual(env.proposed_strength, "DIRECT")
        self.assertEqual(len(res.evidence_packages), 1)
        self.assertEqual(
            env.evidence_refs, ((res.evidence_packages[0].evidence_id, "SUPPORTING"),)
        )
        self.assertEqual(env.evidence_ceiling, TGT01_EVIDENCE_CEILING)

    def test_indirect_strong_from_a_phase_1_same_target_adc(self) -> None:
        res = _run([_record(program_stage="PHASE_1", clinical_activity_disclosed=False,
                            source_id="SRC-00000002", source_identifier="NCT-0002",
                            source_type="NCT")])
        self.assertEqual(res.proposal_envelope.proposed_direction, "POSITIVE")
        self.assertEqual(res.proposal_envelope.proposed_strength, "INDIRECT_STRONG")

    def test_weak_from_a_clinical_stage_adjacent_target_adc(self) -> None:
        res = _run([_record(target_relation="ADJACENT_TARGET",
                            program_target_identity="TARGET_B",
                            adjacency_basis="same receptor tyrosine kinase family",
                            program_stage="APPROVED", source_id="SRC-00000003")])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "POSITIVE")
        self.assertEqual(env.proposed_strength, "WEAK")
        self.assertTrue(any("raise the strength" in u for u, _ in env.critical_unknowns))

    def test_strength_never_exceeds_the_strongest_rung_actually_met(self) -> None:
        res = _run([_record(program_stage="PRECLINICAL", clinical_activity_disclosed=False,
                            source_type="DOI", source_identifier="10.x/preclin")])
        self.assertEqual(res.proposal_envelope.proposed_strength, "WEAK")
        checks = dict(res.machine_acceptance.checks)
        self.assertTrue(checks["proposed_strength_within_the_strongest_rung_met"])


# --- UNKNOWN and both frozen fatal branches ----------------------------------

class UnknownAndFatalPatternTests(unittest.TestCase):
    def test_no_admissible_evidence_is_the_unknown_state_not_kill(self) -> None:
        res = _run([])
        env = res.proposal_envelope
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(env.proposed_direction, "INCONCLUSIVE")
        self.assertEqual(env.proposed_strength, "UNKNOWN")
        self.assertEqual(env.evidence_refs, ())

    def test_a_single_target_mediated_failure_is_never_negative(self) -> None:
        res = _run([_adverse("PROGRAM_A", "SRC-00000001", "TARGET_MEDIATED_TOXICITY")])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "INCONCLUSIVE")
        self.assertEqual({r for _, r in env.evidence_refs}, {"CONTEXTUAL"})

    def test_two_consistent_target_mediated_toxicity_failures_are_a_pattern(self) -> None:
        res = _run([
            _adverse("PROGRAM_A", "SRC-00000001", "TARGET_MEDIATED_TOXICITY"),
            _adverse("PROGRAM_B", "SRC-00000002", "TARGET_MEDIATED_TOXICITY"),
        ])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "NEGATIVE")
        self.assertEqual({r for _, r in env.evidence_refs}, {"CONTRADICTING"})

    def test_two_intrinsic_therapeutic_window_failures_are_also_a_pattern(self) -> None:
        res = _run([
            _adverse("PROGRAM_A", "SRC-00000001", "INTRINSIC_THERAPEUTIC_WINDOW"),
            _adverse("PROGRAM_B", "SRC-00000002", "INTRINSIC_THERAPEUTIC_WINDOW"),
        ])
        self.assertEqual(res.proposal_envelope.proposed_direction, "NEGATIVE")

    def test_a_single_intrinsic_therapeutic_window_failure_is_not_fatal(self) -> None:
        res = _run([_adverse("PROGRAM_A", "SRC-00000001", "INTRINSIC_THERAPEUTIC_WINDOW")])
        self.assertEqual(res.proposal_envelope.proposed_direction, "INCONCLUSIVE")

    def test_a_mix_of_different_adverse_classes_is_not_a_consistent_pattern(self) -> None:
        res = _run([
            _adverse("PROGRAM_A", "SRC-00000001", "TARGET_MEDIATED_TOXICITY"),
            _adverse("PROGRAM_B", "SRC-00000002", "INTRINSIC_THERAPEUTIC_WINDOW"),
        ])
        self.assertEqual(res.proposal_envelope.proposed_direction, "INCONCLUSIVE")
        self.assertNotEqual(res.proposal_envelope.proposed_strength, "UNKNOWN")

    def test_construct_specific_failures_are_context_only(self) -> None:
        r1 = _record(program_id="PROGRAM_A", source_id="SRC-00000001",
                     source_type="NCT", source_identifier="NCT-0001",
                     program_status="DISCONTINUED", clinical_activity_disclosed=False,
                     failure_reason="linker instability",
                     failure_attribution="CONSTRUCT_SPECIFIC",
                     claim="PROGRAM_A halted for a linker reason")
        r2 = _record(program_id="PROGRAM_B", source_id="SRC-00000002",
                     source_type="NCT", source_identifier="NCT-0002",
                     program_status="DISCONTINUED", clinical_activity_disclosed=False,
                     failure_reason="manufacturing",
                     failure_attribution="CONSTRUCT_SPECIFIC",
                     claim="PROGRAM_B halted for a manufacturing reason")
        res = _run([r1, r2])
        self.assertEqual(res.proposal_envelope.proposed_direction, "INCONCLUSIVE")

    def test_positive_precedent_plus_consistent_adverse_pattern_is_conflicting(self) -> None:
        good = _record(program_id="PROGRAM_C", program_stage="APPROVED",
                       clinical_activity_disclosed=True, source_id="SRC-00000003",
                       claim="Approved same-target ADC with disclosed activity")
        res = _run([
            good,
            _adverse("PROGRAM_A", "SRC-00000001", "TARGET_MEDIATED_TOXICITY"),
            _adverse("PROGRAM_B", "SRC-00000002", "TARGET_MEDIATED_TOXICITY"),
        ])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "CONFLICTING")
        roles = {r for _, r in env.evidence_refs}
        self.assertIn("SUPPORTING", roles)
        self.assertIn("CONTRADICTING", roles)


# --- candidate <-> target identity binding (blocker 1) ---------------------

class TargetIdentityBindingTests(unittest.TestCase):
    def test_same_target_record_for_a_different_antigen_rejects_the_run(self) -> None:
        # a candidate <-> program antigen misbinding is a HARD integrity failure:
        # E1 item 13 on_failure -> the run is rejected, never an accepted UNKNOWN.
        res = _run([_record(target_relation="SAME_TARGET",
                            program_target_identity="TROP2")])
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(any("misbinding" in why for _, why in res.hard_integrity_failures))

    def test_adjacent_evidence_package_recovers_the_actual_antigen_and_basis(self) -> None:
        res = _run([_record(target_relation="ADJACENT_TARGET",
                            program_target_identity="TARGET_B",
                            adjacency_basis="paralogue in the same lineage",
                            program_stage="PHASE_2", source_id="SRC-00000004")])
        ctx = res.evidence_packages[0].study_context
        self.assertEqual(ctx["program_target_identity"], "TARGET_B")
        self.assertEqual(ctx["target_relation"], "ADJACENT_TARGET")
        self.assertEqual(ctx["adjacency_basis"], "paralogue in the same lineage")

    def test_run_takes_no_separate_drift_prone_target_argument(self) -> None:
        import inspect

        sig = inspect.signature(run)
        self.assertNotIn("target_identity", sig.parameters)


# --- one package per observation (blocker 4) ------------------------------

class ObservationIdentityTests(unittest.TestCase):
    def test_one_program_two_observations_yield_two_correct_packages(self) -> None:
        label = _record(program_id="PROGRAM_A", observation_id="OBS-LABEL",
                        source_id="SRC-00000001", source_type="REGULATORY",
                        source_identifier="FDA-BLA-0001",
                        claim="PROGRAM_A: approval with disclosed ORR")
        pub = _record(program_id="PROGRAM_A", observation_id="OBS-PUB",
                      source_id="SRC-00000002", source_type="PMID",
                      source_identifier="PMID-999",
                      claim="PROGRAM_A: peer-reviewed activity write-up")
        res = _run([label, pub])
        self.assertEqual(len(res.evidence_packages), 2)
        ref_ids = sorted(e for e, _ in res.proposal_envelope.evidence_refs)
        self.assertEqual(ref_ids, sorted(ep.evidence_id for ep in res.evidence_packages))

    def test_one_program_two_target_mediated_observations_count_as_one_program(self) -> None:
        a1 = _adverse("PROGRAM_A", "SRC-00000001", "TARGET_MEDIATED_TOXICITY",
                      observation_id="OBS-A1")
        a2 = _adverse("PROGRAM_A", "SRC-00000002", "TARGET_MEDIATED_TOXICITY",
                      observation_id="OBS-A2",
                      claim="PROGRAM_A second disclosure of the same on-target toxicity")
        res = _run([a1, a2])
        # two EPs, but only ONE independent program -> no pattern -> INCONCLUSIVE
        self.assertEqual(len(res.evidence_packages), 2)
        self.assertEqual(res.proposal_envelope.proposed_direction, "INCONCLUSIVE")

    def test_same_program_duplicate_source_and_claim_is_cleanly_dropped(self) -> None:
        one = _record(program_id="PROGRAM_A", observation_id="OBS-1",
                      source_id="SRC-00000001", claim="Identical observation")
        two = _record(program_id="PROGRAM_A", observation_id="OBS-2",
                      source_id="SRC-00000001", claim="Identical observation")
        res = _run([one, two])
        self.assertEqual(len(res.evidence_packages), 1)
        self.assertTrue(any("duplicate" in why for _, why in res.rejected_records))
        self.assertTrue(res.machine_acceptance.accepted)


# --- Gate-neutral EP + reuse + provenance (blocker 3) --------------------

class GateNeutralEvidenceTests(unittest.TestCase):
    def test_package_is_gate_neutral(self) -> None:
        ep = _run([_record()]).evidence_packages[0]
        ib = ep.interpretation_boundary
        joined = " ".join(
            list(ib["directly_supports"])
            + list(ib["does_not_support"])
            + list(ib["limitations"])
            + [ib["evidence_ceiling"]]
        )
        self.assertNotIn("ADC-modality feasibility", joined)
        self.assertNotIn(TGT01_EVIDENCE_CEILING, joined)
        # the TGT-01 ceiling lives only on the proposal layer
        env = _run([_record()]).proposal_envelope
        self.assertEqual(env.evidence_ceiling, TGT01_EVIDENCE_CEILING)

    def test_an_existing_library_package_is_reused_unchanged_not_reconstructed(self) -> None:
        rec = _record(observation_id="OBS-REUSE", source_id="SRC-00000001",
                      claim="the canonical observation claim")
        canonical = _canonical_ep("EP-00007777", record=rec)
        res, alloc = _run_parts(
            [rec], library=FakeEvidenceLibrary({"OBS-REUSE": canonical})
        )
        self.assertEqual(alloc.calls, 0)  # allocator NOT called for a reused observation
        self.assertEqual(res.evidence_packages, ())  # no re-created body
        self.assertEqual(res.reused_evidence_ids, ("EP-00007777",))
        self.assertIn(
            "EP-00007777", [e for e, _ in res.proposal_envelope.evidence_refs]
        )

    def test_incompatible_canonical_ep_is_a_hard_integrity_failure(self) -> None:
        rec = _record(observation_id="OBS-BAD", claim="observation claim A")
        wrong = _canonical_ep("EP-00007777", claim="a completely different claim")
        res = _run([rec], library=FakeEvidenceLibrary({"OBS-BAD": wrong}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("incompatible canonical" in why for _, why in res.hard_integrity_failures)
        )

    def test_a_canonical_ep_missing_a_classification_driving_field_rejects_the_run(self) -> None:
        # a canonical EP predating the full study_context cannot be parity-checked
        rec = _record(observation_id="OBS-MISS")
        canonical = _canonical_ep(
            "EP-00007777", record=rec, drop_ctx_keys=("clinical_activity_disclosed",)
        )
        res = _run([rec], library=FakeEvidenceLibrary({"OBS-MISS": canonical}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("missing the classification-driving field" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_a_classification_driving_drift_from_the_canonical_ep_rejects_the_run(self) -> None:
        # same observation_id / source_id / claim / candidate, but the current
        # provider record drifted on a field that drives TGT-01 classification.
        for rec, drift, never in (
            # PHASE_1 canonical, APPROVED now -> must not become DIRECT
            (_record(observation_id="OBS-D1", program_stage="PHASE_1",
                     clinical_activity_disclosed=False),
             _record(observation_id="OBS-D1", program_stage="APPROVED",
                     clinical_activity_disclosed=True),
             "DIRECT"),
            # SAME_TARGET/TARGET_A canonical, ADJACENT/TARGET_B now
            (_record(observation_id="OBS-D2"),
             _record(observation_id="OBS-D2", target_relation="ADJACENT_TARGET",
                     program_target_identity="TARGET_B",
                     adjacency_basis="paralogue"),
             None),
            # non-target/construct-specific canonical, TARGET_MEDIATED_TOXICITY now
            (_record(observation_id="OBS-D3", program_status="DISCONTINUED",
                     clinical_activity_disclosed=False, source_type="NCT",
                     source_identifier="NCT-0001", claim="the discontinuation was disclosed",
                     failure_reason="linker", failure_attribution="CONSTRUCT_SPECIFIC"),
             _record(observation_id="OBS-D3", program_status="DISCONTINUED",
                     clinical_activity_disclosed=False, source_type="NCT",
                     source_identifier="NCT-0001", claim="the discontinuation was disclosed",
                     failure_reason="on-target tox",
                     failure_attribution="TARGET_MEDIATED_TOXICITY",
                     failure_attribution_from_primary_source=True),
             "NEGATIVE"),
        ):
            with self.subTest(drift=drift.observation_id):
                canonical = _canonical_ep("EP-00007777", record=rec)
                res = _run([drift],
                           library=FakeEvidenceLibrary({drift.observation_id: canonical}))
                self.assertFalse(res.machine_acceptance.accepted)
                self.assertIsNone(res.proposal_envelope)
                self.assertTrue(
                    any("classification-driving drift" in why
                        for _, why in res.hard_integrity_failures)
                )

    def test_canonical_source_metadata_mismatch_rejects_the_run(self) -> None:
        res = _run([_record(source_id="SRC-00000009")], mismatch={"SRC-00000009"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("disagrees with the canonical" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_claimed_resolved_source_missing_from_the_index_rejects_the_run(self) -> None:
        res = _run([_record(source_id="SRC-00000009")], unresolved={"SRC-00000009"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("not in the canonical SourceIndex" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_unresolved_adcdb_only_lead_is_a_soft_drop_not_a_run_failure(self) -> None:
        lead = _record(primary_source_resolved=False,
                       claim="ADCdb inventory row, not yet resolved to a primary source")
        res = _run([lead])
        self.assertEqual(len(res.evidence_packages), 0)
        self.assertEqual(res.hard_integrity_failures, ())
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(res.proposal_envelope.proposed_strength, "UNKNOWN")
        self.assertTrue(
            any("unresolved primary source" in why for _, why in res.rejected_records)
        )


# --- stop-rule prerequisite (E2-6) --------------------------------------

class StopRuleTests(unittest.TestCase):
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

    def test_a_direct_positive_does_not_bypass_the_sweep_prerequisite(self) -> None:
        res = _run([_record(program_stage="APPROVED", clinical_activity_disclosed=True)],
                   sweep=SweepCompletionRecord(True, False))
        self.assertFalse(res.machine_acceptance.accepted)


# --- input contract ----------------------------------------------------

class InputContractTests(unittest.TestCase):
    def test_no_implicit_default_scientific_context(self) -> None:
        for bad in (
            dict(gate_id="TGT-02"),
            dict(gateset_id="SOME_OTHER_GATESET"),
            dict(evidence_regime="PUBLIC_PLUS_EXPERIMENTAL"),
            dict(instantiation_id="INST-OTHER-v1"),
            dict(candidate_id="CAND-L03-000001"),
            dict(target_identity=""),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    _input(**bad)

    def test_target_mediated_attribution_requires_a_primary_source_disclosure(self) -> None:
        with self.assertRaises(ValueError):
            _record(
                program_status="DISCONTINUED",
                failure_attribution="TARGET_MEDIATED_TOXICITY",
                failure_attribution_from_primary_source=False,
            )

    def test_adjacent_record_requires_an_auditable_basis(self) -> None:
        with self.assertRaises(ValueError):
            _record(target_relation="ADJACENT_TARGET",
                    program_target_identity="TARGET_B", adjacency_basis="")


# --- proposal / canonical boundary -----------------------------------------

class ProposalEnvelopeBoundaryTests(unittest.TestCase):
    def test_envelope_carries_every_identity_pin(self) -> None:
        env = _run([_record()]).proposal_envelope
        for pin in (
            "candidate_id", "instantiation_id", "context_id", "context_version",
            "gateset_id", "gateset_version", "gate_id", "gate_version",
        ):
            self.assertIn(pin, AssessmentProposalEnvelope.field_names())
            self.assertNotIn(getattr(env, pin), (None, ""))

    def test_envelope_carries_no_canonical_assessment_id_version_or_review(self) -> None:
        names = set(AssessmentProposalEnvelope.field_names())
        for forbidden in CANONICAL_ONLY_FIELDS:
            self.assertNotIn(forbidden, names)

    def test_module_builds_no_canonical_assessment_or_decision(self) -> None:
        res = _run([_record()])
        self.assertIsInstance(res, Tgt01ModuleRunResult)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertNotIsInstance(res.proposal_envelope, CandidateGateAssessment)
        self.assertTrue(
            all(isinstance(ep, EvidencePackage) for ep in res.evidence_packages)
        )
        for attr in ("decision", "assessment", "candidate_gate_assessment", "kill"):
            self.assertFalse(hasattr(res, attr))


if __name__ == "__main__":
    unittest.main()
