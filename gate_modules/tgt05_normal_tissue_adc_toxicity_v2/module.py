"""Pure, inactive MOD-TGT05@2.0.0 evidence producer.

Inputs are normalized facts from injected ports. The module never fetches data,
writes files, creates a canonical Assessment/Decision, or equates a missing
record with normal-tissue safety. A failed run returns a rejection outside the
review/assessment chain and no partially usable EP or proposal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.objects.decision_model import EvidencePackage, EvidenceRef

from .contracts import (
    DOMAINS, GATE_ID, MODULE_ID, MODULE_VERSION, CoverageAudit, ModuleInput,
    NormalizedObservation, Proposal, RunRejection, RunResult, SourceRecord,
)
from .ports import (
    EvidenceIdAllocatorPort, EvidenceLibraryPort, ObservationProviderPort,
    SourceResolverPort,
)


@dataclass(frozen=True)
class _Classified:
    observation: NormalizedObservation
    domain: str
    direction: str  # POSITIVE, NEGATIVE, INCONCLUSIVE, CONTEXTUAL, REFUTES
    strength: str   # DIRECT, INDIRECT_STRONG, WEAK, or empty


def _classify(o: NormalizedObservation, coverage: CoverageAudit) -> _Classified:
    """Derive ladder authority from facts; no provider-supplied grade is read."""
    clinical_complete = coverage.clinical_sweep == "COMPLETE"
    cell_complete = coverage.key_cell_scope == "COMPLETE"
    if o.kind == "ADC_CLINICAL_EVENT":
        if o.finding != "LIABILITY":
            return _Classified(o, "E1", "CONTEXTUAL", "")
        qualified = (
            o.validated and o.severe and o.target_attributed
            and o.organ_cell_attributed and o.exposure_relevant
            and o.alternatives_reviewed and bool(o.organ and o.cell_type and o.construct)
        )
        if qualified:
            return _Classified(o, "E1", "POSITIVE", "DIRECT")
        return _Classified(o, "E1", "INCONCLUSIVE", "WEAK")
    if o.kind == "NORMAL_CELL_ADC_FUNCTION":
        if o.finding != "LIABILITY":
            return _Classified(o, "E1", "CONTEXTUAL", "")
        qualified = (
            o.normal_human and o.validated
            and o.surface_accessible and o.target_dependent and o.adc_killing
            and o.exposure_relevant and o.serious_consequence
            and bool(o.organ and o.cell_type and o.construct)
        )
        if qualified:
            return _Classified(o, "E1", "POSITIVE", "DIRECT")
        return _Classified(o, "E1", "INCONCLUSIVE", "WEAK")
    if o.kind == "CLINICAL_ATTRIBUTION_REFUTATION":
        qualified = o.validated and o.finding == "REFUTES" and bool(o.mechanism and o.method)
        return _Classified(o, "E1", "REFUTES", "" if qualified else "WEAK")
    if o.kind == "CANDIDATE_ANTIBODY_BINDING":
        positive_qualified = o.normal_human and o.validated and o.surface_accessible and bool(o.construct and o.method and o.cell_type)
        negative_qualified = o.normal_human and o.validated and o.physiologically_relevant and bool(o.construct and o.method)
        if o.finding == "DETECTED" and positive_qualified:
            return _Classified(o, "E2", "POSITIVE", "INDIRECT_STRONG")
        if (
            o.finding == "NOT_DETECTED" and negative_qualified and o.key_cells_covered
            and o.assay_sensitive and clinical_complete and cell_complete
            and f"{o.organ}:{o.cell_type}" in coverage.organ_cell_scope
        ):
            return _Classified(o, "E2", "NEGATIVE", "DIRECT")
        return _Classified(o, "E2", "CONTEXTUAL", "")
    if o.kind == "NORMAL_MEMBRANE_PROTEIN":
        qualified = o.normal_human and o.validated and o.membrane_localized and bool(o.cell_type and o.method)
        if o.finding == "DETECTED" and qualified:
            return _Classified(o, "E2", "POSITIVE", "INDIRECT_STRONG")
        if (
            o.finding == "NOT_DETECTED" and qualified and o.key_cells_covered
            and o.assay_sensitive and clinical_complete and cell_complete
            and f"{o.organ}:{o.cell_type}" in coverage.organ_cell_scope
        ):
            return _Classified(o, "E2", "NEGATIVE", "INDIRECT_STRONG")
        return _Classified(o, "E2", "CONTEXTUAL", "")
    if o.kind in ("TOTAL_PROTEIN_IHC", "NORMAL_RNA"):
        if o.finding not in ("DETECTED", "NOT_DETECTED"):
            return _Classified(o, "E3" if o.kind == "NORMAL_RNA" else "E2", "CONTEXTUAL", "")
        return _Classified(o, "E3" if o.kind == "NORMAL_RNA" else "E2", "INCONCLUSIVE", "WEAK")
    return _Classified(o, "SUPPORTING", "CONTEXTUAL", "")


def _study_context(o: NormalizedObservation) -> dict[str, object]:
    # Classification-driving facts are recorded for strict canonical EP reuse.
    return {
        "indication": "not_applicable_normal_tissue_observation",
        "treatment_state": "not_applicable",
        "sample_type": "normal_human" if o.normal_human else "other_or_unknown",
        "observation_id": o.observation_id,
        "event_id": o.event_id,
        "target_hgnc_id": o.target_hgnc_id,
        "adcdb_target_id": o.adcdb_target_id,
        "program_id": o.program_id,
        "context_id": o.context_id,
        "context_version": o.context_version,
        "kind": o.kind,
        "finding": o.finding,
        "organ": o.organ,
        "cell_type": o.cell_type,
        "construct": o.construct,
        "exposure": o.exposure,
        "method": o.method,
        "mechanism": o.mechanism,
        **{key: getattr(o, key) for key in (
            "normal_human", "validated", "severe", "target_attributed", "organ_cell_attributed",
            "exposure_relevant", "alternatives_reviewed", "surface_accessible", "target_dependent",
            "adc_killing", "serious_consequence", "membrane_localized", "assay_sensitive",
            "physiologically_relevant", "key_cells_covered",
        )},
    }


def _ep_body(o: NormalizedObservation, source) -> dict[str, object]:
    return {
        "claim": o.claim,
        "measurement": {
            "type": "normal_tissue_adc_target_observation",
            "analyte": o.target_hgnc_id,
            "readout": f"{o.kind}/{o.finding}",
            "result": o.claim,
            "unit": "",
        },
        "study_context": _study_context(o),
        "provenance": {
            "source_id": source.source_id,
            "source_type": source.source_type,
            "source_identifier": source.source_identifier,
            "locator": source.locator,
            "retrieved_at": o.retrieved_at,
        },
        "interpretation_boundary": {
            "directly_supports": (f"The named source reports {o.finding.lower()} for {o.kind.lower()} in {o.organ or 'an unspecified organ'}/{o.cell_type or 'an unspecified cell'}.",),
            "does_not_support": (
                "target-wide normal-tissue safety", "ADC therapeutic window",
                "a Candidate GO/HOLD/KILL decision",
            ),
            "limitations": (
                "One observation only; Gate-relative grade and direction are not EP fields.",
                "Construct, exposure, assay and covered cells bound any inference.",
            ),
            "evidence_ceiling": "source-bounded normal-tissue observation; no Gate-level or Candidate-level conclusion",
        },
    }


def _same_ep(existing: EvidencePackage, body: dict[str, object], candidate_id: str) -> bool:
    return (
        existing.claim == body["claim"]
        and dict(existing.measurement) == body["measurement"]
        and dict(existing.study_context) == body["study_context"]
        and dict(existing.provenance) == body["provenance"]
        and {k: tuple(v) if isinstance(v, (tuple, list)) else v for k, v in existing.interpretation_boundary.items()}
            == body["interpretation_boundary"]
        and candidate_id in existing.candidate_refs
    )


def _dedup_body(body: dict[str, object]) -> dict[str, object]:
    """An exact repeated source claim may have a second provider observation id."""
    copy = dict(body)
    context = dict(copy["study_context"])
    context.pop("observation_id")
    copy["study_context"] = context
    return copy


def _rejected(request: ModuleInput, code: str, reason: str, observation_id: str = "") -> RunResult:
    return RunResult(MODULE_ID, MODULE_VERSION, GATE_ID, request.run_id, (), (), None,
                     RunRejection(code, reason, observation_id))


def _aggregate(classified: Sequence[tuple[_Classified, str]], coverage: CoverageAudit) -> Proposal:
    by_domain: dict[str, list[str]] = {domain: [] for domain in DOMAINS}
    refs: list[EvidenceRef] = []
    positive_direct: list[tuple[_Classified, str]] = []
    positive_indirect: list[tuple[_Classified, str]] = []
    negative_direct: list[tuple[_Classified, str]] = []
    negative_indirect: list[tuple[_Classified, str]] = []
    weak: list[tuple[_Classified, str]] = []
    refutations: list[tuple[_Classified, str]] = []
    for c, evidence_id in classified:
        by_domain[c.domain].append(evidence_id)
        role = "CONTRADICTING" if c.direction in ("NEGATIVE", "REFUTES") else (
            "SUPPORTING" if c.direction == "POSITIVE" else "CONTEXTUAL"
        )
        refs.append(EvidenceRef(evidence_id, role))
        if c.direction == "POSITIVE" and c.strength == "DIRECT":
            positive_direct.append((c, evidence_id))
        elif c.direction == "POSITIVE" and c.strength == "INDIRECT_STRONG":
            positive_indirect.append((c, evidence_id))
        elif c.direction == "NEGATIVE" and c.strength == "DIRECT":
            negative_direct.append((c, evidence_id))
        elif c.direction == "NEGATIVE" and c.strength == "INDIRECT_STRONG":
            negative_indirect.append((c, evidence_id))
        elif c.direction == "INCONCLUSIVE" and c.strength == "WEAK":
            weak.append((c, evidence_id))
        elif c.direction == "REFUTES" and c.strength == "":
            refutations.append((c, evidence_id))

    conflicting_ids: set[str] = set()
    for positive, positive_id in positive_direct:
        for refutation, refutation_id in refutations:
            if positive.observation.event_id == refutation.observation.event_id:
                conflicting_ids.update((positive_id, refutation_id))
    if conflicting_ids:
        direction, strength, rationale = "CONFLICTING", "DIRECT", "same-event qualified target-attribution disagreement"
    elif positive_direct:
        direction, strength, rationale = "POSITIVE", "DIRECT", "qualified clinical or normal-cell functional liability"
    elif positive_indirect:
        direction, strength, rationale = "POSITIVE", "INDIRECT_STRONG", "validated surface antigen without demonstrated ADC cell loss"
    elif negative_direct:
        direction, strength, rationale = "NEGATIVE", "DIRECT", "bounded candidate-antibody non-binding with audited coverage and clinical sweep"
    elif negative_indirect:
        direction, strength, rationale = "NEGATIVE", "INDIRECT_STRONG", "bounded audited key-cell membrane-protein non-detection"
    elif weak:
        direction, strength, rationale = "INCONCLUSIVE", "WEAK", "attribution-pending, RNA-only or total-protein hypothesis"
    else:
        direction, strength, rationale = "INCONCLUSIVE", "UNKNOWN", "no qualified ladder authority"

    unknowns: list[str] = list(coverage.limitations)
    if coverage.clinical_sweep != "COMPLETE":
        unknowns.append("same-target ADC clinical attribution sweep incomplete")
    if coverage.key_cell_scope != "COMPLETE":
        unknowns.append("key normal-human cells or assay sensitivity not fully covered")
    if any(c.observation.kind == "CANDIDATE_ANTIBODY_BINDING" and c.direction == "POSITIVE"
           and not c.observation.physiologically_relevant for c, _ in classified):
        unknowns.append("positive candidate-antibody binding physiological relevance unresolved")
    if positive_indirect:
        unknowns.append("normal-cell killing and functional consequence not established by surface evidence")
    if any(c.observation.kind == "ADC_CLINICAL_EVENT" and c.strength == "WEAK" for c, _ in classified):
        unknowns.append("serious clinical event target attribution unresolved")
    fatal = bool(positive_direct)
    fatal_routes = tuple((
        "CLINICAL" if c.observation.kind == "ADC_CLINICAL_EVENT" else "FUNCTIONAL", evidence_id
    ) for c, evidence_id in positive_direct)
    attribution = bool(conflicting_ids or any(c.observation.kind == "ADC_CLINICAL_EVENT" and c.strength == "WEAK" for c, _ in classified))
    lead = next((c.observation for c, _ in positive_direct + positive_indirect), None)
    seed = (
        ("assessment_basis_cell", f"{direction}/{strength}" if strength != "UNKNOWN" else "UNKNOWN"),
        ("risk_organ", lead.organ if lead else "not_identified"),
        ("risk_cell_type", lead.cell_type if lead else "not_identified"),
        ("clinical_liability", "SUSPECTED" if attribution else ("CONFIRMED" if positive_direct else "UNKNOWN")),
        ("review_status", "DRAFT"),
    )
    return Proposal(direction, strength, tuple(refs),
                    tuple((d, tuple(by_domain[d])) for d in DOMAINS), coverage,
                    tuple(dict.fromkeys(unknowns)), rationale, fatal, fatal_routes,
                    attribution, tuple(sorted(conflicting_ids)), seed)


def run(
    request: ModuleInput, *, provider: ObservationProviderPort,
    source_resolver: SourceResolverPort, evidence_library: EvidenceLibraryPort,
    evidence_id_allocator: EvidenceIdAllocatorPort,
) -> RunResult:
    """Produce only neutral EPs and an unapproved proposal for human review."""
    if not isinstance(request, ModuleInput):
        raise TypeError("request must be ModuleInput")
    try:
        observations = tuple(provider.fetch_observations(request))
        coverage = provider.coverage_audit(request)
    except Exception as exc:
        return _rejected(request, "PROVIDER_FAILURE", str(exc))
    if not isinstance(coverage, CoverageAudit):
        return _rejected(request, "AUDIT_INVALID", "coverage_audit must be CoverageAudit")
    if (
        coverage.target_hgnc_id != request.target_hgnc_id
        or coverage.program_id != request.program_id
        or coverage.context_id != request.context_id
        or coverage.context_version != request.context_version
    ):
        return _rejected(request, "AUDIT_IDENTITY_MISMATCH", "coverage audit target/program/context disagrees with request")
    if coverage.clinical_sweep == "FAILED" or coverage.key_cell_scope == "FAILED":
        return _rejected(request, "AUDIT_FAILED", "required sweep or coverage audit failed")

    seen_ids: set[str] = set()
    seen_claims: dict[tuple[str, str], dict[str, object]] = {}
    prepared: list[tuple[NormalizedObservation, object, dict[str, object]]] = []
    for o in observations:
        if not isinstance(o, NormalizedObservation):
            return _rejected(request, "OBSERVATION_INVALID", "provider returned invalid observation")
        if o.target_hgnc_id != request.target_hgnc_id or o.adcdb_target_id != request.adcdb_target_id:
            return _rejected(request, "TARGET_IDENTITY_MISMATCH", "observation target disagrees with request", o.observation_id)
        if (o.program_id, o.context_id, o.context_version) != (request.program_id, request.context_id, request.context_version):
            return _rejected(request, "PROGRAM_CONTEXT_MISMATCH", "observation program/context disagrees with request", o.observation_id)
        if o.observation_id in seen_ids:
            return _rejected(request, "DUPLICATE_OBSERVATION_ID", "observation id repeated in one round", o.observation_id)
        seen_ids.add(o.observation_id)
        try:
            source = source_resolver.resolve(o.source_id)
        except Exception as exc:
            return _rejected(request, "SOURCE_RESOLUTION_FAILED", str(exc), o.observation_id)
        if not isinstance(source, SourceRecord) or (source.source_type, source.source_identifier, source.locator) != (o.source_type, o.source_identifier, o.locator):
            return _rejected(request, "SOURCE_INTEGRITY_FAILURE", "source absent or metadata disagrees with canonical index", o.observation_id)
        body = _ep_body(o, source)
        claim_key = (o.source_id, o.claim.strip())
        if claim_key in seen_claims:
            if seen_claims[claim_key] != _dedup_body(body):
                return _rejected(request, "CLAIM_PARITY_DRIFT", "same source and claim have different classification facts", o.observation_id)
            continue  # exact duplicate fact, no new EP
        seen_claims[claim_key] = _dedup_body(body)
        prepared.append((o, source, body))

    emitted: list[EvidencePackage] = []
    reused: list[str] = []
    classified: list[tuple[_Classified, str]] = []
    all_ids: set[str] = set()
    for o, source, body in prepared:
        try:
            existing = evidence_library.resolve(o.observation_id)
        except Exception as exc:
            return _rejected(request, "EVIDENCE_LOOKUP_FAILED", str(exc), o.observation_id)
        if existing is not None:
            if not isinstance(existing, EvidencePackage) or not _same_ep(existing, body, request.candidate_id):
                return _rejected(request, "EP_REUSE_PARITY_FAILURE", "canonical EP differs from observation/source facts", o.observation_id)
            evidence_id = existing.evidence_id
            reused.append(evidence_id)
        else:
            try:
                evidence_id = evidence_id_allocator.next_evidence_id()
                if evidence_id in all_ids:
                    raise ValueError("allocator returned duplicate evidence_id")
                package = EvidencePackage(
                    evidence_id=evidence_id, schema_version=1, claim=body["claim"],
                    measurement=body["measurement"], candidate_refs=(request.candidate_id,),
                    study_context=body["study_context"], provenance=body["provenance"],
                    interpretation_boundary=body["interpretation_boundary"],
                    derivation={"module_run_id": request.run_id, "code_commit": request.code_commit},
                )
            except (ValueError, TypeError) as exc:
                return _rejected(request, "EP_CONSTRUCTION_FAILURE", str(exc), o.observation_id)
            emitted.append(package)
        if evidence_id in all_ids:
            return _rejected(request, "EP_ID_COLLISION", "evidence id repeated in one round", o.observation_id)
        all_ids.add(evidence_id)
        classified.append((_classify(o, coverage), evidence_id))

    proposal = _aggregate(classified, coverage)
    return RunResult(MODULE_ID, MODULE_VERSION, GATE_ID, request.run_id,
                     tuple(emitted), tuple(reused), proposal, None)
