import unittest

from src.capabilities.endpoint_biology_completion import (
    EndpointBiologyCompletionRequest,
    EndpointBiologyCompletionResult,
    EndpointBiologyGateTrace,
    T0_T11_TRACE_GATE_IDS,
)


def _trace(gate_id: str) -> EndpointBiologyGateTrace:
    return EndpointBiologyGateTrace(
        gate_id=gate_id,
        gate_result_ref=f"external:gate-result/{gate_id}",
        model_ref=f"external:model/{gate_id}",
        historical_rule_refs=("external:rule/historical-1",),
        evidence_refs=("external:evidence/1",),
        missing_information_refs=(),
    )


class EndpointBiologyCompletionContractTests(unittest.TestCase):
    def test_request_requires_external_rule_and_model_inputs(self):
        request = EndpointBiologyCompletionRequest(
            request_id="external:run/request-1",
            clinical_frame_ref="external:clinical-frame/1",
            target_candidate_refs=("external:candidate/1",),
            upstream_t0_t2_refs=("external:trace/t0-t2",),
            early_reduction_trace_refs=("external:trace/early",),
            historical_adc_rule_refs=("external:rule/historical-1",),
            gate_model_refs=("external:model/registry-v1",),
            run_context_ref="external:run/context-1",
        )
        self.assertEqual(request.target_candidate_refs, ("external:candidate/1",))
        with self.assertRaises(ValueError):
            EndpointBiologyCompletionRequest(
                request_id="external:run/request-1",
                clinical_frame_ref="external:clinical-frame/1",
                target_candidate_refs=("external:candidate/1",),
                upstream_t0_t2_refs=("external:trace/t0-t2",),
                early_reduction_trace_refs=("external:trace/early",),
                historical_adc_rule_refs=("local:rule/1",),
                gate_model_refs=("external:model/registry-v1",),
                run_context_ref="external:run/context-1",
            )

    def test_result_requires_complete_frozen_t0_t11_trace_and_excludes_t12(self):
        traces = tuple(_trace(gate_id) for gate_id in T0_T11_TRACE_GATE_IDS)
        result = EndpointBiologyCompletionResult(
            request_id="external:run/request-1",
            traces=traces,
            missing_information_refs=(),
            run_ref="external:run/result-1",
            full_trace_ref="external:trace/t0-t11-1",
        )
        self.assertEqual(tuple(t.gate_id for t in result.traces), T0_T11_TRACE_GATE_IDS)
        with self.assertRaises(ValueError):
            EndpointBiologyCompletionResult(
                request_id="external:run/request-1",
                traces=traces[:-1],
                missing_information_refs=(),
                run_ref="external:run/result-1",
                full_trace_ref="external:trace/t0-t11-1",
            )

    def test_trace_rejects_t12(self):
        with self.assertRaises(ValueError):
            _trace("target_opportunity_decision")


if __name__ == "__main__":
    unittest.main()
