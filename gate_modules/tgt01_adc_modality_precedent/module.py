"""MOD-TGT01 orchestration.

``run(...)`` is pure Python. It calls the injected ports only -- it never opens a
network connection, spawns a subprocess, writes the repository, or derives an id
from the filesystem. It never constructs a canonical ``CandidateGateAssessment``
or a ``Decision``; its output is a set of Gate-neutral ``EvidencePackage``
objects plus one non-canonical ``AssessmentProposalEnvelope`` for the human
review surface. The candidate's ``target_identity`` (on the input) is the single
authoritative target -- ``run`` takes no separate, driftable target argument.
"""

from __future__ import annotations

from . import acceptance, aggregate as _aggregate
from .classify import classify_record
from .contracts import (
    GATE_ID,
    MODULE_ID,
    MODULE_VERSION,
    TGT01_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    MachineAcceptanceRecord,
    SweepCompletionRecord,
    Tgt01ModuleInput,
    Tgt01ModuleRunResult,
)
from .evidence import build_evidence_packages
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt01PrecedentProviderPort,
)


def run(
    module_input: Tgt01ModuleInput,
    *,
    provider: Tgt01PrecedentProviderPort,
    evidence_id_allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> Tgt01ModuleRunResult:
    """Produce Gate-neutral EvidencePackages + one assessment proposal envelope
    for (``module_input.candidate_id``, TGT-01). Nothing is persisted."""

    if not isinstance(module_input, Tgt01ModuleInput):
        raise TypeError("module_input must be a Tgt01ModuleInput")

    run_id = module_input.run_id
    target_identity = module_input.target_identity

    records = list(
        provider.fetch_precedents(
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
    if not isinstance(sweep, SweepCompletionRecord):
        raise TypeError("provider.sweep_completion must return a SweepCompletionRecord")

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
    outcome = _aggregate.aggregate(emitted)

    rejected_records: list[tuple[str, str]] = [
        (c.record.program_id, c.rejection_reason)
        for c in classified
        if not c.admissible
    ]
    rejected_records.extend(
        (c.record.program_id, c.rejection_reason) for c in extra_rejections
    )
    rejected_records.extend(dropped)

    checks, reasons = acceptance.evaluate(
        emitted=emitted, outcome=outcome, sweep=sweep
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
                evidence_ceiling=TGT01_EVIDENCE_CEILING,
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

    return Tgt01ModuleRunResult(
        module_id=MODULE_ID,
        module_version=MODULE_VERSION,
        gate_id=GATE_ID,
        run_id=run_id,
        evidence_packages=tuple(e.package for e in emitted),
        reused_evidence_ids=tuple(e.evidence_id for e in emitted if e.reused),
        proposal_envelope=proposal_envelope,
        machine_acceptance=machine_acceptance,
        sweep_completion=sweep,
        rejected_records=tuple(rejected_records),
    )
