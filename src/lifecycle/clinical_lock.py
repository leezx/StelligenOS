"""Progressive lock states for the v5 clinical/product hypothesis.

This lives in the kernel, not in a GenModule, because both the frozen Gate
contracts in ``src/capabilities/gates.py`` and the
``gen_indication_endpoint_target`` GenModule need the same canonical definition.
Defining it in a GenModule made the Capabilities layer import a module
implementation, inverting the architecture's dependency direction; see
``tests/test_kernel_dependency_direction.py``, which now fails if anything under
``src/`` imports anything under ``genmodules/``.

Like ``state_machine``, this module validates proposed transitions only. It does
not persist state, create evidence, or promote a hypothesis automatically. A lock
state describes how much of the hypothesis is committed, never whether it passed.
"""

from enum import Enum
from typing import Final


class ClinicalLockState(str, Enum):
    """Progressive maturity of the clinical/product hypothesis."""

    EXPLORATORY = "exploratory"
    PROVISIONAL = "provisional"
    ANCHORED = "anchored"
    PRODUCT_LOCKED = "product-locked"
    PROTOCOL_LOCKED = "protocol-locked"
    REGULATORY_LOCKED = "regulatory-locked"


LOCK_ORDER: Final[tuple[ClinicalLockState, ...]] = (
    ClinicalLockState.EXPLORATORY,
    ClinicalLockState.PROVISIONAL,
    ClinicalLockState.ANCHORED,
    ClinicalLockState.PRODUCT_LOCKED,
    ClinicalLockState.PROTOCOL_LOCKED,
    ClinicalLockState.REGULATORY_LOCKED,
)
"""The one authoritative progression. Consumers must not restate this order."""


def can_transition_clinical_lock(
    current: ClinicalLockState, target: ClinicalLockState
) -> bool:
    """Allow only monotonic, single-step maturity transitions."""

    if not isinstance(current, ClinicalLockState) or not isinstance(target, ClinicalLockState):
        return False
    return LOCK_ORDER.index(target) == LOCK_ORDER.index(current) + 1
