import unittest

from src.cross_cutting.ip_fto_due_diligence_portfolio import (
    DUE_DILIGENCE_STAGES,
    DueDiligenceRequest,
    IPFTORequest,
    PortfolioRequest,
)


class Phase6CrossCuttingTests(unittest.TestCase):
    def test_due_diligence_is_stage_aware(self):
        self.assertEqual(len(DUE_DILIGENCE_STAGES), 4)
        request = DueDiligenceRequest(
            asset_ref="external:asset/1",
            lifecycle_stage="asset_generation",
            question_set_ref="external:questions/1",
            evidence_scope_ref="external:evidence/1",
            run_context_ref="external:run/1",
        )
        self.assertEqual(request.lifecycle_stage, "asset_generation")

    def test_services_reject_local_references(self):
        with self.assertRaises(ValueError):
            IPFTORequest("local:asset/1", "external:j/1", "external:c/1", "external:e/1", "external:r/1")
        with self.assertRaises(ValueError):
            PortfolioRequest(("external:asset/1", "local:asset/2"), "external:p/1", "external:c/1", "external:risk/1", "external:run/1")

    def test_due_diligence_rejects_unknown_stage(self):
        with self.assertRaises(ValueError):
            DueDiligenceRequest("external:asset/1", "unknown", "external:q/1", "external:e/1", "external:r/1")


if __name__ == "__main__":
    unittest.main()
