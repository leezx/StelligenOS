import unittest

from genmodules.target_safety_therapeutic_window_prescreen import (
    AssessmentRequest,
    Criticality,
    Decision,
    DifferentialStatus,
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


def complete_resolved_claims():
    return [
        claim(
            claim_ref=f"external:claim/complete-{index}",
            axis=axis,
            level=EvidenceLevel.C,
            direction=RiskDirection.SUPPORTS_SAFETY,
        )
        for index, axis in enumerate(EvidenceAxis, start=1)
    ]


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
                        hazard_context_ref="external:hazard/heart",
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

    def test_fatal_claim_without_hazard_context_holds(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/unscoped-fatal",
                        axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        criticality=Criticality.CRITICAL_NON_REGENERATIVE,
                        surface_exposed=True,
                    )
                ]
            )
        )
        self.assertEqual(result.fatal_flags, ())
        self.assertEqual(result.decision, Decision.HOLD)

    def test_plausible_differential_is_conditional_go(self):
        claims = complete_resolved_claims()
        claims[1] = claim(
            claim_ref="external:claim/surface-differential",
            axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
            level=EvidenceLevel.B,
            direction=RiskDirection.SUPPORTS_SAFETY,
            surface_exposed=False,
            differential_status=DifferentialStatus.PRESENT,
            hazard_context_ref="external:hazard/conditional",
        )
        claims[2] = claim(
            claim_ref="external:claim/density-differential",
            axis=EvidenceAxis.ANTIGEN_DENSITY,
            level=EvidenceLevel.C,
            direction=RiskDirection.SUPPORTS_SAFETY,
            normal_density_relation="lower",
            differential_status=DifferentialStatus.PRESENT,
            hazard_context_ref="external:hazard/conditional",
            mitigates_claim_refs=("external:claim/conditional-material-risk",),
        )
        claims.append(
            claim(
                claim_ref="external:claim/conditional-material-risk",
                axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                level=EvidenceLevel.B,
                direction=RiskDirection.SUPPORTS_RISK,
                criticality=Criticality.REGENERATIVE,
                hazard_context_ref="external:hazard/conditional",
            )
        )
        result = assess_target(
            request(claims)
        )
        self.assertEqual(result.decision, Decision.CONDITIONAL_GO)
        self.assertEqual(result.confidence, "medium")
        self.assertTrue(result.mitigation_refs)

    def test_go_requires_all_axes_resolved_and_no_material_risk(self):
        result = assess_target(request(complete_resolved_claims()))
        self.assertEqual(result.decision, Decision.GO)
        self.assertEqual(result.material_risk_refs, ())

    def test_nonfatal_material_risk_is_hold_not_go(self):
        claims = complete_resolved_claims()
        claims.append(
            claim(
                claim_ref="external:claim/nonfatal-risk",
                axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                level=EvidenceLevel.B,
                direction=RiskDirection.SUPPORTS_RISK,
                criticality=Criticality.REGENERATIVE,
            )
        )
        result = assess_target(request(claims))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("external:claim/nonfatal-risk", result.material_risk_refs)

    def test_unknown_direction_is_unresolved_and_holds(self):
        claims = complete_resolved_claims()
        claims[0] = claim(
            claim_ref="external:claim/unknown-direction",
            axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
            level=EvidenceLevel.B,
            direction=RiskDirection.UNKNOWN,
        )
        result = assess_target(request(claims))
        self.assertEqual(result.decision, Decision.HOLD)
        self.assertIn("external:claim/unknown-direction", result.unresolved_refs)

    def test_surface_and_critical_tissue_claims_aggregate_to_fatal(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/surface-risk",
                        axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        surface_exposed=True,
                        hazard_context_ref="external:hazard/heart",
                    ),
                    claim(
                        claim_ref="external:claim/critical-tissue-risk",
                        axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        criticality=Criticality.CRITICAL_NON_REGENERATIVE,
                        hazard_context_ref="external:hazard/heart",
                    ),
                ]
            )
        )
        self.assertIn("critical_surface_hazard", [flag.value for flag in result.fatal_flags])

    def test_density_alone_does_not_kill_when_surface_is_inaccessible(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/density-risk",
                        axis=EvidenceAxis.ANTIGEN_DENSITY,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        normal_density_relation="higher",
                        hazard_context_ref="external:hazard/kidney",
                    ),
                    claim(
                        claim_ref="external:claim/inaccessible-surface",
                        axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        surface_exposed=False,
                        hazard_context_ref="external:hazard/kidney",
                    ),
                    claim(
                        claim_ref="external:claim/critical-tissue",
                        axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        criticality=Criticality.CRITICAL_NON_REGENERATIVE,
                        hazard_context_ref="external:hazard/kidney",
                    ),
                ]
            )
        )
        self.assertNotIn("normal_density_not_lower_than_tumor", [flag.value for flag in result.fatal_flags])
        self.assertEqual(result.decision, Decision.HOLD)

    def test_free_tag_cannot_create_no_differential_fatal(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/free-tag",
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        tags=("widespread_no_differential",),
                    )
                ]
            )
        )
        self.assertNotIn("no_exploitable_target_differential", [flag.value for flag in result.fatal_flags])

    def test_structured_absent_differential_can_create_fatal(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/structured-no-differential",
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        differential_status=DifferentialStatus.ABSENT,
                        differential_assessment_ref="external:assessment/no-differential",
                    )
                ]
            )
        )
        self.assertIn("no_exploitable_target_differential", [flag.value for flag in result.fatal_flags])

    def test_cross_context_surface_and_criticality_do_not_kill(self):
        result = assess_target(
            request(
                [
                    claim(
                        claim_ref="external:claim/liver-surface",
                        axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        surface_exposed=True,
                        hazard_context_ref="external:hazard/liver",
                    ),
                    claim(
                        claim_ref="external:claim/heart-critical",
                        axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                        level=EvidenceLevel.B,
                        direction=RiskDirection.SUPPORTS_RISK,
                        criticality=Criticality.CRITICAL_NON_REGENERATIVE,
                        hazard_context_ref="external:hazard/heart",
                    ),
                ]
            )
        )
        self.assertNotIn("critical_surface_hazard", [flag.value for flag in result.fatal_flags])
        self.assertEqual(result.decision, Decision.HOLD)

    def test_unrelated_differential_does_not_cover_material_risk(self):
        claims = complete_resolved_claims()
        claims[1] = claim(
            claim_ref="external:claim/unrelated-differential",
            axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
            level=EvidenceLevel.B,
            direction=RiskDirection.SUPPORTS_SAFETY,
            surface_exposed=False,
            differential_status=DifferentialStatus.PRESENT,
            hazard_context_ref="external:hazard/gut",
        )
        claims.append(
            claim(
                claim_ref="external:claim/heart-material-risk",
                axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                level=EvidenceLevel.B,
                direction=RiskDirection.SUPPORTS_RISK,
                criticality=Criticality.CRITICAL_NON_REGENERATIVE,
                hazard_context_ref="external:hazard/heart",
            )
        )
        result = assess_target(request(claims))
        self.assertEqual(result.decision, Decision.HOLD)

    def test_partial_differential_coverage_does_not_conditionally_go(self):
        claims = complete_resolved_claims()
        claims[1] = claim(
            claim_ref="external:claim/covered-differential",
            axis=EvidenceAxis.SURFACE_ACCESSIBILITY,
            level=EvidenceLevel.B,
            direction=RiskDirection.SUPPORTS_SAFETY,
            surface_exposed=False,
            differential_status=DifferentialStatus.PRESENT,
            hazard_context_ref="external:hazard/shared",
            mitigates_claim_refs=("external:claim/risk-a",),
        )
        claims.extend(
            [
                claim(
                    claim_ref="external:claim/risk-a",
                    axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                    level=EvidenceLevel.B,
                    direction=RiskDirection.SUPPORTS_RISK,
                    criticality=Criticality.REGENERATIVE,
                    hazard_context_ref="external:hazard/shared",
                ),
                claim(
                    claim_ref="external:claim/risk-b",
                    axis=EvidenceAxis.NORMAL_TISSUE_EXPRESSION,
                    level=EvidenceLevel.B,
                    direction=RiskDirection.SUPPORTS_RISK,
                    criticality=Criticality.REGENERATIVE,
                    hazard_context_ref="external:hazard/other",
                ),
            ]
        )
        result = assess_target(request(claims))
        self.assertEqual(result.decision, Decision.HOLD)

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
