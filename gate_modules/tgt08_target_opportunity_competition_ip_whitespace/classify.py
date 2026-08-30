"""Place each normalized landscape record into a FROZEN TGT-08 evidence class
and give it a Module-owned Gate-relative opportunity implication (E6-4).

Verbatim mapping -- E6 has no discretion:

  COMPETITOR_PROGRAM (same target, same refractory-mCRC context)
    APPROVED / REGISTRATIONAL / ACTIVE_CLINICAL  -> OPPOSES_OPPORTUNITY
    DISCONTINUED / FAILED                         -> CONTEXTUAL (never automatically favorable)
    other indication / early / preclinical        -> CONTEXTUAL

  PATENT_CLAIM (same target)
    live + relevant composition-level ADC claim   -> OPPOSES_OPPORTUNITY (DIRECT-eligible axis)
    live + relevant target-level hit              -> OPPOSES_OPPORTUNITY (axis capped at INDIRECT_STRONG)
    expired / abandoned / cancelled / irrelevant  -> CONTEXTUAL (one expired patent is not whitespace)

  UNMET_NEED_CONTEXT      -> CONTEXTUAL (WEAK hypothesis only; never SUPPORTS on its own)
  SEARCH_COMPLETION_AUDIT -> CONTEXTUAL (a neutral search fact; the absence
                            SUPPORT is derived in aggregate from the completion
                            state + this audit EP, never from records == [])

An absence inference is NEVER produced here from an empty record set -- only
aggregate, and only from an attempted + coverage-complete + audited completion.
"""

from __future__ import annotations

from .contracts import ClassifiedOpportunity, NormalizedOpportunityRecord


def _reject(
    record: NormalizedOpportunityRecord, reason: str, *, severity: str = "SOFT"
) -> ClassifiedOpportunity:
    return ClassifiedOpportunity(
        record=record,
        admissible=False,
        rejection_reason=reason,
        rejection_severity=severity,
        evidence_class="",
        opportunity_implication="",
        qualifying_for_axis=False,
    )


def _admit(
    record: NormalizedOpportunityRecord,
    *,
    evidence_class: str,
    implication: str,
    qualifying: bool = False,
) -> ClassifiedOpportunity:
    return ClassifiedOpportunity(
        record=record,
        admissible=True,
        rejection_reason="",
        rejection_severity="",
        evidence_class=evidence_class,
        opportunity_implication=implication,
        qualifying_for_axis=qualifying,
    )


def classify_record(
    record: NormalizedOpportunityRecord, *, canonical_target_identity: str
) -> ClassifiedOpportunity:
    """One record -> one ClassifiedOpportunity. Deterministic and single-valued."""

    # 1. an unresolved discovery / index lead establishes nothing.
    if not record.primary_or_official_source_resolved:
        return _reject(
            record,
            "the record is not resolved to a primary / official source; a "
            "discovery or search-index lead does not establish a landscape fact",
        )

    # 2. candidate <-> record target identity must match (HARD misbinding).
    if record.target_identity.strip() != canonical_target_identity.strip():
        return _reject(
            record,
            f"record targets {record.target_identity!r}, not the candidate's "
            f"canonical target {canonical_target_identity!r} (evidence misbinding)",
            severity="HARD",
        )

    kind = record.observation_kind

    # 3. SEARCH_COMPLETION_AUDIT -- a neutral audited-search fact.
    if kind == "SEARCH_COMPLETION_AUDIT":
        return _admit(
            record,
            evidence_class=(
                f"audited {record.evidence_axis.lower()} landscape search-completion "
                "record (a neutral search fact; not a Gate direction)"
            ),
            implication="CONTEXTUAL",
        )

    # 4. UNMET_NEED_CONTEXT -- WEAK hypothesis only.
    if kind == "UNMET_NEED_CONTEXT":
        return _admit(
            record,
            evidence_class=(
                "indication-level unmet-need context (a WEAK hypothesis only; "
                "no target-specific competitive or IP read)"
            ),
            implication="CONTEXTUAL",
        )

    # 5. COMPETITOR_PROGRAM -- the frozen competitive mapping.
    if kind == "COMPETITOR_PROGRAM":
        if not record.is_same_indication_context:
            return _admit(
                record,
                evidence_class=(
                    "same-target targeted program outside the refractory-mCRC "
                    "context (context only)"
                ),
                implication="CONTEXTUAL",
            )
        if record.competitor_status_dead:
            return _admit(
                record,
                evidence_class=(
                    "discontinued / failed same-target program in refractory mCRC "
                    "(a competitor failing is NOT automatically a favorable "
                    "opportunity signal -- that would be a scientific inference)"
                ),
                implication="CONTEXTUAL",
            )
        if record.competitor_stage_opposes:
            return _admit(
                record,
                evidence_class=(
                    "approved / registrational / active-clinical same-target "
                    "targeted program in refractory mCRC"
                ),
                implication="OPPOSES_OPPORTUNITY",
                qualifying=True,
            )
        return _admit(
            record,
            evidence_class=(
                "early / preclinical same-target program in refractory mCRC "
                "(context only)"
            ),
            implication="CONTEXTUAL",
        )

    # 6. PATENT_CLAIM -- the frozen patent mapping.
    if kind == "PATENT_CLAIM":
        if record.claim_category == "IRRELEVANT":
            return _admit(
                record,
                evidence_class="patent claim of an irrelevant category (context only)",
                implication="CONTEXTUAL",
            )
        if record.patent_is_dead:
            return _admit(
                record,
                evidence_class=(
                    "expired / abandoned / cancelled patent for the target "
                    "(an expired patent is NOT whitespace)"
                ),
                implication="CONTEXTUAL",
            )
        if record.patent_is_live and record.patent_is_composition_level_adc_claim:
            return _admit(
                record,
                evidence_class=(
                    "live / relevant composition-level target-directed ADC "
                    "patent claim"
                ),
                implication="OPPOSES_OPPORTUNITY",
                qualifying=True,
            )
        if record.patent_is_live:
            return _admit(
                record,
                evidence_class=(
                    "live / relevant target-level (not composition-level) patent "
                    "hit for the target (patent axis capped at INDIRECT_STRONG)"
                ),
                implication="OPPOSES_OPPORTUNITY",
                qualifying=True,
            )
        return _admit(
            record,
            evidence_class="patent claim of undetermined live status (context only)",
            implication="CONTEXTUAL",
        )

    return _reject(record, "matches no frozen TGT-08 evidence class")
