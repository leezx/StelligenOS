import unittest

from src.capabilities.early_t_gate_reduction import (
    CandidateReductionDecision,
    EarlyReductionDisposition,
    EarlyReductionSchedule,
    EarlyTGateReductionRequest,
    EarlyTGateReductionResult,
)


class EarlyTGateReductionContractTests(unittest.TestCase):
    def test_schedule_prioritizes_existing_t2_and_t7_without_t12(self):
        schedule = EarlyReductionSchedule(
            gate_ids=(
                "target_population_mapping",
                "tumor_cell_surface_availability",
                "intratumoral_antigen_accessibility",
            )
        )
        self.assertEqual(schedule.gate_ids[0], "target_population_mapping")
        with self.assertRaises(ValueError):
            EarlyReductionSchedule(
                gate_ids=("target_opportunity_decision", "target_population_mapping")
            )

    def test_missing_evidence_is_hold_not_fail(self):
        decision = CandidateReductionDecision(
            candidate_ref="external:candidate/1",
            disposition=EarlyReductionDisposition.HOLD,
            reason_codes=("missing_surface_evidence",),
            gate_result_refs=(),
            evidence_refs=(),
            missing_information_refs=("external:missing/surface-evidence",),
        )
        self.assertEqual(decision.disposition, EarlyReductionDisposition.HOLD)
        with self.assertRaises(ValueError):
            CandidateReductionDecision(
                candidate_ref="external:candidate/1",
                disposition=EarlyReductionDisposition.HOLD,
                reason_codes=("missing_surface_evidence",),
                gate_result_refs=(),
                evidence_refs=(),
                missing_information_refs=(),
            )

    def test_request_and_result_are_external_only(self):
        request = EarlyTGateReductionRequest(
            request_id="external:run/request-1",
            clinical_frame_ref="external:clinical-frame/1",
            target_candidate_refs=("external:candidate/1",),
            schedule=EarlyReductionSchedule(),
            gate_input_scope_ref="external:gate-input/scope-1",
            run_context_ref="external:run/context-1",
        )
        result = EarlyTGateReductionResult(
            request_id=request.request_id,
            decisions=(
                CandidateReductionDecision(
                    candidate_ref="external:candidate/1",
                    disposition=EarlyReductionDisposition.PROVISIONAL_ADVANCE,
                    reason_codes=("priority_gate_inputs_available",),
                    gate_result_refs=("external:gate-result/t2-1",),
                    evidence_refs=("external:evidence/1",),
                    missing_information_refs=(),
                ),
            ),
            run_ref="external:run/result-1",
            trace_ref="external:trace/1",
        )
        self.assertEqual(len(result.decisions), 1)
        with self.assertRaises(ValueError):
            EarlyTGateReductionRequest(
                request_id="external:run/request-1",
                clinical_frame_ref="local:clinical-frame/1",
                target_candidate_refs=("external:candidate/1",),
                schedule=EarlyReductionSchedule(),
                gate_input_scope_ref="external:gate-input/scope-1",
                run_context_ref="external:run/context-1",
            )


if __name__ == "__main__":
    unittest.main()
