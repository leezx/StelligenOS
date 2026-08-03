"""Verify the kernel invariants declared in extensions/README.md."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS_ROOT = REPO_ROOT / "extensions"
KERNEL_ROOT = REPO_ROOT / "src"

EXPECTED_EXTENSIONS = {
    "ground_truth_learning_loop": ("EXT-01", "shell_only"),
    "dynamic_gate_context": ("EXT-02", "shell_only"),
    "asset_search_engine": ("EXT-03", "shell_only"),
    "stop_rule": ("EXT-04", "active_design"),
}

ALLOWED_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")

DATA_LIKE_SUFFIXES = {
    ".csv",
    ".tsv",
    ".parquet",
    ".h5",
    ".h5ad",
    ".sqlite",
    ".db",
    ".xlsx",
    ".jsonl",
    ".bam",
    ".fastq",
    ".vcf",
}


def _extension_dirs() -> list[Path]:
    return sorted(
        path
        for path in EXTENSIONS_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


class ExtensionRegistryTests(unittest.TestCase):
    def test_registry_matches_the_directory_tree(self) -> None:
        names = {path.name for path in _extension_dirs()}
        self.assertEqual(names, set(EXPECTED_EXTENSIONS))

    def test_every_extension_declares_identity_and_status(self) -> None:
        for path in _extension_dirs():
            with self.subTest(extension=path.name):
                manifest = yaml.safe_load((path / "extension.yaml").read_text())
                extension = manifest["extension"]
                expected_id, expected_status = EXPECTED_EXTENSIONS[path.name]
                self.assertEqual(extension["extension_id"], expected_id)
                self.assertEqual(extension["extension_name"], path.name)
                self.assertEqual(extension["status"], expected_status)
                for key in (
                    "extension_version",
                    "purpose",
                    "kernel_contact_surface",
                    "prohibited",
                    "execution_policy",
                    "activation_requirements",
                ):
                    self.assertIn(key, extension)

    def test_no_extension_claims_governed_status(self) -> None:
        """Promotion to governed requires a separate approved task."""
        for path in _extension_dirs():
            manifest = yaml.safe_load((path / "extension.yaml").read_text())
            self.assertNotEqual(manifest["extension"]["status"], "governed")

    def test_no_extension_modifies_the_kernel(self) -> None:
        for path in _extension_dirs():
            with self.subTest(extension=path.name):
                manifest = yaml.safe_load((path / "extension.yaml").read_text())
                surface = manifest["extension"]["kernel_contact_surface"]
                self.assertEqual(surface.get("modifies"), [])

    def test_every_extension_ships_a_readme_and_contracts(self) -> None:
        for path in _extension_dirs():
            with self.subTest(extension=path.name):
                self.assertTrue((path / "README.md").is_file())
                self.assertTrue((path / "contracts.py").is_file())


class KernelIndependenceTests(unittest.TestCase):
    def test_kernel_never_imports_an_extension(self) -> None:
        """Dependency direction is extension -> kernel, never the reverse."""
        offenders = [
            str(source.relative_to(REPO_ROOT))
            for source in KERNEL_ROOT.rglob("*.py")
            if re.search(
                r"^\s*(from\s+extensions|import\s+extensions)",
                source.read_text(),
                re.MULTILINE,
            )
        ]
        self.assertEqual(offenders, [])

    def test_frozen_kernel_contracts_are_untouched_by_this_extension_set(self) -> None:
        """No extension may declare a gate.yaml or envelope schema as writable."""
        for path in _extension_dirs():
            manifest = yaml.safe_load((path / "extension.yaml").read_text())
            surface = manifest["extension"]["kernel_contact_surface"]
            self.assertFalse(surface.get("modifies"))


class ExtensionBoundaryHygieneTests(unittest.TestCase):
    def test_no_data_bearing_files_in_extensions(self) -> None:
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in EXTENSIONS_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in DATA_LIKE_SUFFIXES
        ]
        self.assertEqual(offenders, [])

    def test_no_runtime_artifacts_in_extensions(self) -> None:
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in EXTENSIONS_ROOT.rglob("__pycache__")
        ]
        self.assertEqual(offenders, [])

    def test_file_names_contain_no_spaces(self) -> None:
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in EXTENSIONS_ROOT.rglob("*")
            if not ALLOWED_NAME_PATTERN.match(path.name)
        ]
        self.assertEqual(offenders, [])


class BacklogTests(unittest.TestCase):
    def test_all_seven_secondary_risks_are_recorded(self) -> None:
        backlog = (EXTENSIONS_ROOT / "BACKLOG.zh-CN.md").read_text()
        for index in range(1, 8):
            self.assertIn(f"BL-0{index}", backlog)


if __name__ == "__main__":
    unittest.main()
