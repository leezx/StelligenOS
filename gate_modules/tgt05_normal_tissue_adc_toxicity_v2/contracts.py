"""Typed, in-memory B1 input and output. No canonical Assessment or Decision.

The provider supplies observations and factual qualifiers, never a Gate grade,
Direction, recommendation, or Candidate decision. Schema validation and human
review occur downstream, outside this module and repository data boundary.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from src.objects.decision_model import EvidencePackage, EvidenceRef, SOURCE_TYPE_VALUES

MODULE_ID: Final[str] = "MOD-TGT05"
MODULE_VERSION: Final[str] = "2.0.0"
GATE_ID: Final[str] = "TGT-05"
GATE_VERSION: Final[str] = "2.0"
GATESET_ID: Final[str] = "ADC_TARGET_GATESET"
GATESET_VERSION: Final[str] = "2.0"
INSTANTIATION_ID: Final[str] = "INST-CRC-REFRACTORY-ADC-TARGET-v2"

KINDS: Final[tuple[str, ...]] = (
    "ADC_CLINICAL_EVENT", "NORMAL_CELL_ADC_FUNCTION",
    "CANDIDATE_ANTIBODY_BINDING", "NORMAL_MEMBRANE_PROTEIN",
    "TOTAL_PROTEIN_IHC", "NORMAL_RNA", "OPEN_TARGETS_SAFETY",
    "HUMAN_GENETICS", "ANIMAL_PHENOTYPE", "NON_ADC_PHARMACOLOGY",
    "CLINICAL_ATTRIBUTION_REFUTATION",
)
FINDINGS: Final[tuple[str, ...]] = (
    "LIABILITY", "DETECTED", "NOT_DETECTED", "UNRESOLVED", "REFUTES", "OTHER",
)
DOMAINS: Final[tuple[str, ...]] = ("E1", "E2", "E3", "SUPPORTING")
_CAND = re.compile(r"^CAND-L04-[0-9]{6}$")
_HGNC = re.compile(r"^HGNC:[0-9]+$")
_SRC = re.compile(r"^SRC-[0-9]{8}$")
_OBS = re.compile(r"^OBS-[A-Za-z0-9._:-]+$")
_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def _required(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty")


@dataclass(frozen=True)
class ModuleInput:
    candidate_id: str
    target_hgnc_id: str
    adcdb_target_id: str
    program_id: str
    context_id: str
    context_version: int
    run_id: str
    code_commit: str
    instantiation_id: str = INSTANTIATION_ID
    gate_id: str = GATE_ID
    gate_version: str = GATE_VERSION
    gateset_id: str = GATESET_ID
    gateset_version: str = GATESET_VERSION

    def __post_init__(self) -> None:
        if not _CAND.fullmatch(self.candidate_id):
            raise ValueError("candidate_id must be CAND-L04-nnnnnn")
        if not _HGNC.fullmatch(self.target_hgnc_id):
            raise ValueError("target_hgnc_id must be HGNC:n")
        for key in ("adcdb_target_id", "program_id", "context_id", "run_id", "code_commit"):
            _required(getattr(self, key), key)
        if not isinstance(self.context_version, int) or isinstance(self.context_version, bool) or self.context_version < 1:
            raise ValueError("context_version must be positive integer")
        for key, expected in (("instantiation_id", INSTANTIATION_ID), ("gate_id", GATE_ID),
                              ("gate_version", GATE_VERSION), ("gateset_id", GATESET_ID),
                              ("gateset_version", GATESET_VERSION)):
            if getattr(self, key) != expected:
                raise ValueError(f"{key} must be {expected}")


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_type: str
    source_identifier: str
    locator: str = ""

    def __post_init__(self) -> None:
        if not _SRC.fullmatch(self.source_id):
            raise ValueError("invalid source_id")
        if self.source_type not in SOURCE_TYPE_VALUES:
            raise ValueError("invalid source_type")
        _required(self.source_identifier, "source_identifier")


@dataclass(frozen=True)
class NormalizedObservation:
    observation_id: str
    event_id: str
    target_hgnc_id: str
    adcdb_target_id: str
    program_id: str
    context_id: str
    context_version: int
    kind: str
    finding: str
    claim: str
    source_id: str
    source_type: str
    source_identifier: str
    locator: str
    retrieved_at: str
    organ: str = ""
    cell_type: str = ""
    construct: str = ""
    exposure: str = ""
    method: str = ""
    mechanism: str = ""
    normal_human: bool = False
    validated: bool = False
    severe: bool = False
    target_attributed: bool = False
    organ_cell_attributed: bool = False
    exposure_relevant: bool = False
    alternatives_reviewed: bool = False
    surface_accessible: bool = False
    target_dependent: bool = False
    adc_killing: bool = False
    serious_consequence: bool = False
    membrane_localized: bool = False
    assay_sensitive: bool = False
    physiologically_relevant: bool = False
    key_cells_covered: bool = False

    def __post_init__(self) -> None:
        if not _OBS.fullmatch(self.observation_id):
            raise ValueError("invalid observation_id")
        for key in ("event_id", "adcdb_target_id", "program_id", "context_id", "claim", "source_identifier", "retrieved_at"):
            _required(getattr(self, key), key)
        if not isinstance(self.context_version, int) or isinstance(self.context_version, bool) or self.context_version < 1:
            raise ValueError("observation context_version must be positive integer")
        if not _HGNC.fullmatch(self.target_hgnc_id):
            raise ValueError("invalid target_hgnc_id")
        if not _SRC.fullmatch(self.source_id):
            raise ValueError("invalid source_id")
        if self.source_type not in SOURCE_TYPE_VALUES or self.kind not in KINDS or self.finding not in FINDINGS:
            raise ValueError("invalid source type, kind or finding")
        if not self.retrieved_at[:10] or not _DATE.fullmatch(self.retrieved_at[:10]):
            raise ValueError("retrieved_at must begin with ISO date")
        for key in (
            "normal_human", "validated", "severe", "target_attributed", "organ_cell_attributed",
            "exposure_relevant", "alternatives_reviewed", "surface_accessible", "target_dependent",
            "adc_killing", "serious_consequence", "membrane_localized", "assay_sensitive",
            "physiologically_relevant", "key_cells_covered",
        ):
            if not isinstance(getattr(self, key), bool):
                raise ValueError(f"{key} must be bool")


@dataclass(frozen=True)
class CoverageAudit:
    target_hgnc_id: str
    program_id: str
    context_id: str
    context_version: int
    clinical_sweep: str  # COMPLETE, INCOMPLETE, FAILED
    key_cell_scope: str  # COMPLETE, INCOMPLETE, FAILED
    as_of_date: str
    source_scope: tuple[str, ...]
    organ_cell_scope: tuple[str, ...]
    assay_sensitivity: str
    clinical_audit_sources: tuple[SourceRecord, ...] = ()
    cell_audit_sources: tuple[SourceRecord, ...] = ()
    sensitivity_audit_sources: tuple[SourceRecord, ...] = ()
    detection_limit_value: float | None = None
    detection_limit_unit: str = ""
    assay_positive_control: str = ""
    assay_negative_control: str = ""
    sensitivity_assay_methods: tuple[str, ...] = ()
    candidate_antibody_constructs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not _HGNC.fullmatch(self.target_hgnc_id):
            raise ValueError("invalid audit target_hgnc_id")
        for key in ("program_id", "context_id"):
            _required(getattr(self, key), key)
        if not isinstance(self.context_version, int) or isinstance(self.context_version, bool) or self.context_version < 1:
            raise ValueError("audit context_version must be positive integer")
        for key in ("clinical_sweep", "key_cell_scope"):
            if getattr(self, key) not in ("COMPLETE", "INCOMPLETE", "FAILED"):
                raise ValueError(f"invalid {key}")
        if not _DATE.fullmatch(self.as_of_date):
            raise ValueError("invalid as_of_date")
        for key in ("clinical_audit_sources", "cell_audit_sources", "sensitivity_audit_sources"):
            if not isinstance(getattr(self, key), tuple) or not all(isinstance(s, SourceRecord) for s in getattr(self, key)):
                raise ValueError(f"{key} must be a tuple of canonical source claims")
        if self.clinical_sweep == "COMPLETE" and (not self.source_scope or not self.clinical_audit_sources):
            raise ValueError("completed clinical sweep requires scope and audit source claims")
        if self.key_cell_scope == "COMPLETE":
            if not self.organ_cell_scope or not self.assay_sensitivity or not self.cell_audit_sources or not self.sensitivity_audit_sources:
                raise ValueError("completed key-cell scope requires cells, sensitivity and audit sources")
            if (not isinstance(self.detection_limit_value, (int, float)) or isinstance(self.detection_limit_value, bool)
                    or self.detection_limit_value <= 0):
                raise ValueError("completed key-cell scope requires a positive measured detection limit")
            for key in ("detection_limit_unit", "assay_positive_control", "assay_negative_control"):
                _required(getattr(self, key), key)
            if not self.sensitivity_assay_methods or not all(isinstance(x, str) and x.strip() for x in self.sensitivity_assay_methods):
                raise ValueError("completed key-cell scope requires named sensitivity assay methods")
            if not isinstance(self.candidate_antibody_constructs, tuple) or not all(isinstance(x, str) and x.strip() for x in self.candidate_antibody_constructs):
                raise ValueError("candidate_antibody_constructs must be named strings")


@dataclass(frozen=True)
class Proposal:
    direction: str
    strength: str
    evidence_refs: tuple[EvidenceRef, ...]
    domain_refs: tuple[tuple[str, tuple[str, ...]], ...]
    coverage_audit: CoverageAudit
    critical_unknowns: tuple[str, ...]
    rationale: str
    fatal_review_trigger: bool
    fatal_review_routes: tuple[tuple[str, str], ...]  # (CLINICAL|FUNCTIONAL, EP id)
    attribution_review_trigger: bool
    same_event_conflict_refs: tuple[str, ...]
    reviewer_seed: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RunRejection:
    code: str
    reason: str
    observation_id: str = ""


@dataclass(frozen=True)
class RunResult:
    module_id: str
    module_version: str
    gate_id: str
    run_id: str
    evidence_packages: tuple[EvidencePackage, ...]
    reused_evidence_ids: tuple[str, ...]
    proposal: Proposal | None
    rejection: RunRejection | None
