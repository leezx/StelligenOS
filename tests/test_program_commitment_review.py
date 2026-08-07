import unittest
from pathlib import Path

import yaml

from src.contracts.program_commitment_review import (
    CommitmentStatus,
    DownstreamStatus,
    ProgramCommitmentDecision,
    ProgramCommitmentReview,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "src" / "contracts" / "program_commitment_review.yaml"


def refs(prefix: str) -> tuple[str, ...]:
    return (f"external:{prefix}/1",)


def review_kwargs() -> dict[str, object]:
    return {
        "review_id": "review-1",
        "program_thesis_ref": "external:program-thesis/1",
        "t12_decision_ref": "external:t12/1",
        "clinical_hypothesis_ref": "external:clinical-hypothesis/1",
        "target_hypothesis_ref": "external:target-hypothesis/1",
        "competition_landscape_ref": "external:competition/1",
        "ip_fto_ref": "external:ip-fto/1",
        "sponsor_profile_ref": "external:sponsor-profile/1",
        "capital_envelope_ref": "external:capital/1",
        "capability_gap_ref": "external:capability-gap/1",
        "buyer_map_ref": "external:buyer-map/1",
        "sponsor_fit_assessment_ref": "external:sponsor-fit-assessment/1",
        "value_inflection_plan_ref": "external:value-inflection-plan/1",
        "decision": ProgramCommitmentDecision.SELF_DEVELOP,
        "commitment_status": CommitmentStatus.COMMITTED,
        "downstream_status": DownstreamStatus.EXTERNAL_HANDOFF_REQUIRED,
        "decision_rationale_ref": "external:rationale/1",
        "condition_refs": refs("condition"),
        "source_refs": refs("source"),
        "human_decision_ref": "external:human-decision/1",
    }


class SponsorFitBindingTests(unittest.TestCase):
    """A commitment must not be reachable without a sponsor-fit assessment."""

    def test_commitment_cannot_be_constructed_without_sponsor_fit(self):
        kwargs = review_kwargs()
        del kwargs["sponsor_fit_assessment_ref"]
        with self.assertRaises(TypeError):
            ProgramCommitmentReview(**kwargs)

    def test_the_binding_field_has_no_default(self):
        """A default would silently reopen the route it closes."""

        import dataclasses

        field = ProgramCommitmentReview.__dataclass_fields__[
            "sponsor_fit_assessment_ref"
        ]
        self.assertIs(field.default, dataclasses.MISSING)
        self.assertIs(field.default_factory, dataclasses.MISSING)

    def test_a_local_sponsor_fit_reference_is_rejected(self):
        for value in ("local:sponsor-fit/1", "", "sponsor-fit/1"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ProgramCommitmentReview(
                        **{**review_kwargs(), "sponsor_fit_assessment_ref": value}
                    )

    def test_no_commitment_decision_bypasses_the_requirement(self):
        """Even STOP_FOR_SPONSOR must name the assessment it rests on."""

        for decision, status, downstream in (
            (ProgramCommitmentDecision.STOP_FOR_SPONSOR,
             CommitmentStatus.NOT_COMMITTED,
             DownstreamStatus.BLOCKED_NO_COMMITMENT),
            (ProgramCommitmentDecision.MONITOR,
             CommitmentStatus.NOT_COMMITTED,
             DownstreamStatus.BLOCKED_NO_COMMITMENT),
            (ProgramCommitmentDecision.CO_DEVELOP,
             CommitmentStatus.COMMITTED,
             DownstreamStatus.EXTERNAL_HANDOFF_REQUIRED),
        ):
            with self.subTest(decision=decision):
                kwargs = review_kwargs()
                kwargs.update(
                    decision=decision,
                    commitment_status=status,
                    downstream_status=downstream,
                )
                del kwargs["sponsor_fit_assessment_ref"]
                with self.assertRaises(TypeError):
                    ProgramCommitmentReview(**kwargs)

    def test_contract_declares_the_binding(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        self.assertEqual(document["version"], "0.2.0")
        self.assertIn(
            "sponsor_fit_assessment_ref", document["contract"]["required_fields"]
        )
        invariants = document["contract"]["invariants"]
        self.assertIn("program_commitment_cannot_exist_without_sponsor_fit", invariants)
        self.assertIn(
            "sponsor_fit_assessment_ref_is_opaque_and_never_dereferenced_here",
            invariants,
        )

    def test_the_commitment_module_does_not_import_the_assessment(self):
        """Binding must not pull the assessment back into the consumer."""

        import ast

        source = (
            ROOT / "src" / "contracts" / "program_commitment_review.py"
        ).read_text(encoding="utf-8")
        modules = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
        self.assertEqual(modules, {"__future__", "dataclasses", "enum", "typing"})


class ProgramCommitmentReviewContractTests(unittest.TestCase):
    def test_contract_freezes_six_commitment_decisions(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        self.assertEqual(
            document["contract"]["contract_id"],
            "ProgramCommitmentReview@0.2.0",
        )
        self.assertEqual(
            document["decision_values"],
            [
                "SELF_DEVELOP",
                "CO_DEVELOP",
                "DATA_PACKAGE_ONLY",
                "PARTNER_NOW",
                "MONITOR",
                "STOP_FOR_SPONSOR",
            ],
        )
        self.assertIn("decision_is_not_go_or_kill", document["contract"]["invariants"])

    def test_self_develop_requires_external_handoff(self):
        review = ProgramCommitmentReview(**review_kwargs())
        self.assertEqual(review.decision, ProgramCommitmentDecision.SELF_DEVELOP)
        self.assertEqual(
            review.downstream_status,
            DownstreamStatus.EXTERNAL_HANDOFF_REQUIRED,
        )

    def test_monitor_and_data_package_block_binder_or_de_novo_routes(self):
        for decision in (
            ProgramCommitmentDecision.MONITOR,
            ProgramCommitmentDecision.DATA_PACKAGE_ONLY,
        ):
            with self.subTest(decision=decision):
                review = ProgramCommitmentReview(
                    **{
                        **review_kwargs(),
                        "decision": decision,
                        "commitment_status": CommitmentStatus.CONDITIONALLY_COMMITTED,
                        "downstream_status": DownstreamStatus.BLOCKED_NO_COMMITMENT,
                    }
                )
                self.assertEqual(
                    review.downstream_status,
                    DownstreamStatus.BLOCKED_NO_COMMITMENT,
                )

    def test_stop_for_sponsor_is_not_scientific_kill(self):
        review = ProgramCommitmentReview(
            **{
                **review_kwargs(),
                "decision": ProgramCommitmentDecision.STOP_FOR_SPONSOR,
                "commitment_status": CommitmentStatus.NOT_COMMITTED,
                "downstream_status": DownstreamStatus.BLOCKED_NO_COMMITMENT,
            }
        )
        self.assertEqual(review.decision.value, "STOP_FOR_SPONSOR")
        self.assertNotIn("KILL", review.decision.value)

    def test_external_refs_and_human_decision_are_required(self):
        with self.assertRaises(ValueError):
            ProgramCommitmentReview(
                **{**review_kwargs(), "human_decision_ref": "local:decision/1"}
            )
        with self.assertRaises(ValueError):
            ProgramCommitmentReview(
                **{
                    **review_kwargs(),
                    "decision": ProgramCommitmentDecision.MONITOR,
                    "downstream_status": DownstreamStatus.EXTERNAL_HANDOFF_REQUIRED,
                }
            )

    def test_value_inflection_plan_is_external_input_not_phase_four_definition(self):
        document = yaml.safe_load(CONTRACT_PATH.read_text())
        self.assertIn(
            "value_inflection_plan_is_referenced_but_not_defined_here",
            document["contract"]["invariants"],
        )
        self.assertIn(
            "commitment_does_not_auto_execute_downstream_work",
            document["contract"]["invariants"],
        )


if __name__ == "__main__":
    unittest.main()
