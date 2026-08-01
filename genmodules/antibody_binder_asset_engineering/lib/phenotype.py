"""ADC carrier phenotype: structured observations, not free text.

This module exists because a boolean ``internalization: true`` has almost no
engineering value. Five physically distinct things get collapsed into that one
word, and an ADC fails if any of them is absent:

1. the antibody leaves the cell surface;
2. it enters the early endosome;
3. it reaches the lysosome;
4. the linker is processed and an active catabolite is released;
5. enough is released to kill the target cell.

An antibody can pass step 1 and fail step 3 by recycling. It can pass step 3 and
fail step 4 with the wrong linker. Reporting these as one criterion makes the
difference invisible, so this module keeps them as five separate criteria and
records which observations bear on each.

Two enforcement rules make the difference between data and an assertion:

- **Metadata is mandatory.** An observation without cell line, target density,
  timepoint, concentration, assay method, replicate count, and uncertainty cannot
  be compared to anything, so it is marked ``unusable`` and cannot support a
  cascade step. It is not silently averaged in.
- **A normalisation basis is mandatory for uptake steps.** The question is never
  "were puncta visible" but "what fraction of surface-bound antibody reached the
  lysosome, in what time". A fraction with no declared denominator is not a
  fraction.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------- measurements

# Each measurement type declares which cascade steps it can inform, and whether a
# high value argues for (``supports``) or against (``refutes``) that step.
MEASUREMENT_TYPES: dict[str, dict[str, Any]] = {
    "surface_binding_4c": {
        "description": "Surface binding at 4 C, where internalisation is arrested.",
        "informs": {},
        "role": "denominator",
        "note": "Provides the normalisation basis for uptake and delivery fractions.",
    },
    "total_uptake_37c": {
        "description": "Total cell-associated antibody at 37 C.",
        "informs": {"surface_departure": "supports"},
        "note": "Total uptake alone cannot distinguish surface-bound from internalised.",
    },
    "surface_retained_fraction": {
        "description": "Fraction of bound antibody still on the surface after incubation.",
        "informs": {"surface_departure": "refutes"},
    },
    "receptor_downregulation": {
        "description": "Loss of surface target after antibody treatment.",
        "informs": {"surface_departure": "supports"},
    },
    "receptor_recovery": {
        "description": "Surface target recovery after antibody-induced depletion.",
        "informs": {"receptor_turnover": "supports"},
    },
    "acid_wash_internalized_fraction": {
        "description": "Acid-wash-resistant (internalised) fraction of bound antibody.",
        "informs": {"endosomal_entry": "supports"},
        "requires_normalization_basis": True,
    },
    "internalization_half_time": {
        "description": "Time to reach half-maximal internalised fraction.",
        "informs": {"endosomal_entry": "supports"},
    },
    "per_cell_accumulation": {
        "description": "Molecules accumulated per cell (pH-sensitive dye or radiolabel).",
        "informs": {"endosomal_entry": "supports"},
        "requires_normalization_basis": True,
    },
    "recycling_fraction": {
        "description": "Fraction returned to the surface or medium rather than degraded.",
        "informs": {"lysosomal_delivery": "refutes"},
    },
    "lysosomal_colocalization": {
        "description": "Colocalisation with LAMP1/LAMP2.",
        "informs": {"lysosomal_delivery": "supports"},
        "note": "Colocalisation is qualitative unless expressed as a delivered fraction.",
    },
    "lysosomal_delivery_fraction": {
        "description": "Fraction of surface-bound antibody delivered to the lysosome per unit time.",
        "informs": {"lysosomal_delivery": "supports"},
        "requires_normalization_basis": True,
        "note": "The headline carrier metric.",
    },
    "catabolite_release": {
        "description": "Release of the active payload catabolite from the conjugate.",
        "informs": {"linker_processing": "supports"},
    },
    "conjugated_vs_unconjugated_binding_shift": {
        "description": "Binding change between conjugate and naked antibody.",
        "informs": {"conjugation_tolerance": "supports"},
    },
    "payload_dependent_killing": {
        "description": "Target-cell killing by the conjugate.",
        "informs": {"cytotoxic_sufficiency": "supports"},
        "requires_counter_screen": True,
    },
    "antigen_negative_counter_screen": {
        "description": "Killing on target-negative cells, establishing antigen dependence.",
        "informs": {},
        "role": "counter_screen",
    },
}

# ------------------------------------------------------------------- cascade

CASCADE_STEPS: tuple[dict[str, Any], ...] = (
    {
        "step": 1,
        "criterion_id": "surface_departure",
        "requirement": "The antibody-target complex leaves the cell surface.",
        "failure_meaning": "Surface retention. The complex stays accessible and no payload enters the cell.",
    },
    {
        "step": 2,
        "criterion_id": "endosomal_entry",
        "requirement": "The complex is internalised into the endosomal compartment.",
        "failure_meaning": "No intracellular pool forms, so no payload can be liberated.",
    },
    {
        "step": 3,
        "criterion_id": "lysosomal_delivery",
        "requirement": "The complex reaches the lysosome rather than recycling.",
        "failure_meaning": "Recycling dominates degradation; the antibody enters and returns without payload release.",
    },
    {
        "step": 4,
        "criterion_id": "linker_processing",
        "requirement": "The linker is processed and an active catabolite is released.",
        "failure_meaning": "Payload stays conjugated and inert despite correct trafficking.",
    },
    {
        "step": 5,
        "criterion_id": "cytotoxic_sufficiency",
        "requirement": "Released payload reaches a cytotoxic intracellular concentration, dependent on target expression.",
        "failure_meaning": "Delivery is real but sub-lethal, or killing is not antigen-dependent.",
    },
)

# Supporting criteria that are not cascade steps but modulate carrier quality.
AUXILIARY_CRITERIA = ("receptor_turnover", "conjugation_tolerance")

REQUIRED_METADATA = (
    "cell_line",
    "endogenous_or_engineered",
    "target_density",
    "timepoint",
    "concentration",
    "assay_method",
    "biological_replicates",
    "uncertainty",
)
VALUE_FIELDS = ("raw_value", "normalized_value")

STATUS_SUPPORTED = "supported"
STATUS_REFUTED = "refuted"
STATUS_NO_DATA = "no_data"
STATUS_CONFLICTING = "conflicting"


def validate_observation(observation: Any, index: int) -> dict[str, Any]:
    """Check one observation against the mandatory metadata schema.

    Returns a record with ``usable`` and, when unusable, exactly why. An
    observation is never partially accepted: a measurement whose context is
    unknown cannot be compared with any other measurement.
    """
    problems: list[str] = []
    if not isinstance(observation, dict):
        return {
            "index": index,
            "usable": False,
            "problems": ["observation must be a mapping"],
            "measurement": None,
        }

    measurement = observation.get("measurement")
    if measurement not in MEASUREMENT_TYPES:
        problems.append(
            f"unknown measurement type {measurement!r}; declare one of: {', '.join(sorted(MEASUREMENT_TYPES))}"
        )

    missing = [field for field in REQUIRED_METADATA if observation.get(field) in (None, "", [])]
    if missing:
        problems.append(f"missing mandatory metadata: {', '.join(missing)}")

    if all(observation.get(field) in (None, "") for field in VALUE_FIELDS):
        problems.append(f"at least one of {', '.join(VALUE_FIELDS)} is required")

    specification = MEASUREMENT_TYPES.get(measurement or "", {})
    if specification.get("requires_normalization_basis") and not observation.get("normalization_basis"):
        problems.append(
            "normalization_basis is required for this measurement; a fraction without a declared "
            "denominator is not a fraction"
        )

    replicates = observation.get("biological_replicates")
    if isinstance(replicates, int) and replicates < 2:
        problems.append("biological_replicates must be at least 2 to support a claim")

    return {
        "index": index,
        "usable": not problems,
        "problems": problems,
        "measurement": measurement,
        "construct": observation.get("construct"),
        "cell_line": observation.get("cell_line"),
        "observation": observation,
    }


def _counter_screen_available(usable: list[dict[str, Any]], construct: Any) -> bool:
    return any(
        record["measurement"] == "antigen_negative_counter_screen"
        and (record["construct"] == construct or construct is None)
        for record in usable
    )


def evaluate_cascade(observations: Any) -> dict[str, Any]:
    """Evaluate the five-step delivery cascade from structured observations."""
    raw = observations if isinstance(observations, list) else []
    validated = [validate_observation(observation, index) for index, observation in enumerate(raw, start=1)]
    usable = [record for record in validated if record["usable"]]
    unusable = [record for record in validated if not record["usable"]]

    criteria: list[dict[str, Any]] = []
    for specification in CASCADE_STEPS:
        criterion_id = specification["criterion_id"]
        supporting: list[dict[str, Any]] = []
        refuting: list[dict[str, Any]] = []
        blocked: list[str] = []

        for record in usable:
            informs = MEASUREMENT_TYPES[record["measurement"]].get("informs", {})
            direction = informs.get(criterion_id)
            if direction is None:
                continue
            specification_meta = MEASUREMENT_TYPES[record["measurement"]]
            if specification_meta.get("requires_counter_screen") and not _counter_screen_available(
                usable, record["construct"]
            ):
                blocked.append(
                    f"{record['measurement']} on {record['cell_line']} cannot support this step without a "
                    "usable antigen_negative_counter_screen: killing must be shown to depend on target expression"
                )
                continue
            entry = {
                "measurement": record["measurement"],
                "construct": record["construct"],
                "cell_line": record["cell_line"],
                "value": record["observation"].get("normalized_value", record["observation"].get("raw_value")),
                "timepoint": record["observation"].get("timepoint"),
                "normalization_basis": record["observation"].get("normalization_basis"),
            }
            (supporting if direction == "supports" else refuting).append(entry)

        if supporting and refuting:
            status = STATUS_CONFLICTING
        elif supporting:
            status = STATUS_SUPPORTED
        elif refuting:
            status = STATUS_REFUTED
        else:
            status = STATUS_NO_DATA

        criteria.append(
            {
                "step": specification["step"],
                "criterion_id": criterion_id,
                "requirement": specification["requirement"],
                "failure_meaning": specification["failure_meaning"],
                "status": status,
                "supporting_observations": supporting,
                "refuting_observations": refuting,
                "blocked_observations": blocked,
            }
        )

    # The cascade is sequential: a later step cannot be credited when an earlier
    # step has no data, because the measurement would have nothing to act on.
    first_unresolved = next(
        (item["criterion_id"] for item in criteria if item["status"] != STATUS_SUPPORTED), None
    )
    for item in criteria:
        if first_unresolved is not None and item["step"] > next(
            entry["step"] for entry in criteria if entry["criterion_id"] == first_unresolved
        ):
            item["gated_by"] = first_unresolved

    resolved = sum(1 for item in criteria if item["status"] == STATUS_SUPPORTED)
    return {
        "criteria": criteria,
        "steps_supported": resolved,
        "steps_total": len(criteria),
        "first_unresolved_step": first_unresolved,
        "usable_observation_count": len(usable),
        # The validated usable records themselves, not only their count. Downstream
        # consumers that need to trace a conclusion back to the measurement that
        # produced it cannot do so from a count, and silently getting an empty list
        # is indistinguishable from having no measurements at all.
        "usable_observations": usable,
        "unusable_observations": unusable,
        "observation_count": len(raw),
        "cascade_complete": first_unresolved is None,
        "boundary": (
            "Each step is evaluated only from observations carrying complete metadata. "
            "Absence of data is reported as no_data and never as a negative result."
        ),
    }


def carrier_quality(cascade: dict[str, Any]) -> dict[str, Any]:
    """Summarise carrier capability into a score, or refuse when there is no data.

    The score is deliberately ``None`` rather than 0 when no usable observation
    exists. A candidate with no phenotype data is *unmeasured*, not bad, and
    placing it at the bottom of a ranking would silently convert missing data
    into a negative finding.
    """
    criteria = cascade.get("criteria") or []
    usable = cascade.get("usable_observation_count", 0)
    if not usable:
        return {
            "adc_carrier_quality_score": None,
            "basis": "no_usable_observations",
            "interpretation": (
                "No observation with complete metadata exists, so carrier capability is unmeasured. "
                "This is not a low score: the candidate cannot be placed on the carrier axis at all "
                "until the delivery cascade is measured."
            ),
            "required_before_scoring": [item["criterion_id"] for item in criteria],
        }

    weights = {
        "surface_departure": 0.10,
        "endosomal_entry": 0.20,
        "lysosomal_delivery": 0.35,
        "linker_processing": 0.15,
        "cytotoxic_sufficiency": 0.20,
    }
    total = earned = 0.0
    for item in criteria:
        weight = weights.get(item["criterion_id"], 0.0)
        if item["status"] == STATUS_NO_DATA:
            continue
        total += weight
        if item["status"] == STATUS_SUPPORTED:
            earned += weight
        elif item["status"] == STATUS_CONFLICTING:
            earned += weight * 0.5
    if not total:
        return {
            "adc_carrier_quality_score": None,
            "basis": "no_step_informed_by_usable_observations",
            "interpretation": "Usable observations exist but none informs a cascade step.",
        }
    return {
        "adc_carrier_quality_score": round(earned / total, 4),
        "basis": "weighted_fraction_of_informed_cascade_steps",
        "coverage": round(total / sum(weights.values()), 3),
        "interpretation": (
            "Fraction of the delivery cascade that measured observations support, over the portion of "
            "the cascade that has any data. Read it together with coverage: a high score at low "
            "coverage means little."
        ),
    }


# ------------------------------------------------------------ modality decision

# Go/no-go rules for a payload-delivering modality. These are target-agnostic ADC
# carrier requirements; each maps to cascade evidence rather than to opinion.
CONTINUE_CONDITIONS: tuple[dict[str, Any], ...] = (
    {"id": "reproducible_internalized_fraction", "requires": "endosomal_entry", "detail": "Reproducible internalised fraction in endogenous target-high cells."},
    {"id": "lysosomal_not_merely_endosomal", "requires": "lysosomal_delivery", "detail": "Confirmed lysosomal entry, not only early endosome."},
    {"id": "binding_retained_after_conjugation", "requires": "conjugation_tolerance", "detail": "Binding retained after conjugation."},
    {"id": "antigen_dependent_cytotoxicity", "requires": "cytotoxic_sufficiency", "detail": "Cytotoxicity depends on target expression."},
    {"id": "delivery_survives_fc_silencing", "requires": "lysosomal_delivery", "detail": "Sufficient delivery retained after Fc silencing.", "needs_construct_comparison": True},
    {"id": "signaling_risk_below_parent", "requires": None, "detail": "Signalling and cytokine risk clearly below the parent IgG1.", "needs_construct_comparison": True},
    {"id": "normal_tissue_safety_window_hypothesis", "requires": None, "detail": "At least one usable normal-tissue safety-window hypothesis."},
)

STOP_CONDITIONS: tuple[dict[str, Any], ...] = (
    {"id": "predominantly_surface_retained", "triggered_by": ("surface_departure", STATUS_REFUTED)},
    {"id": "internalization_requires_fcgr_crosslinking", "triggered_by": None, "detail": "Internalisation depends on FcgammaR crosslinking.", "needs_construct_comparison": True},
    {"id": "delivery_lost_on_fc_silencing", "triggered_by": None, "detail": "Delivery disappears after Fc silencing.", "needs_construct_comparison": True},
    {"id": "lysosomal_delivery_negligible", "triggered_by": ("lysosomal_delivery", STATUS_REFUTED)},
    {"id": "killing_independent_of_target", "triggered_by": ("cytotoxic_sufficiency", STATUS_REFUTED)},
    {"id": "silencing_abolishes_internalization", "triggered_by": None, "detail": "Function silencing also abolishes internalisation.", "needs_construct_comparison": True},
    {"id": "normal_tissue_uptake_comparable", "triggered_by": None, "detail": "Comparable uptake and toxicity in normal liver, pancreas, or kidney cells."},
    {"id": "requires_extreme_dar_or_payload", "triggered_by": None, "detail": "Activity requires extreme DAR or an extreme-potency payload."},
)


def modality_decision(cascade: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the continue / stop rules against cascade evidence."""
    by_id = {item["criterion_id"]: item for item in (cascade.get("criteria") or [])}

    continue_status = []
    for condition in CONTINUE_CONDITIONS:
        required = condition.get("requires")
        if required is None:
            met: bool | None = None
            basis = "not evaluable from the delivery cascade alone"
        else:
            criterion = by_id.get(required)
            if criterion is None or criterion["status"] == STATUS_NO_DATA:
                met = None
                basis = f"{required}: no data"
            else:
                met = criterion["status"] == STATUS_SUPPORTED
                basis = f"{required}: {criterion['status']}"
        continue_status.append(
            {
                "condition_id": condition["id"],
                "detail": condition.get("detail"),
                "met": met,
                "basis": basis,
                "needs_construct_comparison": condition.get("needs_construct_comparison", False),
            }
        )

    triggered = []
    for condition in STOP_CONDITIONS:
        trigger = condition.get("triggered_by")
        if trigger is None:
            continue
        criterion_id, required_status = trigger
        criterion = by_id.get(criterion_id)
        if criterion and criterion["status"] == required_status:
            triggered.append({"condition_id": condition["id"], "basis": f"{criterion_id} is {required_status}"})

    unmet = [item for item in continue_status if item["met"] is not True]
    if triggered:
        decision = "stop_this_route"
        headline = (
            "A stop condition is met. Stopping this route does not stop the target: it may mean a "
            "different epitope or a different modality is required."
        )
    elif not unmet:
        decision = "proceed_to_antibody_optimization"
        headline = "Every continue condition is satisfied; sequence optimisation is justified."
    else:
        decision = "modality_unproven_run_kill_experiment"
        headline = (
            "The modality is unproven. Run the kill experiment before any sequence optimisation: "
            "optimising a carrier that does not deliver payload spends effort on the wrong objective."
        )

    return {
        "decision": decision,
        "headline": headline,
        "continue_conditions": continue_status,
        "continue_conditions_met": sum(1 for item in continue_status if item["met"] is True),
        "continue_conditions_total": len(continue_status),
        "triggered_stop_conditions": triggered,
        "unmet_continue_conditions": [item["condition_id"] for item in unmet],
        "boundary": (
            "Conditions requiring a construct comparison (parent IgG1 versus Fc-silent versus Fab) "
            "cannot be evaluated from single-construct data and are reported as not evaluable."
        ),
    }
