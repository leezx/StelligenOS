"""MOD-TGT01 -- primary Evidence Production Module for Gate TGT-01
(ADC Modality Precedent) under ADC_TARGET_GATESET@1.0 /
INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E2, strictly against the frozen E1 construction
contract (src/contracts/gate_modules/tgt01_adc_modality_precedent.yaml). The
module owns Gate-specific deterministic interpretation only: normalized evidence
-> EvidencePackages -> assessment proposal envelope. Web retrieval, source
registry, persistence, human approval and canonical persistence are outside it.
"""

from __future__ import annotations

from .contracts import (
    GATE_ID,
    GATE_VERSION,
    GATESET_ID,
    GATESET_VERSION,
    INSTANTIATION_ID,
    MODULE_ID,
    MODULE_VERSION,
    TGT01_EVIDENCE_CEILING,
    TGT01_GATE_QUESTION,
    AssessmentProposalEnvelope,
    ClassifiedPrecedent,
    MachineAcceptanceRecord,
    NormalizedPrecedentRecord,
    SweepCompletionRecord,
    Tgt01ModuleInput,
    Tgt01ModuleRunResult,
)
from .ports import (
    EvidenceIdAllocatorPort,
    SourceRegistryPort,
    Tgt01PrecedentProviderPort,
)
from .module import run

__all__ = [
    "MODULE_ID",
    "MODULE_VERSION",
    "GATE_ID",
    "GATE_VERSION",
    "GATESET_ID",
    "GATESET_VERSION",
    "INSTANTIATION_ID",
    "TGT01_EVIDENCE_CEILING",
    "TGT01_GATE_QUESTION",
    "NormalizedPrecedentRecord",
    "Tgt01ModuleInput",
    "ClassifiedPrecedent",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "SweepCompletionRecord",
    "Tgt01ModuleRunResult",
    "Tgt01PrecedentProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceRegistryPort",
    "run",
]
