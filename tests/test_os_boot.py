from __future__ import annotations

import subprocess
import sys
import unittest

from src.repository.boot import BootRequest, boot


class OSBootTests(unittest.TestCase):
    def test_boot_loads_architecture_without_data(self) -> None:
        report = boot(
            BootRequest(
                workspace_ref="external:workspace/assetgenos",
                run_context_ref="external:runs/smoke-001",
                policy_ref="external:policies/exploration",
            )
        )
        self.assertEqual(report.status, "ready_for_external_runtime")
        self.assertEqual(len(report.lifecycle_stages), 4)
        self.assertEqual(len(report.capability_ids), 9)
        self.assertEqual(len(report.gate_groups), 3)
        self.assertEqual(len(report.route_ids), 2)

    def test_boot_rejects_repository_local_context(self) -> None:
        with self.assertRaises(ValueError):
            BootRequest(
                workspace_ref="/tmp/workspace",
                run_context_ref="external:runs/smoke-001",
                policy_ref="external:policies/exploration",
            )

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
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"status": "ready_for_external_runtime"', result.stdout)
        self.assertIn('"asset_generation"', result.stdout)


if __name__ == "__main__":
    unittest.main()
