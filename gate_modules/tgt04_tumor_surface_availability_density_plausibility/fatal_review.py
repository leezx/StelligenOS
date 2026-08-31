"""Machine detection of a POTENTIAL fatal pattern for TGT-04 (E11 item 08 / 12, E12-6).

This produces a machine-generated review TRIGGER, never a fatal CONCLUSION. The
detection is mechanical and conservative -- it consumes the ALREADY-CLASSIFIED
evidence (no second "what counts as a qualified quantitative density" engine).
No embeddings, no LLM semantic similarity, no numeric / molecules-per-cell / ABC
/ percent-positive / H-score / context-count threshold, no invented ADC-effective
density range. Whether the "negligible / undetectable" qualification is justified
vs the assay's lower detection limit, whether the surface contexts are genuinely
independent, whether an apparent negligible signal is an assay / epitope-masking
artifact, whether a reported reproducibility is scientifically convincing,
whether there is truly no targetable surface antigen, and whether the pattern
satisfies the GateSet fatal policy are all human-review judgements the machine
never makes.

``fatal_review.required`` is true iff, on a COMPLETED + audited
surface-availability landscape, there is at least one ELIGIBLE fatal contributor --

  * ``classified.evidence_rung == DIRECT``
  * ``classified.density_implication == OPPOSES_DENSITY_PLAUSIBILITY``
  * ``observation.surface_antigen_level == NEGLIGIBLE_OR_UNDETECTABLE``
  * ``observation.surface_context_class == CRC_MALIGNANT_CELLS``

(which by construction inherits quantitative-density kind + a QUALIFIED
measurement_validation_status + a non-empty assay_method + CRC + a QUALIFIED
context adequacy + malignant-cell attribution + an auditable
surface_antigen_level_basis -- these are classifier authority, NOT re-judged
here) -- a WELL_MATCHED_CRC_MODEL observation is explicitly NOT eligible --

and reproducibility is established by EITHER route:

  Route A -- one eligible contributor carries ``reproducibility_status ==
             QUALIFIED`` AND a non-empty ``reproducibility_basis``. The basis
             text is NEVER parsed -- QUALIFIED is the upstream qualification.
  Route B -- eligible contributors span AT LEAST TWO independent qualified CRC
             MALIGNANT-CELL surface-context identities. It is NOT ">= 3" and NOT
             "> 2". 1 CRC + 1 model, or 2 model contexts, do NOT satisfy
             Route B. Whether the contexts are genuinely independent stays
             human-only.
"""

from __future__ import annotations

from .completion import SurfaceAvailabilityCompletion
from .contracts import EmittedEvidence, FatalReviewRecord


def detect(
    emitted: list[EmittedEvidence],
    completion: SurfaceAvailabilityCompletion,
    *,
    landscape_as_of: str,
    surface_search_scope: str,
) -> FatalReviewRecord:
    # A reproducible-negligible-antigen fatal pattern exists ONLY over a
    # completed, audited surface-availability landscape (E11 item 08 / 16). An
    # incomplete landscape is a legitimate INCONCLUSIVE / UNKNOWN -- there is no
    # fatal trigger yet, and a premature raw trigger must NOT turn that accepted
    # UNKNOWN into a rejected run.
    if not completion.landscape_complete:
        return FatalReviewRecord.none()

    contributors = [
        e
        for e in emitted
        if e.classified.admissible
        and e.classified.evidence_rung == "DIRECT"
        and e.classified.density_implication == "OPPOSES_DENSITY_PLAUSIBILITY"
        and e.observation.surface_antigen_level == "NEGLIGIBLE_OR_UNDETECTABLE"
        and e.observation.surface_context_class == "CRC_MALIGNANT_CELLS"
    ]
    if not contributors:
        return FatalReviewRecord.none()

    route_a = [e for e in contributors if e.observation.is_reproducibility_qualified]

    context_ids: list[str] = []
    for e in contributors:
        for cid in e.observation.surface_context_identities:
            if cid not in context_ids:
                context_ids.append(cid)
    route_b = len(context_ids) >= 2

    if not route_a and not route_b:
        return FatalReviewRecord.none()

    reproducibility_basis_refs = tuple(
        sorted({e.observation.reproducibility_basis for e in route_a})
    )
    return FatalReviewRecord(
        required=True,
        status="POTENTIAL_FATAL_PATTERN",
        evidence_ids=tuple(e.evidence_id for e in contributors),
        surface_context_ids=tuple(sorted(context_ids)),
        antigen_level_class=tuple(
            sorted({e.observation.surface_antigen_level for e in contributors})
        ),
        context_qualification_basis_refs=tuple(
            sorted(
                {e.observation.surface_context_basis for e in contributors}
                | {e.observation.context_adequacy_basis for e in contributors}
            )
        ),
        measurement_validation_basis_refs=tuple(
            sorted({e.observation.measurement_validation_basis for e in contributors})
        ),
        reproducibility_basis_refs=reproducibility_basis_refs,
        landscape_as_of=landscape_as_of,
        surface_search_scope=surface_search_scope,
    )
