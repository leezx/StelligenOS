"""Machine detection of a POTENTIAL sponsor-fatal pattern for TGT-08 (E6-5).

This produces a machine-generated review TRIGGER, never a fatal / commercial
CONCLUSION. It is deliberately mechanical -- no thresholds, no ownership-linkage
inference, no LLM / embedding judgement. "dominant", "well protected", "no
differentiation path" and "this sponsor should stop" are human / sponsor
governance calls the machine never makes.

``required`` is true iff, among the emitted / reused evidence that already
passed identity / provenance / classification, there is at least:

  * a competitive observation: exact same target + ADC modality + exact
    refractory-mCRC context + APPROVED or REGISTRATIONAL + primary-source
    verified (not a pipeline-database row) + classified OPPOSES_OPPORTUNITY;
  AND
  * a patent observation: exact same target + a live, relevant composition-level
    target-directed ADC claim + official / primary patent provenance +
    classified OPPOSES_OPPORTUNITY.

The two objects need not share an assignee -- ownership linkage is a human call.
"""

from __future__ import annotations

from .contracts import EmittedEvidence, SponsorReviewRecord

_SPONSOR_TRIGGER_STAGES = ("APPROVED", "REGISTRATIONAL")


def detect(
    emitted: list[EmittedEvidence], *, landscape_as_of: str, patent_scope: str
) -> SponsorReviewRecord:
    competitors = [
        e
        for e in emitted
        if e.classified.observation_kind == "COMPETITOR_PROGRAM"
        and e.classified.opportunity_implication == "OPPOSES_OPPORTUNITY"
        and e.classified.record.is_adc
        and e.classified.record.is_same_indication_context
        and e.classified.record.program_stage in _SPONSOR_TRIGGER_STAGES
        and e.classified.record.competitive_axis_primary_authority
    ]
    patents = [
        e
        for e in emitted
        if e.classified.observation_kind == "PATENT_CLAIM"
        and e.classified.opportunity_implication == "OPPOSES_OPPORTUNITY"
        and e.classified.record.patent_is_composition_level_adc_claim
        and e.classified.record.patent_is_live
        and e.classified.record.patent_axis_primary_authority
    ]
    if not competitors or not patents:
        return SponsorReviewRecord.none()

    evidence_ids = tuple(sorted({e.evidence_id for e in (*competitors, *patents)}))
    competitor_program_ids = tuple(
        sorted({e.classified.record.program_id for e in competitors})
    )
    patent_family_ids = tuple(
        sorted({e.classified.record.patent_family_id for e in patents})
    )
    return SponsorReviewRecord(
        required=True,
        status="POTENTIAL_SPONSOR_FATAL_PATTERN",
        evidence_ids=evidence_ids,
        competitor_program_ids=competitor_program_ids,
        patent_family_ids=patent_family_ids,
        landscape_as_of=landscape_as_of,
        patent_scope=patent_scope,
    )
