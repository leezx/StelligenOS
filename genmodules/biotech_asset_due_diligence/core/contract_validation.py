"""Small strict validator for Phase 1A entity contracts."""

from __future__ import annotations

from pathlib import Path
import re
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


def _validate_value(value: Any, schema: dict[str, Any], path: str, errors: list[str]) -> None:
    declared = schema.get("type")
    if declared is not None and not _matches(value, declared):
        errors.append(f"{path} has invalid type")
        return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path} must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} has invalid enum value")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path} is empty")
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            errors.append(f"{path} has invalid format")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path} has too few items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_value(item, item_schema, f"{path}[{index}]", errors)
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for field in schema.get("required", []):
            if field not in value:
                errors.append(f"missing required field: {path}.{field}")
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            errors.extend(f"{path} has unknown field: {field}" for field in unknown)
        for field, field_schema in properties.items():
            if field in value and isinstance(field_schema, dict):
                _validate_value(value[field], field_schema, f"{path}.{field}", errors)


def validate_record(record: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ContractError(f"{contract['$id']} record must be a mapping")
    errors: list[str] = []
    _validate_value(record, contract, "record", errors)
    if errors:
        raise ContractError(f"{contract['$id']} invalid: {'; '.join(errors)}")
    return {"status": "passed", "contract_id": contract["$id"], "contract_version": contract["version"]}
