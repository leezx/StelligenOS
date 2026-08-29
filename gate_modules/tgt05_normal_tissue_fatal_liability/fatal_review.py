"""Machine detection of a POTENTIAL fatal pattern for TGT-05 (E4-5).

This produces a machine-generated review TRIGGER, never a fatal CONCLUSION. The
detection is mechanical and conservative -- exact normalized-key comparison
only. No embeddings, no LLM semantic similarity, no adverse-event ontology
distance, no fuzzy match. "materially distinct constructs", "truly
target-mediated" and "biologically meaningful convergence" are human-review
judgements the machine never makes.

``fatal_review.required`` is true iff there are >= 2 same-target ADC clinical
toxicity observations from DISTINCT programs, each with an auditable construct
fingerprint, a disclosed target-attribution basis, and
SUPPORTS_TARGET_ATTRIBUTION, AND the normalized ``affected_tissue`` key and the
normalized ``toxicity_phenotype_key`` are an EXACT match across them. Two
publications of the same program count as one program.
"""

from __future__ import annotations

from collections import defaultdict

from .contracts import EmittedEvidence, FatalReviewRecord


def detect(emitted: list[EmittedEvidence]) -> FatalReviewRecord:
    candidates = [
        e
        for e in emitted
        if e.classified.record.observation_kind == "ADC_CLINICAL_TOXICITY"
        and e.classified.evidence_function == "LIABILITY_RUNG_EVIDENCE"
        and e.classified.record.attribution_supported
        and e.classified.record.construct_fingerprint.strip()
        and e.classified.record.target_attribution_basis.strip()
        and e.classified.record.affected_tissue.strip()
        and e.classified.record.toxicity_phenotype_key.strip()
    ]
    if len(candidates) < 2:
        return FatalReviewRecord.none()

    # group by EXACT (affected_tissue key, toxicity_phenotype_key)
    by_key: dict[tuple[str, str], list[EmittedEvidence]] = defaultdict(list)
    for e in candidates:
        r = e.classified.record
        by_key[(r.affected_tissue.strip(), r.toxicity_phenotype_key.strip())].append(e)

    for (tissue, phenotype), group in sorted(by_key.items()):
        programs = {e.classified.record.program_id for e in group}
        if len(programs) < 2:
            continue
        return FatalReviewRecord(
            required=True,
            status="POTENTIAL_FATAL_PATTERN",
            evidence_ids=tuple(e.evidence_id for e in group),
            program_ids=tuple(sorted(programs)),
            construct_fingerprints=tuple(
                sorted({e.classified.record.construct_fingerprint for e in group})
            ),
            affected_tissues=(tissue,),
            target_attribution_basis_refs=tuple(
                sorted({e.classified.record.target_attribution_basis for e in group})
            ),
        )
    return FatalReviewRecord.none()
