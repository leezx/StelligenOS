#!/usr/bin/env python3
"""Validate an external runtime request and print its handover envelope.

This script does **not** execute anything. It validates that a request conforms
to the contract in ``src/repository/external_runtime.py`` and prints the JSON
envelope that an external controlled runtime consumes.

Execution was deliberately removed: running an arbitrary command from inside
this repository cannot be isolated in-process. See the module docstring in
``src/repository/external_runtime.py`` for the demonstrated holes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.repository.external_runtime import ExternalRuntimeRequest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-ref", required=True)
    parser.add_argument("--workspace-path", required=True)
    parser.add_argument("--output-root-path", required=True)
    parser.add_argument("--input-ref", required=True)
    parser.add_argument("--run-context-ref", required=True)
    parser.add_argument("--output-ref", required=True)
    parser.add_argument(
        "--sandbox-profile-ref",
        required=True,
        help=(
            "external: reference naming the controlled environment the "
            "implementing runtime must execute in"
        ),
    )
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--command", nargs="+", required=True)
    args = parser.parse_args()

    request = ExternalRuntimeRequest(
        runtime_ref=args.runtime_ref,
        command=tuple(args.command),
        workspace_path=args.workspace_path,
        output_root_path=args.output_root_path,
        input_ref=args.input_ref,
        run_context_ref=args.run_context_ref,
        output_ref=args.output_ref,
        sandbox_profile_ref=args.sandbox_profile_ref,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(request.envelope, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
