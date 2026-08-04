"""Behavioural tests for scripts/verify_repository_boundary.sh.

The script derives its repository root from its own location
(``dirname "$0"/..``), so copying it into a temporary directory makes that
directory the root under test. Every case below therefore runs against a
synthetic tree and never touches this repository — which matters, because the
script's whole purpose is to reject stray files, and a test that created them
here would be testing by violating.

These exist because adding `.github/workflows/ci.yml` required generalising the
single-purpose `.claude` exemption into a shared restricted-directory mechanism.
A refactor of an enforcement rule with no test is an enforcement rule you have
stopped knowing the behaviour of.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "verify_repository_boundary.sh"


class BoundaryScriptTests(unittest.TestCase):
    def _run(self, build: object = None) -> subprocess.CompletedProcess[str]:
        """Build a synthetic repository, run the script against it, return it."""

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "scripts").mkdir()
            shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
            # A minimal conforming tree: every entry is on the allowlist.
            (root / "docs").mkdir()
            (root / "src").mkdir()
            (root / "README.md").write_text("# synthetic\n")
            if build is not None:
                build(root)  # type: ignore[operator]
            return subprocess.run(
                ["bash", str(root / "scripts" / SCRIPT.name)],
                check=False,
                capture_output=True,
                text=True,
            )

    def assertAccepted(self, build: object = None) -> None:
        result = self._run(build)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Repository boundary check passed.", result.stdout)

    def assertRejected(self, build: object, expected: str) -> None:
        result = self._run(build)
        self.assertNotEqual(result.returncode, 0, "expected a boundary violation")
        self.assertIn(expected, result.stderr)

    # --- baseline ---------------------------------------------------------

    def test_a_conforming_tree_is_accepted(self) -> None:
        self.assertAccepted()

    def test_a_stray_top_level_file_is_rejected(self) -> None:
        self.assertRejected(
            lambda root: (root / "notes.md").write_text("stray\n"), "notes.md"
        )

    def test_a_stray_top_level_directory_is_rejected(self) -> None:
        self.assertRejected(lambda root: (root / "output").mkdir(), "output")

    def test_requirements_txt_is_allowed(self) -> None:
        self.assertAccepted(
            lambda root: (root / "requirements.txt").write_text("PyYAML>=6.0,<7\n")
        )

    # --- .claude, which the refactor must not have weakened ---------------

    def _claude(self, root: Path, *names: str) -> None:
        (root / ".claude").mkdir()
        for name in names:
            (root / ".claude" / name).write_text("{}\n")

    def test_the_single_allowed_claude_file_is_accepted(self) -> None:
        self.assertAccepted(lambda root: self._claude(root, "settings.local.json"))

    def test_any_other_file_under_claude_is_rejected(self) -> None:
        self.assertRejected(
            lambda root: self._claude(root, "settings.local.json", "secrets.json"),
            ".claude/secrets.json",
        )

    def test_a_nested_directory_under_claude_is_rejected(self) -> None:
        def build(root: Path) -> None:
            (root / ".claude" / "cache").mkdir(parents=True)

        self.assertRejected(build, ".claude/cache")

    def test_a_file_named_claude_is_not_exempt(self) -> None:
        """The exemption is for the directory. A file of that name is not it."""
        self.assertRejected(
            lambda root: (root / ".claude").write_text("not a directory\n"), ".claude"
        )

    # --- .github, added for CI -------------------------------------------

    def _workflow(self, root: Path, *extra: str) -> None:
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
        for name in extra:
            (root / ".github" / name).write_text("stray\n")

    def test_the_ci_workflow_is_accepted(self) -> None:
        self.assertAccepted(self._workflow)

    def test_a_second_workflow_file_is_rejected(self) -> None:
        """Allowing the directory wholesale was rejected in PR #43 review."""

        def build(root: Path) -> None:
            self._workflow(root)
            (root / ".github" / "workflows" / "release.yml").write_text("name: x\n")

        self.assertRejected(build, ".github/workflows/release.yml")

    def test_a_stray_file_under_github_is_rejected(self) -> None:
        self.assertRejected(
            lambda root: self._workflow(root, "CODEOWNERS"), ".github/CODEOWNERS"
        )

    def test_a_stray_directory_under_github_is_rejected(self) -> None:
        def build(root: Path) -> None:
            self._workflow(root)
            (root / ".github" / "ISSUE_TEMPLATE").mkdir()

        self.assertRejected(build, ".github/ISSUE_TEMPLATE")

    def test_github_without_the_workflow_is_still_accepted(self) -> None:
        """The allowlist permits these paths; it does not require them."""
        self.assertAccepted(lambda root: None)

    # --- data-bearing files ---------------------------------------------

    def test_a_data_like_file_is_rejected_even_in_an_allowed_directory(self) -> None:
        self.assertRejected(
            lambda root: (root / "docs" / "results.csv").write_text("a,b\n1,2\n"),
            "data-like file matching *.csv",
        )

    def test_an_archive_is_rejected(self) -> None:
        self.assertRejected(
            lambda root: (root / "docs" / "bundle.zip").write_bytes(b"PK\x03\x04"),
            "data-like file matching *.zip",
        )


if __name__ == "__main__":
    unittest.main()
