"""Migration reference from the frozen legacy 45-gate system to the canonical
Blueprint v1.3 GateSet lineage.

The legacy topology is NOT modified here: ``src/contracts/gate_system.yaml`` and
``src/capabilities/gates.py`` stay exactly as they are, ``status =
FROZEN_LEGACY``. This module only records the semantic mapping so a migration
PR can point at it. Import-time self-checks assert it still agrees with the
kernel's live 45-gate topology.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping

from src.capabilities.gates import GATE_CATALOG, GATE_GROUPS, GATE_IDS
from src.objects.gate_model import CANONICAL_GATESET_IDS


@dataclass(frozen=True)
class LegacyGateSystem:
    """Identity of the frozen legacy gate system."""

    contract_id: str
    contract_version: str
    topology_version: str
    gate_count: int
    status: str


LEGACY_GATE_SYSTEM: Final[LegacyGateSystem] = LegacyGateSystem(
    contract_id="gate_system",
    contract_version="0.1.0",
    topology_version="0.2.0",
    gate_count=45,
    status="FROZEN_LEGACY",
)


@dataclass(frozen=True)
class LegacyGatechainCrosswalk:
    """One legacy gate chain's semantic destination in the canonical lineage."""

    legacy_chain: str
    legacy_gate_count: int
    canonical_gatesets: tuple[str, ...]
    note: str = ""


_LEGACY_GATECHAIN_CROSSWALK: Final[dict[str, LegacyGatechainCrosswalk]] = {
    "target_opportunity": LegacyGatechainCrosswalk(
        legacy_chain="target_opportunity",
        legacy_gate_count=13,
        canonical_gatesets=(
            "INDICATION_GATESET",
            "PATIENT_TERRITORY_GATESET",
            "ENDPOINT_GATESET",
            "ADC_TARGET_GATESET",
            "ADC_EPITOPE_GATESET",
        ),
    ),
    "product_realization": LegacyGatechainCrosswalk(
        legacy_chain="product_realization",
        legacy_gate_count=16,
        canonical_gatesets=(
            "ADC_EPITOPE_GATESET",
            "ANTIBODY_BINDER_GATESET",
            "LINKER_GATESET",
            "PAYLOAD_GATESET",
            "ADC_DESIGN_GATESET",
            "ADC_HIT_GATESET",
        ),
    ),
    "commercial_executability": LegacyGatechainCrosswalk(
        legacy_chain="commercial_executability",
        legacy_gate_count=16,
        canonical_gatesets=("DEVELOPMENT_CANDIDATE_GATESET",),
        note=(
            "Early IP-whitespace signals are distributed across per-layer gates; "
            "formal FTO / regulatory / transaction concerns map to "
            "DEVELOPMENT_CANDIDATE_GATESET plus the sponsor axis (CURRENT_SYSTEM "
            "v5 section 7), which is not a canonical scientific Gate."
        ),
    ),
}

LEGACY_GATECHAIN_CROSSWALK: Final[Mapping[str, LegacyGatechainCrosswalk]] = (
    MappingProxyType(_LEGACY_GATECHAIN_CROSSWALK)
)


def _check_agrees_with_kernel_topology() -> None:
    if set(_LEGACY_GATECHAIN_CROSSWALK) != set(GATE_GROUPS):
        raise RuntimeError(
            "LEGACY_GATECHAIN_CROSSWALK keys must equal the kernel's GATE_GROUPS"
        )
    if LEGACY_GATE_SYSTEM.gate_count != len(GATE_IDS):
        raise RuntimeError(
            f"LEGACY_GATE_SYSTEM.gate_count {LEGACY_GATE_SYSTEM.gate_count} != "
            f"len(GATE_IDS) {len(GATE_IDS)}"
        )
    by_group: dict[str, int] = {}
    for definition in GATE_CATALOG:
        by_group[definition.group] = by_group.get(definition.group, 0) + 1
    for chain, entry in _LEGACY_GATECHAIN_CROSSWALK.items():
        if entry.legacy_gate_count != by_group.get(chain):
            raise RuntimeError(
                f"{chain}: crosswalk legacy_gate_count {entry.legacy_gate_count} != "
                f"kernel count {by_group.get(chain)}"
            )
        unknown = set(entry.canonical_gatesets) - set(CANONICAL_GATESET_IDS.values())
        if unknown:
            raise RuntimeError(f"{chain}: unknown canonical gatesets {sorted(unknown)}")


_check_agrees_with_kernel_topology()
