import unittest

from src.capabilities.opportunity_generation import (
    OpportunityGenerationRequest,
    require_external_reference,
)


class Phase4OpportunityGenerationTests(unittest.TestCase):
    def test_request_is_reference_based(self):
        request = OpportunityGenerationRequest(
            request_id="external:request/1",
            knowledge_scope_ref="external:knowledge/1",
            target_context_ref="external:target/1",
            clinical_context_ref="external:clinical/1",
            generation_policy_ref="external:policy/1",
            run_context_ref="external:run/1",
        )
        self.assertTrue(request.request_id.startswith("external:"))
        self.assertTrue(request.knowledge_scope_ref.startswith("external:"))

    def test_local_reference_is_rejected(self):
        with self.assertRaises(ValueError):
            require_external_reference("local:opportunity/1")

        with self.assertRaises(ValueError):
            OpportunityGenerationRequest(
                request_id="external:request/1",
                knowledge_scope_ref="local:knowledge/1",
                target_context_ref="external:target/1",
                clinical_context_ref="external:clinical/1",
                generation_policy_ref="external:policy/1",
                run_context_ref="external:run/1",
            )

    def test_external_reference_is_accepted(self):
        self.assertEqual(
            require_external_reference("external:opportunity/1"),
            "external:opportunity/1",
        )


if __name__ == "__main__":
    unittest.main()
