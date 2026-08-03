"""EXT-02 dynamic_gate_context: shell only.

Provides a context-qualified identity so that Gate results are keyed by
``Target x Clinical Context`` instead of by target alone.

This is an adapter shell. It does not modify the 45-Gate topology, any
``gate.yaml``, ``GateInputEnvelope@2.0.0`` or ``GateModelOutput@2.0.0``. The
port method bodies are ``...`` on purpose.

Dependency direction is extension -> kernel. Nothing under ``src/`` may import
this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Protocol

from src.capabilities.gates import GATE_IDS


EXTENSION_ID: Final[str] = "EXT-02"
EXTENSION_VERSION: Final[str] = "0.1.0"
EXECUTION_POLICY: Final[str] = "disabled"


CONTEXT_AXES: Final[tuple[str, ...]] = (
    "indication",
    "disease_stage",
    "line_of_therapy",
    "biomarker_status",
    "combination_setting",
)


@dataclass(frozen=True)
class ClinicalContext:
    """The five axes that change what a target means.

    HER2 in breast cancer, HER2 in CRC and HER2-low are three different
    subjects, not one subject with three attributes.
    """

    indication: str
    disease_stage: str
    line_of_therapy: str
    biomarker_status: str
    combination_setting: str

    def __post_init__(self) -> None:
        for axis in CONTEXT_AXES:
            if not getattr(self, axis):
                raise ValueError(f"clinical context axis {axis} is required")

    @property
    def context_key(self) -> str:
        return "|".join(getattr(self, axis) for axis in CONTEXT_AXES)


@dataclass(frozen=True)
class ScoringSubjectRef:
    """Composite identity of what is actually being scored."""

    target_id: str
    context: ClinicalContext

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("target_id is required")

    @property
    def subject_key(self) -> str:
        return f"{self.target_id}@{self.context.context_key}"


class ContextReusePolicy(str):
    """Whether a Gate result may be reused across clinical contexts.

    Neither automatic inheritance nor automatic reset is safe: inheritance
    smuggles a breast-cancer conclusion into CRC, while reset discards target
    biology that genuinely is indication-independent. The policy must therefore
    be annotated per Gate by a domain expert.
    """

    REUSABLE = "reusable_across_contexts"
    CONTEXT_SPECIFIC = "context_specific"
    UNDECIDED = "undecided_requires_expert_annotation"


@dataclass(frozen=True)
class GateContextBinding:
    """Per-Gate reuse annotation. Defaults to undecided, never to reusable."""

    gate_id: str
    reuse_policy: str = ContextReusePolicy.UNDECIDED

    def __post_init__(self) -> None:
        if self.gate_id not in GATE_IDS:
            raise ValueError(f"unknown kernel gate_id: {self.gate_id}")
        allowed = (
            ContextReusePolicy.REUSABLE,
            ContextReusePolicy.CONTEXT_SPECIFIC,
            ContextReusePolicy.UNDECIDED,
        )
        if self.reuse_policy not in allowed:
            raise ValueError(f"unknown reuse_policy: {self.reuse_policy}")


class ScoringSubjectResolverPort(Protocol):
    """External implementation boundary. Not implemented in this repository."""

    def resolve(self, subject: ScoringSubjectRef, gate_id: str) -> str: ...
