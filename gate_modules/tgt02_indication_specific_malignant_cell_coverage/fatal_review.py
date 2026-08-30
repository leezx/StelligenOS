"""Machine detection of a POTENTIAL fatal pattern for TGT-02 (E7 item 08 / 12, E8-6).

This produces a machine-generated review TRIGGER, never a fatal CONCLUSION. The
detection is mechanical and conservative -- exact field reads only. No
embeddings, no LLM semantic similarity, no numeric / percent-positive / H-score
/ heterogeneity threshold. Whether a cohort's adequacy basis is convincing,
whether the cohorts are genuinely independent / non-overlapping, whether the
"rare and highly heterogeneous" characterisation is justified, whether assay /
platform differences explain the apparent convergence, and whether the pattern
satisfies the GateSet fatal policy are all human-review judgements the machine
never makes.

``fatal_review.required`` is true iff, on a COMPLETED + audited CRC coverage
landscape, there are DIRECT-class protein-cohort observations, each

  * classified OPPOSES_COVERAGE with expression_pattern in
    {ABSENT, RARE_HIGHLY_HETEROGENEOUS} and an auditable expression_pattern_basis,
  * with a QUALIFIED cohort adequacy status and an auditable cohort_adequacy_basis,

that together provide cross-cohort support -- AT LEAST TWO independent cohort
identities (distinct auditable cohort_ids), or one declared multi-cohort
analysis with at least two auditable cohort_ids. It is NOT "more than two" /
"> 2". A single negative cohort gives required = false; two observations from
the same cohort are not cross-cohort.
"""

from __future__ import annotations

from .completion import CrcCohortCoverageCompletion
from .contracts import EmittedEvidence, FatalReviewRecord


def detect(
    emitted: list[EmittedEvidence],
    completion: CrcCohortCoverageCompletion,
    *,
    landscape_as_of: str,
    crc_coverage_search_scope: str,
) -> FatalReviewRecord:
    # A cross-cohort fatal pattern exists ONLY over a completed, audited CRC
    # coverage landscape (E7 item 08 / 16). An incomplete landscape is a
    # legitimate INCONCLUSIVE / UNKNOWN -- there is no fatal trigger yet, and a
    # premature raw trigger must NOT turn that accepted UNKNOWN into a rejected
    # run.
    if not completion.landscape_complete:
        return FatalReviewRecord.none()

    candidates = [
        e
        for e in emitted
        if e.classified.admissible
        and e.classified.qualifying_for_direct
        and e.classified.coverage_support == "OPPOSES_COVERAGE"
        and e.observation.observation_kind == "PROTEIN_COHORT"
        and e.observation.is_protein_layer
        and e.observation.is_malignant_attributed
        and e.observation.is_cohort_qualified
        and e.observation.cohort_adequacy_basis.strip()
        and e.observation.expression_pattern in ("ABSENT", "RARE_HIGHLY_HETEROGENEOUS")
        and e.observation.expression_pattern_basis
        and e.observation.expression_pattern_basis_detail.strip()
    ]
    if not candidates:
        return FatalReviewRecord.none()

    # cross-cohort support == at least two independent cohort identities (E7 item
    # 08 across_cohorts_is_plural_cohorts_logic_not_a_new_threshold; ChatGPT
    # AI审核方案 confirmed >= 2, explicitly NOT "> 2").
    cohort_ids: list[str] = []
    for e in candidates:
        for cid in e.observation.cohort_identities:
            if cid not in cohort_ids:
                cohort_ids.append(cid)
    if len(cohort_ids) < 2:
        return FatalReviewRecord.none()

    return FatalReviewRecord(
        required=True,
        status="POTENTIAL_FATAL_PATTERN",
        evidence_ids=tuple(e.evidence_id for e in candidates),
        cohort_ids=tuple(sorted(cohort_ids)),
        coverage_class=tuple(
            sorted({e.observation.expression_pattern for e in candidates})
        ),
        cohort_adequacy_basis_refs=tuple(
            sorted({e.observation.cohort_adequacy_basis for e in candidates})
        ),
        expression_pattern_basis_refs=tuple(
            sorted({e.observation.expression_pattern_basis_detail for e in candidates})
        ),
        landscape_as_of=landscape_as_of,
        crc_coverage_search_scope=crc_coverage_search_scope,
    )
