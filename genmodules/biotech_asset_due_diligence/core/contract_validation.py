"""Small strict validator for Phase 1A entity contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ContractError(ValueError):
    pass


def load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text())
    if not isinstance(payload, dict) or not payload.get("$id") or not payload.get("version"):
        raise ContractError(f"invalid contract: {path}")
    return payload


def _matches(value: Any, declared: Any) -> bool:
    if declared == "string":
        return isinstance(value, str)
    if declared == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared == "boolean":
        return isinstance(value, bool)
    if declared == "object":
        return isinstance(value, dict)
    if declared == "array":
        return isinstance(value, list)
    if declared == "null":
        return value is None
    if isinstance(declared, list):
        return any(_matches(value, item) for item in declared)
    return True


def validate_record(record: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ContractError(f"{contract['$id']} record must be a mapping")
    errors: list[str] = []
    properties = contract.get("properties", {})
    for field in contract.get("required", []):
        if field not in record:
            errors.append(f"missing required field: {field}")
    if contract.get("additionalProperties") is False:
        unknown = sorted(set(record) - set(properties))
        if unknown:
            errors.append(f"unknown fields: {', '.join(unknown)}")
    for field, schema in properties.items():
        if field not in record:
            continue
        if isinstance(schema, dict):
            if "const" in schema and record[field] != schema["const"]:
                errors.append(f"{field} must equal {schema['const']!r}")
            if "type" in schema:
                declared = schema["type"]
                if not _matches(record[field], declared):
                    errors.append(f"{field} has invalid type")
            if isinstance(record[field], str) and schema.get("minLength", 0) and len(record[field]) < schema["minLength"]:
                errors.append(f"{field} is empty")
            if "enum" in schema and record[field] not in schema["enum"]:
                errors.append(f"{field} has invalid enum value")
    if errors:
        raise ContractError(f"{contract['$id']} invalid: {'; '.join(errors)}")
    return {"status": "passed", "contract_id": contract["$id"], "contract_version": contract["version"]}
