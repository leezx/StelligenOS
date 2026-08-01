from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
GENMODULES = ROOT / "genmodules"


class AssetGenOSModuleMigrationTests(unittest.TestCase):
    def test_binder_module_preserves_frozen_catalogue_and_contract(self) -> None:
        module_root = GENMODULES / "antibody_binder_asset_engineering"
        module = yaml.safe_load((module_root / "module.yaml").read_text())[
            "module"
        ]
        self.assertEqual(module["module_version"], "0.4.0")
        self.assertEqual(module["input_contract"], "ExistingBinderAssetInput@0.4.0")
        self.assertEqual(
            module["output_contract"], "AntibodyAssetEngineeringPackage@0.4.0"
        )
        self.assertEqual(len(module["stages"]), 16)
        self.assertEqual(module["external_execution_policy"], "disabled_by_default")

        result = subprocess.run(
            [sys.executable, "run_pipeline.py", "list-steps"],
            cwd=module_root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.strip().splitlines()), 16)

    def test_de_novo_module_preserves_frozen_catalogue_and_contract(self) -> None:
        module_root = GENMODULES / "epitope_conditioned_de_novo_antibody_discovery"
        module = yaml.safe_load((module_root / "module.yaml").read_text())[
            "module"
        ]
        self.assertEqual(module["module_version"], "0.1.0")
        self.assertEqual(
            module["input_contract"], "EpitopeConditionedDiscoveryInput@0.1.0"
        )
        self.assertEqual(
            module["output_contract"],
            "EpitopeConditionedAntibodyAssetPackage@0.1.0",
        )
        self.assertEqual(len(module["stages"]), 15)
        self.assertEqual(module["external_execution_policy"], "disabled_by_default")

        result = subprocess.run(
            [sys.executable, "run_pipeline.py", "list-steps"],
            cwd=module_root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.strip().splitlines()), 15)

    def test_migration_does_not_include_legacy_runtime_state(self) -> None:
        forbidden_names = {".venv", ".pytest_cache", "__pycache__", "data"}
        forbidden_suffixes = {".sqlite", ".sqlite3", ".db", ".pyc"}
        for path in GENMODULES.rglob("*"):
            if any(part in forbidden_names for part in path.parts):
                self.fail(f"legacy runtime state migrated: {path}")
            if path.is_file() and path.suffix in forbidden_suffixes:
                self.fail(f"data-bearing file migrated: {path}")


if __name__ == "__main__":
    unittest.main()
