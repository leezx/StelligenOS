"""Two-track Pareto selection.

v0.2.0 produced one composite rank. The problem is not that the weights were
wrong; it is that the two things being combined are not commensurable:

- **Binder quality** is how good the molecule is as a molecule — sequence
  liabilities, humanness, charge, hydrophobicity. Computed from sequence and
  structure.
- **ADC carrier quality** is whether the molecule delivers a payload —
  internalisation, lysosomal flux, conjugation tolerance. Measured, not computed.

A single weighted sum lets a clean sequence compensate for a carrier that does
not internalise, which is exactly the trade a payload-delivery programme must
never make. So the two stay on separate axes and candidates are compared by
Pareto dominance instead.

The consequence, stated plainly in the output: when the carrier axis has no data,
there is no frontier. Every candidate is incomparable on that axis, and the
correct next action is to measure it, not to fall back to ranking on sequence
alone and calling the winner a lead.
"""

from __future__ import annotations

from typing import Any

AXIS_BINDER = "binder_quality"
AXIS_CARRIER = "adc_carrier_quality"


def dominates(left: dict[str, float], right: dict[str, float]) -> bool:
    """True when ``left`` is at least as good on both axes and strictly better on one."""
    at_least_as_good = left[AXIS_BINDER] >= right[AXIS_BINDER] and left[AXIS_CARRIER] >= right[AXIS_CARRIER]
    strictly_better = left[AXIS_BINDER] > right[AXIS_BINDER] or left[AXIS_CARRIER] > right[AXIS_CARRIER]
    return at_least_as_good and strictly_better


def frontier(points: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the non-dominated set over the two axes.

    ``points`` entries need ``candidate_id`` plus both axis values. A candidate
    with ``None`` on either axis is *not* placed at zero — it is set aside as
    incomparable, because a missing measurement is not a bad measurement.
    """
    comparable: list[dict[str, Any]] = []
    incomparable: list[dict[str, Any]] = []
    for point in points:
        binder = point.get(AXIS_BINDER)
        carrier = point.get(AXIS_CARRIER)
        if binder is None or carrier is None:
            incomparable.append(
                {
                    "candidate_id": point["candidate_id"],
                    "binder_quality": binder,
                    "adc_carrier_quality": carrier,
                    "missing_axis": AXIS_BINDER if binder is None else AXIS_CARRIER,
                }
            )
        else:
            comparable.append(point)

    non_dominated: list[dict[str, Any]] = []
    for candidate in comparable:
        if not any(dominates(other, candidate) for other in comparable if other is not candidate):
            non_dominated.append(candidate)

    dominated = [
        point["candidate_id"] for point in comparable if point not in non_dominated
    ]
    non_dominated.sort(key=lambda item: (-item[AXIS_CARRIER], -item[AXIS_BINDER], item["candidate_id"]))

    return {
        "axes": [AXIS_BINDER, AXIS_CARRIER],
        "frontier": [
            {
                "candidate_id": point["candidate_id"],
                "binder_quality": point[AXIS_BINDER],
                "adc_carrier_quality": point[AXIS_CARRIER],
                "family": point.get("family"),
            }
            for point in non_dominated
        ],
        "dominated": dominated,
        "incomparable": incomparable,
        "comparable_count": len(comparable),
        "frontier_size": len(non_dominated),
    }


def select(
    binder_ranking: list[dict[str, Any]],
    carrier_scores: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the two-axis selection from a binder ranking and carrier scores.

    ``carrier_scores`` maps candidate_id to the record returned by
    ``phenotype.carrier_quality``. Candidates absent from it, or scoring ``None``,
    are unmeasured on the carrier axis.
    """
    carrier_scores = carrier_scores or {}
    points: list[dict[str, Any]] = []
    for row in binder_ranking:
        candidate_id = row["candidate_id"]
        carrier_record = carrier_scores.get(candidate_id) or {}
        points.append(
            {
                "candidate_id": candidate_id,
                "family": row.get("family"),
                AXIS_BINDER: row.get("sequence_computational_developability_score"),
                AXIS_CARRIER: carrier_record.get("adc_carrier_quality_score"),
            }
        )

    result = frontier(points)
    measured = [point for point in points if point[AXIS_CARRIER] is not None]

    if not measured:
        result["status"] = "carrier_axis_unmeasured"
        result["headline"] = (
            "No candidate has a measured ADC carrier quality, so there is no two-axis frontier. "
            "Candidates cannot be ranked for ADC use on sequence descriptors alone. The binder-quality "
            "ordering below is a within-track pre-screen for choosing what to build, not a lead ranking."
        )
        result["recommended_action"] = (
            "Measure the delivery cascade on the parent and a small construct panel before selecting a lead."
        )
    elif len(measured) < len(points):
        result["status"] = "carrier_axis_partially_measured"
        result["headline"] = (
            f"{len(measured)} of {len(points)} candidates have a measured carrier quality. The frontier "
            "covers only those; the rest are incomparable rather than inferior."
        )
    else:
        result["status"] = "both_axes_measured"
        result["headline"] = (
            f"Frontier of {result['frontier_size']} non-dominated candidate(s) over binder quality and "
            "measured ADC carrier quality."
        )

    result["boundary"] = (
        "Pareto non-dominance identifies candidates that are not beaten on both axes at once. It does not "
        "choose among them: that requires a programme decision about how much binder quality is worth "
        "trading for delivery, which this module does not make."
    )
    return result
