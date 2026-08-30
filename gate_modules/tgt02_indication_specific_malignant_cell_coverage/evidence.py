"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified coverage observations (E7 item 11, E8-7). One observation -> one
canonical EP. An existing canonical package is reused EXACTLY (no allocator
call, no new body). Provenance comes from the resolved canonical ``SourceIndex``
record. On reuse, every classification-driving field RELEVANT TO THAT
OBSERVATION KIND must be present AND equal, else a HARD identity integrity
failure.

The package carries observation-level meaning only -- a per-cohort protein /
transcript expression fact, a malignant-compartment single-cell / spatial fact,
a TMA transcript+protein concordance fact, a matched normal-vs-tumor context, or
an audited search-completion fact. It never carries "passes TGT-02", "has
adequate malignant-cell coverage", "coverage is fatal", "should be killed", or
any TGT-03 / TGT-04 / TGT-05 conclusion.
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    ClassifiedCoverage,
    EmittedEvidence,
    NormalizedCoverageObservation,
    Tgt02ModuleInput,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "an adequate / inadequate malignant-cell coverage conclusion for TGT-02",
    "a NEGATIVE / DIRECT Gate proposal or a cross-cohort fatal pattern",
    "a TGT-03 persistence, TGT-04 surface / density, or TGT-05 therapeutic-index conclusion",
    "a favourable therapeutic index read from a matched normal-vs-tumor comparison",
    "a Candidate-level Decision / KILL / HOLD",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single observation; it carries no Gate-relative grade, direction or "
    "coverage-support implication",
    "Gate-relative interpretation (Evidence-Ladder rung, Direction x Strength, "
    "fatal_review) is applied by the aggregate / review layer, not this package",
)
_NEUTRAL_CEILING = "an observation-level target-expression / search fact for the named target"

_KEYS_ALWAYS: tuple[str, ...] = (
    "target_identity",
    "context_key",
    "landscape_as_of",
    "observation_kind",
    "molecular_layer",
    "assay_method",
    "crc_specific",
    "malignant_cell_attribution",
    "malignant_attribution_basis",
    "cohort_adequacy_status",
    "cohort_adequacy_basis",
    "expression_pattern",
    "expression_pattern_basis",
    "expression_pattern_basis_detail",
)
_KEYS_BY_KIND: dict[str, tuple[str, ...]] = {
    "PROTEIN_COHORT": ("cohort_id", "cohort_ids", "cohort_n", "declared_multi_cohort_analysis"),
    "MALIGNANT_SC_SPATIAL": ("cohort_id", "cohort_ids"),
    "TMA_TRANSCRIPT_PROTEIN_CONCORDANCE": ("cohort_id", "cohort_ids"),
    "BULK_CRC_RNA": ("cohort_id",),
    "PAN_CANCER_UNRESOLVED": ("cohort_id",),
    "MATCHED_NORMAL_TUMOR": ("cohort_id",),
    # the audit EP is a completion certificate, so every completion-driving
    # snapshot field is classification-driving on reuse (E8-5 gene).
    "SEARCH_COMPLETION_AUDIT": (
        "audit_search_scope",
        "audit_sources_searched",
        "audit_landscape_as_of",
        "audit_public_crc_coverage_search_complete",
        "audit_protein_cohort_search_complete",
        "audit_malignant_compartment_sc_spatial_search_complete",
        "audit_tma_concordance_search_complete",
        "audit_matched_normal_tumor_search_complete",
        "audit_unresolved_item_keys",
        "audit_qualifying_protein_cohort_ids",
        "audit_qualifying_indirect_cohort_ids",
    ),
}


def _parity_keys(observation: NormalizedCoverageObservation) -> tuple[str, ...]:
    seen: list[str] = []
    for key in (*_KEYS_ALWAYS, *_KEYS_BY_KIND[observation.observation_kind]):
        if key not in seen:
            seen.append(key)
    return tuple(seen)


def _directly_supports(item: ClassifiedCoverage) -> tuple[str, ...]:
    """State the observation's ACTUAL fields (E7 item 11 Gate-neutral factual
    contract). Never assume a malignant / CRC / complete claim from the
    observation kind -- a NON_MALIGNANT / non-CRC / unresolved-compartment
    contextual observation must not be written as if it were in CRC malignant
    cells, and an incomplete audit must not be written as a completed search."""

    o = item.observation
    if o.observation_kind == "SEARCH_COMPLETION_AUDIT":
        state = (
            "declared public CRC coverage search complete"
            if o.audit_public_crc_coverage_search_complete
            else "declared public CRC coverage search NOT yet complete"
        )
        return (
            f"a CRC coverage search-completion record as of {o.audit_landscape_as_of}: "
            f"{state}; components -- protein cohort "
            f"{o.audit_protein_cohort_search_complete}, malignant-compartment "
            f"sc/spatial {o.audit_malignant_compartment_sc_spatial_search_complete}, "
            f"TMA concordance {o.audit_tma_concordance_search_complete}, matched "
            f"normal-tumor {o.audit_matched_normal_tumor_search_complete}",
        )

    cohort_label = ",".join(o.cohort_identities) or "(unnamed cohort)"
    pattern_label = o.expression_pattern or "an unqualified expression pattern"
    facts = (
        f"crc_specific={o.crc_specific}, "
        f"malignant_cell_attribution={o.malignant_cell_attribution}, "
        f"molecular_layer={o.molecular_layer}, assay={o.assay_method}, "
        f"cohort_adequacy_status={o.cohort_adequacy_status}"
    )
    if o.observation_kind == "MATCHED_NORMAL_TUMOR":
        return (
            f"a matched normal-vs-tumor comparison for the target ({facts}); "
            f"context only: {o.claim}",
        )
    return (
        f"cohort {cohort_label!r} reported {pattern_label} target expression "
        f"({facts})",
    )


def _measurement_result(item: ClassifiedCoverage) -> str:
    o = item.observation
    return (
        f"{o.observation_kind} for {o.target_identity!r} (context {o.context_key!r}, "
        f"as of {o.landscape_as_of})"
    )


def _as_rejected(
    item: ClassifiedCoverage, reason: str, *, severity: str
) -> ClassifiedCoverage:
    return ClassifiedCoverage(
        observation=item.observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        coverage_support="",
        qualifying_for_direct=False,
        qualifying_for_indirect=False,
    )


def _reused_package_is_compatible(
    existing: EvidencePackage, item: ClassifiedCoverage, candidate_id: str
) -> str:
    o = item.observation
    if existing.provenance.get("source_id") != o.source_id:
        return "canonical EvidencePackage provenance.source_id differs from the observation"
    if existing.claim != o.claim:
        return "canonical EvidencePackage claim differs from the observation"
    if candidate_id not in tuple(existing.candidate_refs):
        return "canonical EvidencePackage candidate_refs do not include this candidate"
    keys = _parity_keys(o)
    current = {k: getattr(o, k) for k in keys}
    for key in keys:
        if key not in existing.study_context:
            return (
                f"canonical EvidencePackage is missing the classification-driving "
                f"field {key!r}, so classification parity cannot be verified"
            )
        if existing.study_context[key] != current[key]:
            return (
                f"canonical EvidencePackage {key} = {existing.study_context[key]!r} "
                f"but the current normalized observation has {current[key]!r} "
                f"(classification-driving drift)"
            )
    return ""


def build_evidence_packages(
    classified: list[ClassifiedCoverage],
    *,
    module_input: Tgt02ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedCoverage],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates). ``extra_rejections``
    carry a ``rejection_severity`` -- a HARD one rejects the whole run."""

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedCoverage] = []
    dropped: list[tuple[str, str]] = []
    seen_source_claim: set[tuple[str, str]] = set()
    prior_ids = set(module_input.existing_evidence_ids)

    for item in classified:
        if not item.admissible:
            continue
        o = item.observation

        canonical = source_resolver.resolve(o.source_id)
        if canonical is None:
            extra_rejections.append(
                _as_rejected(
                    item,
                    f"provenance.source_id {o.source_id} claimed resolved but is not "
                    "in the canonical SourceIndex",
                    severity="HARD",
                )
            )
            continue
        if (
            canonical.source_type != o.source_type
            or canonical.source_identifier != o.source_identifier
            or canonical.locator != o.locator
        ):
            extra_rejections.append(
                _as_rejected(
                    item,
                    "provider provenance disagrees with the canonical SourceIndex "
                    f"record for {o.source_id}",
                    severity="HARD",
                )
            )
            continue

        key = (o.source_id, o.claim.strip())
        if key in seen_source_claim:
            dropped.append((o.observation_id, "duplicate (source_id, claim)"))
            continue
        seen_source_claim.add(key)

        existing = evidence_library.resolve(o.observation_id)
        if existing is not None:
            why = _reused_package_is_compatible(existing, item, module_input.candidate_id)
            if why:
                extra_rejections.append(
                    _as_rejected(
                        item,
                        "Evidence Library returned an incompatible canonical "
                        f"EvidencePackage for observation {o.observation_id}: {why}",
                        severity="HARD",
                    )
                )
                continue
            emitted.append(
                EmittedEvidence(
                    classified=item,
                    evidence_id=existing.evidence_id,
                    package=existing,
                    reused=True,
                )
            )
            continue

        evidence_id = allocator.next_evidence_id()
        if evidence_id in prior_ids:
            raise ValueError(
                f"allocator returned {evidence_id}, which is already an "
                "existing_evidence_id for this (candidate, gate)"
            )
        study_context = {
            "indication": "refractory_metastatic_colorectal_cancer",
            "treatment_state": "not_applicable",
            "sample_type": "crc_tumor_tissue",
            "observation_id": o.observation_id,
            "target_identity": o.target_identity,
            "context_key": o.context_key,
            "landscape_as_of": o.landscape_as_of,
            "observation_kind": o.observation_kind,
            "molecular_layer": o.molecular_layer,
            "assay_method": o.assay_method,
            "crc_specific": o.crc_specific,
            "malignant_cell_attribution": o.malignant_cell_attribution,
            "malignant_attribution_basis": o.malignant_attribution_basis,
            "cohort_adequacy_status": o.cohort_adequacy_status,
            "cohort_adequacy_basis": o.cohort_adequacy_basis,
            "expression_pattern": o.expression_pattern,
            "expression_pattern_basis": o.expression_pattern_basis,
            "expression_pattern_basis_detail": o.expression_pattern_basis_detail,
            "cohort_id": o.cohort_id,
            "cohort_ids": o.cohort_ids,
            "cohort_n": o.cohort_n,
            "declared_multi_cohort_analysis": o.declared_multi_cohort_analysis,
            "audit_search_scope": o.audit_search_scope,
            "audit_sources_searched": o.audit_sources_searched,
            "audit_landscape_as_of": o.audit_landscape_as_of,
            "audit_public_crc_coverage_search_complete": o.audit_public_crc_coverage_search_complete,
            "audit_protein_cohort_search_complete": o.audit_protein_cohort_search_complete,
            "audit_malignant_compartment_sc_spatial_search_complete": o.audit_malignant_compartment_sc_spatial_search_complete,
            "audit_tma_concordance_search_complete": o.audit_tma_concordance_search_complete,
            "audit_matched_normal_tumor_search_complete": o.audit_matched_normal_tumor_search_complete,
            "audit_unresolved_item_keys": o.audit_unresolved_item_keys,
            "audit_qualifying_protein_cohort_ids": o.audit_qualifying_protein_cohort_ids,
            "audit_qualifying_indirect_cohort_ids": o.audit_qualifying_indirect_cohort_ids,
        }
        package = EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=o.claim,
            measurement={
                "type": "adc_target_indication_specific_malignant_cell_coverage_observation",
                "analyte": o.target_identity,
                "readout": f"{o.observation_kind}/{o.molecular_layer or 'search_audit'}",
                "result": _measurement_result(item),
                "unit": "",
            },
            candidate_refs=(module_input.candidate_id,),
            study_context=study_context,
            provenance={
                "source_id": canonical.source_id,
                "source_type": canonical.source_type,
                "source_identifier": canonical.source_identifier,
                "locator": canonical.locator,
                "retrieved_at": o.retrieved_at,
            },
            interpretation_boundary={
                "directly_supports": _directly_supports(item),
                "does_not_support": _NEUTRAL_DOES_NOT_SUPPORT,
                "limitations": _NEUTRAL_LIMITATIONS,
                "evidence_ceiling": _NEUTRAL_CEILING,
            },
            derivation={
                "module_run_id": module_input.run_id,
                "code_commit": module_input.code_commit,
            },
        )
        emitted.append(
            EmittedEvidence(
                classified=item, evidence_id=evidence_id, package=package, reused=False
            )
        )

    return emitted, extra_rejections, dropped
