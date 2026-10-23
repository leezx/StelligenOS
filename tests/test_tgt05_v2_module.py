"""B1 scenario tests for the inactive MOD-TGT05@2.0.0 evidence producer."""

from __future__ import annotations

import dataclasses
import unittest
from pathlib import Path

import yaml

from gate_modules.tgt05_normal_tissue_adc_toxicity_v2 import (
    CoverageAudit, ModuleInput, NormalizedObservation, SourceRecord, run,
)
from src.objects.decision_model import CandidateGateAssessment


REQUEST = ModuleInput(
    candidate_id="CAND-L04-000001", target_hgnc_id="HGNC:5",
    adcdb_target_id="ADCDB-TARGET-5", program_id="PRG-SYNTHETIC",
    context_id="CTX-CRC-REFRACTORY-MCRC", context_version=1,
    run_id="RUN-B1-SYNTHETIC", code_commit="synthetic-test",
)
AUDIT_CLINICAL = SourceRecord("SRC-90000001", "DATASET", "synthetic clinical sweep manifest", "manifest:clinical")
AUDIT_CELLS = SourceRecord("SRC-90000002", "DATASET", "synthetic key-cell coverage manifest", "manifest:cells")
AUDIT_SENSITIVITY = SourceRecord("SRC-90000003", "DATASET", "synthetic LoD and controls", "manifest:lod")
COMPLETE = CoverageAudit(
    target_hgnc_id="HGNC:5", program_id="PRG-SYNTHETIC",
    context_id="CTX-CRC-REFRACTORY-MCRC", context_version=1,
    clinical_sweep="COMPLETE", key_cell_scope="COMPLETE", as_of_date="2026-10-23",
    source_scope=("same-target ADC clinical sources through 2026-10-23",),
    organ_cell_scope=("CARDIAC:cardiomyocyte", "HEPATIC:hepatocyte"),
    assay_sensitivity="validated assay LoD and controls", limitations=(),
    clinical_audit_sources=(AUDIT_CLINICAL,), cell_audit_sources=(AUDIT_CELLS,),
    sensitivity_audit_sources=(AUDIT_SENSITIVITY,), detection_limit_value=0.1,
    detection_limit_unit="ng/mL", assay_positive_control="spike-in positive",
    assay_negative_control="isotype negative",
    sensitivity_assay_methods=("validated assay",),
    candidate_antibody_constructs=("ADC-A",),
)
INCOMPLETE = dataclasses.replace(COMPLETE, clinical_sweep="INCOMPLETE", key_cell_scope="INCOMPLETE")


def obs(number: int, kind: str, finding: str, **changes) -> NormalizedObservation:
    value = NormalizedObservation(
        observation_id=f"OBS-B1-{number}", event_id=f"EVT-B1-{number}",
        target_hgnc_id="HGNC:5", adcdb_target_id="ADCDB-TARGET-5",
        program_id="PRG-SYNTHETIC", context_id="CTX-CRC-REFRACTORY-MCRC", context_version=1,
        kind=kind, finding=finding, claim=f"synthetic claim {number}",
        source_id=f"SRC-{number:08d}", source_type="PMID",
        source_identifier=f"synthetic-pmid-{number}", locator="page 1",
        retrieved_at="2026-10-23T07:00:00Z", organ="CARDIAC",
        cell_type="cardiomyocyte", construct="ADC-A", exposure="relevant dose",
        method="validated assay", normal_human=True, validated=True,
    )
    return dataclasses.replace(value, **changes)


class Provider:
    def __init__(self, observations, coverage=COMPLETE):
        self.observations = tuple(observations)
        self.coverage = coverage

    def fetch_observations(self, request):
        return self.observations

    def coverage_audit(self, request):
        return self.coverage


class Sources:
    def __init__(self, observations, coverage=COMPLETE):
        self.items = {
            o.source_id: SourceRecord(o.source_id, o.source_type, o.source_identifier, o.locator)
            for o in observations
        }
        self.items.update({s.source_id: s for s in (
            *coverage.clinical_audit_sources, *coverage.cell_audit_sources,
            *coverage.sensitivity_audit_sources,
        )})

    def resolve(self, source_id):
        return self.items.get(source_id)


class Library:
    def __init__(self, items=None):
        self.items = items or {}

    def resolve(self, observation_id):
        return self.items.get(observation_id)


class Allocator:
    def __init__(self):
        self.number = 0

    def next_evidence_id(self):
        self.number += 1
        return f"EP-{self.number:08d}"


def execute(observations=(), coverage=COMPLETE, *, sources=None, library=None):
    observations = tuple(observations)
    return run(
        REQUEST, provider=Provider(observations, coverage),
        source_resolver=sources or Sources(observations, coverage),
        evidence_library=library or Library(), evidence_id_allocator=Allocator(),
    )


class Tgt05V2ModuleScenarios(unittest.TestCase):
    def test_version_identity_is_new_and_v2_binding_remains_inactive(self):
        root = Path(__file__).resolve().parents[1]
        metadata = yaml.safe_load((root / "gate_modules/tgt05_normal_tissue_adc_toxicity_v2/module.yaml").read_text())
        gateset = yaml.safe_load((root / "src/contracts/crc_adc_target_gateset_v2.yaml").read_text())
        gate = gateset["gate_contracts"]["TGT-05"]
        self.assertEqual((metadata["module_id"], metadata["module_version"]), ("MOD-TGT05", "2.0.0"))
        self.assertEqual((metadata["gate_id"], metadata["gate_version"]), (gate["gate_id"], gate["gate_version"]))
        self.assertEqual(gate["primary_module_version"], "0.0.0")
        self.assertEqual(gateset["instantiation"]["status"], "HOLD")

    def test_incomplete_coverage_is_unknown_not_hard_failure(self):
        result = execute(coverage=INCOMPLETE)
        self.assertIsNone(result.rejection)
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertTrue(result.proposal.critical_unknowns)

    def test_positive_direct_survives_unrelated_coverage_gap(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                    target_attributed=True, organ_cell_attributed=True,
                    exposure_relevant=True, alternatives_reviewed=True)
        result = execute((event,), INCOMPLETE)
        self.assertIsNone(result.rejection)
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("POSITIVE", "DIRECT"))
        self.assertTrue(result.proposal.fatal_review_trigger)
        self.assertEqual(result.proposal.fatal_review_routes, (("CLINICAL", "EP-00000001"),))
        self.assertTrue(result.proposal.critical_unknowns)
        self.assertNotIn("direction", result.evidence_packages[0].__dataclass_fields__)
        self.assertNotIsInstance(result.proposal, CandidateGateAssessment)

    def test_unresolved_serious_ae_is_weak_review_trigger(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                    target_attributed=False, exposure_relevant=True)
        result = execute((event,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "WEAK"))
        self.assertTrue(result.proposal.attribution_review_trigger)
        self.assertFalse(result.proposal.fatal_review_trigger)

    def test_unvalidated_clinical_attribution_cannot_reach_direct(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", validated=False, severe=True,
                    target_attributed=True, organ_cell_attributed=True,
                    exposure_relevant=True, alternatives_reviewed=True)
        result = execute((event,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "WEAK"))

    def test_nonsevere_unattributed_clinical_observation_is_contextual(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=False,
                    target_attributed=False)
        result = execute((event,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(dict(result.proposal.reviewer_seed)["clinical_liability"], "UNKNOWN")

    def test_qualified_candidate_antibody_negative_is_bounded_direct(self):
        negative = obs(1, "CANDIDATE_ANTIBODY_BINDING", "NOT_DETECTED",
                       physiologically_relevant=True, key_cells_covered=True, assay_sensitive=True)
        result = execute((negative,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("NEGATIVE", "DIRECT"))
        self.assertFalse(result.proposal.fatal_review_trigger)
        self.assertNotIn("recommendation", vars(result.proposal))

    def test_incomplete_clinical_sweep_blocks_negative(self):
        negative = obs(1, "CANDIDATE_ANTIBODY_BINDING", "NOT_DETECTED",
                       physiologically_relevant=True, key_cells_covered=True, assay_sensitive=True)
        result = execute((negative,), INCOMPLETE)
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "UNKNOWN"))

    def test_membrane_protein_non_detection_is_at_most_indirect(self):
        negative = obs(1, "NORMAL_MEMBRANE_PROTEIN", "NOT_DETECTED",
                       membrane_localized=True, key_cells_covered=True, assay_sensitive=True)
        result = execute((negative,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("NEGATIVE", "INDIRECT_STRONG"))

    def test_validated_surface_binding_is_indirect_even_if_physiology_unresolved(self):
        positive = obs(1, "CANDIDATE_ANTIBODY_BINDING", "DETECTED", surface_accessible=True)
        result = execute((positive,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("POSITIVE", "INDIRECT_STRONG"))

    def test_rna_ihc_and_open_targets_cannot_produce_negative(self):
        records = (
            obs(1, "NORMAL_RNA", "NOT_DETECTED"),
            obs(2, "TOTAL_PROTEIN_IHC", "NOT_DETECTED"),
            obs(3, "OPEN_TARGETS_SAFETY", "NOT_DETECTED"),
        )
        result = execute(records)
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "UNKNOWN"))
        self.assertEqual(dict(result.proposal.domain_refs)["SUPPORTING"], ("EP-00000003",))

    def test_rna_or_ihc_detected_only_forms_weak_hypothesis(self):
        result = execute((obs(1, "NORMAL_RNA", "DETECTED"), obs(2, "TOTAL_PROTEIN_IHC", "DETECTED")))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "WEAK"))

    def test_no_reported_clinical_liability_is_context_not_negative(self):
        no_event = obs(1, "ADC_CLINICAL_EVENT", "OTHER")
        result = execute((no_event,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "UNKNOWN"))

    def test_same_event_qualified_refutation_preserves_both_refs(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                    target_attributed=True, organ_cell_attributed=True,
                    exposure_relevant=True, alternatives_reviewed=True)
        refute = obs(2, "CLINICAL_ATTRIBUTION_REFUTATION", "REFUTES", event_id=event.event_id,
                     mechanism="validated alternative cause")
        result = execute((event, refute))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("CONFLICTING", "DIRECT"))
        self.assertEqual({r.evidence_id for r in result.proposal.evidence_refs}, {"EP-00000001", "EP-00000002"})
        self.assertEqual(set(result.proposal.same_event_conflict_refs), {"EP-00000001", "EP-00000002"})

    def test_different_event_refutation_does_not_create_conflict(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                    target_attributed=True, organ_cell_attributed=True,
                    exposure_relevant=True, alternatives_reviewed=True)
        refute = obs(2, "CLINICAL_ATTRIBUTION_REFUTATION", "REFUTES",
                     mechanism="validated alternative cause")
        result = execute((event, refute))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("POSITIVE", "DIRECT"))

    def test_uncontested_second_direct_survives_first_event_conflict(self):
        first = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                    target_attributed=True, organ_cell_attributed=True,
                    exposure_relevant=True, alternatives_reviewed=True)
        refute = obs(2, "CLINICAL_ATTRIBUTION_REFUTATION", "REFUTES", event_id=first.event_id,
                     mechanism="validated alternative cause")
        second = obs(3, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                     target_attributed=True, organ_cell_attributed=True,
                     exposure_relevant=True, alternatives_reviewed=True)
        result = execute((first, refute, second))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("POSITIVE", "DIRECT"))
        self.assertEqual(set(result.proposal.same_event_conflict_refs), {"EP-00000001", "EP-00000002"})
        self.assertEqual(dict(result.proposal.reviewer_seed)["clinical_liability"], "CONFIRMED")

    def test_unqualified_refutation_does_not_create_conflict(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                    target_attributed=True, organ_cell_attributed=True,
                    exposure_relevant=True, alternatives_reviewed=True)
        refute = obs(2, "CLINICAL_ATTRIBUTION_REFUTATION", "REFUTES", event_id=event.event_id,
                     validated=False, mechanism="unverified alternative")
        result = execute((event, refute))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("POSITIVE", "DIRECT"))

    def test_positive_direct_is_not_erased_by_another_cells_negative(self):
        event = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                    target_attributed=True, organ_cell_attributed=True,
                    exposure_relevant=True, alternatives_reviewed=True)
        negative = obs(2, "CANDIDATE_ANTIBODY_BINDING", "NOT_DETECTED",
                       organ="HEPATIC", cell_type="hepatocyte", physiologically_relevant=True,
                       key_cells_covered=True, assay_sensitive=True)
        result = execute((event, negative))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("POSITIVE", "DIRECT"))

    def test_identical_ep_reuse_is_preserved(self):
        event = obs(1, "NORMAL_RNA", "DETECTED")
        original = execute((event,)).evidence_packages[0]
        result = execute((event,), library=Library({event.observation_id: original}))
        self.assertIsNone(result.rejection)
        self.assertEqual(result.evidence_packages, ())
        self.assertEqual(result.reused_evidence_ids, (original.evidence_id,))

    def test_functional_route_requires_human_relevance_and_consequence(self):
        event = obs(1, "NORMAL_CELL_ADC_FUNCTION", "LIABILITY", surface_accessible=True,
                    target_dependent=True, adc_killing=True, exposure_relevant=True,
                    serious_consequence=True)
        result = execute((event,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("POSITIVE", "DIRECT"))
        self.assertTrue(result.proposal.fatal_review_trigger)
        self.assertEqual(result.proposal.fatal_review_routes, (("FUNCTIONAL", "EP-00000001"),))
        self.assertEqual(dict(result.proposal.reviewer_seed)["clinical_liability"], "NONE_DOCUMENTED")
        weak = execute((dataclasses.replace(event, serious_consequence=False),))
        self.assertEqual(weak.proposal.strength, "WEAK")

    def test_target_identity_or_source_integrity_rejects_whole_round(self):
        event = obs(1, "NORMAL_RNA", "DETECTED")
        mismatch = dataclasses.replace(event, target_hgnc_id="HGNC:6")
        result = execute((mismatch,))
        self.assertEqual(result.rejection.code, "TARGET_IDENTITY_MISMATCH")
        self.assertIsNone(result.proposal)
        sources = Sources((event,))
        sources.items.pop(event.source_id)
        result = execute((event,), sources=sources)
        self.assertEqual(result.rejection.code, "SOURCE_INTEGRITY_FAILURE")
        self.assertEqual(result.evidence_packages, ())

    def test_resolver_wrong_source_id_rejects_even_when_metadata_matches(self):
        event = obs(1, "NORMAL_RNA", "DETECTED")
        sources = Sources((event,))
        sources.items[event.source_id] = SourceRecord("SRC-00000042", event.source_type,
                                                      event.source_identifier, event.locator)
        result = execute((event,), sources=sources)
        self.assertEqual(result.rejection.code, "SOURCE_INTEGRITY_FAILURE")
        self.assertEqual(result.evidence_packages, ())
        self.assertIsNone(result.proposal)

    def test_unresolvable_complete_audit_rejects_before_negative(self):
        negative = obs(1, "CANDIDATE_ANTIBODY_BINDING", "NOT_DETECTED",
                       physiologically_relevant=True, key_cells_covered=True, assay_sensitive=True)
        sources = Sources((negative,))
        sources.items.pop(AUDIT_SENSITIVITY.source_id)
        result = execute((negative,), sources=sources)
        self.assertEqual(result.rejection.code, "AUDIT_SOURCE_INTEGRITY_FAILURE")
        self.assertEqual(result.evidence_packages, ())
        self.assertIsNone(result.proposal)

    def test_claimed_complete_audit_without_lod_or_sources_cannot_be_constructed(self):
        with self.assertRaises(ValueError):
            dataclasses.replace(COMPLETE, detection_limit_value=None)
        with self.assertRaises(ValueError):
            dataclasses.replace(COMPLETE, sensitivity_audit_sources=())

    def test_negative_assay_must_match_audited_method_and_construct(self):
        negative = obs(1, "CANDIDATE_ANTIBODY_BINDING", "NOT_DETECTED",
                       physiologically_relevant=True, key_cells_covered=True,
                       assay_sensitive=True, construct="different antibody")
        result = execute((negative,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "UNKNOWN"))
        wrong_method = dataclasses.replace(negative, construct="ADC-A", method="unreviewed assay")
        result = execute((wrong_method,))
        self.assertEqual((result.proposal.direction, result.proposal.strength), ("INCONCLUSIVE", "UNKNOWN"))

    def test_program_context_or_coverage_identity_drift_rejects(self):
        event = obs(1, "NORMAL_RNA", "DETECTED")
        wrong_program = dataclasses.replace(event, program_id="PRG-OTHER")
        result = execute((wrong_program,))
        self.assertEqual(result.rejection.code, "PROGRAM_CONTEXT_MISMATCH")
        wrong_audit = dataclasses.replace(COMPLETE, context_version=2)
        result = execute((event,), wrong_audit)
        self.assertEqual(result.rejection.code, "AUDIT_IDENTITY_MISMATCH")

    def test_reused_ep_classification_drift_rejects_whole_round(self):
        event = obs(1, "NORMAL_MEMBRANE_PROTEIN", "DETECTED", membrane_localized=True)
        first = execute((event,))
        reused = first.evidence_packages[0]
        changed = dataclasses.replace(event, membrane_localized=False)
        result = execute((changed,), library=Library({event.observation_id: reused}))
        self.assertEqual(result.rejection.code, "EP_REUSE_PARITY_FAILURE")
        self.assertIsNone(result.proposal)

    def test_same_observation_identity_with_changed_facts_rejects(self):
        first = obs(1, "NORMAL_RNA", "DETECTED")
        second = dataclasses.replace(first, cell_type="hepatocyte")
        result = execute((first, second))
        self.assertEqual(result.rejection.code, "OBSERVATION_PARITY_DRIFT")

    def test_same_source_and_claim_can_back_two_independent_events(self):
        first = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY")
        second = obs(2, "ADC_CLINICAL_EVENT", "LIABILITY", claim=first.claim,
                     source_id=first.source_id, source_identifier=first.source_identifier,
                     locator=first.locator, organ="HEPATIC", cell_type="hepatocyte")
        result = execute((first, second))
        self.assertIsNone(result.rejection)
        self.assertEqual(len(result.evidence_packages), 2)

    def test_exact_duplicate_observation_is_single_ep(self):
        first = obs(1, "NORMAL_RNA", "DETECTED")
        result = execute((first, first))
        self.assertIsNone(result.rejection)
        self.assertEqual(len(result.evidence_packages), 1)

    def test_failed_audit_is_rejection_not_hold(self):
        failed = dataclasses.replace(COMPLETE, clinical_sweep="FAILED")
        result = execute(coverage=failed)
        self.assertEqual(result.rejection.code, "AUDIT_FAILED")
        self.assertIsNone(result.proposal)

    def test_confirmed_clinical_event_is_not_downgraded_by_pending_other_event(self):
        confirmed = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                        target_attributed=True, organ_cell_attributed=True,
                        exposure_relevant=True, alternatives_reviewed=True)
        pending = obs(2, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                      target_attributed=False)
        result = execute((confirmed, pending))
        self.assertEqual(dict(result.proposal.reviewer_seed)["clinical_liability"], "CONFIRMED")

    def test_pending_clinical_only_is_suspected_in_seed(self):
        pending = obs(1, "ADC_CLINICAL_EVENT", "LIABILITY", severe=True,
                      target_attributed=False)
        result = execute((pending,))
        self.assertEqual(dict(result.proposal.reviewer_seed)["clinical_liability"], "SUSPECTED")


if __name__ == "__main__":
    unittest.main()
