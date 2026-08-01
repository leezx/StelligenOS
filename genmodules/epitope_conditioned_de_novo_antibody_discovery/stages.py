"""Built-in stages for epitope_conditioned_de_novo_antibody_discovery@0.1.0."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from typing import Any, Callable
import re

import yaml


STAGES = (
    ("01_target_biology", "Target biology"),
    ("02_antigen_engineering", "Antigen engineering"),
    ("03_epitope_engineering", "Epitope engineering"),
    ("04_ip_fto_epitope_selection", "IP/FTO-guided epitope selection"),
    ("05_structural_preparation", "Structural preparation"),
    ("06_negative_design", "Negative design"),
    ("07_de_novo_antibody_design", "Epitope-conditioned de novo antibody design"),
    ("08_computational_ranking", "Multi-objective computational ranking"),
    ("09_asset_diversity_optimization", "Asset-diversity optimization"),
    ("10_focused_wet_lab_design", "Focused wet-lab design"),
    ("11_structural_validation", "Structural validation"),
    ("12_affinity_maturation", "Affinity maturation"),
    ("13_adc_readiness", "ADC-readiness evaluation"),
    ("14_patent_package", "Patent package"),
    ("15_asset_report", "Asset report"),
)

VALID_AA = set("ACDEFGHIKLMNPQRSTVWYX")


def normalized_sequence(value: Any) -> str:
    return "".join(str(value or "").split()).upper()


def validate_discovery(payload: dict[str, Any]) -> dict[str, Any]:
    required = ("asset_id", "discovery_id", "target", "antigen_construct", "epitope", "antibody")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Missing required discovery fields: {', '.join(missing)}")
    target = payload["target"]
    if not isinstance(target, dict) or not all(target.get(field) for field in ("gene", "protein", "indication")):
        raise ValueError("target.gene, target.protein, and target.indication are required")
    sequence = normalized_sequence(target.get("antigen_sequence"))
    invalid = sorted(set(sequence) - VALID_AA)
    if sequence and invalid:
        raise ValueError(f"target.antigen_sequence contains invalid amino-acid codes: {invalid}")
    epitope = payload["epitope"]
    positions = epitope.get("residue_positions", [])
    if positions and (
        not isinstance(positions, list)
        or any(not isinstance(position, int) or isinstance(position, bool) or position < 1 for position in positions)
    ):
        raise ValueError("epitope.residue_positions must be positive integers")
    positions = sorted(set(positions))
    if not positions and not epitope.get("description"):
        raise ValueError("Provide epitope.residue_positions or epitope.description")
    if sequence and positions and positions[-1] > len(sequence):
        raise ValueError("epitope residue position exceeds target.antigen_sequence length")
    construct = payload["antigen_construct"]
    start, end = construct.get("residue_start"), construct.get("residue_end")
    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
        raise ValueError("antigen_construct residue_start/residue_end are invalid")
    if sequence and end > len(sequence):
        raise ValueError("antigen construct exceeds target.antigen_sequence length")
    if positions and any(position < start or position > end for position in positions):
        raise ValueError("epitope residues must lie inside the antigen construct")
    normalized = dict(payload)
    normalized["target"] = dict(target) | {"antigen_sequence": sequence or None}
    normalized["epitope"] = dict(epitope) | {"residue_positions": positions}
    return normalized


def _sequence_features(sequence: str) -> dict[str, Any]:
    counts = Counter(sequence)
    return {
        "length": len(sequence),
        "sha256": sha256(sequence.encode()).hexdigest(),
        "unknown_residue_count": counts["X"],
        "n_linked_glycosylation_motifs": [match.group() for match in re.finditer(r"N[^P][ST]", sequence)],
        "methionine_count": counts["M"],
        "unpaired_cysteine_flag_count": counts["C"] % 2,
        "charge_proxy": counts["K"] + counts["R"] - counts["D"] - counts["E"],
        "long_hydrophobic_stretches": [match.group() for match in re.finditer(r"[AILMFWVY]{5,}", sequence)],
    }


def _availability(context: dict[str, Any], tool_ids: list[str]) -> dict[str, str]:
    tools = context["software_status"]["tools"]
    return {tool_id: tools.get(tool_id, {}).get("status", "not_declared") for tool_id in tool_ids}


def _epitope_audit(discovery: dict[str, Any]) -> dict[str, Any]:
    target_sequence = discovery["target"].get("antigen_sequence")
    positions = discovery["epitope"].get("residue_positions", [])
    residues = None
    if target_sequence and positions:
        residues = "".join(target_sequence[position - 1] for position in positions)
    ranges = []
    if positions:
        start = previous = positions[0]
        for position in positions[1:]:
            if position != previous + 1:
                ranges.append([start, previous])
                start = position
            previous = position
        ranges.append([start, previous])
    return {
        "epitope_id": discovery["epitope"]["epitope_id"],
        "sequence_version": discovery["target"].get("sequence_version"),
        "residue_positions": positions,
        "residue_ranges": ranges,
        "epitope_sequence": residues,
        "desired_function": discovery["epitope"].get("desired_function"),
        "conformation": discovery["epitope"].get("conformation"),
        "membrane_relationship": discovery["epitope"].get("membrane_relationship"),
    }


def target_biology(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    known = discovery.get("known_evidence", {})
    fields = {
        "target_biology": known.get("target_biology"),
        "normal_tissue": known.get("normal_tissue"),
        "surface_availability": known.get("surface_availability"),
        "internalization": known.get("internalization"),
        "known_therapeutics": known.get("known_therapeutics"),
        "known_adcs": known.get("known_adcs"),
        "resistance": known.get("resistance"),
        "biomarkers": known.get("biomarkers"),
    }
    return {
        "status": "complete_with_gaps",
        "target": {
            "gene": discovery["target"]["gene"],
            "protein": discovery["target"]["protein"],
            "indication": discovery["target"]["indication"],
            "accession": discovery["target"].get("accession"),
            "sequence_version": discovery["target"].get("sequence_version"),
        },
        "evidence": fields,
        "evidence_gaps": [name for name, value in fields.items() if not value],
        "required_data": [
            "target_sequence_reference",
            "therapeutic_antibody_reference",
            "normal_tissue_atlas",
            "adc_reference",
        ],
    }


def antigen_engineering(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    sequence = discovery["target"].get("antigen_sequence")
    construct = discovery["antigen_construct"]
    construct_sequence = None
    if sequence:
        construct_sequence = sequence[construct["residue_start"] - 1 : construct["residue_end"]]
    return {
        "status": "complete_with_gaps",
        "construct": construct,
        "full_sequence": None if not sequence else _sequence_features(sequence),
        "construct_sequence": construct_sequence,
        "construct_sequence_audit": None if not construct_sequence else _sequence_features(construct_sequence),
        "unresolved": [
            item
            for item, value in {
                "experimental construct expression": construct.get("expression_evidence"),
                "oligomeric-state validation": construct.get("oligomeric_state_validation"),
                "glycosylation-state validation": construct.get("glycosylation_state_validation"),
                "native membrane orientation": construct.get("native_orientation_evidence"),
            }.items()
            if not value
        ],
        "boundary": "Sequence slicing does not establish a native, folded, or discovery-ready antigen.",
    }


def epitope_engineering(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    audit = _epitope_audit(discovery)
    gaps = []
    if not audit["residue_positions"]:
        gaps.append("residue-resolved epitope definition")
    if not discovery.get("known_evidence", {}).get("target_structure"):
        gaps.append("structure-bound epitope coordinates")
    gaps.extend(["native-cell accessibility", "glycan accessibility", "functional epitope validation"])
    return {
        "status": "complete_with_gaps",
        "epitope": audit,
        "positive_objectives": discovery.get("positive_objectives", []),
        "candidate_epitopes": [audit],
        "ranking": None,
        "evidence_gaps": gaps,
        "boundary": "User-defined residue identity is preserved; no epitope rank or accessibility is invented.",
    }


def ip_fto_epitope_selection(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    target = discovery["target"]
    epitope = _epitope_audit(discovery)
    return {
        "status": "complete_with_gaps",
        "search_scopes": [
            {"scope": "target and residue-defined epitope", "inputs": [target["gene"], target["protein"], epitope]},
            {"scope": "competition and functional claims", "inputs": [discovery["epitope"].get("desired_function")]},
            {"scope": "known antibody sequences and families", "inputs": ["competitor antibodies", "therapeutic references"]},
            {"scope": "ADC composition/use claims", "inputs": [target["protein"], target["indication"]]},
            {"scope": "design-method/tool claims", "inputs": ["configured generation methods"]},
        ],
        "software": _availability(context, ["blast_plus", "mmseqs2"]),
        "scores": {
            "epitope_freedom_score": None,
            "patent_opportunity_score": None,
            "commercial_opportunity_score": None,
        },
        "required_outputs": [
            "epitope claim map",
            "competitor pose/competition map",
            "sequence neighborhood report",
            "design-around constraints",
            "external-counsel review",
        ],
        "legal_boundary": "Technical search plan only; not an FTO or patentability opinion.",
    }


def structural_preparation(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    return {
        "status": "complete_with_gaps",
        "epitope": _epitope_audit(discovery),
        "supplied_structure": discovery.get("known_evidence", {}).get("target_structure"),
        "software": _availability(context, ["pdbfixer", "openmm", "freesasa", "openfold"]),
        "preparation_tasks": [
            "select one exact antigen construct and sequence version",
            "assemble experimental/predicted conformational ensemble",
            "restore unresolved residues only with explicit provenance",
            "retain glycans and membrane orientation relevant to the epitope",
            "map epitope residues into every structure",
            "define hotspot, allowed-contact, and forbidden-contact residue sets",
            "record structure confidence and model limitations",
        ],
        "design_ready": False,
        "required_outputs": [
            "cleaned versioned structure ensemble",
            "epitope/hotspot map",
            "glycan and membrane-context map",
            "structure/model checksums",
        ],
    }


def negative_design(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    defaults = [
        "avoid known patented/competitor epitope contacts",
        "avoid normal-tissue-high conformations",
        "avoid glycan-only or glycan-dependent binding",
        "avoid nonspecific, polyreactive, or highly hydrophobic paratopes",
        "avoid predicted agonistic geometry",
        "avoid inaccessible membrane-facing approaches",
        "avoid framework/CDR liabilities unsupported by rescue evidence",
    ]
    supplied = discovery.get("negative_constraints", [])
    constraints = list(dict.fromkeys([*supplied, *defaults]))
    return {
        "status": "complete_with_gaps",
        "negative_constraints": constraints,
        "machine_resolved_constraints": [],
        "evidence_required": [
            "competitor epitope map",
            "normal-tissue conformational evidence",
            "glycosylated antigen structure/assay",
            "cell-context specificity and agonism assays",
        ],
        "boundary": "Text constraints are frozen but cannot become geometric masks until supporting evidence is supplied.",
    }


def de_novo_antibody_design(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    candidates = []
    for index, candidate in enumerate(discovery.get("known_evidence", {}).get("designed_candidates", []), start=1):
        candidates.append(
            {
                "candidate_id": candidate.get("candidate_id", f"{discovery['discovery_id']}-DESIGN-{index:04d}"),
                "family": candidate.get("family"),
                "format": candidate.get("format", discovery["antibody"]["preferred_format"]),
                "vh": normalized_sequence(candidate.get("vh")) or None,
                "vl": normalized_sequence(candidate.get("vl")) or None,
                "predicted_epitope_positions": sorted(set(candidate.get("predicted_epitope_positions", []))),
                "predicted_binding_pose": candidate.get("predicted_binding_pose"),
                "generation_record": candidate.get("generation_record"),
            }
        )
    return {
        "status": "complete_with_gaps",
        "software": _availability(
            context, ["rfantibody", "rfdiffusion", "proteinmpnn", "ligandmpnn", "anarci", "abnumber"]
        ),
        "input_epitope": _epitope_audit(discovery),
        "antibody_policy": discovery["antibody"],
        "generated_candidates": candidates,
        "candidate_count": len(candidates),
        "required_generation_record": [
            "tool repository commit",
            "weight checksum",
            "input structure checksum",
            "hotspot and negative masks",
            "random seed and sampling settings",
            "raw unfiltered outputs",
        ],
        "boundary": "No sequence is generated by the built-in module; configure a versioned external adapter.",
    }


def computational_ranking(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    desired = set(discovery["epitope"].get("residue_positions", []))
    candidates = context["previous"]["07_de_novo_antibody_design"]["generated_candidates"]
    rows = []
    for candidate in candidates:
        predicted = set(candidate.get("predicted_epitope_positions", []))
        union = desired | predicted
        overlap = None if not union else round(len(desired & predicted) / len(union), 4)
        chain_features = {
            name: _sequence_features(sequence)
            for name, sequence in (("vh", candidate.get("vh")), ("vl", candidate.get("vl")))
            if sequence
        }
        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "family": candidate.get("family"),
                "sequence_flags": chain_features,
                "predicted_epitope_jaccard": overlap,
                "binding_energy": None,
                "shape_complementarity": None,
                "buried_surface": None,
                "humanness": None,
                "immunogenicity": None,
                "polyreactivity": None,
                "expression": None,
                "fto_risk": None,
            }
        )
    return {
        "status": "complete_with_gaps",
        "candidate_features": rows,
        "software": _availability(
            context, ["freesasa", "immune_builder", "igfold", "esm", "rosetta", "foldx", "pandas"]
        ),
        "pareto_front": None,
        "ranking_boundary": "Predicted pose overlap is not experimental epitope confirmation; no scalar rank is emitted.",
    }


def _paired_sequence(candidate: dict[str, Any]) -> str:
    return f"{candidate.get('vh') or ''}|{candidate.get('vl') or ''}"


def _identity(left: str, right: str) -> float:
    length = max(len(left), len(right))
    return 1.0 if length == 0 else round(sum(a == b for a, b in zip(left, right)) / length, 4)


def asset_diversity_optimization(context: dict[str, Any]) -> dict[str, Any]:
    candidates = context["previous"]["07_de_novo_antibody_design"]["generated_candidates"]
    pairwise = []
    for left, right in combinations(candidates, 2):
        pairwise.append(
            {
                "candidate_a": left["candidate_id"],
                "candidate_b": right["candidate_id"],
                "raw_paired_sequence_identity": _identity(_paired_sequence(left), _paired_sequence(right)),
            }
        )
    return {
        "status": "complete_with_gaps",
        "family_archetypes": [
            {"family": "A", "objective": "high-affinity blocking"},
            {"family": "B", "objective": "moderate-affinity high-internalization"},
            {"family": "C", "objective": "membrane-proximal ADC geometry"},
            {"family": "D", "objective": "bispecific-format compatibility"},
            {"family": "E", "objective": "maximum IP/FTO separation"},
        ],
        "observed_candidate_count": len(candidates),
        "pairwise_sequence_identity": pairwise,
        "family_assignments": None,
        "diversity_requirements": [
            "different germline/framework",
            "different HCDR3",
            "different paratope",
            "different predicted pose",
            "different or partially shifted epitope where allowed",
            "independent backup sequence",
        ],
        "boundary": "Sequence identity alone does not establish independent binding pose, epitope, function, or IP family.",
    }


def focused_wet_lab_design(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "complete_with_gaps",
        "minimum_package": [
            {"priority": 1, "assay": "small-scale expression, SEC, and identity", "decision": "remove nonexpressing/aggregated designs"},
            {"priority": 1, "assay": "SPR or BLI against designed construct", "decision": "confirm direct binding and kinetics"},
            {"priority": 1, "assay": "native-cell binding with knockout/negative controls", "decision": "confirm target-dependent cell-context binding"},
            {"priority": 1, "assay": "epitope competition and residue-mutant panel", "decision": "test specified epitope"},
            {"priority": 2, "assay": "internalization time course", "decision": "measure uptake and family differences"},
            {"priority": 2, "assay": "lysosomal colocalization", "decision": "confirm productive trafficking"},
            {"priority": 2, "assay": "polyreactivity and nonspecific-binding panel", "decision": "test negative design"},
            {"priority": 3, "assay": "small focused rescue/maturation library", "decision": "only after confirmed binders"},
        ],
        "required_controls": [
            "irrelevant isotype",
            "target-negative or knockout cells",
            "known competing and noncompeting antibodies when lawful",
            "wild-type and epitope-mutant antigen",
            "glycosylated and controlled deglycosylated antigen where relevant",
        ],
        "cost_and_timeline": "To be supplied by the selected laboratory or CRO.",
    }


def structural_validation(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "complete_with_gaps",
        "validation_ladder": [
            {"method": "competition and mutagenesis", "role": "fast epitope localization"},
            {"method": "HDX-MS or crosslinking-MS", "role": "regional interface evidence"},
            {"method": "cryo-EM or crystallography", "role": "residue-level pose validation"},
            {"method": "prediction-to-experiment comparison", "role": "model error audit"},
        ],
        "binding_pose_confidence": None,
        "epitope_confirmed": False,
        "boundary": "Predicted structures cannot satisfy structural validation.",
    }


def affinity_maturation(context: dict[str, Any]) -> dict[str, Any]:
    experimental = context["discovery"].get("known_evidence", {}).get("experimental_binders", [])
    eligible = [
        binder
        for binder in experimental
        if binder.get("target_binding_confirmed") is True and binder.get("epitope_confirmed") is True
    ]
    return {
        "status": "complete_with_gaps",
        "maturation_allowed": bool(eligible),
        "eligible_binders": [binder.get("candidate_id") for binder in eligible],
        "required_before_maturation": [
            "QC-passed target binding",
            "specified-epitope confirmation",
            "developability baseline",
            "protected contact and negative-design residues",
        ],
        "strategy": None if not eligible else "small focused libraries plus active learning; preserve independent families",
        "software": _availability(context, ["rosetta", "foldx", "scikit_learn", "optuna"]),
    }


def adc_readiness(context: dict[str, Any]) -> dict[str, Any]:
    known = context["discovery"].get("known_evidence", {})
    evidence = {
        "native_cell_binding": known.get("cell_binding"),
        "epitope_accessibility": known.get("epitope_accessibility"),
        "internalization": known.get("internalization"),
        "lysosomal_trafficking": known.get("lysosomal_trafficking"),
        "membrane_orientation": known.get("membrane_orientation"),
        "glycosylation_effect": known.get("glycosylation_effect"),
        "normal_tissue_risk": known.get("normal_tissue_risk"),
        "conjugation_compatibility": known.get("conjugation_compatibility"),
    }
    return {
        "status": "complete_with_gaps",
        "evidence": evidence,
        "evidence_gaps": [name for name, value in evidence.items() if not value],
        "adc_readiness_score": None,
        "boundary": "ADC readiness remains a downstream Gate evaluation, not a prediction from sequence or pose alone.",
    }


def patent_package(context: dict[str, Any]) -> dict[str, Any]:
    discovery = context["discovery"]
    return {
        "status": "complete_with_gaps",
        "package_sections": [
            "target, antigen construct, and specified epitope",
            "representative antibodies and independent sequence families",
            "predicted and experimentally resolved binding modes",
            "epitope competition and mutagenesis evidence",
            "functional, developability, and ADC evidence",
            "negative-design constraints and unexpected effects",
            "known prior art and unresolved FTO risks",
            "inventor and AI-tool contribution record",
        ],
        "representative_asset": discovery["asset_id"],
        "software": _availability(context, ["blast_plus", "mmseqs2", "jinja2"]),
        "missing": [
            "generated and tested independent families",
            "completed patent/claim searches",
            "experimental epitope evidence",
            "comparative functional evidence",
            "patent-attorney review",
        ],
        "legal_boundary": "Attorney-facing technical outline only; not legal advice or a patentability/FTO conclusion.",
    }


def asset_report(context: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(context["run_dir"])
    discovery = context["discovery"]
    previous = context["previous"]
    rows = [
        (stage_id, name, previous.get(stage_id, {}).get("status", "not_run"))
        for stage_id, name in STAGES[:-1]
    ]
    lines = [
        f"# Epitope-conditioned antibody asset report — {discovery['asset_id']}",
        "",
        f"- Discovery: `{discovery['discovery_id']}`",
        f"- Target: `{discovery['target']['gene']}` / `{discovery['target']['protein']}`",
        f"- Epitope: `{discovery['epitope']['epitope_id']}`",
        f"- GenModule: `epitope_conditioned_de_novo_antibody_discovery@0.1.0`",
        "",
        "## Stage status",
        "",
        "| Stage | Name | Status |",
        "|---|---|---|",
    ]
    lines.extend(f"| `{stage_id}` | {name} | `{status}` |" for stage_id, name, status in rows)
    lines.extend(
        [
            "",
            "## Current conclusion",
            "",
            "The antigen and specified epitope now have a versioned discovery work package.",
            "No de novo antibody sequence, validated binder, epitope confirmation, FTO conclusion, or ADC-ready lead is claimed.",
            "",
            "## Immediate next actions",
            "",
            "1. Replace demonstration input with a versioned real target sequence, construct, structure, and epitope.",
            "2. Complete target/normal-tissue and epitope IP/FTO evidence.",
            "3. Install RFantibody on a Linux NVIDIA environment and register exact weights.",
            "4. Generate a small pilot batch and retain all raw designs.",
            "5. Select diverse families only after computational and focused experimental evidence.",
        ]
    )
    report_path = run_dir / "asset_report.md"
    report_path.write_text("\n".join(lines) + "\n")
    return {
        "status": "complete_with_gaps",
        "report_path": str(report_path),
        "asset_state": "epitope_conditioned_discovery_work_package_initialized",
        "validated_asset": False,
    }


STAGE_FUNCTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "01_target_biology": target_biology,
    "02_antigen_engineering": antigen_engineering,
    "03_epitope_engineering": epitope_engineering,
    "04_ip_fto_epitope_selection": ip_fto_epitope_selection,
    "05_structural_preparation": structural_preparation,
    "06_negative_design": negative_design,
    "07_de_novo_antibody_design": de_novo_antibody_design,
    "08_computational_ranking": computational_ranking,
    "09_asset_diversity_optimization": asset_diversity_optimization,
    "10_focused_wet_lab_design": focused_wet_lab_design,
    "11_structural_validation": structural_validation,
    "12_affinity_maturation": affinity_maturation,
    "13_adc_readiness": adc_readiness,
    "14_patent_package": patent_package,
    "15_asset_report": asset_report,
}


def write_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))
