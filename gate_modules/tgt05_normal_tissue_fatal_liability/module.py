"""MOD-TGT05 orchestration.

``run(...)`` is pure Python. It calls the injected ports only -- never a network
connection, a subprocess, a repository write, an id derived from the filesystem,
or an ontology / embedding / LLM similarity model. It never constructs a
canonical ``CandidateGateAssessment`` or a ``Decision``; its output is a set of
Gate-neutral ``EvidencePackage`` objects, a machine-local ``fatal_review``
review TRIGGER, and one non-canonical ``AssessmentProposalEnvelope`` for the
human review surface. The candidate's ``target_identity`` (on the input) is the
single authoritative target -- ``run`` takes no separate, driftable target
argument.
"""

from __future__ import annotations

from . import acceptance, aggregate as _aggregate, fatal_review as _fatal_review
from .classify import classify_record
from .contracts import (
    GATE_ID,
    MODULE_ID,
    MODULE_VERSION,
    TGT05_EVIDENCE_CEILING,
    VITAL_ORGAN_CLASSES,
    AssessmentProposalEnvelope,
    CoverageMapRecord,
    MachineAcceptanceRecord,
    Tgt05ModuleInput,
    Tgt05ModuleRunResult,
    Tgt05SweepCompletionRecord,
)
from .evidence import build_evidence_packages
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt05LiabilityProviderPort,
)


def _is_human_protein_observation(record) -> bool:
    """A validated human normal-tissue PROTEIN atlas observation -- DETECTED
    (an INDIRECT_STRONG liability EP) or NOT_DETECTED (a COVERAGE_CONTEXT EP).
    Both are admissible protein data a human can click through to a source."""

    return (
        record.observation_kind == "HUMAN_NORMAL_EXPRESSION"
        and record.molecular_layer == "PROTEIN"
        and record.atlas_validated
        and record.finding in ("DETECTED", "NOT_DETECTED")
    )


def _coverage_map(emitted, sweep: Tgt05SweepCompletionRecord) -> CoverageMapRecord:
    by_organ = tuple(
        (
            organ,
            sweep.vital_organ_protein_coverage[organ].coverage_result,
            sweep.vital_organ_protein_coverage[organ].search_complete,
        )
        for organ in VITAL_ORGAN_CLASSES
    )
    # every admissible human-protein observation for the organ backs its coverage
    # state -- the DETECTED liability EP as much as the NOT_DETECTED coverage EP.
    supporting: dict[str, list[str]] = {organ: [] for organ in VITAL_ORGAN_CLASSES}
    for e in emitted:
        record = e.classified.record
        if not _is_human_protein_observation(record):
            continue
        organ = record.vital_organ_class
        if organ in supporting:
            supporting[organ].append(e.evidence_id)
    supporting_evidence_ids = tuple(
        (organ, tuple(supporting[organ])) for organ in VITAL_ORGAN_CLASSES
    )
    return CoverageMapRecord(
        by_organ=by_organ, supporting_evidence_ids=supporting_evidence_ids
    )


def run(
    module_input: Tgt05ModuleInput,
    *,
    provider: Tgt05LiabilityProviderPort,
    evidence_id_allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> Tgt05ModuleRunResult:
    """Produce Gate-neutral EvidencePackages + a machine-local fatal_review +
    one assessment proposal envelope for (``module_input.candidate_id``,
    TGT-05). Nothing is persisted."""

    if not isinstance(module_input, Tgt05ModuleInput):
        raise TypeError("module_input must be a Tgt05ModuleInput")

    run_id = module_input.run_id
    target_identity = module_input.target_identity

    records = list(
        provider.fetch_liability_records(
            candidate_id=module_input.candidate_id,
            target_identity=target_identity,
            run_id=run_id,
        )
    )
    sweep = provider.sweep_completion(
        candidate_id=module_input.candidate_id,
        target_identity=target_identity,
        run_id=run_id,
    )
    if not isinstance(sweep, Tgt05SweepCompletionRecord):
        raise TypeError(
            "provider.sweep_completion must return a Tgt05SweepCompletionRecord"
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

    fatal_review = _fatal_review.detect(emitted)
    outcome = _aggregate.aggregate(emitted, sweep)
    coverage_map = _coverage_map(emitted, sweep)
    path = acceptance.classify_path(emitted, fatal_review)

    all_rejections = [c for c in classified if not c.admissible] + extra_rejections
    rejected_records: list[tuple[str, str]] = [
        (c.record.program_id or c.record.observation_id, c.rejection_reason)
        for c in all_rejections
    ]
    rejected_records.extend(dropped)
    hard_integrity_failures: list[tuple[str, str]] = [
        (c.record.program_id or c.record.observation_id, c.rejection_reason)
        for c in all_rejections
        if c.rejection_severity == "HARD"
    ]

    checks, reasons = acceptance.evaluate(
        emitted=emitted,
        outcome=outcome,
        sweep=sweep,
        fatal_review=fatal_review,
        hard_integrity_failures=hard_integrity_failures,
        path=path,
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
                evidence_ceiling=TGT05_EVIDENCE_CEILING,
            )
        except ValueError as exc:  # pragma: no cover - guard, not expected
            accepted = False
            checks.append(("proposal_envelope_internally_consistent", False))
            reasons.append(f"proposal envelope inconsistent: {exc}")
            proposal_envelope = None

    machine_acceptance = MachineAcceptanceRecord(
        accepted=accepted,
        checks=tuple(checks),
        reasons=tuple(reasons),
        module_id=MODULE_ID,
        module_version=MODULE_VERSION,
        run_id=run_id,
    )

    return Tgt05ModuleRunResult(
        module_id=MODULE_ID,
        module_version=MODULE_VERSION,
        gate_id=GATE_ID,
        run_id=run_id,
        evidence_packages=tuple(e.package for e in emitted if not e.reused),
        reused_evidence_ids=tuple(e.evidence_id for e in emitted if e.reused),
        proposal_envelope=proposal_envelope,
        machine_acceptance=machine_acceptance,
        sweep_completion=sweep,
        coverage_map=coverage_map,
        fatal_review=fatal_review,
        rejected_records=tuple(rejected_records),
        hard_integrity_failures=tuple(hard_integrity_failures),
    )
