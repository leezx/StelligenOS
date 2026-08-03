"""Pure lifecycle transition rules.

The state machine validates proposed transitions only. It does not persist
state, create evidence, or promote an object automatically.
"""

from enum import StrEnum
from typing import Final


class LifecycleStage(StrEnum):
    OPPORTUNITY_GENERATION = "Opportunity Generation"
    OPPORTUNITY_VALIDATION = "Opportunity Validation"
    ASSET_GENERATION = "Asset Generation"
    ASSET_DEVELOPMENT = "Asset Development"


LIFECYCLE_STAGE_IDS: Final[tuple[str, ...]] = tuple(
    stage.name.lower() for stage in LifecycleStage
)
"""Machine-readable stage IDs, derived from the enum rather than restated.

``LifecycleStage`` carries operator-facing names; consumers that need IDs take
them from here, so a renamed or reordered stage cannot leave a second copy
behind.
"""


ALLOWED_TRANSITIONS: Final[dict[LifecycleStage, frozenset[LifecycleStage]]] = {
    LifecycleStage.OPPORTUNITY_GENERATION: frozenset(
        {LifecycleStage.OPPORTUNITY_VALIDATION}
    ),
    LifecycleStage.OPPORTUNITY_VALIDATION: frozenset(
        {LifecycleStage.ASSET_GENERATION}
    ),
    LifecycleStage.ASSET_GENERATION: frozenset(
        {LifecycleStage.ASSET_DEVELOPMENT}
    ),
    LifecycleStage.ASSET_DEVELOPMENT: frozenset(),
}


def can_transition(current: LifecycleStage, proposed: LifecycleStage) -> bool:
    """Return whether a proposed transition is allowed by the contract."""

    return proposed in ALLOWED_TRANSITIONS[current]
