"""Lifecycle contracts for StelligenOS."""

from .clinical_lock import (
    LOCK_ORDER,
    ClinicalLockState,
    can_transition_clinical_lock,
)
from .state_machine import (
    ALLOWED_TRANSITIONS,
    LIFECYCLE_STAGE_IDS,
    LifecycleStage,
    can_transition,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "LIFECYCLE_STAGE_IDS",
    "LOCK_ORDER",
    "ClinicalLockState",
    "LifecycleStage",
    "can_transition",
    "can_transition_clinical_lock",
]
