"""CRC-ADC-TARGET-GATESET-v1: the first context-specific specialization of the
canonical ADC_TARGET_GATESET (runtime side).

Runtime Migration PR D. Frozen dataclasses that validate the TGT-01..TGT-08
gate roster, eight concrete Evidence Ladders, the ADC_TARGET_GATESET@1.0 GateSet
and the CRC refractory-mCRC Instantiation + its context-specific bindings. The
GateSet / Instantiation / Evidence Ladder shape is reused verbatim from PR A
(``decision_model``) and PR B (``gate_model``); PR D adds only the CRC roster,
the concrete ladders and the binding invariants.

* ``TgtGateSpec`` -- one row of the frozen roster: gate_id in TGT-01..TGT-08,
  name from CURRENT_SYSTEM v5 section 6.4, candidate_level L04, gateset_id
  ADC_TARGET_GATESET, gate_version "1.0".
* ``TgtGateContract`` -- one gate's concrete contract: gate_question, the
  three-rung Evidence Ladder (evidence-class semantics only -- no invented
  numeric thresholds), evidence ceiling, allowed / forbidden inference,
  unknown behavior, fatal conditions, and the primary-Module binding
  (MOD-TGT0n; version "0.0.0" == a declared slot, "1.0.0" for TGT-01 whose
  Module was built in PR E2 -- see ``BUILT_MODULE_VERSIONS``). Validation of the
  fields shared with PR B's ``Gate`` is delegated to ``Gate.__post_init__``.
* ``CrcAdcTargetGateSetV1`` -- the whole specialization: roster + GateSet +
  Instantiation + eight gate contracts, with the "exactly TGT-01..TGT-08, in
  order, all L04, all v1.0" invariants.

``CRC-ADC-TARGET-GATESET-v1`` is a program label only; it is never a
``gateset_id`` (import-time check). PR D created no Evidence Production Module;
PR E2 built MOD-TGT01 in ``gate_modules/`` and raised its binding to "1.0.0".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from types import MappingProxyType
from typing import Final, Mapping

from src.objects.decision_model import (
    _require_pattern,
    _require_str_tuple,
    _require_text,
)
from src.objects.gate_model import (
    CANONICAL_GATESET_IDS,
    DOMINANT_EVIDENCE_REGIMES,
    EvidenceLadder,
    Gate,
    GateSet,
    _GATESET_ID,
    _MODULE_ID,
)
from src.objects.decision_model import Instantiation


# --- Frozen roster (CURRENT_SYSTEM v5 section 6.4; regimes per the AI审核方案
#     scoping decision) ----------------------------------------------------

TGT_GATE_IDS: Final[tuple[str, ...]] = (
    "TGT-01",
    "TGT-02",
    "TGT-03",
    "TGT-04",
    "TGT-05",
    "TGT-06",
    "TGT-07",
    "TGT-08",
)

_TGT_GATE_ID = re.compile(r"^TGT-0[1-8]$")

ADC_TARGET_GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
TGT_CANDIDATE_LEVEL: Final[str] = "L04"
TGT_GATE_VERSION: Final[str] = "1.0"
TGT_GATESET_VERSION: Final[str] = "1.0"
#: primary_module_version for a gate whose primary Module is a declared slot,
#: not built. PR D created every gate at this version.
UNBUILT_MODULE_VERSION: Final[str] = "0.0.0"

#: gate_id -> primary_module_version once the Module is built. Runtime Migration
#: PR E2 built MOD-TGT01 (gate_modules/tgt01_adc_modality_precedent/). The other
#: seven TGT gates stay at UNBUILT_MODULE_VERSION until their own PR E3+.
BUILT_MODULE_VERSIONS: Final[Mapping[str, str]] = MappingProxyType({"TGT-01": "1.0.0"})


def expected_primary_module_version(gate_id: str) -> str:
    """The one accepted ``primary_module_version`` for a gate's binding."""

    return BUILT_MODULE_VERSIONS.get(gate_id, UNBUILT_MODULE_VERSION)

#: "CRC-ADC-TARGET-GATESET-v1" is a program / specialization label, never a
#: gateset_id (v5 section 6.4 / PR B identity rule).
PROGRAM_LABEL: Final[str] = "CRC-ADC-TARGET-GATESET-v1"

_TGT_GATE_NAMES: Final[dict[str, str]] = {
    "TGT-01": "ADC Modality Precedent",
    "TGT-02": "Indication-Specific Malignant-Cell Coverage",
    "TGT-03": "Treatment / Metastatic Persistence",
    "TGT-04": "Tumor Surface Availability / Density Plausibility",
    "TGT-05": "Normal-Tissue Fatal Liability",
    "TGT-06": "Internalization / Trafficking Addressability",
    "TGT-07": "Shedding / Soluble-Antigen / Sink Liability",
    "TGT-08": "Target Opportunity / Competition / IP Whitespace",
}
TGT_GATE_NAMES: Final[Mapping[str, str]] = MappingProxyType(_TGT_GATE_NAMES)

_TGT_GATE_REGIMES: Final[dict[str, str]] = {
    "TGT-01": "PUBLIC_PRIMARY",
    "TGT-02": "PUBLIC_HYBRID",
    "TGT-03": "PUBLIC_HYBRID",
    "TGT-04": "PUBLIC_HYBRID",
    "TGT-05": "PUBLIC_HYBRID",
    "TGT-06": "PUBLIC_HYBRID",
    "TGT-07": "PUBLIC_HYBRID",
    "TGT-08": "PUBLIC_PRIMARY",
}
TGT_GATE_REGIMES: Final[Mapping[str, str]] = MappingProxyType(_TGT_GATE_REGIMES)


# import-time sanity: the label is not a gateset_id; L04's canonical GateSet is
# ADC_TARGET_GATESET; the name/regime maps cover exactly the roster.
if _GATESET_ID.match(PROGRAM_LABEL):
    raise RuntimeError("CRC-ADC-TARGET-GATESET-v1 must not look like a gateset_id")
if CANONICAL_GATESET_IDS.get(TGT_CANDIDATE_LEVEL) != ADC_TARGET_GATESET_ID:
    raise RuntimeError("L04 canonical GateSet is not ADC_TARGET_GATESET")
if tuple(_TGT_GATE_NAMES) != TGT_GATE_IDS or tuple(_TGT_GATE_REGIMES) != TGT_GATE_IDS:
    raise RuntimeError("TGT name / regime maps must cover exactly TGT-01..TGT-08")
for _r in _TGT_GATE_REGIMES.values():
    if _r not in DOMINANT_EVIDENCE_REGIMES:
        raise RuntimeError(f"unknown dominant_evidence_regime {_r}")


def _deterministic_module_id(gate_id: str) -> str:
    """Data Layout Spec Appendix A: Module = MOD-<GATE without hyphen>."""

    return "MOD-" + gate_id.replace("-", "")


# --- Roster row --------------------------------------------------------

@dataclass(frozen=True)
class TgtGateSpec:
    """One frozen roster row for an ADC_TARGET_GATESET gate."""

    gate_id: str
    name: str
    candidate_level: str
    gateset_id: str
    gate_version: str
    dominant_evidence_regime: str

    def __post_init__(self) -> None:
        _require_pattern(self.gate_id, _TGT_GATE_ID, "gate_id")
        _require_text(self.name, "name")
        if self.name != TGT_GATE_NAMES[self.gate_id]:
            raise ValueError(
                f"{self.gate_id} name must be {TGT_GATE_NAMES[self.gate_id]!r}"
            )
        if self.candidate_level != TGT_CANDIDATE_LEVEL:
            raise ValueError("candidate_level must be L04")
        if self.gateset_id != ADC_TARGET_GATESET_ID:
            raise ValueError("gateset_id must be ADC_TARGET_GATESET")
        if self.gate_version != TGT_GATE_VERSION:
            raise ValueError('gate_version must be "1.0" (PR D initializes the lineage)')
        if self.dominant_evidence_regime != TGT_GATE_REGIMES[self.gate_id]:
            raise ValueError(
                f"{self.gate_id} dominant_evidence_regime must be "
                f"{TGT_GATE_REGIMES[self.gate_id]}"
            )


# --- Concrete gate contract ------------------------------------------

@dataclass(frozen=True)
class TgtGateContract:
    """One gate's concrete, review-frozen contract. Evidence-class semantics
    only; no invented numeric thresholds."""

    gate_spec: TgtGateSpec
    gate_question: str
    evidence_required: tuple[str, ...]
    ladder: EvidenceLadder
    allowed_inference: tuple[str, ...]
    forbidden_inference: tuple[str, ...]
    unknown_behavior: str
    fatal_conditions: tuple[str, ...]
    evidence_ladder_ref: str
    assessment_rule_ref: str
    primary_module_id: str
    primary_module_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.gate_spec, TgtGateSpec):
            raise ValueError("gate_spec must be a TgtGateSpec")
        if not isinstance(self.ladder, EvidenceLadder):
            raise ValueError("ladder must be an EvidenceLadder")

        gate_id = self.gate_spec.gate_id
        if self.ladder.gate_id != gate_id or self.ladder.gate_version != self.gate_spec.gate_version:
            raise ValueError("ladder gate_id / gate_version must match gate_spec")

        _require_str_tuple(self.evidence_required, "evidence_required")
        _require_str_tuple(self.allowed_inference, "allowed_inference")
        _require_str_tuple(self.forbidden_inference, "forbidden_inference")
        _require_str_tuple(self.fatal_conditions, "fatal_conditions")
        for name in (
            "evidence_required",
            "allowed_inference",
            "forbidden_inference",
            "fatal_conditions",
        ):
            value = getattr(self, name)
            if not value or not all(item.strip() for item in value):
                raise ValueError(f"{name} must be a non-empty tuple of non-empty strings")
        _require_text(self.gate_question, "gate_question")
        _require_text(self.unknown_behavior, "unknown_behavior")

        expected_module = _deterministic_module_id(gate_id)
        _require_pattern(self.primary_module_id, _MODULE_ID, "primary_module_id")
        if self.primary_module_id != expected_module:
            raise ValueError(
                f"{gate_id} primary_module_id must be the deterministic "
                f"{expected_module!r}"
            )
        expected_version = expected_primary_module_version(gate_id)
        if self.primary_module_version != expected_version:
            built = gate_id in BUILT_MODULE_VERSIONS
            raise ValueError(
                f"{gate_id} primary_module_version must be {expected_version!r} "
                + (
                    "(the Module is built)"
                    if built
                    else "(the Module is a declared slot, not built)"
                )
            )

        # delegate validation of every field shared with PR B's Gate to Gate
        # itself (canonical gateset for L04, regime enum, external: refs, module
        # id pattern, ...). If it raises, this contract is invalid too.
        Gate(
            gate_id=gate_id,
            gate_version=self.gate_spec.gate_version,
            gateset_id=self.gate_spec.gateset_id,
            candidate_level=self.gate_spec.candidate_level,
            gate_question=self.gate_question,
            dominant_evidence_regime=self.gate_spec.dominant_evidence_regime,
            evidence_required=self.evidence_required,
            evidence_ladder_ref=self.evidence_ladder_ref,
            assessment_rule_ref=self.assessment_rule_ref,
            primary_module_id=self.primary_module_id,
            primary_module_version=self.primary_module_version,
            fatal_conditions=self.fatal_conditions,
        )


# --- The whole specialization --------------------------------------

@dataclass(frozen=True)
class CrcAdcTargetGateSetV1:
    """CRC-ADC-TARGET-GATESET-v1: roster + GateSet + Instantiation + eight
    concrete gate contracts, all over the SAME canonical ADC_TARGET_GATESET."""

    roster: tuple[TgtGateSpec, ...]
    gateset: GateSet
    instantiation: Instantiation
    gate_contracts: tuple[TgtGateContract, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.roster, tuple) or not all(
            isinstance(spec, TgtGateSpec) for spec in self.roster
        ):
            raise ValueError("roster must be a sequence of TgtGateSpec")
        if tuple(spec.gate_id for spec in self.roster) != TGT_GATE_IDS:
            raise ValueError("roster must be exactly TGT-01..TGT-08 in order")

        if not isinstance(self.gateset, GateSet):
            raise ValueError("gateset must be a GateSet")
        if self.gateset.gateset_id != ADC_TARGET_GATESET_ID:
            raise ValueError("gateset_id must be ADC_TARGET_GATESET (never the program label)")
        if self.gateset.gateset_version != TGT_GATESET_VERSION:
            raise ValueError('gateset_version must be "1.0"')
        if self.gateset.candidate_level != TGT_CANDIDATE_LEVEL:
            raise ValueError("gateset candidate_level must be L04")
        if tuple(m.gate_id for m in self.gateset.gates) != TGT_GATE_IDS:
            raise ValueError("gateset members must be exactly TGT-01..TGT-08 in order")
        if any(m.gate_version != TGT_GATE_VERSION for m in self.gateset.gates):
            raise ValueError('every gateset member gate_version must be "1.0"')

        if not isinstance(self.instantiation, Instantiation):
            raise ValueError("instantiation must be an Instantiation")
        if self.instantiation.gateset_id != ADC_TARGET_GATESET_ID:
            raise ValueError("instantiation gateset_id must be ADC_TARGET_GATESET")
        if self.instantiation.gateset_version != TGT_GATESET_VERSION:
            raise ValueError('instantiation gateset_version must be "1.0"')
        if self.instantiation.candidate_level != TGT_CANDIDATE_LEVEL:
            raise ValueError("instantiation candidate_level must be L04")

        if not isinstance(self.gate_contracts, tuple) or not all(
            isinstance(contract, TgtGateContract) for contract in self.gate_contracts
        ):
            raise ValueError("gate_contracts must be a sequence of TgtGateContract")
        if tuple(c.gate_spec.gate_id for c in self.gate_contracts) != TGT_GATE_IDS:
            raise ValueError("gate_contracts must cover exactly TGT-01..TGT-08 in order")
        for spec, contract in zip(self.roster, self.gate_contracts):
            if contract.gate_spec != spec:
                raise ValueError(
                    f"gate_contracts[{spec.gate_id}].gate_spec must equal the roster row"
                )


# --- Introspection helpers (used by the parity test) -----------------

CRC_ADC_TARGET_OBJECTS: Final[tuple[type, ...]] = (
    TgtGateSpec,
    TgtGateContract,
    CrcAdcTargetGateSetV1,
)


def field_names(object_type: type) -> tuple[str, ...]:
    """Return the declared field names of a PR D dataclass."""

    return tuple(f.name for f in fields(object_type))
