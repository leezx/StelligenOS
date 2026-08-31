"""Machine detection of a POTENTIAL fatal pattern for TGT-03 (E9 item 08 / 12, E10-6).

This produces a machine-generated review TRIGGER, never a fatal CONCLUSION. The
detection is mechanical and conservative -- it consumes the ALREADY-CLASSIFIED
evidence (no second "what counts as a qualified protein loss" engine). No
embeddings, no LLM semantic similarity, no numeric / percent-positive / H-score /
fold-change threshold. Whether the marked / near-loss qualification is justified
vs a transient / minor effect, whether the contexts are genuinely independent,
whether an apparent loss is an assay / platform artifact, whether a reported
reproducibility is scientifically convincing, whether meaningful target
availability is actually lost, and whether the pattern satisfies the GateSet
fatal policy are all human-review judgements the machine never makes.

``fatal_review.required`` is true iff, on a COMPLETED + audited clinical-
persistence landscape, there is at least one ELIGIBLE fatal contributor --

  * ``classified.evidence_rung == DIRECT``
  * ``classified.persistence_implication == OPPOSES_PERSISTENCE``
  * ``observation.persistence_pattern == NEAR_LOSS_OR_MARKED_LOSS``

(which by construction inherits protein-level + a QUALIFIED
protein_measurement_validation_status + CRC + a QUALIFIED context adequacy +
malignant-cell attribution + an auditable persistence_pattern_basis) --

and reproducibility is established by EITHER route:

  Route A -- one eligible contributor carries ``reproducibility_status ==
             QUALIFIED`` AND a non-empty ``reproducibility_basis``. The basis
             text is NEVER parsed -- QUALIFIED is the upstream qualification.
  Route B -- eligible contributors span AT LEAST TWO independent qualified
             persistence-context identities. It is NOT ">= 3" and NOT "> 2".
             Whether the contexts are genuinely independent stays human-only.
"""

from __future__ import annotations

from .completion import ClinicalPersistenceCompletion
from .contracts import EmittedEvidence, FatalReviewRecord


def detect(
    emitted: list[EmittedEvidence],
    completion: ClinicalPersistenceCompletion,
    *,
    landscape_as_of: str,
    persistence_search_scope: str,
) -> FatalReviewRecord:
    # A reproducible-loss fatal pattern exists ONLY over a completed, audited
    # clinical-persistence landscape (E9 item 08 / 16). An incomplete landscape
    # is a legitimate INCONCLUSIVE / UNKNOWN -- there is no fatal trigger yet, and
    # a premature raw trigger must NOT turn that accepted UNKNOWN into a rejected
    # run.
    if not completion.landscape_complete:
        return FatalReviewRecord.none()

    contributors = [
        e
        for e in emitted
        if e.classified.admissible
        and e.classified.evidence_rung == "DIRECT"
        and e.classified.persistence_implication == "OPPOSES_PERSISTENCE"
        and e.observation.persistence_pattern == "NEAR_LOSS_OR_MARKED_LOSS"
    ]
    if not contributors:
        return FatalReviewRecord.none()

    route_a = [e for e in contributors if e.observation.is_reproducibility_qualified]

    context_ids: list[str] = []
    for e in contributors:
        for cid in e.observation.persistence_context_identities:
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
        persistence_context_ids=tuple(sorted(context_ids)),
        persistence_class=tuple(
            sorted({e.observation.persistence_pattern for e in contributors})
        ),
        context_qualification_basis_refs=tuple(
            sorted(
                {e.observation.clinical_context_basis for e in contributors}
                | {e.observation.context_adequacy_basis for e in contributors}
            )
        ),
        persistence_pattern_basis_refs=tuple(
            sorted({e.observation.persistence_pattern_basis for e in contributors})
        ),
        reproducibility_basis_refs=reproducibility_basis_refs,
        landscape_as_of=landscape_as_of,
        persistence_search_scope=persistence_search_scope,
    )
