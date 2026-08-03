import unittest

from src.capabilities.clinical_frame_pipeline import (
    ClinicalFramePipelineRequest,
    ClinicalFramePipelineResult,
)


class ClinicalFramePipelineContractTests(unittest.TestCase):
    def test_request_is_external_and_budgeted(self):
        request = ClinicalFramePipelineRequest(
            request_id="external:request/1",
            search_scope_ref="external:scope/1",
            clinical_unmet_need_ref="external:unmet-need/1",
            t0_input_ref="external:t0-input/1",
            t1_input_ref="external:t1-input/1",
            generation_policy_ref="external:policy/1",
            run_context_ref="external:run/1",
            candidate_budget=2,
        )
        self.assertEqual(request.candidate_budget, 2)
        with self.assertRaises(ValueError):
            ClinicalFramePipelineRequest(
                **{**request.__dict__, "clinical_unmet_need_ref": "local:data"}
            )

    def test_result_contains_only_external_refs(self):
        result = ClinicalFramePipelineResult(
            request_id="external:request/1",
            clinical_frame_refs=("external:frame/1",),
            t0_result_ref="external:t0/1",
            t1_result_ref="external:t1/1",
            evidence_refs=("external:evidence/1",),
            missing_information_refs=("external:missing/1",),
            run_ref="external:run/1",
        )
        self.assertEqual(result.clinical_frame_refs, ("external:frame/1",))
        with self.assertRaises(ValueError):
            ClinicalFramePipelineResult(
                **{**result.__dict__, "t1_result_ref": "local:t1"}
            )

    def test_empty_reference_groups_are_allowed(self):
        result = ClinicalFramePipelineResult(
            request_id="external:request/1",
            clinical_frame_refs=(),
            t0_result_ref="external:t0/1",
            t1_result_ref="external:t1/1",
            evidence_refs=(),
            missing_information_refs=(),
            run_ref="external:run/1",
        )
        self.assertEqual(result.evidence_refs, ())


if __name__ == "__main__":
    unittest.main()

