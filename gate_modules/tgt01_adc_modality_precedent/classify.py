"""Place each normalized precedent record against the FROZEN TGT-01 Evidence
Ladder. No rung is invented; no admissible class is added.

Frozen ladder (src/contracts/crc_adc_target_gateset.yaml gate_contracts.TGT-01):

  DIRECT           approved / late-clinical (phase 2 or 3) ADC against the SAME
                   target antigen WITH disclosed clinical activity
  INDIRECT_STRONG  early-clinical (phase 1) ADC against the SAME target antigen
  WEAK             approved / clinical-stage ADC against an ADJACENT target in
                   the same lineage (class-level signal only);
                   preclinical-only ADC constructs against the target;
                   patents / company disclosures naming the target, no clinical data

Directness of an ADVERSE observation (a discontinued same-target program with a
disclosed target-mediated failure) inherits the same directness scale -- it does
NOT get a fourth ladder (E2-5): late-clinical human -> DIRECT, phase 1 ->
INDIRECT_STRONG, preclinical -> WEAK.
"""

from __future__ import annotations

from .contracts import (
    LATE_CLINICAL_STAGES,
    ClassifiedPrecedent,
    NormalizedPrecedentRecord,
)
from .ports import SourceRegistryPort

_CLINICAL_STAGES = frozenset({"APPROVED", "PHASE_3", "PHASE_2", "PHASE_1"})


def _directness_rung(stage: str) -> str:
    if stage in LATE_CLINICAL_STAGES:
        return "DIRECT"
    if stage == "PHASE_1":
        return "INDIRECT_STRONG"
    return "WEAK"  # PRECLINICAL / PATENT_OR_DISCLOSURE


def _reject(record: NormalizedPrecedentRecord, reason: str) -> ClassifiedPrecedent:
    return ClassifiedPrecedent(
        record=record,
        admissible=False,
        rejection_reason=reason,
        ladder_rung="",
        evidence_class="",
        direction_role="CONTEXTUAL",
        contributes_adverse_signal=False,
    )


def classify_record(
    record: NormalizedPrecedentRecord, *, source_registry: SourceRegistryPort
) -> ClassifiedPrecedent:
    """One record -> one ClassifiedPrecedent. Deterministic and single-valued."""

    # 1. An ADCdb-class / database-only lead that the provider has not resolved
    #    to a primary disclosure is a retrieval lead, never rung-establishing.
    if not record.primary_source_resolved:
        return _reject(
            record,
            "unresolved primary source: a database-only / discovery-index lead "
            "does not establish an Evidence Ladder rung",
        )

    # 2. The provenance source id must resolve in the upstream source registry.
    if not source_registry.is_registered_primary_source(record.source_id):
        return _reject(
            record,
            f"provenance.source_id {record.source_id} is not a registered "
            "primary source",
        )

    same_target = record.is_same_target
    stage = record.program_stage
    discontinued_target_mediated = record.is_target_mediated_failure

    # 3. Discontinued same-target program with a disclosed TARGET-MEDIATED failure
    #    -> adverse candidate (the aggregate decides if the >= 2-program pattern
    #    is met; a single one is never sufficient -- frozen item 08).
    if same_target and discontinued_target_mediated:
        return ClassifiedPrecedent(
            record=record,
            admissible=True,
            rejection_reason="",
            ladder_rung=_directness_rung(stage),
            evidence_class=(
                "discontinued same-target ADC program with a disclosed "
                "target-mediated / on-target failure"
            ),
            direction_role="ADVERSE_CANDIDATE",
            contributes_adverse_signal=True,
        )

    # 4. Discontinued (same or adjacent) without target attribution -> context
    #    only. A single product's failure driven by linker / payload / format is
    #    explicitly NOT sufficient to be an adverse signal (frozen item 08).
    if record.program_status == "DISCONTINUED":
        return ClassifiedPrecedent(
            record=record,
            admissible=True,
            rejection_reason="",
            ladder_rung=_directness_rung(stage),
            evidence_class=(
                "discontinued ADC program; failure not attributed to the target "
                "(construct-specific / non-target / undisclosed)"
            ),
            direction_role="CONTEXTUAL",
            contributes_adverse_signal=False,
        )

    # 5. Supporting precedent -- same target.
    if same_target:
        if stage in LATE_CLINICAL_STAGES:
            if not record.clinical_activity_disclosed:
                return _reject(
                    record,
                    "same-target late-clinical ADC without disclosed clinical "
                    "activity matches no frozen DIRECT / INDIRECT_STRONG "
                    "admissible class",
                )
            return ClassifiedPrecedent(
                record=record,
                admissible=True,
                rejection_reason="",
                ladder_rung="DIRECT",
                evidence_class=(
                    "approved / late-clinical (phase 2 or 3) ADC against the "
                    "same target antigen with disclosed clinical activity"
                ),
                direction_role="SUPPORTING",
                contributes_adverse_signal=False,
            )
        if stage == "PHASE_1":
            return ClassifiedPrecedent(
                record=record,
                admissible=True,
                rejection_reason="",
                ladder_rung="INDIRECT_STRONG",
                evidence_class="early-clinical (phase 1) ADC against the same target antigen",
                direction_role="SUPPORTING",
                contributes_adverse_signal=False,
            )
        if stage == "PRECLINICAL":
            return ClassifiedPrecedent(
                record=record,
                admissible=True,
                rejection_reason="",
                ladder_rung="WEAK",
                evidence_class="preclinical-only ADC constructs against the target",
                direction_role="SUPPORTING",
                contributes_adverse_signal=False,
            )
        # PATENT_OR_DISCLOSURE
        return ClassifiedPrecedent(
            record=record,
            admissible=True,
            rejection_reason="",
            ladder_rung="WEAK",
            evidence_class=(
                "patents or company disclosures naming the target with no clinical data"
            ),
            direction_role="SUPPORTING",
            contributes_adverse_signal=False,
        )

    # 6. Adjacent target -- only a clinical-stage adjacent ADC is a frozen WEAK
    #    class ("a class-level signal only"). Below clinical stage it matches no
    #    frozen admissible class.
    if stage in _CLINICAL_STAGES:
        return ClassifiedPrecedent(
            record=record,
            admissible=True,
            rejection_reason="",
            ladder_rung="WEAK",
            evidence_class=(
                "approved or clinical-stage ADC against a biologically adjacent "
                "target in the same lineage (class-level signal only; the success "
                "of an adjacent-target ADC does not de-risk this target)"
            ),
            direction_role="SUPPORTING",
            contributes_adverse_signal=False,
        )
    return _reject(
        record,
        "adjacent-target evidence below clinical stage matches no frozen TGT-01 "
        "admissible class",
    )
