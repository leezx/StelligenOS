"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified records.

* One observation -> one package (mapping keyed by observation, never by
  program_id).
* An observation already in the PR C Evidence Library is REUSED as its EXACT
  canonical ``EvidencePackage`` -- no allocator call, no new body. A returned
  package incompatible with the current observation is a HARD identity
  integrity failure.
* Provenance comes from the canonical ``SourceIndex`` record, not the provider's
  raw fields; an unresolved id or a metadata conflict on a record the provider
  claimed ``primary_source_resolved=True`` is a HARD provenance integrity
  failure (E1 item 13 on_failure -> the run is rejected).
* The package carries observation-level meaning only. The TGT-01 ceiling,
  inference and Direction x Strength live in the proposal / assessment layer.
* ``(source_id, claim)`` duplicates are dropped (a SOFT drop).
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    ClassifiedPrecedent,
    EmittedEvidence,
    Tgt01ModuleInput,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "antigen expression or malignant-cell coverage in any indication",
    "treatment / metastatic persistence of the antigen",
    "cell-surface antigen density or surface localization",
    "normal-tissue on-target liability or therapeutic index",
    "internalization or lysosomal trafficking",
    "shedding / soluble-antigen sink behaviour",
    "competitive or intellectual-property landscape",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single ADC program fact; it carries no Gate-relative grade or direction",
    "Gate-relative interpretation (ladder rung, role, ceiling, Direction x "
    "Strength) is applied by the assessment layer, not this package",
)
_NEUTRAL_CEILING = {
    "DIRECT": "a clinical-stage ADC development fact for the named antigen",
    "INDIRECT_STRONG": "an early-clinical ADC development fact for the named antigen",
    "WEAK": "a preclinical / disclosure-level ADC fact for the named antigen",
}


def _directly_supports(item: ClassifiedPrecedent) -> tuple[str, ...]:
    r = item.record
    antigen = r.program_target_identity
    if item.direction_role == "ADVERSE_CANDIDATE":
        return (
            f"ADC program {r.program_id!r} against antigen {antigen!r} was "
            f"discontinued; the primary source attributes the failure to "
            f"{r.failure_attribution.lower().replace('_', ' ')}",
        )
    if item.direction_role == "CONTEXTUAL":
        return (
            f"ADC program {r.program_id!r} against antigen {antigen!r} was "
            f"discontinued; the primary source does not attribute the failure to "
            f"the target",
        )
    if r.target_relation == "ADJACENT_TARGET":
        return (
            f"an ADC targeting antigen {antigen!r} (biologically adjacent to the "
            f"queried target on the basis: {r.adjacency_basis}) reached "
            f"{r.program_stage} stage",
        )
    activity = (
        " with disclosed clinical activity" if r.clinical_activity_disclosed else ""
    )
    return (
        f"an ADC targeting antigen {antigen!r} reached {r.program_stage} stage"
        f"{activity}",
    )


def _neutral_result(item: ClassifiedPrecedent) -> str:
    r = item.record
    return (
        f"{r.target_relation} ADC program {r.program_id!r} against "
        f"{r.program_target_identity!r} at {r.program_stage}/{r.program_status}"
    )


def _as_rejected(
    item: ClassifiedPrecedent, reason: str, *, severity: str
) -> ClassifiedPrecedent:
    return ClassifiedPrecedent(
        record=item.record,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        ladder_rung="",
        evidence_class="",
        direction_role="CONTEXTUAL",
        contributes_adverse_signal=False,
        adverse_class="",
    )


# Every field the reused canonical package must still agree with on the current
# normalized record. The first three are provenance / attribution identity; the
# rest are exactly the fields that drive TGT-01 classification (ladder rung,
# direction role, adverse class). A drift on any of them means the referenced
# immutable EP no longer backs the Strength / Direction the module would compute.
_CLASSIFICATION_DRIVING_CONTEXT_KEYS: tuple[str, ...] = (
    "program_target_identity",
    "target_relation",
    "adjacency_basis",
    "program_stage",
    "program_status",
    "clinical_activity_disclosed",
    "failure_attribution",
)


def _reused_package_is_compatible(
    existing: EvidencePackage, item: ClassifiedPrecedent, candidate_id: str
) -> str:
    """Return "" if the canonical package matches this observation, else why not."""

    r = item.record
    if existing.provenance.get("source_id") != r.source_id:
        return "canonical EvidencePackage provenance.source_id differs from the observation"
    if existing.claim != r.claim:
        return "canonical EvidencePackage claim differs from the observation"
    if candidate_id not in tuple(existing.candidate_refs):
        return "canonical EvidencePackage candidate_refs do not include this candidate"
    current = {
        "program_target_identity": r.program_target_identity,
        "target_relation": r.target_relation,
        "adjacency_basis": r.adjacency_basis,
        "program_stage": r.program_stage,
        "program_status": r.program_status,
        "clinical_activity_disclosed": r.clinical_activity_disclosed,
        "failure_attribution": r.failure_attribution,
    }
    for key in _CLASSIFICATION_DRIVING_CONTEXT_KEYS:
        if key in existing.study_context and existing.study_context[key] != current[key]:
            return (
                f"canonical EvidencePackage {key} = "
                f"{existing.study_context[key]!r} but the current normalized "
                f"observation has {current[key]!r} (classification-driving drift)"
            )
    return ""


def build_evidence_packages(
    classified: list[ClassifiedPrecedent],
    *,
    module_input: Tgt01ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedPrecedent],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates).

    ``extra_rejections`` each carry a ``rejection_severity`` -- a HARD one
    rejects the whole run.
    """

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedPrecedent] = []
    dropped: list[tuple[str, str]] = []
    seen_source_claim: set[tuple[str, str]] = set()
    prior_ids = set(module_input.existing_evidence_ids)

    for item in classified:
        if not item.admissible:
            continue
        record = item.record

        canonical = source_resolver.resolve(record.source_id)
        if canonical is None:
            extra_rejections.append(
                _as_rejected(
                    item,
                    f"provenance.source_id {record.source_id} claimed resolved but "
                    "is not in the canonical SourceIndex",
                    severity="HARD",
                )
            )
            continue
        if (
            canonical.source_type != record.source_type
            or canonical.source_identifier != record.source_identifier
            or canonical.locator != record.locator
        ):
            extra_rejections.append(
                _as_rejected(
                    item,
                    "provider provenance disagrees with the canonical SourceIndex "
                    f"record for {record.source_id}",
                    severity="HARD",
                )
            )
            continue

        key = (record.source_id, record.claim.strip())
        if key in seen_source_claim:
            dropped.append((record.program_id, "duplicate (source_id, claim)"))
            continue
        seen_source_claim.add(key)

        existing = evidence_library.resolve(record.observation_id)
        if existing is not None:
            why = _reused_package_is_compatible(
                existing, item, module_input.candidate_id
            )
            if why:
                extra_rejections.append(
                    _as_rejected(
                        item,
                        f"Evidence Library returned an incompatible canonical "
                        f"EvidencePackage for observation {record.observation_id}: "
                        f"{why}",
                        severity="HARD",
                    )
                )
                continue
            emitted.append(
                EmittedEvidence(
                    classified=item,
                    evidence_id=existing.evidence_id,
                    package=existing,  # the EXACT canonical package, unchanged
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
        package = EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=record.claim,
            measurement={
                "type": "adc_program_fact_observation",
                "analyte": record.program_target_identity,
                "readout": f"{record.program_stage}/{record.program_status}",
                "result": _neutral_result(item),
                "unit": "",
            },
            candidate_refs=(module_input.candidate_id,),
            study_context={
                "indication": "not_applicable_adc_program_fact",
                "treatment_state": "not_applicable",
                "sample_type": "not_applicable",
                "observation_id": record.observation_id,
                "program_id": record.program_id,
                "program_target_identity": record.program_target_identity,
                "target_relation": record.target_relation,
                "adjacency_basis": record.adjacency_basis,
                "program_stage": record.program_stage,
                "program_status": record.program_status,
                "clinical_activity_disclosed": record.clinical_activity_disclosed,
                "failure_attribution": record.failure_attribution,
            },
            provenance={
                "source_id": canonical.source_id,
                "source_type": canonical.source_type,
                "source_identifier": canonical.source_identifier,
                "locator": canonical.locator,
                "retrieved_at": record.retrieved_at,
            },
            interpretation_boundary={
                "directly_supports": _directly_supports(item),
                "does_not_support": _NEUTRAL_DOES_NOT_SUPPORT,
                "limitations": _NEUTRAL_LIMITATIONS,
                "evidence_ceiling": _NEUTRAL_CEILING[item.ladder_rung],
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
