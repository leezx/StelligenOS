import unittest

from genmodules.gen_indication_endpoint_target import (
    CandidateDisposition,
    CandidateFilterResult,
    ClinicalFrame,
    EvaluationStatus,
    OpportunitySearchScope,
    TargetCandidate,
    TargetOpportunityHandoff,
)


class GenIndicationEndpointTargetContractTests(unittest.TestCase):
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
