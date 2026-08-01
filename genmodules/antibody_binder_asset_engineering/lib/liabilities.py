"""Position-resolved chemical and sequence liability scan.

Three properties distinguish this from a motif count:

1. Overlap safety. Each rule matches its *reactive* residue with a lookahead for
   the sequence context, so adjacent and overlapping motifs are all reported
   rather than consumed by a previous non-overlapping match.
2. Position and region. Every hit carries a linear position, the numbering-scheme
   position, and the framework/CDR region it falls in.
3. Separated risk axes. ``chemical_risk`` is how likely the chemistry is to
   happen. ``functional_consequence`` is how much it matters if it does.
   ``remediation_risk`` is how dangerous it is to engineer the site away. Folding
   these into one number hides the trade-off the designer has to make.

Solvent exposure, when a structure is available, scales ``chemical_risk`` only.
A buried methionine is still a methionine; it is simply much less likely to
oxidise.
"""

from __future__ import annotations

import re
from typing import Any

# Motif rules. Each pattern matches exactly the reactive residue; the lookahead
# carries the sequence context. Severities are ordinal tiers, not probabilities.
LIABILITY_RULES: tuple[dict[str, Any], ...] = (
    {
        "id": "deamidation_NG",
        "name": "Asn deamidation (NG)",
        "pattern": r"N(?=G)",
        "residue": "N",
        "chemical_severity": 3,
        "mechanism": "Succinimide-mediated deamidation to iso-Asp; fastest in the NG context.",
        "remediation": ("N->Q", "G+1->A"),
    },
    {
        "id": "deamidation_NS_NT",
        "name": "Asn deamidation (NS/NT)",
        "pattern": r"N(?=[ST])",
        "residue": "N",
        "chemical_severity": 2,
        "mechanism": "Deamidation at a moderately permissive n+1 residue.",
        "remediation": ("N->Q",),
    },
    {
        "id": "deamidation_weak_context",
        "name": "Asn deamidation (weak context)",
        "pattern": r"N(?=[NHAD])",
        "residue": "N",
        "chemical_severity": 1,
        "mechanism": "Deamidation possible but slow in this n+1 context.",
        "remediation": ("N->Q",),
    },
    {
        "id": "isomerization_DG",
        "name": "Asp isomerization (DG)",
        "pattern": r"D(?=G)",
        "residue": "D",
        "chemical_severity": 3,
        "mechanism": "Succinimide formation and iso-Asp accumulation; also a fragmentation site.",
        "remediation": ("D->E", "G+1->A"),
    },
    {
        "id": "isomerization_DS_DT_DD",
        "name": "Asp isomerization (DS/DT/DD)",
        "pattern": r"D(?=[STD])",
        "residue": "D",
        "chemical_severity": 2,
        "mechanism": "Slower Asp isomerization at a permissive n+1 residue.",
        "remediation": ("D->E",),
    },
    {
        "id": "hydrolysis_DP",
        "name": "Asp-Pro acid-labile bond",
        "pattern": r"D(?=P)",
        "residue": "D",
        "chemical_severity": 2,
        "mechanism": "Acid-labile Asp-Pro bond; backbone cleavage under low-pH hold or elution.",
        "remediation": ("D->E",),
    },
    {
        "id": "oxidation_M",
        "name": "Met oxidation",
        "pattern": r"M",
        "residue": "M",
        "chemical_severity": 2,
        "mechanism": "Methionine sulfoxide formation; strongly solvent-exposure dependent.",
        "remediation": ("M->L", "M->F", "M->V"),
    },
    {
        "id": "oxidation_W",
        "name": "Trp oxidation",
        "pattern": r"W",
        "residue": "W",
        "chemical_severity": 2,
        "mechanism": "Trp oxidation to kynurenine/hydroxytryptophan under light or peroxide stress.",
        "remediation": ("W->F", "W->Y"),
    },
    {
        "id": "n_glycosylation_sequon",
        "name": "N-linked glycosylation sequon",
        "pattern": r"N(?=[^P][ST])",
        "residue": "N",
        "chemical_severity": 3,
        "mechanism": "N-X-S/T sequon; variable-domain occupancy creates glycoform heterogeneity.",
        "remediation": ("N->Q", "S/T+2->A"),
    },
    {
        "id": "glycation_K",
        "name": "Lys glycation-prone context",
        "pattern": r"K(?=[DE])",
        "residue": "K",
        "chemical_severity": 1,
        "mechanism": "Acidic neighbour catalyses Lys glycation in reducing-sugar formulations.",
        "remediation": (),
    },
    {
        "id": "integrin_motif_RGD",
        "name": "Integrin-binding RGD motif",
        "pattern": r"R(?=GD)",
        "residue": "R",
        "chemical_severity": 1,
        "mechanism": "RGD can confer integrin binding and off-target cell adhesion.",
        "remediation": (),
    },
)

# How much a liability matters if the chemistry happens, by region.
FUNCTIONAL_CONSEQUENCE = {"CDR3": 3, "CDR1": 3, "CDR2": 2, "FR1": 1, "FR2": 1, "FR3": 1, "FR4": 1}
# How dangerous it is to mutate the site away, by region.
REMEDIATION_RISK = {"CDR3": 3, "CDR1": 3, "CDR2": 3, "FR1": 1, "FR2": 1, "FR3": 1, "FR4": 1}

RISK_TIERS = {3: "high", 2: "moderate", 1: "low", 0: "negligible"}
# Relative SASA above which a residue is treated as solvent-exposed.
EXPOSED_RELATIVE_SASA = 0.20
BURIED_RELATIVE_SASA = 0.05


def _exposure_factor(relative_sasa: float | None) -> tuple[float, str]:
    """Scale chemical risk by solvent exposure."""
    if relative_sasa is None:
        return 1.0, "unknown"
    if relative_sasa >= EXPOSED_RELATIVE_SASA:
        return 1.0, "exposed"
    if relative_sasa <= BURIED_RELATIVE_SASA:
        return 0.34, "buried"
    return 0.67, "partially_buried"


# Burial moves the two risk axes in opposite directions, and reporting only the
# first is what made buried core residues look like cheap fixes. Solvent, peroxide
# and light reach a buried side chain less well, so the chemistry is slower and
# the *urgency* falls -- that is the ``_exposure_factor`` above. But a buried side
# chain is packed against its neighbours, so substituting it perturbs the core and
# the *cost of remediation* rises. A buried liability is therefore the least
# urgent and most expensive to fix, not the safest.
REMEDIATION_COST_BY_EXPOSURE = {
    "exposed": (0, "Side chain is solvent-exposed; substitution is unlikely to perturb core packing."),
    "partially_buried": (
        1,
        "Side chain is partially buried; substitution may perturb local packing and needs an expression "
        "and thermostability check.",
    ),
    "buried": (
        2,
        "Side chain is buried in the domain core; substitution is a packing change. Chemical urgency is "
        "low precisely because solvent access is low, so the fix costs more than the liability.",
    ),
    "unknown": (0, "No structure available, so burial is unknown and remediation cost cannot be adjusted."),
}


def scan_chain(
    sequence: str,
    chain: str,
    position_map: dict[int, dict[str, Any]] | None = None,
    exposure: dict[int, float] | None = None,
) -> list[dict[str, Any]]:
    """Scan one chain for motif liabilities.

    ``position_map`` maps 1-based linear index to ``{"label", "region"}`` from the
    numbering stage. ``exposure`` maps 1-based linear index to relative SASA.
    """
    position_map = position_map or {}
    exposure = exposure or {}
    hits: list[dict[str, Any]] = []
    for rule in LIABILITY_RULES:
        for match in re.finditer(rule["pattern"], sequence):
            index = match.start() + 1
            annotation = position_map.get(index, {})
            region = annotation.get("region", "unknown")
            relative_sasa = exposure.get(index)
            factor, exposure_class = _exposure_factor(relative_sasa)
            chemical = rule["chemical_severity"] * factor
            burial_penalty, burial_note = REMEDIATION_COST_BY_EXPOSURE[exposure_class]
            anchor = annotation.get("structural_anchor")
            remediation = REMEDIATION_RISK.get(region, 2) + burial_penalty
            if anchor:
                # An anchor is invariant across the whole immunoglobulin fold, so no
                # region- or burial-derived score describes it. Pin it at the top.
                remediation = 3
            hits.append(
                {
                    "liability_id": rule["id"],
                    "name": rule["name"],
                    "chain": chain,
                    "position": index,
                    "scheme_position": annotation.get("label"),
                    "region": region,
                    "imgt_region": annotation.get("imgt_region", region),
                    "kabat_region": annotation.get("kabat_region"),
                    "region_definitions_agree": annotation.get("region_definitions_agree", True),
                    "structural_anchor": anchor,
                    "germline_encoded": annotation.get("germline_encoded"),
                    "germline_residue": annotation.get("germline_residue"),
                    "residue": sequence[index - 1],
                    "context": sequence[max(0, index - 2) : index + 2],
                    "mechanism": rule["mechanism"],
                    "chemical_risk": round(chemical, 2),
                    "chemical_risk_tier": RISK_TIERS[min(3, max(0, round(chemical)))],
                    "relative_sasa": None if relative_sasa is None else round(relative_sasa, 3),
                    "exposure_class": exposure_class,
                    "functional_consequence": FUNCTIONAL_CONSEQUENCE.get(region, 2),
                    "remediation_risk": min(3, remediation),
                    "remediation_cost_note": (
                        f"Conserved structural anchor: {anchor}. Substitution is a fold change, not a "
                        "developability fix."
                        if anchor
                        else burial_note
                    ),
                    "remediation_options": list(rule["remediation"]),
                }
            )
    hits.sort(key=lambda hit: (hit["position"], hit["liability_id"]))
    return hits


def cysteine_audit(sequence: str, chain: str, position_map: dict[int, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Audit cysteines against the single canonical intradomain disulfide.

    An immunoglobulin variable domain carries one buried intradomain disulfide,
    so two cysteines. Any additional cysteine is a candidate free thiol: an
    aggregation and conjugation-heterogeneity risk, and for an ADC a site that
    can compete with intended conjugation chemistry.
    """
    position_map = position_map or {}
    positions = [index + 1 for index, residue in enumerate(sequence) if residue == "C"]
    expected = 2
    extra = max(0, len(positions) - expected)
    return {
        "chain": chain,
        "cysteine_positions": [
            {"position": index, "scheme_position": position_map.get(index, {}).get("label"), "region": position_map.get(index, {}).get("region", "unknown")}
            for index in positions
        ],
        "cysteine_count": len(positions),
        "expected_canonical_count": expected,
        "unpaired_cysteine_candidates": extra,
        "odd_count": len(positions) % 2 == 1,
        "status": "canonical" if len(positions) == expected else "non_canonical",
        "interpretation": (
            "Two cysteines consistent with the canonical intradomain disulfide."
            if len(positions) == expected
            else f"{len(positions)} cysteines found; {extra} beyond the canonical pair require free-thiol assessment."
        ),
    }


def summarize(hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate a liability list into counts and a burden score."""
    by_tier: dict[str, int] = {"high": 0, "moderate": 0, "low": 0, "negligible": 0}
    by_region: dict[str, int] = {}
    for hit in hits:
        by_tier[hit["chemical_risk_tier"]] = by_tier.get(hit["chemical_risk_tier"], 0) + 1
        by_region[hit["region"]] = by_region.get(hit["region"], 0) + 1
    burden = sum(hit["chemical_risk"] * hit["functional_consequence"] for hit in hits)
    cdr_hits = [hit for hit in hits if hit["region"].startswith("CDR")]
    anchor_hits = [hit for hit in hits if hit.get("structural_anchor")]
    contested = [hit for hit in hits if not hit.get("region_definitions_agree", True)]
    germline_encoded = [hit for hit in hits if hit.get("germline_encoded") is True]
    somatic = [hit for hit in hits if hit.get("germline_encoded") is False]
    germline_uncompared = [hit for hit in hits if hit.get("germline_encoded") is None]
    return {
        "total_hits": len(hits),
        "by_chemical_risk_tier": by_tier,
        "by_region": dict(sorted(by_region.items())),
        "cdr_localised_hits": len(cdr_hits),
        "structural_anchor_hits": len(anchor_hits),
        "structural_anchor_positions": [
            f"{hit['chain']}:{hit['position']} ({hit['scheme_position']}) {hit['structural_anchor']}"
            for hit in anchor_hits
        ],
        # Hits where IMGT and Kabat disagree on whether the position is a CDR. These
        # are the positions where a single-scheme pipeline mislabels risk, so they are
        # surfaced rather than silently resolved.
        "region_definition_conflicts": len(contested),
        "region_definition_conflict_positions": [
            f"{hit['chain']}:{hit['position']} imgt={hit['imgt_region']} kabat={hit['kabat_region']}"
            for hit in contested
        ],
        # Liabilities that are the human germline residue at their position. They are
        # shared with every antibody built on the same V gene, so their prevalence in
        # approved products is evidence that the risk is tolerated in practice, and
        # remediating one lowers framework identity. Reported separately because the
        # right default for this class is to leave it alone.
        "germline_encoded_hits": len(germline_encoded),
        "germline_encoded_positions": [
            f"{hit['chain']}:{hit['position']} ({hit['scheme_position']}) {hit['residue']} is the germline residue"
            for hit in germline_encoded
        ],
        # Somatic liabilities are the ones actually introduced by this antibody's
        # maturation, so they are the only ones whose remediation does not cost
        # framework identity. This is the list to engineer.
        "somatic_hits": len(somatic),
        "somatic_positions": [
            f"{hit['chain']}:{hit['position']} ({hit['scheme_position']}) {hit['residue']} vs germline "
            f"{hit['germline_residue']}"
            for hit in somatic
        ],
        "germline_comparison_unavailable_hits": len(germline_uncompared),
        "germline_comparison_unavailable_positions": [
            f"{hit['chain']}:{hit['position']} ({hit['scheme_position']}) region {hit['region']}"
            for hit in germline_uncompared
        ],
        "liability_burden": round(burden, 2),
        "burden_definition": "sum over hits of chemical_risk x functional_consequence; comparative only, not a measured degradation rate",
        "germline_encoded_policy": (
            "A germline-encoded liability is not evidence of a defect in this antibody. Remediating one trades "
            "framework identity for a chemical risk that the human repertoire already carries. Counts are "
            "tri-state: germline-encoded, somatic, or not comparable. Not comparable means the position lies "
            "outside the V-gene framework alignment (CDR3 is junctional, FR4 is J-derived) and must not be "
            "read as somatic."
        ),
        "cdr_definition_policy": (
            "A position counted as CDR if either IMGT or Kabat places it in a CDR. Chosen because the two "
            "definitions answer different questions and a paratope residue missed by one still binds antigen."
        ),
    }


def scan_binder(
    chains: dict[str, str],
    position_maps: dict[str, dict[int, dict[str, Any]]] | None = None,
    exposure: dict[str, dict[int, float]] | None = None,
) -> dict[str, Any]:
    """Scan every chain of a binder and aggregate."""
    position_maps = position_maps or {}
    exposure = exposure or {}
    hits: list[dict[str, Any]] = []
    cysteines: list[dict[str, Any]] = []
    for chain, sequence in sorted(chains.items()):
        if not sequence:
            continue
        hits.extend(scan_chain(sequence, chain, position_maps.get(chain), exposure.get(chain)))
        cysteines.append(cysteine_audit(sequence, chain, position_maps.get(chain)))
    structure_informed = any(hit["exposure_class"] != "unknown" for hit in hits)
    return {
        "hits": hits,
        "cysteine_audit": cysteines,
        "summary": summarize(hits),
        "structure_informed": structure_informed,
        "method": "motif_rule_scan_with_exposure_weighting" if structure_informed else "motif_rule_scan_sequence_only",
        "boundary": (
            "Rule-based liability flags. A flag is a hypothesis to test by forced-degradation "
            "and peptide-mapping studies, not an observed degradation event."
        ),
    }
