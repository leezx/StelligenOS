"""Guard the ``gate_modules/`` boundary the way tests/test_extension_boundary.py
and tests/test_kernel_dependency_direction.py guard ``extensions/`` and
``genmodules/``.

Runtime Migration PR E2 created the top-level ``gate_modules/`` package for the
per-Gate primary Evidence Production Modules. The kernel invariants in
``gate_modules/README.md`` must hold:

* one-way dependency: ``src/`` never imports ``gate_modules/``;
* a Module imports the kernel, never a sibling outer layer;
* the repository stays data-free and zero-persistence;
* the built Module declares one consistent version.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
KERNEL_ROOT = REPO_ROOT / "src"
GATE_MODULES_ROOT = REPO_ROOT / "gate_modules"
TGT01 = GATE_MODULES_ROOT / "tgt01_adc_modality_precedent"
TGT02 = GATE_MODULES_ROOT / "tgt02_indication_specific_malignant_cell_coverage"
TGT05 = GATE_MODULES_ROOT / "tgt05_normal_tissue_fatal_liability"
TGT08 = GATE_MODULES_ROOT / "tgt08_target_opportunity_competition_ip_whitespace"
TGT03 = GATE_MODULES_ROOT / "tgt03_treatment_metastatic_persistence"
TGT04 = GATE_MODULES_ROOT / "tgt04_tumor_surface_availability_density_plausibility"

DATA_LIKE_SUFFIXES = {
    ".csv", ".tsv", ".parquet", ".feather", ".rds", ".h5", ".h5ad", ".loom",
    ".sqlite", ".db", ".xlsx", ".jsonl", ".bam", ".fastq", ".fq", ".vcf",
    ".tar", ".gz", ".zip", ".7z",
}
FORBIDDEN_RUNTIME_IMPORTS = {
    "socket", "http", "urllib", "urllib2", "requests", "httpx", "aiohttp",
    "subprocess", "ftplib", "telnetlib", "asyncio", "sqlite3", "shelve",
}
ALLOWED_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def _imported_roots(source: Path) -> set[str]:
    tree = ast.parse(source.read_text(), filename=str(source))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots


class GateModulesDependencyDirectionTests(unittest.TestCase):
    def test_kernel_never_imports_a_gate_module(self) -> None:
        offenders = [
            str(p.relative_to(REPO_ROOT))
            for p in KERNEL_ROOT.rglob("*.py")
            if "gate_modules" in _imported_roots(p)
        ]
        self.assertEqual(
            offenders, [], "src/ must not import gate_modules/ (one-way dependency)"
        )

    def test_a_gate_module_imports_the_kernel_not_a_sibling_outer_layer(self) -> None:
        for source in GATE_MODULES_ROOT.rglob("*.py"):
            roots = _imported_roots(source)
            with self.subTest(source=str(source.relative_to(REPO_ROOT))):
                self.assertNotIn("extensions", roots)
                self.assertNotIn("genmodules", roots)

    def test_the_module_core_performs_no_network_db_or_subprocess_io(self) -> None:
        for source in GATE_MODULES_ROOT.rglob("*.py"):
            roots = _imported_roots(source)
            bad = roots & FORBIDDEN_RUNTIME_IMPORTS
            with self.subTest(source=str(source.relative_to(REPO_ROOT))):
                self.assertEqual(
                    bad,
                    set(),
                    "a gate module must not open network / DB / subprocess IO; "
                    "shared retrieval and persistence live outside the repo",
                )


class GateModulesBoundaryHygieneTests(unittest.TestCase):
    def test_gate_modules_is_an_allowed_top_level_directory(self) -> None:
        script = (REPO_ROOT / "scripts" / "verify_repository_boundary.sh").read_text()
        self.assertIn('"gate_modules"', script)

    def test_no_data_bearing_files_under_gate_modules(self) -> None:
        offenders = [
            str(p.relative_to(REPO_ROOT))
            for p in GATE_MODULES_ROOT.rglob("*")
            if p.is_file() and p.suffix.lower() in DATA_LIKE_SUFFIXES
        ]
        self.assertEqual(offenders, [])

    def test_file_names_contain_no_spaces(self) -> None:
        offenders = [
            str(p.relative_to(REPO_ROOT))
            for p in GATE_MODULES_ROOT.rglob("*")
            if not ALLOWED_NAME_PATTERN.match(p.name)
        ]
        self.assertEqual(offenders, [])

    def test_no_runtime_artifacts_committed(self) -> None:
        offenders = [
            str(p.relative_to(REPO_ROOT))
            for p in GATE_MODULES_ROOT.rglob("__pycache__")
        ]
        self.assertEqual(offenders, [])


class Tgt01ModuleManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = yaml.safe_load((TGT01 / "module.yaml").read_text())["module"]

    def test_identity_and_version(self) -> None:
        self.assertEqual(self.manifest["module_id"], "MOD-TGT01")
        self.assertEqual(self.manifest["module_version"], "1.0.0")
        self.assertEqual(self.manifest["built_in"], "runtime_migration_pr_e2")
        self.assertEqual(self.manifest["gate_binding"]["gate_id"], "TGT-01")
        self.assertEqual(
            self.manifest["gate_binding"]["gateset_id"], "ADC_TARGET_GATESET"
        )

    def test_manifest_version_matches_the_package_constant(self) -> None:
        from gate_modules.tgt01_adc_modality_precedent import MODULE_ID, MODULE_VERSION

        self.assertEqual(self.manifest["module_id"], MODULE_ID)
        self.assertEqual(self.manifest["module_version"], MODULE_VERSION)

    def test_manifest_matches_the_crc_gateset_binding(self) -> None:
        gateset = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml").read_text()
        )
        binding = next(
            b
            for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-01"
        )
        self.assertEqual(binding["primary_module_id"], self.manifest["module_id"])
        self.assertEqual(
            binding["primary_module_version"], self.manifest["module_version"]
        )
        self.assertEqual(
            gateset["primary_module_binding"]["built_module_versions"]["TGT-01"],
            "1.0.0",
        )

    def test_boundary_flags_are_all_conservative(self) -> None:
        flags = self.manifest["boundary_flags"]
        for name in (
            "performs_network_io",
            "spawns_subprocess",
            "writes_repository",
            "allocates_ids_from_filesystem",
            "constructs_canonical_assessment",
            "produces_decision_or_kill",
            "numeric_scoring",
            "modifies_frozen_gate_science",
            "lifts_migration_pending",
        ):
            self.assertFalse(flags[name], name)

    def test_readme_registers_the_built_module(self) -> None:
        readme = " ".join((GATE_MODULES_ROOT / "README.md").read_text().split())
        self.assertIn("MOD-TGT01", readme)
        self.assertIn("1.0.0", readme)
        self.assertIn("`import gate_modules`", readme)
        self.assertIn("`from gate_modules`", readme)


class Tgt05ModuleManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = yaml.safe_load((TGT05 / "module.yaml").read_text())["module"]

    def test_identity_and_version(self) -> None:
        self.assertEqual(self.manifest["module_id"], "MOD-TGT05")
        self.assertEqual(self.manifest["module_version"], "1.0.0")
        self.assertEqual(self.manifest["built_in"], "runtime_migration_pr_e4")
        self.assertEqual(self.manifest["gate_binding"]["gate_id"], "TGT-05")
        self.assertEqual(
            self.manifest["gate_binding"]["gateset_id"], "ADC_TARGET_GATESET"
        )

    def test_manifest_version_matches_the_package_constant(self) -> None:
        from gate_modules.tgt05_normal_tissue_fatal_liability import (
            MODULE_ID,
            MODULE_VERSION,
        )

        self.assertEqual(self.manifest["module_id"], MODULE_ID)
        self.assertEqual(self.manifest["module_version"], MODULE_VERSION)

    def test_manifest_matches_the_crc_gateset_binding(self) -> None:
        gateset = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml").read_text()
        )
        binding = next(
            b
            for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-05"
        )
        self.assertEqual(binding["primary_module_id"], self.manifest["module_id"])
        self.assertEqual(
            binding["primary_module_version"], self.manifest["module_version"]
        )
        self.assertEqual(
            gateset["primary_module_binding"]["built_module_versions"]["TGT-05"],
            "1.0.0",
        )

    def test_boundary_flags_are_all_conservative(self) -> None:
        flags = self.manifest["boundary_flags"]
        for name, value in flags.items():
            self.assertFalse(value, name)

    def test_readme_registers_the_built_module(self) -> None:
        readme = " ".join((GATE_MODULES_ROOT / "README.md").read_text().split())
        self.assertIn("MOD-TGT05", readme)
        self.assertIn("tgt05_normal_tissue_fatal_liability", readme)


class Tgt08ModuleManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = yaml.safe_load((TGT08 / "module.yaml").read_text())["module"]

    def test_identity_and_version(self) -> None:
        self.assertEqual(self.manifest["module_id"], "MOD-TGT08")
        self.assertEqual(self.manifest["module_version"], "1.0.0")
        self.assertEqual(self.manifest["built_in"], "runtime_migration_pr_e6")
        self.assertEqual(self.manifest["gate_binding"]["gate_id"], "TGT-08")
        self.assertEqual(
            self.manifest["gate_binding"]["gateset_id"], "ADC_TARGET_GATESET"
        )

    def test_manifest_version_matches_the_package_constant(self) -> None:
        from gate_modules.tgt08_target_opportunity_competition_ip_whitespace import (
            MODULE_ID,
            MODULE_VERSION,
        )

        self.assertEqual(self.manifest["module_id"], MODULE_ID)
        self.assertEqual(self.manifest["module_version"], MODULE_VERSION)

    def test_manifest_matches_the_crc_gateset_binding(self) -> None:
        gateset = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml").read_text()
        )
        binding = next(
            b
            for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-08"
        )
        self.assertEqual(binding["primary_module_id"], self.manifest["module_id"])
        self.assertEqual(
            binding["primary_module_version"], self.manifest["module_version"]
        )
        self.assertEqual(
            gateset["primary_module_binding"]["built_module_versions"]["TGT-08"],
            "1.0.0",
        )

    def test_boundary_flags_are_all_conservative(self) -> None:
        flags = self.manifest["boundary_flags"]
        for name, value in flags.items():
            self.assertFalse(value, name)

    def test_readme_registers_the_built_module(self) -> None:
        readme = " ".join((GATE_MODULES_ROOT / "README.md").read_text().split())
        self.assertIn("MOD-TGT08", readme)
        self.assertIn("tgt08_target_opportunity_competition_ip_whitespace", readme)


class Tgt02ModuleManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = yaml.safe_load((TGT02 / "module.yaml").read_text())["module"]

    def test_identity_and_version(self) -> None:
        self.assertEqual(self.manifest["module_id"], "MOD-TGT02")
        self.assertEqual(self.manifest["module_version"], "1.0.0")
        self.assertEqual(self.manifest["built_in"], "runtime_migration_pr_e8")
        self.assertEqual(self.manifest["gate_binding"]["gate_id"], "TGT-02")
        self.assertEqual(
            self.manifest["gate_binding"]["gateset_id"], "ADC_TARGET_GATESET"
        )

    def test_manifest_version_matches_the_package_constant(self) -> None:
        from gate_modules.tgt02_indication_specific_malignant_cell_coverage import (
            MODULE_ID,
            MODULE_VERSION,
        )

        self.assertEqual(self.manifest["module_id"], MODULE_ID)
        self.assertEqual(self.manifest["module_version"], MODULE_VERSION)

    def test_manifest_matches_the_crc_gateset_binding(self) -> None:
        gateset = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml").read_text()
        )
        binding = next(
            b
            for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-02"
        )
        self.assertEqual(binding["primary_module_id"], self.manifest["module_id"])
        self.assertEqual(
            binding["primary_module_version"], self.manifest["module_version"]
        )
        self.assertEqual(
            gateset["primary_module_binding"]["built_module_versions"]["TGT-02"],
            "1.0.0",
        )

    def test_boundary_flags_are_all_conservative(self) -> None:
        flags = self.manifest["boundary_flags"]
        for name, value in flags.items():
            self.assertFalse(value, name)

    def test_readme_registers_the_built_module(self) -> None:
        readme = " ".join((GATE_MODULES_ROOT / "README.md").read_text().split())
        self.assertIn("MOD-TGT02", readme)
        self.assertIn("tgt02_indication_specific_malignant_cell_coverage", readme)


class Tgt03ModuleManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = yaml.safe_load((TGT03 / "module.yaml").read_text())["module"]

    def test_identity_and_version(self) -> None:
        self.assertEqual(self.manifest["module_id"], "MOD-TGT03")
        self.assertEqual(self.manifest["module_version"], "1.0.0")
        self.assertEqual(self.manifest["built_in"], "runtime_migration_pr_e10")
        self.assertEqual(self.manifest["gate_binding"]["gate_id"], "TGT-03")
        self.assertEqual(
            self.manifest["gate_binding"]["gateset_id"], "ADC_TARGET_GATESET"
        )

    def test_manifest_version_matches_the_package_constant(self) -> None:
        from gate_modules.tgt03_treatment_metastatic_persistence import (
            MODULE_ID,
            MODULE_VERSION,
        )

        self.assertEqual(self.manifest["module_id"], MODULE_ID)
        self.assertEqual(self.manifest["module_version"], MODULE_VERSION)

    def test_manifest_matches_the_crc_gateset_binding(self) -> None:
        gateset = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml").read_text()
        )
        binding = next(
            b
            for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-03"
        )
        self.assertEqual(binding["primary_module_id"], self.manifest["module_id"])
        self.assertEqual(
            binding["primary_module_version"], self.manifest["module_version"]
        )
        self.assertEqual(
            gateset["primary_module_binding"]["built_module_versions"]["TGT-03"],
            "1.0.0",
        )

    def test_boundary_flags_are_all_conservative(self) -> None:
        flags = self.manifest["boundary_flags"]
        for name, value in flags.items():
            self.assertFalse(value, name)

    def test_readme_registers_the_built_module(self) -> None:
        readme = " ".join((GATE_MODULES_ROOT / "README.md").read_text().split())
        self.assertIn("MOD-TGT03", readme)
        self.assertIn("tgt03_treatment_metastatic_persistence", readme)


class Tgt04ModuleManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = yaml.safe_load((TGT04 / "module.yaml").read_text())["module"]

    def test_identity_and_version(self) -> None:
        self.assertEqual(self.manifest["module_id"], "MOD-TGT04")
        self.assertEqual(self.manifest["module_version"], "1.0.0")
        self.assertEqual(self.manifest["built_in"], "runtime_migration_pr_e12")
        self.assertEqual(self.manifest["gate_binding"]["gate_id"], "TGT-04")
        self.assertEqual(
            self.manifest["gate_binding"]["gateset_id"], "ADC_TARGET_GATESET"
        )

    def test_manifest_version_matches_the_package_constant(self) -> None:
        from gate_modules.tgt04_tumor_surface_availability_density_plausibility import (
            MODULE_ID,
            MODULE_VERSION,
        )

        self.assertEqual(self.manifest["module_id"], MODULE_ID)
        self.assertEqual(self.manifest["module_version"], MODULE_VERSION)

    def test_manifest_matches_the_crc_gateset_binding(self) -> None:
        gateset = yaml.safe_load(
            (REPO_ROOT / "src" / "contracts" / "crc_adc_target_gateset.yaml").read_text()
        )
        binding = next(
            b
            for b in gateset["context_specific_bindings"]["gate_bindings"]
            if b["gate_id"] == "TGT-04"
        )
        self.assertEqual(binding["primary_module_id"], self.manifest["module_id"])
        self.assertEqual(
            binding["primary_module_version"], self.manifest["module_version"]
        )
        self.assertEqual(
            gateset["primary_module_binding"]["built_module_versions"]["TGT-04"],
            "1.0.0",
        )

    def test_boundary_flags_are_all_conservative(self) -> None:
        flags = self.manifest["boundary_flags"]
        for name, value in flags.items():
            self.assertFalse(value, name)

    def test_readme_registers_the_built_module(self) -> None:
        readme = " ".join((GATE_MODULES_ROOT / "README.md").read_text().split())
        self.assertIn("MOD-TGT04", readme)
        self.assertIn("tgt04_tumor_surface_availability_density_plausibility", readme)


if __name__ == "__main__":
    unittest.main()
