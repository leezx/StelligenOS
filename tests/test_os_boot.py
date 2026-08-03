from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

from src.capabilities.binder_adc_routes import ROUTE_IDS
from src.capabilities.registry import CAPABILITY_IDS, CAPABILITY_NAMES
from src.lifecycle.state_machine import LIFECYCLE_STAGE_IDS, LifecycleStage
from src.repository.boot import BootRequest, boot


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_DOC = REPO_ROOT / "docs" / "architecture" / "capabilities.zh-CN.md"

EXPECTED_LIFECYCLE_STAGES = (
    "opportunity_generation",
    "opportunity_validation",
    "asset_generation",
    "asset_development",
)
EXPECTED_CAPABILITY_IDS = (
    "opportunity_discovery",
    "knowledge_mining",
    "rule_learning",
    "evidence_extraction",
    "adc_design",
    "binder_engineering",
    "patent_analysis",
    "due_diligence",
    "portfolio_management",
)


def _request(**overrides: str) -> BootRequest:
    values: dict[str, str] = {
        "workspace_ref": "external:workspace/assetgenos",
        "run_context_ref": "external:runs/smoke-001",
        "policy_ref": "external:policies/exploration",
    }
    values.update(overrides)
    return BootRequest(**values)


class OSBootTests(unittest.TestCase):
    def test_boot_loads_architecture_without_data(self) -> None:
        self.assertEqual(boot(_request()).status, "ready_for_external_runtime")

    def test_boot_reports_exact_lifecycle_stages_in_order(self) -> None:
        """Counting 4 would still pass if a stage were renamed or reordered."""
        self.assertEqual(boot(_request()).lifecycle_stages, EXPECTED_LIFECYCLE_STAGES)

    def test_boot_reports_exact_capability_ids_in_order(self) -> None:
        self.assertEqual(boot(_request()).capability_ids, EXPECTED_CAPABILITY_IDS)

    def test_boot_reports_exact_gate_groups_in_order(self) -> None:
        self.assertEqual(
            boot(_request()).gate_groups,
            ("target_opportunity", "product_realization", "commercial_executability"),
        )

    def test_boot_reports_exact_route_ids_in_order(self) -> None:
        self.assertEqual(boot(_request()).route_ids, ROUTE_IDS)
        self.assertEqual(len(ROUTE_IDS), 2)

    def test_boot_echoes_its_external_references(self) -> None:
        report = boot(_request())
        self.assertEqual(report.workspace_ref, "external:workspace/assetgenos")
        self.assertEqual(report.run_context_ref, "external:runs/smoke-001")
        self.assertEqual(report.policy_ref, "external:policies/exploration")


class SingleSourceOfTruthTests(unittest.TestCase):
    """Boot must read the architecture, not restate it.

    Each assertion below fails if a second copy of the lifecycle or capability
    list is reintroduced and then drifts.
    """

    def test_boot_lifecycle_comes_from_the_state_machine(self) -> None:
        self.assertEqual(boot(_request()).lifecycle_stages, LIFECYCLE_STAGE_IDS)

    def test_lifecycle_ids_are_derived_from_the_lifecycle_enum(self) -> None:
        self.assertEqual(
            LIFECYCLE_STAGE_IDS,
            tuple(stage.name.lower() for stage in LifecycleStage),
        )

    def test_boot_capabilities_come_from_the_capability_registry(self) -> None:
        self.assertEqual(boot(_request()).capability_ids, CAPABILITY_IDS)

    def test_boot_does_not_define_its_own_lifecycle_or_capability_list(self) -> None:
        source = (REPO_ROOT / "src" / "repository" / "boot.py").read_text()
        for stage in EXPECTED_LIFECYCLE_STAGES:
            self.assertNotIn(f'"{stage}"', source)
        for capability in EXPECTED_CAPABILITY_IDS:
            self.assertNotIn(f'"{capability}"', source)

    def test_capability_registry_matches_the_architecture_contract(self) -> None:
        """The architecture document is the contractual authority."""
        document = CAPABILITIES_DOC.read_text()
        section = document.split("## Initial Capabilities", 1)[1].split("##", 1)[0]
        documented = tuple(re.findall(r"^- (.+)$", section, re.MULTILINE))
        self.assertEqual(documented, CAPABILITY_NAMES)

    def test_capability_ids_are_derived_from_the_contract_names(self) -> None:
        self.assertEqual(
            CAPABILITY_IDS,
            tuple(name.lower().replace(" ", "_") for name in CAPABILITY_NAMES),
        )


class BootExternalReferenceTests(unittest.TestCase):
    """Every reference field must reject repository-local values, not just one."""

    def test_each_reference_field_rejects_a_local_path(self) -> None:
        for field in ("workspace_ref", "run_context_ref", "policy_ref"):
            for local_value in ("/tmp/workspace", "logs/worklog.md", "./local"):
                with self.subTest(field=field, value=local_value):
                    with self.assertRaises(ValueError):
                        _request(**{field: local_value})

    def test_fully_external_request_is_accepted(self) -> None:
        self.assertEqual(_request().contract_version, "0.1.0")


class BootCliTests(unittest.TestCase):
    def test_cli_prints_external_boot_plan(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/boot_os.py",
                "--workspace-ref",
                "external:workspace/assetgenos",
                "--run-context-ref",
                "external:runs/smoke-001",
                "--policy-ref",
                "external:policies/exploration",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"status": "ready_for_external_runtime"', result.stdout)
        for stage in EXPECTED_LIFECYCLE_STAGES:
            self.assertIn(f'"{stage}"', result.stdout)
        for capability in EXPECTED_CAPABILITY_IDS:
            self.assertIn(f'"{capability}"', result.stdout)


if __name__ == "__main__":
    unittest.main()
