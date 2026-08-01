"""Track A: binder-quality triage over generated candidate sequences.

What this ranking is: a comparison of candidate *sequences* on axes actually
computed from sequence and structure.

What it is not: a prediction of which candidate is the better drug, and not a
ranking for ADC use. Target binding, expression titre, thermal stability,
immunogenicity, and payload delivery are not computed here, and no weighting of
the axes below can substitute for them.

The emitted field is named ``sequence_computational_developability_score`` rather
than ``developability_score``. The longer name is deliberate: v0.2.0's short name
invited readers to treat the top-ranked row as the best candidate overall, which
it is not. Carrier capability is a separate, measured axis handled by
``lib.phenotype``, and the two are combined only by Pareto dominance in
``lib.pareto`` — never by summing them into one number, because that would let a
clean sequence compensate for a molecule that does not deliver payload.
"""

from __future__ import annotations

from typing import Any

from lib import biophysics, liabilities

# Axis direction: "lower_is_better" or "higher_is_better". Weights are declared
# here and echoed into the run output so a reviewer sees what produced the rank.
DEFAULT_POLICY = {
    "policy_id": "binder_sequence_computational_developability",
    "policy_version": "0.3.0",
    "axes": {
        "liability_burden": {"weight": 0.35, "direction": "lower_is_better"},
        "cdr_liability_count": {"weight": 0.15, "direction": "lower_is_better"},
        "framework_humanness": {"weight": 0.20, "direction": "higher_is_better"},
        "charge_deviation": {"weight": 0.10, "direction": "lower_is_better"},
        "hydrophobicity": {"weight": 0.10, "direction": "lower_is_better"},
        "parent_distance": {"weight": 0.10, "direction": "lower_is_better"},
    },
    "excluded_axes": [
        "target binding and affinity",
        "expression titre",
        "thermal and colloidal stability",
        "immunogenicity",
        "internalisation and payload delivery",
    ],
    "reference_net_charge_at_ph_7_4": 4.0,
}


def _axis_values(
    candidate: dict[str, Any],
    scan: dict[str, Any],
    humanness: float | None,
    policy: dict[str, Any],
) -> dict[str, float | None]:
    chains = {"vh": candidate["vh"], "vl": candidate.get("vl")}
    joined = (candidate["vh"] or "") + (candidate.get("vl") or "")
    summary = scan["summary"]
    net_charge = biophysics.net_charge_at_ph(joined, 7.4)
    reference = policy.get("reference_net_charge_at_ph_7_4", 4.0)
    return {
        "liability_burden": summary["liability_burden"],
        "cdr_liability_count": float(summary["cdr_localised_hits"]),
        "framework_humanness": humanness,
        "charge_deviation": round(abs(net_charge - reference), 3),
        "hydrophobicity": biophysics.gravy(joined),
        "parent_distance": float(candidate.get("mutation_count", 0)),
        "_net_charge_at_ph_7_4": round(net_charge, 2),
        "_isoelectric_point": biophysics.isoelectric_point(joined),
        "_hydrophobic_window_count": float(
            sum(len(biophysics.hydrophobic_windows(sequence or "")) for sequence in chains.values())
        ),
    }


def _normalize(values: list[float | None], direction: str) -> list[float | None]:
    """Min-max normalise to [0, 1] where 1 is always the better end."""
    present = [value for value in values if value is not None]
    if not present:
        return [None] * len(values)
    low, high = min(present), max(present)
    if high == low:
        return [None if value is None else 1.0 for value in values]
    normalized: list[float | None] = []
    for value in values:
        if value is None:
            normalized.append(None)
            continue
        scaled = (value - low) / (high - low)
        normalized.append(round(1.0 - scaled if direction == "lower_is_better" else scaled, 4))
    return normalized


def framework_identity(chains: dict[str, str | None], germline: dict[str, dict[str, Any]]) -> float | None:
    """Exact pooled framework identity to the closest human germline V genes.

    Recomputed from the candidate's own residues at every framework position that
    was compared for the parent, so a substitution that moves *away* from germline
    lowers the value just as a reversion raises it. Pooled across chains by
    position count rather than averaged per chain, so a short chain does not carry
    the same weight as a long one.
    """
    matched = total = 0
    for chain, record in germline.items():
        sequence = chains.get(chain)
        reference = record.get("framework_germline_residues") or {}
        if not sequence or not reference:
            continue
        for position, germline_residue in reference.items():
            index = int(position)
            if not 1 <= index <= len(sequence):
                continue
            total += 1
            matched += sequence[index - 1] == germline_residue
    if not total:
        return None
    return round(100 * matched / total, 2)


def triage(
    candidates: list[dict[str, Any]],
    position_maps: dict[str, dict[int, dict[str, Any]]] | None = None,
    exposure: dict[str, dict[int, float]] | None = None,
    germline: dict[str, dict[str, Any]] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score, normalise, and rank every candidate."""
    policy = policy or DEFAULT_POLICY
    position_maps = position_maps or {}
    exposure = exposure or {}
    germline = germline or {}

    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        chains = {"vh": candidate["vh"], "vl": candidate.get("vl")}
        scan = liabilities.scan_binder(
            {name: sequence for name, sequence in chains.items() if sequence}, position_maps, exposure
        )
        candidate_humanness = framework_identity(chains, germline)
        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "family": candidate["family"],
                "mutation_count": candidate.get("mutation_count", 0),
                "mutations": [mutation["substitution"] for mutation in candidate.get("mutations", [])],
                "axes": _axis_values(candidate, scan, candidate_humanness, policy),
                "liability_summary": scan["summary"],
                "requires_binding_confirmation": candidate.get("requires_binding_confirmation", False),
                # The score cannot express these, so they travel beside it. A rank is
                # a comparison of computed descriptors, not a recommendation, and a
                # top-ranked row that needs an affinity remeasurement, a fold check,
                # or costs framework identity has to say so in the same table.
                "requires_fold_confirmation": candidate.get("requires_fold_confirmation", False),
                "reduces_framework_humanness": candidate.get("reduces_framework_humanness", False),
                "highest_engineering_risk": candidate.get("highest_engineering_risk"),
            }
        )

    axis_names = list(policy["axes"])
    normalized: dict[str, list[float | None]] = {}
    for axis in axis_names:
        normalized[axis] = _normalize(
            [row["axes"].get(axis) for row in rows], policy["axes"][axis]["direction"]
        )

    for index, row in enumerate(rows):
        contributions: dict[str, Any] = {}
        total = weight_used = 0.0
        for axis in axis_names:
            value = normalized[axis][index]
            weight = policy["axes"][axis]["weight"]
            contributions[axis] = {
                "raw": row["axes"].get(axis),
                "normalized": value,
                "weight": weight,
            }
            if value is not None:
                total += value * weight
                weight_used += weight
        row["axis_detail"] = contributions
        row["sequence_computational_developability_score"] = round(total / weight_used, 4) if weight_used else None
        row["score_coverage"] = round(weight_used / sum(policy["axes"][axis]["weight"] for axis in axis_names), 3)

    ranked = sorted(
        rows,
        key=lambda row: (-(row["sequence_computational_developability_score"] or -1.0), row["candidate_id"]),
    )
    for rank, row in enumerate(ranked, start=1):
        row["sequence_computational_developability_rank"] = rank

    parent = next((row for row in ranked if row["family"] == "parent"), None)
    improved = [
        row["candidate_id"]
        for row in ranked
        if parent
        and row["sequence_computational_developability_score"] is not None
        and parent["sequence_computational_developability_score"] is not None
        and row["sequence_computational_developability_score"] > parent["sequence_computational_developability_score"]
    ]

    return {
        "policy": policy,
        "candidates_scored": len(ranked),
        "ranking": ranked,
        "parent_candidate_id": parent["candidate_id"] if parent else None,
        "parent_sequence_developability_score": parent["sequence_computational_developability_score"] if parent else None,
        "candidates_scoring_above_parent": improved,
        "humanness_note": (
            "Candidate framework identity is recomputed exactly from each candidate's own residues at the "
            "framework positions compared for the parent, against the same closest human germline V genes."
        ),
        "method": "min_max_normalised_weighted_sum_over_computed_axes",
        "comparability": (
            "Axes are min-max normalised across the candidates in this run, so a score is meaningful only "
            "relative to the other candidates here. Scores are not comparable between runs or between "
            "candidate sets, and the absolute value carries no units."
        ),
        "boundary": (
            "A developability ranking over computed descriptors only. It excludes binding, expression, "
            "stability, and immunogenicity, so it must not be read as an overall candidate ranking or "
            "used to promote a candidate without assay data."
        ),
    }
