"""Interpreter resolution and out-of-process delegation.

The module runner lives in the StelligenOS repository environment, which
deliberately holds only orchestration dependencies. The declared antibody
scientific stack (ANARCI, abnumber, biopython, ImmuneBuilder, torch, ...) lives
in the shared antibody runtime. Probing tool availability with the *runner*
interpreter therefore reports every scientific tool as missing even when it is
installed.

This module resolves both interpreters, probes each declared python import in
whichever interpreter can satisfy it, and routes a computation either in-process
or through a JSON sidecar in the shared runtime.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

MODULE_ROOT = Path(__file__).resolve().parents[1]
GENMODULES_ROOT = MODULE_ROOT.parent
REPO_ROOT = GENMODULES_ROOT.parent

SHARED_RUNTIME_RELPATH = Path("SOFTWARES/venvs/antibody_pipeline_shared/py311/bin/python")

# Heavyweight model inference that must stay behind the module's
# ``external_execution_policy: disabled_by_default`` boundary.
EXTERNAL_EXECUTION_OPS = frozenset({"predict_structure"})

_SIDECAR_BOOTSTRAP = (
    "import sys; sys.path.insert(0, {module_root!r}); "
    "from lib.sidecar import main; main()"
)


def shared_python() -> Path | None:
    """Locate the shared antibody runtime interpreter, if present.

    Interpreter paths are deliberately *not* resolved through symlinks. A venv's
    identity is its own path: both this repository's ``.venv/bin/python`` and the
    shared runtime's ``bin/python`` are symlinks to the same framework
    interpreter, and resolving them collapses two different environments onto one
    path, which would make the shared runtime look like a duplicate of the runner
    and silently drop it.
    """
    candidates: list[Path] = []
    override = os.environ.get("ANTIBODY_SHARED_PYTHON")
    if override:
        candidates.append(Path(override))
    workspace = os.environ.get("BIOWORKSPACE_ROOT")
    if workspace:
        candidates.append(Path(workspace) / SHARED_RUNTIME_RELPATH)
    candidates.append(REPO_ROOT / SHARED_RUNTIME_RELPATH)
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def interpreters() -> list[dict[str, Any]]:
    """Ordered interpreters used to satisfy declared python imports."""
    resolved: list[dict[str, Any]] = [{"role": "runner", "path": sys.executable}]
    shared = shared_python()
    if shared and str(shared) != sys.executable:
        resolved.append({"role": "shared_antibody_runtime", "path": str(shared)})
    return resolved


def _probe_in_process(modules: list[str]) -> dict[str, str | None]:
    import importlib.metadata as md
    import importlib.util

    found: dict[str, str | None] = {}
    for name in modules:
        try:
            if importlib.util.find_spec(name) is None:
                continue
        except (ImportError, ModuleNotFoundError, ValueError):
            continue
        try:
            found[name] = md.version(name)
        except Exception:
            found[name] = "unknown"
    return found


_PROBE_SCRIPT = """
import importlib.metadata as md, importlib.util, json, sys
found = {}
for name in json.loads(sys.argv[1]):
    try:
        if importlib.util.find_spec(name) is None:
            continue
    except Exception:
        continue
    try:
        found[name] = md.version(name)
    except Exception:
        found[name] = "unknown"
print(json.dumps(found))
"""


def _probe_subprocess(python: Path, modules: list[str]) -> dict[str, str | None]:
    try:
        completed = subprocess.run(
            [str(python), "-c", _PROBE_SCRIPT, json.dumps(modules)],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (OSError, subprocess.SubprocessError):
        return {}
    if completed.returncode != 0:
        return {}
    try:
        return json.loads(completed.stdout.strip() or "{}")
    except json.JSONDecodeError:
        return {}


def probe_python_imports(modules: list[str]) -> dict[str, dict[str, Any]]:
    """Report where each python import is satisfiable, across interpreters.

    The first interpreter that satisfies an import wins, so an import available
    in-process never pays for a subprocess.
    """
    wanted = sorted(set(modules))
    report: dict[str, dict[str, Any]] = {
        name: {"status": "missing", "interpreter": None, "role": None, "version": None}
        for name in wanted
    }
    for entry in interpreters():
        outstanding = [name for name in wanted if report[name]["status"] == "missing"]
        if not outstanding:
            break
        if entry["role"] == "runner":
            found = _probe_in_process(outstanding)
        else:
            found = _probe_subprocess(Path(entry["path"]), outstanding)
        for name, version in found.items():
            report[name] = {
                "status": "available",
                "interpreter": entry["path"],
                "role": entry["role"],
                "version": version,
            }
    return report


class OpUnavailable(RuntimeError):
    """A computation could not run in any resolved interpreter."""


def run_op(
    op: str,
    payload: dict[str, Any],
    requires: list[str],
    *,
    allow_external: bool = False,
    timeout: int = 3600,
) -> dict[str, Any]:
    """Run a sidecar operation in-process when possible, else in the shared runtime.

    ``requires`` lists the python imports the operation needs. Operations in
    ``EXTERNAL_EXECUTION_OPS`` run only when ``allow_external`` is set, honouring
    the module's external-execution policy.
    """
    if op in EXTERNAL_EXECUTION_OPS and not allow_external:
        raise OpUnavailable(
            f"{op} is gated by external_execution_policy=disabled_by_default; "
            "re-run with --allow-external to enable it"
        )

    availability = probe_python_imports(requires)
    missing = sorted(name for name, rec in availability.items() if rec["status"] == "missing")
    if missing:
        raise OpUnavailable(f"{op} requires unavailable imports: {', '.join(missing)}")

    roles = {rec["role"] for rec in availability.values()}
    if roles == {"runner"}:
        from lib import sidecar

        return sidecar.dispatch(op, payload)

    python = shared_python()
    if python is None:
        raise OpUnavailable(f"{op} needs the shared antibody runtime, which was not found")
    try:
        completed = subprocess.run(
            [str(python), "-c", _SIDECAR_BOOTSTRAP.format(module_root=str(MODULE_ROOT))],
            input=json.dumps({"op": op, "payload": payload}),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise OpUnavailable(f"{op} timed out after {timeout}s") from error
    except (OSError, subprocess.SubprocessError) as error:
        raise OpUnavailable(f"{op} could not start in the shared runtime: {error}") from error

    if completed.returncode != 0:
        detail = (completed.stderr or "").strip().splitlines()
        raise OpUnavailable(f"{op} failed in the shared runtime: {detail[-1] if detail else 'no stderr'}")
    try:
        response = json.loads(completed.stdout.strip() or "{}")
    except json.JSONDecodeError as error:
        raise OpUnavailable(f"{op} returned unparsable output") from error
    if "error" in response:
        raise OpUnavailable(f"{op} failed in the shared runtime: {response['error']}")
    return response["result"]
