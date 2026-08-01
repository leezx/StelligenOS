"""Lifecycle contracts for StelligenOS."""

from .state_machine import ALLOWED_TRANSITIONS, LifecycleStage, can_transition

__all__ = ["ALLOWED_TRANSITIONS", "LifecycleStage", "can_transition"]
