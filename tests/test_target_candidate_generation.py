import unittest

from src.capabilities.target_candidate_generation import (
    TargetCandidateGenerationPolicy,
    TargetCandidateGenerationRequest,
    TargetCandidateGenerationResult,
)


class TargetCandidateGenerationContractTests(unittest.TestCase):
    def test_policy_is_bounded_and_disables_unsupported_modes(self):
        policy = TargetCandidateGenerationPolicy(
            maximum_candidates_per_clinical_frame=5,
            minimum_distinct_positive_evidence_groups=2,
        )
        self.assertTrue(policy.require_target_identity_resolution)
        with self.assertRaises(ValueError):
            TargetCandidateGenerationPolicy(
                maximum_candidates_per_clinical_frame=0,
                minimum_distinct_positive_evidence_groups=1,
            )
        with self.assertRaises(ValueError):
            TargetCandidateGenerationPolicy(
                maximum_candidates_per_clinical_frame=5,
                minimum_distinct_positive_evidence_groups=1,
                permit_model_only_generation=True,
            )

    def test_request_is_single_frame_and_external_only(self):
        request = TargetCandidateGenerationRequest(
            request_id="external:run/request-1",
            clinical_frame_ref="external:clinical-frame/1",
            evidence_scope_refs=("external:evidence-scope/public",),
            generation_policy_ref="external:policy/target-candidates-v1",
            run_context_ref="external:run/context-1",
            candidate_budget=5,
            minimum_distinct_positive_evidence_groups=2,
        )
        self.assertEqual(request.candidate_budget, 5)
        with self.assertRaises(ValueError):
            TargetCandidateGenerationRequest(
                request_id="external:run/request-1",
                clinical_frame_ref="local:clinical-frame/1",
                evidence_scope_refs=(),
                generation_policy_ref="external:policy/1",
                run_context_ref="external:run/context-1",
                candidate_budget=1,
                minimum_distinct_positive_evidence_groups=1,
            )

    def test_result_allows_empty_groups_but_rejects_local_refs(self):
        result = TargetCandidateGenerationResult(
            request_id="external:run/request-1",
            target_candidate_refs=(),
            evidence_refs=(),
            missing_information_refs=("external:missing/target-identity",),
            run_ref="external:run/result-1",
        )
        self.assertEqual(result.target_candidate_refs, ())
        with self.assertRaises(ValueError):
            TargetCandidateGenerationResult(
                request_id="external:run/request-1",
                target_candidate_refs=("local:candidate/1",),
                evidence_refs=(),
                missing_information_refs=(),
                run_ref="external:run/result-1",
            )


if __name__ == "__main__":
    unittest.main()
