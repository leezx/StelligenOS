"""ADC-readiness evaluation and conjugation analysis.

The evaluation is evidence-driven and distinguishes three states that a simple
gap list would collapse into one:

- ``satisfied``   - versioned evidence supports the requirement.
- ``gap``         - no evidence either way; an experiment would resolve it.
- ``adverse``     - evidence exists and points against ADC feasibility.

That third state is the reason this module exists. Reporting a documented
negative as a mere "gap" would misrepresent a known problem as an open question,
which is the most consequential way an asset-engineering report can mislead.

No numeric readiness score is emitted without versioned experimental evidence,
per the module's prohibited-claims list. Evidence *completeness* is reported
instead, which is a count of what exists, not a claim about what it shows.
"""

from __future__ import annotations

from typing import Any

# Requirements for a classical internalising, lysosomally-processed ADC.
# ``gating`` marks a requirement that cannot be compensated for elsewhere.
ADC_CRITERIA: tuple[dict[str, Any], ...] = (
    {
        "criterion_id": "target_expression_tumor",
        "requirement": "Target expressed at adequate copy number on the tumour cell surface in the intended indication.",
        "evidence_key": "tumor_expression",
        "gating": True,
        "resolving_experiment": "Quantitative surface receptor density (e.g. QIFIKIT) across indication-representative models and patient samples.",
    },
    {
        "criterion_id": "target_expression_normal_tissue",
        "requirement": "Normal-tissue expression characterised well enough to predict on-target off-tumour toxicity.",
        "evidence_key": "normal_tissue_risk",
        "gating": True,
        "resolving_experiment": "Full normal-tissue cross-reactivity IHC panel plus quantitative expression in the organs at risk.",
    },
    {
        "criterion_id": "binding_affinity",
        "requirement": "Affinity measured and within a range that supports tumour penetration and uptake.",
        "evidence_key": "affinity",
        "gating": False,
        "resolving_experiment": "SPR or BLI kinetics against the human target, with the parent as comparator.",
    },
    {
        "criterion_id": "native_cell_binding",
        "requirement": "Binding confirmed on cells expressing endogenous target, not only on transfectants.",
        "evidence_key": "cell_binding",
        "gating": False,
        "resolving_experiment": "Flow cytometry on endogenous-expressing lines and primary cells.",
    },
    {
        "criterion_id": "internalization",
        "requirement": "Antibody-induced internalisation of the target-antibody complex.",
        "evidence_key": "internalization",
        "gating": True,
        "resolving_experiment": "Quantitative internalisation time course (pH-sensitive dye or radiolabel) with a surface-retention control.",
    },
    {
        "criterion_id": "lysosomal_trafficking",
        "requirement": "Productive delivery to the lysosome, where payload release occurs.",
        "evidence_key": "lysosomal_trafficking",
        "gating": True,
        "resolving_experiment": "Live-cell lysosomal colocalisation imaging plus a catabolite-release assay.",
    },
    {
        "criterion_id": "receptor_turnover",
        "requirement": "Receptor turnover sufficient to accumulate an intracellular payload dose.",
        "evidence_key": "receptor_turnover",
        "gating": False,
        "resolving_experiment": "Surface recovery kinetics after antibody-induced depletion.",
    },
    {
        "criterion_id": "tox_species_cross_reactivity",
        "requirement": "A toxicology species whose target the antibody binds, so on-target toxicity can be modelled.",
        "evidence_key": "species_cross_reactivity",
        "gating": True,
        "resolving_experiment": "Cross-species binding panel; if only one species qualifies, a surrogate antibody or transgenic model is required.",
    },
    {
        "criterion_id": "conjugation_compatibility",
        "requirement": "Conjugation chemistry defined, with retained binding and acceptable DAR distribution.",
        "evidence_key": "conjugation_compatibility",
        "gating": False,
        "resolving_experiment": "Small conjugation panel at target DAR, then binding, SEC, and hydrophobicity comparison against the naked antibody.",
    },
    {
        "criterion_id": "naked_antibody_tolerability",
        "requirement": "Unconjugated antibody tolerated at exposures that leave room for a payload dose.",
        "evidence_key": "naked_tolerability",
        "gating": True,
        "resolving_experiment": "Dose-range-finding tolerability in the qualified tox species; for a clinically tested antibody, the reported MTD applies.",
    },
    {
        "criterion_id": "adc_in_vivo_activity",
        "requirement": "Conjugate efficacy demonstrated in vivo at tolerated doses.",
        "evidence_key": "adc_activity",
        "gating": True,
        "resolving_experiment": "Xenograft efficacy of the conjugate with an isotype-ADC control and a non-binding-payload control.",
    },
    {
        "criterion_id": "conjugate_freedom_to_operate",
        "requirement": "Technical patent screen covering the conjugate composition, not only the naked antibody.",
        "evidence_key": "conjugate_ip",
        "gating": False,
        "resolving_experiment": "Patent-family and claim analysis of conjugate claims, then external counsel review.",
    },
)

STATUS_SATISFIED = "satisfied"
STATUS_GAP = "gap"
STATUS_ADVERSE = "adverse"


def _classify(entry: Any) -> tuple[str, dict[str, Any]]:
    """Classify a supplied evidence entry.

    Accepts a plain value or a mapping with ``finding``, ``direction``,
    ``source``, and ``version``. ``direction: adverse`` marks evidence that argues
    against feasibility; ``direction: absent_with_negative_indication`` marks the
    case where the only available statement points the wrong way.
    """
    if entry is None:
        return STATUS_GAP, {"finding": None}
    if not isinstance(entry, dict):
        return STATUS_SATISFIED, {"finding": entry}
    direction = str(entry.get("direction", "supportive")).lower()
    if direction in {"adverse", "absent_with_negative_indication", "negative"}:
        return STATUS_ADVERSE, entry
    if entry.get("finding") in (None, "", "unknown"):
        return STATUS_GAP, entry
    return STATUS_SATISFIED, entry


def evaluate_readiness(known_evidence: dict[str, Any] | None) -> dict[str, Any]:
    """Evaluate ADC readiness against the criteria matrix."""
    known_evidence = known_evidence or {}
    assessments: list[dict[str, Any]] = []
    for criterion in ADC_CRITERIA:
        status, detail = _classify(known_evidence.get(criterion["evidence_key"]))
        assessments.append(
            {
                "criterion_id": criterion["criterion_id"],
                "requirement": criterion["requirement"],
                "gating": criterion["gating"],
                "status": status,
                "evidence": detail.get("finding"),
                "evidence_source": detail.get("source"),
                "evidence_version": detail.get("version"),
                "evidence_direction": detail.get("direction", "supportive" if status == STATUS_SATISFIED else None),
                "caveat": detail.get("caveat"),
                "resolving_experiment": criterion["resolving_experiment"],
            }
        )

    satisfied = [item for item in assessments if item["status"] == STATUS_SATISFIED]
    gaps = [item for item in assessments if item["status"] == STATUS_GAP]
    adverse = [item for item in assessments if item["status"] == STATUS_ADVERSE]
    blocking = [item for item in assessments if item["gating"] and item["status"] != STATUS_SATISFIED]

    if adverse and any(item["gating"] for item in adverse):
        verdict = "adverse_evidence_on_a_gating_criterion"
        headline = (
            "At least one gating ADC requirement has evidence pointing against feasibility. "
            "This is not an evidence gap that more of the same work will close; the adverse "
            "finding must be directly overturned or the modality reconsidered."
        )
    elif blocking:
        verdict = "gating_evidence_incomplete"
        headline = "Gating ADC requirements lack evidence. Readiness cannot be assessed until they are resolved."
    else:
        verdict = "gating_evidence_present"
        headline = "All gating requirements have supplied evidence; Gate evaluation can proceed on that evidence."

    return {
        "criteria": assessments,
        "counts": {
            "total": len(assessments),
            "satisfied": len(satisfied),
            "gap": len(gaps),
            "adverse": len(adverse),
            "gating_total": sum(1 for item in assessments if item["gating"]),
            "gating_unsatisfied": len(blocking),
        },
        "evidence_completeness": round(len(satisfied) / len(assessments), 3),
        "blocking_criteria": [item["criterion_id"] for item in blocking],
        "adverse_criteria": [item["criterion_id"] for item in adverse],
        "verdict": verdict,
        "headline": headline,
        "adc_readiness_score": None,
        "score_boundary": (
            "No ADC-readiness score is emitted. Scoring requires versioned experimental evidence on every "
            "gating criterion and is the Gate system's decision, not this module's."
        ),
        "decisive_experiments": [
            {
                "criterion_id": item["criterion_id"],
                "experiment": item["resolving_experiment"],
                "why_decisive": (
                    "Existing evidence argues against this requirement; resolving it determines whether the "
                    "programme is viable in this modality."
                    if item["status"] == STATUS_ADVERSE
                    else "Gating requirement with no evidence; it bounds every downstream decision."
                ),
            }
            for item in sorted(blocking, key=lambda item: 0 if item["status"] == STATUS_ADVERSE else 1)
        ],
    }


def conjugation_analysis(
    chains: dict[str, str],
    position_maps: dict[str, dict[int, dict[str, Any]]] | None = None,
    exposure: dict[str, dict[int, float]] | None = None,
    isotype: str | None = None,
    constant_regions_supplied: bool = False,
) -> dict[str, Any]:
    """Inventory conjugatable residues in the supplied sequence.

    The scope limit here is load-bearing and is reported rather than smoothed
    over: in a full-length IgG most conjugatable lysines and every interchain
    cysteine used by classical maleimide chemistry sit in the constant domains.
    An input carrying only VH and VL cannot support a DAR or conjugation-site
    conclusion, and this function will not offer one.
    """
    position_maps = position_maps or {}
    exposure = exposure or {}

    lysines: list[dict[str, Any]] = []
    cysteines: list[dict[str, Any]] = []
    for chain, sequence in sorted(chains.items()):
        if not sequence:
            continue
        chain_exposure = exposure.get(chain, {})
        chain_map = position_maps.get(chain, {})
        for index, residue in enumerate(sequence, start=1):
            if residue not in {"K", "C"}:
                continue
            relative = chain_exposure.get(index)
            record = {
                "chain": chain,
                "position": index,
                "scheme_position": chain_map.get(index, {}).get("label"),
                "region": chain_map.get(index, {}).get("region", "unknown"),
                "relative_sasa": relative,
                "accessibility": "unknown" if relative is None else ("accessible" if relative >= 0.20 else "buried"),
            }
            (lysines if residue == "K" else cysteines).append(record)

    accessible_lysines = [record for record in lysines if record["accessibility"] == "accessible"]
    cdr_proximal = [record for record in accessible_lysines if record["region"].startswith("CDR")]

    return {
        "scope": "variable_domains_only" if not constant_regions_supplied else "full_chains",
        "isotype": isotype,
        "lysine_inventory": lysines,
        "lysine_count": len(lysines),
        "accessible_lysine_count": len(accessible_lysines) if exposure else None,
        "cdr_proximal_accessible_lysines": [record["scheme_position"] or record["position"] for record in cdr_proximal],
        "cysteine_inventory": cysteines,
        "interchain_cysteines_present": constant_regions_supplied,
        "dar_estimate": None,
        "site_specific_conjugation_assessment": None,
        "scope_limitation": (
            "Only variable domains were supplied. Classical lysine conjugation draws mostly on constant-domain "
            "lysines, and reduced-interchain-cysteine conjugation uses hinge and CH1/CL cysteines that are absent "
            "here, as are engineered-cysteine positions such as the HC and LC THIOMAB sites. No DAR, conjugation "
            "site, or heterogeneity conclusion can be drawn from this input."
            if not constant_regions_supplied
            else "Full chains supplied; constant-domain conjugation sites are in scope."
        ),
        "actionable_finding": (
            f"{len(cdr_proximal)} solvent-accessible lysine(s) sit inside a CDR. Lysine conjugation at a paratope "
            "residue can reduce binding, so a site-specific chemistry or a conjugation-then-binding check is warranted."
            if cdr_proximal
            else "No solvent-accessible lysine was found inside a CDR, so random lysine conjugation is less likely to strike the paratope."
        ),
        "required_input_extension": None
        if constant_regions_supplied
        else "Supply full heavy and light chains, or the isotype and constant-region sequences, to assess conjugation.",
        "method": "sequence_and_exposure_inventory",
    }
