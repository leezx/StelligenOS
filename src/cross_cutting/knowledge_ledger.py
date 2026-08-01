"""External Knowledge Ledger port.

The port defines the integration boundary only. Implementations must live in
an external workspace and must not turn StelligenOS into a data store.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LedgerEntryRequest:
    """Metadata needed to request an external ledger operation."""

    entry_type: str
    subject_id: str
    schema_version: str


class KnowledgeLedgerPort(Protocol):
    """Port for external ledger adapters; no persistence is provided here."""

    def record(self, request: LedgerEntryRequest) -> str:
        """Submit a request to an external ledger and return its reference."""

        ...
