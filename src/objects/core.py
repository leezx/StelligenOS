"""Architecture-level core object definitions.

These definitions describe the shape of objects handled by the system. They
do not persist records or provide a database-backed repository.
"""

from dataclasses import dataclass
from typing import Final


CORE_OBJECT_TYPES: Final[tuple[str, ...]] = (
    "Opportunity",
    "ClinicalHypothesis",
    "TargetHypothesis",
    "BinderCandidate",
    "ADCConstruct",
    "LeadSeries",
    "DevelopmentCandidate",
    "Asset",
)


@dataclass(frozen=True)
class CoreObject:
    """Minimal identity contract shared by all core object implementations."""

    object_type: str
    object_id: str
    schema_version: str

    def __post_init__(self) -> None:
        if self.object_type not in CORE_OBJECT_TYPES:
            raise ValueError(f"Unsupported core object type: {self.object_type}")
        if not self.object_id:
            raise ValueError("object_id must not be empty")
        if not self.schema_version:
            raise ValueError("schema_version must not be empty")
