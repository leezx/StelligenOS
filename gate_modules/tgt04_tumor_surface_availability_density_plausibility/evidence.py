"""Build atomic, Gate-NEUTRAL PR A ``EvidencePackage`` objects from admissible
classified surface observations (E11 item 11, E12-7). One observation -> one
canonical EP. An existing canonical package is reused EXACTLY (no allocator call,
no new body). Provenance comes from the resolved canonical ``SourceIndex``
record. On reuse, every classification-driving field RELEVANT TO THAT OBSERVATION
KIND must be present AND equal, and -- for a QUANTITATIVE_SURFACE_DENSITY
observation -- the raw ``reported_density_value`` / ``reported_density_unit`` /
``reported_density_summary`` must have SYMMETRIC presence-and-value parity
(present on one side only, or a value / unit / summary difference, is a HARD
identity integrity failure; identical on both or absent on both is compatible).
The raw strings are never coerced to a number (E12 tightening 4).

TGT-04 dedup (E12-7, the improved TGT-03 rule): the module does NOT
unconditionally copy the E8 ``(source_id, claim)`` dedup. ``observation_id`` is
the authoritative observation identity (a duplicate is a HARD run rejection,
handled in ``module.py``, BEFORE this semantic dedup). Two normalized records are
collapsed as a true duplicate ONLY when their ``source_id`` AND ``claim`` AND
every classification-driving fact AND their LOCAL surface-context identity all
match. Any surface-context difference -> both survive. A SEARCH_COMPLETION_AUDIT
EP is never a dedup loser.

The package carries observation-level meaning only -- a per-context quantitative
density fact, a membranous-IHC / surface-proteomics localization fact, a
subcellular-localization / topology / non-CRC / RNA-proxy context, or an audited
search-completion fact. It never carries "passes TGT-04", "adequate antigen
density established", "the antigen density is inadequate for an ADC", "should be
killed", or any TGT-02 / TGT-03 / TGT-06 conclusion.
"""

from __future__ import annotations

from src.objects.decision_model import EvidencePackage

from .contracts import (
    ClassifiedSurfaceObservation,
    EmittedEvidence,
    NormalizedSurfaceObservation,
    Tgt04ModuleInput,
)
from .ports import (
    EvidenceIdAllocatorPort,
    ExistingEvidenceLibraryPort,
    SourceResolverPort,
)

_NEUTRAL_DOES_NOT_SUPPORT: tuple[str, ...] = (
    "an adequate antigen density established / inadequate antigen density conclusion for TGT-04",
    "a NEGATIVE / DIRECT Gate proposal or a reproducible fatal pattern",
    "a TGT-02 baseline malignant-cell coverage substitution",
    "a TGT-03 treatment / metastatic persistence conclusion",
    "a TGT-06 internalization conclusion",
    "a Candidate-level Decision / KILL / HOLD",
)
_NEUTRAL_LIMITATIONS: tuple[str, ...] = (
    "a single observation; it carries no Gate-relative grade, direction or "
    "density-implication",
    "Gate-relative interpretation (Evidence-Ladder rung, Direction x Strength, "
    "fatal_review) is applied by the aggregate / review layer, not this package",
)
_NEUTRAL_CEILING = "an observation-level surface-availability / search fact for the named target"

_KEYS_ALWAYS: tuple[str, ...] = (
    "observation_id",
    "target_identity",
    "context_key",
    "landscape_as_of",
    "observation_kind",
    "molecular_layer",
    "assay_method",
    "measurement_validation_status",
    "measurement_validation_basis",
    "crc_specific",
    "surface_context_class",
    "surface_context_basis",
    "context_adequacy_status",
    "context_adequacy_basis",
    "malignant_cell_attribution",
    "malignant_attribution_basis",
    "surface_localization_status",
    "surface_localization_basis",
    "density_plausibility_status",
    "density_plausibility_basis",
    "surface_antigen_level",
    "surface_antigen_level_basis",
    "reproducibility_status",
    "reproducibility_basis",
    "surface_context_id",
    "surface_context_ids",
    "declared_multi_context_analysis",
)
#: raw density facts -- present on a QUANTITATIVE_SURFACE_DENSITY EP; SYMMETRIC
#: presence-and-value parity keys on reuse (E12 tightening 4).
_DENSITY_KEYS: tuple[str, ...] = (
    "reported_density_value",
    "reported_density_unit",
    "reported_density_summary",
)
_AUDIT_KEYS: tuple[str, ...] = (
    "audit_search_scope",
    "audit_sources_searched",
    "audit_landscape_as_of",
    "audit_public_surface_search_complete",
    "audit_quantitative_surface_density_search_complete",
    "audit_membranous_ihc_search_complete",
    "audit_surface_proteomics_search_complete",
    "audit_subcellular_localization_search_complete",
    "audit_unresolved_item_keys",
    "audit_qualifying_direct_surface_context_ids",
    "audit_qualifying_indirect_surface_context_ids",
)


def _parity_keys(observation: NormalizedSurfaceObservation) -> tuple[str, ...]:
    keys = list(_KEYS_ALWAYS)
    if observation.observation_kind == "QUANTITATIVE_SURFACE_DENSITY":
        keys.extend(_DENSITY_KEYS)
    if observation.observation_kind == "SEARCH_COMPLETION_AUDIT":
        keys.extend(_AUDIT_KEYS)
    return tuple(keys)


def _dedup_key(o: NormalizedSurfaceObservation) -> tuple:
    """A true-duplicate key: source_id + claim + every classification-driving
    fact + the LOCAL surface-context identity. Any surface-context difference
    makes two records DISTINCT scientific observations (E12-7)."""

    return (
        o.source_id,
        o.claim.strip(),
        tuple(sorted(o.surface_context_identities)),
        tuple(getattr(o, k) for k in _parity_keys(o) if k != "observation_id"),
    )


def _directly_supports(item: ClassifiedSurfaceObservation) -> tuple[str, ...]:
    """State the observation's ACTUAL fields (E11 item 11 Gate-neutral factual
    contract). Never assume a malignant / CRC / qualified-context / complete
    claim from the observation kind."""

    o = item.observation
    if o.observation_kind == "SEARCH_COMPLETION_AUDIT":
        state = (
            "declared public surface-availability search complete"
            if o.audit_public_surface_search_complete
            else "declared public surface-availability search NOT yet complete"
        )
        return (
            f"a surface-availability search-completion record as of "
            f"{o.audit_landscape_as_of}: {state}; components -- quantitative surface "
            f"density {o.audit_quantitative_surface_density_search_complete}, "
            f"membranous IHC {o.audit_membranous_ihc_search_complete}, cell-surface "
            f"proteomics {o.audit_surface_proteomics_search_complete}, subcellular "
            f"localization {o.audit_subcellular_localization_search_complete}",
        )

    context_label = ",".join(o.surface_context_identities) or "(unnamed context)"
    density_bits = ""
    if o.reported_density_value or o.reported_density_unit or o.reported_density_summary:
        density_bits = (
            f", reported_density_value={o.reported_density_value or '(absent)'} "
            f"reported_density_unit={o.reported_density_unit or '(absent)'} "
            f"reported_density_summary={o.reported_density_summary or '(absent)'} "
            "(raw factual measurement, never numerically compared)"
        )
    facts = (
        f"crc_specific={o.crc_specific}, "
        f"malignant_cell_attribution={o.malignant_cell_attribution}, "
        f"molecular_layer={o.molecular_layer}, assay={o.assay_method or '(unspecified)'}, "
        f"measurement_validation_status={o.measurement_validation_status or '(n/a)'}, "
        f"surface_context_class={o.surface_context_class or '(unspecified)'}, "
        f"context_adequacy_status={o.context_adequacy_status}, "
        f"surface_localization_status={o.surface_localization_status or '(unspecified)'}, "
        f"density_plausibility_status={o.density_plausibility_status or '(unspecified)'}, "
        f"surface_antigen_level={o.surface_antigen_level or '(unspecified)'}, "
        f"reproducibility_status={o.reproducibility_status}"
    )
    return (
        f"local surface context {context_label!r} reported a "
        f"{o.observation_kind} observation for the target{density_bits} ({facts})",
    )


def _measurement_result(item: ClassifiedSurfaceObservation) -> str:
    o = item.observation
    return (
        f"{o.observation_kind} for {o.target_identity!r} (context {o.context_key!r}, "
        f"as of {o.landscape_as_of})"
    )


#: kind -> a NON-inflated normalized (indication, treatment_state, sample_type)
#: for the neutral EP's study_context (E11 item 11; the E8 / E10 non-inflation
#: gene). The Module never promotes a non-CRC / prediction / RNA-proxy / audit
#: observation to a CRC malignant-cell surface density measurement; the run's
#: scientific context is pinned separately by context_key / the Instantiation.
#: TGT-04 surface availability is a treatment-agnostic property -- the source EP
#: never carries a treatment axis it did not itself state, so treatment_state is
#: "not_applicable" for every surface observation kind.
def _study_context_facts(o: NormalizedSurfaceObservation) -> tuple[str, str, str]:
    """kind / fact-specific, NON-inflated study context for the neutral EP.
    Returns (indication, treatment_state, sample_type)."""

    kind = o.observation_kind
    if kind == "SEARCH_COMPLETION_AUDIT":
        return "not_applicable", "not_applicable", "search_audit"
    if kind == "NON_CRC_SURFACE_EVIDENCE":
        return "non_crc_surface_evidence", "not_applicable", "source_reported"
    if kind == "TOPOLOGY_OR_GO_PREDICTION":
        return "prediction_only", "not_applicable", "sequence_topology_or_go_prediction"
    if not o.crc_specific:
        return "not_crc_resolved", "not_applicable", "source_reported"
    if kind == "RNA_SURFACE_PROXY":
        return "colorectal_cancer", "not_applicable", "crc_rna_surface_proxy"
    if kind == "SUBCELLULAR_LOCALIZATION":
        return "colorectal_cancer", "not_applicable", "crc_subcellular_localization_evidence"
    if kind == "MEMBRANOUS_IHC":
        return "colorectal_cancer", "not_applicable", "crc_membranous_ihc_tissue"
    if kind == "SURFACE_PROTEOMICS":
        return "colorectal_cancer", "not_applicable", "crc_cell_surface_proteomics"
    # QUANTITATIVE_SURFACE_DENSITY
    if o.surface_context_class == "WELL_MATCHED_CRC_MODEL":
        return "colorectal_cancer", "not_applicable", "well_matched_crc_malignant_cell_model"
    return "colorectal_cancer", "not_applicable", "crc_malignant_cell_quantitative_surface_density"


def _as_rejected(
    item: ClassifiedSurfaceObservation, reason: str, *, severity: str
) -> ClassifiedSurfaceObservation:
    return ClassifiedSurfaceObservation(
        observation=item.observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        density_implication="",
        qualifying_for_direct=False,
        qualifying_for_indirect=False,
    )


def _reused_package_is_compatible(
    existing: EvidencePackage,
    item: ClassifiedSurfaceObservation,
    candidate_id: str,
    canonical,
) -> str:
    o = item.observation
    if existing.provenance.get("source_id") != o.source_id:
        return "canonical EvidencePackage provenance.source_id differs from the observation"
    # E11 item 13: the reused EP's own provenance metadata must still equal the
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
        # --- the raw density facts have a SYMMETRIC presence-and-value contract
        #     (E12 review round 1, blocker 3): a canonical package that simply
        #     omits the key is "absent" -- absent on both sides is COMPATIBLE.
        #     present on one side only, or a value / unit / summary difference, is
        #     HARD. The raw string is never coerced to a number.
        if key in _DENSITY_KEYS:
            canonical_value = str(existing.study_context.get(key, "")).strip()
            current_value = str(current[key]).strip()
            if bool(canonical_value) != bool(current_value):
                return (
                    f"raw density field {key!r}: present on one side only "
                    f"(canonical {canonical_value!r} vs current {current_value!r}) "
                    "-- symmetric presence-and-value parity failure"
                )
            if canonical_value != current_value:
                return (
                    f"raw density field {key!r} = {canonical_value!r} on the canonical "
                    f"package but {current_value!r} on the current observation "
                    "(raw-density value / unit / summary drift)"
                )
            continue
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
    classified: list[ClassifiedSurfaceObservation],
    *,
    module_input: Tgt04ModuleInput,
    allocator: EvidenceIdAllocatorPort,
    source_resolver: SourceResolverPort,
    evidence_library: ExistingEvidenceLibraryPort,
) -> tuple[
    list[EmittedEvidence],
    list[ClassifiedSurfaceObservation],
    list[tuple[str, str]],
]:
    """Return (emitted, extra_rejections, dropped_duplicates). ``extra_rejections``
    carry a ``rejection_severity`` -- a HARD one rejects the whole run."""

    emitted: list[EmittedEvidence] = []
    extra_rejections: list[ClassifiedSurfaceObservation] = []
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

        # TGT-04-specific dedup: a SEARCH_COMPLETION_AUDIT EP is NEVER a dedup
        # loser; every other observation is a true duplicate only when source_id
        # + claim + every classification-driving fact + its LOCAL surface-context
        # identity all match.
        if o.observation_kind != "SEARCH_COMPLETION_AUDIT":
            key = _dedup_key(o)
            if key in seen_dedup:
                dropped.append(
                    (
                        o.observation_id,
                        "true duplicate (same source_id + claim + every "
                        "classification-driving fact + surface-context identity)",
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
        for key in (*_KEYS_ALWAYS, *_DENSITY_KEYS, *_AUDIT_KEYS):
            study_context[key] = getattr(o, key)
        package = EvidencePackage(
            evidence_id=evidence_id,
            schema_version=1,
            claim=o.claim,
            measurement={
                "type": "adc_target_tumor_surface_availability_density_observation",
                "analyte": o.target_identity,
                "readout": f"{o.observation_kind}/{o.molecular_layer or 'search_audit'}",
                "result": _measurement_result(item),
                "unit": o.reported_density_unit,
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
