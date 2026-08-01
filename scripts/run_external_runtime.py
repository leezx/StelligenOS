#!/usr/bin/env python3
"""Run an explicitly enabled external runtime through the OS boundary."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.repository.external_runtime import (  # noqa: E402
    ExternalRuntimeRequest,
    SubprocessExternalRuntime,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-ref", required=True)
    parser.add_argument("--workspace-path", required=True)
    parser.add_argument("--output-root-path", required=True)
    parser.add_argument("--input-ref", required=True)
    parser.add_argument("--run-context-ref", required=True)
    parser.add_argument("--output-ref", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--command", nargs="+", required=True)
    args = parser.parse_args()

    result = SubprocessExternalRuntime().run(
        ExternalRuntimeRequest(
            runtime_ref=args.runtime_ref,
            command=tuple(args.command),
            workspace_path=args.workspace_path,
            output_root_path=args.output_root_path,
            input_ref=args.input_ref,
            run_context_ref=args.run_context_ref,
            output_ref=args.output_ref,
            execution_enabled=args.execute,
            timeout_seconds=args.timeout_seconds,
        )
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
