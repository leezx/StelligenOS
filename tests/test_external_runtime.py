from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from src.repository.external_runtime import (
    ExternalRuntimeRequest,
    SubprocessExternalRuntime,
)


class ExternalRuntimeTests(unittest.TestCase):
    def _request(self, workspace: Path, output_root: Path, **overrides: object) -> ExternalRuntimeRequest:
        values: dict[str, object] = {
            "runtime_ref": "external:assetgenos/runtime",
            "command": (sys.executable, "-c", "raise SystemExit(0)"),
            "workspace_path": str(workspace),
            "output_root_path": str(output_root),
            "input_ref": "external:inputs/smoke",
            "run_context_ref": "external:runs/smoke",
            "output_ref": "external:outputs/smoke",
            "execution_enabled": True,
        }
        values.update(overrides)
        return ExternalRuntimeRequest(**values)  # type: ignore[arg-type]

    def test_execution_is_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            request = self._request(
                Path(workspace), Path(output), execution_enabled=False
            )
            with self.assertRaises(PermissionError):
                SubprocessExternalRuntime().run(request)

    def test_external_command_runs_without_repository_output(self) -> None:
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            result = SubprocessExternalRuntime().run(
                self._request(Path(workspace), Path(output))
            )
            self.assertEqual(result.status, "completed")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(list(Path(workspace).iterdir()), [])
            self.assertEqual(list(Path(output).iterdir()), [])

    def test_repository_paths_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._request(
                Path(__file__).resolve().parents[1],
                Path(tempfile.gettempdir()),
            )


if __name__ == "__main__":
    unittest.main()
