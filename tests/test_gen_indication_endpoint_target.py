import unittest

from genmodules.gen_indication_endpoint_target import (
    AdversarialReview,
    BiomarkerHypothesis,
    BiomarkerCutoffStatus,
    CDxStatus,
    CandidateLifecycle,
    CandidateDisposition,
    CandidateFilterResult,
    ClinicalFrame,
    ClinicalHypothesis,
    ClinicalHypothesisEntryMode,
    ClinicalLockState,
    EvaluationStatus,
    OpportunitySearchScope,
    TargetCandidate,
    TargetOpportunityHandoff,
    can_transition_clinical_lock,
)


class GenIndicationEndpointTargetContractTests(unittest.TestCase):
    def test_v5_clinical_hypothesis_is_composed_from_external_refs(self):
        hypothesis = ClinicalHypothesis(
            hypothesis_id="hypothesis-1",
            target_ref="external:target/1",
            anchor_context_ref="external:anchor/1",
            intended_benefit_ref="external:benefit/1",
            biomarker_hypothesis_ref="external:biomarker/1",
            product_hypothesis_ref="external:product/1",
            lock_state=ClinicalLockState.PROVISIONAL,
            source_refs=("external:source/1",),
        )
        self.assertEqual(hypothesis.lock_state, ClinicalLockState.PROVISIONAL)
        with self.assertRaises(ValueError):
            ClinicalHypothesis(
                **{**hypothesis.__dict__, "target_ref": "local:target/1"}
            )

    def test_v5_biomarker_cutoff_is_explicitly_deferred(self):
        biomarker = BiomarkerHypothesis(
            biomarker_id="bm-1",
            biological_feature="surface expression",
            specimen_type="archived_tissue",
            assay_method="IHC",
            measurement_scale="continuous",
            heterogeneity_risk="unknown",
            assay_feasibility="feasible",
            final_cutoff_deferred=True,
            source_refs=("external:source/1",),
        )
        self.assertTrue(biomarker.final_cutoff_deferred)

    def test_v5_cutoff_and_cdx_lock_require_external_refs(self):
        with self.assertRaises(ValueError):
            BiomarkerHypothesis(
                biomarker_id="bm-locked",
                biological_feature="surface expression",
                specimen_type="tissue",
                assay_method="IHC",
                measurement_scale="continuous",
                heterogeneity_risk="unknown",
                assay_feasibility="feasible",
                source_refs=("external:source/1",),
                cutoff_status=BiomarkerCutoffStatus.LOCKED,
                cdx_status=CDxStatus.LOCKED,
            )

    def test_v5_lock_transitions_are_monotonic_single_step(self):
        self.assertTrue(
            can_transition_clinical_lock(
                ClinicalLockState.EXPLORATORY,
                ClinicalLockState.PROVISIONAL,
            )
        )
        self.assertFalse(
            can_transition_clinical_lock(
                ClinicalLockState.REGULATORY_LOCKED,
                ClinicalLockState.EXPLORATORY,
            )
        )
        self.assertFalse(
            can_transition_clinical_lock(
                ClinicalLockState.EXPLORATORY,
                ClinicalLockState.PRODUCT_LOCKED,
            )
        )

    def test_v5_entry_modes_define_valid_exploratory_seeds(self):
        for mode, seed_kwargs in (
            (ClinicalHypothesisEntryMode.MATURE_TARGET_FIRST, {"target_ref": "external:target/1"}),
            (ClinicalHypothesisEntryMode.TARGET_CONTEXT_COSELECTION, {"anchor_context_ref": "external:anchor/1"}),
            (ClinicalHypothesisEntryMode.CLINICAL_PROBLEM_FIRST, {"intended_benefit_ref": "external:benefit/1"}),
        ):
            hypothesis = ClinicalHypothesis(
                hypothesis_id=f"seed-{mode.value}",
                lock_state=ClinicalLockState.EXPLORATORY,
                source_refs=(),
                entry_mode=mode,
                **seed_kwargs,
            )
            self.assertEqual(hypothesis.entry_mode, mode)
        seed_scope = OpportunitySearchScope(
            scope_id="seed-scope", version="2.0", modality="ADC", candidate_budget=1,
            clinical_hypothesis_seed_ref="external:seed/1",
            entry_mode=ClinicalHypothesisEntryMode.MATURE_TARGET_FIRST,
        )
        self.assertEqual(seed_scope.entry_mode, ClinicalHypothesisEntryMode.MATURE_TARGET_FIRST)
        with self.assertRaises(ValueError):
            ClinicalHypothesis(
                hypothesis_id="bad",
                target_ref=None,
                anchor_context_ref=None,
                intended_benefit_ref=None,
                biomarker_hypothesis_ref=None,
                product_hypothesis_ref=None,
                lock_state=ClinicalLockState.PROVISIONAL,
                source_refs=(),
                entry_mode=ClinicalHypothesisEntryMode.CLINICAL_PROBLEM_FIRST,
            )
        with self.assertRaises(ValueError):
            ClinicalHypothesis(
                hypothesis_id="empty-co-selection",
                lock_state=ClinicalLockState.EXPLORATORY,
                source_refs=(),
                entry_mode=ClinicalHypothesisEntryMode.TARGET_CONTEXT_COSELECTION,
            )

    def test_v5_lock_requirements_are_cumulative(self):
        with self.assertRaises(ValueError):
            ClinicalHypothesis(
                hypothesis_id="invalid-protocol", lock_state=ClinicalLockState.PROTOCOL_LOCKED,
                source_refs=(), protocol_endpoint_ref="external:protocol/1",
            )
        with self.assertRaises(ValueError):
            ClinicalHypothesis(
                hypothesis_id="invalid-regulatory", lock_state=ClinicalLockState.REGULATORY_LOCKED,
                source_refs=(), protocol_endpoint_ref="external:protocol/1",
                final_indication_ref="external:indication/1", registrational_endpoint_ref="external:endpoint/1",
                biomarker_cutoff_ref="external:cutoff/1", cdx_ref="external:cdx/1",
            )

    def test_v5_hypothesis_flows_to_t12_handoff(self):
        handoff = TargetOpportunityHandoff(
            handoff_id="handoff-v5",
            candidate_id="candidate-1",
            opportunity_ref="external:opportunity/1",
            target_hypothesis_ref="external:hypothesis/target-1",
            t12_gate_result_ref="external:t12/1",
            evidence_refs=("external:evidence/1",),
            adversarial_review_ref="external:review/1",
            lifecycle=CandidateLifecycle.READY_FOR_T12_DECISION,
            readiness=EvaluationStatus.EVALUATED,
            clinical_hypothesis_ref="external:hypothesis/clinical-1",
            clinical_lock_state=ClinicalLockState.PRODUCT_LOCKED,
            anchor_context_ref="external:anchor/1",
        )
        self.assertEqual(handoff.clinical_hypothesis_ref, "external:hypothesis/clinical-1")

    def test_v5_candidate_can_use_hypothesis_identity_without_legacy_snapshot(self):
        candidate = TargetCandidate(
            candidate_id="candidate-v5",
            clinical_frame_id="frame-v5",
            biological_hypothesis="external biology hypothesis",
            adc_hypothesis="external adc hypothesis",
            generation_method="external_policy",
            source_run_ref="external:run/v5",
            clinical_hypothesis_ref="external:hypothesis/clinical-v5",
        )
        self.assertIsNone(candidate.indication)
        self.assertEqual(candidate.clinical_hypothesis_ref, "external:hypothesis/clinical-v5")

    def test_v5_t12_requires_hypothesis_and_lock_state_as_a_pair(self):
        handoff_kwargs = dict(
            handoff_id="handoff-v5-invalid",
            candidate_id="candidate-1",
            opportunity_ref="external:opportunity/1",
            target_hypothesis_ref="external:hypothesis/target-1",
            t12_gate_result_ref="external:t12/1",
            evidence_refs=("external:evidence/1",),
            adversarial_review_ref="external:review/1",
            lifecycle=CandidateLifecycle.READY_FOR_T12_DECISION,
            readiness=EvaluationStatus.EVALUATED,
            clinical_hypothesis_ref="external:hypothesis/clinical-1",
        )
        with self.assertRaises(ValueError):
            TargetOpportunityHandoff(**handoff_kwargs)
        with self.assertRaises(ValueError):
            TargetOpportunityHandoff(
                **{**handoff_kwargs, "clinical_hypothesis_ref": None, "clinical_lock_state": ClinicalLockState.PRODUCT_LOCKED}
            )

    def test_scope_requires_adc_and_external_policy_inputs(self):
        scope = OpportunitySearchScope(
            scope_id="scope-1",
            version="1.0",
            indication="indication",
            disease_setting="setting",
            line_of_therapy="line",
            treatment_context="context",
            comparator="comparator",
            patient_segment_constraints=("segment",),
            endpoint_definition="endpoint",
            endpoint_time_horizon="time",
            clinical_success_condition="success",
            modality="ADC",
            evidence_cutoff_date="2026-08-01",
            candidate_budget=3,
            source_policy_id="external:policy/1",
            evaluation_plan_id="external:plan/1",
        )
        self.assertEqual(scope.modality, "ADC")
        with self.assertRaises(ValueError):
            OpportunitySearchScope(
                **{**scope.__dict__, "modality": "small_molecule"}
            )
        with self.assertRaises(ValueError):
            OpportunitySearchScope(
                **{**scope.__dict__, "source_policy_id": "local:policy"}
            )
        with self.assertRaises(ValueError):
            OpportunitySearchScope(
                **{**scope.__dict__, "evaluation_plan_id": "local:plan"}
            )

    def test_target_identity_contains_four_required_dimensions(self):
        candidate = TargetCandidate(
            candidate_id="candidate-1",
            clinical_frame_id="frame-1",
            indication="indication",
            patient_population="population",
            clinical_endpoint="endpoint",
            adc_target="target",
            disease_setting="setting",
            line_of_therapy="line",
            treatment_context="context",
            comparator="comparator",
            endpoint_time_horizon="time",
            biological_hypothesis="biology",
            adc_hypothesis="adc",
            generation_method="external_policy",
            source_run_ref="external:run/1",
            legacy_compatibility=True,
        )
        self.assertEqual(
            candidate.opportunity_identity,
            ("indication", "population", "endpoint", "target"),
        )

    def test_clinical_frame_gate_results_must_be_external(self):
        with self.assertRaises(ValueError):
            ClinicalFrame(
                frame_id="frame-1",
                scope_id="scope-1",
                indication="indication",
                disease_setting="setting",
                line_of_therapy="line",
                treatment_context="context",
                comparator="comparator",
                endpoint_definition="endpoint",
                endpoint_time_horizon="time",
                endpoint_driving_population="population",
                source_evidence_ids=("external:evidence/1",),
                t0_gate_result_ref="local:t0",
                t1_gate_result_ref="external:t1",
            )

    def test_clinical_frame_rejects_local_evidence_reference(self):
        with self.assertRaises(ValueError):
            ClinicalFrame(
                frame_id="frame-1",
                scope_id="scope-1",
                indication="indication",
                disease_setting="setting",
                line_of_therapy="line",
                treatment_context="context",
                comparator="comparator",
                endpoint_definition="endpoint",
                endpoint_time_horizon="time",
                endpoint_driving_population="population",
                source_evidence_ids=("local:evidence",),
                t0_gate_result_ref="external:t0",
                t1_gate_result_ref="external:t1",
            )

    def test_filter_is_not_a_gate_and_preserves_unresolved(self):
        result = CandidateFilterResult(
            filter_id="filter-1",
            candidate_id="candidate-1",
            disposition=CandidateDisposition.DEFER,
            status=EvaluationStatus.UNRESOLVED,
            reason_codes=("insufficient_evidence",),
        )
        self.assertEqual(result.status, EvaluationStatus.UNRESOLVED)
        self.assertNotIn("gate_id", result.__dataclass_fields__)

    def test_filter_rejects_local_evidence_reference(self):
        with self.assertRaises(ValueError):
            CandidateFilterResult(
                filter_id="filter-1",
                candidate_id="candidate-1",
                disposition=CandidateDisposition.DEFER,
                status=EvaluationStatus.UNRESOLVED,
                reason_codes=("insufficient_evidence",),
                evidence_ids=("local:evidence",),
            )

    def test_adversarial_review_rejects_local_counter_evidence(self):
        with self.assertRaises(ValueError):
            AdversarialReview(
                review_id="review-1",
                candidate_id="candidate-1",
                objections=("objection",),
                counter_evidence_ids=("local:evidence",),
                alternative_explanations=("alternative",),
                critical_unknowns=("unknown",),
                validation_tasks=("validate",),
                reviewer_ref="external:reviewer/1",
                status=EvaluationStatus.UNRESOLVED,
            )

    def test_t12_handoff_rejects_local_evidence_reference(self):
        with self.assertRaises(ValueError):
            TargetOpportunityHandoff(
                handoff_id="handoff-1",
                candidate_id="candidate-1",
                opportunity_ref="external:opportunity/1",
                target_hypothesis_ref="external:hypothesis/1",
                t12_gate_result_ref="external:t12/1",
                evidence_refs=("local:evidence",),
                adversarial_review_ref="external:review/1",
                lifecycle="READY_FOR_T12_DECISION",
                readiness=EvaluationStatus.EVALUATED,
            )

    def test_repository_has_no_data_bearing_runtime_artifacts(self):
        from pathlib import Path

        module_root = Path(__file__).parents[1] / "genmodules" / "gen_indication_endpoint_target"
        files = {path.name for path in module_root.rglob("*") if path.is_file()}
        self.assertEqual(files, {"__init__.py", "contracts.py", "README.md"})


if __name__ == "__main__":
    unittest.main()
