"""Guard the architecture's dependency direction: genmodules -> src, never back.

``tests/test_extension_boundary.py`` already forbids ``src/`` -> ``extensions/``.
Nothing forbade ``src/`` -> ``genmodules/``, so PR #45 added a module-level
``from genmodules.gen_indication_endpoint_target.contracts import
ClinicalLockState`` to ``src/capabilities/gates.py`` without any test objecting.
That made the Capabilities layer depend on a module implementation and made the
OS boot path unloadable without that GenModule present.

These tests are the missing symmetric guard.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
KERNEL_ROOT = REPO_ROOT / "src"
GENMODULES_ROOT = REPO_ROOT / "genmodules"


def _kernel_sources() -> list[Path]:
    return sorted(KERNEL_ROOT.rglob("*.py"))


def _imported_roots(source: Path) -> set[str]:
    """Every top-level package this file imports, including inside functions.

    Walking the AST rather than matching line starts is deliberate: a deferred
    import inside a function body is still a dependency, and the reverse edge in
    ``genmodules/gate_model_rule/core/contracts.py`` is exactly that shape.
    """

    tree = ast.parse(source.read_text(), filename=str(source))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import, cannot escape the package
                continue
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots


class KernelDependencyDirectionTests(unittest.TestCase):
    def test_no_kernel_module_imports_a_genmodule(self) -> None:
        offenders = [
            str(source.relative_to(REPO_ROOT))
            for source in _kernel_sources()
            if "genmodules" in _imported_roots(source)
        ]
        self.assertEqual(
            offenders,
            [],
            "src/ must not import genmodules/; move the shared definition into "
            "the kernel and let the GenModule import it instead",
        )

    def test_the_guard_also_catches_deferred_imports(self) -> None:
        """A function-local import must not be able to slip past this test."""

        offenders = [
            path
            for path in GENMODULES_ROOT.rglob("*.py")
            if "src" in _imported_roots(path)
        ]
        self.assertIn(
            "genmodules/gate_model_rule/core/contracts.py",
            [str(path.relative_to(REPO_ROOT)) for path in offenders],
            "this known function-local genmodules -> src import must be visible "
            "to the AST walk, otherwise the guard above proves nothing",
        )

    def test_the_kernel_imports_without_genmodules_on_the_path(self) -> None:
        """Booting the OS must not require any GenModule to be importable."""

        probe = (
            "import sys;"
            "import src.repository.boot, src.capabilities.gates;"
            "leaked=sorted(m for m in sys.modules if m.split('.')[0]=='genmodules');"
            "print(','.join(leaked))"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", probe],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "",
            "importing the kernel pulled in a GenModule",
        )


class CanonicalClinicalLockStateTests(unittest.TestCase):
    def test_the_kernel_owns_the_only_definition(self) -> None:
        definition = re.compile(r"^class ClinicalLockState\b", re.MULTILINE)
        owners = [
            str(source.relative_to(REPO_ROOT))
            for source in sorted(REPO_ROOT.rglob("*.py"))
            if ".git" not in source.parts and definition.search(source.read_text())
        ]
        self.assertEqual(owners, ["src/lifecycle/clinical_lock.py"])

    def test_gate_and_genmodule_share_the_kernel_type(self) -> None:
        from genmodules.gen_indication_endpoint_target import ClinicalLockState as module_state
        from src.capabilities.gates import ClinicalLockState as gate_state
        from src.lifecycle.clinical_lock import ClinicalLockState as kernel_state

        self.assertIs(gate_state, kernel_state)
        self.assertIs(module_state, kernel_state)

    def test_the_lock_progression_is_not_restated_anywhere(self) -> None:
        """One ordering only, so a second copy cannot drift out of step."""

        ordering = re.compile(r"LOCK_ORDER\s*:\s*Final")
        owners = [
            str(source.relative_to(REPO_ROOT))
            for source in sorted(REPO_ROOT.rglob("*.py"))
            if ".git" not in source.parts and ordering.search(source.read_text())
        ]
        self.assertEqual(owners, ["src/lifecycle/clinical_lock.py"])


if __name__ == "__main__":
    unittest.main()
