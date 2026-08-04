import unittest

from src.cross_cutting.knowledge_ledger import LedgerEntryRequest
from src.lifecycle.state_machine import (
    LifecycleStage,
    can_transition,
)
from src.objects.core import CORE_OBJECT_TYPES, CoreObject


class Phase2ContractTests(unittest.TestCase):
    def test_core_object_registry_matches_frozen_contract(self):
        self.assertEqual(
            CORE_OBJECT_TYPES,
            (
                "Opportunity",
                "ClinicalHypothesis",
                "TargetHypothesis",
                "BinderCandidate",
                "ADCConstruct",
                "LeadSeries",
                "DevelopmentCandidate",
                "Asset",
            ),
        )

    def test_core_object_requires_identity(self):
        object_definition = CoreObject("Opportunity", "example-id", "1.0")
        self.assertEqual(object_definition.object_type, "Opportunity")
        with self.assertRaises(ValueError):
            CoreObject("Unknown", "example-id", "1.0")

    def test_lifecycle_is_forward_only(self):
        self.assertTrue(
            can_transition(
                LifecycleStage.OPPORTUNITY_GENERATION,
                LifecycleStage.OPPORTUNITY_VALIDATION,
            )
        )
        self.assertFalse(
            can_transition(
                LifecycleStage.ASSET_DEVELOPMENT,
                LifecycleStage.OPPORTUNITY_GENERATION,
            )
        )

    def test_ledger_request_is_only_a_port_request(self):
        request = LedgerEntryRequest("evidence", "subject-id", "1.0")
        self.assertEqual(request.subject_id, "subject-id")


if __name__ == "__main__":
    unittest.main()
