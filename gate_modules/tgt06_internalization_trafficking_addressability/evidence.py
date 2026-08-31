"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified internalization observations (E13 item 11, E14-7). One observation ->
one canonical EP. An existing canonical package is reused EXACTLY (no allocator
call, no new body). Provenance comes from the resolved canonical ``SourceIndex``
record. On reuse, ``observation_id`` is part of the exact-reuse identity parity,
and every classification / absence driving field RELEVANT TO THAT OBSERVATION
KIND -- including ``internalization_outcome`` and the
antibody / epitope / affinity / conjugation factual identity fields (E14-7
tightening 5) -- must be present AND equal on the canonical package's
study_context, and the reused EP's own provenance source_type / source_identifier
/ locator must still equal the resolved canonical SourceIndex record.

There is NO dedicated typed raw numeric field for internalization and therefore NO
TGT-04-style symmetric raw-value reuse-parity branch (E14-7 tightening 6) -- a
source-reported numeric assay fact ("65% internalized at 4 h") lives inside the
neutral ``claim`` string, which the ordinary claim + classification-driving field
parity already covers.

TGT-06 dedup (E14-7, the improved TGT-03 rule): the module does NOT
unconditionally copy the E8 ``(source_id, claim)`` dedup. ``observation_id`` is
the authoritative observation identity (a duplicate is a HARD run rejection,
handled in ``module.py``, BEFORE this semantic dedup). Two normalized records are
collapsed as a true duplicate ONLY when their ``source_id`` AND ``claim`` AND
every classification-driving fact AND their LOCAL configuration identity
projection all match. Same source_id + same claim + a DIFFERENT
internalization_configuration_id -> BOTH survive. A SEARCH_COMPLETION_AUDIT EP is
never a dedup loser.

The package carries observation-level meaning only -- a per-configuration
internalization / trafficking fact, a receptor-biology / same-target-ADC
addressability fact, an inference context, or an audited search-completion fact.
It never carries "passes TGT-06", "the target is internalizing / non-internalizing",
"the ADC will work", or any TGT-02 / TGT-03 / TGT-04 conclusion.
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    ClassifiedInternalizationObservation,
    EmittedEvidence,
    NormalizedInternalizationObservation,
    Tgt06ModuleInput,
    configuration_identity_projection,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "a TGT-06 POSITIVE / NEGATIVE / addressable / non-internalizing conclusion",
    "a target-wide internalizing / non-internalizing claim",
    "a NEGATIVE / DIRECT Gate proposal or a machine POTENTIAL_FATAL_PATTERN",
    "a TGT-02 baseline malignant-cell coverage substitution",
    "a TGT-03 treatment / metastatic persistence conclusion",
    "a TGT-04 surface-availability / density conclusion",
    "a Candidate-level Decision / KILL / HOLD, and any ADC-efficacy or payload-release claim",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single observation; it carries no Gate-relative grade, direction or "
    "addressability implication",
    "internalization efficiency is configuration-specific -- this observation is "
    "not a target-intrinsic internalization rate",
    "Gate-relative interpretation (Evidence-Ladder rung, Direction x Strength, "
    "fatal_review) is applied by the aggregate / review layer, not this package",
)
_NEUTRAL_CEILING = (
    "an observation-level internalization / trafficking / search fact for the named target"
)

_KEYS_ALWAYS: tuple[str, ...] = (
    "observation_id",
    "target_identity",
    "context_key",
    "landscape_as_of",
    "observation_kind",
    "assay_method",
    "assay_validation_status",
    "assay_validation_basis",
    "crc_specific",
    "surface_context_class",
    "surface_context_basis",
    "context_adequacy_status",
    "context_adequacy_basis",
    "internalization_outcome",
    "internalization_outcome_basis",
    "reproducibility_status",
    "reproducibility_basis",
    "declared_multi_configuration_analysis",
    "internalization_configuration_id",
    "internalization_configuration_ids",
    "configuration_identity_basis",
    # --- E14-7 tightening 5: the factual configuration identity fields join the
    #     exact reuse / dedup parity.
    "antibody_identity",
    "epitope_identity_or_region",
    "affinity_context",
    "conjugation_context",
)
_AUDIT_KEYS: tuple[str, ...] = (
    "audit_search_scope",
    "audit_sources_searched",
    "audit_landscape_as_of",
    "audit_public_internalization_search_complete",
    "audit_antibody_configuration_internalization_search_complete",
    "audit_productive_trafficking_search_complete",
    "audit_same_target_adc_functional_delivery_search_complete",
    "audit_receptor_endocytosis_and_inference_search_complete",
    "audit_unresolved_item_keys",
    "audit_qualifying_direct_configuration_ids",
)


def _parity_keys(observation: NormalizedInternalizationObservation) -> tuple[str, ...]:
    keys = list(_KEYS_ALWAYS)
    if observation.observation_kind == "SEARCH_COMPLETION_AUDIT":
        keys.extend(_AUDIT_KEYS)
    return tuple(keys)


def _dedup_key(o: NormalizedInternalizationObservation) -> tuple:
    """A true-duplicate key: source_id + claim + every classification-driving fact
    + the LOCAL configuration identity projection. Any configuration-projection
    difference makes two records DISTINCT scientific observations (E14-7)."""

    return (
        o.source_id,
        o.claim.strip(),
        tuple(sorted(configuration_identity_projection(o))),
        tuple(getattr(o, k) for k in _parity_keys(o) if k != "observation_id"),
    )


def _directly_supports(item: ClassifiedInternalizationObservation) -> tuple[str, ...]:
    """State the observation's ACTUAL fields (E13 item 11 Gate-neutral factual
    contract). Never assume a disease-relevant / qualified / integrated claim from
    the observation kind. A source-reported numeric assay fact lives only in the
    neutral ``claim`` -- it is deliberately NOT re-stated here."""

    o = item.observation
    if o.observation_kind == "SEARCH_COMPLETION_AUDIT":
        state = (
            "declared public internalization-evidence search complete"
            if o.audit_public_internalization_search_complete
            else "declared public internalization-evidence search NOT yet complete"
        )
        return (
            f"an internalization-evidence search-completion record as of "
            f"{o.audit_landscape_as_of}: {state}; components -- "
            f"antibody-configuration internalization "
            f"{o.audit_antibody_configuration_internalization_search_complete}, "
            f"productive trafficking {o.audit_productive_trafficking_search_complete}, "
            f"same-target ADC functional-delivery precedent "
            f"{o.audit_same_target_adc_functional_delivery_search_complete}, "
            f"receptor endocytosis and inference "
            f"{o.audit_receptor_endocytosis_and_inference_search_complete}",
        )

    config_label = ",".join(sorted(configuration_identity_projection(o))) or "(configuration not disclosed)"
    facts = (
        f"crc_specific={o.crc_specific}, "
        f"surface_context_class={o.surface_context_class or '(unspecified)'}, "
        f"context_adequacy_status={o.context_adequacy_status}, "
        f"assay={o.assay_method or '(unspecified)'}, "
        f"assay_validation_status={o.assay_validation_status}, "
        f"internalization_outcome={o.internalization_outcome}, "
        f"reproducibility_status={o.reproducibility_status}, "
        f"configuration_identity_state={o.configuration_identity_state}"
    )
    return (
        f"local configuration {config_label!r} carried a {o.observation_kind} "
        f"observation for the target ({facts})",
    )


def _measurement_result(item: ClassifiedInternalizationObservation) -> str:
    o = item.observation
    return (
        f"{o.observation_kind} for {o.target_identity!r} (context {o.context_key!r}, "
        f"as of {o.landscape_as_of})"
    )


def _study_context_facts(
    o: NormalizedInternalizationObservation,
) -> tuple[str, str, str]:
    """kind / fact-specific, NON-inflated study context for the neutral EP
    (E13 item 11; the E8 / E10 / E12 non-inflation gene). Returns (indication,
    treatment_state, sample_type). TGT-06 internalization addressability is
    treatment-agnostic -- ``treatment_state`` is "not_applicable" for EVERY
    observation kind (E14-2). ``indication`` / ``sample_type`` stay kind-specific
    factual; the Module never inflates a non-CRC / inference / audit observation
    to a disease-relevant integrated internalization observation, and never to
    "refractory_mcrc"."""

    kind = o.observation_kind
    if kind == "SEARCH_COMPLETION_AUDIT":
        return "not_applicable", "not_applicable", "search_audit"
    if kind == "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE":
        return "receptor_family_inference", "not_applicable", "receptor_family_membership_inference"
    if kind == "SURFACE_LOCALIZATION_ONLY_INFERENCE":
        return "surface_localization_inference", "not_applicable", "surface_localization_only_inference"
    if kind == "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY":
        return "target_receptor_biology", "not_applicable", "constitutive_endocytosis_or_receptor_biology"
    if kind == "SAME_TARGET_ADC_DELIVERY_PRECEDENT":
        return "same_target_adc_precedent", "not_applicable", "successful_same_target_adc_functional_delivery"
    if o.surface_context_class == "NON_CRC_CONTEXT" or not o.crc_specific:
        return "non_crc_internalization_context", "not_applicable", "source_reported"
    if o.surface_context_class == "WELL_MATCHED_CRC_MODEL":
        return "colorectal_cancer", "not_applicable", "well_matched_crc_malignant_cell_model"
    # CRC_MALIGNANT_CELLS or an unresolved CRC context
    return "colorectal_cancer", "not_applicable", "crc_malignant_cell_internalization_trafficking"


def _as_rejected(
    item: ClassifiedInternalizationObservation, reason: str, *, severity: str
) -> ClassifiedInternalizationObservation:
    return ClassifiedInternalizationObservation(
        observation=item.observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        addressability_implication="",
        qualifying_direct_productive=False,
        qualifying_direct_failure=False,
        qualifying_indirect=False,
    )


def _reused_package_is_compatible(
    existing: EvidencePackage,
    item: ClassifiedInternalizationObservation,
    candidate_id: str,
    canonical,
) -> str:
    o = item.observation
    if existing.provenance.get("source_id") != o.source_id:
        return "canonical EvidencePackage provenance.source_id differs from the observation"
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
                "canonical EvidencePackage is missing the classification-driving "
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
    classified: list[ClassifiedInternalizationObservation],
    *,
    module_input: Tgt06ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedInternalizationObservation],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates). ``extra_rejections``
    carry a ``rejection_severity`` -- a HARD one rejects the whole run."""

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedInternalizationObservation] = []
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

        # TGT-06-specific dedup: a SEARCH_COMPLETION_AUDIT EP is NEVER a dedup
        # loser; every other observation is a true duplicate only when source_id
        # + claim + every classification-driving fact + its LOCAL configuration
        # identity projection all match.
        if o.observation_kind != "SEARCH_COMPLETION_AUDIT":
            key = _dedup_key(o)
            if key in seen_dedup:
                dropped.append(
                    (
                        o.observation_id,
                        "true duplicate (same source_id + claim + every "
                        "classification-driving fact + configuration identity)",
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
                "type": "adc_target_internalization_trafficking_addressability_observation",
                "analyte": o.target_identity,
                "readout": f"{o.observation_kind}/{o.assay_method or 'search_audit'}",
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
