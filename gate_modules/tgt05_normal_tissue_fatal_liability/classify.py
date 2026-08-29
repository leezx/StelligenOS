"""Place each normalized record against the FROZEN TGT-05 Evidence Ladder and
the E4-2 three-way evidence-function split. Verbatim E4-3 mapping -- no rung is
invented, no "safety score" is produced, a validated protein NOT_DETECTED is
COVERAGE_CONTEXT (never a rung, never NEGATIVE).

Frozen ladder (src/contracts/crc_adc_target_gateset.yaml gate_contracts.TGT-05):

  DIRECT           clinical on-target / off-tumor toxicity attributable to this
                   target from an ADC against the same target
  INDIRECT_STRONG  same-target non-ADC clinical target-mediated toxicity;
                   validated human normal-tissue protein expression in vital
                   organs; translationally relevant same-target NHP toxicity
  WEAK             RNA-only normal-tissue expression; rodent-only data
"""

from __future__ import annotations

from .contracts import ClassifiedLiability, NormalizedLiabilityRecord


def _reject(
    record: NormalizedLiabilityRecord, reason: str, *, severity: str = "SOFT"
) -> ClassifiedLiability:
    return ClassifiedLiability(
        record=record,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_function=record.evidence_function,
        ladder_rung="",
        evidence_class="",
        attribution_stance="",
        covered_vital_organ="",
    )


def _admit(
    record: NormalizedLiabilityRecord,
    *,
    evidence_function: str,
    ladder_rung: str = "",
    evidence_class: str = "",
    attribution_stance: str = "",
    covered_vital_organ: str = "",
) -> ClassifiedLiability:
    return ClassifiedLiability(
        record=record,
        admissible=True,
        rejection_reason="",
        rejection_severity="",
        evidence_function=evidence_function,
        ladder_rung=ladder_rung,
        evidence_class=evidence_class,
        attribution_stance=attribution_stance,
        covered_vital_organ=covered_vital_organ,
    )


def classify_record(
    record: NormalizedLiabilityRecord, *, canonical_target_identity: str
) -> ClassifiedLiability:
    """One record -> one ClassifiedLiability. Deterministic and single-valued."""

    # 1. an unresolved / database-only lead is a retrieval lead (SOFT drop).
    if not record.primary_source_resolved:
        return _reject(
            record,
            "unresolved primary source: a database-only / discovery-index lead "
            "does not establish anything",
        )

    # 2. candidate <-> observation target identity must match (HARD misbinding).
    if record.target_identity.strip() != canonical_target_identity.strip():
        return _reject(
            record,
            f"record targets antigen {record.target_identity!r}, not the "
            f"candidate's canonical target {canonical_target_identity!r} "
            "(evidence misbinding)",
            severity="HARD",
        )

    fn = record.evidence_function

    # 3. COVERAGE_CONTEXT -- a validated human protein atlas NOT_DETECTED.
    if fn == "COVERAGE_CONTEXT":
        return _admit(
            record,
            evidence_function="COVERAGE_CONTEXT",
            covered_vital_organ=record.vital_organ_class,
            evidence_class=(
                "validated human normal-tissue protein atlas: no detectable "
                "target protein (coverage context -- proves the tissue was "
                "checked; NOT a liability rung and NOT safety)"
            ),
        )

    # 4. ATTRIBUTION_ADJUDICATION -- supports / refutes a *clinical toxicity's*
    #    target attribution. Never a NEGATIVE safety rung. Only a clinical
    #    toxicity observation can adjudicate a clinical toxicity's attribution --
    #    an atlas / expression / rodent observation cannot enter the
    #    attribution-conflict machinery via a shared liability_event_id.
    if fn == "ATTRIBUTION_ADJUDICATION":
        if record.observation_kind not in (
            "ADC_CLINICAL_TOXICITY",
            "NON_ADC_CLINICAL_TOXICITY",
        ):
            return _reject(
                record,
                "an ATTRIBUTION_ADJUDICATION record adjudicates a clinical "
                "toxicity's target attribution; its observation_kind must be "
                "ADC_CLINICAL_TOXICITY or NON_ADC_CLINICAL_TOXICITY",
            )
        if record.target_attribution_stance not in (
            "SUPPORTS_TARGET_ATTRIBUTION",
            "REFUTES_TARGET_ATTRIBUTION",
        ):
            return _reject(
                record,
                "an ATTRIBUTION_ADJUDICATION record must take a "
                "SUPPORTS_TARGET_ATTRIBUTION / REFUTES_TARGET_ATTRIBUTION stance",
            )
        return _admit(
            record,
            evidence_function="ATTRIBUTION_ADJUDICATION",
            attribution_stance=record.target_attribution_stance,
            evidence_class=(
                f"target-attribution adjudication ({record.target_attribution_stance}) "
                f"for liability event {record.liability_event_id}"
            ),
        )

    # 5. LIABILITY_RUNG_EVIDENCE -- the frozen TGT-05 ladder, verbatim.
    if record.observation_kind == "ADC_CLINICAL_TOXICITY":
        if not record.attribution_supported:
            return _reject(
                record,
                "an ADC clinical toxicity establishes a DIRECT rung only with "
                "SUPPORTS_TARGET_ATTRIBUTION; otherwise it belongs to "
                "ATTRIBUTION_ADJUDICATION",
            )
        return _admit(
            record,
            evidence_function="LIABILITY_RUNG_EVIDENCE",
            ladder_rung="DIRECT",
            attribution_stance="SUPPORTS_TARGET_ATTRIBUTION",
            evidence_class=(
                "clinical on-target / off-tumor toxicity attributable to this "
                "target from an ADC against the same target"
            ),
        )
    if record.observation_kind == "NON_ADC_CLINICAL_TOXICITY":
        if not record.attribution_supported:
            return _reject(
                record,
                "a non-ADC clinical toxicity establishes an INDIRECT_STRONG rung "
                "only with SUPPORTS_TARGET_ATTRIBUTION; otherwise it belongs to "
                "ATTRIBUTION_ADJUDICATION",
            )
        return _admit(
            record,
            evidence_function="LIABILITY_RUNG_EVIDENCE",
            ladder_rung="INDIRECT_STRONG",
            attribution_stance="SUPPORTS_TARGET_ATTRIBUTION",
            evidence_class=(
                "clinical on-target / off-tumor toxicity for the same target from "
                "a non-ADC targeted modality (CAR-T / T-cell engager / naked "
                "antibody)"
            ),
        )
    if record.is_validated_human_protein_detected:
        return _admit(
            record,
            evidence_function="LIABILITY_RUNG_EVIDENCE",
            ladder_rung="INDIRECT_STRONG",
            evidence_class=(
                "protein-level normal-tissue expression in vital organs from "
                "validated human atlases"
            ),
        )
    if record.is_nhp_translational_toxicity:
        # frozen INDIRECT_STRONG class = same-target *on-target* NHP toxicity
        # with translational relevance. Translational relevance alone does not
        # make it on-target: it needs a primary-source-supported target
        # attribution, exactly like a clinical toxicity rung.
        if not (
            record.attribution_supported
            and record.target_attribution_basis.strip()
        ):
            return _reject(
                record,
                "a translationally relevant NHP toxicity establishes an "
                "INDIRECT_STRONG rung only with SUPPORTS_TARGET_ATTRIBUTION and a "
                "disclosed target_attribution_basis; otherwise it may be "
                "off-target / construct-specific and is not the frozen on-target "
                "NHP evidence class",
            )
        return _admit(
            record,
            evidence_function="LIABILITY_RUNG_EVIDENCE",
            ladder_rung="INDIRECT_STRONG",
            attribution_stance="SUPPORTS_TARGET_ATTRIBUTION",
            evidence_class=(
                "same-target on-target toxicity in non-human primates with "
                "translational relevance"
            ),
        )
    if record.is_rna_normal_signal:
        return _admit(
            record,
            evidence_function="LIABILITY_RUNG_EVIDENCE",
            ladder_rung="WEAK",
            evidence_class=(
                "normal-tissue liability inferred only from RNA atlases without "
                "protein confirmation"
            ),
        )
    if record.is_rodent_only:
        return _admit(
            record,
            evidence_function="LIABILITY_RUNG_EVIDENCE",
            ladder_rung="WEAK",
            evidence_class="rodent-only normal-tissue or toxicity data",
        )

    return _reject(
        record,
        "matches no frozen TGT-05 liability evidence class (a validated protein "
        "NOT_DETECTED is COVERAGE_CONTEXT, not a rung; an NHP toxicity without "
        "translational relevance and an atlas without validation do not qualify)",
    )
