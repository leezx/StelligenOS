"""Pure model identity and lifecycle contract adapters.

This module carries no model artifacts, governance records, or persistence.
Implementations of the governance port belong to an external workspace.
"""

from dataclasses import dataclass
import re
from typing import Final, Protocol


MODEL_LIFECYCLE_STANDARD_REF: Final = "ModelLifecycleStandard@1.0.0"
_MODEL_REF_PATTERN: Final = re.compile(
    r"^(?P<model_id>[A-Za-z0-9][A-Za-z0-9._-]*)@"
    r"(?P<version>"
    r"(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)"
    r")(?:-[0-9A-Za-z.-]+)?"
    r"(?:\+[0-9A-Za-z.-]+)?$"
)
_LIFECYCLE_STAGES: Final = frozenset(
    {"initialized", "formal_candidate", "validated", "deprecated"}
)


@dataclass(frozen=True)
class ModelRef:
    """Stable external identity for one model artifact version."""

    model_id: str
    version: str

    def __post_init__(self) -> None:
        parsed = parse_model_ref(f"{self.model_id}@{self.version}")
        if parsed is None:
            raise ValueError("model_id and version must form a valid model reference")

    def as_string(self) -> str:
        return f"{self.model_id}@{self.version}"


@dataclass(frozen=True)
class ModelLifecycleDescriptor:
    """Contract metadata supplied by an external model registry."""

    model_ref: ModelRef
    standard_ref: str = MODEL_LIFECYCLE_STANDARD_REF
    artifact_stage: str = "initialized"
    predecessor_model_ref: ModelRef | None = None

    def __post_init__(self) -> None:
        if self.standard_ref != MODEL_LIFECYCLE_STANDARD_REF:
            raise ValueError(
                "standard_ref must be ModelLifecycleStandard@1.0.0"
            )
        if self.artifact_stage not in _LIFECYCLE_STAGES:
            raise ValueError(f"Unsupported artifact_stage: {self.artifact_stage}")
        if self.predecessor_model_ref == self.model_ref:
            raise ValueError("predecessor_model_ref must differ from model_ref")


@dataclass(frozen=True)
class ModelGovernanceRequest:
    """A request for an external governance operation, not a stored record."""

    model_ref: ModelRef
    operation: str
    rationale_ref: str

    def __post_init__(self) -> None:
        if self.operation not in {"inspect", "validate", "request_promotion"}:
            raise ValueError(f"Unsupported governance operation: {self.operation}")
        if not self.rationale_ref:
            raise ValueError("rationale_ref must not be empty")


class ModelGovernancePort(Protocol):
    """External boundary for model lifecycle governance."""

    def submit(self, request: ModelGovernanceRequest) -> str:
        """Submit a request externally and return its external reference."""

        ...


def parse_model_ref(value: str) -> tuple[str, str] | None:
    """Parse ``model_id@SemVer`` without consulting a registry or filesystem."""

    match = _MODEL_REF_PATTERN.fullmatch(value)
    if match is None:
        return None
    return match.group("model_id"), match.group("version")
