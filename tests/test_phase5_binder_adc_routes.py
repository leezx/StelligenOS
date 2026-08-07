import ast
import dataclasses
import pathlib
import unittest

import yaml

from src.capabilities.binder_adc_routes import (
    BinderAdcRouteRequest,
    BinderAdcRouteResult,
    EPITOPE_DE_NOVO_ROUTE,
    EXISTING_BINDER_ROUTE,
    REQUIRED_REQUEST_REFERENCE_FIELDS,
    ROUTE_IDS,
    SPONSOR_CONTROL_REQUEST_FIELDS,
    route_stages,
)

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
CAPABILITY_SOURCE = REPOSITORY_ROOT / "src" / "capabilities" / "binder_adc_routes.py"
CONTRACT_PATH = REPOSITORY_ROOT / "src" / "contracts" / "binder_adc_routes.yaml"

VALID_REQUEST_FIELDS = {
    "route_id": EXISTING_BINDER_ROUTE,
    "input_ref": "external:input/1",
    "opportunity_ref": "external:opportunity/1",
    "policy_ref": "external:policy/1",
    "tool_environment_ref": "external:tools/1",
    "run_context_ref": "external:run/1",
    "program_commitment_review_ref": "external:program-commitment-review/1",
    "value_inflection_plan_ref": "external:value-inflection-plan/1",
    "asset_generation_authorization_ref": "external:human-handoff/asset-generation/1",
}


def _request(**overrides):
    """Build a fully external request, overriding named fields."""

    return BinderAdcRouteRequest(**{**VALID_REQUEST_FIELDS, **overrides})


def _repository_tree() -> set[str]:
    """Snapshot tracked-scope paths, ignoring VCS and interpreter caches."""

    paths = set()
    for path in REPOSITORY_ROOT.rglob("*"):
        parts = path.relative_to(REPOSITORY_ROOT).parts
        if ".git" in parts or "__pycache__" in parts:
            continue
        paths.add(str(path.relative_to(REPOSITORY_ROOT)))
    return paths


class Phase5BinderAdcRouteTests(unittest.TestCase):
    def test_two_routes_and_frozen_stage_counts(self):
        self.assertEqual(len(ROUTE_IDS), 2)
        self.assertEqual(len(route_stages(EXISTING_BINDER_ROUTE)), 14)
        self.assertEqual(len(route_stages(EPITOPE_DE_NOVO_ROUTE)), 15)

    def test_route_request_requires_external_references(self):
        with self.assertRaises(ValueError):
            _request(input_ref="local:input/1")

    def test_route_result_requires_external_references(self):
        with self.assertRaises(ValueError):
            BinderAdcRouteResult(
                route_id=EPITOPE_DE_NOVO_ROUTE,
                run_ref="external:run/1",
                package_ref="local:package/1",
                candidate_refs=(),
                report_ref="external:report/1",
            )


class SponsorControlBindingTests(unittest.TestCase):
    """The Phase 3-4 hard controls must bind at request construction time."""

    def test_request_contract_version_records_the_breaking_change(self):
        self.assertEqual(_request().contract_version, "0.2.0")

    def test_result_envelope_is_unchanged(self):
        result = BinderAdcRouteResult(
            route_id=EXISTING_BINDER_ROUTE,
            run_ref="external:run/1",
            package_ref="external:package/1",
            candidate_refs=(),
            report_ref="external:report/1",
        )
        self.assertEqual(result.contract_version, "0.1.0")

    def test_missing_program_commitment_review_ref_cannot_construct_request(self):
        fields = dict(VALID_REQUEST_FIELDS)
        del fields["program_commitment_review_ref"]
        with self.assertRaises(TypeError):
            BinderAdcRouteRequest(**fields)

    def test_missing_value_inflection_plan_ref_cannot_construct_request(self):
        fields = dict(VALID_REQUEST_FIELDS)
        del fields["value_inflection_plan_ref"]
        with self.assertRaises(TypeError):
            BinderAdcRouteRequest(**fields)

    def test_missing_asset_generation_authorization_ref_cannot_construct_request(self):
        fields = dict(VALID_REQUEST_FIELDS)
        del fields["asset_generation_authorization_ref"]
        with self.assertRaises(TypeError):
            BinderAdcRouteRequest(**fields)

    def test_no_sponsor_control_field_has_a_default(self):
        """A default would silently reintroduce the unenforced control."""

        for field_name in SPONSOR_CONTROL_REQUEST_FIELDS:
            with self.subTest(field=field_name):
                field = BinderAdcRouteRequest.__dataclass_fields__[field_name]
                self.assertIs(field.default, dataclasses.MISSING)
                self.assertIs(field.default_factory, dataclasses.MISSING)

    def test_the_three_bound_refs_are_named_literally(self):
        """Named literally so the parameterised tests below cannot self-shrink."""

        self.assertEqual(
            SPONSOR_CONTROL_REQUEST_FIELDS,
            (
                "program_commitment_review_ref",
                "value_inflection_plan_ref",
                "asset_generation_authorization_ref",
            ),
        )

    def test_local_program_commitment_review_ref_is_rejected(self):
        with self.assertRaises(ValueError):
            _request(program_commitment_review_ref="local:program-commitment-review/1")

    def test_local_value_inflection_plan_ref_is_rejected(self):
        with self.assertRaises(ValueError):
            _request(value_inflection_plan_ref="local:value-inflection-plan/1")

    def test_local_asset_generation_authorization_ref_is_rejected(self):
        with self.assertRaises(ValueError):
            _request(asset_generation_authorization_ref="local:human-handoff/1")

    def test_local_references_are_rejected_for_every_sponsor_control_field(self):
        for field_name in SPONSOR_CONTROL_REQUEST_FIELDS:
            with self.subTest(field=field_name):
                with self.assertRaises(ValueError):
                    _request(**{field_name: "local:instance/1"})

    def test_every_required_reference_field_is_validated_uniformly(self):
        """All eight references now share one loop; none may be bare or local."""

        self.assertEqual(
            REQUIRED_REQUEST_REFERENCE_FIELDS,
            (
                "input_ref",
                "opportunity_ref",
                "program_commitment_review_ref",
                "value_inflection_plan_ref",
                "asset_generation_authorization_ref",
                "policy_ref",
                "tool_environment_ref",
                "run_context_ref",
            ),
        )
        class LooksExternal:
            """Non-str whose text form would pass a coercing check."""

            def __str__(self):
                return "external:impostor/1"

        for field_name in REQUIRED_REQUEST_REFERENCE_FIELDS:
            for value in (
                "",
                "external:",
                "external:   ",
                "local:x/1",
                1,
                None,
                LooksExternal(),
            ):
                with self.subTest(field=field_name, value=repr(value)):
                    with self.assertRaises(ValueError):
                        _request(**{field_name: value})

    def test_fully_external_request_is_accepted_for_both_routes(self):
        for route_id in ROUTE_IDS:
            with self.subTest(route=route_id):
                request = _request(route_id=route_id)
                self.assertEqual(request.route_id, route_id)
                self.assertEqual(
                    request.program_commitment_review_ref,
                    "external:program-commitment-review/1",
                )
                self.assertEqual(
                    request.value_inflection_plan_ref,
                    "external:value-inflection-plan/1",
                )
                self.assertEqual(
                    request.asset_generation_authorization_ref,
                    "external:human-handoff/asset-generation/1",
                )

    def test_a_request_cannot_start_a_route_by_itself(self):
        """Holding a valid request must not be a way to execute one."""

        request = _request()
        for attribute in dir(request):
            if attribute.startswith("_"):
                continue
            self.assertFalse(
                callable(getattr(request, attribute)),
                f"request exposes callable {attribute!r}",
            )

    def test_constructing_a_request_creates_no_result(self):
        """A satisfied precondition is not a run: no result may come into being."""

        created = []
        original_post_init = BinderAdcRouteResult.__post_init__

        def spy_post_init(self):  # pragma: no cover - must never be reached
            created.append(self)
            original_post_init(self)

        BinderAdcRouteResult.__post_init__ = spy_post_init
        try:
            _request()
        finally:
            BinderAdcRouteResult.__post_init__ = original_post_init
        self.assertEqual(created, [])

    def test_constructing_a_request_does_not_advance_lifecycle(self):
        from src.lifecycle import clinical_lock, state_machine

        def snapshot():
            return {
                (module.__name__, name): repr(getattr(module, name))
                for module in (state_machine, clinical_lock)
                for name in dir(module)
                if not name.startswith("_")
            }

        before = snapshot()
        for route_id in ROUTE_IDS:
            _request(route_id=route_id)
        self.assertEqual(snapshot(), before)

    def test_constructing_a_request_writes_no_repository_state(self):
        before = _repository_tree()
        for route_id in ROUTE_IDS:
            _request(route_id=route_id)
        self.assertEqual(_repository_tree(), before)

    def test_request_is_frozen_and_carries_no_resolved_instance(self):
        request = _request()
        with self.assertRaises(Exception):
            request.asset_generation_authorization_ref = "external:other/1"
        for field_name in SPONSOR_CONTROL_REQUEST_FIELDS:
            self.assertIsInstance(getattr(request, field_name), str)

    def test_capability_module_imports_no_contract_or_lifecycle_symbol(self):
        """Binding must not pull external instances back into the kernel."""

        tree = ast.parse(CAPABILITY_SOURCE.read_text(encoding="utf-8"))
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        self.assertEqual(modules, {"dataclasses", "typing"})

    def test_contract_yaml_declares_the_binding(self):
        contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))["contract"]
        self.assertEqual(contract["request_contract_version"], "0.2.0")
        self.assertEqual(contract["result_contract_version"], "0.1.0")
        binding = contract["sponsor_control_binding"]
        self.assertEqual(
            tuple(binding["required_request_refs"]), SPONSOR_CONTROL_REQUEST_FIELDS
        )
        self.assertEqual(
            tuple(binding["required_request_reference_fields"]),
            REQUIRED_REQUEST_REFERENCE_FIELDS,
        )
        self.assertEqual(
            binding["bound_contracts"],
            {
                "program_commitment_review": "ProgramCommitmentReview@0.2.0",
                "value_inflection_plan": "ValueInflectionPlan@0.1.0",
            },
        )
        for forbidden_key in (
            "authorization_read_by_repository",
            "authorization_re_adjudicated_by_repository",
            "authorization_generated_by_repository",
            "contract_class_import_by_capability",
            "external_instance_materialisation",
        ):
            self.assertEqual(binding[forbidden_key], "forbidden")


if __name__ == "__main__":
    unittest.main()
