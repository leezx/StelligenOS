"""Adapter boundary for runtimes owned by an external workspace.

What this module does and does not guarantee
--------------------------------------------

It does **not** sandbox the command. A child process can name any absolute path,
so checking ``workspace_path`` and ``output_root_path`` cannot stop a write into
StelligenOS. In-process prevention of writes by an arbitrary child is not
achievable here, and claiming otherwise would be worse than not claiming it.

What is enforced instead, in layers:

1. **Execution is opt-in.** Without ``execution_enabled`` nothing runs.
2. **Isolation is attested, not assumed.** The caller must supply a
   ``sandbox_profile_ref`` describing the controlled environment the command
   runs in. The repository cannot verify that claim, so it records it as an
   auditable external reference and refuses to run without one.
3. **The environment is an allowlist, not an inheritance.** Credentials and
   tokens held by the parent process are not passed through, and ``HOME`` is
   redirected into the external workspace.
4. **Repository mutation is detected and raised.** The repository is
   fingerprinted before and after the run. This is detection, not prevention:
   by the time it fires the write already happened. It exists so that a violated
   boundary fails loudly instead of silently.

True write isolation must come from the environment named by
``sandbox_profile_ref`` — a container, a read-only bind mount, or a host that
does not have this repository on it at all.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Protocol


REPO_ROOT = Path(__file__).resolve().parents[2]

INHERITED_ENVIRONMENT_KEYS: Final[tuple[str, ...]] = (
    "PATH",
    "LANG",
    "LC_ALL",
    "TZ",
    "TMPDIR",
)
"""The only parent variables an external command may inherit.

``HOME`` is deliberately absent. Inheriting it would expose ``~/.aws``,
``~/.ssh`` and similar; it is set to the external workspace instead, so a tool
that writes to ``$HOME`` stays outside the repository.
"""

_FINGERPRINT_EXCLUDED_PARTS: Final[frozenset[str]] = frozenset(
    {".git", "__pycache__"}
)
_FINGERPRINT_EXCLUDED_NAMES: Final[frozenset[str]] = frozenset({".DS_Store"})


class RepositoryMutationError(RuntimeError):
    """An external command changed the StelligenOS repository."""


def _require_external_ref(reference: str) -> str:
    if not reference.startswith("external:"):
        raise ValueError("External runtime requires external references")
    return reference


def _require_external_path(path_value: str, label: str) -> Path:
    path = Path(path_value).expanduser().resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError:
        return path
    raise ValueError(f"{label} must be outside the StelligenOS repository")


def _repository_fingerprint() -> dict[str, str]:
    """Content hash of every file in the repository.

    Hashes contents rather than size and mtime, so an in-place edit of the same
    length cannot slip through.
    """

    fingerprint: dict[str, str] = {}
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(REPO_ROOT)
        if _FINGERPRINT_EXCLUDED_PARTS.intersection(relative.parts):
            continue
        if path.name in _FINGERPRINT_EXCLUDED_NAMES:
            continue
        fingerprint[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return fingerprint


def _describe_mutations(before: dict[str, str], after: dict[str, str]) -> list[str]:
    changes: list[str] = []
    for path in sorted(set(before) | set(after)):
        old = before.get(path)
        new = after.get(path)
        if old == new:
            continue
        if old is None:
            changes.append(f"created: {path}")
        elif new is None:
            changes.append(f"deleted: {path}")
        else:
            changes.append(f"modified: {path}")
    return changes


@dataclass(frozen=True)
class ExternalRuntimeRequest:
    """A request whose inputs and outputs are owned outside StelligenOS."""

    runtime_ref: str
    command: tuple[str, ...]
    workspace_path: str
    output_root_path: str
    input_ref: str
    run_context_ref: str
    output_ref: str
    sandbox_profile_ref: str
    execution_enabled: bool = False
    timeout_seconds: int = 1800

    def __post_init__(self) -> None:
        for reference in (
            self.runtime_ref,
            self.input_ref,
            self.run_context_ref,
            self.output_ref,
            self.sandbox_profile_ref,
        ):
            _require_external_ref(reference)
        if not self.command:
            raise ValueError("External runtime command cannot be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("External runtime timeout must be positive")
        _require_external_path(self.workspace_path, "workspace_path")
        _require_external_path(self.output_root_path, "output_root_path")


@dataclass(frozen=True)
class ExternalRuntimeResult:
    """An external result envelope; process output is intentionally discarded."""

    runtime_ref: str
    run_context_ref: str
    output_ref: str
    sandbox_profile_ref: str
    status: str
    exit_code: int


class ExternalRuntimePort(Protocol):
    def run(self, request: ExternalRuntimeRequest) -> ExternalRuntimeResult:
        """Run an external command without persisting data in StelligenOS."""


class SubprocessExternalRuntime:
    """Run an opt-in external command, treating repository mutation as a fault.

    This class does not isolate the command. See the module docstring for what is
    and is not guaranteed.
    """

    def run(self, request: ExternalRuntimeRequest) -> ExternalRuntimeResult:
        if not request.execution_enabled:
            raise PermissionError(
                "External runtime execution is disabled; pass an explicit opt-in"
            )

        workspace = _require_external_path(request.workspace_path, "workspace_path")
        output_root = _require_external_path(
            request.output_root_path, "output_root_path"
        )
        if not workspace.is_dir():
            raise NotADirectoryError(
                f"External workspace is not a directory: {workspace}"
            )
        if not output_root.is_dir():
            raise NotADirectoryError(
                f"External output root is not a directory: {output_root}"
            )

        environment = {
            key: os.environ[key]
            for key in INHERITED_ENVIRONMENT_KEYS
            if key in os.environ
        }
        environment["HOME"] = str(workspace)
        environment.update(
            {
                "STELLIGEN_RUNTIME_REF": request.runtime_ref,
                "STELLIGEN_INPUT_REF": request.input_ref,
                "STELLIGEN_RUN_CONTEXT_REF": request.run_context_ref,
                "STELLIGEN_OUTPUT_REF": request.output_ref,
                "STELLIGEN_OUTPUT_ROOT": str(output_root),
                "STELLIGEN_SANDBOX_PROFILE_REF": request.sandbox_profile_ref,
            }
        )

        before = _repository_fingerprint()
        try:
            completed = subprocess.run(
                request.command,
                cwd=workspace,
                env=environment,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=request.timeout_seconds,
            )
        finally:
            mutations = _describe_mutations(before, _repository_fingerprint())
        if mutations:
            raise RepositoryMutationError(
                "External runtime modified the StelligenOS repository: "
                + "; ".join(mutations)
            )

        status = "completed" if completed.returncode == 0 else "failed"
        return ExternalRuntimeResult(
            runtime_ref=request.runtime_ref,
            run_context_ref=request.run_context_ref,
            output_ref=request.output_ref,
            sandbox_profile_ref=request.sandbox_profile_ref,
            status=status,
            exit_code=completed.returncode,
        )
