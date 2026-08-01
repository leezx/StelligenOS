"""Machine validation for antibody GenModule v0.4.0 contracts.

The YAML files are the published contract. This module is deliberately small and
dependency-light so the runner and downstream adapters execute the same checks.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import yaml


class ContractViolation(ValueError):
    """Raised when an artifact does not satisfy a published machine contract."""


def load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("contract"), dict):
        raise ContractViolation(f"Invalid contract document: {path}")
    return payload


def sha256_file(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stage_catalog_sha256(stage_ids: list[str] | tuple[str, ...]) -> str:
    encoded = json.dumps(list(stage_ids), ensure_ascii=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def artifact_ref(path: str | Path, run_dir: str | Path) -> dict[str, Any]:
    artifact = Path(path).resolve()
    root = Path(run_dir).resolve()
    try:
        relative = artifact.relative_to(root)
    except ValueError as error:
        raise ContractViolation(f"Artifact is outside the run directory: {artifact}") from error
    if not artifact.is_file():
        raise ContractViolation(f"Artifact does not exist: {artifact}")
    return {
        "path": relative.as_posix(),
        "sha256": sha256_file(artifact),
        "bytes": artifact.stat().st_size,
    }


def _type_matches(value: Any, declared: str) -> bool:
    if declared == "nonempty_string":
        return isinstance(value, str) and bool(value.strip())
    if declared == "string":
        return isinstance(value, str)
    if declared == "string_or_null":
        return value is None or isinstance(value, str)
    if declared == "mapping":
        return isinstance(value, dict)
    if declared == "mapping_or_null":
        return value is None or isinstance(value, dict)
    if declared == "list":
        return isinstance(value, list)
    if declared == "list_or_null":
        return value is None or isinstance(value, list)
    return False


def validate_input_payload(payload: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    """Validate an input record and return an auditable validation receipt."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        raise ContractViolation("Input must be a YAML mapping")

    accepted = contract["compatibility"]["accepted_source_contracts"]
    source_contract = payload.get("input_contract")
    if source_contract not in accepted:
        errors.append(f"input_contract {source_contract!r} is not accepted")

    root = contract["root"]
    for field in root["required"]:
        if field not in payload:
            errors.append(f"missing required field: {field}")
    for field, declared in root["fields"].items():
        if field in payload and not _type_matches(payload[field], declared):
            errors.append(f"{field} must be {declared}")

    for object_name, object_contract in contract["objects"].items():
        value = payload.get(object_name)
        if not isinstance(value, dict):
            continue
        for field in object_contract["required"]:
            if field not in value:
                errors.append(f"missing required field: {object_name}.{field}")
        for field, declared in object_contract["fields"].items():
            if field in value and not _type_matches(value[field], declared):
                errors.append(f"{object_name}.{field} must be {declared}")

    format_name = str(payload.get("format") or "").casefold()
    sequences = payload.get("sequences")
    if isinstance(sequences, dict) and format_name not in {"vhh", "nanobody"}:
        if not _type_matches(sequences.get("vl"), "nonempty_string"):
            errors.append("sequences.vl is required unless format is VHH or nanobody")

    receipt = {
        "status": "passed" if not errors else "failed",
        "contract_ref": contract["contract"]["ref"],
        "source_contract": source_contract,
        "normalization_target": contract["compatibility"]["normalization_target"],
        "errors": errors,
    }
    if errors:
        raise ContractViolation("; ".join(errors))
    return receipt


def _validate_artifact_reference(
    reference: Any,
    run_dir: Path,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(reference, dict):
        errors.append(f"{label} artifact reference is missing")
        return
    missing = [field for field in ("path", "sha256", "bytes") if field not in reference]
    if missing:
        errors.append(f"{label} artifact reference missing: {', '.join(missing)}")
        return
    candidate = (run_dir / str(reference["path"])).resolve()
    try:
        candidate.relative_to(run_dir)
    except ValueError:
        errors.append(f"{label} artifact path escapes run directory")
        return
    if not candidate.is_file():
        errors.append(f"{label} artifact does not exist: {reference['path']}")
        return
    actual_bytes = candidate.stat().st_size
    if reference["bytes"] != actual_bytes:
        errors.append(f"{label} artifact byte count mismatch")
    actual_sha = sha256_file(candidate)
    if reference["sha256"] != actual_sha:
        errors.append(f"{label} artifact checksum mismatch")


def validate_output_package(
    run_dir: str | Path,
    manifest: dict[str, Any],
    contract: dict[str, Any],
    *,
    raise_on_error: bool = False,
) -> dict[str, Any]:
    """Validate a run package against exact identity, catalogue, and checksums."""
    root = Path(run_dir).resolve()
    errors: list[str] = []
    producer = contract["producer"]
    expected_stages = list(contract["accepted_stage_catalogue"]["stages"])

    expected_identity = {
        "manifest_contract": producer["manifest_contract"],
        "module_id": producer["module_id"],
        "module_version": producer["module_version"],
        "input_contract": producer["accepted_input_contract"],
        "output_contract": contract["contract"]["ref"],
    }
    for field, expected in expected_identity.items():
        if manifest.get(field) != expected:
            errors.append(f"{field} must equal {expected!r}")

    for field in contract["manifest"]["required"]:
        if field not in manifest:
            errors.append(f"manifest missing required field: {field}")
    if manifest.get("mode") not in contract["manifest"]["mode_values"]:
        errors.append(f"unsupported run mode: {manifest.get('mode')!r}")

    execution_order = manifest.get("execution_order")
    if execution_order != expected_stages:
        errors.append("execution_order does not equal the accepted 14-stage catalogue")
    expected_catalog_sha = stage_catalog_sha256(expected_stages)
    if manifest.get("stage_catalog_sha256") != expected_catalog_sha:
        errors.append("stage_catalog_sha256 mismatch")

    stage_records = manifest.get("stages")
    if not isinstance(stage_records, dict) or list(stage_records) != expected_stages:
        errors.append("manifest stage keys do not equal the accepted 14-stage catalogue")
        stage_records = stage_records if isinstance(stage_records, dict) else {}
    for prohibited in contract["accepted_stage_catalogue"]["explicitly_not_registered"]:
        if prohibited in stage_records or (root / prohibited).exists():
            errors.append(f"unregistered stage present: {prohibited}")

    required_result_fields = contract["stage_artifacts"]["required_result_fields"]["all_modes"]
    stage_output_contracts = contract.get("stage_output_contracts")
    if not isinstance(stage_output_contracts, dict) or list(stage_output_contracts) != expected_stages:
        errors.append("contract stage_output_contracts do not cover the exact stage catalogue")
        stage_output_contracts = stage_output_contracts if isinstance(stage_output_contracts, dict) else {}
    for stage_id in expected_stages:
        record = stage_records.get(stage_id)
        if not isinstance(record, dict):
            errors.append(f"missing stage record: {stage_id}")
            continue
        reference = (record.get("artifacts") or {}).get("result")
        _validate_artifact_reference(reference, root, f"stage {stage_id} result", errors)
        result_path = root / stage_id / contract["stage_artifacts"]["result_file"]
        if result_path.is_file():
            result = yaml.safe_load(result_path.read_text())
            if not isinstance(result, dict):
                errors.append(f"stage {stage_id} result must be a mapping")
            else:
                for field in required_result_fields:
                    if field not in result:
                        errors.append(f"stage {stage_id} result missing field: {field}")
                if manifest.get("mode") == "execute":
                    execute_required = (stage_output_contracts.get(stage_id) or {}).get(
                        "execute_required", []
                    )
                    for field in execute_required:
                        if field not in result:
                            errors.append(f"stage {stage_id} execute result missing field: {field}")
                if result.get("stage_id") != stage_id:
                    errors.append(f"stage {stage_id} result stage_id mismatch")

    root_artifacts = manifest.get("artifacts")
    if not isinstance(root_artifacts, dict):
        errors.append("manifest artifacts must be a mapping")
        root_artifacts = {}
    required_root = list(contract["root_artifacts"]["required_all_modes"])
    if manifest.get("mode") == "execute":
        required_root.extend(contract["root_artifacts"]["required_execute"])
    for artifact_name in required_root:
        _validate_artifact_reference(root_artifacts.get(artifact_name), root, artifact_name, errors)

    receipt = {
        "status": "passed" if not errors else "failed",
        "contract_ref": contract["contract"]["ref"],
        "manifest_contract": producer["manifest_contract"],
        "stage_catalog_sha256": expected_catalog_sha,
        "verified_stage_count": len(expected_stages),
        "checksum_algorithm": contract["artifact_integrity"]["algorithm"],
        "errors": errors,
    }
    if raise_on_error and errors:
        raise ContractViolation("; ".join(errors))
    return receipt
