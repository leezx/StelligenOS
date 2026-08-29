"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified records (E4-7). One observation -> one canonical EP. An existing
canonical package is reused EXACTLY (no allocator call, no new body). Provenance
comes from the resolved canonical ``SourceIndex`` record. On reuse, every
classification-driving field RELEVANT TO THAT OBSERVATION KIND must be present
AND equal, else a HARD identity integrity failure.

The package carries observation-level meaning only. A validated atlas
NOT_DETECTED observation is an EP too -- its interpretation_boundary explicitly
says it does NOT support the absence of a liability, safety, or a
product-specific therapeutic window.
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import ClassifiedLiability, EmittedEvidence, Tgt05ModuleInput
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "the absence of a normal-tissue on-target liability",
    "normal-tissue safety",
    "a product-specific therapeutic window",
    "tumor selectivity or malignant-cell coverage",
    "ADC efficacy",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single observation; it carries no Gate-relative grade or direction",
    "Gate-relative interpretation (ladder rung, role, ceiling, Direction x "
    "Strength, fatal-pattern) is applied by the assessment / review layer, not "
    "this package",
)
_NEUTRAL_CEILING = {
    "DIRECT": "a clinical on-target / off-tumor toxicity fact for the named target",
    "INDIRECT_STRONG": "a clinical non-ADC toxicity / validated protein expression / translational NHP toxicity fact for the named target",
    "WEAK": "an RNA-level or rodent-only fact for the named target",
    "": "an observation-level fact for the named target",
}

# Classification-driving fields to re-verify on reuse, per observation kind.
_KEYS_BY_KIND: dict[str, tuple[str, ...]] = {
    "ADC_CLINICAL_TOXICITY": (
        "target_identity", "observation_kind", "modality", "program_id",
        "construct_fingerprint", "affected_tissue", "toxicity_phenotype_key",
        "observed_severity", "target_attribution_stance", "target_attribution_basis",
        "evidence_function",
    ),
    "NON_ADC_CLINICAL_TOXICITY": (
        "target_identity", "observation_kind", "modality", "program_id",
        "construct_fingerprint", "affected_tissue", "toxicity_phenotype_key",
        "observed_severity", "target_attribution_stance", "target_attribution_basis",
        "evidence_function",
    ),
    "HUMAN_NORMAL_EXPRESSION": (
        "target_identity", "observation_kind", "species", "molecular_layer",
        "finding", "atlas_validated", "vital_organ_class", "affected_tissue",
        "cell_compartment", "evidence_function",
    ),
    "NHP_TOXICITY": (
        "target_identity", "observation_kind", "species", "affected_tissue",
        "toxicity_phenotype_key", "translational_relevance", "evidence_function",
    ),
    "RODENT_NORMAL_OR_TOXICITY": (
        "target_identity", "observation_kind", "species", "molecular_layer",
        "finding", "affected_tissue", "evidence_function",
    ),
}


def _directly_supports(item: ClassifiedLiability) -> tuple[str, ...]:
    r = item.record
    if item.evidence_function == "COVERAGE_CONTEXT":
        return (
            f"a validated human protein atlas reported NO detectable "
            f"{r.target_identity!r} protein in {r.vital_organ_class} "
            f"({r.affected_tissue or 'tissue'})",
        )
    if item.evidence_function == "ATTRIBUTION_ADJUDICATION":
        verb = "supports" if item.attribution_stance == "SUPPORTS_TARGET_ATTRIBUTION" else "refutes"
        return (
            f"a primary source {verb} the target attribution of liability event "
            f"{r.liability_event_id} (program {r.program_id!r})",
        )
    if r.observation_kind in ("ADC_CLINICAL_TOXICITY", "NON_ADC_CLINICAL_TOXICITY"):
        return (
            f"program {r.program_id!r} ({r.modality or 'modality n/a'}) against "
            f"{r.target_identity!r} reported {r.toxicity_phenotype_raw or r.toxicity_phenotype_key} "
            f"in {r.affected_tissue}; the primary source attributes the event to "
            f"on-target expression (severity for this product: "
            f"{r.observed_severity or 'not stated'})",
        )
    if r.observation_kind == "HUMAN_NORMAL_EXPRESSION":
        return (
            f"a {'validated ' if r.atlas_validated else ''}{r.molecular_layer} atlas "
            f"reported {r.finding} {r.target_identity!r} in {r.vital_organ_class} "
            f"({r.affected_tissue or 'tissue'}, {r.cell_compartment or 'compartment n/a'})",
        )
    if r.observation_kind == "NHP_TOXICITY":
        return (
            f"non-human-primate on-target toxicity against {r.target_identity!r} "
            f"in {r.affected_tissue or 'tissue'} "
            f"(translational relevance: {r.translational_relevance})",
        )
    return (
        f"rodent-only observation for {r.target_identity!r}: {r.claim}",
    )


def _measurement_result(item: ClassifiedLiability) -> str:
    r = item.record
    return (
        f"{r.observation_kind} / {item.evidence_function} for {r.target_identity!r}"
        + (f" in {r.vital_organ_class}" if r.vital_organ_class else "")
    )


def _as_rejected(
    item: ClassifiedLiability, reason: str, *, severity: str
) -> ClassifiedLiability:
    return ClassifiedLiability(
        record=item.record,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_function=item.record.evidence_function,
        ladder_rung="",
        evidence_class="",
        attribution_stance="",
        covered_vital_organ="",
    )


def _reused_package_is_compatible(
    existing: EvidencePackage, item: ClassifiedLiability, candidate_id: str
) -> str:
    r = item.record
    if existing.provenance.get("source_id") != r.source_id:
        return "canonical EvidencePackage provenance.source_id differs from the observation"
    if existing.claim != r.claim:
        return "canonical EvidencePackage claim differs from the observation"
    if candidate_id not in tuple(existing.candidate_refs):
        return "canonical EvidencePackage candidate_refs do not include this candidate"
    keys = _KEYS_BY_KIND[r.observation_kind]
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
    classified: list[ClassifiedLiability],
    *,
    module_input: Tgt05ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedLiability],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates). ``extra_rejections``
    carry a ``rejection_severity`` -- a HARD one rejects the whole run."""

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedLiability] = []
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
            dropped.append((record.program_id or record.observation_id,
                            "duplicate (source_id, claim)"))
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
            "indication": "not_applicable_target_level_liability_fact",
            "treatment_state": "not_applicable",
            "sample_type": "not_applicable",
            "observation_id": record.observation_id,
            "liability_event_id": record.liability_event_id,
            "evidence_function": record.evidence_function,
            "target_identity": record.target_identity,
            "observation_kind": record.observation_kind,
            "species": record.species,
            "modality": record.modality,
            "molecular_layer": record.molecular_layer,
            "finding": record.finding,
            "atlas_validated": record.atlas_validated,
            "vital_organ_class": record.vital_organ_class,
            "affected_tissue": record.affected_tissue,
            "cell_compartment": record.cell_compartment,
            "program_id": record.program_id,
            "construct_fingerprint": record.construct_fingerprint,
            "toxicity_phenotype_key": record.toxicity_phenotype_key,
            "observed_severity": record.observed_severity,
            "target_attribution_stance": record.target_attribution_stance,
            "target_attribution_basis": record.target_attribution_basis,
            "translational_relevance": record.translational_relevance,
        }
        package = EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=record.claim,
            measurement={
                "type": "adc_target_normal_tissue_liability_observation",
                "analyte": record.target_identity,
                "readout": f"{record.observation_kind}/{record.finding or 'n/a'}",
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
