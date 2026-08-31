"""Place each normalized persistence observation into a FROZEN TGT-03
Evidence-Ladder rung and give it a Module-owned Gate-relative
persistence-implication reading (E9 item 05 / 06, E10-3).

Verbatim mapping -- E10 has no discretion:

  REFRACTORY_OR_PRIOR_TREATED_PROTEIN / METASTATIC_LESION_PROTEIN /
  PAIRED_PRE_POST_PROTEIN, CRC-specific, MALIGNANT-attributed,
      molecular_layer includes PROTEIN
      AND protein_measurement_validation_status == QUALIFIED + auditable basis
      AND context_adequacy_status == QUALIFIED + clinical_context_basis + basis
      AND clinical_context matches the observation kind
        -> rung DIRECT, qualifying_for_direct
           implication per persistence_pattern (see below)
      (assay_method is an OPEN factual type -- there is NO closed assay
       whitelist; a reliable protein method is not auto-downgraded, but it still
       needs protein_measurement_validation_status == QUALIFIED to drive DIRECT.)

  TREATED_METASTATIC_TRANSCRIPT, CRC-specific, MALIGNANT-attributed
  or RESISTANCE_MODEL, CRC-specific (well-validated resistance context)
        -> rung INDIRECT_STRONG, qualifying_for_indirect (never DIRECT; a
           resistance model stays INDIRECT_STRONG even if it measures protein --
           the ceiling is limited by the CONTEXT, not the measurement layer)
           implication per persistence_pattern

  TREATMENT_NAIVE_PRIMARY / DIFFERENT_TUMOR_TYPE  -> rung WEAK, CONTEXTUAL
                                                    (hypothesis / context only;
                                                     never above WEAK, never a
                                                     persistence claim, never a
                                                     TGT-02 baseline-coverage
                                                     substitution)
  SEARCH_COMPLETION_AUDIT               -> rung "" , CONTEXTUAL (a neutral fact)

Pattern -> implication (strict; the Module never parses basis prose):
  RETAINED                                        -> SUPPORTS_PERSISTENCE
  NEAR_LOSS_OR_MARKED_LOSS                        -> OPPOSES_PERSISTENCE
  TRANSIENT_OR_MINOR_DOWNREGULATION + PRESENT     -> SUPPORTS_PERSISTENCE
  TRANSIENT_OR_MINOR_DOWNREGULATION + UNRESOLVED  -> CONTEXTUAL
  MIXED_OR_UNRESOLVED                             -> CONTEXTUAL

Hard locks:
  * transcript / a resistance model never reaches DIRECT; protein without a
    QUALIFIED protein_measurement_validation_status never reaches DIRECT;
    protein without malignant-cell attribution never reaches DIRECT.
  * a non-CRC / non-malignant / unresolved-context protein observation is
    CONTEXTUAL and does NOT discharge TGT-03 (it is not a HARD failure).
  * a single observation is NEVER a Direction. This function only classifies a
    rung and a direction-SUPPORTING reading; ``aggregate`` produces the proposed
    Direction x Strength over a completed audited landscape.
"""

from __future__ import annotations

from .contracts import (
    ClassifiedPersistenceObservation,
    NormalizedPersistenceObservation,
    pattern_to_implication,
)

_CLINICAL_PROTEIN_KINDS = (
    "REFRACTORY_OR_PRIOR_TREATED_PROTEIN",
    "METASTATIC_LESION_PROTEIN",
    "PAIRED_PRE_POST_PROTEIN",
)
_KIND_TO_CONTEXT = {
    "REFRACTORY_OR_PRIOR_TREATED_PROTEIN": "REFRACTORY_OR_PRIOR_TREATED",
    "METASTATIC_LESION_PROTEIN": "METASTATIC_CRC",
    "PAIRED_PRE_POST_PROTEIN": "PAIRED_PRE_POST",
    # INDIRECT_STRONG kinds -- the treatment / metastasis context must be
    # explicitly qualified too (E10 review round 1, blocker 1).
    "TREATED_METASTATIC_TRANSCRIPT": "METASTATIC_CRC",
    "RESISTANCE_MODEL": "RESISTANCE_MODEL",
}


def _reject(
    observation: NormalizedPersistenceObservation, reason: str, *, severity: str = "SOFT"
) -> ClassifiedPersistenceObservation:
    return ClassifiedPersistenceObservation(
        observation=observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        persistence_implication="",
        qualifying_for_direct=False,
        qualifying_for_indirect=False,
    )


def _admit(
    observation: NormalizedPersistenceObservation,
    *,
    rung: str,
    implication: str,
    qualifying_direct: bool = False,
    qualifying_indirect: bool = False,
) -> ClassifiedPersistenceObservation:
    return ClassifiedPersistenceObservation(
        observation=observation,
        admissible=True,
        rejection_reason="",
        rejection_severity="",
        evidence_rung=rung,
        persistence_implication=implication,
        qualifying_for_direct=qualifying_direct,
        qualifying_for_indirect=qualifying_indirect,
    )


def classify_observation(
    observation: NormalizedPersistenceObservation, *, canonical_target_identity: str
) -> ClassifiedPersistenceObservation:
    """One observation -> one ClassifiedPersistenceObservation. Deterministic and
    single-valued."""

    # 1. an unresolved discovery / index lead establishes nothing.
    if not observation.primary_or_repository_source_resolved:
        return _reject(
            observation,
            "the observation is not resolved to a primary / repository source; a "
            "discovery or search-index lead does not establish a persistence fact",
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

    # 4. TREATMENT_NAIVE_PRIMARY / DIFFERENT_TUMOR_TYPE -- WEAK context only.
    #    A pretty protein measurement here still stays WEAK -- no smuggling a
    #    TGT-02 baseline-coverage read in as persistence.
    if kind in ("TREATMENT_NAIVE_PRIMARY", "DIFFERENT_TUMOR_TYPE"):
        return _admit(observation, rung="WEAK", implication="CONTEXTUAL")

    implication = pattern_to_implication(observation)

    # 5. INDIRECT_STRONG kinds -- treated / metastatic transcript, resistance model.
    if kind in ("TREATED_METASTATIC_TRANSCRIPT", "RESISTANCE_MODEL"):
        if not observation.crc_specific:
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if kind == "TREATED_METASTATIC_TRANSCRIPT" and not observation.is_malignant_attributed:
            # a transcript signal with the malignant compartment unresolved is
            # contextual -- it does not discharge TGT-03.
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if observation.persistence_pattern == "":
            return _admit(observation, rung="", implication="CONTEXTUAL")
        # the treatment / metastasis context must be EXPLICITLY qualified -- a
        # bare crc_specific transcript / model signal is not persistence
        # (E10 review round 1, blocker 1).
        if (
            observation.clinical_context != _KIND_TO_CONTEXT[kind]
            or not observation.is_context_qualified
        ):
            return _admit(observation, rung="", implication="CONTEXTUAL")
        return _admit(
            observation,
            rung="INDIRECT_STRONG",
            implication=implication,
            qualifying_indirect=True,
        )

    # 6. DIRECT kinds -- clinical-context protein.
    if kind in _CLINICAL_PROTEIN_KINDS:
        if not observation.crc_specific:
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if not observation.is_malignant_attributed:
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if observation.persistence_pattern == "":
            return _admit(observation, rung="", implication="CONTEXTUAL")
        if (
            observation.is_protein_layer
            and observation.assay_method.strip()
            and observation.is_protein_measurement_qualified
            and observation.is_context_qualified
            and observation.clinical_context == _KIND_TO_CONTEXT[kind]
        ):
            return _admit(
                observation,
                rung="DIRECT",
                implication=implication,
                qualifying_direct=True,
            )
        # protein, malignant, CRC -- but a missing factual assay_method, or the
        # closed validation predicate / context adequacy is not QUALIFIED, or the
        # clinical_context does not match the kind: it does not reach DIRECT
        # (assay_method non-empty per E10 review round 1, blocker 4 -- still NOT
        # a closed assay whitelist).
        return _admit(observation, rung="", implication="CONTEXTUAL")

    return _reject(observation, "matches no frozen TGT-03 Evidence-Ladder rung")
