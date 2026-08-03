from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.repository.external_runtime import (
    INHERITED_ENVIRONMENT_KEYS,
    ExternalRuntimeRequest,
    RepositoryMutationError,
    SubprocessExternalRuntime,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class ExternalRuntimeTestCase(unittest.TestCase):
    def _request(
        self, workspace: Path, output_root: Path, **overrides: object
    ) -> ExternalRuntimeRequest:
        values: dict[str, object] = {
            "runtime_ref": "external:assetgenos/runtime",
            "command": (sys.executable, "-c", "raise SystemExit(0)"),
            "workspace_path": str(workspace),
            "output_root_path": str(output_root),
            "input_ref": "external:inputs/smoke",
            "run_context_ref": "external:runs/smoke",
            "output_ref": "external:outputs/smoke",
            "sandbox_profile_ref": "external:sandbox/profiles/assetgenos",
            "execution_enabled": True,
        }
        values.update(overrides)
        return ExternalRuntimeRequest(**values)  # type: ignore[arg-type]


class ExternalRuntimeTests(ExternalRuntimeTestCase):
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

    def test_failing_command_is_reported_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            result = SubprocessExternalRuntime().run(
                self._request(
                    Path(workspace),
                    Path(output),
                    command=(sys.executable, "-c", "raise SystemExit(3)"),
                )
            )
            self.assertEqual(result.status, "failed")
            self.assertEqual(result.exit_code, 3)

    def test_result_records_the_sandbox_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            result = SubprocessExternalRuntime().run(
                self._request(Path(workspace), Path(output))
            )
            self.assertEqual(
                result.sandbox_profile_ref, "external:sandbox/profiles/assetgenos"
            )


class RepositoryPathRejectionTests(ExternalRuntimeTestCase):
    def test_repository_paths_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._request(REPO_ROOT, Path(tempfile.gettempdir()))

    def test_repository_subdirectory_paths_are_rejected(self) -> None:
        for field, value in (
            ("workspace_path", str(REPO_ROOT / "logs")),
            ("output_root_path", str(REPO_ROOT / "docs")),
        ):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as other:
                    with self.assertRaises(ValueError):
                        self._request(Path(other), Path(other), **{field: value})

    def test_output_root_must_be_a_directory(self) -> None:
        """A file, or a path that does not exist, is not an output root."""
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            as_file = Path(output) / "not-a-directory"
            as_file.write_text("")
            with self.assertRaises(NotADirectoryError):
                SubprocessExternalRuntime().run(
                    self._request(
                        Path(workspace), Path(output), output_root_path=str(as_file)
                    )
                )
            missing = Path(output) / "absent"
            with self.assertRaises(NotADirectoryError):
                SubprocessExternalRuntime().run(
                    self._request(
                        Path(workspace), Path(output), output_root_path=str(missing)
                    )
                )

    def test_workspace_must_be_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            as_file = Path(workspace) / "not-a-directory"
            as_file.write_text("")
            with self.assertRaises(NotADirectoryError):
                SubprocessExternalRuntime().run(
                    self._request(
                        Path(workspace), Path(output), workspace_path=str(as_file)
                    )
                )


class SandboxAttestationTests(ExternalRuntimeTestCase):
    """Path checks are not write isolation, so isolation must be attested."""

    def test_sandbox_profile_ref_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            with self.assertRaises(TypeError):
                ExternalRuntimeRequest(  # type: ignore[call-arg]
                    runtime_ref="external:assetgenos/runtime",
                    command=(sys.executable, "-c", "pass"),
                    workspace_path=workspace,
                    output_root_path=workspace,
                    input_ref="external:inputs/smoke",
                    run_context_ref="external:runs/smoke",
                    output_ref="external:outputs/smoke",
                )

    def test_sandbox_profile_ref_must_be_external(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            with self.assertRaises(ValueError):
                self._request(
                    Path(workspace),
                    Path(workspace),
                    sandbox_profile_ref="local/sandbox",
                )


class RepositoryMutationDetectionTests(ExternalRuntimeTestCase):
    """The boundary must fail loudly when a command writes into the repository.

    Detection, not prevention: an arbitrary child can always name an absolute
    path. What must not happen is that the write goes unnoticed.
    """

    def test_command_writing_into_the_repository_is_detected(self) -> None:
        target = REPO_ROOT / "external-runtime-boundary-probe.txt"
        self.addCleanup(target.unlink, missing_ok=True)
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            request = self._request(
                Path(workspace),
                Path(output),
                command=(
                    sys.executable,
                    "-c",
                    f"open({str(target)!r}, 'w').write('escaped')",
                ),
            )
            with self.assertRaises(RepositoryMutationError) as caught:
                SubprocessExternalRuntime().run(request)
            self.assertIn("external-runtime-boundary-probe.txt", str(caught.exception))
            self.assertIn("created", str(caught.exception))

    def test_command_modifying_a_repository_file_is_detected(self) -> None:
        target = REPO_ROOT / "logs" / "worklog.md"
        original = target.read_bytes()
        self.addCleanup(target.write_bytes, original)
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            request = self._request(
                Path(workspace),
                Path(output),
                command=(
                    sys.executable,
                    "-c",
                    f"open({str(target)!r}, 'a').write('tampered')",
                ),
            )
            with self.assertRaises(RepositoryMutationError) as caught:
                SubprocessExternalRuntime().run(request)
            self.assertIn("modified", str(caught.exception))

    def test_clean_run_reports_no_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            result = SubprocessExternalRuntime().run(
                self._request(
                    Path(workspace),
                    Path(output),
                    command=(
                        sys.executable,
                        "-c",
                        "import os; open(os.path.join(os.environ['STELLIGEN_OUTPUT_ROOT'], 'ok'), 'w').write('x')",
                    ),
                )
            )
            self.assertEqual(result.status, "completed")
            self.assertEqual([p.name for p in Path(output).iterdir()], ["ok"])


class EnvironmentIsolationTests(ExternalRuntimeTestCase):
    """Sensitive parent environment must not reach the external command."""

    def _captured_environment(self, extra_parent_env: dict[str, str]) -> dict[str, str]:
        with tempfile.TemporaryDirectory() as workspace, tempfile.TemporaryDirectory() as output:
            dump = Path(output) / "env.json"
            request = self._request(
                Path(workspace),
                Path(output),
                command=(
                    sys.executable,
                    "-c",
                    f"import json, os; json.dump(dict(os.environ), open({str(dump)!r}, 'w'))",
                ),
            )
            with mock.patch.dict(os.environ, extra_parent_env, clear=False):
                result = SubprocessExternalRuntime().run(request)
            self.assertEqual(result.status, "completed")
            return json.loads(dump.read_text())

    def test_credentials_are_not_inherited(self) -> None:
        secrets = {
            "AWS_SECRET_ACCESS_KEY": "must-not-leak",
            "GITHUB_TOKEN": "must-not-leak",
            "ANTHROPIC_API_KEY": "must-not-leak",
            "OPENAI_API_KEY": "must-not-leak",
            "SSH_AUTH_SOCK": "/must/not/leak",
        }
        child_env = self._captured_environment(secrets)
        for key in secrets:
            with self.subTest(variable=key):
                self.assertNotIn(key, child_env)
        self.assertNotIn("must-not-leak", "".join(child_env.values()))

    def test_home_is_redirected_into_the_external_workspace(self) -> None:
        """Inheriting HOME would expose ~/.ssh and ~/.aws."""
        child_env = self._captured_environment({"HOME": "/parent/home"})
        self.assertIn("HOME", child_env)
        self.assertNotEqual(child_env["HOME"], "/parent/home")

    @staticmethod
    def _platform_injected_keys() -> set[str]:
        """Variables the OS adds to any child, even when given an empty env.

        macOS injects ``__CF_USER_TEXT_ENCODING``, ``SDKROOT`` and friends. Those
        are not leaks, so the leak assertion is measured against this baseline
        rather than against a hardcoded per-platform exclusion list.
        """

        probe = subprocess.run(
            [sys.executable, "-c", "import json, os; print(json.dumps(dict(os.environ)))"],
            env={},
            check=True,
            capture_output=True,
            text=True,
        )
        return set(json.loads(probe.stdout))

    def test_no_parent_variable_leaks_outside_the_allowlist(self) -> None:
        child_env = self._captured_environment({"UNRELATED_PARENT_VAR": "nope"})
        self.assertNotIn("UNRELATED_PARENT_VAR", child_env)
        permitted = (
            set(INHERITED_ENVIRONMENT_KEYS)
            | {"HOME"}
            | self._platform_injected_keys()
        )
        for key in child_env:
            if key.startswith("STELLIGEN_"):
                continue
            with self.subTest(variable=key):
                self.assertIn(key, permitted)

    def test_run_context_is_passed_through_as_references(self) -> None:
        child_env = self._captured_environment({})
        self.assertEqual(
            child_env["STELLIGEN_SANDBOX_PROFILE_REF"],
            "external:sandbox/profiles/assetgenos",
        )
        self.assertEqual(
            child_env["STELLIGEN_RUNTIME_REF"], "external:assetgenos/runtime"
        )


if __name__ == "__main__":
    unittest.main()
