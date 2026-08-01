"""Stages for antibody_binder_asset_engineering@0.4.0.

Changed from 0.2.0: the pipeline splits into two orthogonal tracks.

0.2.0 computed real sequence engineering, but its implicit narrative was
"input binder -> remove liabilities -> rank candidates -> judge ADC readiness".
That narrative optimises a cleaner antibody, not a payload-delivering carrier,
and the two optima can diverge. A naked antibody may want strong agonism and Fc
effector function; a carrier may need them silenced. A naked antibody tends to
want maximal affinity; a carrier may trade affinity for tumour penetration and
receptor turnover.

    Track A  Binder molecule quality
             sequence integrity -> liabilities -> humanness -> candidate sequences
             -> sequence_computational_developability rank

    Track B  ADC carrier phenotype
             native-cell binding -> the five-step delivery cascade
             -> conjugation tolerance -> conjugated-state behaviour

The tracks meet only at a Pareto frontier, never in a single composite score.
Track A is computed; Track B is measured. When Track B has no data, the module
says so and refuses to name a lead.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

import yaml

from lib import (
    adc,
    biophysics,
    cross_asset,
    design,
    evidence,
    evidence_graph,
    failure_modes,
    liabilities,
    numbering,
    pareto,
    phenotype,
    product,
    runtime,
    scoring,
)

STAGES = (
    ("01_binder_intake", "Binder intake and sequence audit"),
    ("02_ip_fto_landscape", "IP and FTO landscape"),
    ("03_structural_analysis", "Structural analysis"),
    ("04_binder_engineering_design", "Binder engineering design"),
    ("05_candidate_family_generation", "Candidate-family generation"),
    ("06_binder_quality_triage", "Track A: binder-quality triage"),
    ("07_adc_carrier_phenotype", "Track B: ADC carrier phenotype"),
    ("08_adc_product_assembly", "ADC product assembly"),
    ("09_adc_failure_mode_analysis", "ADC failure-mode analysis"),
    ("10_pareto_selection", "Two-track Pareto selection"),
    ("11_experimental_design", "Information-gain experimental design"),
    ("12_active_learning", "Active-learning data closed loop"),
    ("13_patent_package", "Patent package"),
    ("14_asset_report", "Asset report"),
    ("15_evidence_graph", "Evidence reasoning graph"),
    ("16_cross_asset_retrieval", "Cross-asset retrieval"),
)

# 0.2.0 stage id -> 0.3.0 stage id, for anyone reading an older run directory.
STAGE_MIGRATION_FROM_0_2_0 = {
    "01_binder_intake": "01_binder_intake",
    "02_ip_fto_landscape": "02_ip_fto_landscape",
    "03_structural_analysis": "03_structural_analysis",
    "04_ai_guided_engineering": "04_binder_engineering_design",
    "05_candidate_family_generation": "05_candidate_family_generation",
    "06_computational_triage": "06_binder_quality_triage",
    "07_experimental_design": "11_experimental_design",
    "08_active_learning": "12_active_learning",
    "09_adc_readiness": "09_adc_failure_mode_analysis",
    "10_patent_package": "13_patent_package",
    "11_asset_report": "14_asset_report",
}

VALID_AA = set("ACDEFGHIKLMNPQRSTVWYX")

NUMBERING_IMPORTS = ["abnumber", "anarci"]
STRUCTURE_IMPORTS = ["ImmuneBuilder", "torch"]
SASA_IMPORTS = ["Bio"]


def normalized_sequence(value: Any) -> str:
    return "".join(str(value or "").split()).upper()


def _check_residues(sequence: str, label: str) -> None:
    invalid = sorted(set(sequence) - VALID_AA)
    if sequence and invalid:
        raise ValueError(f"{label} contains invalid amino-acid codes: {invalid}")


def validate_binder(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalise the frozen input.

    Accepts the 0.1.0 shape (scalar evidence values), the 0.2.0 shape (evidence
    mappings with ``direction``), and the 0.3.0 additions
    (``adc_carrier_observations``, ``payload``).
    """
    required = ("asset_id", "binder_id", "format", "target", "sequences", "provenance")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Missing required binder fields: {', '.join(missing)}")

    target = payload["target"]
    if not isinstance(target, dict) or not all(target.get(field) for field in ("gene", "protein", "indication")):
        raise ValueError("target.gene, target.protein, and target.indication are required")

    sequences = payload["sequences"]
    if not isinstance(sequences, dict):
        raise ValueError("sequences must be a mapping")
    vh = normalized_sequence(sequences.get("vh"))
    vl = normalized_sequence(sequences.get("vl"))
    if not vh:
        raise ValueError("sequences.vh is required")
    if str(payload["format"]).casefold() not in {"vhh", "nanobody"} and not vl:
        raise ValueError("sequences.vl is required unless format is VHH/nanobody")
    _check_residues(vh, "vh")
    _check_residues(vl, "vl")

    validated_candidates: list[dict[str, Any]] = []
    supplied = payload.get("candidate_sequences") or []
    if not isinstance(supplied, list):
        raise ValueError("candidate_sequences must be a list when present")
    for index, candidate in enumerate(supplied, start=1):
        if not isinstance(candidate, dict):
            raise ValueError(f"candidate_sequences[{index}] must be a mapping")
        candidate_vh = normalized_sequence(candidate.get("vh"))
        candidate_vl = normalized_sequence(candidate.get("vl"))
        if not candidate_vh:
            raise ValueError(f"candidate_sequences[{index}].vh is required")
        _check_residues(candidate_vh, f"candidate_sequences[{index}].vh")
        _check_residues(candidate_vl, f"candidate_sequences[{index}].vl")
        validated_candidates.append({**candidate, "vh": candidate_vh, "vl": candidate_vl or None})

    constraints = payload.get("constraints") or {}
    if not isinstance(constraints, dict):
        raise ValueError("constraints must be a mapping when present")
    budget = constraints.get("maximum_mutations_per_candidate")
    if budget is not None and (not isinstance(budget, int) or budget < 1):
        raise ValueError("constraints.maximum_mutations_per_candidate must be a positive integer")

    observations = payload.get("adc_carrier_observations")
    if observations is not None and not isinstance(observations, list):
        raise ValueError("adc_carrier_observations must be a list when present")

    normalized = dict(payload)
    normalized["sequences"] = {"vh": vh, "vl": vl or None}
    if validated_candidates:
        normalized["candidate_sequences"] = validated_candidates
    return normalized


def _chains(binder: dict[str, Any]) -> dict[str, str]:
    return {name: sequence for name, sequence in binder["sequences"].items() if sequence}


def _availability(context: dict[str, Any], tool_ids: list[str]) -> dict[str, Any]:
    status = context["software_status"]["tools"]
    return {
        tool_id: {
            "status": status.get(tool_id, {}).get("status", "not_declared"),
            "resolved_in": status.get(tool_id, {}).get("interpreter_role"),
            "version": status.get(tool_id, {}).get("version"),
        }
        for tool_id in tool_ids
    }


def _int_keyed(mapping: Any) -> dict[int, Any]:
    if not isinstance(mapping, dict):
        return {}
    coerced: dict[int, Any] = {}
    for key, value in mapping.items():
        try:
            coerced[int(key)] = value
        except (TypeError, ValueError):
            continue
    return coerced


def _adc_corpus_root(context: dict[str, Any]) -> Path | None:
    """Locate the clinical ADC comparator corpus.

    Two sources, in order: the declared ``ADC_REFERENCE_ROOT`` data root, then the
    ``source_root`` recorded in the workspace's historical ADC benchmark. Falling back
    to the benchmark keeps the comparator corpus and the Gate system's calibration
    corpus from silently diverging onto different trees.
    """
    declared = os.environ.get("ADC_REFERENCE_ROOT")
    if declared and Path(declared).exists():
        return Path(declared)
    benchmark = Path(__file__).resolve().parents[2] / "configs/historical_adc_benchmark.yaml"
    if not benchmark.exists():
        return None
    try:
        source_root = (yaml.safe_load(benchmark.read_text()) or {}).get("source_root")
    except yaml.YAMLError:
        return None
    if not source_root:
        return None
    resolved = (benchmark.parent.parent / str(source_root)).resolve()
    return resolved if resolved.exists() else None


def _reference_year(context: dict[str, Any]) -> int | None:
    """Year of this run, from the manifest timestamp rather than the clock.

    Evidence freshness must be a property of the run, so re-executing a stage inside
    an old run directory reproduces the numbers it produced originally.
    """
    stamp = str(context.get("created_at_utc") or "")
    return int(stamp[:4]) if stamp[:4].isdigit() else None


def _position_maps(context: dict[str, Any]) -> dict[str, dict[int, dict[str, Any]]]:
    intake = context["previous"].get("01_binder_intake", {})
    raw = (intake.get("numbering") or {}).get("position_maps") or {}
    return {chain: _int_keyed(entry) for chain, entry in raw.items()}


def _exposure(context: dict[str, Any]) -> dict[str, dict[int, float]]:
    structural = context["previous"].get("03_structural_analysis", {})
    raw = (structural.get("solvent_accessibility") or {}).get("exposure") or {}
    return {chain: _int_keyed(entry) for chain, entry in raw.items()}


def _germline(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    intake = context["previous"].get("01_binder_intake", {})
    return (intake.get("numbering") or {}).get("germline") or {}


def _cascade(context: dict[str, Any]) -> dict[str, Any]:
    return context["previous"].get("07_adc_carrier_phenotype", {}).get("delivery_cascade") or {}


# --------------------------------------------------------------------------- 01


def binder_intake(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    chains = _chains(binder)

    numbering_record: dict[str, Any] = {"status": "unavailable"}
    unresolved: list[str] = []
    try:
        raw = runtime.run_op("number_chains", {"chains": chains}, requires=NUMBERING_IMPORTS)
    except runtime.OpUnavailable as error:
        numbering_record = {"status": "unavailable", "detail": str(error)}
        unresolved.append("antibody numbering (ANARCI/abnumber) unavailable; CDR-aware analysis degraded")
    else:
        numbering_record = {
            "status": raw.get("status", "unavailable"),
            "tool": raw.get("tool"),
            "tool_version": raw.get("tool_version"),
            "primary_definition": raw.get("primary_definition"),
            "position_maps": numbering.position_maps(raw, "union"),
            "germline": {chain: entry.get("germline", {}) for chain, entry in (raw.get("chains") or {}).items()},
            "regions": {
                chain: {
                    scheme: {
                        "chain_type": record.get("chain_type"),
                        "cdr1": record.get("cdr1"),
                        "cdr2": record.get("cdr2"),
                        "cdr3": record.get("cdr3"),
                        "regions": record.get("regions"),
                    }
                    for scheme, record in (entry.get("schemes") or {}).items()
                }
                for chain, entry in (raw.get("chains") or {}).items()
            },
        }

    position_maps = {chain: _int_keyed(entry) for chain, entry in (numbering_record.get("position_maps") or {}).items()}
    scan = liabilities.scan_binder(chains, position_maps)
    biophysical = {chain: biophysics.describe_chain(sequence) for chain, sequence in sorted(chains.items())}
    biophysical["fv_combined"] = biophysics.combined_variable_domain(chains["vh"], chains.get("vl"))

    provenance = binder["provenance"]
    if str(provenance.get("owner_or_license_status", "")).casefold() in {"", "unknown", "unresolved", "tbd"}:
        unresolved.append("binder ownership/licence status")
    if not binder.get("known_evidence", {}).get("affinity"):
        unresolved.append("versioned affinity evidence")
    for record in scan["cysteine_audit"]:
        if record["status"] != "canonical":
            unresolved.append(f"{record['chain']} cysteine count is non-canonical: {record['interpretation']}")
    if not binder.get("adc_carrier_observations"):
        unresolved.append("no structured ADC carrier phenotype observations supplied")

    return {
        "status": "complete_with_gaps" if unresolved else "complete",
        "binder_identity": {
            "asset_id": binder["asset_id"],
            "binder_id": binder["binder_id"],
            "format": binder["format"],
            "isotype": binder.get("isotype"),
            "target": binder["target"],
        },
        "numbering": numbering_record,
        "germline_summary": {
            chain: {
                "closest_human_v_gene": entry.get("closest_human_v_gene"),
                "closest_human_j_gene": entry.get("closest_human_j_gene"),
                "framework_identity_percent": entry.get("framework_identity_percent"),
                "framework_deviation_count": len(entry.get("framework_deviations_from_germline") or []),
            }
            for chain, entry in (numbering_record.get("germline") or {}).items()
        },
        "liabilities": scan,
        "biophysical_properties": biophysical,
        "annotation_tools": _availability(context, ["anarci", "abnumber", "biopython"]),
        "unresolved": unresolved,
        "claims": [
            "Numbering, region assignment, and germline identity are computational annotations of the supplied sequence.",
            "Liability entries are rule-based flags, not measured degradation.",
            "Biophysical descriptors are sequence-derived, not measured.",
        ],
    }


# --------------------------------------------------------------------------- 02


def ip_fto_landscape(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    target = binder["target"]
    regions = (context["previous"].get("01_binder_intake", {}).get("numbering") or {}).get("regions") or {}

    cdr_queries: list[dict[str, Any]] = []
    for chain, schemes in sorted(regions.items()):
        for scheme, record in sorted(schemes.items()):
            if not any([record.get("cdr1"), record.get("cdr2"), record.get("cdr3")]):
                continue
            cdr_queries.append(
                {
                    "chain": chain,
                    "cdr_definition": scheme,
                    "cdr1": record.get("cdr1"),
                    "cdr2": record.get("cdr2"),
                    "cdr3": record.get("cdr3"),
                }
            )

    conjugate_ip = (binder.get("known_evidence") or {}).get("conjugate_ip")
    conjugate_note = None
    if isinstance(conjugate_ip, dict):
        conjugate_note = {
            "supplied_finding": conjugate_ip.get("finding"),
            "direction": conjugate_ip.get("direction"),
            "source": conjugate_ip.get("source"),
            "caveat": conjugate_ip.get("caveat"),
        }

    return {
        "status": "complete_with_gaps",
        "search_scopes": [
            {"scope": "exact VH/VL sequence", "query_inputs": ["VH", "VL", "paired VH/VL"]},
            {
                "scope": "CDR-defined sequence families",
                "query_inputs": cdr_queries or ["numbering unavailable; CDRs could not be extracted"],
                "note": "Percent-identity claim thresholds must be screened against these exact CDR strings.",
            },
            {"scope": "target and epitope claims", "query_inputs": [target["gene"], target["protein"], target.get("epitope")]},
            {"scope": "conjugate composition and use", "query_inputs": [target["protein"], "cytotoxic conjugate", "payload class"]},
        ],
        "supplied_conjugate_ip_evidence": conjugate_note,
        "epitope_diversification_note": (
            "If the parent epitope is encumbered, sequence engineering around the parent does not escape an "
            "epitope claim. Only a different epitope does, which is an antibody-discovery task rather than an "
            "engineering task."
        ),
        "software": _availability(context, ["blast_plus", "mmseqs2"]),
        "required_data": ["therapeutic_antibody_reference", "patent_sequence_exports"],
        "outputs_pending": [
            "claim chart",
            "sequence-neighborhood report",
            "epitope/functional-claim map",
            "conjugate-claim analysis",
            "design-around constraints",
            "external-counsel review",
        ],
        "legal_boundary": (
            "Technical search plan only. This is not an FTO opinion, and no statement here clears any "
            "activity. External counsel review remains required."
        ),
    }


# --------------------------------------------------------------------------- 03


def structural_analysis(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    chains = _chains(binder)
    run_dir = Path(context["run_dir"])
    allow_external = bool(context.get("allow_external"))

    prediction: dict[str, Any] = {"status": "not_run"}
    accessibility: dict[str, Any] = {"status": "not_run"}
    external_executed = False

    supplied_structure = (binder.get("known_evidence") or {}).get("structure")
    structure_path: str | None = None
    if isinstance(supplied_structure, dict) and supplied_structure.get("path"):
        structure_path = str(supplied_structure["path"])
        prediction = {"status": "supplied", "structure_path": structure_path, "source": "input known_evidence.structure"}
    else:
        try:
            prediction = runtime.run_op(
                "predict_structure",
                {"chains": chains, "output_path": str(run_dir / "03_structural_analysis" / "fv_model.pdb")},
                requires=STRUCTURE_IMPORTS,
                allow_external=allow_external,
            )
            structure_path = prediction.get("structure_path")
            external_executed = True
        except runtime.OpUnavailable as error:
            prediction = {"status": "skipped", "detail": str(error)}

    if structure_path:
        try:
            accessibility = runtime.run_op(
                "solvent_accessibility", {"structure_path": structure_path}, requires=SASA_IMPORTS
            )
        except runtime.OpUnavailable as error:
            accessibility = {"status": "unavailable", "detail": str(error)}

    exposure = {chain: _int_keyed(entry) for chain, entry in (accessibility.get("exposure") or {}).items()}
    position_maps = _position_maps(context)
    rescan = liabilities.scan_binder(chains, position_maps, exposure) if exposure else None

    reclassified: list[dict[str, Any]] = []
    if rescan:
        baseline = {
            (hit["chain"], hit["position"], hit["liability_id"]): hit
            for hit in (context["previous"].get("01_binder_intake", {}).get("liabilities") or {}).get("hits", [])
        }
        for hit in rescan["hits"]:
            previous = baseline.get((hit["chain"], hit["position"], hit["liability_id"]))
            if previous and previous["chemical_risk_tier"] != hit["chemical_risk_tier"]:
                reclassified.append(
                    {
                        "liability_id": hit["liability_id"],
                        "chain": hit["chain"],
                        "position": hit["position"],
                        "scheme_position": hit["scheme_position"],
                        "region": hit["region"],
                        "sequence_only_tier": previous["chemical_risk_tier"],
                        "exposure_weighted_tier": hit["chemical_risk_tier"],
                        "relative_sasa": hit["relative_sasa"],
                        "exposure_class": hit["exposure_class"],
                    }
                )

    return {
        "status": "complete" if rescan else "complete_with_gaps",
        "external_programs_executed": external_executed,
        "structure_prediction": prediction,
        "solvent_accessibility": {key: value for key, value in accessibility.items() if key != "per_residue"},
        "per_residue_accessibility": accessibility.get("per_residue"),
        "exposure_weighted_liabilities": rescan,
        "reclassified_by_exposure": reclassified,
        "software": _availability(context, ["immune_builder", "igfold", "openfold", "rosetta", "foldx", "biopython"]),
        "outstanding_work": [
            "predict an ensemble rather than a single conformation",
            "map interface contacts once antigen-complex evidence exists",
            "confirm CDR-H3 and VH/VL orientation against an experimental structure",
            "recompute framework exposure on a full-length construct, where CH1/CL packing buries part of it",
        ],
        "boundary": (
            "A predicted apo Fv model. No antigen is present, so no paratope, epitope contact, or "
            "interface residue can be derived from it, and exposure reflects one conformation."
        ),
        "scope_caveat": accessibility.get("scope_caveat"),
    }


# --------------------------------------------------------------------------- 04


def binder_engineering_design(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    chains = _chains(binder)
    constraints = binder.get("constraints") or {}
    position_maps = _position_maps(context)

    structural = context["previous"].get("03_structural_analysis", {})
    exposure_weighted = structural.get("exposure_weighted_liabilities")
    intake = context["previous"].get("01_binder_intake", {})
    scan = exposure_weighted or intake.get("liabilities") or {"hits": []}

    proposals = design.propose_mutations(
        chains=chains,
        liabilities=scan.get("hits", []),
        germline=_germline(context),
        constraints=constraints,
        position_maps=position_maps,
    )

    # Positions worth scanning for a signalling/affinity decoupling campaign: CDR
    # positions, which are where binding and agonism are most likely encoded.
    cdr_scan_positions = [
        {"chain": chain, "position": position, "scheme_position": annotation.get("label"), "region": annotation.get("region")}
        for chain, entries in sorted(position_maps.items())
        for position, annotation in sorted(entries.items())
        if str(annotation.get("region", "")).startswith("CDR")
    ]

    specifications = design.construct_specifications(binder, cdr_scan_positions)

    by_source: dict[str, int] = {}
    by_region: dict[str, int] = {}
    for proposal in proposals["proposals"]:
        by_source[proposal["source"]] = by_source.get(proposal["source"], 0) + 1
        by_region[proposal["region"]] = by_region.get(proposal["region"], 0) + 1

    return {
        "status": "complete" if proposals["proposals"] else "complete_with_gaps",
        "objectives": binder.get("engineering_objectives", []),
        "constraints": constraints,
        "liability_basis": "exposure_weighted" if exposure_weighted else "sequence_only",
        "sequence_proposals": proposals["proposals"],
        "rejected_proposals": proposals["rejected"],
        "protected_positions": proposals["protected_positions"],
        "dual_benefit_proposals": proposals["dual_benefit_proposals"],
        "construct_specifications": specifications,
        "cdr_scan_positions": cdr_scan_positions,
        "proposal_counts": {
            "total": len(proposals["proposals"]),
            "by_source": dict(sorted(by_source.items())),
            "by_region": dict(sorted(by_region.items())),
            "dual_benefit": len(proposals["dual_benefit_proposals"]),
            "requiring_binding_confirmation": sum(
                1 for proposal in proposals["proposals"] if proposal["requires_binding_confirmation"]
            ),
            "requiring_fold_confirmation": sum(
                1 for proposal in proposals["proposals"] if proposal.get("requires_fold_confirmation")
            ),
            "reducing_framework_humanness": sum(
                1 for proposal in proposals["proposals"] if proposal.get("reduces_framework_humanness")
            ),
            "region_definition_contested": sum(
                1 for proposal in proposals["proposals"] if not proposal.get("region_definitions_agree", True)
            ),
        },
        "risk_axis_note": (
            "Three risks are separated because they are settled by different experiments. "
            "requires_binding_confirmation: the position is a CDR under IMGT or Kabat, so affinity must be "
            "remeasured. requires_fold_confirmation: the side chain is buried, so expression and "
            "thermostability must be checked. reduces_framework_humanness: the residue being removed is the "
            "human germline residue, so the fix costs framework identity. A proposal can carry all three."
        ),
        "software": _availability(context, ["proteinmpnn", "esm", "rosetta"]),
        "model_backed_design_status": (
            "Not configured, and deliberately not the next priority. A learned sequence designer would "
            "generate more plausible sequences, but the objective function for an ADC carrier - non-agonism, "
            "high lysosomal flux, low normal-tissue uptake, conjugated-state stability - is not yet "
            "measurable in this pipeline. A model would optimise the wrong target more efficiently. "
            "Establish the phenotype assay schema and a variant-phenotype dataset first."
        ),
        "paratope_first_warning": (
            "Do not synthesise all CDR liability fixes. Map the paratope first (alanine or low-complexity "
            "substitution scan, display selection, parent competition binding) with signalling and "
            "internalisation measured in parallel, to classify positions as binding-critical, "
            "signalling-biasing, or engineering-tolerant. A CDR variant that keeps binding and "
            "internalisation while reducing agonism is worth more than any reduction in liability burden."
        ),
        "method": proposals["method"],
        "boundary": proposals["boundary"],
    }


# --------------------------------------------------------------------------- 05


def candidate_family_generation(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    constraints = binder.get("constraints") or {}
    engineering = context["previous"].get("04_binder_engineering_design", {})
    proposals = engineering.get("sequence_proposals") or []
    specifications = engineering.get("construct_specifications") or {}

    generated = design.generate_candidates(binder, proposals, constraints)
    for candidate in generated["candidates"]:
        candidate.setdefault("entry_kind", "sequence")

    construct_entries: list[dict[str, Any]] = []
    for family_name, family in (specifications.get("families") or {}).items():
        construct_entries.extend(family.get("constructs") or [])
        construct_entries.extend(family.get("bands") or [])

    for candidate in binder.get("candidate_sequences") or []:
        generated["candidates"].append(
            {
                "candidate_id": candidate.get("candidate_id", f"{binder['binder_id']}-SUPPLIED"),
                "family": candidate.get("family", "supplied"),
                "entry_kind": "sequence",
                "vh": candidate["vh"],
                "vl": candidate.get("vl"),
                "mutations": [],
                "mutation_count": 0,
                "generation_method": candidate.get("generation_method", "user supplied"),
            }
        )

    sequence_families = sorted({candidate["family"] for candidate in generated["candidates"]} - {"parent"})
    construct_families = sorted({entry["family"] for entry in construct_entries})

    return {
        "status": "complete" if generated["independent_family_count"] >= 3 else "complete_with_gaps",
        "sequence_candidates": generated["candidates"],
        "sequence_candidate_count": len(generated["candidates"]),
        "construct_specifications": construct_entries,
        "construct_specification_count": len(construct_entries),
        "excluded_candidates": generated["excluded"],
        "proposals_in_no_family": generated["proposals_in_no_family"],
        "sequence_families": sequence_families,
        "construct_families": construct_families,
        "total_family_count": len(sequence_families) + len(construct_families),
        "mutation_budget": generated["mutation_budget"],
        "forbidden_motifs_screened": generated["forbidden_motifs_screened"],
        "entry_kind_legend": {
            "sequence": "A complete variant sequence, orderable as a gene today.",
            "construct_specification": "A construct to build; needs constant-region sequence to express as sequence.",
            "campaign_specification": "Needs a scanning or selection campaign; not a single construct.",
        },
        "method": generated["method"],
        "boundary": (
            "Sequence candidates are constructed, not validated. Construct and campaign specifications are "
            "not sequences at all. None of the three has been expressed or measured."
        ),
    }


# --------------------------------------------------------------------------- 06


def binder_quality_triage(context: dict[str, Any]) -> dict[str, Any]:
    previous = context["previous"]
    if "05_candidate_family_generation" not in previous:
        return {
            "status": "blocked",
            "detail": "05_candidate_family_generation has not produced candidates; run the stages in order.",
        }
    candidates = previous["05_candidate_family_generation"].get("sequence_candidates") or []

    result = scoring.triage(
        candidates=candidates,
        position_maps=_position_maps(context),
        exposure=_exposure(context),
        germline=_germline(context),
    )

    return {
        "status": "complete",
        "track": "A_binder_molecule_quality",
        "scoring_policy": result["policy"],
        "candidates_scored": result["candidates_scored"],
        "ranking": result["ranking"],
        "parent_candidate_id": result["parent_candidate_id"],
        "parent_sequence_developability_score": result["parent_sequence_developability_score"],
        "candidates_scoring_above_parent": result["candidates_scoring_above_parent"],
        "software": _availability(context, ["anarci", "abnumber", "esm", "foldx", "pandas"]),
        "not_predicted": result["policy"]["excluded_axes"],
        "humanness_note": result["humanness_note"],
        "comparability": result["comparability"],
        "track_boundary": (
            "This is Track A only. It ranks sequences as molecules and says nothing about payload delivery. "
            "It must not be used to select an ADC lead; see 10_pareto_selection."
        ),
        "method": result["method"],
        "boundary": result["boundary"],
    }


# --------------------------------------------------------------------------- 07


def adc_carrier_phenotype(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    observations = binder.get("adc_carrier_observations") or []

    cascade = phenotype.evaluate_cascade(observations)
    carrier = phenotype.carrier_quality(cascade)
    decision = phenotype.modality_decision(cascade)

    return {
        "status": "complete" if cascade["usable_observation_count"] else "complete_with_gaps",
        "track": "B_adc_carrier_phenotype",
        "delivery_cascade": cascade,
        "carrier_quality": carrier,
        "modality_decision": decision,
        "measurement_catalogue": sorted(phenotype.MEASUREMENT_TYPES),
        "required_observation_metadata": list(phenotype.REQUIRED_METADATA),
        "unusable_observation_count": len(cascade["unusable_observations"]),
        "why_five_steps": (
            "Leaving the surface, entering the endosome, reaching the lysosome, releasing an active "
            "catabolite, and releasing enough to kill are five physically distinct events. An antibody can "
            "pass the first and fail the third by recycling, or pass the third and fail the fourth with the "
            "wrong linker. Collapsing them into one internalisation flag makes those failures invisible."
        ),
        "boundary": (
            "Absence of observations is reported as no_data, never as a negative result, and carrier "
            "quality is null rather than zero when unmeasured."
        ),
    }


# --------------------------------------------------------------------------- 08


def adc_product_assembly(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    families = context["previous"].get("05_candidate_family_generation", {})
    antibody_candidates = list(families.get("sequence_candidates") or []) + list(
        families.get("construct_specifications") or []
    )

    conjugation = adc.conjugation_analysis(
        chains=_chains(binder),
        position_maps=_position_maps(context),
        exposure=_exposure(context),
        isotype=binder.get("isotype"),
        constant_regions_supplied=bool(binder.get("constant_regions_supplied")),
    )

    payload = binder.get("payload") or {}
    matrix = product.assemble(
        antibody_candidates=antibody_candidates,
        conjugation_analysis=conjugation,
        constant_regions_supplied=bool(binder.get("constant_regions_supplied")),
        payload_declared=bool(payload.get("payload_class") and payload.get("linker")),
    )

    return {
        "status": "complete_with_gaps",
        "conjugation_analysis": conjugation,
        "declared_payload": payload or None,
        "product_matrix": matrix,
        "entity_model": [
            "AntibodyCandidate (Fv plus format and Fc specification)",
            "ConjugationVariant (site chemistry plus DAR)",
            "ADCProductCandidate (the cross product, which is what a programme actually decides about)",
        ],
        "why_not_reuse_the_fv_ranking": (
            "Conjugate hydrophobicity, aggregation, charge heterogeneity, plasma stability, and clearance "
            "are dominated by payload physicochemistry and constant-region context. Carrying a naked-Fv "
            "ranking onto a product would assume the payload is inert."
        ),
        "boundary": matrix["boundary"],
    }


# --------------------------------------------------------------------------- 09


def adc_failure_mode_analysis(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    known = binder.get("known_evidence") or {}
    cascade = _cascade(context)

    readiness = adc.evaluate_readiness(known)
    analysis = failure_modes.analyse(cascade, known)
    propagated = evidence.propagate(known, _reference_year(context))
    return {
        "status": "complete_with_gaps",
        "failure_mode_analysis": analysis,
        "evidence_matrix": readiness,
        # Direction alone cannot say whether a criterion rests on a patent sentence or
        # an animal study. lib/evidence.py explains why agreement, tier, diversity and
        # freshness are reported separately rather than blended into one number.
        "evidence_confidence": propagated,
        "adc_readiness_score": None,
        "why_a_graph_not_a_checklist": (
            "A checklist answers how many gaps remain, which does not say what to do next: gaps are not "
            "equally informative and one experiment can close several. The causal trees let each experiment "
            "be scored by how many unresolved failure modes it can discriminate."
        ),
        "required_data": ["normal_tissue_atlas", "adc_reference", "experimental_results"],
        "boundary": (
            "No ADC-readiness score is emitted. The trees enumerate modelled failure modes, not every "
            "possible one, and an excluded mode is excluded only to the strength of its cited evidence."
        ),
    }


# --------------------------------------------------------------------------- 10


def pareto_selection(context: dict[str, Any]) -> dict[str, Any]:
    triage = context["previous"].get("06_binder_quality_triage", {})
    phenotype_stage = context["previous"].get("07_adc_carrier_phenotype", {})
    ranking = triage.get("ranking") or []

    carrier_record = phenotype_stage.get("carrier_quality") or {}
    # The phenotype stage scores the parent molecule. A candidate inherits nothing:
    # carrier capability is a measured property of a specific construct, and no
    # sequence variant may inherit its parent's measurement.
    carrier_scores = {}
    parent_id = triage.get("parent_candidate_id")
    if parent_id and carrier_record.get("adc_carrier_quality_score") is not None:
        carrier_scores[parent_id] = carrier_record

    selection = pareto.select(ranking, carrier_scores)

    return {
        "status": "complete",
        "selection": selection,
        "carrier_scores_available_for": sorted(carrier_scores),
        "no_inheritance_rule": (
            "Carrier quality is never inherited by a variant from its parent. Each construct's delivery "
            "behaviour must be measured on that construct: a single CDR substitution can abolish "
            "internalisation without changing any sequence descriptor."
        ),
        "boundary": selection["boundary"],
    }


# --------------------------------------------------------------------------- 11


def experimental_design(context: dict[str, Any]) -> dict[str, Any]:
    previous = context["previous"]
    analysis = previous.get("09_adc_failure_mode_analysis", {}).get("failure_mode_analysis", {})
    prioritisation = analysis.get("experiment_prioritisation", {})
    ranked = prioritisation.get("ranked_experiments") or []
    decision = previous.get("07_adc_carrier_phenotype", {}).get("modality_decision", {})
    triage = previous.get("06_binder_quality_triage", {})
    engineering = previous.get("04_binder_engineering_design", {})

    modality_first = decision.get("decision") in {"modality_unproven_run_kill_experiment", "stop_this_route"}

    package = [
        {
            "priority": index,
            "experiment_id": item["experiment_id"],
            "assay": item["name"],
            "detail": item["detail"],
            "information_gain": item["information_gain"],
            "resolves_failure_modes": item["resolves_unresolved_modes"],
            "can_overturn": item["can_overturn_supported_modes"],
            "ready_to_run": item["ready_to_run"],
            "unmet_prerequisites": item["unmet_prerequisites"],
            "phase": item["phase"],
            "cost_tier": item["cost_tier"],
        }
        for index, item in enumerate(
            [entry for entry in ranked if entry["information_gain"] > 0], start=1
        )
    ]

    deferred = [
        {
            "assay": "expression and SEC of engineered sequence variants",
            "why_deferred": "Sequence optimisation is only worth running once the modality is proven.",
            "candidates": [row["candidate_id"] for row in (triage.get("ranking") or [])[:5]],
        },
        {
            "assay": "forced degradation with peptide mapping",
            "why_deferred": "Confirms the computational liability flags; not on the critical path to the modality decision.",
        },
        {
            "assay": "SPR or BLI of engineered variants against the parent",
            "why_deferred": "Needed before promoting any variant, but not before deciding whether an ADC is viable.",
            "applies_to": [
                proposal["proposal_id"]
                for proposal in (engineering.get("sequence_proposals") or [])
                if proposal.get("requires_binding_confirmation")
            ][:20],
        },
    ]

    return {
        "status": "complete_with_gaps",
        "sequencing_rule": (
            "Experiments are ordered by information gain against unresolved failure modes, not by assay "
            "convention. Sequence-optimisation assays are deferred until the modality decision is resolved."
            if modality_first
            else "Modality is not in question; the package is ordered by information gain."
        ),
        "modality_decision": decision.get("decision"),
        "critical_path": package,
        "next_experiment": prioritisation.get("next_experiment"),
        "deferred_until_modality_resolved": deferred if modality_first else [],
        "uninformative_experiments": prioritisation.get("uninformative_experiments"),
        "design_rules": [
            "include the parent and an irrelevant-isotype control in every comparison",
            "compare constructs, not only concentrations: parent IgG1 versus Fc-silent versus Fab",
            "normalise uptake and delivery to surface binding, and declare the basis",
            "use at least two biological replicates and report uncertainty",
            "include an antigen-negative counter-screen for every killing readout",
            "retain raw data, assay version, operator, lot, and acceptance criteria",
        ],
        "cost_and_time": "To be supplied by the selected laboratory or CRO.",
    }


# --------------------------------------------------------------------------- 12


def active_learning(context: dict[str, Any]) -> dict[str, Any]:
    previous = context["previous"]
    triage = previous.get("06_binder_quality_triage", {})
    cascade = _cascade(context)
    ranking = triage.get("ranking") or []

    return {
        "status": "complete_with_gaps",
        "role": "strict_data_closed_loop",
        "label_schema": {
            "binder_labels": ["expression_titre", "monomer_percent", "tm", "affinity_kd", "on_rate", "off_rate"],
            "carrier_labels": [
                "surface_binding_4c",
                "acid_wash_internalized_fraction",
                "lysosomal_delivery_fraction",
                "recycling_fraction",
                "catabolite_release",
                "payload_dependent_killing",
            ],
            "safety_labels": ["canonical_nfkb", "alternative_nfkb", "cytokine_release", "normal_cell_uptake"],
            "required_metadata": list(phenotype.REQUIRED_METADATA),
        },
        "observations": [],
        "awaiting_observations_for": [row["candidate_id"] for row in ranking],
        "prior_sequence_developability_scores": {
            row["candidate_id"]: row["sequence_computational_developability_score"] for row in ranking
        },
        "usable_carrier_observations": cascade.get("usable_observation_count", 0),
        "software": _availability(context, ["pandas", "scikit_learn", "optuna"]),
        "model_fitting_status": (
            "No model is fitted, and that remains correct. The next version's goal is not to start fitting "
            "but to become a strict data closed loop: variant in, phenotype out, with metadata enforced. "
            "A model trained on sequence descriptors alone would predict sequence descriptors."
        ),
        "sequencing_for_model_readiness": [
            "1. Establish the ADC phenotype assay schema (done: 07_adc_carrier_phenotype).",
            "2. Collect real data on the parent and a small rational construct panel.",
            "3. Build a variant-phenotype dataset with enforced metadata.",
            "4. Only then attach a structure or learned model.",
            "5. Use active learning to choose the next batch of variants.",
        ],
        "update_policy": [
            "never overwrite prior candidate scores; append a new scored version",
            "fit only after assay QC and candidate identity confirmation",
            "keep binder, carrier, safety, and IP objectives on separate axes",
            "a sequence developability score must never outweigh a delivery or binding failure",
            "carrier labels belong to a specific construct and are never inherited by a variant",
            "human approval is required before the next design round",
        ],
        "boundary": "No model is fitted in this run because no usable experimental observation exists yet.",
    }


# --------------------------------------------------------------------------- 13


def patent_package(context: dict[str, Any]) -> dict[str, Any]:
    binder = context["binder"]
    previous = context["previous"]
    regions = (previous.get("01_binder_intake", {}).get("numbering") or {}).get("regions") or {}
    families = previous.get("05_candidate_family_generation", {})
    products = previous.get("08_adc_product_assembly", {}).get("product_matrix", {})

    cdr_table = [
        {
            "chain": chain,
            "cdr_definition": scheme,
            "cdr1": record.get("cdr1"),
            "cdr2": record.get("cdr2"),
            "cdr3": record.get("cdr3"),
        }
        for chain, schemes in sorted(regions.items())
        for scheme, record in sorted(schemes.items())
    ]

    return {
        "status": "complete_with_gaps",
        "package_sections": [
            "binder and provenance",
            "representative VH/VL sequences",
            "numbered CDRs under both definitions",
            "generated sequence families and their derivation",
            "construct and conjugation formats claimed",
            "structural and epitope evidence",
            "comparative functional data",
            "carrier phenotype data",
            "conjugate developability data",
            "unexpected effects",
            "known prior art and unresolved FTO risks",
            "inventor contribution record",
        ],
        "representative_asset": binder["asset_id"],
        "numbered_cdrs": cdr_table,
        "generated_sequence_families": [
            {
                "candidate_id": candidate["candidate_id"],
                "family": candidate["family"],
                "mutation_count": candidate.get("mutation_count", 0),
                "substitutions": [mutation["substitution"] for mutation in candidate.get("mutations", [])],
            }
            for candidate in (families.get("sequence_candidates") or [])
        ],
        "claimable_product_formats": [
            {"product_id": item["product_id"], "conjugation_variant": item["conjugation_variant"], "format": item["antibody_format"]}
            for item in (products.get("products") or [])
        ],
        "software": _availability(context, ["blast_plus", "mmseqs2", "jinja2"]),
        "missing": [
            "completed patent searches",
            "claim chart",
            "experimentally tested sequence families",
            "carrier phenotype data",
            "comparative experimental evidence",
            "unexpected-effect data supporting inventive step",
            "patent-attorney review",
        ],
        "derivation_caveat": (
            "Every generated family here is computationally derived from a third-party sequence. "
            "Derivation from a patented sequence does not by itself create a patentable position, and the "
            "parent provenance travels with each variant. Where the parent epitope is itself claimed, "
            "point substitutions do not escape that claim."
        ),
        "legal_boundary": "Attorney-facing technical outline only; not legal advice and not a patentability or FTO conclusion.",
    }


# --------------------------------------------------------------------------- 14


def _format_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return lines


def asset_report(context: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(context["run_dir"])
    previous = context["previous"]
    binder = context["binder"]
    module = context.get("module", {})

    intake = previous.get("01_binder_intake", {})
    structural = previous.get("03_structural_analysis", {})
    engineering = previous.get("04_binder_engineering_design", {})
    families = previous.get("05_candidate_family_generation", {})
    triage = previous.get("06_binder_quality_triage", {})
    carrier_stage = previous.get("07_adc_carrier_phenotype", {})
    products = previous.get("08_adc_product_assembly", {})
    analysis = previous.get("09_adc_failure_mode_analysis", {}).get("failure_mode_analysis", {})
    selection = previous.get("10_pareto_selection", {}).get("selection", {})
    experiments = previous.get("11_experimental_design", {})

    module_ref = f"{module.get('module_id', 'antibody_binder_asset_engineering')}@{module.get('module_version', '0.3.1')}"
    decision = carrier_stage.get("modality_decision", {})

    lines = [
        f"# Antibody asset report — {binder['asset_id']}",
        "",
        f"- Binder: `{binder['binder_id']}`",
        f"- Target: `{binder['target']['gene']}` / `{binder['target']['protein']}`",
        f"- Indication: `{binder['target']['indication']}`",
        f"- GenModule: `{module_ref}`",
        f"- Run: `{run_dir.name}`",
        "",
        "## Modality decision",
        "",
    ]

    if decision.get("decision") == "stop_this_route":
        lines.extend(
            [
                "**Stop this route.** A stop condition is met.",
                "",
                decision.get("headline", ""),
            ]
        )
    elif decision.get("decision") == "modality_unproven_run_kill_experiment":
        lines.extend(
            [
                "**The ADC modality is unproven for this binder. Run the kill experiment before optimising sequence.**",
                "",
                "The engineering output below is real, but it optimises binder quality, which is not the",
                "constraint. Spending on sequence optimisation before the delivery cascade is measured",
                "optimises the wrong objective.",
                "",
                f"Continue conditions satisfied: **{decision.get('continue_conditions_met')}"
                f" of {decision.get('continue_conditions_total')}**.",
            ]
        )
    elif decision.get("decision") == "proceed_to_antibody_optimization":
        lines.append("**Proceed to antibody optimisation.** Every continue condition is satisfied.")
    else:
        lines.append("Modality decision was not evaluated in this run.")

    if analysis.get("headline"):
        lines.extend(["", "## Failure-mode position", "", analysis["headline"]])
        resolution = analysis.get("resolution", {})
        active = resolution.get("active_route_terminating_modes") or []
        if active:
            lines.extend(
                [
                    "",
                    "Route-terminating modes currently supported by evidence:",
                    "",
                ]
            )
            lines.extend(f"- `{mode_id}`" for mode_id in active)
        counts = resolution.get("counts", {})
        if counts:
            lines.extend(
                [
                    "",
                    f"Modes: **{counts.get('supported')}** supported, **{counts.get('excluded')}** excluded, "
                    f"**{counts.get('unresolved')}** unresolved, of {counts.get('total')} modelled.",
                ]
            )

    next_experiment = (analysis.get("experiment_prioritisation") or {}).get("next_experiment")
    if next_experiment:
        lines.extend(
            [
                "",
                "## Highest-information next experiment",
                "",
                f"**{next_experiment['name']}** (information gain {next_experiment['information_gain']})",
                "",
                next_experiment["detail"],
                "",
            ]
        )
        overturn = next_experiment.get("can_overturn_supported_modes") or []
        if overturn:
            lines.extend(
                [
                    "Can **overturn** the currently-blocking finding(s): "
                    + ", ".join(f"`{mode}`" for mode in overturn)
                    + ". This is why it ranks first: the evidence behind a blocking finding is often weaker",
                    "than the evidence needed to act on it, so testing it directly is worth more than",
                    "measuring anything downstream of it.",
                    "",
                ]
            )
        resolves = next_experiment.get("resolves_unresolved_modes") or []
        if resolves:
            lines.append("Also resolves: " + ", ".join(f"`{mode}`" for mode in resolves))
        blocked = (analysis.get("experiment_prioritisation") or {}).get("blocked_by_prerequisites") or []
        if blocked:
            lines.extend(
                [
                    "",
                    "Deferred until an earlier cascade step is established (a downstream fraction is",
                    "uninterpretable without its denominator):",
                    "",
                ]
            )
            lines.extend(
                f"- `{item['experiment_id']}` — needs {', '.join(item['unmet_prerequisites'])}"
                for item in blocked
            )

    lines.extend(["", "## Stage status", ""])
    lines.extend(
        _format_table(
            ["Stage", "Name", "Status"],
            [
                [f"`{stage_id}`", name, f"`{previous.get(stage_id, {}).get('status', 'not_run')}`"]
                for stage_id, name in STAGES[:-1]
            ],
        )
    )

    cascade = carrier_stage.get("delivery_cascade", {})
    if cascade.get("criteria"):
        lines.extend(
            [
                "",
                "## Track B — ADC carrier delivery cascade",
                "",
                f"Usable observations: **{cascade.get('usable_observation_count')}** of "
                f"{cascade.get('observation_count')} supplied. "
                f"Steps supported: **{cascade.get('steps_supported')}/{cascade.get('steps_total')}**.",
                "",
            ]
        )
        lines.extend(
            _format_table(
                ["Step", "Criterion", "Status", "If it fails"],
                [
                    [item["step"], f"`{item['criterion_id']}`", f"**{item['status']}**", item["failure_meaning"]]
                    for item in cascade["criteria"]
                ],
            )
        )
        carrier = carrier_stage.get("carrier_quality", {})
        if carrier.get("adc_carrier_quality_score") is None:
            lines.extend(["", f"Carrier quality: **not measurable**. {carrier.get('interpretation', '')}"])
        else:
            lines.extend(
                [
                    "",
                    f"Carrier quality: **{carrier['adc_carrier_quality_score']}** "
                    f"(coverage {carrier.get('coverage')}). {carrier.get('interpretation', '')}",
                ]
            )

    germline = intake.get("germline_summary") or {}
    if germline:
        lines.extend(["", "## Track A — sequence identity", ""])
        lines.extend(
            _format_table(
                ["Chain", "Closest human V", "Closest human J", "Framework identity", "Framework deviations"],
                [
                    [
                        chain.upper(),
                        f"`{record.get('closest_human_v_gene')}`",
                        f"`{record.get('closest_human_j_gene')}`",
                        f"{record.get('framework_identity_percent')}%",
                        record.get("framework_deviation_count"),
                    ]
                    for chain, record in sorted(germline.items())
                ],
            )
        )

    scan = structural.get("exposure_weighted_liabilities") or intake.get("liabilities") or {}
    summary = scan.get("summary") or {}
    if summary:
        basis = "exposure-weighted" if structural.get("exposure_weighted_liabilities") else "sequence-only"
        lines.extend(
            [
                "",
                f"## Track A — liability profile ({basis})",
                "",
                f"- Total flags: **{summary.get('total_hits')}**, of which **{summary.get('cdr_localised_hits')}** fall in a CDR.",
                f"- Burden score: **{summary.get('liability_burden')}** (comparative only).",
                f"- By chemical-risk tier: `{summary.get('by_chemical_risk_tier')}`.",
                "",
            ]
        )
        top_hits = sorted(
            scan.get("hits", []),
            key=lambda hit: (-(hit["chemical_risk"] * hit["functional_consequence"]), hit["chain"], hit["position"]),
        )[:10]
        lines.extend(
            _format_table(
                ["Chain", "Position", "Scheme", "Region", "Liability", "Chemical risk", "Exposure"],
                [
                    [
                        hit["chain"].upper(),
                        hit["position"],
                        f"`{hit['scheme_position']}`",
                        hit["region"],
                        hit["name"],
                        f"{hit['chemical_risk']} ({hit['chemical_risk_tier']})",
                        hit["exposure_class"],
                    ]
                    for hit in top_hits
                ],
            )
        )

    counts = engineering.get("proposal_counts") or {}
    if counts:
        lines.extend(
            [
                "",
                "## Candidates and constructs",
                "",
                f"- Sequence proposals: **{counts.get('total')}** ({counts.get('by_source')}); "
                f"**{counts.get('requiring_binding_confirmation')}** need binding confirmation.",
                f"- Sequence candidates: **{families.get('sequence_candidate_count')}** in families "
                f"{families.get('sequence_families')}.",
                f"- Construct/campaign specifications: **{families.get('construct_specification_count')}** in families "
                f"{families.get('construct_families')}.",
            ]
        )
        dual = engineering.get("dual_benefit_proposals") or []
        if dual:
            lines.extend(
                [
                    "",
                    f"**Dual-benefit substitutions ({len(dual)}):** `" + "`, `".join(dual) + "`. ",
                    "Each removes a chemical liability *and* restores the human germline residue at the same",
                    "position, improving two objectives with one change.",
                ]
            )

    ranking = triage.get("ranking") or []
    if ranking:
        lines.extend(
            [
                "",
                "## Track A — sequence computational developability rank",
                "",
                "This is a within-track pre-screen. It excludes "
                + ", ".join(triage.get("not_predicted") or [])
                + ", so it must not be read as a lead ranking.",
                "",
            ]
        )
        lines.extend(
            _format_table(
                ["Rank", "Candidate", "Score", "Muts", "Risk", "Binding check", "Fold check", "Humanness cost"],
                [
                    [
                        row["sequence_computational_developability_rank"],
                        f"`{row['candidate_id']}`",
                        row["sequence_computational_developability_score"],
                        row["mutation_count"],
                        row.get("highest_engineering_risk") or "-",
                        "yes" if row["requires_binding_confirmation"] else "no",
                        "yes" if row.get("requires_fold_confirmation") else "no",
                        "yes" if row.get("reduces_framework_humanness") else "no",
                    ]
                    for row in ranking[:8]
                ],
            )
        )
        lines.extend(
            [
                "",
                "The last four columns are not priced into the score. Liability burden carries the largest "
                "weight, so a candidate that bundles several substitutions tends to rank well even when one "
                "of them is a paratope change, a buried-core substitution, or a move away from the human "
                "germline residue. Read the flags before the rank.",
            ]
        )

    if selection:
        lines.extend(["", "## Two-track Pareto selection", "", selection.get("headline", "")])
        if selection.get("recommended_action"):
            lines.extend(["", f"Recommended action: {selection['recommended_action']}"])

    matrix = products.get("product_matrix") or {}
    if matrix.get("products"):
        risk = matrix.get("paratope_conjugation_risk", {})
        lines.extend(
            [
                "",
                "## ADC product matrix",
                "",
                f"- Product candidates enumerated: **{matrix.get('product_count')}** "
                f"({len(matrix.get('conjugation_variants_considered') or [])} conjugation chemistries).",
                f"- Buildable with current input: **{matrix.get('buildable_now_count')}**.",
            ]
        )
        if risk.get("finding"):
            lines.extend(["", f"Conjugation finding: {risk['finding']}"])
        if matrix.get("recommended_variant"):
            lines.extend([f"", f"Recommended first chemistry: `{matrix['recommended_variant']}` — {matrix.get('recommendation_basis')}"])

    critical_path = experiments.get("critical_path") or []
    if critical_path:
        lines.extend(["", "## Critical path, ordered by information gain", ""])
        lines.extend(
            _format_table(
                ["#", "Experiment", "Gain", "Ready", "Overturns / resolves", "Cost"],
                [
                    [
                        item["priority"],
                        item["assay"],
                        item["information_gain"],
                        "yes"
                        if item["ready_to_run"]
                        else f"blocked: needs {', '.join(item['unmet_prerequisites'])}",
                        ", ".join(
                            [f"**`{mode}`**" for mode in item["can_overturn"]]
                            + [f"`{mode}`" for mode in item["resolves_failure_modes"]]
                        )
                        or "-",
                        item["cost_tier"],
                    ]
                    for item in critical_path[:8]
                ],
            )
        )
        lines.append("")
        lines.append(
            "**Bold** entries are currently-blocking findings the experiment could overturn. "
            "Blocked rows are ordered after ready ones regardless of gain."
        )
        deferred = experiments.get("deferred_until_modality_resolved") or []
        if deferred:
            lines.extend(["", "Deferred until the modality decision resolves:", ""])
            lines.extend(f"- {item['assay']} — {item['why_deferred']}" for item in deferred)

    lines.extend(
        [
            "",
            "## What this report is not",
            "",
            "- No candidate has been expressed, and no binding, delivery, stability, or potency value was measured here.",
            "- Track A ranks sequences as molecules. It does not rank them for ADC use.",
            "- Carrier quality is measured, never computed, and is never inherited by a variant from its parent.",
            "- Liability flags are computational hypotheses until forced degradation and peptide mapping confirm them.",
            "- No FTO or patentability conclusion is offered, and no ADC-readiness score is emitted.",
            "",
        ]
    )

    report_path = run_dir / "asset_report.md"
    report_path.write_text("\n".join(lines) + "\n")
    return {
        "status": "complete",
        "report_path": str(report_path),
        "asset_state": "two_track_work_package_with_modality_decision",
        "modality_decision": decision.get("decision"),
        "next_experiment": (next_experiment or {}).get("experiment_id"),
        "validated_asset": False,
    }


# --------------------------------------------------------------------------- 15


def evidence_reasoning_graph(context: dict[str, Any]) -> dict[str, Any]:
    """Reify the reasoning behind the recommendation, including what it rejected.

    Every edge was already computed by stages 07 and 09 but was visible only as
    control flow, so a reviewer asking "why this experiment and not lysosomal
    trafficking" had to read the ranking function. Nothing new is inferred.
    """
    previous = context["previous"]
    failure_stage = previous.get("09_adc_failure_mode_analysis", {})
    analysis = failure_stage.get("failure_mode_analysis", {})
    phenotype_stage = previous.get("07_adc_carrier_phenotype", {})

    graph = evidence_graph.build(
        known_evidence=context["binder"].get("known_evidence") or {},
        cascade=phenotype_stage.get("delivery_cascade") or {},
        resolution=analysis.get("resolution") or {},
        gain=analysis.get("experiment_prioritisation") or {},
        decision=phenotype_stage.get("modality_decision") or {},
        confidence=failure_stage.get("evidence_confidence") or {},
    )
    return {
        "status": "complete" if graph["edges"] else "complete_with_gaps",
        "evidence_graph": graph,
        "reviewer_questions_answered": [
            "why is this criterion in this state -- follow the observation edges into it",
            "why this experiment -- see evidence_graph.why_selected",
            "why not the others -- see evidence_graph.rejected_alternatives, one entry each",
            "what is unsupported -- see evidence_graph.hypotheses_without_observations",
        ],
        "hypotheses_without_observations_count": len(graph["hypotheses_without_observations"]),
        "boundary": graph["boundary"],
    }


# --------------------------------------------------------------------------- 16


def cross_asset_retrieval(context: dict[str, Any]) -> dict[str, Any]:
    """Nearest clinical ADC comparators by declared attributes, and how they differ."""
    root = _adc_corpus_root(context)
    corpus = (
        cross_asset.load_cases(root)
        if root
        else {
            "status": "unavailable",
            "detail": (
                "no ADC comparator corpus configured; set ADC_REFERENCE_ROOT or the "
                "source_root in configs/historical_adc_benchmark.yaml"
            ),
            "cases": [],
            "coverage": {},
        }
    )
    retrieval = cross_asset.retrieve(context["binder"], corpus)
    return {
        "status": "complete" if retrieval.get("comparators") else "complete_with_gaps",
        "retrieval": retrieval,
        "why_this_layer": (
            "An asset analysed alone cannot answer what else looked like this and what happened "
            "to it. The differing attributes matter more than the similarity score: they are "
            "exactly what a comparator cannot transfer."
        ),
        "boundary": retrieval.get("boundary", "No corpus available, so no comparator claim is made."),
    }


STAGE_FUNCTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "01_binder_intake": binder_intake,
    "02_ip_fto_landscape": ip_fto_landscape,
    "03_structural_analysis": structural_analysis,
    "04_binder_engineering_design": binder_engineering_design,
    "05_candidate_family_generation": candidate_family_generation,
    "06_binder_quality_triage": binder_quality_triage,
    "07_adc_carrier_phenotype": adc_carrier_phenotype,
    "08_adc_product_assembly": adc_product_assembly,
    "09_adc_failure_mode_analysis": adc_failure_mode_analysis,
    "10_pareto_selection": pareto_selection,
    "11_experimental_design": experimental_design,
    "12_active_learning": active_learning,
    "13_patent_package": patent_package,
    "14_asset_report": asset_report,
    "15_evidence_graph": evidence_reasoning_graph,
    "16_cross_asset_retrieval": cross_asset_retrieval,
}

# The declared catalogue is also the execution order in 0.3.0. The 0.2.0
# out-of-order case (ADC readiness before experimental design) is resolved
# structurally: the phenotype and failure-mode stages simply come earlier.
EXECUTION_ORDER = tuple(stage_id for stage_id, _ in STAGES)


def write_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))
