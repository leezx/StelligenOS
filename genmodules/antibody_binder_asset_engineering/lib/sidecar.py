"""JSON dispatch entry point for computations that need the shared runtime.

Reads ``{"op": ..., "payload": ...}`` on stdin and writes ``{"result": ...}`` or
``{"error": ...}`` on stdout. Nothing else may be printed to stdout, so any tool
that chatters is responsible for writing to stderr.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Callable


def _operations() -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
    from lib import numbering, structure

    return {
        "number_chains": numbering.number_chains,
        "predict_structure": structure.predict_structure,
        "solvent_accessibility": structure.solvent_accessibility,
    }


def dispatch(op: str, payload: dict[str, Any]) -> dict[str, Any]:
    operations = _operations()
    if op not in operations:
        raise KeyError(f"Unknown sidecar operation: {op}")
    return operations[op](payload)


def main() -> int:
    try:
        request = json.loads(sys.stdin.read() or "{}")
        result = dispatch(request["op"], request.get("payload") or {})
    except Exception as error:  # a sidecar failure must surface as data, not a traceback
        json.dump({"error": f"{type(error).__name__}: {error}"}, sys.stdout)
        return 1
    json.dump({"result": result}, sys.stdout, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
