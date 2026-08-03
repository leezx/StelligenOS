from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

from src.capabilities.gates import GATE_CATALOG, GATE_GROUPS, GATE_IDS


ROOT = Path(__file__).resolve().parents[1]
GENMODULES = ROOT / "genmodules"
CATALOG = GENMODULES / "assetgenos_catalog"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _load_catalog_gates() -> list[dict[str, object]]:
    """Every migrated gate.yaml, as its inner ``gate`` mapping."""

    gates = []
    for path in sorted(CATALOG.rglob("gate.yaml")):
        document = yaml.safe_load(path.read_text())
        gate = document["gate"]
        gate["__path"] = str(path.relative_to(ROOT))
        gates.append(gate)
    return gates


class AssetGenOSModuleMigrationTests(unittest.TestCase):
    def test_assetgenos_catalog_migrates_only_software_definitions(self) -> None:
        module_root = GENMODULES / "assetgenos_catalog"
        module = yaml.safe_load((module_root / "module.yaml").read_text())["module"]
        self.assertEqual(module["status"], "migrated_contracts_only")
        self.assertEqual(module["contents"], {
            "contracts": 7,
            "gates": 45,
            "models": 59,
            "profiles": 53,
        })
        self.assertEqual(len(list((module_root / "gates").rglob("gate.yaml"))), 45)
        self.assertEqual(len(list((module_root / "models").rglob("model.yaml"))), 59)
        self.assertEqual(len(list((module_root / "profiles").rglob("profile.yaml"))), 53)
        self.assertEqual(len(list((module_root / "contracts").glob("*.yaml"))), 7)

        forbidden = {"model_governance", "model_work_packages", "data", "cache", "results"}
        for path in module_root.rglob("*"):
            self.assertTrue(
                not any(part in forbidden for part in path.parts),
                f"runtime or governance state migrated: {path}",
            )

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
        self.assertEqual(module["external_stage_count"], 14)
        self.assertEqual(len(module["external_stage_mapping"]), 14)
        self.assertEqual(module["external_execution_policy"], "disabled_by_default")

        result = subprocess.run(
            [sys.executable, "run_pipeline.py", "list-steps"],
            cwd=module_root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.strip().splitlines()), 14)

        internal_result = subprocess.run(
            [sys.executable, "run_pipeline.py", "list-internal-steps"],
            cwd=module_root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(internal_result.returncode, 0, internal_result.stderr)
        self.assertEqual(len(internal_result.stdout.strip().splitlines()), 16)

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


class MigratedYamlIntegrityTests(unittest.TestCase):
    """Counting files cannot show that 19k+ migrated lines are intact.

    A corrupt document, a renamed Gate or a drifted version would all pass a
    count-only check, so the migrated content is parsed and compared against the
    frozen Gate registry in ``src/capabilities/gates.py``.
    """

    def test_every_migrated_yaml_document_parses(self) -> None:
        unparsable: list[str] = []
        for path in sorted(GENMODULES.rglob("*.yaml")):
            try:
                yaml.safe_load(path.read_text())
            except yaml.YAMLError as error:
                unparsable.append(f"{path.relative_to(ROOT)}: {error}")
        self.assertEqual(unparsable, [])

    def test_migrated_yaml_count_is_not_silently_reduced(self) -> None:
        """Guards the parse test above from passing on an emptied tree."""
        self.assertGreaterEqual(len(list(GENMODULES.rglob("*.yaml"))), 200)

    def test_catalog_gate_ids_match_the_frozen_registry_exactly(self) -> None:
        catalog_ids = {gate["gate_id"] for gate in _load_catalog_gates()}
        self.assertEqual(catalog_ids, set(GATE_IDS))

    def test_catalog_gate_groups_match_the_frozen_registry(self) -> None:
        frozen_group = {entry.gate_id: entry.group for entry in GATE_CATALOG}
        for gate in _load_catalog_gates():
            with self.subTest(gate=gate["gate_id"]):
                self.assertIn(gate["runtime"]["gate_group"], GATE_GROUPS)
                self.assertEqual(
                    gate["runtime"]["gate_group"],
                    frozen_group[gate["gate_id"]],
                    gate["__path"],
                )

    def test_catalog_gate_order_matches_the_frozen_registry(self) -> None:
        """Relative order, not absolute numbering.

        The catalog numbers Gates sparsely (0-12, 20-35, 40-55) while the frozen
        registry numbers them contiguously (0-44). The invariant that must hold
        is the ordering, so comparing raw sequence values would be wrong.
        """
        ordered = [
            gate["gate_id"]
            for gate in sorted(_load_catalog_gates(), key=lambda g: g["sequence"])
        ]
        self.assertEqual(ordered, list(GATE_IDS))

    def test_catalog_gate_sequences_are_unique(self) -> None:
        sequences = [gate["sequence"] for gate in _load_catalog_gates()]
        self.assertEqual(len(sequences), len(set(sequences)))

    def test_catalog_gate_versions_are_semver(self) -> None:
        for gate in _load_catalog_gates():
            with self.subTest(gate=gate["gate_id"]):
                self.assertRegex(str(gate["gate_version"]), SEMVER, gate["__path"])

    def test_catalog_gate_identity_is_consistent_with_its_path(self) -> None:
        """A Gate moved into the wrong directory would otherwise go unnoticed."""
        for gate in _load_catalog_gates():
            with self.subTest(gate=gate["gate_id"]):
                self.assertIn(gate["gate_id"], gate["__path"])
                self.assertIn(gate["runtime"]["gate_group"], gate["__path"])

    def test_every_model_binds_a_gate_in_the_frozen_registry(self) -> None:
        dangling: list[str] = []
        for path in sorted(CATALOG.rglob("model.yaml")):
            model = yaml.safe_load(path.read_text())["model"]
            if model["gate_id"] not in GATE_IDS:
                dangling.append(f"{path.relative_to(ROOT)} -> {model['gate_id']}")
        self.assertEqual(dangling, [])

    def test_every_model_version_is_semver(self) -> None:
        for path in sorted(CATALOG.rglob("model.yaml")):
            model = yaml.safe_load(path.read_text())["model"]
            with self.subTest(model=model["model_id"]):
                self.assertRegex(str(model["model_version"]), SEMVER)


if __name__ == "__main__":
    unittest.main()
