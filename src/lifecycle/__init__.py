"""Lifecycle contracts for StelligenOS."""

from .state_machine import (
    ALLOWED_TRANSITIONS,
    LIFECYCLE_STAGE_IDS,
    LifecycleStage,
    can_transition,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "LIFECYCLE_STAGE_IDS",
    "LifecycleStage",
    "can_transition",
]
