"""Structure prediction and per-residue solvent accessibility.

Structure prediction is heavyweight model inference, so it sits behind the
module's ``external_execution_policy`` and only runs on explicit opt-in. SASA is
computed from whatever structure is available; without a structure the liability
scan stays sequence-only and says so.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lib.biophysics import MAX_ASA

# ABodyBuilder2 writes its per-residue predicted error (Angstrom) into the
# B-factor column; above this the local geometry is not trustworthy enough to
# support an exposure claim.
CONFIDENT_PREDICTED_ERROR_A = 1.5


def predict_structure(payload: dict[str, Any]) -> dict[str, Any]:
    """Predict a paired-chain Fv structure with ABodyBuilder2."""
    chains: dict[str, str] = payload["chains"]
    output_path = Path(payload["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    import ImmuneBuilder
    from ImmuneBuilder import ABodyBuilder2

    sequences = {"H": chains["vh"]}
    if chains.get("vl"):
        sequences["L"] = chains["vl"]

    predictor = ABodyBuilder2()
    antibody = predictor.predict(sequences)
    antibody.save(str(output_path))

    return {
        "status": "predicted",
        "structure_path": str(output_path),
        "tool": "ABodyBuilder2",
        "tool_version": getattr(ImmuneBuilder, "__version__", "unknown"),
        "chains_modelled": sorted(sequences),
        "confidence_field": "per-residue predicted error (Angstrom) in the PDB B-factor column",
        "boundary": (
            "A predicted model, not an experimental structure. No antigen is present, so no "
            "interface or epitope contact can be derived from it."
        ),
    }


def _parse_ca_confidence(pdb_path: Path) -> dict[str, dict[int, float]]:
    """Per-residue predicted error, read from CA B-factors."""
    confidence: dict[str, dict[int, float]] = {}
    for line in pdb_path.read_text().splitlines():
        if not line.startswith("ATOM"):
            continue
        if line[12:16].strip() != "CA":
            continue
        chain_id = line[21].strip()
        try:
            residue_number = int(line[22:26])
            b_factor = float(line[60:66])
        except ValueError:
            continue
        confidence.setdefault(chain_id, {})[residue_number] = b_factor
    return confidence


def solvent_accessibility(payload: dict[str, Any]) -> dict[str, Any]:
    """Per-residue absolute and relative SASA for a predicted or supplied structure.

    Returns exposure keyed by *linear* chain position so the liability scan can
    join on it directly. PDB chain H maps to ``vh`` and L to ``vl``.
    """
    pdb_path = Path(payload["structure_path"])
    if not pdb_path.is_file():
        return {"status": "unavailable", "detail": f"structure not found: {pdb_path}"}

    from Bio.PDB import PDBParser
    from Bio.PDB.SASA import ShrakeRupley

    parser = PDBParser(QUIET=True)
    model = next(iter(parser.get_structure("fv", str(pdb_path))))
    ShrakeRupley().compute(model, level="R")

    three_to_one = {
        "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
        "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
        "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
        "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
    }
    chain_alias = {"H": "vh", "L": "vl"}
    confidence = _parse_ca_confidence(pdb_path)

    exposure: dict[str, dict[int, float]] = {}
    detail: dict[str, list[dict[str, Any]]] = {}
    for chain in model:
        alias = chain_alias.get(chain.id.strip(), chain.id.strip())
        residues = [residue for residue in chain if residue.id[0] == " "]
        exposure[alias] = {}
        detail[alias] = []
        for linear_index, residue in enumerate(residues, start=1):
            one_letter = three_to_one.get(residue.get_resname(), "X")
            absolute = float(getattr(residue, "sasa", 0.0))
            reference = MAX_ASA.get(one_letter)
            relative = absolute / reference if reference else None
            predicted_error = confidence.get(chain.id.strip(), {}).get(residue.id[1])
            if relative is not None:
                exposure[alias][linear_index] = round(min(relative, 1.5), 4)
            detail[alias].append(
                {
                    "position": linear_index,
                    "residue": one_letter,
                    "absolute_sasa": round(absolute, 2),
                    "relative_sasa": None if relative is None else round(min(relative, 1.5), 4),
                    "predicted_error_angstrom": None if predicted_error is None else round(predicted_error, 2),
                    "geometry_confident": None if predicted_error is None else predicted_error <= CONFIDENT_PREDICTED_ERROR_A,
                }
            )

    return {
        "status": "available",
        "structure_path": str(pdb_path),
        "exposure": exposure,
        "per_residue": detail,
        "tool": "biopython Bio.PDB.SASA.ShrakeRupley",
        "reference_max_asa": "Tien et al. 2013 empirical maximum accessibility",
        "boundary": "Exposure derives from a single predicted conformation; it is not an ensemble average.",
        "scope_caveat": (
            "SASA is computed on an isolated Fv. In an intact IgG the C-terminal and elbow framework "
            "packs against CH1 and CL, so framework accessibility here is an upper bound and framework "
            "liabilities may be over-weighted relative to CDR liabilities. Treat a framework residue "
            "called exposed on this model as a candidate for confirmation on a full-length construct."
        ),
    }
