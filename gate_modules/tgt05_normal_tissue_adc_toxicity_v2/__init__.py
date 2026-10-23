"""Contract-bounded MOD-TGT05@2.0.0 evidence producer (inactive until binding)."""

from .contracts import (
    CoverageAudit,
    ModuleInput,
    NormalizedObservation,
    Proposal,
    RunRejection,
    RunResult,
    SourceRecord,
)
from .module import run

__all__ = [
    "CoverageAudit", "ModuleInput", "NormalizedObservation", "Proposal",
    "RunRejection", "RunResult", "SourceRecord", "run",
]
