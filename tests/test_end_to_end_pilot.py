import unittest

from src.capabilities.end_to_end_pilot import (
    EndToEndPilotRequest,
    EndToEndPilotResult,
    PilotCandidateOutcome,
    PilotOutcome,
)


class EndToEndPilotContractTests(unittest.TestCase):
    def test_request_is_external_and_preserves_all_pilot_inputs(self):
        request = EndToEndPilotRequest(
            request_id="external:pilot/request-1",
            clinical_frame_ref="external:clinical-frame/crc-1",
            external_data_bundle_ref="external:data/crc-pilot-bundle",
            candidate_generation_ref="external:generation/run-1",
            lifecycle_contract_refs=("external:contract/lifecycle-v1",),
            stage_trace_refs=("external:trace/phase0-7",),
            candidate_refs=("external:candidate/tweakr", "external:candidate/other"),
            selection_policy_ref="external:policy/pilot-selection-v1",
            pilot_run_context_ref="external:run/pilot-1",
        )
        self.assertEqual(len(request.candidate_refs), 2)
        with self.assertRaises(ValueError):
            EndToEndPilotRequest(
                request_id="external:pilot/request-1",
                clinical_frame_ref="local:clinical-frame/crc-1",
                external_data_bundle_ref="external:data/crc-pilot-bundle",
                candidate_generation_ref="external:generation/run-1",
                lifecycle_contract_refs=("external:contract/lifecycle-v1",),
                stage_trace_refs=("external:trace/phase0-7",),
                candidate_refs=("external:candidate/1",),
                selection_policy_ref="external:policy/pilot-selection-v1",
                pilot_run_context_ref="external:run/pilot-1",
            )

    def test_result_allows_hold_reject_or_no_advance_and_disables_assets(self):
        result = EndToEndPilotResult(
            request_id="external:pilot/request-1",
            outcome=PilotOutcome.NO_CANDIDATE_ADVANCED,
            candidate_outcomes=(
                PilotCandidateOutcome(
                    candidate_ref="external:candidate/tweakr",
                    disposition_ref="external:disposition/hold",
                    decision_trace_ref="external:trace/candidate-1",
                ),
            ),
            selected_candidate_refs=(),
            held_candidate_refs=("external:candidate/tweakr",),
            rejected_candidate_refs=(),
            pilot_trace_ref="external:trace/pilot-1",
            pilot_run_ref="external:run/pilot-1",
        )
        self.assertEqual(result.outcome, PilotOutcome.NO_CANDIDATE_ADVANCED)
        with self.assertRaises(ValueError):
            EndToEndPilotResult(
                request_id="external:pilot/request-1",
                outcome=PilotOutcome.COMPLETED,
                candidate_outcomes=result.candidate_outcomes,
                selected_candidate_refs=(),
                held_candidate_refs=(),
                rejected_candidate_refs=(),
                pilot_trace_ref="external:trace/pilot-1",
                pilot_run_ref="external:run/pilot-1",
                asset_generation_enabled=True,
            )


if __name__ == "__main__":
    unittest.main()
