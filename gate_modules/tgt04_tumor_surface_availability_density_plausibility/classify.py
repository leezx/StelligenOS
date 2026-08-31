"""Place each normalized surface observation into a FROZEN TGT-04 Evidence-Ladder
rung and give it a Module-owned Gate-relative density-implication reading
(E11 item 05 / 06, E12-3).

Verbatim mapping -- E12 has no discretion:

  QUANTITATIVE_SURFACE_DENSITY, crc_specific, MALIGNANT-attributed,
      molecular_layer includes PROTEIN
      AND measurement_validation_status == QUALIFIED + auditable basis
      AND a non-empty factual assay_method
      AND surface_context_class in {CRC_MALIGNANT_CELLS, WELL_MATCHED_CRC_MODEL}
      AND context_adequacy_status == QUALIFIED + surface_context_basis + basis
        -> rung DIRECT, qualifying_for_direct
           density_implication per the frozen density_direction_mapping
      (assay_method is an OPEN factual type -- there is NO closed assay
       whitelist; the "or well-matched CRC models" permission is DIRECT-only.)

  MEMBRANOUS_IHC / SURFACE_PROTEOMICS, crc_specific, MALIGNANT-attributed,
      surface_context_class == CRC_MALIGNANT_CELLS only
      AND context_adequacy_status == QUALIFIED + auditable bases
      AND surface_localization_status == SURFACE_LOCALIZED
        -> rung INDIRECT_STRONG, qualifying_for_indirect (never DIRECT; a
           well-matched CRC model localization observation is CONTEXTUAL, never
           an INDIRECT_STRONG rung -- the ceiling is limited by the CONTEXT).
           density_implication CONTEXTUAL -- localization is not antigen density.

  SUBCELLULAR_LOCALIZATION / TOPOLOGY_OR_GO_PREDICTION / NON_CRC_SURFACE_EVIDENCE
  / RNA_SURFACE_PROXY  -> rung WEAK, CONTEXTUAL (hypothesis / context only; never
                          above WEAK, never a surface-density claim; a pretty
                          membranous IHC on a non-CRC line stays WEAK).
  SEARCH_COMPLETION_AUDIT               -> rung "" , CONTEXTUAL (a neutral fact).

density_direction_mapping (strict; the Module never parses basis prose and never
coerces a raw density value to a number), applied ONLY to a qualifying DIRECT
observation, in this order:
  surface_antigen_level == NEGLIGIBLE_OR_UNDETECTABLE   -> OPPOSES_DENSITY_PLAUSIBILITY
  else density_plausibility_status == PLAUSIBLY_ADEQUATE -> SUPPORTS_DENSITY_PLAUSIBILITY
  else density_plausibility_status == NOT_PLAUSIBLY_ADEQUATE -> OPPOSES_DENSITY_PLAUSIBILITY
  else (MIXED_OR_UNRESOLVED / NOT_ESTABLISHED)          -> CONTEXTUAL
LOW_BUT_PRESENT alone decides nothing.

Hard locks:
  * a well-matched CRC model membranous-IHC / surface-proteomics observation
    never reaches INDIRECT_STRONG; a non-CRC / non-malignant / unresolved-context
    observation is CONTEXTUAL and does NOT discharge TGT-04 (not a HARD failure).
  * NON_CRC_SURFACE_EVIDENCE / RNA_SURFACE_PROXY never rise above WEAK.
  * a single observation is NEVER a Direction. This function only classifies a
    rung and a direction-SUPPORTING reading; ``aggregate`` produces the proposed
    Direction x Strength over a completed audited landscape.
"""

from __future__ import annotations

from .contracts import (
    ClassifiedSurfaceObservation,
    NormalizedSurfaceObservation,
    density_implication,
)

_DIRECT_KIND = "QUANTITATIVE_SURFACE_DENSITY"
_INDIRECT_STRONG_KINDS = ("MEMBRANOUS_IHC", "SURFACE_PROTEOMICS")
_WEAK_KINDS = (
    "SUBCELLULAR_LOCALIZATION",
    "TOPOLOGY_OR_GO_PREDICTION",
    "NON_CRC_SURFACE_EVIDENCE",
    "RNA_SURFACE_PROXY",
)
_DIRECT_CONTEXT_CLASSES = ("CRC_MALIGNANT_CELLS", "WELL_MATCHED_CRC_MODEL")


def _reject(
    observation: NormalizedSurfaceObservation, reason: str, *, severity: str = "SOFT"
) -> ClassifiedSurfaceObservation:
    return ClassifiedSurfaceObservation(
        observation=observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        density_implication="",
        qualifying_for_direct=False,
        qualifying_for_indirect=False,
    )


def _admit(
    observation: NormalizedSurfaceObservation,
    *,
    rung: str,
    implication: str,
    qualifying_direct: bool = False,
    qualifying_indirect: bool = False,
) -> ClassifiedSurfaceObservation:
    return ClassifiedSurfaceObservation(
        observation=observation,
        admissible=True,
        rejection_reason="",
        rejection_severity="",
        evidence_rung=rung,
        density_implication=implication,
        qualifying_for_direct=qualifying_direct,
        qualifying_for_indirect=qualifying_indirect,
    )


def classify_observation(
    observation: NormalizedSurfaceObservation, *, canonical_target_identity: str
) -> ClassifiedSurfaceObservation:
    """One observation -> one ClassifiedSurfaceObservation. Deterministic and
    single-valued."""

    # 1. an unresolved discovery / index lead establishes nothing.
    if not observation.primary_or_repository_source_resolved:
        return _reject(
            observation,
            "the observation is not resolved to a primary / repository source; a "
            "discovery or search-index lead does not establish a surface fact",
        )

    # 2. candidate <-> observation target identity must match (HARD misbinding).
    if observation.target_identity.strip() != canonical_target_identity.strip():
        return _reject(
            observation,
            f"observation targets {observation.target_identity!r}, not the "
            f"candidate's canonical target {canonical_target_identity!r} "
            "(evidence misbinding)",
            severity="HARD",
        )

    kind = observation.observation_kind

    # 3. SEARCH_COMPLETION_AUDIT -- a neutral audited-search fact.
    if kind == "SEARCH_COMPLETION_AUDIT":
        return _admit(observation, rung="", implication="CONTEXTUAL")

    # 4. WEAK-only kinds -- context / hypothesis only. A pretty membranous IHC on
    #    a non-CRC line still stays WEAK -- no smuggling non-CRC surface evidence
    #    up the ladder.
    if kind in _WEAK_KINDS:
        return _admit(observation, rung="WEAK", implication="CONTEXTUAL")

    # 5. INDIRECT_STRONG kinds -- validated membranous IHC / cell-surface
    #    proteomics. CRC_MALIGNANT_CELLS only -- a well-matched CRC model
    #    localization observation is CONTEXTUAL, never an INDIRECT_STRONG rung.
    if kind in _INDIRECT_STRONG_KINDS:
        if not observation.crc_specific:
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if (
            observation.surface_context_class == "CRC_MALIGNANT_CELLS"
            and observation.is_context_qualified
            and observation.is_malignant_attributed
            and observation.is_surface_localized
        ):
            return _admit(
                observation,
                rung="INDIRECT_STRONG",
                implication="CONTEXTUAL",
                qualifying_indirect=True,
            )
        # CRC membranous IHC / proteomics -- but not on a qualified
        # CRC_MALIGNANT_CELLS context, or malignant attribution / surface
        # localization not established: a CONTEXTUAL localization reading.
        return _admit(observation, rung="", implication="CONTEXTUAL")

    # 6. DIRECT kind -- quantitative cell-surface antigen density.
    if kind == _DIRECT_KIND:
        if not observation.crc_specific:
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if not observation.is_malignant_attributed:
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if (
            observation.is_protein_layer
            and observation.assay_method.strip()
            and observation.is_measurement_qualified
            and observation.is_context_qualified
            and observation.surface_context_class in _DIRECT_CONTEXT_CLASSES
        ):
            return _admit(
                observation,
                rung="DIRECT",
                implication=density_implication(observation),
                qualifying_direct=True,
            )
        # quantitative, malignant, CRC -- but a missing factual assay_method, or
        # the closed validation predicate / context adequacy is not QUALIFIED, or
        # the surface_context_class is not a DIRECT class: it does not reach
        # DIRECT (assay_method non-empty -- still NOT a closed assay whitelist).
        return _admit(observation, rung="", implication="CONTEXTUAL")

    return _reject(observation, "matches no frozen TGT-04 Evidence-Ladder rung")
