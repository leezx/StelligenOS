"""Machine detection of a POTENTIAL fatal pattern for TGT-06 (E13 item 08 / 12, E14-6).

This produces a machine-generated review TRIGGER, never a fatal CONCLUSION. The
detection is mechanical and conservative -- it consumes the ALREADY-CLASSIFIED
evidence (E14-6 tightening 2: no second "what counts as a qualified
productive-internalization failure" engine). No embeddings, no LLM semantic
similarity, no internalization-rate / half-life / percent-internalized /
lysosomal-colocalization-coefficient threshold, no invented ADC-effective
internalization range. Whether the failing antibody / epitope configurations are
genuinely independent, whether "fails productive internalization or trafficking"
is justified vs assay sensitivity, whether an apparent failure is an epitope /
assay artifact, whether the disease-relevant model is representative, whether a
reported reproducibility is convincing, and whether the surface-static pattern
satisfies the GateSet fatal policy are all human-review judgements the machine
never makes.

``fatal_review.required`` is true iff, on a COMPLETED + audited
internalization-evidence landscape:

  * GLOBAL PRECONDITION (HARD lock) -- NO qualifying productive DIRECT
    configuration exists. Any single qualifying productive DIRECT observation
    CANCELS the target-wide surface-static machine trigger.
  * there is at least one ELIGIBLE contributor -- a classified DIRECT-quality
    productive-internalization / trafficking FAILURE observation
    (``classified.qualifying_direct_failure``), observation_kind in
    {ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING,
    ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY, TRAFFICKING_OR_RECYCLING_ONLY}.
    By construction it inherits a qualified disease-relevant context (a QUALIFIED
    WELL_MATCHED_CRC_MODEL context IS eligible here, unlike TGT-04), a QUALIFIED
    assay_validation_status + a non-empty assay_method, internalization_outcome ==
    FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING and a SINGLE / IDENTIFIED_MULTI
    configuration identity -- these are classifier authority, NOT re-judged here.
  * multiple independent configurations are established by EITHER route:
      Route A -- ONE contributor is an IDENTIFIED_MULTI observation whose
                 configuration_identity_projection set has size >= 2 AND
                 ``reproducibility_status == QUALIFIED`` + a non-empty
                 ``reproducibility_basis``. The basis text is NEVER parsed.
      Route B -- AT LEAST TWO DISTINCT eligible failure OBSERVATIONS AND the union
                 of their configuration_identity_projection sets has size >= 2. A
                 SINGLE IDENTIFIED_MULTI observation, regardless of projection
                 cardinality, does NOT satisfy Route B. It is NOT ">= 3" and NOT
                 "> 2".

An ordinary Gate NEGATIVE / DIRECT scientific assessment is NOT a machine
POTENTIAL_FATAL_PATTERN: a single IDENTIFIED_MULTI {A, B} failure observation
still projects to two failure configuration identities and may support
NEGATIVE / DIRECT, but it satisfies neither route here without
reproducibility_status == QUALIFIED.
"""

from __future__ import annotations

from .completion import InternalizationEvidenceCompletion
from .contracts import EmittedEvidence, FatalReviewRecord

_FAILS = "FAILS_PRODUCTIVE_INTERNALIZATION_OR_TRAFFICKING"
_ELIGIBLE_KINDS = (
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_TRAFFICKING",
    "ANTIBODY_CONFIGURATION_INTERNALIZATION_ONLY",
    "TRAFFICKING_OR_RECYCLING_ONLY",
)


def detect(
    emitted: list[EmittedEvidence],
    completion: InternalizationEvidenceCompletion,
    *,
    landscape_as_of: str,
    internalization_search_scope: str,
) -> FatalReviewRecord:
    # A multiple-independent-configuration surface-static fatal pattern exists
    # ONLY over a completed, audited internalization-evidence landscape (E13 item
    # 08 / 16). An incomplete landscape is a legitimate INCONCLUSIVE / UNKNOWN --
    # there is no fatal trigger yet.
    if not completion.landscape_complete:
        return FatalReviewRecord.none()

    # --- GLOBAL PRECONDITION (HARD lock): any qualifying productive DIRECT
    #     configuration CANCELS the trigger.
    if any(
        e.classified.admissible and e.classified.qualifying_direct_productive
        for e in emitted
    ):
        return FatalReviewRecord.none()

    contributors = [
        e
        for e in emitted
        if e.classified.admissible
        and e.classified.qualifying_direct_failure
        and e.observation.observation_kind in _ELIGIBLE_KINDS
    ]
    if not contributors:
        return FatalReviewRecord.none()

    # --- Route A: ONE IDENTIFIED_MULTI contributor, projection size >= 2,
    #     reproducibility QUALIFIED + auditable basis.
    route_a = [
        e
        for e in contributors
        if e.observation.configuration_identity_state == "IDENTIFIED_MULTI"
        and len(e.configuration_identities) >= 2
        and e.observation.is_reproducibility_qualified
    ]

    # --- Route B: >= 2 DISTINCT eligible failure observations AND the union of
    #     their projected configuration identities has size >= 2.
    union_ids: set[str] = set()
    for e in contributors:
        union_ids |= set(e.configuration_identities)
    route_b = len(contributors) >= 2 and len(union_ids) >= 2

    if not route_a and not route_b:
        return FatalReviewRecord.none()

    reproducibility_basis_refs = tuple(
        sorted({e.observation.reproducibility_basis for e in route_a})
    )
    return FatalReviewRecord(
        required=True,
        status="POTENTIAL_FATAL_PATTERN",
        evidence_ids=tuple(e.evidence_id for e in contributors),
        configuration_ids=tuple(sorted(union_ids)),
        internalization_outcome_class=(_FAILS,),
        context_qualification_basis_refs=tuple(
            sorted(
                {e.observation.surface_context_basis for e in contributors}
                | {e.observation.context_adequacy_basis for e in contributors}
            )
        ),
        assay_validation_basis_refs=tuple(
            sorted({e.observation.assay_validation_basis for e in contributors})
        ),
        reproducibility_basis_refs=reproducibility_basis_refs,
        landscape_as_of=landscape_as_of,
        internalization_search_scope=internalization_search_scope,
    )
