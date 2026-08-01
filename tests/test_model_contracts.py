import unittest

from src.cross_cutting.model_contracts import (
    MODEL_LIFECYCLE_STANDARD_REF,
    ModelGovernanceRequest,
    ModelLifecycleDescriptor,
    ModelRef,
    parse_model_ref,
)


class ModelContractTests(unittest.TestCase):
    def test_parse_model_ref_matches_assetgenos_identity_rule(self):
        self.assertEqual(
            parse_model_ref("binder-ranker@1.2.3"),
            ("binder-ranker", "1.2.3"),
        )
        self.assertIsNone(parse_model_ref("binder-ranker@1.2"))
        self.assertIsNone(parse_model_ref("binder-ranker@01.2.3"))

    def test_lifecycle_descriptor_binds_frozen_standard(self):
        model_ref = ModelRef("binder-ranker", "1.2.3")
        descriptor = ModelLifecycleDescriptor(model_ref, artifact_stage="validated")
        self.assertEqual(descriptor.standard_ref, MODEL_LIFECYCLE_STANDARD_REF)
        with self.assertRaises(ValueError):
            ModelLifecycleDescriptor(model_ref, standard_ref="OtherStandard@1.0.0")

    def test_governance_is_an_external_request(self):
        request = ModelGovernanceRequest(
            ModelRef("binder-ranker", "1.2.3"),
            "inspect",
            "external-review-ref",
        )
        self.assertEqual(request.operation, "inspect")
        with self.assertRaises(ValueError):
            ModelGovernanceRequest(request.model_ref, "promote", "review-ref")


if __name__ == "__main__":
    unittest.main()
