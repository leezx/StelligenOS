from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.repository import external_runtime
from src.repository.external_runtime import (
    ExternalRuntimePort,
    ExternalRuntimeRequest,
    ExternalRuntimeResult,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_SOURCE = (REPO_ROOT / "src" / "repository" / "external_runtime.py").read_text()
CLI_SOURCE = (REPO_ROOT / "scripts" / "run_external_runtime.py").read_text()


def _request(**overrides: object) -> ExternalRuntimeRequest:
    values: dict[str, object] = {
        "runtime_ref": "external:assetgenos/runtime",
        "command": ("adc-factory", "v2", "evaluate"),
        "workspace_path": tempfile.gettempdir(),
        "output_root_path": tempfile.gettempdir(),
        "input_ref": "external:inputs/smoke",
        "run_context_ref": "external:runs/smoke",
        "output_ref": "external:outputs/smoke",
        "sandbox_profile_ref": "external:sandbox/profiles/assetgenos",
    }
    values.update(overrides)
    return ExternalRuntimeRequest(**values)  # type: ignore[arg-type]


def _result(**overrides: object) -> ExternalRuntimeResult:
    values: dict[str, object] = {
        "runtime_ref": "external:assetgenos/runtime",
        "run_context_ref": "external:runs/smoke",
        "output_ref": "external:outputs/smoke",
        "sandbox_profile_ref": "external:sandbox/profiles/assetgenos",
        "status": "completed",
        "exit_code": 0,
    }
    values.update(overrides)
    return ExternalRuntimeResult(**values)  # type: ignore[arg-type]


class NoExecutionCapabilityTests(unittest.TestCase):
    """This module is contracts only; execution must not come back.

    The removed ``SubprocessExternalRuntime`` could not isolate the command it
    ran: writes into ``.git/`` were excluded from its fingerprint, a write could
    be reverted before exit to defeat the after-the-fact comparison, and nothing
    stopped the command reading host credentials. These assertions exist so that
    executor cannot be reintroduced without failing the suite.
    """

    def test_module_exposes_no_runtime_implementation(self) -> None:
        self.assertFalse(
            hasattr(external_runtime, "SubprocessExternalRuntime"),
            "the in-repository executor must not be reintroduced",
        )

    def test_module_does_not_import_process_or_hashing_machinery(self) -> None:
        for forbidden in ("import subprocess", "import os", "import hashlib"):
            with self.subTest(statement=forbidden):
                self.assertNotIn(forbidden, MODULE_SOURCE)

    def test_module_defines_no_repository_fingerprinting(self) -> None:
        """Fingerprinting was detection, not prevention, and is gone with it."""
        for removed in ("_repository_fingerprint", "RepositoryMutationError"):
            with self.subTest(symbol=removed):
                self.assertNotIn(removed, MODULE_SOURCE)
                self.assertFalse(hasattr(external_runtime, removed))

    def test_module_exports_only_contract_symbols(self) -> None:
        public = {
            name
            for name in vars(external_runtime)
            if not name.startswith("_") and name[0].isupper()
        }
        self.assertEqual(
            public,
            {
                "ExternalRuntimeRequest",
                "ExternalRuntimeResult",
                "ExternalRuntimePort",
                "REPO_ROOT",
                "Path",
                "Protocol",
            },
        )

    def test_port_run_is_a_stub(self) -> None:
        self.assertIsNone(
            ExternalRuntimePort.run(None, _request())  # type: ignore[arg-type]
        )

    def test_cli_cannot_execute(self) -> None:
        for forbidden in ("subprocess", "--execute", "execution_enabled"):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, CLI_SOURCE)


class RequestContractTests(unittest.TestCase):
    def test_all_reference_fields_must_be_external(self) -> None:
        for field in (
            "runtime_ref",
            "input_ref",
            "run_context_ref",
            "output_ref",
            "sandbox_profile_ref",
        ):
            for local_value in ("local/thing", "/tmp/thing", "./thing"):
                with self.subTest(field=field, value=local_value):
                    with self.assertRaises(ValueError):
                        _request(**{field: local_value})

    def test_sandbox_profile_ref_is_required(self) -> None:
        with self.assertRaises(TypeError):
            ExternalRuntimeRequest(  # type: ignore[call-arg]
                runtime_ref="external:assetgenos/runtime",
                command=("adc-factory",),
                workspace_path=tempfile.gettempdir(),
                output_root_path=tempfile.gettempdir(),
                input_ref="external:inputs/smoke",
                run_context_ref="external:runs/smoke",
                output_ref="external:outputs/smoke",
            )

    def test_repository_paths_are_rejected(self) -> None:
        for field, value in (
            ("workspace_path", str(REPO_ROOT)),
            ("workspace_path", str(REPO_ROOT / "logs")),
            ("output_root_path", str(REPO_ROOT)),
            ("output_root_path", str(REPO_ROOT / "docs")),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    _request(**{field: value})

    def test_empty_command_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _request(command=())

    def test_timeout_must_be_positive(self) -> None:
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _request(timeout_seconds=value)

    def test_conforming_request_is_accepted(self) -> None:
        self.assertEqual(_request().timeout_seconds, 1800)


class HandoverEnvelopeTests(unittest.TestCase):
    def test_envelope_states_that_execution_is_external(self) -> None:
        envelope = _request().envelope
        self.assertEqual(envelope["executed_by"], "external_controlled_runtime")
        self.assertIs(envelope["executed_in_repository"], False)

    def test_envelope_carries_the_sandbox_requirement(self) -> None:
        self.assertEqual(
            _request().envelope["sandbox_profile_ref"],
            "external:sandbox/profiles/assetgenos",
        )

    def test_envelope_is_json_serialisable(self) -> None:
        self.assertIn("adc-factory", json.dumps(_request().envelope))


class ResultContractTests(unittest.TestCase):
    def test_all_reference_fields_must_be_external(self) -> None:
        for field in (
            "runtime_ref",
            "run_context_ref",
            "output_ref",
            "sandbox_profile_ref",
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    _result(**{field: "local/thing"})

    def test_status_is_constrained(self) -> None:
        for value in ("running", "ok", ""):
            with self.subTest(status=value):
                with self.assertRaises(ValueError):
                    _result(status=value)
        self.assertEqual(_result(status="failed", exit_code=3).exit_code, 3)


class CliTests(unittest.TestCase):
    def _run_cli(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "scripts/run_external_runtime.py",
                "--runtime-ref",
                "external:assetgenos/runtime",
                "--workspace-path",
                tempfile.gettempdir(),
                "--output-root-path",
                tempfile.gettempdir(),
                "--input-ref",
                "external:inputs/smoke",
                "--run-context-ref",
                "external:runs/smoke",
                "--output-ref",
                "external:outputs/smoke",
                *extra,
                "--command",
                "adc-factory",
                "v2",
                "evaluate",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )

    def test_cli_prints_the_handover_envelope(self) -> None:
        result = self._run_cli(
            "--sandbox-profile-ref", "external:sandbox/profiles/assetgenos"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        envelope = json.loads(result.stdout)
        self.assertIs(envelope["executed_in_repository"], False)
        self.assertEqual(envelope["command"], ["adc-factory", "v2", "evaluate"])

    def test_cli_requires_a_sandbox_profile_ref(self) -> None:
        result = self._run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--sandbox-profile-ref", result.stderr)

    def test_cli_rejects_a_repository_workspace(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/run_external_runtime.py",
                "--runtime-ref",
                "external:assetgenos/runtime",
                "--workspace-path",
                str(REPO_ROOT),
                "--output-root-path",
                tempfile.gettempdir(),
                "--input-ref",
                "external:inputs/smoke",
                "--run-context-ref",
                "external:runs/smoke",
                "--output-ref",
                "external:outputs/smoke",
                "--sandbox-profile-ref",
                "external:sandbox/profiles/assetgenos",
                "--command",
                "adc-factory",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be outside the StelligenOS repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
