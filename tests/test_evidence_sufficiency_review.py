import unittest

from src.capabilities.evidence_sufficiency_review import (
    AdversarialReviewRequest,
    AdversarialReviewResult,
    AdversarialReviewStatus,
    EvidenceReadiness,
    EvidenceReadinessRequest,
    EvidenceReadinessResult,
    PositiveEvidencePolicy,
)


class EvidenceSufficiencyReviewContractTests(unittest.TestCase):
    def test_policy_thresholds_are_external_configuration(self):
        policy = PositiveEvidencePolicy(
            policy_id="external:policy/evidence-v1",
            required_gate_ids=("external:gate/t0", "external:gate/t1"),
            minimum_independent_source_groups=2,
            maximum_critical_unknowns=3,
        )
        self.assertEqual(policy.minimum_independent_source_groups, 2)
        with self.assertRaises(ValueError):
            PositiveEvidencePolicy(
                policy_id="external:policy/evidence-v1",
                required_gate_ids=(),
                minimum_independent_source_groups=1,
                maximum_critical_unknowns=0,
            )

    def test_adversarial_review_is_external_and_non_gate(self):
        request = AdversarialReviewRequest(
            request_id="external:run/review-request-1",
            candidate_ref="external:candidate/1",
            t0_t11_trace_ref="external:trace/t0-t11-1",
            evidence_ledger_ref="external:ledger/1",
            independence_report_ref="external:independence/1",
            review_scope_ref="external:review-scope/1",
            run_context_ref="external:run/context-1",
        )
        result = AdversarialReviewResult(
            request_id=request.request_id,
            review_ref="external:review/1",
            status=AdversarialReviewStatus.REQUIRES_VALIDATION,
            objections_ref="external:objections/1",
            counter_evidence_refs=(),
            validation_task_refs=("external:validation-task/1",),
            critical_unknown_refs=("external:unknown/1",),
            run_ref="external:run/result-1",
        )
        self.assertEqual(result.status, AdversarialReviewStatus.REQUIRES_VALIDATION)

    def test_readiness_requires_external_refs_and_keeps_validation_tasks(self):
        request = EvidenceReadinessRequest(
            request_id="external:run/readiness-request-1",
            candidate_ref="external:candidate/1",
            positive_evidence_refs=("external:evidence/1",),
            gate_trace_ref="external:trace/t0-t11-1",
            policy_ref="external:policy/evidence-v1",
            independence_report_ref="external:independence/1",
            adversarial_review_ref="external:review/1",
            validation_task_refs=("external:validation-task/1",),
            run_context_ref="external:run/context-1",
        )
        result = EvidenceReadinessResult(
            request_id=request.request_id,
            candidate_ref=request.candidate_ref,
            readiness=EvidenceReadiness.VALIDATION_REQUIRED,
            policy_ref=request.policy_ref,
            independence_report_ref=request.independence_report_ref,
            adversarial_review_ref=request.adversarial_review_ref,
            validation_task_refs=request.validation_task_refs,
            unresolved_refs=("external:unknown/1",),
            run_ref="external:run/result-1",
        )
        self.assertEqual(result.readiness, EvidenceReadiness.VALIDATION_REQUIRED)
        with self.assertRaises(ValueError):
            EvidenceReadinessResult(
                request_id="external:run/readiness-request-1",
                candidate_ref="external:candidate/1",
                readiness=EvidenceReadiness.READY_FOR_T12_DECISION,
                policy_ref="external:policy/evidence-v1",
                independence_report_ref="external:independence/1",
                adversarial_review_ref="external:review/1",
                validation_task_refs=("external:validation-task/1",),
                unresolved_refs=(),
                run_ref="external:run/result-1",
            )


if __name__ == "__main__":
    unittest.main()
