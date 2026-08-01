"""Safe adapter boundary for runtimes owned by an external workspace."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


REPO_ROOT = Path(__file__).resolve().parents[2]


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
    execution_enabled: bool = False
    timeout_seconds: int = 1800

    def __post_init__(self) -> None:
        for reference in (
            self.runtime_ref,
            self.input_ref,
            self.run_context_ref,
            self.output_ref,
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
    status: str
    exit_code: int


class ExternalRuntimePort(Protocol):
    def run(self, request: ExternalRuntimeRequest) -> ExternalRuntimeResult:
        """Run an external command without persisting data in StelligenOS."""


class SubprocessExternalRuntime:
    """Execute an explicitly enabled external command with no repository writes."""

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
            raise FileNotFoundError(f"External workspace does not exist: {workspace}")
        if not output_root.exists():
            raise FileNotFoundError(f"External output root does not exist: {output_root}")

        environment = os.environ.copy()
        environment.update(
            {
                "STELLIGEN_RUNTIME_REF": request.runtime_ref,
                "STELLIGEN_INPUT_REF": request.input_ref,
                "STELLIGEN_RUN_CONTEXT_REF": request.run_context_ref,
                "STELLIGEN_OUTPUT_REF": request.output_ref,
                "STELLIGEN_OUTPUT_ROOT": str(output_root),
            }
        )
        completed = subprocess.run(
            request.command,
            cwd=workspace,
            env=environment,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=request.timeout_seconds,
        )
        status = "completed" if completed.returncode == 0 else "failed"
        return ExternalRuntimeResult(
            runtime_ref=request.runtime_ref,
            run_context_ref=request.run_context_ref,
            output_ref=request.output_ref,
            status=status,
            exit_code=completed.returncode,
        )
