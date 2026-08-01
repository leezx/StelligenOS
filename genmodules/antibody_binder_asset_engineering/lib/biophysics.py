"""Sequence-derived biophysical descriptors.

Every constant table below is a published reference set, named at its point of
use so a reviewer can check the value rather than trust the code. These are
sequence-derived descriptors, not measurements: they describe the molecule as
written, and none of them is a substitute for an assay.
"""

from __future__ import annotations

from typing import Any

# Kyte & Doolittle (1982) J Mol Biol 157:105-132 hydropathy index.
KYTE_DOOLITTLE = {
    "A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5,
    "Q": -3.5, "E": -3.5, "G": -0.4, "H": -3.2, "I": 4.5,
    "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8, "P": -1.6,
    "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2,
}

# EMBOSS iep pKa set, as used by EMBOSS/Expasy-style isoelectric point routines.
PKA_SIDE_CHAIN = {"C": 8.5, "D": 3.9, "E": 4.1, "H": 6.5, "K": 10.8, "R": 12.5, "Y": 10.1}
PKA_N_TERMINUS = 8.6
PKA_C_TERMINUS = 3.6
POSITIVE_RESIDUES = frozenset("KRH")
NEGATIVE_RESIDUES = frozenset("DECY")

# Tien et al. (2013) PLoS ONE 8:e80635, empirical maximum solvent accessibility
# (A^2) per residue in a Gly-X-Gly context. Used to convert absolute SASA to a
# relative value.
MAX_ASA = {
    "A": 121.0, "R": 265.0, "N": 187.0, "D": 187.0, "C": 148.0,
    "Q": 214.0, "E": 214.0, "G": 97.0, "H": 216.0, "I": 195.0,
    "L": 191.0, "K": 230.0, "M": 203.0, "F": 228.0, "P": 154.0,
    "S": 143.0, "T": 163.0, "W": 264.0, "Y": 255.0, "V": 165.0,
}

# Gill & von Hippel (1989) Anal Biochem 182:319-326, molar extinction at 280 nm.
EXTINCTION_280 = {"W": 5500, "Y": 1490, "C": 125}


def net_charge_at_ph(sequence: str, ph: float) -> float:
    """Net formal charge from Henderson-Hasselbalch over ionisable groups."""
    charge = 1.0 / (1.0 + 10 ** (ph - PKA_N_TERMINUS))
    charge -= 1.0 / (1.0 + 10 ** (PKA_C_TERMINUS - ph))
    for residue in sequence:
        pka = PKA_SIDE_CHAIN.get(residue)
        if pka is None:
            continue
        if residue in ("K", "R", "H"):
            charge += 1.0 / (1.0 + 10 ** (ph - pka))
        else:
            charge -= 1.0 / (1.0 + 10 ** (pka - ph))
    return charge


def isoelectric_point(sequence: str, tolerance: float = 1e-4) -> float | None:
    """Bisect the pH at which net charge is zero."""
    if not sequence:
        return None
    low, high = 0.0, 14.0
    if net_charge_at_ph(sequence, low) < 0:
        return low
    if net_charge_at_ph(sequence, high) > 0:
        return high
    while high - low > tolerance:
        middle = (low + high) / 2.0
        if net_charge_at_ph(sequence, middle) > 0:
            low = middle
        else:
            high = middle
    return round((low + high) / 2.0, 2)


def gravy(sequence: str) -> float | None:
    """Grand average of hydropathy (mean Kyte-Doolittle index)."""
    scored = [KYTE_DOOLITTLE[residue] for residue in sequence if residue in KYTE_DOOLITTLE]
    if not scored:
        return None
    return round(sum(scored) / len(scored), 3)


def extinction_coefficient_280(sequence: str) -> dict[str, int]:
    """Molar extinction at 280 nm, reduced and fully cystine-paired."""
    tryptophan = sequence.count("W")
    tyrosine = sequence.count("Y")
    cysteine = sequence.count("C")
    reduced = tryptophan * EXTINCTION_280["W"] + tyrosine * EXTINCTION_280["Y"]
    return {
        "reduced_cysteines": reduced,
        "paired_cystines": reduced + (cysteine // 2) * 2 * EXTINCTION_280["C"],
    }


def hydrophobic_windows(sequence: str, window: int = 5, threshold: float = 1.8) -> list[dict[str, Any]]:
    """Contiguous windows whose mean hydropathy exceeds a threshold.

    A coarse aggregation-propensity heuristic, not an APR predictor. It flags
    where to look; it does not assert that a region aggregates.
    """
    if len(sequence) < window:
        return []
    flagged: list[dict[str, Any]] = []
    for start in range(len(sequence) - window + 1):
        segment = sequence[start : start + window]
        values = [KYTE_DOOLITTLE.get(residue, 0.0) for residue in segment]
        mean = sum(values) / window
        if mean >= threshold:
            flagged.append({"start": start + 1, "end": start + window, "segment": segment, "mean_hydropathy": round(mean, 3)})
    merged: list[dict[str, Any]] = []
    for record in flagged:
        if merged and record["start"] <= merged[-1]["end"]:
            previous = merged[-1]
            previous["end"] = record["end"]
            previous["segment"] = sequence[previous["start"] - 1 : previous["end"]]
            previous["mean_hydropathy"] = round(
                sum(KYTE_DOOLITTLE.get(residue, 0.0) for residue in previous["segment"])
                / len(previous["segment"]),
                3,
            )
        else:
            merged.append(dict(record))
    return merged


def describe_chain(sequence: str, ph: float = 7.4) -> dict[str, Any]:
    """Full biophysical descriptor set for one chain."""
    return {
        "length": len(sequence),
        "isoelectric_point": isoelectric_point(sequence),
        "net_charge_at_ph": {"ph": ph, "value": round(net_charge_at_ph(sequence, ph), 2)},
        "gravy": gravy(sequence),
        "extinction_coefficient_280": extinction_coefficient_280(sequence),
        "cysteine_count": sequence.count("C"),
        "cysteine_parity": "even" if sequence.count("C") % 2 == 0 else "odd",
        "lysine_count": sequence.count("K"),
        "hydrophobic_windows": hydrophobic_windows(sequence),
        "method": "sequence_derived_descriptors",
        "references": [
            "Kyte & Doolittle 1982 (hydropathy)",
            "EMBOSS iep pKa set (isoelectric point)",
            "Gill & von Hippel 1989 (extinction at 280 nm)",
        ],
        "boundary": "Descriptors computed from sequence only; no measured stability, solubility, or aggregation value is implied.",
    }


def combined_variable_domain(vh: str, vl: str | None) -> dict[str, Any]:
    """Descriptors for the paired variable domains treated as one species."""
    joined = vh + (vl or "")
    record = describe_chain(joined)
    record["composition"] = "VH+VL concatenated for whole-Fv charge and hydropathy only"
    return record
