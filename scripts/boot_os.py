#!/usr/bin/env python3
"""Boot the data-free StelligenOS architecture and print its external plan."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.repository.boot import BootRequest, boot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-ref", required=True)
    parser.add_argument("--run-context-ref", required=True)
    parser.add_argument("--policy-ref", required=True)
    args = parser.parse_args()

    report = boot(
        BootRequest(
            workspace_ref=args.workspace_ref,
            run_context_ref=args.run_context_ref,
            policy_ref=args.policy_ref,
        )
    )
    print(json.dumps(asdict(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
