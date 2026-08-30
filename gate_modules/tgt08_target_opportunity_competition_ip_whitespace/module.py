"""MOD-TGT08 orchestration.

``run(...)`` is pure Python. It calls the injected ports only -- never a network
connection, a subprocess, a repository write, a filesystem-derived id, a patent
adapter, an FTO engine, a sponsor routing / Decision runtime, or an LLM /
embedding commercial-judgement model. It never constructs a canonical
``CandidateGateAssessment`` or a ``Decision``; its output is a set of
Gate-neutral ``EvidencePackage`` objects, two module-local completion states, a
machine-local ``sponsor_review`` review TRIGGER, and one non-canonical
``AssessmentProposalEnvelope`` for the human review surface. The candidate's
``target_identity`` (on the input) is the single authoritative target.
"""

from __future__ import annotations

from . import acceptance, aggregate as _aggregate, sponsor_review as _sponsor_review
from .classify import classify_record
from .contracts import (
    GATE_ID,
    MODULE_ID,
    MODULE_VERSION,
    TGT08_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    CompetitiveLandscapeCompletion,
    MachineAcceptanceRecord,
    PatentLandscapeCompletion,
    SponsorReviewRecord,
    Tgt08ModuleInput,
    Tgt08ModuleRunResult,
)
from .evidence import build_evidence_packages
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt08OpportunityProviderPort,
)


def run(
    module_input: Tgt08ModuleInput,
    *,
    provider: Tgt08OpportunityProviderPort,
    evidence_id_allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> Tgt08ModuleRunResult:
    """Produce Gate-neutral EvidencePackages + two completion states + a
    machine-local sponsor_review + one assessment proposal envelope for
    (``module_input.candidate_id``, TGT-08). Nothing is persisted."""

    if not isinstance(module_input, Tgt08ModuleInput):
        raise TypeError("module_input must be a Tgt08ModuleInput")

    run_id = module_input.run_id
    target_identity = module_input.target_identity

    records = list(
        provider.fetch_records(
            candidate_id=module_input.candidate_id,
            target_identity=target_identity,
            run_id=run_id,
        )
    )
    competitive = provider.competitive_completion(
        candidate_id=module_input.candidate_id,
        target_identity=target_identity,
        run_id=run_id,
    )
    patent = provider.patent_completion(
        candidate_id=module_input.candidate_id,
        target_identity=target_identity,
        run_id=run_id,
    )
    if not isinstance(competitive, CompetitiveLandscapeCompletion):
        raise TypeError(
            "provider.competitive_completion must return a CompetitiveLandscapeCompletion"
        )
    if not isinstance(patent, PatentLandscapeCompletion):
        raise TypeError(
            "provider.patent_completion must return a PatentLandscapeCompletion"
        )

    classified = [
        classify_record(record, canonical_target_identity=target_identity)
        for record in records
    ]

    emitted, extra_rejections, dropped = build_evidence_packages(
        classified,
        module_input=module_input,
        allocator=evidence_id_allocator,
        source_resolver=source_resolver,
        evidence_library=evidence_library,
    )

    outcome = _aggregate.aggregate(emitted, competitive, patent)
    sponsor_review = _sponsor_review.detect(
        emitted,
        landscape_as_of=module_input.landscape_as_of,
        patent_scope=module_input.patent_scope,
    )

    all_rejections = [c for c in classified if not c.admissible] + extra_rejections
    rejected_records: list[tuple[str, str]] = [
        (c.record.observation_id, c.rejection_reason) for c in all_rejections
    ]
    rejected_records.extend(dropped)
    hard_integrity_failures: list[tuple[str, str]] = [
        (c.record.observation_id, c.rejection_reason)
        for c in all_rejections
        if c.rejection_severity == "HARD"
    ]

    # E6 round-1 blocker 1: a SEARCH_COMPLETION_AUDIT EvidencePackage that names
    # a completion's audit_observation_id must snapshot that typed completion
    # exactly. Any drift is a HARD run-level integrity failure -- never a
    # trustworthy completion certificate.
    for e in emitted:
        record = e.classified.record
        if record.observation_kind != "SEARCH_COMPLETION_AUDIT":
            continue
        why = _aggregate.audit_snapshot_mismatch(record, competitive, patent)
        if why:
            hard_integrity_failures.append((record.observation_id, why))
            rejected_records.append((record.observation_id, why))

    checks, reasons = acceptance.evaluate(
        emitted=emitted,
        outcome=outcome,
        competitive=competitive,
        patent=patent,
        sponsor_review=sponsor_review,
        hard_integrity_failures=hard_integrity_failures,
        module_input=module_input,
    )

    proposal_envelope: AssessmentProposalEnvelope | None = None
    accepted = all(ok for _, ok in checks)
    if accepted:
        try:
            proposal_envelope = AssessmentProposalEnvelope(
                candidate_id=module_input.candidate_id,
                instantiation_id=module_input.instantiation_id,
                context_id=module_input.context_id,
                context_version=module_input.context_version,
                gateset_id=module_input.gateset_id,
                gateset_version=module_input.gateset_version,
                gate_id=module_input.gate_id,
                gate_version=module_input.gate_version,
                proposed_direction=outcome.proposed_direction,
                proposed_strength=outcome.proposed_strength,
                evidence_refs=outcome.evidence_refs,
                aggregation_rationale=outcome.aggregation_rationale,
                critical_unknowns=outcome.critical_unknowns,
                evidence_ceiling=TGT08_EVIDENCE_CEILING,
            )
        except ValueError as exc:  # pragma: no cover - guard, not expected
            accepted = False
            checks.append(("proposal_envelope_internally_consistent", False))
            reasons.append(f"proposal envelope inconsistent: {exc}")
            proposal_envelope = None

    # a sponsor_review trigger is only an actionable handoff on an accepted run.
    run_sponsor_review = sponsor_review if accepted else SponsorReviewRecord.none()

    machine_acceptance = MachineAcceptanceRecord(
        accepted=accepted,
        checks=tuple(checks),
        reasons=tuple(reasons),
        module_id=MODULE_ID,
        module_version=MODULE_VERSION,
        run_id=run_id,
    )

    return Tgt08ModuleRunResult(
        module_id=MODULE_ID,
        module_version=MODULE_VERSION,
        gate_id=GATE_ID,
        run_id=run_id,
        evidence_packages=tuple(e.package for e in emitted if not e.reused),
        reused_evidence_ids=tuple(e.evidence_id for e in emitted if e.reused),
        proposal_envelope=proposal_envelope,
        machine_acceptance=machine_acceptance,
        competitive_completion=competitive,
        patent_completion=patent,
        sponsor_review=run_sponsor_review,
        rejected_records=tuple(rejected_records),
        hard_integrity_failures=tuple(hard_integrity_failures),
    )
