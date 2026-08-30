"""Place each normalized coverage observation into a FROZEN TGT-02 Evidence-Ladder
rung and give it a Module-owned Gate-relative coverage-support reading
(E7 item 05 / 06, E8-3).

Verbatim mapping -- E8 has no discretion:

  PROTEIN_COHORT, CRC-specific, MALIGNANT-attributed,
      validated protein assay (VALIDATED_IHC / QUANTITATIVE_PROTEOMICS /
      VALIDATED_MULTIPLEX_IF) AND a QUALIFIED cohort adequacy status
        -> rung DIRECT, qualifying_for_direct
           expression_pattern PRESENT_CONSISTENT      -> SUPPORTS_COVERAGE
           expression_pattern ABSENT / RARE_HIGHLY_HETEROGENEOUS -> OPPOSES_COVERAGE
           expression_pattern MIXED_OR_UNRESOLVED     -> CONTEXTUAL (nondirectional)

  MALIGNANT_SC_SPATIAL, CRC-specific, MALIGNANT-attributed, SC / SPATIAL assay
  or TMA_TRANSCRIPT_PROTEIN_CONCORDANCE, CRC-specific, MALIGNANT-attributed
        -> rung INDIRECT_STRONG, qualifying_for_indirect (never DIRECT; a TMA
           transcript+protein concordance stays INDIRECT_STRONG even at the BOTH
           molecular layer -- PR D froze it there)
           expression_pattern mapping as above

  BULK_CRC_RNA / PAN_CANCER_UNRESOLVED  -> rung WEAK, CONTEXTUAL (hypothesis only)
  MATCHED_NORMAL_TUMOR                  -> rung "" , CONTEXTUAL (contextualises CRC
                                          malignant-cell expression only; NEVER a
                                          therapeutic-index read -- that is TGT-05)
  SEARCH_COMPLETION_AUDIT               -> rung "" , CONTEXTUAL (a neutral search fact)

Hard locks:
  * transcript never reaches DIRECT; a generic / non-validated protein assay
    never reaches DIRECT; protein without malignant-cell attribution never
    reaches DIRECT.
  * stromal / immune / unresolved-compartment expression is NOT CRC malignant-cell
    expression -- it is a CONTEXTUAL observation and does NOT discharge TGT-02
    (it is not a HARD failure).
  * a single observation is NEVER a Direction. This function only classifies a
    rung and a direction-SUPPORTING reading; ``aggregate`` produces the proposed
    Direction x Strength over a completed audited landscape.
"""

from __future__ import annotations

from .contracts import ClassifiedCoverage, NormalizedCoverageObservation

_PATTERN_TO_SUPPORT: dict[str, str] = {
    "PRESENT_CONSISTENT": "SUPPORTS_COVERAGE",
    "ABSENT": "OPPOSES_COVERAGE",
    "RARE_HIGHLY_HETEROGENEOUS": "OPPOSES_COVERAGE",
    "MIXED_OR_UNRESOLVED": "CONTEXTUAL",
}
_RUNG_BEARING_KINDS = (
    "PROTEIN_COHORT",
    "MALIGNANT_SC_SPATIAL",
    "TMA_TRANSCRIPT_PROTEIN_CONCORDANCE",
)


def _reject(
    observation: NormalizedCoverageObservation, reason: str, *, severity: str = "SOFT"
) -> ClassifiedCoverage:
    return ClassifiedCoverage(
        observation=observation,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_rung="",
        coverage_support="",
        qualifying_for_direct=False,
        qualifying_for_indirect=False,
    )


def _admit(
    observation: NormalizedCoverageObservation,
    *,
    rung: str,
    support: str,
    qualifying_direct: bool = False,
    qualifying_indirect: bool = False,
) -> ClassifiedCoverage:
    return ClassifiedCoverage(
        observation=observation,
        admissible=True,
        rejection_reason="",
        rejection_severity="",
        evidence_rung=rung,
        coverage_support=support,
        qualifying_for_direct=qualifying_direct,
        qualifying_for_indirect=qualifying_indirect,
    )


def classify_observation(
    observation: NormalizedCoverageObservation, *, canonical_target_identity: str
) -> ClassifiedCoverage:
    """One observation -> one ClassifiedCoverage. Deterministic and single-valued."""

    # 1. an unresolved discovery / index lead establishes nothing.
    if not observation.primary_or_repository_source_resolved:
        return _reject(
            observation,
            "the observation is not resolved to a primary / repository source; a "
            "discovery or search-index lead does not establish a coverage fact",
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
        return _admit(
            observation,
            rung="",
            support="CONTEXTUAL",
        )

    # 4. MATCHED_NORMAL_TUMOR -- contextual only.
    if kind == "MATCHED_NORMAL_TUMOR":
        return _admit(observation, rung="", support="CONTEXTUAL")

    # 5. BULK_CRC_RNA / PAN_CANCER_UNRESOLVED -- WEAK hypothesis only.
    if kind in ("BULK_CRC_RNA", "PAN_CANCER_UNRESOLVED"):
        return _admit(observation, rung="WEAK", support="CONTEXTUAL")

    # 6. rung-bearing kinds -- compartment / CRC / attribution hard locks first.
    if kind in _RUNG_BEARING_KINDS:
        if not observation.crc_specific:
            return _admit(
                observation,
                rung="",
                support="CONTEXTUAL",
            )
        if not observation.is_malignant_attributed:
            # stroma / immune / unresolved compartment -- a contextual observation
            # that does NOT discharge TGT-02. Never a HARD failure.
            return _admit(observation, rung="", support="CONTEXTUAL")
        if observation.expression_pattern == "":
            return _admit(observation, rung="", support="CONTEXTUAL")

        support = _PATTERN_TO_SUPPORT[observation.expression_pattern]

        if kind == "PROTEIN_COHORT":
            if observation.is_validated_protein_assay and observation.is_cohort_qualified:
                return _admit(
                    observation,
                    rung="DIRECT",
                    support=support,
                    qualifying_direct=True,
                )
            # protein, malignant, CRC -- but not on a validated assay + qualified
            # cohort: it does not reach the DIRECT class (an adequately powered
            # CRC cohort measured with a validated protein assay).
            return _admit(observation, rung="", support="CONTEXTUAL")

        if kind == "MALIGNANT_SC_SPATIAL":
            if observation.is_sc_spatial_assay:
                return _admit(
                    observation,
                    rung="INDIRECT_STRONG",
                    support=support,
                    qualifying_indirect=True,
                )
            return _admit(observation, rung="", support="CONTEXTUAL")

        # TMA_TRANSCRIPT_PROTEIN_CONCORDANCE -- strictly INDIRECT_STRONG.
        return _admit(
            observation,
            rung="INDIRECT_STRONG",
            support=support,
            qualifying_indirect=True,
        )

    return _reject(observation, "matches no frozen TGT-02 Evidence-Ladder rung")
