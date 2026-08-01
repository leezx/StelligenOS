#!/usr/bin/env python3
"""CLI runner for antibody_binder_asset_engineering@0.4.0."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Any

import yaml

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from lib import runtime  # noqa: E402
from contract_validation import (  # noqa: E402
    artifact_ref,
    load_contract,
    stage_catalog_sha256,
    validate_input_payload,
    validate_output_package,
)
from stages import (  # noqa: E402
    EXECUTION_ORDER,
    EXTERNAL_ROUTE_STAGES,
    STAGE_FUNCTIONS,
    STAGES,
    validate_binder,
    write_yaml,
)

MODULE_CONFIG = MODULE_ROOT / "module.yaml"
SOFTWARE_CONFIG = MODULE_ROOT / "config/software_manifest.yaml"
DATA_CONFIG = MODULE_ROOT / "config/data_manifest.template.yaml"
INPUT_CONTRACT = MODULE_ROOT / "contracts/existing_binder_asset_input.v0.4.0.yaml"
OUTPUT_CONTRACT = MODULE_ROOT / "contracts/antibody_asset_engineering_package.v0.4.0.yaml"


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


def _find_executable(name: str) -> tuple[str | None, str | None]:
    """Locate an executable on PATH, then in the shared runtime's bin directory.

    Tools installed into the shared antibody environment (ANARCI, ABodyBuilder2,
    ...) are not on the ambient PATH, so a PATH-only check reports an installed
    tool as missing.
    """
    found = shutil.which(name)
    if found:
        return found, "path"
    shared = runtime.shared_python()
    if shared:
        candidate = shared.parent / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate), "shared_antibody_runtime"
    return None, None


def software_doctor() -> dict[str, Any]:
    """Report declared tool and data availability across resolved interpreters."""
    manifest = load_yaml(SOFTWARE_CONFIG)["software"]

    wanted_imports: list[str] = []
    for entries in manifest.values():
        for entry in entries:
            if entry["kind"] == "python_import":
                wanted_imports.append(entry["check"])
    import_report = runtime.probe_python_imports(wanted_imports)

    tools: dict[str, dict[str, Any]] = {}
    for category, entries in manifest.items():
        for entry in entries:
            kind, check = entry["kind"], entry["check"]
            resolved: str | None = None
            role: str | None = None
            version: str | None = None
            if kind == "executable":
                resolved, role = _find_executable(check)
            elif kind == "python_import":
                record = import_report.get(check, {})
                if record.get("status") == "available":
                    resolved = record.get("interpreter")
                    role = record.get("role")
                    version = record.get("version")
            elif kind == "env_path":
                candidate = os.environ.get(check)
                resolved = candidate if candidate and Path(candidate).exists() else None
                role = "environment" if resolved else None
            tools[entry["id"]] = {
                "category": category,
                "kind": kind,
                "check": check,
                "status": "available" if resolved else "missing",
                "resolved": resolved,
                "interpreter_role": role,
                "version": version,
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
        "interpreters": runtime.interpreters(),
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
    binder_path: str | Path,
    output_root: str | Path,
    mode: str = "execute",
    run_id: str | None = None,
    allow_external: bool = False,
) -> dict[str, Any]:
    raw_binder = load_yaml(binder_path)
    module = load_yaml(MODULE_CONFIG)["module"]
    input_contract = load_contract(INPUT_CONTRACT)
    source_input_validation = validate_input_payload(raw_binder, input_contract)
    source_input_contract = raw_binder["input_contract"]
    binder = validate_binder(raw_binder)
    binder["input_contract"] = module["input_contract"]
    normalized_input_validation = validate_input_payload(binder, input_contract)
    digest = sha256(yaml.safe_dump(binder, sort_keys=True).encode()).hexdigest()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    actual_run_id = _safe_id(run_id or f"{timestamp}-{digest[:8]}")
    run_dir = Path(output_root).resolve() / _safe_id(binder["asset_id"]) / actual_run_id
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    write_yaml(run_dir / "normalized_input.yaml", binder)
    status = software_doctor()
    write_yaml(run_dir / "software_status.yaml", status)
    stage_ids = [stage_id for stage_id, _ in STAGES]
    manifest = {
        "manifest_contract": "AntibodyAssetRunManifest@0.4.0",
        "run_id": actual_run_id,
        "asset_id": binder["asset_id"],
        "binder_id": binder["binder_id"],
        "module_id": module["module_id"],
        "module_version": module["module_version"],
        "source_input_contract": source_input_contract,
        "input_contract": module["input_contract"],
        "output_contract": module["output_contract"],
        "mode": mode,
        "allow_external": allow_external,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_sha256": digest,
        "run_dir": str(run_dir),
        "external_programs_executed": False,
        "execution_order": list(EXECUTION_ORDER),
        "stage_catalog_sha256": stage_catalog_sha256(stage_ids),
        "input_contract_validation": {
            "source": source_input_validation,
            "normalized": normalized_input_validation,
        },
        "artifact_integrity": {"algorithm": "sha256", "path_scope": "run_directory_relative"},
        "artifacts": {
            "normalized_input": artifact_ref(run_dir / "normalized_input.yaml", run_dir),
            "software_status": artifact_ref(run_dir / "software_status.yaml", run_dir),
        },
        "contract_validation": {
            "status": "pending",
            "contract_ref": module["output_contract"],
        },
        "stages": {stage_id: {"name": name, "status": "pending"} for stage_id, name in STAGES},
    }
    write_yaml(run_dir / "run_manifest.yaml", manifest)
    return {
        "binder_path": str(Path(binder_path).resolve()),
        "run_dir": str(run_dir),
        "mode": mode,
        "allow_external": allow_external,
    }


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
    binder = load_yaml(run_dir / "normalized_input.yaml")
    software_status = load_yaml(run_dir / "software_status.yaml")
    stage_dir = run_dir / stage_id
    stage_dir.mkdir(parents=True, exist_ok=True)

    if state["mode"] == "plan":
        result = {
            "stage_id": stage_id,
            "status": "planned",
            "name": dict(STAGES)[stage_id],
            "external_programs_executed": False,
        }
    else:
        context = {
            "binder": binder,
            "run_dir": str(run_dir),
            "software_status": software_status,
            "previous": _load_previous(run_dir),
            "allow_external": bool(state.get("allow_external")),
            "module": {
                "module_id": manifest["module_id"],
                "module_version": manifest["module_version"],
            },
            # From the manifest, not the clock: evidence freshness is a property of the
            # run, so re-executing a stage in an old run directory reproduces it.
            "created_at_utc": manifest.get("created_at_utc"),
        }
        stage_result = STAGE_FUNCTIONS[stage_id](context)
        result = {
            "stage_id": stage_id,
            "name": dict(STAGES)[stage_id],
            "external_programs_executed": bool(stage_result.get("external_programs_executed", False)),
            **stage_result,
        }

    write_yaml(stage_dir / "result.yaml", result)
    manifest["stages"][stage_id]["status"] = result["status"]
    manifest["stages"][stage_id]["result"] = str(stage_dir / "result.yaml")
    manifest["stages"][stage_id]["artifacts"] = {
        path.stem if path.name != "result.yaml" else "result": artifact_ref(path, run_dir)
        for path in sorted(stage_dir.iterdir())
        if path.is_file()
    }
    asset_report = run_dir / "asset_report.md"
    if asset_report.is_file():
        manifest["artifacts"]["asset_report"] = artifact_ref(asset_report, run_dir)
    if result.get("external_programs_executed"):
        manifest["external_programs_executed"] = True
    manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_yaml(run_dir / "run_manifest.yaml", manifest)
    return state


def finalize_run(state: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(state["run_dir"])
    manifest = load_yaml(run_dir / "run_manifest.yaml")
    statuses = [record["status"] for record in manifest["stages"].values()]
    acceptable = {"complete", "complete_with_gaps", "planned"}
    manifest["status"] = "complete" if all(status in acceptable for status in statuses) else "blocked"
    manifest["blocked_stages"] = [
        stage_id for stage_id, record in manifest["stages"].items() if record["status"] not in acceptable
    ]
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    output_contract = load_contract(OUTPUT_CONTRACT)
    contract_receipt = validate_output_package(run_dir, manifest, output_contract)
    manifest["contract_validation"] = contract_receipt
    if contract_receipt["status"] != "passed":
        manifest["status"] = "blocked"
        manifest["blocked_stages"].append("output_contract_validation")
    write_yaml(run_dir / "run_manifest.yaml", manifest)
    return state | {
        "status": manifest["status"],
        "blocked_stages": manifest["blocked_stages"],
        "contract_validation": contract_receipt,
    }


def run_all(
    binder_path: str | Path,
    output_root: str | Path,
    mode: str,
    allow_external: bool = False,
) -> dict[str, Any]:
    state = create_run(binder_path, output_root, mode, allow_external=allow_external)
    for stage_id in EXECUTION_ORDER:
        state = execute_stage(state, stage_id)
    return finalize_run(state)


def _print_doctor(status: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(status, indent=2))
        return
    summary = status["summary"]
    print("Interpreters:")
    for entry in status["interpreters"]:
        print(f"  {entry['role']:24} {entry['path']}")
    print(f"Tools: {summary['tools_available']}/{summary['tools_total']} available")
    print(f"Data roots: {summary['data_available']}/{summary['data_total']} available")
    for tool_id, record in status["tools"].items():
        where = record["interpreter_role"] or "-"
        version = record["version"] or ""
        print(f"{record['status']:9} tool {tool_id:24} {record['check']:16} {where:24} {version}")
    for data_id, record in status["data"].items():
        print(f"{record['status']:9} data {data_id:24} ${record['env_var']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-steps", help="show the frozen external route stages")
    subparsers.add_parser("list-internal-steps", help="show internal implementation steps")
    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    run = subparsers.add_parser("run")
    run.add_argument("--binder", required=True)
    run.add_argument("--output-root", required=True)
    run.add_argument("--mode", choices=("plan", "execute"), default="execute")
    run.add_argument("--run-id", default=None)
    run.add_argument(
        "--allow-external",
        action="store_true",
        help="permit heavyweight model inference (structure prediction), which is disabled by default",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list-steps":
        for stage_id, internal_ids in EXTERNAL_ROUTE_STAGES:
            print(f"{stage_id}\t{','.join(internal_ids)}")
        return 0
    if args.command == "list-internal-steps":
        execution_position = {stage_id: index + 1 for index, stage_id in enumerate(EXECUTION_ORDER)}
        for stage_id, name in STAGES:
            print(f"{stage_id}\t{name}\t(executes {execution_position[stage_id]} of {len(EXECUTION_ORDER)})")
        return 0
    if args.command == "doctor":
        _print_doctor(software_doctor(), args.json)
        return 0
    if args.command == "run":
        state = create_run(
            args.binder, args.output_root, args.mode, run_id=args.run_id, allow_external=args.allow_external
        )
        for stage_id in EXECUTION_ORDER:
            state = execute_stage(state, stage_id)
        state = finalize_run(state)
        print(json.dumps(state, indent=2))
        return 0 if state["status"] == "complete" else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
