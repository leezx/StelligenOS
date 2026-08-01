"""Stable, content-addressed IDs for the Phase 1A records."""

from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def stable_id(prefix: str, value: Any) -> str:
    digest = sha256(canonical_json(value).encode()).hexdigest()[:16]
    return f"{prefix}:{digest}"


def validate_id(value: str, prefix: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(rf"{re.escape(prefix)}:[A-Za-z0-9_.-]+", value):
        raise ValueError(f"{value!r} is not a valid {prefix} ID")
