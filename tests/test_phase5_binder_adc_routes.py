import unittest

from src.capabilities.binder_adc_routes import (
    BinderAdcRouteRequest,
    BinderAdcRouteResult,
    EPITOPE_DE_NOVO_ROUTE,
    EXISTING_BINDER_ROUTE,
    ROUTE_IDS,
    route_stages,
)


class Phase5BinderAdcRouteTests(unittest.TestCase):
    def test_two_routes_and_frozen_stage_counts(self):
        self.assertEqual(len(ROUTE_IDS), 2)
        self.assertEqual(len(route_stages(EXISTING_BINDER_ROUTE)), 14)
        self.assertEqual(len(route_stages(EPITOPE_DE_NOVO_ROUTE)), 15)

    def test_route_request_requires_external_references(self):
        with self.assertRaises(ValueError):
            BinderAdcRouteRequest(
                route_id=EXISTING_BINDER_ROUTE,
                input_ref="local:input/1",
                opportunity_ref="external:opportunity/1",
                policy_ref="external:policy/1",
                tool_environment_ref="external:tools/1",
                run_context_ref="external:run/1",
            )

    def test_route_result_requires_external_references(self):
        with self.assertRaises(ValueError):
            BinderAdcRouteResult(
                route_id=EPITOPE_DE_NOVO_ROUTE,
                run_ref="external:run/1",
                package_ref="local:package/1",
                candidate_refs=(),
                report_ref="external:report/1",
            )


if __name__ == "__main__":
    unittest.main()
