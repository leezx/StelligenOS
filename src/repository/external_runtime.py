"""Contract boundary for runtimes owned by an external workspace.

This module is contracts only. It defines the request and result envelopes and
the port an external runtime must implement. **It does not execute anything.**

Why there is no executor here
-----------------------------

An earlier revision shipped a ``SubprocessExternalRuntime`` that ran the command
directly, guarded by path checks, an environment allowlist, an attested sandbox
reference, and a before/after repository fingerprint. Review established that
this did not add up to a defensible boundary, and three concrete holes were
demonstrated:

- Writes into ``.git/`` went undetected, because the fingerprint excluded it.
  A written ``.git/hooks/`` entry is arbitrary code execution on a later
  checkout or commit.
- A command could write, read whatever it wanted, then restore the file before
  exiting, so the after-the-fact fingerprint compared equal.
- No filesystem isolation existed at all, so host credentials and the whole
  repository were readable regardless of which environment variables were
  passed.

None of that is fixable in-process. Preventing an arbitrary child process from
reading or writing the filesystem is the job of the execution environment — a
container, a read-only mount, or a host that does not have this repository on
it. So the executor was removed rather than patched, which also puts this module
in line with the rest of ``src/``: contracts and ports, no execution.

An external controlled runtime implements ``ExternalRuntimePort``. This
repository validates the envelope and hands it over; it never runs the command.
"""

from __future__ import annotations

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
    """A request whose inputs and outputs are owned outside StelligenOS.

    Validation here is contract validation, not a security control. It states
    what a conforming request looks like; enforcing isolation while the command
    runs is the implementing runtime's responsibility.
    """

    runtime_ref: str
    command: tuple[str, ...]
    workspace_path: str
    output_root_path: str
    input_ref: str
    run_context_ref: str
    output_ref: str
    sandbox_profile_ref: str
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

    @property
    def envelope(self) -> dict[str, object]:
        """The handover payload for an external runtime implementation."""

        return {
            "runtime_ref": self.runtime_ref,
            "command": list(self.command),
            "workspace_path": self.workspace_path,
            "output_root_path": self.output_root_path,
            "input_ref": self.input_ref,
            "run_context_ref": self.run_context_ref,
            "output_ref": self.output_ref,
            "sandbox_profile_ref": self.sandbox_profile_ref,
            "timeout_seconds": self.timeout_seconds,
            "executed_by": "external_controlled_runtime",
            "executed_in_repository": False,
        }


@dataclass(frozen=True)
class ExternalRuntimeResult:
    """A result envelope reported back by an external runtime.

    Process output is not carried. Results live in the external workspace and
    appear here only as ``output_ref``.

    This is an **inbound** contract: the result is submitted by an external
    implementation, not produced here. So ``status`` and ``exit_code`` must be
    checked against each other. While an in-repository executor derived the two
    together they could not disagree; now nothing upstream guarantees that, and a
    contradictory result would otherwise be accepted and recorded as fact.
    """

    runtime_ref: str
    run_context_ref: str
    output_ref: str
    sandbox_profile_ref: str
    status: str
    exit_code: int

    def __post_init__(self) -> None:
        for reference in (
            self.runtime_ref,
            self.run_context_ref,
            self.output_ref,
            self.sandbox_profile_ref,
        ):
            _require_external_ref(reference)
        if self.status not in ("completed", "failed"):
            raise ValueError("External runtime status must be completed or failed")
        if self.status == "completed" and self.exit_code != 0:
            raise ValueError(
                "a completed external runtime must report exit_code 0, "
                f"got {self.exit_code}"
            )
        if self.status == "failed" and self.exit_code == 0:
            raise ValueError(
                "a failed external runtime must report a non-zero exit_code"
            )


class ExternalRuntimePort(Protocol):
    """Implemented outside StelligenOS, by a runtime that can actually isolate.

    The implementation is responsible for honouring ``sandbox_profile_ref``: the
    repository must be invisible or read-only to the command, and host
    credentials must be unreachable.
    """

    def run(self, request: ExternalRuntimeRequest) -> ExternalRuntimeResult: ...
