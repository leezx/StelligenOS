import pathlib
import unittest

import yaml

from src.contracts.sponsor_fit_assessment import (
    ASSET_DIRECTED_ROUTES,
    ROUTE_REQUIREMENTS,
    CapabilityAvailability,
    CapabilityMapEntry,
    QuestionStatus,
    ResourceMapEntry,
    SPONSOR_FIT_QUESTIONS,
    SponsorFitAssessment,
    SponsorFitQuestionResult,
    SponsorFitRoute,
)

CONTRACT_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "src"
    / "contracts"
    / "sponsor_fit_assessment.yaml"
)


def _questions(**overrides):
    """Seven answers, SATISFIED by default, overridden by question id."""

    return tuple(
        SponsorFitQuestionResult(
            question_id=question,
            status=overrides.get(question, QuestionStatus.SATISFIED),
            evidence_ref=f"external:evidence/{question}",
        )
        for question in SPONSOR_FIT_QUESTIONS
    )


def _capability_map():
    return (
        CapabilityMapEntry(
            capability_id="spatial_multiomics",
            availability=CapabilityAvailability.OWNED,
            evidence_ref="external:capability/spatial",
        ),
        CapabilityMapEntry(
            capability_id="adc_conjugation",
            availability=CapabilityAvailability.COLLABORATIVE,
            evidence_ref="external:capability/conjugation",
        ),
    )


def _resource_map():
    return (
        ResourceMapEntry(
            uncertainty_ref="external:uncertainty/post-treatment-retention",
            experiment_ref="external:experiment/paired-biopsy-surface",
            decision_changed_ref="external:decision/target-state-retained",
            cost_band_ref="external:cost-band/small",
            capability_source=CapabilityAvailability.OWNED,
            failure_consequence_ref="external:consequence/stop-program",
        ),
    )


def _assessment(**overrides):
    fields = {
        "assessment_id": "SFA-CRC-001",
        "program_thesis_ref": "external:program-thesis/1",
        "sponsor_profile_ref": "external:sponsor-profile/stelligen",
        "scientific_opportunity_ref": "external:t12/opportunity/1",
        "question_results": _questions(),
        "capability_map": _capability_map(),
        "resource_map": _resource_map(),
        "differentiation_requires_phase_3": False,
        "route": SponsorFitRoute.SELF_DEVELOP,
        "route_policy_ref": "external:policy/sponsor-fit/v1",
        "rationale_ref": "external:rationale/1",
        "human_decision_ref": "external:human-decision/1",
        "source_refs": ("external:source/1",),
    }
    fields.update(overrides)
    return SponsorFitAssessment(**fields)


class SponsorFitShapeTests(unittest.TestCase):
    def test_seven_mandatory_questions_are_frozen_by_name(self):
        self.assertEqual(
            SPONSOR_FIT_QUESTIONS,
            (
                "evidence_advantage",
                "capability_fit",
                "capital_fit",
                "time_fit",
                "differentiation_visibility",
                "ip_capture",
                "partnerability",
            ),
        )

    def test_a_fully_external_assessment_is_accepted(self):
        assessment = _assessment()
        self.assertEqual(assessment.route, SponsorFitRoute.SELF_DEVELOP)
        self.assertEqual(len(assessment.question_results), 7)

    def test_every_route_value_is_available(self):
        self.assertEqual(
            tuple(route.value for route in SponsorFitRoute),
            (
                "SELF_DEVELOP",
                "CO_DEVELOP",
                "DATA_PACKAGE_ONLY",
                "PARTNER_NOW",
                "MONITOR",
                "STOP_FOR_SPONSOR",
            ),
        )

    def test_a_missing_question_is_rejected(self):
        with self.assertRaises(ValueError):
            _assessment(question_results=_questions()[:-1])

    def test_a_duplicated_question_is_rejected(self):
        answers = _questions()
        with self.assertRaises(ValueError):
            _assessment(question_results=answers[:-1] + (answers[0],))

    def test_an_unknown_question_id_is_rejected(self):
        with self.assertRaises(ValueError):
            SponsorFitQuestionResult(
                question_id="vibe_check",
                status=QuestionStatus.SATISFIED,
                evidence_ref="external:evidence/x",
            )

    def test_local_references_are_rejected_everywhere(self):
        for field in (
            "program_thesis_ref",
            "sponsor_profile_ref",
            "scientific_opportunity_ref",
            "route_policy_ref",
            "rationale_ref",
            "human_decision_ref",
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    _assessment(**{field: "local:x/1"})
        with self.assertRaises(ValueError):
            _assessment(source_refs=("local:source/1",))
        with self.assertRaises(ValueError):
            SponsorFitQuestionResult(
                question_id="ip_capture",
                status=QuestionStatus.SATISFIED,
                evidence_ref="local:evidence/1",
            )

    def test_capability_and_resource_maps_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            _assessment(capability_map=())
        with self.assertRaises(ValueError):
            _assessment(resource_map=())

    def test_resource_map_entry_requires_every_external_reference(self):
        for field in (
            "uncertainty_ref",
            "experiment_ref",
            "decision_changed_ref",
            "cost_band_ref",
            "failure_consequence_ref",
        ):
            with self.subTest(field=field):
                fields = {
                    "uncertainty_ref": "external:u/1",
                    "experiment_ref": "external:e/1",
                    "decision_changed_ref": "external:d/1",
                    "cost_band_ref": "external:c/1",
                    "capability_source": CapabilityAvailability.OWNED,
                    "failure_consequence_ref": "external:f/1",
                }
                fields[field] = "local:x/1"
                with self.assertRaises(ValueError):
                    ResourceMapEntry(**fields)


class SponsorFitDecisionRuleTests(unittest.TestCase):
    """The rules that make this checkpoint mean something."""

    def test_no_aggregate_score_field_exists(self):
        """The source note is explicit: no total score here."""

        for field_name in SponsorFitAssessment.__dataclass_fields__:
            self.assertNotIn(
                field_name,
                {"score", "total_score", "fit_score", "weighted_score", "rating"},
            )
            self.assertFalse(
                field_name.endswith("_score"), f"{field_name} looks like a score"
            )

    def test_self_develop_requires_affirmative_evidence_on_six_questions(self):
        for question in (
            "evidence_advantage",
            "capability_fit",
            "capital_fit",
            "time_fit",
            "differentiation_visibility",
            "ip_capture",
        ):
            for status in (QuestionStatus.UNKNOWN, QuestionStatus.UNSATISFIED):
                with self.subTest(question=question, status=status):
                    with self.assertRaises(ValueError):
                        _assessment(
                            question_results=_questions(**{question: status}),
                            route=SponsorFitRoute.SELF_DEVELOP,
                        )

    def test_self_develop_leaves_partnerability_free(self):
        """A programme may plan to keep funding independently."""

        for status in QuestionStatus:
            with self.subTest(status=status):
                assessment = _assessment(
                    question_results=_questions(partnerability=status),
                    route=SponsorFitRoute.SELF_DEVELOP,
                )
                self.assertEqual(assessment.route, SponsorFitRoute.SELF_DEVELOP)

    def test_no_waiver_mechanism_exists(self):
        """A case-by-case waiver would be a back door around this checkpoint."""

        self.assertNotIn(
            "asymmetric_advantage_waiver_ref",
            SponsorFitAssessment.__dataclass_fields__,
        )
        for field_name in SponsorFitAssessment.__dataclass_fields__:
            self.assertNotIn("waiver", field_name)
        with self.assertRaises(TypeError):
            _assessment(asymmetric_advantage_waiver_ref="external:waiver/1")

    def test_co_develop_requires_something_worth_partnering_on(self):
        for question in (
            "evidence_advantage",
            "differentiation_visibility",
            "partnerability",
        ):
            for status in (QuestionStatus.UNKNOWN, QuestionStatus.UNSATISFIED):
                with self.subTest(question=question, status=status):
                    with self.assertRaises(ValueError):
                        _assessment(
                            question_results=_questions(**{question: status}),
                            route=SponsorFitRoute.CO_DEVELOP,
                        )

    def test_co_develop_tolerates_capability_and_capital_uncertainty(self):
        """A partner is exactly what would resolve those two."""

        assessment = _assessment(
            question_results=_questions(
                capability_fit=QuestionStatus.UNKNOWN,
                capital_fit=QuestionStatus.UNKNOWN,
            ),
            route=SponsorFitRoute.CO_DEVELOP,
        )
        self.assertEqual(assessment.route, SponsorFitRoute.CO_DEVELOP)

    def test_co_develop_rejects_an_unsatisfied_ip_path(self):
        with self.assertRaises(ValueError):
            _assessment(
                question_results=_questions(ip_capture=QuestionStatus.UNSATISFIED),
                route=SponsorFitRoute.CO_DEVELOP,
            )

    def test_co_develop_tolerates_an_unknown_ip_path(self):
        assessment = _assessment(
            question_results=_questions(ip_capture=QuestionStatus.UNKNOWN),
            route=SponsorFitRoute.CO_DEVELOP,
        )
        self.assertEqual(assessment.route, SponsorFitRoute.CO_DEVELOP)

    def test_partner_now_requires_partnerability(self):
        for status in (QuestionStatus.UNKNOWN, QuestionStatus.UNSATISFIED):
            with self.subTest(status=status):
                with self.assertRaises(ValueError):
                    _assessment(
                        question_results=_questions(partnerability=status),
                        route=SponsorFitRoute.PARTNER_NOW,
                    )

    def test_partner_now_requires_something_to_take_to_a_partner(self):
        with self.assertRaises(ValueError):
            _assessment(
                question_results=_questions(
                    evidence_advantage=QuestionStatus.UNKNOWN,
                    differentiation_visibility=QuestionStatus.UNKNOWN,
                ),
                route=SponsorFitRoute.PARTNER_NOW,
            )
        for present in ("evidence_advantage", "differentiation_visibility"):
            with self.subTest(present=present):
                absent = (
                    "differentiation_visibility"
                    if present == "evidence_advantage"
                    else "evidence_advantage"
                )
                assessment = _assessment(
                    question_results=_questions(**{absent: QuestionStatus.UNKNOWN}),
                    route=SponsorFitRoute.PARTNER_NOW,
                )
                self.assertEqual(assessment.route, SponsorFitRoute.PARTNER_NOW)

    def test_a_mostly_unknown_assessment_cannot_reach_a_committed_route(self):
        """The core fix: absence of a negative is not evidence of fit."""

        all_unknown = _questions(
            **{question: QuestionStatus.UNKNOWN for question in SPONSOR_FIT_QUESTIONS}
        )
        for route in (
            SponsorFitRoute.SELF_DEVELOP,
            SponsorFitRoute.CO_DEVELOP,
            SponsorFitRoute.PARTNER_NOW,
        ):
            with self.subTest(route=route):
                with self.assertRaises(ValueError):
                    _assessment(question_results=all_unknown, route=route)

    def test_unknown_is_not_failure_and_never_auto_kills(self):
        """All-UNKNOWN is a valid assessment; it just cannot commit resources."""

        all_unknown = _questions(
            **{question: QuestionStatus.UNKNOWN for question in SPONSOR_FIT_QUESTIONS}
        )
        for route in (
            SponsorFitRoute.MONITOR,
            SponsorFitRoute.DATA_PACKAGE_ONLY,
            SponsorFitRoute.STOP_FOR_SPONSOR,
        ):
            with self.subTest(route=route):
                assessment = _assessment(question_results=all_unknown, route=route)
                self.assertEqual(assessment.route, route)

    def test_phase_3_only_differentiation_cannot_be_satisfied(self):
        with self.assertRaises(ValueError):
            _assessment(
                differentiation_requires_phase_3=True,
                question_results=_questions(
                    differentiation_visibility=QuestionStatus.SATISFIED
                ),
            )

    def test_phase_3_only_differentiation_is_fine_when_not_claimed_visible(self):
        assessment = _assessment(
            differentiation_requires_phase_3=True,
            question_results=_questions(
                differentiation_visibility=QuestionStatus.UNKNOWN
            ),
            route=SponsorFitRoute.PARTNER_NOW,
        )
        self.assertTrue(assessment.differentiation_requires_phase_3)


class SponsorFitBoundaryTests(unittest.TestCase):
    def test_constructing_an_assessment_grants_no_commitment(self):
        """An assessment is a recommendation; it exposes no authorisation."""

        assessment = _assessment()
        for attribute in dir(assessment):
            if attribute.startswith("_"):
                continue
            self.assertFalse(callable(getattr(assessment, attribute)))
        self.assertNotIn("commitment_status", SponsorFitAssessment.__dataclass_fields__)
        self.assertNotIn("downstream_status", SponsorFitAssessment.__dataclass_fields__)

    def test_module_does_not_import_the_commitment_or_gate_layers(self):
        import ast

        source = (
            pathlib.Path(__file__).resolve().parents[1]
            / "src"
            / "contracts"
            / "sponsor_fit_assessment.py"
        ).read_text(encoding="utf-8")
        modules = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        self.assertEqual(modules, {"__future__", "dataclasses", "enum", "typing"})

    def test_contract_yaml_matches_the_code(self):
        contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            tuple(contract["mandatory_questions"]), SPONSOR_FIT_QUESTIONS
        )
        self.assertEqual(
            tuple(contract["route_values"]),
            tuple(route.value for route in SponsorFitRoute),
        )
        self.assertEqual(
            tuple(contract["question_status_values"]),
            tuple(status.value for status in QuestionStatus),
        )
        self.assertEqual(
            tuple(contract["capability_availability_values"]),
            tuple(value.value for value in CapabilityAvailability),
        )
        self.assertEqual(contract["contract"]["aggregate_score"], "forbidden")
        self.assertEqual(
            contract["downstream_relationship"]["binding_status"], "bound"
        )
        self.assertEqual(
            contract["downstream_relationship"]["consumed_by"],
            "ProgramCommitmentReview@0.2.0",
        )

    def test_contract_declares_the_invariants_that_carry_the_meaning(self):
        contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
        invariants = set(contract["contract"]["invariants"])
        for required in (
            "no_aggregate_score_is_computed_or_stored",
            "unknown_is_not_failure",
            "unknown_never_auto_kills",
            "critical_unknowns_block_asset_directed_routes_until_resolved",
            "route_eligibility_is_affirmative_not_absence_of_negative",
            "self_develop_requires_affirmative_sponsor_fit_evidence",
            "no_waiver_mechanism_exists_for_sponsor_fit",
            "differentiation_requiring_phase_3_is_not_visible_differentiation",
            "assessment_does_not_grant_program_commitment",
            "stop_for_sponsor_is_not_scientific_kill",
            "route_is_a_recommendation_not_an_authorisation",
        ):
            self.assertIn(required, invariants)
        self.assertNotIn("unknown_alone_does_not_block_a_route", invariants)

    def test_contract_yaml_route_eligibility_matches_the_code(self):
        contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
        declared = contract["route_eligibility"]
        self.assertEqual(
            set(declared), {route.value for route in SponsorFitRoute}
        )
        for route, requirement in ROUTE_REQUIREMENTS.items():
            with self.subTest(route=route):
                entry = declared[route.value]
                self.assertEqual(
                    tuple(entry["must_be_satisfied"]), requirement.must_be_satisfied
                )
                self.assertEqual(
                    tuple(entry["must_not_be_unsatisfied"]),
                    requirement.must_not_be_unsatisfied,
                )
                self.assertEqual(
                    tuple(entry["at_least_one_satisfied"]),
                    requirement.at_least_one_satisfied,
                )
        self.assertEqual(contract["contract"]["waiver_mechanism"], "none")
        self.assertEqual(contract["contract"]["optional_fields"], [])

    def test_every_asset_directed_route_demands_affirmative_evidence(self):
        """No asset-directed route may be reachable with an empty requirement."""

        for route in ASSET_DIRECTED_ROUTES:
            with self.subTest(route=route):
                self.assertTrue(ROUTE_REQUIREMENTS[route].must_be_satisfied)


if __name__ == "__main__":
    unittest.main()
