"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified soluble-antigen observations (E15 item 11; E16 tightening 6). One
observation -> one canonical EP. An existing canonical package is reused EXACTLY
(no allocator call, no new body). Provenance comes from the resolved canonical
``SourceIndex`` record. On reuse, ``observation_id`` is part of the exact-reuse
identity parity, and every classification / absence driving field RELEVANT TO
THAT OBSERVATION KIND -- including ``circulating_soluble_target_status`` and
``sink_materiality_outcome`` -- must be present AND equal on the canonical
package's study_context, and the reused EP's own provenance source_type /
source_identifier / locator must still equal the resolved canonical SourceIndex
record.

There is NO dedicated typed raw numeric field for soluble antigen and therefore
NO TGT-04-style symmetric raw-value reuse-parity branch -- a source-reported
numeric fact ("serum soluble target 18 ng/mL", "below assay LLOQ", "K_D 2 nM")
lives inside the neutral ``claim`` string, which the ordinary claim +
classification-driving field parity already covers.

E16 tightening 6: ``claim`` / ``sink_exposure_context_id`` / basis strings use
EXACT string presence-and-value equality for reuse / dedup parity -- NO
``.strip()``, lowercasing or whitespace normalization before equality. ``"A"``
and ``"A "`` are NOT the same factual representation.

TGT-07 dedup (the improved TGT-03 rule): the module does NOT unconditionally copy
the E8 ``(source_id, claim)`` dedup. ``observation_id`` is the authoritative
observation identity (a duplicate is a HARD run rejection, handled in
``module.py``, BEFORE this semantic dedup). Two normalized records are collapsed
as a true duplicate ONLY when their ``source_id`` AND ``claim`` AND every
classification-driving fact AND their local ``sink_exposure_context_id`` all
match. Same source_id + same claim + a DIFFERENT ``sink_exposure_context_id`` ->
BOTH survive. A SEARCH_COMPLETION_AUDIT EP is never a dedup loser.
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    ClassifiedSolubleAntigenObservation,
    EmittedEvidence,
    NormalizedSolubleAntigenObservation,
    Tgt07ModuleInput,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "a TGT-07 POSITIVE / NEGATIVE / CONFLICTING sink-liability conclusion",
    "a universal material soluble-antigen sink concentration / sink-ratio range",
    "a NEGATIVE / DIRECT Gate proposal or a machine POTENTIAL_FATAL_PATTERN",
    "a TGT-01 / TGT-02 / TGT-03 / TGT-04 / TGT-05 / TGT-06 / TGT-08 conclusion",
    "a Candidate-level Decision / KILL / HOLD, an ADC-efficacy claim or a dose recommendation",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single observation; it carries no Gate-relative grade, direction or "
    "sink-liability implication",
    "a measured circulating soluble-antigen value -- including a low or "
    "below-assay-limit value -- is not a material-sink threshold",
    "Gate-relative interpretation (Evidence-Ladder rung, Direction x Strength, "
    "fatal_review) is applied by the aggregate / review layer, not this package",
)
_NEUTRAL_CEILING = (
    "an observation-level soluble-antigen / sheddase / secreted-isoform / "
    "search fact for the named target"
)

_KEYS_ALWAYS: tuple[str, ...] = (
    "observation_id",
    "target_identity",
    "context_key",
    "landscape_as_of",
    "observation_kind",
    "analysis_method",
    "circulating_soluble_target_status",
    "circulating_soluble_target_basis",
    "cohort_class",
    "cohort_class_basis",
    "sink_materiality_outcome",
    "sink_materiality_outcome_basis",
    "analysis_validation_status",
    "analysis_validation_basis",
    "tmdd_input_adequacy_status",
    "tmdd_input_adequacy_basis",
    "same_target_therapeutic_match_status",
    "same_target_therapeutic_match_basis",
    "same_target_therapeutic_ref",
    "soluble_antigen_attribution_status",
    "soluble_antigen_attribution_basis",
    "exposure_scenario_class",
    "exposure_scenario_basis",
    "reproducibility_status",
    "reproducibility_basis",
    "sink_exposure_context_id",
    "sink_exposure_context_basis",
)
_AUDIT_KEYS: tuple[str, ...] = (
    "audit_search_scope",
    "audit_sources_searched",
    "audit_landscape_as_of",
    "audit_public_soluble_antigen_search_complete",
    "audit_soluble_antigen_quantitation_search_complete",
    "audit_crc_patient_quantitation_subspace_search_complete",
    "audit_healthy_donor_quantitation_subspace_search_complete",
    "audit_sheddase_processing_search_complete",
    "audit_secreted_isoform_search_complete",
    "audit_same_target_pk_pd_or_tmdd_search_complete",
    "audit_unresolved_item_keys",
    "audit_qualifying_direct_evidence_context_ids",
)


def _parity_keys(observation: NormalizedSolubleAntigenObservation) -> tuple[str, ...]:
    keys = list(_KEYS_ALWAYS)
    if observation.observation_kind == "SEARCH_COMPLETION_AUDIT":
        keys.extend(_AUDIT_KEYS)
    return tuple(keys)


def _dedup_key(o: NormalizedSolubleAntigenObservation) -> tuple:
    """A true-duplicate key: source_id + claim + every classification-driving fact
    + the local sink_exposure_context_id. EXACT strings -- no ``.strip()`` /
    lowercasing / whitespace normalization (E16 tightening 6). Any difference
    (including a trailing space in ``claim`` or ``sink_exposure_context_id``)
    makes two records DISTINCT."""

    return (
        o.source_id,
        o.claim,
        o.sink_exposure_context_id,
        tuple(getattr(o, k) for k in _parity_keys(o) if k != "observation_id"),
    )


def _directly_supports(item: ClassifiedSolubleAntigenObservation) -> tuple[str, ...]:
    """State the observation's ACTUAL fields (E15 item 11 Gate-neutral factual
    contract). Never assume a qualified / documented / material claim from the
    observation kind. A source-reported numeric fact lives only in the neutral
    ``claim`` -- it is deliberately NOT re-stated here."""

    o = item.observation
    if o.observation_kind == "SEARCH_COMPLETION_AUDIT":
        state = (
            "declared public soluble-antigen-evidence search complete"
            if o.audit_public_soluble_antigen_search_complete
            else "declared public soluble-antigen-evidence search NOT yet complete"
        )
        return (
            f"a soluble-antigen-evidence search-completion record as of "
            f"{o.audit_landscape_as_of}: {state}; components -- "
            f"quantitation {o.audit_soluble_antigen_quantitation_search_complete} "
            f"(CRC-patient subspace "
            f"{o.audit_crc_patient_quantitation_subspace_search_complete}, "
            f"healthy-donor subspace "
            f"{o.audit_healthy_donor_quantitation_subspace_search_complete}), "
            f"sheddase processing {o.audit_sheddase_processing_search_complete}, "
            f"secreted isoform {o.audit_secreted_isoform_search_complete}, "
            f"same-target PK / PD or TMDD "
            f"{o.audit_same_target_pk_pd_or_tmdd_search_complete}",
        )

    ctx_label = o.sink_exposure_context_id or "(no sink-exposure context)"
    facts = (
        f"circulating_soluble_target_status="
        f"{o.circulating_soluble_target_status or '(unspecified)'}, "
        f"cohort_class={o.cohort_class or '(unspecified)'}, "
        f"analysis_method={o.analysis_method or '(unspecified)'}, "
        f"analysis_validation_status={o.analysis_validation_status}, "
        f"tmdd_input_adequacy_status={o.tmdd_input_adequacy_status}, "
        f"same_target_therapeutic_match_status={o.same_target_therapeutic_match_status}, "
        f"soluble_antigen_attribution_status={o.soluble_antigen_attribution_status}, "
        f"exposure_scenario_class={o.exposure_scenario_class or '(n/a)'}, "
        f"sink_materiality_outcome={o.sink_materiality_outcome}, "
        f"reproducibility_status={o.reproducibility_status}"
    )
    return (
        f"sink-exposure context {ctx_label!r} carried a {o.observation_kind} "
        f"observation for the target ({facts})",
    )


def _measurement_result(item: ClassifiedSolubleAntigenObservation) -> str:
    o = item.observation
    return (
        f"{o.observation_kind} for {o.target_identity!r} (context {o.context_key!r}, "
        f"as of {o.landscape_as_of})"
    )


def _study_context_facts(
    o: NormalizedSolubleAntigenObservation,
) -> tuple[str, str, str]:
    """kind / fact-specific, NON-inflated study context for the neutral EP
    (E15 item 11; the E8 / E10 / E12 / E14 non-inflation gene). Returns
    (indication, treatment_state, sample_type). TGT-07 soluble-antigen sink
    liability is treatment-agnostic -- ``treatment_state`` is "not_applicable" for
    EVERY observation kind (E16-2). ``indication`` / ``sample_type`` stay
    kind-specific factual; the Module never inflates a healthy-donor / inference /
    audit observation, and never to "refractory_mcrc"."""

    kind = o.observation_kind
    if kind == "SEARCH_COMPLETION_AUDIT":
        return "not_applicable", "not_applicable", "search_audit"
    if kind == "PREDICTED_CLEAVAGE_SITE_INFERENCE":
        return "predicted_cleavage_inference", "not_applicable", "predicted_cleavage_site_inference"
    if kind == "FAMILY_ANALOGY_SHEDDING_INFERENCE":
        return "family_analogy_inference", "not_applicable", "family_analogy_shedding_inference"
    if kind == "SHEDDASE_SUBSTRATE_STATUS":
        return "target_sheddase_biology", "not_applicable", "documented_sheddase_substrate_status"
    if kind == "SECRETED_ISOFORM":
        return "target_isoform_biology", "not_applicable", "validated_secreted_isoform"
    if kind == "SOLUBLE_ANTIGEN_QUANTITATION":
        if o.cohort_class == "CRC_PATIENT_SERUM":
            return "colorectal_cancer", "not_applicable", "crc_patient_serum_soluble_antigen_quantitation"
        if o.cohort_class == "HEALTHY_DONOR_SERUM":
            return "healthy_donor_reference", "not_applicable", "healthy_donor_serum_soluble_antigen_quantitation"
        return "soluble_antigen_quantitation_context", "not_applicable", "source_reported"
    if kind == "CLINICAL_ANTIGEN_SINK_PK_EFFECT":
        return "same_target_therapeutic_pk_pd", "not_applicable", "clinical_antigen_sink_pk_pd_effect"
    # SOLUBLE_ANTIGEN_TMDD_ANALYSIS
    return "target_mediated_disposition_analysis", "not_applicable", "soluble_antigen_tmdd_analysis"


def _as_rejected(
    item: ClassifiedSolubleAntigenObservation, reason: str, *, severity: str
) -> ClassifiedSolubleAntigenObservation:
    return ClassifiedSolubleAntigenObservation(
        observation=item.observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        sink_liability_implication="",
        qualifying_direct_material_sink=False,
        qualifying_direct_no_material_sink=False,
        qualifying_direct_mixed=False,
        qualifying_indirect=False,
    )


def _reused_package_is_compatible(
    existing: EvidencePackage,
    item: ClassifiedSolubleAntigenObservation,
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
    classified: list[ClassifiedSolubleAntigenObservation],
    *,
    module_input: Tgt07ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedSolubleAntigenObservation],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates). ``extra_rejections``
    carry a ``rejection_severity`` -- a HARD one rejects the whole run."""

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedSolubleAntigenObservation] = []
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

        # TGT-07-specific dedup: a SEARCH_COMPLETION_AUDIT EP is NEVER a dedup
        # loser; every other observation is a true duplicate only when source_id
        # + claim + every classification-driving fact + its local
        # sink_exposure_context_id all match EXACTLY.
        if o.observation_kind != "SEARCH_COMPLETION_AUDIT":
            key = _dedup_key(o)
            if key in seen_dedup:
                dropped.append(
                    (
                        o.observation_id,
                        "true duplicate (same source_id + claim + every "
                        "classification-driving fact + sink_exposure_context_id)",
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
                "type": "adc_target_soluble_antigen_sink_liability_observation",
                "analyte": o.target_identity,
                "readout": f"{o.observation_kind}/{o.analysis_method or 'search_audit'}",
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
