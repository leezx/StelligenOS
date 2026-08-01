"""ADC product entities: antibody, conjugation variant, product candidate.

v0.2.0 modelled one entity, the Fv, and correctly refused to infer a DAR from it.
Refusing was right but insufficient: an ADC programme's decisions are made about
*products*, and one antibody maps to many products.

    AntibodyCandidate  x  ConjugationVariant  ->  ADCProductCandidate

    Fv-A + Fc-silent   + engineered-Cys site + linker-Y + payload-Z + DAR2
    Fv-A + Fc-silent   + engineered-Cys site + linker-Y + payload-Z + DAR4
    Fv-A + wild-type Fc + stochastic Lys      + linker-Y + payload-Z + DAR~3.5

These three behave differently in hydrophobicity, aggregation, charge
heterogeneity, binding retention, plasma stability, and clearance. Carrying the
naked-Fv ranking forward to all of them would assume the payload is inert, which
is the opposite of true.

This module builds the product matrix and, for each product property, reports
whether the property is computable now, needs more input, or needs an experiment.
It does not invent values. The properties that dominate conjugate behaviour depend
on payload physicochemistry and the constant regions, so with an Fv-only input
most of them are honestly ``requires_input``.
"""

from __future__ import annotations

from typing import Any

# ------------------------------------------------------- conjugation chemistries

CONJUGATION_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "variant_id": "stochastic_lysine",
        "chemistry": "NHS-ester acylation of surface lysines",
        "site_control": "none",
        "typical_dar": "0-8, distribution centred near 3.5",
        "dar_homogeneity": "heterogeneous",
        "requires_constant_regions": True,
        "paratope_risk": True,
        "note": "Most accessible lysines are in the constant domains, but any CDR lysine is also a substrate.",
    },
    {
        "variant_id": "reduced_interchain_cysteine",
        "chemistry": "partial interchain disulfide reduction, maleimide coupling",
        "site_control": "partial",
        "typical_dar": "2, 4, or 8",
        "dar_homogeneity": "mixed species",
        "requires_constant_regions": True,
        "paratope_risk": False,
        "note": "Uses hinge and CH1/CL cysteines; absent entirely from a variable-domain-only input.",
    },
    {
        "variant_id": "site_specific_engineered_cysteine",
        "chemistry": "engineered free cysteine, maleimide coupling",
        "site_control": "full",
        "typical_dar": "2",
        "dar_homogeneity": "homogeneous",
        "requires_constant_regions": True,
        "paratope_risk": False,
        "note": "Requires an engineered site in a constant domain, chosen for stability and solvent exposure.",
    },
    {
        "variant_id": "site_specific_enzymatic",
        "chemistry": "enzymatic tag conjugation (e.g. transglutaminase or sortase)",
        "site_control": "full",
        "typical_dar": "2",
        "dar_homogeneity": "homogeneous",
        "requires_constant_regions": True,
        "paratope_risk": False,
    },
)

# ------------------------------------------------------------ product properties

# ``depends_on`` records what a value would require. ``computable_from_fv`` marks
# the few properties an Fv-only input can genuinely inform.
PRODUCT_PROPERTIES: tuple[dict[str, Any], ...] = (
    {"property_id": "conjugate_hydrophobicity", "depends_on": ("payload physicochemistry", "DAR", "conjugation site"), "resolution": "experiment", "assay": "HIC retention versus naked antibody"},
    {"property_id": "aggregation_propensity", "depends_on": ("payload hydrophobicity", "DAR", "full-length sequence"), "resolution": "experiment", "assay": "SEC and stress aggregation"},
    {"property_id": "charge_heterogeneity", "depends_on": ("conjugation chemistry", "full-length sequence"), "resolution": "experiment", "assay": "cIEF or imaged capillary IEF"},
    {"property_id": "binding_retention", "depends_on": ("conjugation site relative to paratope",), "resolution": "experiment", "assay": "SPR/BLI and cell binding, conjugate versus naked", "partially_computable_from_fv": True},
    {"property_id": "fc_receptor_interaction", "depends_on": ("Fc sequence", "Fc modification"), "resolution": "input", "assay": "FcgammaR and FcRn binding panel"},
    {"property_id": "plasma_stability", "depends_on": ("linker chemistry",), "resolution": "experiment", "assay": "plasma incubation with DAR drift and free-payload readout"},
    {"property_id": "payload_deconjugation", "depends_on": ("linker chemistry", "conjugation site"), "resolution": "experiment", "assay": "free-payload release over time"},
    {"property_id": "pk_risk", "depends_on": ("hydrophobicity", "aggregation", "charge", "FcRn binding"), "resolution": "experiment", "assay": "in vivo PK of conjugate versus naked"},
    {"property_id": "lysosomal_metabolite", "depends_on": ("linker chemistry", "payload"), "resolution": "experiment", "assay": "catabolite identification by LC-MS"},
    {"property_id": "bystander_potential", "depends_on": ("payload membrane permeability",), "resolution": "experiment", "assay": "co-culture bystander killing"},
)


def _paratope_conjugation_risk(conjugation_analysis: dict[str, Any] | None) -> dict[str, Any]:
    """The one conjugation conclusion an Fv-only input genuinely supports."""
    conjugation_analysis = conjugation_analysis or {}
    cdr_lysines = conjugation_analysis.get("cdr_proximal_accessible_lysines") or []
    if cdr_lysines:
        return {
            "risk": "present",
            "cdr_accessible_lysines": cdr_lysines,
            "finding": (
                f"{len(cdr_lysines)} solvent-accessible lysine(s) sit inside a CDR ({', '.join(str(item) for item in cdr_lysines)}). "
                "Stochastic lysine conjugation can therefore modify the paratope, so a site-specific chemistry "
                "is preferred, or binding must be re-measured after conjugation."
            ),
        }
    return {
        "risk": "not_detected",
        "cdr_accessible_lysines": [],
        "finding": (
            "No solvent-accessible lysine was found inside a CDR, so stochastic lysine conjugation is less "
            "likely to modify the paratope. Constant-domain lysines remain unassessed."
        ),
    }


def assemble(
    antibody_candidates: list[dict[str, Any]],
    conjugation_analysis: dict[str, Any] | None = None,
    constant_regions_supplied: bool = False,
    payload_declared: bool = False,
    selected_variants: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Build the ADC product candidate matrix.

    Only antibody candidates that are plausible carriers are expanded, to keep the
    matrix a decision aid rather than a combinatorial dump: the parent, the
    construct-specification variants, and any candidate explicitly flagged as a
    carrier candidate.
    """
    variant_ids = selected_variants or tuple(variant["variant_id"] for variant in CONJUGATION_VARIANTS)
    variants = [variant for variant in CONJUGATION_VARIANTS if variant["variant_id"] in variant_ids]
    paratope_risk = _paratope_conjugation_risk(conjugation_analysis)

    carriers = [
        candidate
        for candidate in antibody_candidates
        if candidate.get("family") in {"parent", "function_silenced", "valency_clustering"}
        or candidate.get("carrier_candidate")
    ]
    if not carriers:
        carriers = [candidate for candidate in antibody_candidates if candidate.get("family") == "parent"]

    products: list[dict[str, Any]] = []
    for candidate in carriers:
        for variant in variants:
            blockers: list[str] = []
            if variant["requires_constant_regions"] and not constant_regions_supplied:
                blockers.append("constant-region sequences not supplied")
            if not payload_declared:
                blockers.append("linker and payload not declared")

            properties = []
            for spec in PRODUCT_PROPERTIES:
                if spec["property_id"] == "binding_retention" and variant["paratope_risk"]:
                    status = "flagged_by_computation"
                    detail = paratope_risk["finding"]
                elif spec["resolution"] == "input":
                    status = "requires_input"
                    detail = f"needs: {', '.join(spec['depends_on'])}"
                else:
                    status = "requires_experiment"
                    detail = spec["assay"]
                properties.append(
                    {
                        "property_id": spec["property_id"],
                        "status": status,
                        "detail": detail,
                        "depends_on": list(spec["depends_on"]),
                    }
                )

            products.append(
                {
                    "product_id": f"{candidate['candidate_id']}::{variant['variant_id']}",
                    "antibody_candidate_id": candidate["candidate_id"],
                    "antibody_family": candidate.get("family"),
                    "antibody_format": candidate.get("format", "IgG"),
                    "fc_modification": candidate.get("fc_modification"),
                    "conjugation_variant": variant["variant_id"],
                    "chemistry": variant["chemistry"],
                    "site_control": variant["site_control"],
                    "typical_dar": variant["typical_dar"],
                    "dar_homogeneity": variant["dar_homogeneity"],
                    "buildable_now": not blockers,
                    "blockers": blockers,
                    "properties": properties,
                    "paratope_conjugation_risk": paratope_risk["risk"] if variant["paratope_risk"] else "not_applicable",
                }
            )

    computable = sum(
        1
        for product in products
        for prop in product["properties"]
        if prop["status"] == "flagged_by_computation"
    )
    return {
        "products": products,
        "product_count": len(products),
        "antibody_candidates_expanded": [candidate["candidate_id"] for candidate in carriers],
        "conjugation_variants_considered": [variant["variant_id"] for variant in variants],
        "paratope_conjugation_risk": paratope_risk,
        "buildable_now_count": sum(1 for product in products if product["buildable_now"]),
        "computed_property_findings": computable,
        "recommended_variant": (
            "site_specific_engineered_cysteine"
            if paratope_risk["risk"] == "present"
            else None
        ),
        "recommendation_basis": (
            "A CDR-accessible lysine makes stochastic lysine conjugation a paratope risk, so a "
            "site-controlled chemistry is preferred for the first conjugate."
            if paratope_risk["risk"] == "present"
            else "No computational basis to prefer one chemistry; the choice is an experimental question."
        ),
        "required_input_extension": None
        if (constant_regions_supplied and payload_declared)
        else "Supply full-length heavy and light chains plus a declared linker and payload to evaluate product properties.",
        "boundary": (
            "This is a product matrix with per-property resolution requirements, not a scored ranking. "
            "No product property is estimated: conjugate behaviour is dominated by payload "
            "physicochemistry and constant-region context, neither of which is inferable from an Fv."
        ),
    }
