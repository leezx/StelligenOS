"""Machine detection of a POTENTIAL fatal pattern for TGT-07 (E15 item 08 / 12;
E16 tightening 5).

This produces a machine-generated review TRIGGER, never a fatal CONCLUSION. The
detection is mechanical and conservative -- it does ONLY fatal-specific narrowing
over the ALREADY-CLASSIFIED evidence. It is NOT a second DIRECT qualification
engine: ``classify.py`` already decided whether an observation is a qualifying
DIRECT material-sink observation (same-target match / soluble-antigen attribution
/ TMDD input adequacy / analysis validation are classifier authority). This
detector never re-checks those and never semantic-parses ``claim`` or a basis to
decide "did the source really document a material compromise" -- that is what the
typed ``sink_materiality_outcome`` and ``exposure_scenario_class`` are for
(E16 tightening 5).

No embeddings, no LLM semantic similarity, no concentration / turnover / affinity
/ dose-exposure / sink-ratio threshold, no invented "material soluble-antigen sink
concentration" range.

``fatal_review.required`` is true iff, on a COMPLETED + audited
soluble-antigen-evidence landscape, there is at least one classified qualifying
DIRECT observation whose ``sink_materiality_outcome ==
MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE`` and that observation
satisfies EITHER admissible SOURCE PATH:

  * Clinical source path -- ``observation_kind == CLINICAL_ANTIGEN_SINK_PK_EFFECT``
    (its clinical qualification -- same-target match, soluble-antigen attribution,
    analysis validation -- is guaranteed by ``classify.qualifying_direct_material_sink``)
    AND ``documents_clinical_exposure_compromise``.
  * TMDD source path -- ``observation_kind == SOLUBLE_ANTIGEN_TMDD_ANALYSIS`` AND
    ``exposure_scenario_class == INTENDED_ADC_EXPOSURE`` (its TMDD qualification is
    guaranteed by the classifier) AND ``documents_clinical_exposure_compromise``.

ONE qualifying observation on EITHER path is sufficient. The two paths are NOT
combined and NOT a convergence pair; there is NO mandatory reproducibility
predicate; there is NO global cancellation precondition (a POSITIVE / DIRECT does
NOT clear the trigger). A
``MATERIAL_SOLUBLE_SINK_WITHOUT_ESTABLISHED_CLINICAL_EXPOSURE_COMPROMISE`` DIRECT
is POSITIVE / DIRECT but NONFATAL.
"""

from __future__ import annotations

from .completion import SolubleAntigenEvidenceCompletion
from .contracts import EmittedEvidence, FatalReviewRecord

_MATERIAL_WITH_COMPROMISE = "MATERIAL_SOLUBLE_SINK_WITH_CLINICAL_EXPOSURE_COMPROMISE"


def _fatal_source_path(e: EmittedEvidence) -> str:
    """Return "CLINICAL" / "TMDD" if this classified qualifying material-sink DIRECT
    observation satisfies a fatal source path, else ""."""

    o = e.observation
    if o.sink_materiality_outcome != _MATERIAL_WITH_COMPROMISE:
        return ""
    if not o.documents_clinical_exposure_compromise:
        return ""
    if o.observation_kind == "CLINICAL_ANTIGEN_SINK_PK_EFFECT":
        return "CLINICAL"
    if (
        o.observation_kind == "SOLUBLE_ANTIGEN_TMDD_ANALYSIS"
        and o.exposure_scenario_class == "INTENDED_ADC_EXPOSURE"
    ):
        return "TMDD"
    return ""


def detect(
    emitted: list[EmittedEvidence],
    completion: SolubleAntigenEvidenceCompletion,
    *,
    landscape_as_of: str,
    soluble_antigen_search_scope: str,
) -> FatalReviewRecord:
    # A potential-fatal signal exists ONLY over a completed, audited
    # soluble-antigen-evidence landscape (E15 item 08 / 16). An incomplete
    # landscape is a legitimate INCONCLUSIVE / UNKNOWN -- there is no fatal trigger
    # yet.
    if not completion.landscape_complete:
        return FatalReviewRecord.none()

    contributors: list[tuple[EmittedEvidence, str]] = []
    for e in emitted:
        if not (e.classified.admissible and e.classified.qualifying_direct_material_sink):
            continue
        path = _fatal_source_path(e)
        if path:
            contributors.append((e, path))

    if not contributors:
        return FatalReviewRecord.none()

    clinical = [e for e, p in contributors if p == "CLINICAL"]
    tmdd = [e for e, p in contributors if p == "TMDD"]
    return FatalReviewRecord(
        required=True,
        status="POTENTIAL_FATAL_PATTERN",
        evidence_ids=tuple(e.evidence_id for e, _ in contributors),
        sink_exposure_context_ids=tuple(
            sorted({e.sink_exposure_context_id for e, _ in contributors})
        ),
        sink_materiality_outcome_class=(_MATERIAL_WITH_COMPROMISE,),
        source_path=tuple(sorted({p for _, p in contributors})),
        analysis_validation_basis_refs=tuple(
            sorted({e.observation.analysis_validation_basis for e, _ in contributors})
        ),
        clinical_attribution_basis_refs=tuple(
            sorted(
                {e.observation.same_target_therapeutic_match_basis for e in clinical}
                | {e.observation.soluble_antigen_attribution_basis for e in clinical}
            )
        ),
        tmdd_input_adequacy_basis_refs=tuple(
            sorted(
                {e.observation.tmdd_input_adequacy_basis for e in tmdd}
                | {e.observation.exposure_scenario_basis for e in tmdd}
            )
        ),
        landscape_as_of=landscape_as_of,
        soluble_antigen_search_scope=soluble_antigen_search_scope,
    )
