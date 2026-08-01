#!/usr/bin/env python3
"""CLI runner for epitope_conditioned_de_novo_antibody_discovery@0.1.0."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Any

import yaml

from stages import STAGES, STAGE_FUNCTIONS, validate_discovery, write_yaml


MODULE_ROOT = Path(__file__).resolve().parent
MODULE_CONFIG = MODULE_ROOT / "module.yaml"
SOFTWARE_CONFIG = MODULE_ROOT / "config/software_manifest.yaml"
DATA_CONFIG = MODULE_ROOT / "config/data_manifest.template.yaml"


def load_yaml(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return payload


def _safe_id(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    if not normalized:
        raise ValueError("Identifier becomes empty after normalization")
    return normalized


def software_doctor() -> dict[str, Any]:
    manifest = load_yaml(SOFTWARE_CONFIG)["software"]
    tools: dict[str, dict[str, Any]] = {}
    for category, entries in manifest.items():
        for entry in entries:
            kind, check = entry["kind"], entry["check"]
            resolved = None
            if kind == "executable":
                resolved = shutil.which(check)
            elif kind == "python_import":
                try:
                    resolved = "importable" if importlib.util.find_spec(check) is not None else None
                except (ImportError, ModuleNotFoundError):
                    resolved = None
            elif kind == "env_path":
                candidate = os.environ.get(check)
                resolved = candidate if candidate and Path(candidate).exists() else None
            tools[entry["id"]] = {
                "category": category,
                "kind": kind,
                "check": check,
                "status": "available" if resolved else "missing",
                "resolved": resolved,
                "required_for": entry["required_for"],
            }
    data_status: dict[str, dict[str, Any]] = {}
    for entry in load_yaml(DATA_CONFIG)["data"]:
        candidate = os.environ.get(entry["env_var"])
        data_status[entry["id"]] = {
            "env_var": entry["env_var"],
            "status": "available" if candidate and Path(candidate).exists() else "missing",
            "resolved": candidate,
            "required_for": entry["required_for"],
            "purpose": entry["purpose"],
            "licence_review_required": entry["licence_review_required"],
        }
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "tools": tools,
        "data": data_status,
        "summary": {
            "tools_available": sum(item["status"] == "available" for item in tools.values()),
            "tools_total": len(tools),
            "data_available": sum(item["status"] == "available" for item in data_status.values()),
            "data_total": len(data_status),
        },
    }


def create_run(
    input_path: str | Path,
    output_root: str | Path,
    mode: str = "execute",
    run_id: str | None = None,
) -> dict[str, Any]:
    discovery = validate_discovery(load_yaml(input_path))
    digest = sha256(yaml.safe_dump(discovery, sort_keys=True).encode()).hexdigest()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    actual_run_id = _safe_id(run_id or f"{timestamp}-{digest[:8]}")
    run_dir = Path(output_root).resolve() / _safe_id(discovery["asset_id"]) / actual_run_id
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    write_yaml(run_dir / "normalized_input.yaml", discovery)
    status = software_doctor()
    write_yaml(run_dir / "software_status.yaml", status)
    module = load_yaml(MODULE_CONFIG)["module"]
    manifest = {
        "run_id": actual_run_id,
        "asset_id": discovery["asset_id"],
        "discovery_id": discovery["discovery_id"],
        "module_id": module["module_id"],
        "module_version": module["module_version"],
        "input_contract": module["input_contract"],
        "output_contract": module["output_contract"],
        "mode": mode,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_sha256": digest,
        "run_dir": str(run_dir),
        "external_programs_executed": False,
        "stages": {stage_id: {"name": name, "status": "pending"} for stage_id, name in STAGES},
    }
    write_yaml(run_dir / "run_manifest.yaml", manifest)
    return {"input_path": str(Path(input_path).resolve()), "run_dir": str(run_dir), "mode": mode}


def _load_previous(run_dir: Path) -> dict[str, Any]:
    previous = {}
    for stage_id, _ in STAGES:
        path = run_dir / stage_id / "result.yaml"
        if path.exists():
            previous[stage_id] = load_yaml(path)
    return previous


def execute_stage(state: dict[str, Any], stage_id: str) -> dict[str, Any]:
    if stage_id not in STAGE_FUNCTIONS:
        raise KeyError(f"Unknown stage: {stage_id}")
    run_dir = Path(state["run_dir"])
    manifest = load_yaml(run_dir / "run_manifest.yaml")
    stage_dir = run_dir / stage_id
    stage_dir.mkdir(parents=True, exist_ok=True)
    if state["mode"] == "plan":
        result = {
            "stage_id": stage_id,
            "name": dict(STAGES)[stage_id],
            "status": "planned",
            "external_programs_executed": False,
        }
    else:
        context = {
            "discovery": load_yaml(run_dir / "normalized_input.yaml"),
            "run_dir": str(run_dir),
            "software_status": load_yaml(run_dir / "software_status.yaml"),
            "previous": _load_previous(run_dir),
        }
        result = {
            "stage_id": stage_id,
            "name": dict(STAGES)[stage_id],
            "external_programs_executed": False,
            **STAGE_FUNCTIONS[stage_id](context),
        }
    write_yaml(stage_dir / "result.yaml", result)
    manifest["stages"][stage_id]["status"] = result["status"]
    manifest["stages"][stage_id]["result"] = str(stage_dir / "result.yaml")
    manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_yaml(run_dir / "run_manifest.yaml", manifest)
    return state


def finalize_run(state: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(state["run_dir"])
    manifest = load_yaml(run_dir / "run_manifest.yaml")
    statuses = [record["status"] for record in manifest["stages"].values()]
    allowed = {"complete", "complete_with_gaps", "planned"}
    manifest["status"] = "complete" if all(status in allowed for status in statuses) else "blocked"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_yaml(run_dir / "run_manifest.yaml", manifest)
    return state | {"status": manifest["status"]}


def run_all(input_path: str | Path, output_root: str | Path, mode: str) -> dict[str, Any]:
    state = create_run(input_path, output_root, mode)
    for stage_id, _ in STAGES:
        state = execute_stage(state, stage_id)
    return finalize_run(state)


def _print_doctor(status: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(status, indent=2))
        return
    summary = status["summary"]
    print(f"Tools: {summary['tools_available']}/{summary['tools_total']} available")
    print(f"Data roots: {summary['data_available']}/{summary['data_total']} available")
    for tool_id, record in status["tools"].items():
        print(f"{record['status']:9} tool {tool_id:24} {record['check']}")
    for data_id, record in status["data"].items():
        print(f"{record['status']:9} data {data_id:24} ${record['env_var']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-steps")
    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    run = subparsers.add_parser("run")
    run.add_argument("--input", required=True)
    run.add_argument("--output-root", required=True)
    run.add_argument("--mode", choices=("plan", "execute"), default="execute")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list-steps":
        for stage_id, name in STAGES:
            print(f"{stage_id}\t{name}")
        return 0
    if args.command == "doctor":
        _print_doctor(software_doctor(), args.json)
        return 0
    if args.command == "run":
        state = run_all(args.input, args.output_root, args.mode)
        print(json.dumps(state, indent=2))
        return 0 if state["status"] == "complete" else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
