"""MOD-TGT07 -- primary Evidence Production Module for Gate TGT-07
(Shedding / Soluble-Antigen / Sink Liability) under ADC_TARGET_GATESET@1.0 /
INST-CRC-REFRACTORY-ADC-TARGET-v1.

Built in Runtime Migration PR E16, strictly against the frozen PR E15 construction
contract (src/contracts/gate_modules/tgt07_shedding_soluble_antigen_sink_liability.yaml).
The module owns Gate-specific deterministic interpretation only: normalized
upstream soluble-antigen facts -> source / identity QC -> frozen Evidence-Ladder
rung mapping -> Gate-neutral EvidencePackages -> one typed
SolubleAntigenEvidenceCompletion (with the E6 / E8 / E10 / E14 completion-audit
exact-identity + snapshot-parity gene, the dual CRC-patient / healthy-donor
quantitation subspace audit facts, and the UNION-of-single-string
qualifying-DIRECT-context set) -> a proposed Direction x Strength via the TGT-07
HIGHEST-QUALIFYING-RUNG grading authority under the frozen
tgt07_specific_aggregation_truth_table.frozen_evaluation_order (one CLEAN
material-sink DIRECT sink-exposure context is POSITIVE / DIRECT; a same-context
material-vs-no-material pair is CONFLICTING / DIRECT with NO machine conflict
resolver; a qualified intended-ADC no-material-sink TMDD is NEGATIVE / DIRECT; a
DIRECT-quality MIXED_OR_UNRESOLVED analysis is INCONCLUSIVE / DIRECT; a qualifying
INDIRECT_STRONG landscape with no DIRECT is POSITIVE / INDIRECT_STRONG; the legal
pairs are exactly POSITIVE/DIRECT, POSITIVE/INDIRECT_STRONG, NEGATIVE/DIRECT,
CONFLICTING/DIRECT, INCONCLUSIVE/DIRECT, INCONCLUSIVE/UNKNOWN) -> a machine-local
fatal_review review TRIGGER (one qualifying material-sink-with-clinical-exposure-
compromise DIRECT observation on the clinical OR the intended-ADC TMDD source
path; no convergence, no reproducibility predicate, no global cancellation
precondition) -> machine acceptance -> one non-canonical assessment proposal
envelope.

Frozen invariants (E16 tightenings):

* A measurable soluble form is not a material antigen sink. INDIRECT_STRONG
  supports the sink-liability class; materiality requires DIRECT. A concentration
  value -- including a low or below-assay-limit value -- is never a threshold.
  There is NO dedicated raw numeric field and NO raw-value reuse-parity branch.
* DIRECT qualification is kind-specific and lives in classify.py alone: clinical
  DIRECT needs same-target-match + soluble-antigen attribution + analysis
  validation QUALIFIED; TMDD DIRECT needs TMDD input adequacy + analysis
  validation QUALIFIED. aggregate / fatal consume the classified result and never
  re-judge a typed status. MIXED_OR_UNRESOLVED may be DIRECT-quality CONTEXTUAL;
  NOT_ESTABLISHED is never a qualifying DIRECT-rung observation.
* The potential-fatal signal is a strict subset of POSITIVE / DIRECT, not a
  convergence rule. reproducibility_status is optional factual metadata only.
  The Module never decides fatality, KILL, HOLD, therapeutic efficacy or the
  Candidate-level consequence.

Live retrieval, extractors, normalizers, runners, persistence, and any GateSet
Decision / KILL are OUTSIDE this module (injected ports or downstream layers).
There is NO normalizer inside this package -- soluble-antigen qualifications are
given upstream by the provider.

MOD-TGT07 is the eighth and final primary Evidence Production Module. Merging PR
E16 completes the Blueprint-v1.3 Candidate x Gate x Evidence runtime-conformance
migration and the eight-primary-Module migration; other StelligenOS deferred work
(quantitative calibration, epitope-layer analyses, external evaluators, downstream
Candidate levels, FTO tasks) remains.
"""

from __future__ import annotations

from .aggregate import AggregationOutcome
from .completion import (
    SOLUBLE_ANTIGEN_UNRESOLVED_KIND_VALUES,
    SolubleAntigenEvidenceCompletion,
    SolubleAntigenUnresolvedItem,
)
from .contracts import (
    ANALYSIS_VALIDATION_STATUS_VALUES,
    CANDIDATE_LEVEL,
    CANONICAL_ONLY_FIELDS,
    CIRCULATING_SOLUBLE_TARGET_STATUS_VALUES,
    COHORT_CLASS_VALUES,
    CONTEXT_ID,
    CONTEXT_VERSION,
    EVIDENCE_RUNG_VALUES,
    EXPOSURE_SCENARIO_CLASS_VALUES,
    FATAL_REVIEW_STATUS_VALUES,
    FATAL_SOURCE_PATH_VALUES,
    GATE_ID,
    GATE_VERSION,
    GATESET_ID,
    GATESET_VERSION,
    INSTANTIATION_ID,
    LEGAL_DIRECTION_STRENGTH_PAIRS,
    MODULE_ID,
    MODULE_VERSION,
    OBSERVATION_KIND_VALUES,
    REPRODUCIBILITY_STATUS_VALUES,
    SAME_TARGET_THERAPEUTIC_MATCH_STATUS_VALUES,
    SINK_LIABILITY_IMPLICATION_VALUES,
    SINK_MATERIALITY_OUTCOME_VALUES,
    SOLUBLE_ANTIGEN_ATTRIBUTION_STATUS_VALUES,
    TGT07_EVIDENCE_CEILING,
    TGT07_GATE_QUESTION,
    TMDD_INPUT_ADEQUACY_STATUS_VALUES,
    AssessmentProposalEnvelope,
    CanonicalSourceRecord,
    ClassifiedSolubleAntigenObservation,
    EmittedEvidence,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    NormalizedSolubleAntigenObservation,
    Tgt07ModuleInput,
    Tgt07ModuleRunResult,
    sink_materiality_direction,
)
from .module import run
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt07SolubleAntigenEvidenceProviderPort,
)

__all__ = [
    "MODULE_ID",
    "MODULE_VERSION",
    "GATE_ID",
    "GATE_VERSION",
    "GATESET_ID",
    "GATESET_VERSION",
    "INSTANTIATION_ID",
    "CONTEXT_ID",
    "CONTEXT_VERSION",
    "CANDIDATE_LEVEL",
    "TGT07_EVIDENCE_CEILING",
    "TGT07_GATE_QUESTION",
    "OBSERVATION_KIND_VALUES",
    "SINK_MATERIALITY_OUTCOME_VALUES",
    "CIRCULATING_SOLUBLE_TARGET_STATUS_VALUES",
    "COHORT_CLASS_VALUES",
    "EXPOSURE_SCENARIO_CLASS_VALUES",
    "TMDD_INPUT_ADEQUACY_STATUS_VALUES",
    "ANALYSIS_VALIDATION_STATUS_VALUES",
    "SAME_TARGET_THERAPEUTIC_MATCH_STATUS_VALUES",
    "SOLUBLE_ANTIGEN_ATTRIBUTION_STATUS_VALUES",
    "REPRODUCIBILITY_STATUS_VALUES",
    "EVIDENCE_RUNG_VALUES",
    "SINK_LIABILITY_IMPLICATION_VALUES",
    "FATAL_REVIEW_STATUS_VALUES",
    "FATAL_SOURCE_PATH_VALUES",
    "SOLUBLE_ANTIGEN_UNRESOLVED_KIND_VALUES",
    "LEGAL_DIRECTION_STRENGTH_PAIRS",
    "CANONICAL_ONLY_FIELDS",
    "CanonicalSourceRecord",
    "NormalizedSolubleAntigenObservation",
    "SolubleAntigenUnresolvedItem",
    "SolubleAntigenEvidenceCompletion",
    "Tgt07ModuleInput",
    "ClassifiedSolubleAntigenObservation",
    "EmittedEvidence",
    "FatalReviewRecord",
    "AssessmentProposalEnvelope",
    "MachineAcceptanceRecord",
    "AggregationOutcome",
    "Tgt07ModuleRunResult",
    "sink_materiality_direction",
    "Tgt07SolubleAntigenEvidenceProviderPort",
    "EvidenceIdAllocatorPort",
    "SourceResolverPort",
    "ExistingEvidenceLibraryPort",
    "run",
]
