"""MOD-TGT04 orchestration.

``run(...)`` is pure Python. It calls the injected ports only -- never a network
connection, a subprocess, a repository write, a filesystem-derived id, an
absolute-quantitation flow / QIFIKIT / mass-cytometry / quantitative-surfaceomics
/ membranous-IHC / cell-surface-proteomics / subcellular-localization retrieval
adapter, a runner, or an LLM / embedding model. It never coerces a raw
``reported_density_value`` to a number. It never constructs a canonical
``CandidateGateAssessment`` or a ``Decision``; its output is a set of Gate-neutral
``EvidencePackage`` objects, one typed ``SurfaceAvailabilityCompletion``, a
machine-local ``fatal_review`` review TRIGGER, and one non-canonical
``AssessmentProposalEnvelope`` for the human review surface. The candidate's
``target_identity`` (on the input) is the single authoritative target.
"""

from __future__ import annotations

from . import acceptance
from .aggregate import aggregate
from .classify import classify_observation
from .completion import (
    SurfaceAvailabilityCompletion,
    audit_presence_failure,
    audit_snapshot_mismatch,
    completeness_contradiction,
    qualifying_set_mismatch,
)
from .contracts import (
    CONTEXT_ID,
    GATE_ID,
    MODULE_ID,
    MODULE_VERSION,
    TGT04_EVIDENCE_CEILING,
    AssessmentProposalEnvelope,
    FatalReviewRecord,
    MachineAcceptanceRecord,
    Tgt04ModuleInput,
    Tgt04ModuleRunResult,
)
from .evidence import build_evidence_packages
from .fatal_review import detect as detect_fatal_review
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
    Tgt04SurfaceAvailabilityProviderPort,
)


def run(
    module_input: Tgt04ModuleInput,
    *,
    provider: Tgt04SurfaceAvailabilityProviderPort,
    evidence_id_allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> Tgt04ModuleRunResult:
    """Produce Gate-neutral EvidencePackages + one typed completion + a
    machine-local fatal_review + one assessment proposal envelope for
    (``module_input.candidate_id``, TGT-04). Nothing is persisted."""

    if not isinstance(module_input, Tgt04ModuleInput):
        raise TypeError("module_input must be a Tgt04ModuleInput")

    run_id = module_input.run_id
    target_identity = module_input.target_identity

    observations = list(
        provider.fetch_observations(
            candidate_id=module_input.candidate_id,
            target_identity=target_identity,
            run_id=run_id,
        )
    )
    completion = provider.surface_completion(
        candidate_id=module_input.candidate_id,
        target_identity=target_identity,
        run_id=run_id,
    )
    if not isinstance(completion, SurfaceAvailabilityCompletion):
        raise TypeError(
            "provider.surface_completion must return a SurfaceAvailabilityCompletion"
        )

    classified = [
        classify_observation(o, canonical_target_identity=target_identity)
        for o in observations
    ]

    rejected_records: list[tuple[str, str]] = []
    hard_integrity_failures: list[tuple[str, str]] = []

    # --- normalized-input identity PREFLIGHT (E11 item 10; E12-7 authoritative
    #     identity precedence; E12 review round 2, blocker 3) ------------------
    # A duplicate observation_id is an ambiguous identity -- the Evidence Library
    # resolves canonical packages BY observation_id, so two normalized records
    # sharing one id cannot both be trustworthy. It is a HARD whole-run reject
    # that MUST be decided BEFORE any semantic dedup, source resolution, Evidence
    # ID allocation or transient EvidencePackage construction. When it fires the
    # run short-circuits: build_evidence_packages() is never called.
    obs_id_counts: dict[str, int] = {}
    for o in observations:
        obs_id_counts[o.observation_id] = obs_id_counts.get(o.observation_id, 0) + 1
    duplicate_observation_ids = [oid for oid, n in obs_id_counts.items() if n > 1]
    for oid in duplicate_observation_ids:
        why = (
            f"observation_id {oid!r} appears {obs_id_counts[oid]} times "
            "-- ambiguous observation identity"
        )
        hard_integrity_failures.append((oid, why))
        rejected_records.append((oid, why))

    if duplicate_observation_ids:
        emitted: list = []
        extra_rejections: list = []
        dropped: list[tuple[str, str]] = []
    else:
        emitted, extra_rejections, dropped = build_evidence_packages(
            classified,
            module_input=module_input,
            allocator=evidence_id_allocator,
            source_resolver=source_resolver,
            evidence_library=evidence_library,
        )

    all_rejections = [c for c in classified if not c.admissible] + extra_rejections
    rejected_records.extend(
        (c.observation.observation_id, c.rejection_reason) for c in all_rejections
    )
    rejected_records.extend(dropped)
    hard_integrity_failures.extend(
        (c.observation.observation_id, c.rejection_reason)
        for c in all_rejections
        if c.rejection_severity == "HARD"
    )

    # --- local surface-context identity authority (E10 identity-namespace gene;
    #     E11 review round 1) --------------------------------------------------
    # a LOCAL surface-context identity may never be the canonical Instantiation
    # context_id; and any observation the Module classifies as qualifying DIRECT /
    # INDIRECT_STRONG MUST carry at least one auditable local surface-context
    # identity (else completion parity has nothing to reconcile and a graded
    # Direction rests on an anonymous context).
    for o in observations:
        for cid in (o.surface_context_id, *o.surface_context_ids):
            if cid.strip() == CONTEXT_ID:
                why = (
                    f"observation {o.observation_id} carries a local "
                    f"surface_context_id {cid!r} equal to the canonical "
                    f"Instantiation context_id -- namespace collapse"
                )
                hard_integrity_failures.append((o.observation_id, why))
                rejected_records.append((o.observation_id, why))
    for c in classified:
        if not c.admissible or not c.is_qualifying:
            continue
        if not c.observation.surface_context_identities:
            why = (
                f"observation {c.observation.observation_id} is classified "
                f"qualifying {c.evidence_rung} but carries no auditable local "
                "surface_context_id / surface_context_ids"
            )
            hard_integrity_failures.append((c.observation.observation_id, why))
            rejected_records.append((c.observation.observation_id, why))

    # Every observation must belong to THIS candidate's scientific context and
    # THIS run's declared surface search scope -- no implicit default context, and
    # a foreign completion may not be used for grading (E11 item 10).
    for o in observations:
        if o.context_key.strip() != module_input.context_key.strip():
            why = (
                f"observation {o.observation_id} carries context_key "
                f"{o.context_key!r}, not the run's context_key "
                f"{module_input.context_key!r}"
            )
            hard_integrity_failures.append((o.observation_id, why))
            rejected_records.append((o.observation_id, why))
    if completion.attempted and (
        completion.search_scope.strip() != module_input.surface_search_scope.strip()
    ):
        why = (
            "surface_completion.search_scope "
            f"{completion.search_scope!r} != the run's declared "
            f"surface_search_scope {module_input.surface_search_scope!r}"
        )
        hard_integrity_failures.append(("surface_completion", why))
        rejected_records.append(("surface_completion", why))

    # --- E12-5 invariant 1: completion completeness consistency -----------
    why = completeness_contradiction(completion)
    if why:
        hard_integrity_failures.append(("surface_completion", why))
        rejected_records.append(("surface_completion", why))

    # --- E12-5 invariant 2: audit presence + snapshot parity ------------
    audit_obs_ids = [
        c.observation.observation_id
        for c in classified
        if c.admissible and c.observation.observation_kind == "SEARCH_COMPLETION_AUDIT"
    ]
    why = audit_presence_failure(completion, audit_obs_ids)
    if why:
        hard_integrity_failures.append(("surface_completion", why))
        rejected_records.append(("surface_completion", why))
    # The completion's authority is backed by a PROVENANCE-BEARING audit EP; a
    # SEARCH_COMPLETION_AUDIT EP is never a dedup loser, but verify the emitted /
    # reused surface too: an attempted completion needs exactly one matching
    # SEARCH_COMPLETION_AUDIT EvidencePackage.
    audit_eps = [
        e for e in emitted
        if e.observation.observation_kind == "SEARCH_COMPLETION_AUDIT"
        and e.observation.observation_id == completion.audit_observation_id
    ]
    if completion.attempted and len(audit_eps) != 1:
        why = (
            "the attempted surface-availability landscape has no matching "
            f"provenance-bearing SEARCH_COMPLETION_AUDIT EvidencePackage (got {len(audit_eps)})"
        )
        hard_integrity_failures.append(("surface_completion", why))
        rejected_records.append(("surface_completion", why))
    for e in emitted:
        o = e.observation
        if o.observation_kind != "SEARCH_COMPLETION_AUDIT":
            continue
        why = audit_snapshot_mismatch(o, completion)
        if why:
            hard_integrity_failures.append((o.observation_id, why))
            rejected_records.append((o.observation_id, why))

    # --- E12-5 invariant 3: qualifying surface-context-set parity --------
    # Only ever the final qualifying-set authority on a COMPLETED landscape
    # (E12 tightening 3). An incomplete landscape may carry observations; it
    # just cannot produce a graded Direction.
    if completion.landscape_complete:
        direct_context_ids: set[str] = set()
        indirect_context_ids: set[str] = set()
        for e in emitted:
            if not e.classified.admissible:
                continue
            if e.classified.qualifying_for_direct:
                direct_context_ids.update(e.observation.surface_context_identities)
            elif e.classified.qualifying_for_indirect:
                indirect_context_ids.update(e.observation.surface_context_identities)
        why = qualifying_set_mismatch(
            completion,
            direct_context_ids=direct_context_ids,
            indirect_context_ids=indirect_context_ids,
        )
        if why:
            hard_integrity_failures.append(("surface_completion", why))
            rejected_records.append(("surface_completion", why))

    outcome = aggregate(emitted, completion)
    raw_fatal_review = detect_fatal_review(
        emitted,
        completion,
        landscape_as_of=module_input.landscape_as_of,
        surface_search_scope=module_input.surface_search_scope,
    )

    checks, reasons = acceptance.evaluate(
        emitted=emitted,
        outcome=outcome,
        completion=completion,
        fatal_review=raw_fatal_review,
        hard_integrity_failures=hard_integrity_failures,
        module_input=module_input,
    )

    accepted = all(ok for _, ok in checks)
    proposal_envelope: AssessmentProposalEnvelope | None = None
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
                evidence_ceiling=TGT04_EVIDENCE_CEILING,
            )
        except ValueError as exc:  # pragma: no cover - guard, not expected
            accepted = False
            checks.append(("proposal_envelope_internally_consistent", False))
            reasons.append(f"proposal envelope inconsistent: {exc}")
            proposal_envelope = None

    # a fatal_review trigger is only an actionable handoff on an accepted run.
    run_fatal_review = raw_fatal_review if accepted else FatalReviewRecord.none()

    machine_acceptance = MachineAcceptanceRecord(
        accepted=accepted,
        checks=tuple(checks),
        reasons=tuple(reasons),
        module_id=MODULE_ID,
        module_version=MODULE_VERSION,
        run_id=run_id,
    )

    return Tgt04ModuleRunResult(
        module_id=MODULE_ID,
        module_version=MODULE_VERSION,
        gate_id=GATE_ID,
        run_id=run_id,
        evidence_packages=tuple(e.package for e in emitted if not e.reused),
        reused_evidence_ids=tuple(e.evidence_id for e in emitted if e.reused),
        proposal_envelope=proposal_envelope,
        machine_acceptance=machine_acceptance,
        surface_completion=completion,
        fatal_review=run_fatal_review,
        rejected_records=tuple(rejected_records),
        hard_integrity_failures=tuple(hard_integrity_failures),
    )
