"""Causal failure-mode graph and experiment information gain.

A three-state evidence checklist is good bookkeeping and poor engineering
guidance. It answers "how many gaps remain", which does not tell you what to do
next, because gaps are not equally informative and one experiment can close
several at once.

This module models *why* an ADC would fail, as two causal trees, and then maps
every candidate experiment onto the set of failure modes it can exclude or
support. The output is an ordered list of next experiments by information gain,
where gain counts how many currently-unresolved failure modes an experiment can
discriminate, weighted by whether those modes are route-terminating.

Design rule: an experiment earns credit only for modes it can actually
*discriminate*. An assay that returns the same result whether or not a mode is
active has zero information gain against that mode, however expensive it is.
"""

from __future__ import annotations

from typing import Any

STATUS_EXCLUDED = "excluded"
STATUS_SUPPORTED = "supported"
STATUS_UNRESOLVED = "unresolved"

# ------------------------------------------------------------------- the trees

EFFICACY_TREE = "adc_activity_absent"
TOXICITY_TREE = "adc_toxicity"

FAILURE_MODES: tuple[dict[str, Any], ...] = (
    # ---- Why would the ADC have no activity? ----
    {
        "mode_id": "target_density_insufficient",
        "tree": EFFICACY_TREE,
        "description": "Too few surface targets per cell to accumulate a lethal payload dose.",
        "route_terminating": True,
    },
    {
        "mode_id": "antibody_binding_insufficient",
        "tree": EFFICACY_TREE,
        "description": "Binding too weak, or lost on conjugation, to engage the target in native context.",
        "route_terminating": False,
    },
    {
        "mode_id": "surface_retention",
        "tree": EFFICACY_TREE,
        "description": "The complex stays on the surface instead of internalising.",
        "route_terminating": True,
    },
    {
        "mode_id": "recycling_dominates_degradation",
        "tree": EFFICACY_TREE,
        "description": "The complex internalises but recycles back rather than reaching the lysosome.",
        "route_terminating": True,
    },
    {
        "mode_id": "lysosomal_delivery_insufficient",
        "tree": EFFICACY_TREE,
        "description": "Lysosomal flux too low to liberate a lethal payload dose.",
        "route_terminating": True,
    },
    {
        "mode_id": "linker_not_processed",
        "tree": EFFICACY_TREE,
        "description": "Trafficking is correct but the linker is not cleaved, so payload stays inert.",
        "route_terminating": False,
    },
    {
        "mode_id": "payload_resistance",
        "tree": EFFICACY_TREE,
        "description": "Target cells are intrinsically resistant to the payload class.",
        "route_terminating": False,
    },
    {
        "mode_id": "bystander_context_mismatch",
        "tree": EFFICACY_TREE,
        "description": "Payload bystander behaviour mismatched to target-expression heterogeneity in the tumour.",
        "route_terminating": False,
    },
    # ---- Why would the ADC be toxic? ----
    {
        "mode_id": "receptor_agonism",
        "tree": TOXICITY_TREE,
        "description": "Antibody binding itself activates the receptor, producing on-target signalling toxicity.",
        "route_terminating": True,
    },
    {
        "mode_id": "fcgr_dependent_crosslinking",
        "tree": TOXICITY_TREE,
        "description": "FcgammaR engagement crosslinks the antibody, amplifying agonism or effector-cell activation.",
        "route_terminating": False,
    },
    {
        "mode_id": "normal_tissue_target_expression",
        "tree": TOXICITY_TREE,
        "description": "Target expressed on normal tissue, giving on-target off-tumour payload delivery.",
        "route_terminating": True,
    },
    {
        "mode_id": "circulating_target_sink",
        "tree": TOXICITY_TREE,
        "description": "Shed or soluble target consumes the conjugate before it reaches tumour.",
        "route_terminating": False,
    },
    {
        "mode_id": "linker_instability",
        "tree": TOXICITY_TREE,
        "description": "Premature linker cleavage in plasma releases free payload systemically.",
        "route_terminating": False,
    },
    {
        "mode_id": "payload_nonspecific_toxicity",
        "tree": TOXICITY_TREE,
        "description": "Payload class toxicity independent of targeting.",
        "route_terminating": False,
    },
    {
        "mode_id": "conjugate_aggregation_rapid_clearance",
        "tree": TOXICITY_TREE,
        "description": "Payload hydrophobicity drives aggregation, fast clearance, and nonspecific uptake.",
        "route_terminating": False,
    },
)

MODE_INDEX = {mode["mode_id"]: mode for mode in FAILURE_MODES}

# ------------------------------------------------------------- the experiments

# ``excludes``: a clean result rules the mode out.
# ``supports``: a positive result argues the mode is active.
# Only modes an experiment can genuinely discriminate are listed.
EXPERIMENTS: tuple[dict[str, Any], ...] = (
    {
        "experiment_id": "modality_kill_internalization_panel",
        "name": "Internalisation panel across constructs and target-density tiers",
        "detail": (
            "Parent IgG1, Fc-silent, Fab, irrelevant isotype, and a fast-internalising positive control, "
            "across target-high, target-medium and target-negative endogenous lines. Measure 4 C surface "
            "binding, 37 C total uptake, acid-wash internalised fraction, surface-retained fraction, "
            "LAMP1 colocalisation, and receptor degradation/recovery over multiple times and concentrations."
        ),
        "excludes": ("surface_retention", "recycling_dominates_degradation", "target_density_insufficient"),
        "supports": ("surface_retention", "recycling_dominates_degradation", "fcgr_dependent_crosslinking"),
        "phase": 0,
        "cost_tier": "medium",
    },
    {
        "experiment_id": "lysosomal_flux_quantification",
        "name": "Quantitative lysosomal delivery fraction",
        "detail": (
            "Fraction of surface-bound antibody delivered to the lysosome per unit time, with a declared "
            "normalisation basis. Live-cell imaging plus a catabolite-release readout."
        ),
        "excludes": ("lysosomal_delivery_insufficient", "recycling_dominates_degradation"),
        "supports": ("lysosomal_delivery_insufficient",),
        "prerequisite_steps": ("endosomal_entry",),
        "phase": 0,
        "cost_tier": "medium",
    },
    {
        "experiment_id": "proof_of_modality_adc_cytotoxicity",
        "name": "Proof-of-modality conjugate cytotoxicity with full control set",
        "detail": (
            "Simple conjugate on target-high versus target-negative cells, with free payload, non-binding "
            "ADC, naked antibody, target competition, and lysosomal-processing interference controls."
        ),
        "excludes": ("linker_not_processed", "payload_resistance", "payload_nonspecific_toxicity"),
        "supports": ("payload_resistance", "linker_not_processed", "payload_nonspecific_toxicity"),
        "prerequisite_steps": ("lysosomal_delivery",),
        "phase": 0,
        "cost_tier": "medium",
    },
    {
        "experiment_id": "construct_signaling_comparison",
        "name": "Signalling and cytokine comparison across constructs",
        "detail": (
            "Canonical and alternative NF-kB, cytokine release, and receptor clustering for parent IgG1, "
            "Fc-silent, Fab, and the site-specific conjugate."
        ),
        "excludes": ("receptor_agonism", "fcgr_dependent_crosslinking"),
        "supports": ("receptor_agonism", "fcgr_dependent_crosslinking"),
        "phase": 1,
        "cost_tier": "medium",
    },
    {
        "experiment_id": "normal_cell_uptake_panel",
        "name": "Normal-cell uptake and toxicity panel",
        "detail": (
            "Conjugate uptake and killing in normal hepatocyte, pancreatic, and renal cell models against "
            "the tumour panel, to test whether a therapeutic window exists at all."
        ),
        "excludes": ("normal_tissue_target_expression",),
        "supports": ("normal_tissue_target_expression",),
        "phase": 1,
        "cost_tier": "high",
    },
    {
        "experiment_id": "quantitative_target_density",
        "name": "Quantitative surface target density",
        "detail": "Receptors per cell across indication-representative models and patient samples.",
        "excludes": ("target_density_insufficient",),
        "supports": ("target_density_insufficient",),
        "phase": 0,
        "cost_tier": "low",
    },
    {
        "experiment_id": "conjugated_binding_retention",
        "name": "Post-conjugation binding retention",
        "detail": "SPR/BLI and cell binding of conjugate versus naked antibody at matched DAR.",
        "excludes": ("antibody_binding_insufficient",),
        "supports": ("antibody_binding_insufficient",),
        "phase": 1,
        "cost_tier": "low",
    },
    {
        "experiment_id": "plasma_stability_and_deconjugation",
        "name": "Plasma stability and payload deconjugation",
        "detail": "Free-payload release and DAR drift in plasma over time, across conjugation chemistries.",
        "excludes": ("linker_instability",),
        "supports": ("linker_instability",),
        "phase": 2,
        "cost_tier": "low",
    },
    {
        "experiment_id": "conjugate_biophysical_panel",
        "name": "Conjugated-state biophysical panel",
        "detail": "SEC, HIC hydrophobicity, stress aggregation, and charge heterogeneity of conjugate versus naked.",
        "excludes": ("conjugate_aggregation_rapid_clearance",),
        "supports": ("conjugate_aggregation_rapid_clearance",),
        "phase": 2,
        "cost_tier": "low",
    },
    {
        "experiment_id": "soluble_target_quantification",
        "name": "Circulating soluble target quantification",
        "detail": "Shed target in patient and model plasma, and its effect on conjugate binding.",
        "excludes": ("circulating_target_sink",),
        "supports": ("circulating_target_sink",),
        "phase": 2,
        "cost_tier": "low",
    },
    {
        "experiment_id": "target_heterogeneity_and_bystander",
        "name": "Target heterogeneity mapping and bystander assessment",
        "detail": "Spatial target-expression heterogeneity plus a co-culture bystander-killing readout.",
        "excludes": ("bystander_context_mismatch",),
        "supports": ("bystander_context_mismatch",),
        "prerequisite_steps": ("cytotoxic_sufficiency",),
        "phase": 2,
        "cost_tier": "medium",
    },
)

# Which cascade criterion / readiness evidence resolves which failure mode.
CASCADE_TO_MODE = {
    ("surface_departure", "supported"): [("surface_retention", STATUS_EXCLUDED)],
    ("surface_departure", "refuted"): [("surface_retention", STATUS_SUPPORTED)],
    ("endosomal_entry", "supported"): [("surface_retention", STATUS_EXCLUDED)],
    ("lysosomal_delivery", "supported"): [
        ("lysosomal_delivery_insufficient", STATUS_EXCLUDED),
        ("recycling_dominates_degradation", STATUS_EXCLUDED),
    ],
    ("lysosomal_delivery", "refuted"): [
        ("lysosomal_delivery_insufficient", STATUS_SUPPORTED),
        ("recycling_dominates_degradation", STATUS_SUPPORTED),
    ],
    ("linker_processing", "supported"): [("linker_not_processed", STATUS_EXCLUDED)],
    ("linker_processing", "refuted"): [("linker_not_processed", STATUS_SUPPORTED)],
    ("cytotoxic_sufficiency", "supported"): [("payload_resistance", STATUS_EXCLUDED)],
    ("cytotoxic_sufficiency", "refuted"): [("payload_resistance", STATUS_SUPPORTED)],
}

# Which supplied readiness evidence keys bear on which failure modes, and in
# which direction when the evidence is marked adverse.
EVIDENCE_TO_MODE = {
    "tumor_expression": {"supportive": [("target_density_insufficient", STATUS_EXCLUDED)]},
    "affinity": {"supportive": [("antibody_binding_insufficient", STATUS_EXCLUDED)]},
    "cell_binding": {"supportive": [("antibody_binding_insufficient", STATUS_EXCLUDED)]},
    "normal_tissue_risk": {"adverse": [("normal_tissue_target_expression", STATUS_SUPPORTED)]},
    "internalization": {
        "adverse": [("surface_retention", STATUS_SUPPORTED)],
        "supportive": [("surface_retention", STATUS_EXCLUDED)],
    },
    "naked_tolerability": {"adverse": [("receptor_agonism", STATUS_SUPPORTED)]},
    "receptor_agonism": {"adverse": [("receptor_agonism", STATUS_SUPPORTED)]},
}


def _direction_of(entry: Any) -> str:
    if not isinstance(entry, dict):
        return "supportive" if entry is not None else "absent"
    direction = str(entry.get("direction", "supportive")).lower()
    if direction in {"adverse", "negative", "absent_with_negative_indication"}:
        return "adverse"
    return "supportive"


def resolve_modes(
    cascade: dict[str, Any] | None = None,
    known_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assign every failure mode a status from cascade results and supplied evidence."""
    cascade = cascade or {}
    known_evidence = known_evidence or {}

    status: dict[str, str] = {mode["mode_id"]: STATUS_UNRESOLVED for mode in FAILURE_MODES}
    reasons: dict[str, list[str]] = {mode["mode_id"]: [] for mode in FAILURE_MODES}

    for criterion in cascade.get("criteria") or []:
        key = (criterion["criterion_id"], criterion["status"])
        for mode_id, new_status in CASCADE_TO_MODE.get(key, []):
            # A supported failure mode is never downgraded to excluded by weaker evidence.
            if status[mode_id] == STATUS_SUPPORTED and new_status == STATUS_EXCLUDED:
                continue
            status[mode_id] = new_status
            reasons[mode_id].append(f"delivery cascade: {criterion['criterion_id']} is {criterion['status']}")

    for evidence_key, mapping in EVIDENCE_TO_MODE.items():
        entry = known_evidence.get(evidence_key)
        if entry is None:
            continue
        direction = _direction_of(entry)
        for mode_id, new_status in mapping.get(direction, []):
            if status[mode_id] == STATUS_SUPPORTED and new_status == STATUS_EXCLUDED:
                continue
            status[mode_id] = new_status
            source = entry.get("source") if isinstance(entry, dict) else None
            reasons[mode_id].append(
                f"supplied evidence {evidence_key} ({direction})" + (f" [{source}]" if source else "")
            )

    modes = []
    for mode in FAILURE_MODES:
        modes.append(
            {
                **mode,
                "status": status[mode["mode_id"]],
                "basis": reasons[mode["mode_id"]] or ["no evidence bears on this mode yet"],
            }
        )
    return {
        "modes": modes,
        "by_tree": {
            tree: [item["mode_id"] for item in modes if item["tree"] == tree]
            for tree in (EFFICACY_TREE, TOXICITY_TREE)
        },
        "counts": {
            "total": len(modes),
            "excluded": sum(1 for item in modes if item["status"] == STATUS_EXCLUDED),
            "supported": sum(1 for item in modes if item["status"] == STATUS_SUPPORTED),
            "unresolved": sum(1 for item in modes if item["status"] == STATUS_UNRESOLVED),
        },
        "active_route_terminating_modes": [
            item["mode_id"]
            for item in modes
            if item["status"] == STATUS_SUPPORTED and item["route_terminating"]
        ],
    }


# Weights. Overturning a *supported* route-terminating mode is the highest-value
# action available: that finding is currently what would stop the programme, and
# the evidence behind it is often weaker than the evidence needed to act on it.
WEIGHT_OVERTURN_ROUTE_TERMINATING = 4
WEIGHT_UNRESOLVED_ROUTE_TERMINATING = 2
WEIGHT_UNRESOLVED_OTHER = 1
WEIGHT_OVERTURN_OTHER = 2


def information_gain(
    resolution: dict[str, Any], cascade: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Rank experiments by information gain, respecting prerequisites.

    Two corrections over a naive unresolved-mode count, both of which changed the
    recommended experiment in practice:

    1. **Overturn credit.** An experiment that can *exclude* a mode currently
       ``supported`` by evidence earns the highest weight. A naive count treats a
       supported mode as settled and awards nothing, which is backwards: a
       supported route-terminating mode is precisely what has to be tested,
       especially when the evidence behind it is weak. Without this, the assay
       that directly tests the blocking finding scores zero against it.

    2. **Prerequisite gating.** The delivery cascade is sequential, so a step-3
       measurement is uninterpretable while step 1 is unestablished — a lysosomal
       delivery *fraction* has no meaning without the surface-binding denominator
       and the internalisation baseline. Experiments whose prerequisites are unmet
       are ranked after those that are ready, however high their raw gain.
    """
    cascade = cascade or {}
    status = {item["mode_id"]: item["status"] for item in resolution["modes"]}
    unresolved = {mode_id for mode_id, value in status.items() if value == STATUS_UNRESOLVED}
    supported = {mode_id for mode_id, value in status.items() if value == STATUS_SUPPORTED}
    cascade_status = {item["criterion_id"]: item["status"] for item in (cascade.get("criteria") or [])}

    ranked = []
    for experiment in EXPERIMENTS:
        discriminates = sorted(set(experiment["excludes"]) | set(experiment["supports"]))
        addressable = [mode_id for mode_id in discriminates if mode_id in unresolved]
        # Only modes the experiment can actively exclude count as overturnable.
        overturnable = [mode_id for mode_id in experiment["excludes"] if mode_id in supported]

        gain = sum(
            WEIGHT_UNRESOLVED_ROUTE_TERMINATING
            if MODE_INDEX[mode_id]["route_terminating"]
            else WEIGHT_UNRESOLVED_OTHER
            for mode_id in addressable
        )
        gain += sum(
            WEIGHT_OVERTURN_ROUTE_TERMINATING
            if MODE_INDEX[mode_id]["route_terminating"]
            else WEIGHT_OVERTURN_OTHER
            for mode_id in overturnable
        )

        prerequisites = experiment.get("prerequisite_steps", ())
        unmet = [
            step
            for step in prerequisites
            if cascade_status.get(step, "no_data") != "supported"
        ]

        ranked.append(
            {
                "experiment_id": experiment["experiment_id"],
                "name": experiment["name"],
                "detail": experiment["detail"],
                "phase": experiment["phase"],
                "cost_tier": experiment["cost_tier"],
                "resolves_unresolved_modes": addressable,
                "can_overturn_supported_modes": overturnable,
                "already_resolved_modes": [
                    mode_id
                    for mode_id in discriminates
                    if mode_id not in unresolved and mode_id not in overturnable
                ],
                "information_gain": gain,
                "prerequisite_steps": list(prerequisites),
                "unmet_prerequisites": unmet,
                "ready_to_run": not unmet,
            }
        )

    # Ready experiments first, then by gain. A high-gain experiment whose
    # prerequisites are unmet would produce an uninterpretable result.
    ranked.sort(
        key=lambda item: (
            not item["ready_to_run"],
            -item["information_gain"],
            item["phase"],
            item["experiment_id"],
        )
    )
    actionable = [item for item in ranked if item["ready_to_run"] and item["information_gain"] > 0]
    return {
        "ranked_experiments": ranked,
        "unresolved_mode_count": len(unresolved),
        "unresolved_modes": sorted(unresolved),
        "supported_modes_open_to_challenge": sorted(supported),
        "next_experiment": actionable[0] if actionable else None,
        "blocked_by_prerequisites": [
            {"experiment_id": item["experiment_id"], "unmet_prerequisites": item["unmet_prerequisites"]}
            for item in ranked
            if not item["ready_to_run"]
        ],
        "uninformative_experiments": [
            item["experiment_id"] for item in ranked if item["information_gain"] == 0
        ],
        "gain_definition": (
            f"Unresolved modes score {WEIGHT_UNRESOLVED_ROUTE_TERMINATING} if route-terminating else "
            f"{WEIGHT_UNRESOLVED_OTHER}. Excluding a currently-supported mode scores "
            f"{WEIGHT_OVERTURN_ROUTE_TERMINATING} if route-terminating else {WEIGHT_OVERTURN_OTHER}, "
            "because overturning the finding that would stop the programme is the highest-value action. "
            "Comparative only; it is not a cost-benefit ratio and does not account for assay difficulty."
        ),
    }


def analyse(
    cascade: dict[str, Any] | None = None,
    known_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full failure-mode analysis: resolution plus ranked next experiments."""
    resolution = resolve_modes(cascade, known_evidence)
    gain = information_gain(resolution, cascade)

    terminating = resolution["active_route_terminating_modes"]
    if terminating:
        headline = (
            "Route-terminating failure mode(s) are actively supported by evidence: "
            + ", ".join(terminating)
            + ". Resolve or overturn these before any optimisation spend."
        )
    elif gain["unresolved_mode_count"]:
        headline = (
            f"{gain['unresolved_mode_count']} failure mode(s) unresolved. The highest-information "
            "experiment is listed first."
        )
    else:
        headline = "Every modelled failure mode is resolved."

    return {
        "trees": {"efficacy": EFFICACY_TREE, "toxicity": TOXICITY_TREE},
        "resolution": resolution,
        "experiment_prioritisation": gain,
        "headline": headline,
        "boundary": (
            "The trees enumerate modelled failure modes, not every possible one. An excluded mode is "
            "excluded only to the strength of the evidence cited in its basis."
        ),
    }
