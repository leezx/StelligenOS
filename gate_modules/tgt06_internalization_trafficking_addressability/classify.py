"""Place each normalized internalization observation into a FROZEN TGT-06
Evidence-Ladder rung and give it a Module-owned Gate-relative
addressability-implication reading (E13 item 05 / 06, E14-3).

This is the SINGLE classifier authority (E14-3 tightening 2). Every DIRECT-quality
FAILURE -- whether it arrives as an
ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING failure, an
ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY failure, or a
TRAFFICKING_OR_RECYCLING_ONLY failure -- is normalised here to
``evidence_rung == DIRECT`` + ``addressability_implication ==
OPPOSES_ADDRESSABILITY``. ``aggregate`` and ``fatal_review`` consume the
classified result; they never re-run an assay / context qualification engine.

There is NO generic "missed the DIRECT gate -> INDIRECT_STRONG" fallback
(E14 review round-1 blocker 1): a positive INDIRECT_STRONG rung is kind / context
/ outcome specific. A disease-relevant PRODUCTIVE observation whose assay /
context qualification is NOT_ESTABLISHED is CONTEXTUAL, non-qualifying -- it is
NOT auto-promoted to INDIRECT_STRONG.

Verbatim mapping -- E14 has no discretion:

  ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING (the integrated kind)
    * config resolved (SINGLE / IDENTIFIED_MULTI) AND disease-relevant qualified
      context AND assay_validation_status == QUALIFIED + a non-empty factual
      assay_method:
        - internalization_outcome == PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY
              -> rung DIRECT, SUPPORTS_ADDRESSABILITY, qualifying_direct_productive
        - internalization_outcome == FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING
              -> rung DIRECT, OPPOSES_ADDRESSABILITY, qualifying_direct_failure
        - internalization_outcome == INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED
              -> rung INDIRECT_STRONG, SUPPORTS_ADDRESSABILITY, qualifying_indirect
                 (lysosomal delivery not confirmed -- NEVER DIRECT)
        - internalization_outcome MIXED_OR_UNRESOLVED / NOT_ESTABLISHED
              -> rung "" , CONTEXTUAL (nondirectional)
    * integrated but the DIRECT rung predicates are NOT satisfied (NON_CRC
      context, or a disease-relevant context whose assay / context qualification
      is NOT_ESTABLISHED):
        - DELIVERY_UNRESOLVED -> rung INDIRECT_STRONG, SUPPORTS_ADDRESSABILITY, qualifying_indirect (its frozen lower ceiling)
        - PRODUCTIVE + NON_CRC_CONTEXT -> rung INDIRECT_STRONG, SUPPORTS_ADDRESSABILITY, qualifying_indirect
        - PRODUCTIVE + disease-relevant but assay / context NOT_ESTABLISHED -> rung "" , CONTEXTUAL, non-qualifying
        - FAILS / MIXED / NOT_ESTABLISHED -> rung "" , CONTEXTUAL
    * a DIRECT-quality-shaped observation in the IDENTITY_NOT_DISCLOSED state can
      no longer reach classify -- the contract constructor rejects a
      disease-relevant / unresolved internalization-family observation that does
      not disclose its configuration (E14 review round-1 blocker 3)

  ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY
    * config resolved AND disease-relevant AND assay QUALIFIED AND
      internalization_outcome == FAILS
        -> rung DIRECT, OPPOSES_ADDRESSABILITY, qualifying_direct_failure (branch b)
    * internalization_outcome == INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED
        -> rung INDIRECT_STRONG, SUPPORTS_ADDRESSABILITY, qualifying_indirect
    * (PRODUCTIVE is a typed-fact incoherence rejected by the contract constructor)
    * else -> rung "" , CONTEXTUAL

  TRAFFICKING_OR_RECYCLING_ONLY -- ASYMMETRIC authority
    * NEGATIVE direction: config resolved AND disease-relevant AND assay QUALIFIED
      AND internalization_outcome == FAILS
        -> rung DIRECT, OPPOSES_ADDRESSABILITY, qualifying_direct_failure (branch b)
    * POSITIVE direction: internalization_outcome == PRODUCTIVE / DELIVERY_UNRESOLVED
        -> rung INDIRECT_STRONG, SUPPORTS_ADDRESSABILITY, qualifying_indirect
           (at most INDIRECT_STRONG -- it can NEVER synthesize a positive DIRECT)
    * else -> rung "" , CONTEXTUAL

  CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY / SAME_TARGET_ADC_DELIVERY_PRECEDENT
        -> rung INDIRECT_STRONG, SUPPORTS_ADDRESSABILITY, qualifying_indirect
           (a configuration identity is NOT required; the frozen ladder does not
            demand one -- never rejected for lacking one)

  RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE / SURFACE_LOCALIZATION_ONLY_INFERENCE
        -> rung WEAK, CONTEXTUAL (hypothesis only; never above WEAK)

  SEARCH_COMPLETION_AUDIT
        -> rung "" , CONTEXTUAL (a neutral audited-search fact)

Hard locks:
  * a single observation is NEVER a Direction. This function classifies a rung and
    a direction-SUPPORTING / OPPOSING reading; ``aggregate`` produces the proposed
    Direction x Strength over a completed audited landscape.
  * DIRECT is NEVER synthesized across observations -- a productive DIRECT
    contributor is ALWAYS a single integrated
    ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING observation whose
    internalization_outcome is PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY.
"""

from __future__ import annotations

from .contracts import (
    ClassifiedInternalizationObservation,
    NormalizedInternalizationObservation,
)

_INTEGRATED_KIND = "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING"
_DIRECT_QUALITY_FAILURE_KINDS = (
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
    "TRAFFICKING_OR_RECYCLING_ONLY",
)
_INDIRECT_STRONG_KINDS = (
    "CONSTITUTIVE_ENDOCYTOSIS_OR_RECEPTOR_BIOLOGY",
    "SAME_TARGET_ADC_DELIVERY_PRECEDENT",
)
_WEAK_KINDS = (
    "RECEPTOR_FAMILY_MEMBERSHIP_INFERENCE",
    "SURFACE_LOCALIZATION_ONLY_INFERENCE",
)
_PRODUCTIVE = "PRODUCTIVE_INTERNALIZATION_WITH_LYSOSOMAL_DELIVERY"
_DELIVERY_UNRESOLVED = "INTERNALIZATION_OBSERVED_LYSOSOMAL_DELIVERY_UNRESOLVED"
_FAILS = "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"


def _reject(
    observation: NormalizedInternalizationObservation,
    reason: str,
    *,
    severity: str = "SOFT",
) -> ClassifiedInternalizationObservation:
    return ClassifiedInternalizationObservation(
        observation=observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        addressability_implication="",
        qualifying_direct_productive=False,
        qualifying_direct_failure=False,
        qualifying_indirect=False,
    )


def _admit(
    observation: NormalizedInternalizationObservation,
    *,
    rung: str,
    implication: str,
    qualifying_direct_productive: bool = False,
    qualifying_direct_failure: bool = False,
    qualifying_indirect: bool = False,
) -> ClassifiedInternalizationObservation:
    return ClassifiedInternalizationObservation(
        observation=observation,
        admissible=True,
        rejection_reason="",
        rejection_severity="",
        evidence_rung=rung,
        addressability_implication=implication,
        qualifying_direct_productive=qualifying_direct_productive,
        qualifying_direct_failure=qualifying_direct_failure,
        qualifying_indirect=qualifying_indirect,
    )


def _meets_direct_predicates_except_outcome(
    o: NormalizedInternalizationObservation,
) -> bool:
    """The shared DIRECT-quality predicate -- config resolved, disease-relevant
    qualified context, assay validation QUALIFIED + a non-empty factual
    assay_method. The specific ``internalization_outcome`` picks
    productive-vs-failure vs nondirectional."""

    return (
        o.is_configuration_resolved
        and o.is_disease_relevant_context
        and o.is_assay_qualified
    )


def classify_observation(
    observation: NormalizedInternalizationObservation,
    *,
    canonical_target_identity: str,
) -> ClassifiedInternalizationObservation:
    """One observation -> one ClassifiedInternalizationObservation. Deterministic
    and single-valued."""

    # 1. an unresolved discovery / index lead establishes nothing.
    if not observation.primary_or_repository_source_resolved:
        return _reject(
            observation,
            "the observation is not resolved to a primary / repository source; a "
            "discovery or search-index lead does not establish an internalization fact",
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

    # 5. INDIRECT_STRONG kinds -- constitutive endocytosis / internalizing-receptor
    #    biology / a genuinely successful same-target ADC functional-delivery
    #    precedent. A configuration identity is NOT required (frozen ladder).
    if kind in _INDIRECT_STRONG_KINDS:
        return _admit(
            observation,
            rung="INDIRECT_STRONG",
            implication="SUPPORTS_ADDRESSABILITY",
            qualifying_indirect=True,
        )

    # 6. internalization / trafficking family kinds -----------------------
    # NOTE: the configuration-identity allowed-kind boundary is enforced in the
    # contract constructor (a disease-relevant / unresolved family observation
    # without a disclosed configuration cannot be built), so classify never sees
    # a would-be DIRECT-quality observation in the IDENTITY_NOT_DISCLOSED state.
    # There is NO generic "missed DIRECT -> INDIRECT_STRONG" fallback (E14 review
    # round-1 blocker 1): a positive rung is kind / context / outcome specific.
    if kind in _DIRECT_QUALITY_FAILURE_KINDS:
        outcome = observation.internalization_outcome
        non_crc = observation.surface_context_class == "NON_CRC_CONTEXT"

        # --- the integrated kind: the only productive-DIRECT-capable path ----
        if kind == _INTEGRATED_KIND:
            if _meets_direct_predicates_except_outcome(observation):
                if outcome == _PRODUCTIVE:
                    return _admit(
                        observation,
                        rung="DIRECT",
                        implication="SUPPORTS_ADDRESSABILITY",
                        qualifying_direct_productive=True,
                    )
                if outcome == _FAILS:
                    return _admit(
                        observation,
                        rung="DIRECT",
                        implication="OPPOSES_ADDRESSABILITY",
                        qualifying_direct_failure=True,
                    )
                if outcome == _DELIVERY_UNRESOLVED:
                    # internalization observed, lysosomal delivery NOT confirmed
                    # -- positive support at the INDIRECT_STRONG ceiling only.
                    return _admit(
                        observation,
                        rung="INDIRECT_STRONG",
                        implication="SUPPORTS_ADDRESSABILITY",
                        qualifying_indirect=True,
                    )
                # MIXED_OR_UNRESOLVED / NOT_ESTABLISHED -- nondirectional.
                return _admit(observation, rung="", implication="CONTEXTUAL")
            # integrated, but the DIRECT rung predicates are NOT satisfied
            # (NON_CRC context, or a disease-relevant context whose assay /
            # context qualification is NOT_ESTABLISHED).
            if outcome == _DELIVERY_UNRESOLVED:
                # its frozen lower ceiling -- positive INDIRECT_STRONG support.
                return _admit(
                    observation,
                    rung="INDIRECT_STRONG",
                    implication="SUPPORTS_ADDRESSABILITY",
                    qualifying_indirect=True,
                )
            if outcome == _PRODUCTIVE and non_crc:
                # a NON_CRC antibody-induced internalization + lysosomal delivery
                # observation -- INDIRECT_STRONG, never DIRECT (context is not
                # disease-relevant).
                return _admit(
                    observation,
                    rung="INDIRECT_STRONG",
                    implication="SUPPORTS_ADDRESSABILITY",
                    qualifying_indirect=True,
                )
            # a disease-relevant PRODUCTIVE observation whose assay / context
            # qualification is NOT_ESTABLISHED, a FAILS outcome that did not meet
            # the DIRECT predicates, MIXED / NOT_ESTABLISHED -- CONTEXTUAL,
            # non-qualifying.
            return _admit(observation, rung="", implication="CONTEXTUAL")

        # --- the internalization-only / trafficking-only kinds --------------
        # DIRECT-quality FAILURE branch (b).
        if _meets_direct_predicates_except_outcome(observation) and outcome == _FAILS:
            return _admit(
                observation,
                rung="DIRECT",
                implication="OPPOSES_ADDRESSABILITY",
                qualifying_direct_failure=True,
            )
        # positive direction -- capped at INDIRECT_STRONG (a
        # TRAFFICKING_OR_RECYCLING_ONLY observation can NEVER synthesize a
        # positive DIRECT; an _ONLY observation with PRODUCTIVE is a
        # contract-constructor ValueError). A FAILS outcome is NEVER positive IS.
        if outcome in (_PRODUCTIVE, _DELIVERY_UNRESOLVED):
            return _admit(
                observation,
                rung="INDIRECT_STRONG",
                implication="SUPPORTS_ADDRESSABILITY",
                qualifying_indirect=True,
            )
        # a non-CRC FAILS observation, a disease-relevant FAILS that did not meet
        # the DIRECT predicates, MIXED / NOT_ESTABLISHED -- CONTEXTUAL.
        return _admit(observation, rung="", implication="CONTEXTUAL")

    return _reject(observation, "matches no frozen TGT-06 Evidence-Ladder rung")
