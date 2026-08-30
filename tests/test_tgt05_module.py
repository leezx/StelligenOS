"""Runtime Migration PR E4: MOD-TGT05 deterministic scientific core.

Synthetic, in-memory only -- no network, no real atlas / clinical data, no
persistence. The candidate target is ``TARGET_A``; programs are ``PROGRAM_A`` /
``PROGRAM_B``; the vital organ is ``HEPATIC`` (affected tissue ``LIVER``); the
toxicity phenotype key is ``PHENO_X``.

Covers the E4-8 acceptance scenarios: the frozen E3 item-06 truth table
(DIRECT / INDIRECT_STRONG positives, RNA-only / rodent-only -> WEAK, a validated
protein NOT_DETECTED -> coverage context and never NEGATIVE, no admissible
evidence -> UNKNOWN and never auto-PASS); positive precedence over coverage
gaps; CONFLICTING per liability_event_id (and "ADC-B reports no toxicity" never
a conflict); the machine-local fatal_review review TRIGGER (>= 2 distinct
same-target ADC programs on an exact tissue + phenotype key -> POTENTIAL pattern;
same program twice / different tissue -> no pattern; never
PUBLIC_FATAL_SIGNAL_ESTABLISHED; never on the proposal envelope); the E4-6
path-based stop-rule prerequisites; exact canonical EvidencePackage reuse and
the HARD identity / provenance integrity gate; and the TGT-05 binding
reconciliation with MIGRATION_PENDING still in force.
"""

from __future__ import annotations

import inspect
import re
import unittest
from pathlib import Path

import yaml

from src.objects.crc_adc_target_gateset import BUILT_MODULE_VERSIONS
from src.objects.decision_model import CandidateGateAssessment, EvidencePackage

from gate_modules.tgt05_normal_tissue_fatal_liability import (
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    NormalizedLiabilityRecord,
    TGT05_EVIDENCE_CEILING,
    Tgt05ModuleInput,
    Tgt05ModuleRunResult,
    VITAL_ORGAN_CLASSES,
    run,
)
from gate_modules.tgt05_normal_tissue_fatal_liability.contracts import (
    CANONICAL_ONLY_FIELDS,
    FATAL_REVIEW_STATUS_VALUES,
    Tgt05SweepCompletionRecord,
    VitalOrganCoverageState,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "gate_modules" / "tgt05_normal_tissue_fatal_liability"


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
    def __init__(
        self,
        records: list[NormalizedLiabilityRecord],
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
            ident = r.source_identifier + ("-DIFFERENT" if r.source_id in mismatch else "")
            self._by_id.setdefault(
                r.source_id,
                CanonicalSourceRecord(
                    source_id=r.source_id,
                    source_type=r.source_type,
                    source_identifier=ident,
                    locator=r.locator,
                ),
            )

    def resolve(self, source_id: str) -> CanonicalSourceRecord | None:
        return self._by_id.get(source_id)


class FakeEvidenceLibrary:
    def __init__(self, known: dict[str, EvidencePackage] | None = None) -> None:
        self._known = known or {}

    def resolve(self, observation_id: str) -> EvidencePackage | None:
        return self._known.get(observation_id)


class _Provider:
    def __init__(self, records, sweep):
        self._records = records
        self._sweep = sweep

    def fetch_liability_records(self, **_):
        return list(self._records)

    def sweep_completion(self, **_):
        return self._sweep


# --- factories -----------------------------------------------------------

def _coverage(**over) -> dict:
    # default: every vital-organ protein search is complete and found nothing
    # admissible -- consistent with a run that emits no human-protein
    # EvidencePackage, and enough to satisfy Path C completion.
    base = {
        o: VitalOrganCoverageState(True, "PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA")
        for o in VITAL_ORGAN_CLASSES
    }
    base.update(over)
    return base


_FOUND = VitalOrganCoverageState(True, "ADMISSIBLE_PROTEIN_DATA_FOUND")
_NOT_YET = VitalOrganCoverageState(False, "NOT_YET_COMPLETE")


def _covered(*organs: str) -> dict:
    """Coverage map where the named organs have admissible protein data (backed
    by an emitted human-protein EP) and the rest are exhausted."""

    return _coverage(**{o: _FOUND for o in organs})


def _sweep(**over) -> Tgt05SweepCompletionRecord:
    base = dict(
        same_target_adc_construct_inventory_complete=True,
        adc_toxicity_attribution_sweep_complete=True,
        non_adc_same_target_toxicity_sweep_complete=True,
        nhp_sweep_complete=True,
        rna_supporting_sweep_complete=True,
        vital_organ_protein_coverage=_coverage(),
    )
    base.update(over)
    return Tgt05SweepCompletionRecord(**base)


def _input(**over) -> Tgt05ModuleInput:
    base: dict[str, object] = dict(
        candidate_id="CAND-L04-000123",
        candidate_name="TARGET_A candidate",
        target_identity="TARGET_A",
        instantiation_id="INST-CRC-REFRACTORY-ADC-TARGET-v1",
        context_id="CTX-CRC-REFRACTORY-ADC",
        context_version=1,
        gateset_id="ADC_TARGET_GATESET",
        gateset_version="1.0",
        gate_id="TGT-05",
        gate_version="1.0",
        evidence_regime="PUBLIC_ONLY",
        run_id="RUN-TEST",
        code_commit="0" * 12,
    )
    base.update(over)
    return Tgt05ModuleInput(**base)  # type: ignore[arg-type]


_OBS = iter(range(1, 100_000))


def _adc(**over) -> NormalizedLiabilityRecord:
    n = next(_OBS)
    base: dict[str, object] = dict(
        observation_id=f"OBS-{n:05d}",
        liability_event_id="EVT-1",
        evidence_function="LIABILITY_RUNG_EVIDENCE",
        target_identity="TARGET_A",
        observation_kind="ADC_CLINICAL_TOXICITY",
        claim=f"an ADC against TARGET_A reported on-target hepatotoxicity ({n})",
        source_id="SRC-00000001",
        source_type="NCT",
        source_identifier="NCT-0001",
        locator="",
        retrieved_at="2026-02-01",
        primary_source_resolved=True,
        modality="ADC",
        program_id="PROGRAM_A",
        construct_fingerprint="FP-A",
        affected_tissue="LIVER",
        toxicity_phenotype_raw="hepatocellular injury",
        toxicity_phenotype_key="PHENO_X",
        observed_severity="grade 3",
        target_attribution_stance="SUPPORTS_TARGET_ATTRIBUTION",
        target_attribution_basis="label attributes the event to on-target hepatocyte expression",
    )
    base.update(over)
    return NormalizedLiabilityRecord(**base)  # type: ignore[arg-type]


def _non_adc(**over) -> NormalizedLiabilityRecord:
    return _adc(
        observation_kind="NON_ADC_CLINICAL_TOXICITY",
        modality="CAR-T",
        claim=over.pop(
            "claim",
            "a same-target CAR-T reported on-target hepatotoxicity attributed to "
            "the antigen",
        ),
        **over,
    )


def _attr(**over) -> NormalizedLiabilityRecord:
    return _adc(
        evidence_function="ATTRIBUTION_ADJUDICATION",
        target_attribution_stance=over.pop(
            "target_attribution_stance", "REFUTES_TARGET_ATTRIBUTION"
        ),
        claim=over.pop(
            "claim", "a re-analysis attributes the event to the payload, not the target"
        ),
        **over,
    )


def _expr(**over) -> NormalizedLiabilityRecord:
    n = next(_OBS)
    base: dict[str, object] = dict(
        observation_id=f"OBS-{n:05d}",
        liability_event_id=f"EVT-EXPR-{n}",
        evidence_function="LIABILITY_RUNG_EVIDENCE",
        target_identity="TARGET_A",
        observation_kind="HUMAN_NORMAL_EXPRESSION",
        claim=f"a human normal-tissue atlas reports TARGET_A in vital tissue ({n})",
        source_id="SRC-00000002",
        source_type="DATASET",
        source_identifier="HPA-0001",
        locator="",
        retrieved_at="2026-02-02",
        primary_source_resolved=True,
        species="human",
        molecular_layer="PROTEIN",
        finding="DETECTED",
        atlas_validated=True,
        vital_organ_class="HEPATIC",
        affected_tissue="LIVER",
        cell_compartment="hepatocyte",
    )
    base.update(over)
    return NormalizedLiabilityRecord(**base)  # type: ignore[arg-type]


def _coverage_rec(**over) -> NormalizedLiabilityRecord:
    return _expr(
        evidence_function="COVERAGE_CONTEXT",
        finding="NOT_DETECTED",
        claim=over.pop(
            "claim", "a validated human protein atlas reports NO TARGET_A protein here"
        ),
        **over,
    )


def _nhp(**over) -> NormalizedLiabilityRecord:
    n = next(_OBS)
    base: dict[str, object] = dict(
        observation_id=f"OBS-{n:05d}",
        liability_event_id=f"EVT-NHP-{n}",
        evidence_function="LIABILITY_RUNG_EVIDENCE",
        target_identity="TARGET_A",
        observation_kind="NHP_TOXICITY",
        claim=f"a same-target agent caused on-target NHP toxicity ({n})",
        source_id="SRC-00000003",
        source_type="DOI",
        source_identifier="10.x/nhp",
        locator="",
        retrieved_at="2026-02-03",
        primary_source_resolved=True,
        species="cynomolgus",
        affected_tissue="LIVER",
        toxicity_phenotype_key="PHENO_X",
        translational_relevance=True,
        target_attribution_stance="SUPPORTS_TARGET_ATTRIBUTION",
        target_attribution_basis="NHP histopathology localises the injury to "
        "target-expressing hepatocytes",
    )
    base.update(over)
    return NormalizedLiabilityRecord(**base)  # type: ignore[arg-type]


def _rodent(**over) -> NormalizedLiabilityRecord:
    n = next(_OBS)
    base: dict[str, object] = dict(
        observation_id=f"OBS-{n:05d}",
        liability_event_id=f"EVT-ROD-{n}",
        evidence_function="LIABILITY_RUNG_EVIDENCE",
        target_identity="TARGET_A",
        observation_kind="RODENT_NORMAL_OR_TOXICITY",
        claim=f"a rodent study reports TARGET_A in normal tissue ({n})",
        source_id="SRC-00000004",
        source_type="DOI",
        source_identifier="10.x/rodent",
        locator="",
        retrieved_at="2026-02-04",
        primary_source_resolved=True,
        species="mouse",
        molecular_layer="PROTEIN",
        finding="DETECTED",
        affected_tissue="LIVER",
    )
    base.update(over)
    return NormalizedLiabilityRecord(**base)  # type: ignore[arg-type]


def _canonical_ep(evidence_id: str, record: NormalizedLiabilityRecord,
                  *, candidate_id: str = "CAND-L04-000123", **ctx_over) -> EvidencePackage:
    r = record
    ctx: dict[str, object] = {
        "indication": "not_applicable_target_level_liability_fact",
        "treatment_state": "not_applicable",
        "sample_type": "not_applicable",
        "observation_id": r.observation_id,
        "liability_event_id": r.liability_event_id,
        "evidence_function": r.evidence_function,
        "target_identity": r.target_identity,
        "observation_kind": r.observation_kind,
        "species": r.species,
        "modality": r.modality,
        "molecular_layer": r.molecular_layer,
        "finding": r.finding,
        "atlas_validated": r.atlas_validated,
        "vital_organ_class": r.vital_organ_class,
        "affected_tissue": r.affected_tissue,
        "cell_compartment": r.cell_compartment,
        "program_id": r.program_id,
        "construct_fingerprint": r.construct_fingerprint,
        "toxicity_phenotype_key": r.toxicity_phenotype_key,
        "observed_severity": r.observed_severity,
        "target_attribution_stance": r.target_attribution_stance,
        "target_attribution_basis": r.target_attribution_basis,
        "translational_relevance": r.translational_relevance,
    }
    ctx.update(ctx_over)
    return EvidencePackage(
        evidence_id=evidence_id,
        schema_version=1,
        claim=r.claim,
        measurement={"type": "adc_target_normal_tissue_liability_observation",
                     "analyte": r.target_identity, "readout": "x/y",
                     "result": "a prior observation-level fact", "unit": ""},
        candidate_refs=(candidate_id,),
        study_context=ctx,
        provenance={"source_id": r.source_id, "source_type": r.source_type,
                    "source_identifier": r.source_identifier, "locator": r.locator,
                    "retrieved_at": r.retrieved_at},
        interpretation_boundary={
            "directly_supports": ("a prior normal-tissue observation-level fact",),
            "does_not_support": ("the absence of a normal-tissue on-target liability",
                                 "normal-tissue safety",
                                 "a product-specific therapeutic window"),
            "limitations": ("a single observation; no Gate-relative grade",),
            "evidence_ceiling": "an observation-level fact for the named target",
        },
        derivation={"module_run_id": "RUN-EARLIER", "code_commit": "cafe"},
    )


def _default_sweep_for(records) -> Tgt05SweepCompletionRecord:
    """A fully-complete sweep whose per-organ coverage_result is consistent with
    the human-protein observations in ``records`` (organs with a validated
    protein observation report ADMISSIBLE_PROTEIN_DATA_FOUND, the rest exhausted).
    """

    covered = sorted(
        r.vital_organ_class
        for r in records
        if r.observation_kind == "HUMAN_NORMAL_EXPRESSION"
        and r.molecular_layer == "PROTEIN"
        and r.atlas_validated
        and r.finding in ("DETECTED", "NOT_DETECTED")
        and r.vital_organ_class
    )
    return _sweep(vital_organ_protein_coverage=_covered(*covered))


def _run_parts(records, sweep=None, *, unresolved=None, mismatch=None,
               library=None, module_input=None, allocator=None):
    alloc = allocator or FakeAllocator()
    result = run(
        module_input or _input(),
        provider=_Provider(records, sweep or _default_sweep_for(records)),
        evidence_id_allocator=alloc,
        source_resolver=FakeSourceResolver(records, unresolved=unresolved, mismatch=mismatch),
        evidence_library=library or FakeEvidenceLibrary(),
    )
    return result, alloc


def _run(*a, **kw):
    return _run_parts(*a, **kw)[0]


# --- frozen E3 item-06 truth table -------------------------------------------

class TruthTableTests(unittest.TestCase):
    def test_direct_positive_from_a_supported_adc_clinical_toxicity(self):
        res = _run([_adc()])
        self.assertTrue(res.machine_acceptance.accepted)
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("POSITIVE", "DIRECT"))
        self.assertEqual(env.evidence_ceiling, TGT05_EVIDENCE_CEILING)
        self.assertEqual({r for _, r in env.evidence_refs}, {"SUPPORTING"})

    def test_indirect_strong_from_a_validated_human_protein_atlas(self):
        res = _run([_expr()])
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("POSITIVE", "INDIRECT_STRONG"))

    def test_indirect_strong_from_translationally_relevant_nhp_toxicity(self):
        res = _run([_nhp(translational_relevance=True)])
        self.assertEqual(res.proposal_envelope.proposed_strength, "INDIRECT_STRONG")

    def test_nhp_without_translational_relevance_is_not_a_rung(self):
        res = _run([_nhp(translational_relevance=False)])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_strength, "UNKNOWN")
        self.assertTrue(any("no frozen TGT-05" in why for _, why in res.rejected_records))
        self.assertTrue(res.machine_acceptance.accepted)

    def test_rna_only_atlas_is_weak(self):
        res = _run([_expr(molecular_layer="RNA", atlas_validated=False)])
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("INCONCLUSIVE", "WEAK"))

    def test_rodent_only_data_is_weak(self):
        res = _run([_rodent()])
        self.assertEqual(res.proposal_envelope.proposed_strength, "WEAK")

    def test_no_admissible_evidence_is_unknown_never_auto_pass_never_negative(self):
        res = _run([])
        env = res.proposal_envelope
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(env.evidence_refs, ())
        self.assertNotEqual(env.proposed_direction, "NEGATIVE")

    def test_validated_protein_not_detected_is_coverage_context_not_a_rung(self):
        res = _run([_coverage_rec(vital_organ_class="HEPATIC")])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_strength, "UNKNOWN")
        self.assertNotEqual(env.proposed_direction, "NEGATIVE")
        self.assertEqual(len(res.evidence_packages), 1)  # coverage IS an EP
        organ_ids = dict(res.coverage_map.supporting_evidence_ids)
        self.assertEqual(len(organ_ids["HEPATIC"]), 1)

    def test_every_accepted_pair_is_a_frozen_truth_table_output(self):
        for recs in ([_adc()], [_expr()], [_rodent()], [], [_coverage_rec()]):
            res = _run(recs)
            checks = dict(res.machine_acceptance.checks)
            self.assertTrue(
                checks["proposed_direction_strength_is_a_frozen_truth_table_output"]
            )


# --- admissibility boundary == frozen ladder (review round 1, blocker 1) ----

class AdmissibilityBoundaryTests(unittest.TestCase):
    def test_nhp_translational_without_supported_target_attribution_is_not_a_rung(self):
        rec = _nhp(translational_relevance=True,
                   target_attribution_stance="UNRESOLVED",
                   target_attribution_basis="")
        res = _run([rec])
        self.assertEqual(res.proposal_envelope.proposed_strength, "UNKNOWN")
        self.assertTrue(
            any("NHP" in why or "on-target" in why for _, why in res.rejected_records)
        )
        self.assertTrue(res.machine_acceptance.accepted)

    def test_nhp_translational_with_supported_on_target_attribution_is_indirect_strong(self):
        res = _run([_nhp(translational_relevance=True)])  # default carries SUPPORTS + basis
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("POSITIVE", "INDIRECT_STRONG"))

    def test_non_adc_clinical_without_construct_fingerprint_is_still_indirect_strong(self):
        rec = _non_adc(construct_fingerprint="", toxicity_phenotype_key="")
        res = _run([rec])
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("POSITIVE", "INDIRECT_STRONG"))
        self.assertFalse(res.fatal_review.required)

    def test_adc_direct_without_phenotype_key_is_still_direct_but_not_a_fatal_candidate(self):
        a = _adc(program_id="PROGRAM_A", source_id="SRC-00000001",
                 construct_fingerprint="FP-A", toxicity_phenotype_key="")
        b = _adc(program_id="PROGRAM_B", source_id="SRC-00000002",
                 source_identifier="NCT-0002", construct_fingerprint="FP-B",
                 toxicity_phenotype_key="", claim="PROGRAM_B on-target hepatotox")
        res = _run([a, b])
        self.assertEqual(res.proposal_envelope.proposed_strength, "DIRECT")
        # no normalized phenotype key -> the machine cannot assert convergence
        self.assertFalse(res.fatal_review.required)

    def test_attribution_adjudication_from_a_non_clinical_observation_is_rejected(self):
        rec = _expr(evidence_function="ATTRIBUTION_ADJUDICATION",
                    target_attribution_stance="REFUTES_TARGET_ATTRIBUTION",
                    liability_event_id="EVT-1")
        # the atlas record is SOFT-dropped, so it never becomes a protein EP;
        # the sweep must not claim admissible protein data for HEPATIC.
        res = _run([_adc(liability_event_id="EVT-1"), rec], sweep=_sweep())
        # the atlas record cannot enter the attribution machinery; the ADC
        # liability stands undisputed.
        self.assertEqual(res.proposal_envelope.proposed_direction, "POSITIVE")
        self.assertTrue(
            any("adjudicates a clinical toxicity" in why
                for _, why in res.rejected_records)
        )


# --- positive precedence over coverage gaps --------------------------------

class PositivePrecedenceTests(unittest.TestCase):
    def test_direct_liability_plus_an_uncovered_organ_stays_positive(self):
        sweep = _sweep(vital_organ_protein_coverage=_coverage(
            CNS=VitalOrganCoverageState(False, "NOT_YET_COMPLETE")
        ))
        res = _run([_adc()], sweep=sweep)
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("POSITIVE", "DIRECT"))
        self.assertTrue(any("CNS" in u for u, _ in env.critical_unknowns))

    def test_no_liability_completed_sweeps_exhausted_coverage_is_experiment_required(self):
        sweep = _sweep(vital_organ_protein_coverage=_coverage(
            CNS=VitalOrganCoverageState(
                True, "PUBLIC_SEARCH_EXHAUSTED_NO_ADMISSIBLE_PROTEIN_DATA"
            )
        ))
        res = _run([], sweep=sweep)
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("INCONCLUSIVE", "UNKNOWN"))
        self.assertTrue(
            any(r == "EXPERIMENT_REQUIRED" and "CNS" in u
                for u, r in env.critical_unknowns)
        )


# --- CONFLICTING per liability_event_id (E4-4) ----------------------------

class ConflictingTests(unittest.TestCase):
    def test_same_event_support_and_refute_with_no_independent_liability_is_conflicting(self):
        res = _run([
            _adc(liability_event_id="EVT-1", source_id="SRC-00000001"),
            _attr(liability_event_id="EVT-1", source_id="SRC-00000009",
                  source_identifier="PMID-9"),
        ])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "CONFLICTING")
        roles = {r for _, r in env.evidence_refs}
        self.assertIn("SUPPORTING", roles)
        self.assertIn("CONTRADICTING", roles)

    def test_disputed_event_plus_independent_indirect_strong_is_positive(self):
        res = _run([
            _adc(liability_event_id="EVT-1", source_id="SRC-00000001"),
            _attr(liability_event_id="EVT-1", source_id="SRC-00000009",
                  source_identifier="PMID-9"),
            _expr(),  # independent, undisputed INDIRECT_STRONG
        ])
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("POSITIVE", "INDIRECT_STRONG"))
        self.assertTrue(any("EVT-1" in u for u, _ in env.critical_unknowns))
        # role is relative to the POSITIVE assessment: the disputed event's
        # refutation is CONTEXTUAL here, never CONTRADICTING.
        self.assertNotIn("CONTRADICTING", {r for _, r in env.evidence_refs})

    def test_conflicting_does_not_taint_an_unrelated_attribution_record(self):
        # EVT-1 is a legitimate conflict; EVT-2's refutation is unrelated (no
        # rung on EVT-2) and must be CONTEXTUAL, not CONTRADICTING (E4-4).
        a = _adc(liability_event_id="EVT-1", source_id="SRC-00000001")
        refute1 = _attr(liability_event_id="EVT-1", source_id="SRC-00000009",
                        source_identifier="PMID-9")
        refute2 = _attr(liability_event_id="EVT-2", source_id="SRC-00000010",
                        source_identifier="PMID-10",
                        claim="an unrelated re-analysis of a different program")
        res = _run([a, refute1, refute2])
        env = res.proposal_envelope
        self.assertEqual(env.proposed_direction, "CONFLICTING")
        by_id = {e: r for e, r in env.evidence_refs}
        contradicting = [e for e, r in env.evidence_refs if r == "CONTRADICTING"]
        # exactly one CONTRADICTING ref -- the EVT-1 refutation
        self.assertEqual(len(contradicting), 1)

    def test_adc_b_reports_no_toxicity_is_never_a_conflict_or_contradicting(self):
        res = _run([
            _adc(liability_event_id="EVT-1", source_id="SRC-00000001"),
            _attr(liability_event_id="EVT-2", source_id="SRC-00000009",
                  source_identifier="PMID-9",
                  claim="a different ADC against TARGET_A reported no on-target toxicity"),
        ])
        env = res.proposal_envelope
        self.assertEqual((env.proposed_direction, env.proposed_strength),
                         ("POSITIVE", "DIRECT"))
        self.assertNotIn("CONTRADICTING", {r for _, r in env.evidence_refs})


# --- fatal_review: a machine review TRIGGER, not a conclusion (E4-5) --------

class FatalReviewTests(unittest.TestCase):
    def _two_programs(self, **b_over):
        a = _adc(program_id="PROGRAM_A", source_id="SRC-00000001",
                 construct_fingerprint="FP-A", claim="PROGRAM_A on-target hepatotox")
        b = _adc(program_id="PROGRAM_B", source_id="SRC-00000002",
                 source_identifier="NCT-0002", construct_fingerprint="FP-B",
                 claim="PROGRAM_B on-target hepatotox", **b_over)
        return [a, b]

    def test_single_direct_liability_does_not_require_fatal_review(self):
        res = _run([_adc()])
        self.assertFalse(res.fatal_review.required)
        self.assertEqual(res.fatal_review.status, "")

    def test_two_distinct_programs_same_tissue_and_phenotype_is_a_potential_pattern(self):
        res = _run(self._two_programs())
        fr = res.fatal_review
        self.assertTrue(fr.required)
        self.assertEqual(fr.status, "POTENTIAL_FATAL_PATTERN")
        self.assertEqual(set(fr.program_ids), {"PROGRAM_A", "PROGRAM_B"})
        self.assertIn("LIVER", fr.affected_tissues)
        self.assertTrue(res.machine_acceptance.accepted)

    def test_same_program_two_sources_is_not_a_pattern(self):
        res = _run([
            _adc(program_id="PROGRAM_A", source_id="SRC-00000001", claim="disclosure one"),
            _adc(program_id="PROGRAM_A", source_id="SRC-00000002",
                 source_identifier="NCT-0002", claim="disclosure two"),
        ])
        self.assertFalse(res.fatal_review.required)

    def test_different_tissue_or_phenotype_is_not_a_pattern(self):
        res = _run(self._two_programs(affected_tissue="BRAIN",
                                     toxicity_phenotype_key="PHENO_Y"))
        self.assertFalse(res.fatal_review.required)

    def test_machine_never_emits_an_established_fatal_signal(self):
        res = _run(self._two_programs())
        self.assertNotIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", FATAL_REVIEW_STATUS_VALUES)
        self.assertNotEqual(res.fatal_review.status, "PUBLIC_FATAL_SIGNAL_ESTABLISHED")
        blob = " ".join(n for n, _ in res.machine_acceptance.checks) + \
            " ".join(res.machine_acceptance.reasons)
        self.assertNotIn("PUBLIC_FATAL_SIGNAL_ESTABLISHED", blob)

    def test_fatal_review_is_never_a_proposal_or_canonical_field(self):
        names = set(AssessmentProposalEnvelope.field_names())
        self.assertFalse(any("fatal" in n or "review" in n for n in names))
        for forbidden in CANONICAL_ONLY_FIELDS:
            self.assertNotIn(forbidden, names)
        res = _run(self._two_programs())
        self.assertFalse(hasattr(res.proposal_envelope, "fatal_review"))


# --- E4-6 path-based stop-rule prerequisites -----------------------------

class StopRuleTests(unittest.TestCase):
    def test_path_b_incomplete_attribution_sweep_rejects_the_run(self):
        res = _run([_adc()], sweep=_sweep(adc_toxicity_attribution_sweep_complete=False))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(res.machine_acceptance.reasons)

    def test_path_c_incomplete_sweep_set_rejects_the_run(self):
        res = _run([_expr()], sweep=_sweep(nhp_sweep_complete=False))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)

    def test_path_a_fatal_pattern_still_requires_the_adc_sweeps(self):
        a = _adc(program_id="PROGRAM_A", source_id="SRC-00000001", construct_fingerprint="FP-A")
        b = _adc(program_id="PROGRAM_B", source_id="SRC-00000002",
                 source_identifier="NCT-0002", construct_fingerprint="FP-B",
                 claim="PROGRAM_B on-target hepatotox")
        res = _run([a, b],
                   sweep=_sweep(same_target_adc_construct_inventory_complete=False))
        self.assertTrue(res.fatal_review.required)
        self.assertFalse(res.machine_acceptance.accepted)

    def test_a_direct_positive_does_not_bypass_the_prerequisite(self):
        res = _run([_adc()],
                   sweep=_sweep(same_target_adc_construct_inventory_complete=False))
        self.assertFalse(res.machine_acceptance.accepted)


# --- exact canonical EvidencePackage reuse + HARD integrity gate (E4-7) -----

class EvidenceReuseAndIntegrityTests(unittest.TestCase):
    def test_exact_library_package_is_reused_with_no_allocator_call_or_rebuild(self):
        rec = _adc(observation_id="OBS-REUSE", claim="the canonical observation claim")
        canonical = _canonical_ep("EP-00007777", rec)
        res, alloc = _run_parts(
            [rec], library=FakeEvidenceLibrary({"OBS-REUSE": canonical})
        )
        self.assertEqual(alloc.calls, 0)
        self.assertEqual(res.evidence_packages, ())
        self.assertEqual(res.reused_evidence_ids, ("EP-00007777",))
        self.assertIn("EP-00007777", [e for e, _ in res.proposal_envelope.evidence_refs])

    def test_a_drifted_canonical_package_is_a_hard_integrity_failure(self):
        rec = _adc(observation_id="OBS-DRIFT", claim="the canonical observation claim")
        canonical = _canonical_ep("EP-00007777", rec, affected_tissue="SKIN")
        res = _run([rec], library=FakeEvidenceLibrary({"OBS-DRIFT": canonical}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("classification-driving drift" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_a_canonical_package_missing_a_driving_field_rejects_the_run(self):
        rec = _adc(observation_id="OBS-MISS", claim="the canonical observation claim")
        canonical = _canonical_ep("EP-00007777", rec)
        del_ctx = dict(canonical.study_context)
        del_ctx.pop("toxicity_phenotype_key")
        canonical = EvidencePackage(
            evidence_id=canonical.evidence_id, schema_version=1, claim=canonical.claim,
            measurement=dict(canonical.measurement), candidate_refs=canonical.candidate_refs,
            study_context=del_ctx, provenance=dict(canonical.provenance),
            interpretation_boundary={k: v for k, v in canonical.interpretation_boundary.items()},
            derivation=dict(canonical.derivation),
        )
        res = _run([rec], library=FakeEvidenceLibrary({"OBS-MISS": canonical}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(
            any("missing the classification-driving field" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_liability_event_id_drift_in_the_canonical_package_rejects_the_run(self):
        # same observation_id / source / claim / candidate, but the canonical EP
        # body was recorded under EVT-A and the current record is EVT-B -- the
        # immutable body would drive a different CONFLICTING grouping.
        rec = _adc(observation_id="OBS-EVT", liability_event_id="EVT-B",
                   claim="the canonical observation claim")
        canonical = _canonical_ep("EP-00007777", rec, liability_event_id="EVT-A")
        res = _run([rec], library=FakeEvidenceLibrary({"OBS-EVT": canonical}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("classification-driving drift" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_attribution_stance_drift_in_the_canonical_package_rejects_the_run(self):
        rec = _attr(observation_id="OBS-ATTR", liability_event_id="EVT-1",
                    target_attribution_stance="REFUTES_TARGET_ATTRIBUTION",
                    claim="the canonical adjudication claim")
        canonical = _canonical_ep(
            "EP-00007777", rec, target_attribution_stance="SUPPORTS_TARGET_ATTRIBUTION"
        )
        res = _run([_adc(liability_event_id="EVT-1"), rec],
                   library=FakeEvidenceLibrary({"OBS-ATTR": canonical}))
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(
            any("classification-driving drift" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_source_missing_from_the_index_rejects_the_run(self):
        res = _run([_adc(source_id="SRC-00000001")], unresolved={"SRC-00000001"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("not in the canonical SourceIndex" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_canonical_source_metadata_mismatch_rejects_the_run(self):
        res = _run([_adc(source_id="SRC-00000001")], mismatch={"SRC-00000001"})
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(
            any("disagrees with the canonical" in why
                for _, why in res.hard_integrity_failures)
        )

    def test_an_unresolved_lead_is_a_soft_drop_not_a_run_failure(self):
        res = _run([_adc(primary_source_resolved=False,
                         claim="a discovery-index row not yet resolved to a primary source")])
        self.assertEqual(len(res.evidence_packages), 0)
        self.assertEqual(res.hard_integrity_failures, ())
        self.assertTrue(res.machine_acceptance.accepted)
        self.assertEqual(res.proposal_envelope.proposed_strength, "UNKNOWN")


# --- boundary: no IO, no scoring, no therapeutic-window conclusion ----------

class BoundaryTests(unittest.TestCase):
    FORBIDDEN = {"socket", "http", "urllib", "requests", "httpx", "subprocess",
                 "sqlite3", "asyncio", "shelve"}

    def test_no_network_db_or_subprocess_imports_in_the_package(self):
        import ast

        for src in PKG.rglob("*.py"):
            tree = ast.parse(src.read_text())
            roots: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots |= {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                    roots.add(node.module.split(".")[0])
            self.assertEqual(roots & self.FORBIDDEN, set(), src.name)

    def test_run_takes_no_separate_drift_prone_target_argument(self):
        self.assertNotIn("target_identity", inspect.signature(run).parameters)

    def test_no_numeric_scoring_or_biological_threshold_in_the_core(self):
        # count guards ("< 2 candidates") are fine; a biological threshold
        # (a number bound to a unit) or a numeric "score" is not.
        pat = re.compile(
            r"\b\d[\d,.]*\s*(molecules|nmol|µm|um\b|ng/ml|ug/ml|per cell|%|-fold)"
            r"|\bscore\s*=|\bnumeric_score\b",
            re.I,
        )
        for name in ("classify.py", "aggregate.py", "acceptance.py", "evidence.py",
                     "fatal_review.py", "module.py"):
            self.assertIsNone(pat.search((PKG / name).read_text()), name)
        manifest = yaml.safe_load((PKG / "module.yaml").read_text())["module"]
        self.assertFalse(manifest["boundary_flags"]["numeric_scoring"])

    def test_no_product_specific_therapeutic_window_conclusion(self):
        res = _run([_adc()])
        self.assertNotIn("therapeutic window",
                         res.proposal_envelope.aggregation_rationale.lower())
        for ep in res.evidence_packages:
            for line in ep.interpretation_boundary["directly_supports"]:
                self.assertNotIn("therapeutic window", line.lower())
            self.assertIn("a product-specific therapeutic window",
                          ep.interpretation_boundary["does_not_support"])

    def test_module_builds_no_canonical_assessment_or_decision(self):
        res = _run([_adc()])
        self.assertIsInstance(res, Tgt05ModuleRunResult)
        self.assertIsInstance(res.proposal_envelope, AssessmentProposalEnvelope)
        self.assertNotIsInstance(res.proposal_envelope, CandidateGateAssessment)
        for attr in ("decision", "assessment", "candidate_gate_assessment", "kill"):
            self.assertFalse(hasattr(res, attr))


# --- coverage state must be backed by evidence (review round 1, blocker 4) ---

class CoverageBackingTests(unittest.TestCase):
    def test_admissible_protein_claim_without_a_protein_ep_is_rejected(self):
        sweep = _sweep(vital_organ_protein_coverage=_covered(*VITAL_ORGAN_CLASSES))
        res = _run([], sweep=sweep)  # no EvidencePackages at all
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertIsNone(res.proposal_envelope)
        self.assertTrue(
            any("no admissible human-protein EvidencePackage" in r
                for r in res.machine_acceptance.reasons)
        )

    def test_exhausted_claim_contradicted_by_a_protein_ep_is_rejected(self):
        # HEPATIC has a validated protein DETECTED EP, but the sweep says the
        # HEPATIC public search was exhausted with nothing admissible.
        sweep = _sweep(vital_organ_protein_coverage=_coverage())  # all exhausted
        res = _run([_expr()], sweep=sweep)
        self.assertFalse(res.machine_acceptance.accepted)
        self.assertTrue(
            any("an admissible human-protein EvidencePackage exists" in r
                for r in res.machine_acceptance.reasons)
        )

    def test_validated_not_detected_ep_backs_an_admissible_protein_claim(self):
        sweep = _sweep(vital_organ_protein_coverage=_covered("HEPATIC"))
        res = _run([_coverage_rec(vital_organ_class="HEPATIC")], sweep=sweep)
        self.assertTrue(res.machine_acceptance.accepted)
        organ_ids = dict(res.coverage_map.supporting_evidence_ids)
        self.assertEqual(len(organ_ids["HEPATIC"]), 1)

    def test_detected_protein_liability_ep_also_backs_the_coverage_map(self):
        res = _run([_expr(vital_organ_class="HEPATIC")])  # auto sweep covers HEPATIC
        self.assertTrue(res.machine_acceptance.accepted)
        organ_ids = dict(res.coverage_map.supporting_evidence_ids)
        self.assertEqual(len(organ_ids["HEPATIC"]), 1)


# --- binding reconciliation + MIGRATION_PENDING ---------------------------

class BindingTests(unittest.TestCase):
    def setUp(self):
        self.gateset = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml").read_text()
        )

    def test_tgt05_binding_is_the_e4_built_module(self):
        bindings = {
            b["gate_id"]: b["primary_module_version"]
            for b in self.gateset["context_specific_bindings"]["gate_bindings"]
        }
        self.assertEqual(bindings["TGT-05"], "1.0.0")
        self.assertEqual(bindings["TGT-01"], "1.0.0")
        # Runtime Migration PR E6 built MOD-TGT08.
        self.assertEqual(bindings["TGT-08"], "1.0.0")
        for gid in ("TGT-02", "TGT-03", "TGT-04", "TGT-06", "TGT-07"):
            self.assertEqual(bindings[gid], "0.0.0")

    def test_built_module_versions_maps_are_consistent(self):
        self.assertEqual(
            self.gateset["primary_module_binding"]["built_module_versions"],
            {"TGT-01": "1.0.0", "TGT-05": "1.0.0", "TGT-08": "1.0.0"},
        )
        self.assertEqual(dict(BUILT_MODULE_VERSIONS),
                         {"TGT-01": "1.0.0", "TGT-05": "1.0.0", "TGT-08": "1.0.0"})

    def test_migration_pending_remains(self):
        readme = (REPO_ROOT / "gate_modules" / "README.md").read_text()
        self.assertIn("MIGRATION_PENDING", readme)
        manifest = yaml.safe_load((PKG / "module.yaml").read_text())["module"]
        self.assertFalse(manifest["boundary_flags"]["lifts_migration_pending"])
        self.assertIn("per_gate_primary_modules",
                      self.gateset["migration"]["deferred"])


if __name__ == "__main__":
    unittest.main()
