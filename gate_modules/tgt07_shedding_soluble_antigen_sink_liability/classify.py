"""Place each normalized soluble-antigen observation into a FROZEN TGT-07
Evidence-Ladder rung and give it a Module-owned Gate-relative sink-liability
reading (E15 item 05 / 06; E16 tightenings 1 / 2 / 3).

This is the SINGLE scientific qualification authority (E16 tightening 3).
``aggregate.py`` and ``fatal_review.py`` consume the classified result; they
never re-run a same-target-match / attribution / TMDD-input-adequacy /
analysis-validation qualification engine.

DIRECT qualification is KIND-SPECIFIC (E16 tightening 1) -- there is NO generic
``kind in {clinical, TMDD} + sink context + analysis validation + method +
materiality outcome`` predicate.

  CLINICAL_ANTIGEN_SINK_PK_EFFECT -- clinical DIRECT-quality requires ALL of:
    * same_target_therapeutic_match_status == QUALIFIED + a non-empty
      same_target_therapeutic_match_basis + a non-empty same_target_therapeutic_ref
    * soluble_antigen_attribution_status == QUALIFIED + a non-empty basis
    * analysis_validation_status == QUALIFIED + a non-empty basis + a non-empty
      factual analysis_method
    * a non-empty sink_exposure_context_id + a non-empty basis
    then, by sink_materiality_outcome:
      - MATERIAL_*                    -> DIRECT, SUPPORTS_SINK_LIABILITY, material-sink
      - MIXED_OR_UNRESOLVED           -> DIRECT, CONTEXTUAL, mixed
      - NO_MATERIAL_SOLUBLE_SINK      -> rung "" , CONTEXTUAL, non-qualifying
                                        (clinical "no sink observed" is NEVER a
                                         canonical DIRECT negative)
      - NOT_ESTABLISHED              -> rung "" , CONTEXTUAL, non-qualifying
    * any missing qualifier          -> rung "" , CONTEXTUAL, non-qualifying

  SOLUBLE_ANTIGEN_TMDD_ANALYSIS -- TMDD DIRECT-quality requires ALL of:
    * tmdd_input_adequacy_status == QUALIFIED + a non-empty basis
    * analysis_validation_status == QUALIFIED + a non-empty basis + a non-empty
      factual analysis_method
    * a non-empty sink_exposure_context_id + a non-empty basis
    then, by sink_materiality_outcome:
      - MATERIAL_*                    -> DIRECT, SUPPORTS_SINK_LIABILITY, material-sink
      - NO_MATERIAL_SOLUBLE_SINK + exposure_scenario_class == INTENDED_ADC_EXPOSURE
                                     -> DIRECT, OPPOSES_SINK_LIABILITY, no-material-sink
                                        (the ONLY path to a canonical NEGATIVE / DIRECT)
      - NO_MATERIAL_SOLUBLE_SINK + SAME_TARGET_THERAPEUTIC_ANALOGUE / UNRESOLVED
                                     -> rung "" , CONTEXTUAL, non-qualifying
      - MIXED_OR_UNRESOLVED           -> DIRECT, CONTEXTUAL, mixed
      - NOT_ESTABLISHED              -> rung "" , CONTEXTUAL, non-qualifying
    * any missing qualifier          -> rung "" , CONTEXTUAL, non-qualifying

  SOLUBLE_ANTIGEN_QUANTITATION
    * cohort_class == CRC_PATIENT_SERUM AND
      circulating_soluble_target_status == QUANTIFIED_PRESENT
                                     -> INDIRECT_STRONG, SUPPORTS_SINK_LIABILITY
    * else (below detection / quantitation limit, healthy-donor-only, mixed /
      not-established)                -> rung "" , CONTEXTUAL, non-qualifying

  SHEDDASE_SUBSTRATE_STATUS / SECRETED_ISOFORM
                                     -> INDIRECT_STRONG, SUPPORTS_SINK_LIABILITY
       (the kind ITSELF is the "documented" / "validated" authority -- the
        provider never passes off a predicted / putative record as one of these)

  PREDICTED_CLEAVAGE_SITE_INFERENCE / FAMILY_ANALOGY_SHEDDING_INFERENCE
                                     -> WEAK, CONTEXTUAL (hypothesis only)

  SEARCH_COMPLETION_AUDIT            -> rung "" , CONTEXTUAL (a neutral audited-search fact)

Hard locks:
  * a single observation is NEVER a Direction. ``aggregate`` produces the proposed
    Direction x Strength over a completed audited landscape.
  * DIRECT is NEVER synthesized across observations -- a DIRECT contributor is
    ALWAYS a single upstream-qualified INTEGRATED CLINICAL_ANTIGEN_SINK_PK_EFFECT
    or SOLUBLE_ANTIGEN_TMDD_ANALYSIS observation.
  * ``reproducibility_status`` is optional factual metadata; it is NEVER a
    classification predicate (E16 tightening 5).
"""

from __future__ import annotations

from .contracts import (
    ClassifiedSolubleAntigenObservation,
    NormalizedSolubleAntigenObservation,
    sink_materiality_direction,
)

_MATERIAL_WITH_COMPROMISE = "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE"
_MATERIAL_WITHOUT_COMPROMISE = (
    "MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE"
)
_NO_MATERIAL_SINK = "NO_MATERIAL_SOLUBLE_SINK"
_MIXED_OR_UNRESOLVED = "MIXED_OR_UNRESOLVED"
_MATERIAL_OUTCOMES = (_MATERIAL_WITH_COMPROMISE, _MATERIAL_WITHOUT_COMPROMISE)

_INDIRECT_STRONG_KINDS = (
    "SOLUBLE_ANTIGEN_QUANTITATION",
    "SHEDDASE_SUBSTRATE_STATUS",
    "SECRETED_ISOFORM",
)
_WEAK_KINDS = (
    "PREDICTED_CLEAVAGE_SITE_INFERENCE",
    "FAMILY_ANALOGY_SHEDDING_INFERENCE",
)


def _reject(
    observation: NormalizedSolubleAntigenObservation,
    reason: str,
    *,
    severity: str = "SOFT",
) -> ClassifiedSolubleAntigenObservation:
    return ClassifiedSolubleAntigenObservation(
        observation=observation,
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


def _admit(
    observation: NormalizedSolubleAntigenObservation,
    *,
    rung: str,
    implication: str,
    qualifying_direct_material_sink: bool = False,
    qualifying_direct_no_material_sink: bool = False,
    qualifying_direct_mixed: bool = False,
    qualifying_indirect: bool = False,
) -> ClassifiedSolubleAntigenObservation:
    return ClassifiedSolubleAntigenObservation(
        observation=observation,
        admissible=True,
        rejection_reason="",
        rejection_severity="",
        evidence_rung=rung,
        sink_liability_implication=implication,
        qualifying_direct_material_sink=qualifying_direct_material_sink,
        qualifying_direct_no_material_sink=qualifying_direct_no_material_sink,
        qualifying_direct_mixed=qualifying_direct_mixed,
        qualifying_indirect=qualifying_indirect,
    )


def _contextual(
    observation: NormalizedSolubleAntigenObservation,
) -> ClassifiedSolubleAntigenObservation:
    return _admit(observation, rung="", implication="CONTEXTUAL")


def _classify_clinical(
    o: NormalizedSolubleAntigenObservation,
) -> ClassifiedSolubleAntigenObservation:
    """CLINICAL_ANTIGEN_SINK_PK_EFFECT -- kind-specific DIRECT authority (T1)."""

    qualified = (
        o.is_same_target_match_qualified
        and o.is_soluble_antigen_attribution_qualified
        and o.is_analysis_validation_qualified
        and o.has_sink_exposure_context
    )
    if not qualified:
        return _contextual(o)
    outcome = o.sink_materiality_outcome
    if outcome in _MATERIAL_OUTCOMES:
        return _admit(
            o,
            rung="DIRECT",
            implication="SUPPORTS_SINK_LIABILITY",
            qualifying_direct_material_sink=True,
        )
    if outcome == _MIXED_OR_UNRESOLVED:
        return _admit(
            o, rung="DIRECT", implication="CONTEXTUAL", qualifying_direct_mixed=True
        )
    # NO_MATERIAL_SOLUBLE_SINK / NOT_ESTABLISHED -- a clinical "no sink observed"
    # is NEVER a canonical DIRECT negative (E16 tightening 1 / 2).
    return _contextual(o)


def _classify_tmdd(
    o: NormalizedSolubleAntigenObservation,
) -> ClassifiedSolubleAntigenObservation:
    """SOLUBLE_ANTIGEN_TMDD_ANALYSIS -- kind-specific DIRECT authority (T1)."""

    qualified = (
        o.is_tmdd_input_adequate
        and o.is_analysis_validation_qualified
        and o.has_sink_exposure_context
    )
    if not qualified:
        return _contextual(o)
    outcome = o.sink_materiality_outcome
    if outcome in _MATERIAL_OUTCOMES:
        return _admit(
            o,
            rung="DIRECT",
            implication="SUPPORTS_SINK_LIABILITY",
            qualifying_direct_material_sink=True,
        )
    if outcome == _NO_MATERIAL_SINK:
        if o.exposure_scenario_class == "INTENDED_ADC_EXPOSURE":
            return _admit(
                o,
                rung="DIRECT",
                implication="OPPOSES_SINK_LIABILITY",
                qualifying_direct_no_material_sink=True,
            )
        # SAME_TARGET_THERAPEUTIC_ANALOGUE / UNRESOLVED -- CONTEXTUAL, not a
        # canonical DIRECT negative (E15 item 09 hard lock).
        return _contextual(o)
    if outcome == _MIXED_OR_UNRESOLVED:
        return _admit(
            o, rung="DIRECT", implication="CONTEXTUAL", qualifying_direct_mixed=True
        )
    # NOT_ESTABLISHED -- not DIRECT.
    return _contextual(o)


def classify_observation(
    observation: NormalizedSolubleAntigenObservation,
    *,
    canonical_target_identity: str,
) -> ClassifiedSolubleAntigenObservation:
    """One observation -> one ClassifiedSolubleAntigenObservation. Deterministic
    and single-valued."""

    # 1. an unresolved discovery / index lead establishes nothing.
    if not observation.primary_or_repository_source_resolved:
        return _reject(
            observation,
            "the observation is not resolved to a primary / repository source; a "
            "discovery or search-index lead does not establish a soluble-antigen fact",
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

    # 4. WEAK-only inference kinds -- hypothesis / context only.
    if kind in _WEAK_KINDS:
        return _admit(observation, rung="WEAK", implication="CONTEXTUAL")

    # 5. INDIRECT_STRONG kinds -----------------------------------------
    if kind == "SOLUBLE_ANTIGEN_QUANTITATION":
        if (
            observation.cohort_class == "CRC_PATIENT_SERUM"
            and observation.circulating_soluble_target_status == "QUANTIFIED_PRESENT"
        ):
            return _admit(
                observation,
                rung="INDIRECT_STRONG",
                implication="SUPPORTS_SINK_LIABILITY",
                qualifying_indirect=True,
            )
        # below detection / quantitation limit, healthy-donor-only, mixed /
        # not-established -- CONTEXTUAL factual, non-qualifying (E15 item 09 /
        # tightening 2).
        return _contextual(observation)
    if kind in ("SHEDDASE_SUBSTRATE_STATUS", "SECRETED_ISOFORM"):
        return _admit(
            observation,
            rung="INDIRECT_STRONG",
            implication="SUPPORTS_SINK_LIABILITY",
            qualifying_indirect=True,
        )

    # 6. DIRECT-authority kinds -- kind-specific qualification (T1) ---------
    if kind == "CLINICAL_ANTIGEN_SINK_PK_EFFECT":
        result = _classify_clinical(observation)
    elif kind == "SOLUBLE_ANTIGEN_TMDD_ANALYSIS":
        result = _classify_tmdd(observation)
    else:  # pragma: no cover - OBSERVATION_KIND_VALUES is exhausted above
        return _reject(observation, "matches no frozen TGT-07 Evidence-Ladder rung")

    # coherence: the frozen sink_materiality_direction_mapping must agree with the
    # classifier's directional reading for a qualifying DIRECT observation.
    if result.admissible and result.is_qualifying_direct:
        expected = sink_materiality_direction(observation)
        if result.sink_liability_implication != expected:  # pragma: no cover - guard
            return _reject(
                observation,
                "classifier directional reading disagrees with the frozen "
                "sink_materiality_direction_mapping",
                severity="HARD",
            )
    return result
