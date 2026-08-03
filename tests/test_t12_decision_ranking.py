import unittest

from src.capabilities.t12_decision_ranking import (
    OpportunityHandoffPackage,
    OpportunityRankingRequest,
    OpportunityRankingResult,
    T12DecisionDisposition,
    T12DecisionRequest,
    T12DecisionResult,
)


class T12DecisionRankingContractTests(unittest.TestCase):
    def test_t12_request_is_bound_to_readiness_and_full_trace(self):
        request = T12DecisionRequest(
            request_id="external:run/t12-request-1",
            candidate_ref="external:candidate/1",
            readiness_ref="external:readiness/1",
            t0_t11_trace_ref="external:trace/t0-t11-1",
            decision_policy_ref="external:policy/t12-v1",
            run_context_ref="external:run/context-1",
        )
        self.assertEqual(request.candidate_ref, "external:candidate/1")

    def test_t12_result_preserves_disposition_and_disables_asset_generation(self):
        handoff = OpportunityHandoffPackage(
            opportunity_ref="external:opportunity/1",
            decision_ref="external:t12-result/1",
            rationale_ref="external:rationale/1",
            required_next_evidence_refs=("external:evidence/next-1",),
            cheapest_decisive_experiment_ref="external:experiment/1",
        )
        result = T12DecisionResult(
            request_id="external:run/t12-request-1",
            disposition=T12DecisionDisposition.HOLD,
            t12_result_ref="external:t12-result/1",
            hard_failure_refs=(),
            unresolved_refs=("external:unknown/1",),
            handoff=handoff,
            run_ref="external:run/t12-result-1",
        )
        self.assertEqual(result.disposition, T12DecisionDisposition.HOLD)
        with self.assertRaises(ValueError):
            OpportunityHandoffPackage(
                opportunity_ref="external:opportunity/1",
                decision_ref="external:t12-result/1",
                rationale_ref="external:rationale/1",
                required_next_evidence_refs=(),
                cheapest_decisive_experiment_ref="external:experiment/1",
                eligible_for_asset_generation=True,
            )

    def test_ranking_requires_eligible_decisions_and_external_outputs(self):
        request = OpportunityRankingRequest(
            request_id="external:run/rank-request-1",
            eligible_decision_refs=("external:t12-result/1",),
            excluded_decision_refs=("external:t12-result/2",),
            ranking_policy_ref="external:policy/ranking-v1",
            run_context_ref="external:run/context-1",
        )
        result = OpportunityRankingResult(
            request_id=request.request_id,
            ranked_opportunity_refs=("external:opportunity/1",),
            held_opportunity_refs=(),
            rejected_opportunity_refs=(),
            ranking_trace_ref="external:trace/ranking-1",
            run_ref="external:run/ranking-result-1",
        )
        self.assertEqual(result.ranked_opportunity_refs, ("external:opportunity/1",))
        with self.assertRaises(ValueError):
            OpportunityRankingRequest(
                request_id="external:run/rank-request-1",
                eligible_decision_refs=(),
                excluded_decision_refs=(),
                ranking_policy_ref="external:policy/ranking-v1",
                run_context_ref="external:run/context-1",
            )


if __name__ == "__main__":
    unittest.main()
