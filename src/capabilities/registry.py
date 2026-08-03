"""Authoritative registry of OS-level capabilities.

The architecture contract lists capabilities in
``docs/architecture/capabilities.zh-CN.md``. This module is the single
machine-readable expression of that list; consumers import it instead of
restating the IDs, so a capability cannot be added, renamed or reordered in one
place only.

``tests/test_os_boot.py`` asserts this registry against the architecture
document, which remains the contractual authority.
"""

from typing import Final


CAPABILITY_NAMES: Final[tuple[str, ...]] = (
    "Opportunity Discovery",
    "Knowledge Mining",
    "Rule Learning",
    "Evidence Extraction",
    "ADC Design",
    "Binder Engineering",
    "Patent Analysis",
    "Due Diligence",
    "Portfolio Management",
)
"""Contract names, in the order given by the architecture document."""


def _capability_id(name: str) -> str:
    return name.lower().replace(" ", "_")


CAPABILITY_IDS: Final[tuple[str, ...]] = tuple(
    _capability_id(name) for name in CAPABILITY_NAMES
)
"""Machine-readable capability IDs, derived from the contract names."""
