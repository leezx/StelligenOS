"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified persistence observations (E9 item 11, E10-7). One observation -> one
canonical EP. An existing canonical package is reused EXACTLY (no allocator call,
no new body). Provenance comes from the resolved canonical ``SourceIndex``
record. On reuse, every classification-driving field RELEVANT TO THAT OBSERVATION
KIND must be present AND equal, else a HARD identity integrity failure.

TGT-03-specific dedup deviation (E10-7): the module does NOT unconditionally copy
the E8 ``(source_id, claim)`` dedup. ``observation_id`` is the authoritative
observation identity (a duplicate is a HARD run rejection, handled in
``module.py``). Two normalized records are collapsed as a true duplicate ONLY
when their ``source_id`` AND ``claim`` AND every classification-driving fact AND
their LOCAL persistence-context identity all match. Any persistence-context
difference -> both survive. A SEARCH_COMPLETION_AUDIT EP is never a dedup loser.

The package carries observation-level meaning only -- a per-context protein /
transcript persistence fact, a resistance-model persistence fact, a
treatment-naive / different-tumor context, or an audited search-completion fact.
It never carries "passes TGT-03", "persistence established", "meaningful target
availability is lost", "should be killed", or any TGT-02 / TGT-04 conclusion.
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    ClassifiedPersistenceObservation,
    EmittedEvidence,
    NormalizedPersistenceObservation,
    Tgt03ModuleInput,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "a persistence established / materially impaired persistence conclusion for TGT-03",
    "a NEGATIVE / DIRECT Gate proposal or a reproducible fatal pattern",
    "a TGT-02 baseline malignant-cell coverage substitution",
    "a TGT-04 surface availability / antigen density / localization conclusion",
    "a Candidate-level Decision / KILL / HOLD",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single observation; it carries no Gate-relative grade, direction or "
    "persistence-implication",
    "Gate-relative interpretation (Evidence-Ladder rung, Direction x Strength, "
    "fatal_review) is applied by the aggregate / review layer, not this package",
)
_NEUTRAL_CEILING = "an observation-level target-persistence / search fact for the named target"

_KEYS_ALWAYS: tuple[str, ...] = (
    "observation_id",
    "target_identity",
    "context_key",
    "landscape_as_of",
    "observation_kind",
    "molecular_layer",
    "assay_method",
    "protein_measurement_validation_status",
    "protein_measurement_validation_basis",
    "crc_specific",
    "clinical_context",
    "clinical_context_basis",
    "context_adequacy_status",
    "context_adequacy_basis",
    "malignant_cell_attribution",
    "malignant_attribution_basis",
    "persistence_pattern",
    "persistence_pattern_basis",
    "residual_target_presence_status",
    "residual_target_presence_basis",
    "reproducibility_status",
    "reproducibility_basis",
    "persistence_context_id",
    "persistence_context_ids",
    "declared_multi_context_analysis",
)
_AUDIT_KEYS: tuple[str, ...] = (
    "audit_search_scope",
    "audit_sources_searched",
    "audit_landscape_as_of",
    "audit_public_persistence_search_complete",
    "audit_refractory_prior_treated_search_complete",
    "audit_metastatic_lesion_search_complete",
    "audit_paired_pre_post_search_complete",
    "audit_resistance_model_search_complete",
    "audit_unresolved_item_keys",
    "audit_qualifying_direct_persistence_context_ids",
    "audit_qualifying_indirect_persistence_context_ids",
)


def _parity_keys(observation: NormalizedPersistenceObservation) -> tuple[str, ...]:
    keys = list(_KEYS_ALWAYS)
    if observation.observation_kind == "SEARCH_COMPLETION_AUDIT":
        keys.extend(_AUDIT_KEYS)
    return tuple(keys)


def _dedup_key(o: NormalizedPersistenceObservation) -> tuple:
    """A true-duplicate key: source_id + claim + every classification-driving
    fact + the LOCAL persistence-context identity. Any persistence-context
    difference makes two records DISTINCT scientific observations (E10-7)."""

    return (
        o.source_id,
        o.claim.strip(),
        tuple(sorted(o.persistence_context_identities)),
        tuple(getattr(o, k) for k in _parity_keys(o) if k != "observation_id"),
    )


def _directly_supports(item: ClassifiedPersistenceObservation) -> tuple[str, ...]:
    """State the observation's ACTUAL fields (E9 item 11 Gate-neutral factual
    contract). Never assume a malignant / CRC / qualified-context / complete
    claim from the observation kind."""

    o = item.observation
    if o.observation_kind == "SEARCH_COMPLETION_AUDIT":
        state = (
            "declared public persistence search complete"
            if o.audit_public_persistence_search_complete
            else "declared public persistence search NOT yet complete"
        )
        return (
            f"a clinical-persistence search-completion record as of "
            f"{o.audit_landscape_as_of}: {state}; components -- refractory / "
            f"prior-treated {o.audit_refractory_prior_treated_search_complete}, "
            f"metastatic lesion {o.audit_metastatic_lesion_search_complete}, paired "
            f"pre/post {o.audit_paired_pre_post_search_complete}, resistance model "
            f"{o.audit_resistance_model_search_complete}",
        )

    context_label = ",".join(o.persistence_context_identities) or "(unnamed context)"
    pattern_label = o.persistence_pattern or "an unqualified persistence pattern"
    residual_label = (
        f", residual_target_presence_status={o.residual_target_presence_status}"
        if o.residual_target_presence_status
        else ""
    )
    facts = (
        f"crc_specific={o.crc_specific}, "
        f"malignant_cell_attribution={o.malignant_cell_attribution}, "
        f"molecular_layer={o.molecular_layer}, assay={o.assay_method or '(unspecified)'}, "
        f"protein_measurement_validation_status={o.protein_measurement_validation_status or '(n/a)'}, "
        f"clinical_context={o.clinical_context or '(unspecified)'}, "
        f"context_adequacy_status={o.context_adequacy_status}, "
        f"reproducibility_status={o.reproducibility_status}"
    )
    return (
        f"local persistence context {context_label!r} reported {pattern_label} "
        f"target expression{residual_label} ({facts})",
    )


def _measurement_result(item: ClassifiedPersistenceObservation) -> str:
    o = item.observation
    return (
        f"{o.observation_kind} for {o.target_identity!r} (context {o.context_key!r}, "
        f"as of {o.landscape_as_of})"
    )


#: kind -> a NON-inflated normalized treatment_state fact for the neutral EP's
#: study_context (E9 item 11; E10 review round 1 blocker 5). The Module must not
#: write clearly treated / refractory / paired-series evidence as
#: "not_applicable"; it maps only from the observation kind, never up to the
#: run's refractory mCRC context.
_KIND_TO_TREATMENT_STATE: dict[str, str] = {
    "REFRACTORY_OR_PRIOR_TREATED_PROTEIN": "refractory_or_prior_treated",
    "METASTATIC_LESION_PROTEIN": "metastatic_context",
    "PAIRED_PRE_POST_PROTEIN": "paired_pre_post",
    "TREATED_METASTATIC_TRANSCRIPT": "metastatic_context",
    "RESISTANCE_MODEL": "resistance_model",
    "TREATMENT_NAIVE_PRIMARY": "treatment_naive",
    "DIFFERENT_TUMOR_TYPE": "source_reported",
    "SEARCH_COMPLETION_AUDIT": "not_applicable",
}


def _study_context_facts(o: NormalizedPersistenceObservation) -> tuple[str, str, str]:
    """kind / fact-specific, NON-inflated study context for the neutral EP
    (E9 item 11). The Module never promotes a source study to "refractory
    metastatic colorectal cancer" -- the run's scientific context is pinned
    separately by context_key / the Instantiation; a source EP states only what
    the source itself is. Returns (indication, treatment_state, sample_type)."""

    kind = o.observation_kind
    treatment_state = _KIND_TO_TREATMENT_STATE[kind]
    if kind == "SEARCH_COMPLETION_AUDIT":
        return "not_applicable", treatment_state, "search_audit"
    if kind == "DIFFERENT_TUMOR_TYPE":
        return "different_tumor_type", treatment_state, "source_reported"
    if not o.crc_specific:
        return "not_crc_resolved", treatment_state, "source_reported"
    if kind == "TREATMENT_NAIVE_PRIMARY":
        return "colorectal_cancer", treatment_state, "treatment_naive_primary_crc_tissue"
    if kind == "RESISTANCE_MODEL":
        return "colorectal_cancer", treatment_state, "crc_treatment_resistance_model"
    if kind == "TREATED_METASTATIC_TRANSCRIPT":
        return "colorectal_cancer", treatment_state, "treated_or_metastatic_crc_malignant_compartment"
    if kind == "METASTATIC_LESION_PROTEIN":
        return "colorectal_cancer", treatment_state, "metastatic_crc_lesion_tissue"
    if kind == "PAIRED_PRE_POST_PROTEIN":
        return "colorectal_cancer", treatment_state, "paired_pre_post_treatment_crc_biopsy"
    # REFRACTORY_OR_PRIOR_TREATED_PROTEIN
    return "colorectal_cancer", treatment_state, "refractory_or_prior_treated_crc_tissue"


def _as_rejected(
    item: ClassifiedPersistenceObservation, reason: str, *, severity: str
) -> ClassifiedPersistenceObservation:
    return ClassifiedPersistenceObservation(
        observation=item.observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        persistence_implication="",
        qualifying_for_direct=False,
        qualifying_for_indirect=False,
    )


def _reused_package_is_compatible(
    existing: EvidencePackage,
    item: ClassifiedPersistenceObservation,
    candidate_id: str,
    canonical,
) -> str:
    o = item.observation
    if existing.provenance.get("source_id") != o.source_id:
        return "canonical EvidencePackage provenance.source_id differs from the observation"
    # E9 item 13: the reused EP's own provenance metadata must still equal the
    # resolved canonical SourceIndex record -- not just resolve to the same id.
    if (
        existing.provenance.get("source_type") != canonical.source_type
        or existing.provenance.get("source_identifier") != canonical.source_identifier
        or existing.provenance.get("locator") != canonical.locator
    ):
        return (
            "canonical EvidencePackage provenance (source_type / source_identifier "
            "/ locator) no longer matches the resolved canonical SourceIndex record"
        )
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
    classified: list[ClassifiedPersistenceObservation],
    *,
    module_input: Tgt03ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedPersistenceObservation],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates). ``extra_rejections``
    carry a ``rejection_severity`` -- a HARD one rejects the whole run."""

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedPersistenceObservation] = []
    dropped: list[tuple[str, str]] = []
    seen_dedup: set[tuple] = set()
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

        # TGT-03-specific dedup: a SEARCH_COMPLETION_AUDIT EP is NEVER a dedup
        # loser; every other observation is a true duplicate only when source_id
        # + claim + every classification-driving fact + its LOCAL
        # persistence-context identity all match.
        if o.observation_kind != "SEARCH_COMPLETION_AUDIT":
            key = _dedup_key(o)
            if key in seen_dedup:
                dropped.append(
                    (
                        o.observation_id,
                        "true duplicate (same source_id + claim + every "
                        "classification-driving fact + persistence-context identity)",
                    )
                )
                continue
            seen_dedup.add(key)

        existing = evidence_library.resolve(o.observation_id)
        if existing is not None:
            why = _reused_package_is_compatible(
                existing, item, module_input.candidate_id, canonical
            )
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
        sc_indication, sc_treatment_state, sc_sample_type = _study_context_facts(o)
        study_context = {
            "indication": sc_indication,
            "treatment_state": sc_treatment_state,
            "sample_type": sc_sample_type,
        }
        for key in (*_KEYS_ALWAYS, *_AUDIT_KEYS):
            study_context[key] = getattr(o, key)
        package = EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=o.claim,
            measurement={
                "type": "adc_target_treatment_metastatic_persistence_observation",
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
