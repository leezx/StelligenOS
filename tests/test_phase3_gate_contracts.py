import unittest

from src.capabilities.gates import (
    GATE_CATALOG,
    GATE_GROUPS,
    GATE_IDS,
    GateInputEnvelope,
    ClinicalLockState,
    gate_definition,
)


class Phase3GateContractTests(unittest.TestCase):
    def test_frozen_catalog_has_three_groups_and_45_unique_gates(self):
        self.assertEqual(GATE_GROUPS, (
            "target_opportunity",
            "product_realization",
            "commercial_executability",
        ))
        self.assertEqual(len(GATE_IDS), 45)
        self.assertEqual(len(set(GATE_IDS)), 45)
        self.assertEqual(len(GATE_CATALOG), 45)

    def test_catalog_sequences_are_contiguous_and_lookup_is_stable(self):
        self.assertEqual([item.sequence for item in GATE_CATALOG], list(range(45)))
        self.assertEqual(gate_definition("clinical_context_endpoint").sequence, 0)
        self.assertEqual(gate_definition("product_design_objective").sequence, 13)
        self.assertEqual(gate_definition("transaction_readiness").sequence, 44)

    def test_input_envelope_contains_external_references_only(self):
        envelope = GateInputEnvelope(
            candidate_ref="external:candidate/1",
            target_opportunity_ref="external:opportunity/1",
            adc_product_candidate_ref="external:adc/1",
            commercial_execution_context_ref="external:commercial/1",
            evidence_refs=("external:evidence/1",),
            upstream_result_refs={},
            graph_context_ref="external:graph/1",
            run_context_ref="external:run/1",
        )
        self.assertTrue(all(value.startswith("external:") for value in (
            envelope.candidate_ref,
            envelope.target_opportunity_ref,
            envelope.adc_product_candidate_ref,
            envelope.commercial_execution_context_ref,
            envelope.graph_context_ref,
            envelope.run_context_ref,
        )))

    def test_unknown_gate_is_rejected(self):
        with self.assertRaises(KeyError):
            gate_definition("not_a_real_gate")

    def test_t0_extension_requires_typed_state_and_hypothesis_ref(self):
        with self.assertRaises(ValueError):
            GateInputEnvelope(
                "external:candidate/1", "external:opportunity/1", "external:adc/1",
                "external:commercial/1", (), {}, "external:graph/1", "external:run/1",
                "2.1.0", None, None, None, None, None, "invalid",
            )
        with self.assertRaises(ValueError):
            GateInputEnvelope(
                "external:candidate/1", "external:opportunity/1", "external:adc/1",
                "external:commercial/1", (), {}, "external:graph/1", "external:run/1",
                "2.1.0", None, None, None, None, None, ClinicalLockState.PROVISIONAL,
            )

    def test_t0_extension_keeps_contract_version_before_new_fields(self):
        envelope = GateInputEnvelope(
            "external:candidate/1", "external:opportunity/1", "external:adc/1",
            "external:commercial/1", (), {}, "external:graph/1", "external:run/1",
            "2.1.0", "external:clinical-hypothesis/1", "external:anchor/1",
            "external:benefit/1", "external:biomarker/1", "external:product/1",
            ClinicalLockState.PROVISIONAL,
        )
        self.assertEqual(envelope.contract_version, "2.1.0")


if __name__ == "__main__":
    unittest.main()
