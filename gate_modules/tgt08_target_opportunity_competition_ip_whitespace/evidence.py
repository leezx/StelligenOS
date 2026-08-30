"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified landscape records (E6-6). One observation -> one canonical EP. An
existing canonical package is reused EXACTLY (no allocator call, no new body).
Provenance comes from the resolved canonical ``SourceIndex`` record. On reuse,
every classification / absence driving field RELEVANT TO THAT OBSERVATION KIND
must be present AND equal, else a HARD identity integrity failure.

The package carries observation-level meaning only -- a program fact, a patent
claim / status fact, an unmet-need context, or an audited search-completion
fact. It never carries "good / bad opportunity", "TGT-08 NEGATIVE", "crowded
target", "FTO blocked", "dominant competitor", "no design around" or "no
differentiation path".
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    ClassifiedOpportunity,
    EmittedEvidence,
    NormalizedOpportunityRecord,
    Tgt08ModuleInput,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "a differentiated or non-differentiated target-opportunity conclusion",
    "a freedom-to-operate, infringement, validity or design-around conclusion",
    "a 'no differentiation path' conclusion",
    "any scientific de-risking of TGT-01 through TGT-07",
    "a sponsor Decision / KILL / STOP_FOR_SPONSOR / OUT_OF_MANDATE",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single observation; it carries no Gate-relative grade, direction or "
    "opportunity implication",
    "Gate-relative interpretation (opportunity implication, axis authority "
    "ceiling, Direction x Strength, sponsor_review) is applied by the "
    "assessment / review layer, not this package",
)
_NEUTRAL_CEILING = "an observation-level public-landscape fact for the named target"

# Classification / absence-driving fields to re-verify on reuse, per kind. The
# reused canonical body is immutable, so any field that would change the frozen
# evidence class or the derived opportunity implication must be present AND
# equal, or the canonical body no longer backs what the module would compute.
_KEYS_ALWAYS: tuple[str, ...] = (
    "target_identity",
    "evidence_axis",
    "observation_kind",
    "context_key",
    "landscape_as_of",
    "source_authority_kind",
)
_KEYS_BY_KIND: dict[str, tuple[str, ...]] = {
    "COMPETITOR_PROGRAM": (
        "program_id", "modality", "program_stage", "program_status",
        "indication_context_key",
    ),
    "PATENT_CLAIM": (
        "patent_family_id", "patent_publication_id", "jurisdiction",
        "claim_category", "legal_status", "composition_level",
    ),
    "UNMET_NEED_CONTEXT": (),
    "SEARCH_COMPLETION_AUDIT": (),
}


def _parity_keys(record: NormalizedOpportunityRecord) -> tuple[str, ...]:
    seen: list[str] = []
    for key in (*_KEYS_ALWAYS, *_KEYS_BY_KIND[record.observation_kind]):
        if key not in seen:
            seen.append(key)
    return tuple(seen)


def _directly_supports(item: ClassifiedOpportunity) -> tuple[str, ...]:
    r = item.record
    if r.observation_kind == "COMPETITOR_PROGRAM":
        return (
            f"program {r.program_id!r} ({r.modality}) against {r.target_identity!r} "
            f"is at stage {r.program_stage} / status {r.program_status} in "
            f"indication context {r.indication_context_key!r}",
        )
    if r.observation_kind == "PATENT_CLAIM":
        return (
            f"patent family {r.patent_family_id!r} (publication "
            f"{r.patent_publication_id!r}) contains a {r.claim_category} claim "
            f"(composition_level={r.composition_level}) with legal status "
            f"{r.legal_status} in {r.jurisdiction}",
        )
    if r.observation_kind == "UNMET_NEED_CONTEXT":
        return (
            f"the refractory-mCRC context {r.context_key!r}: {r.claim}",
        )
    return (
        f"a declared {r.evidence_axis.lower()} landscape search was completed as "
        f"of {r.landscape_as_of}: {r.claim}",
    )


def _measurement_result(item: ClassifiedOpportunity) -> str:
    r = item.record
    return (
        f"{r.evidence_axis} / {r.observation_kind} for {r.target_identity!r} "
        f"(context {r.context_key!r}, as of {r.landscape_as_of})"
    )


def _as_rejected(
    item: ClassifiedOpportunity, reason: str, *, severity: str
) -> ClassifiedOpportunity:
    return ClassifiedOpportunity(
        record=item.record,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_class="",
        opportunity_implication="",
        qualifying_for_axis=False,
    )


def _reused_package_is_compatible(
    existing: EvidencePackage, item: ClassifiedOpportunity, candidate_id: str
) -> str:
    r = item.record
    if existing.provenance.get("source_id") != r.source_id:
        return "canonical EvidencePackage provenance.source_id differs from the observation"
    if existing.claim != r.claim:
        return "canonical EvidencePackage claim differs from the observation"
    if candidate_id not in tuple(existing.candidate_refs):
        return "canonical EvidencePackage candidate_refs do not include this candidate"
    keys = _parity_keys(r)
    current = {k: getattr(r, k) for k in keys}
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
    classified: list[ClassifiedOpportunity],
    *,
    module_input: Tgt08ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedOpportunity],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates). ``extra_rejections``
    carry a ``rejection_severity`` -- a HARD one rejects the whole run."""

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedOpportunity] = []
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
            dropped.append((record.observation_id, "duplicate (source_id, claim)"))
            continue
        seen_source_claim.add(key)

        existing = evidence_library.resolve(record.observation_id)
        if existing is not None:
            why = _reused_package_is_compatible(existing, item, module_input.candidate_id)
            if why:
                extra_rejections.append(
                    _as_rejected(
                        item,
                        f"Evidence Library returned an incompatible canonical "
                        f"EvidencePackage for observation {record.observation_id}: {why}",
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
            "indication": "not_applicable_target_level_landscape_fact",
            "treatment_state": "not_applicable",
            "sample_type": "not_applicable",
            "observation_id": record.observation_id,
            "target_identity": record.target_identity,
            "evidence_axis": record.evidence_axis,
            "observation_kind": record.observation_kind,
            "context_key": record.context_key,
            "landscape_as_of": record.landscape_as_of,
            "source_authority_kind": record.source_authority_kind,
            "program_id": record.program_id,
            "modality": record.modality,
            "program_stage": record.program_stage,
            "program_status": record.program_status,
            "indication_context_key": record.indication_context_key,
            "failure_reason_disclosed": record.failure_reason_disclosed,
            "patent_family_id": record.patent_family_id,
            "patent_publication_id": record.patent_publication_id,
            "assignee": record.assignee,
            "jurisdiction": record.jurisdiction,
            "claim_category": record.claim_category,
            "legal_status": record.legal_status,
            "composition_level": record.composition_level,
        }
        package = EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=record.claim,
            measurement={
                "type": "adc_target_opportunity_landscape_observation",
                "analyte": record.target_identity,
                "readout": f"{record.evidence_axis}/{record.observation_kind}",
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
                "retrieved_at": record.retrieved_at,
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
