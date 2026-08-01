"""Antibody numbering, region assignment, and germline humanness.

Runs inside whichever interpreter holds ANARCI/abnumber. When neither is
available the caller receives an explicit unavailability record rather than a
guessed CDR boundary: a wrong CDR definition silently corrupts every downstream
stage, so it is safer to stop than to approximate.
"""

from __future__ import annotations

from typing import Any

CDR_DEFINITIONS = ("imgt", "kabat")

# Conserved immunoglobulin structural anchors, by IMGT position number. These are
# the positions IMGT itself defines as invariant landmarks of the V-domain fold:
# the two cysteines of the intradomain disulfide, the two core tryptophans, and
# the hydrophobic pivot. They are not engineering options. A liability scan will
# flag the tryptophans as oxidation-prone and it is right to report them, but a
# substitution there is a fold change rather than a developability fix, so a
# proposal at an anchor must never be presented as a low-risk framework tidy-up.
STRUCTURAL_ANCHORS = {
    23: "1st-CYS, intradomain disulfide partner",
    41: "CONSERVED-TRP of the V-domain core",
    89: "hydrophobic pivot of the inner sheet",
    104: "2nd-CYS, intradomain disulfide partner",
    118: "J-region TRP/PHE anchoring FR4 to the core",
}

# Which region assignment dominates when two CDR definitions disagree. A residue
# inside a CDR under *either* definition is treated as a CDR residue for risk,
# because the definitions are not competing truths: IMGT boundaries are
# structural, Kabat boundaries are variability-derived, and a paratope residue
# missed by one is still a paratope residue. Ranking is by how much a change
# there can cost, so the higher rank wins.
REGION_RISK_RANK = {"CDR3": 4, "CDR1": 3, "CDR2": 2, "FR1": 0, "FR2": 0, "FR3": 0, "FR4": 0}


def _chain_record(sequence: str, scheme: str) -> dict[str, Any]:
    from abnumber import Chain

    chain = Chain(sequence, scheme=scheme)
    position_map: dict[int, dict[str, Any]] = {}
    linear_index = 0
    for position, residue in chain.positions.items():
        linear_index += 1
        position_map[linear_index] = {
            "label": str(position),
            "number": position.number,
            "insertion": (getattr(position, "letter", "") or "").strip(),
            "region": position.get_region(),
            "residue": residue,
        }
    regions = {name: sequence_part for name, sequence_part in chain.regions.items()}
    return {
        "scheme": scheme,
        "chain_type": chain.chain_type,
        "numbered_length": len(chain.positions),
        "position_map": position_map,
        "regions": {name: "".join(part.values()) if isinstance(part, dict) else str(part) for name, part in regions.items()},
        "cdr1": chain.cdr1_seq,
        "cdr2": chain.cdr2_seq,
        "cdr3": chain.cdr3_seq,
    }


def _germline_record(sequence: str, scheme: str) -> dict[str, Any]:
    """Closest human germline genes and framework identity."""
    from abnumber import Chain

    chain = Chain(sequence, scheme=scheme)
    record: dict[str, Any] = {"method": "abnumber.find_human_germlines"}
    try:
        v_genes, j_genes = chain.find_human_germlines(limit=1)
    except Exception as error:  # germline DB miss should not abort the stage
        record["status"] = "unavailable"
        record["detail"] = str(error)
        return record

    v_germline = v_genes[0]
    record["closest_human_v_gene"] = v_germline.name
    record["closest_human_j_gene"] = j_genes[0].name

    # Derive the linear index from the chain's own position ordering, which is the
    # same ordering the downstream position_map uses, so the two cannot drift.
    label_to_linear = {str(position): index for index, position in enumerate(chain.positions, start=1)}

    framework_match = framework_total = 0
    whole_match = whole_total = 0
    differences: list[dict[str, Any]] = []
    framework_germline: dict[int, str] = {}
    for position, residues in chain.align(v_germline):
        query, germline = residues[0], residues[1]
        if query == "-" or germline == "-":
            continue
        label = str(position)
        region = position.get_region()
        whole_total += 1
        whole_match += query == germline
        if region.startswith("FR"):
            framework_total += 1
            framework_match += query == germline
            linear_index = label_to_linear.get(label)
            if linear_index is not None:
                framework_germline[linear_index] = germline
            if query != germline:
                differences.append(
                    {
                        "scheme_position": label,
                        "region": region,
                        "linear_position": linear_index,
                        "binder_residue": query,
                        "germline_residue": germline,
                    }
                )

    record["status"] = "available"
    record["framework_identity_percent"] = round(100 * framework_match / framework_total, 1) if framework_total else None
    record["framework_positions_compared"] = framework_total
    record["framework_positions_matching"] = framework_match
    record["v_gene_identity_percent"] = round(100 * whole_match / whole_total, 1) if whole_total else None
    record["framework_deviations_from_germline"] = differences
    # Germline residue at every compared framework position, so a candidate's
    # framework identity can be recomputed exactly after substitution rather than
    # estimated from a reversion count.
    record["framework_germline_residues"] = framework_germline
    record["interpretation"] = (
        "Framework identity to the closest human germline V gene. A humanness proxy "
        "for engineering triage, not a validated immunogenicity prediction."
    )
    return record


def number_chains(payload: dict[str, Any]) -> dict[str, Any]:
    """Number each supplied chain under every CDR definition, plus germline analysis."""
    chains: dict[str, str] = payload["chains"]
    result: dict[str, Any] = {"chains": {}, "definitions": list(CDR_DEFINITIONS)}
    try:
        import abnumber
        from anarci import anarci  # noqa: F401  (presence check only)

        result["tool"] = "abnumber"
        result["tool_version"] = getattr(abnumber, "__version__", "unknown")
    except Exception as error:
        return {"status": "unavailable", "detail": f"numbering stack unavailable: {error}", "chains": {}}

    for chain_name, sequence in sorted(chains.items()):
        if not sequence:
            continue
        entry: dict[str, Any] = {"schemes": {}}
        for scheme in CDR_DEFINITIONS:
            try:
                entry["schemes"][scheme] = _chain_record(sequence, scheme)
            except Exception as error:
                entry["schemes"][scheme] = {"status": "failed", "detail": str(error)}
        try:
            entry["germline"] = _germline_record(sequence, "imgt")
        except Exception as error:
            entry["germline"] = {"status": "failed", "detail": str(error)}
        primary = entry["schemes"].get("imgt", {})
        entry["chain_type"] = primary.get("chain_type")
        entry["length"] = len(sequence)
        result["chains"][chain_name] = entry

    result["status"] = "available"
    result["primary_definition"] = "imgt"
    result["boundary"] = "Numbering and germline assignment are computational annotations of the supplied sequence."
    return result


def position_maps(numbering: dict[str, Any], definition: str = "union") -> dict[str, dict[int, dict[str, Any]]]:
    """Extract ``{chain: {linear_position: {label, region, ...}}}`` for downstream stages.

    ``definition`` may name a single scheme (``"imgt"``, ``"kabat"``) or ``"union"``.

    ``"union"`` is the default because the single-scheme maps are unsafe for risk
    assignment. Under IMGT, Kabat CDR-H1 positions 34-35 and the whole Kabat
    CDR-H2 tail 58-65 fall in FR2/FR3, so an affinity-matured paratope residue is
    labelled framework and inherits framework's low functional consequence, low
    engineering risk, and ``requires_binding_confirmation: false``. The union map
    keeps both assignments visible and resolves ``region`` to whichever costs more
    to disturb.
    """
    maps: dict[str, dict[int, dict[str, Any]]] = {}
    for chain_name, entry in (numbering.get("chains") or {}).items():
        schemes = entry.get("schemes") or {}
        if definition != "union":
            raw = schemes.get(definition, {}).get("position_map") or {}
            maps[chain_name] = {int(key): value for key, value in raw.items()}
            continue
        maps[chain_name] = _union_map(
            schemes.get("imgt", {}).get("position_map") or {},
            schemes.get("kabat", {}).get("position_map") or {},
            (entry.get("germline") or {}).get("framework_germline_residues") or {},
        )
    return maps


def _union_map(
    imgt_raw: dict[Any, dict[str, Any]],
    kabat_raw: dict[Any, dict[str, Any]],
    germline_raw: dict[Any, str] | None = None,
) -> dict[int, dict[str, Any]]:
    """Merge the IMGT and Kabat position maps of one chain on linear position.

    Both schemes number the same residues in sequence order, so linear position is
    a shared key; the residue identity is asserted rather than assumed, and a
    mismatch degrades to the IMGT assignment instead of silently mixing schemes.
    """
    imgt = {int(key): value for key, value in imgt_raw.items()}
    kabat = {int(key): value for key, value in kabat_raw.items()}
    # Keys survive a JSON round trip as strings, so normalise rather than assume.
    germline = {int(key): value for key, value in (germline_raw or {}).items()}
    merged: dict[int, dict[str, Any]] = {}
    for index, imgt_entry in sorted(imgt.items()):
        kabat_entry = kabat.get(index) or {}
        imgt_region = imgt_entry.get("region", "unknown")
        kabat_region = kabat_entry.get("region")
        aligned = bool(kabat_entry) and kabat_entry.get("residue") == imgt_entry.get("residue")
        if not aligned:
            kabat_region = None
        candidates = [region for region in (imgt_region, kabat_region) if region]
        region = max(candidates, key=lambda name: REGION_RISK_RANK.get(name, 1)) if candidates else "unknown"
        entry = dict(imgt_entry)
        entry.update(
            {
                "region": region,
                "imgt_region": imgt_region,
                "kabat_region": kabat_region,
                "kabat_label": kabat_entry.get("label") if aligned else None,
                "region_definitions_agree": (kabat_region is None) or (imgt_region == kabat_region),
                "region_definition_basis": "union_of_imgt_and_kabat" if aligned else "imgt_only",
                "structural_anchor": STRUCTURAL_ANCHORS.get(imgt_entry.get("number")),
                "germline_residue": germline.get(index),
                # Tri-state, following the module's rule that absence of data is not a
                # negative result. True: the residue here IS the closest human germline
                # residue, so the liability is encoded by the human germline, shared
                # with every antibody on this V gene, and removing it lowers framework
                # identity. False: the residue differs from germline, so it is somatic.
                # None: not comparable -- the V-gene alignment covers framework FR1-FR3
                # only, so CDR3 (junctional) and FR4 (J-derived) have no germline
                # counterpart here and must not be reported as somatic by default.
                "germline_encoded": (
                    (germline[index] == imgt_entry.get("residue")) if index in germline else None
                ),
            }
        )
        merged[index] = entry
    return merged
