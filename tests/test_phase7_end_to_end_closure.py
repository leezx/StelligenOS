import unittest

from src.repository.end_to_end_closure import CLOSURE_STAGES, ClosureRequest, DEMO_ASSET_REF


class Phase7EndToEndClosureTests(unittest.TestCase):
    def test_closure_covers_four_lifecycle_stages(self):
        self.assertEqual(len(CLOSURE_STAGES), 4)
        request = ClosureRequest(DEMO_ASSET_REF, ("external:stage/1",), (), "external:run/1")
        self.assertEqual(request.demo_asset_ref, DEMO_ASSET_REF)

    def test_closure_rejects_local_refs(self):
        with self.assertRaises(ValueError):
            ClosureRequest("local:tweakr", (), (), "external:run/1")


if __name__ == "__main__":
    unittest.main()
