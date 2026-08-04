import unittest

from genmodules.target_safety_therapeutic_window_prescreen import (
    AssessmentRequest,
    Criticality,
    Decision,
    EvidenceAxis,
    EvidenceClaim,
    EvidenceLevel,
    RiskDirection,
    TargetProfile,
    assess_target,
)


def claim(**overrides):
    values = {
        "claim_ref": "external:claim/1",
        "axis": EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
        "level": EvidenceLevel.C,
        "direction": RiskDirection.SUPPORTS_SAFETY,
        "source_ref": "external:source/1",
        "rationale_ref": "external:rationale/1",
    }
    values.update(overrides)
    return EvidenceClaim(**values)


def request(claims):
    return AssessmentRequest(
        request_ref="external:request/1",
        target=TargetProfile(target_ref="external:target/1", gene_symbol="GUCY2C"),
        evidence_refs=tuple(item.claim_ref for item in claims),
        claims=tuple(claims),
        policy_ref="external:policy/target-safety-v0.1",
        run_context_ref="external:run/context-1",
    )


class TargetSafetyPreScreenTests(unittest.TestCase):
    def test_fatal_critical_surface_hazard_wins(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/critical-surface",
                        axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        criticality=Criticality.CRITICAL_NON_REGENERATIVE,
                        surface_exposed=True,
                    ),
                    claim(
                        claim_ref="external:claim/unknown-density",
                        axis=EvidenceAxis.ANTIGEN_DENSITY,
                        level=EvidenceLevel.U,
                        direction=RiskDirection.UNKNOWN,
                        unresolved=True,
                    ),
                ]
            )
        )
        self.assertEqual(result.decision, Decision.KILL)
        self.assertEqual(result.fatal_flags[0].value, "critical_surface_hazard")
        self.assertIn("external:claim/unknown-density", result.unresolved_refs)

    def test_unknown_or_conflicting_critical_evidence_holds(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/critical-conflict",
                        axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
                        level=EvidenceLevel.D,
                        direction=RiskDirection.CONFLICTING,
                        criticality=Criticality.CRITICAL_REVERSIBLE,
                    )
                ]
            )
        )
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("external:claim/critical-conflict", result.conflict_refs)

    def test_plausible_differential_is_conditional_go(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/surface-differential",
                        axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_SAFETY,
                        surface_exposed=False,
                    ),
                    claim(
                        claim_ref="external:claim/density-differential",
                        axis=EvidenceAxis.ANTIGEN_DENSITY,
                        level=EvidenceLevel.C,
                        direction=RiskDirection.SUPPORTS_SAFETY,
                        normal_density_relation="lower",
                    ),
                ]
            )
        )
        self.assertEqual(result.decision, Decision.CONDITIONAL_GO)
        self.assertEqual(result.confidence, "medium")
        self.assertTrue(result.mitigation_refs)

    def test_empty_evidence_is_hold_and_requests_next_experiments(self):
        result = assess_target(request([]))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertEqual(len(result.axis_summaries), 6)
        self.assertEqual(len(result.next_experiment_refs), 6)

    def test_contract_rejects_non_external_evidence(self):
        with self.assertRaises(ValueError):
            claim(source_ref="local:source/1")


if __name__ == "__main__":
    unittest.main()
