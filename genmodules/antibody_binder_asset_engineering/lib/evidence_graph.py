"""The reasoning graph: Observation -> Hypothesis -> Failure mode -> Decision -> Experiment.

Every edge in this graph was already being computed in 0.3.1. None of it was
visible. The pipeline would report ``internalization = adverse`` and then recommend
a kill experiment, and a reviewer asking *why that one and not lysosomal
trafficking* had to read ``failure_modes.information_gain`` to find out.

So this module adds no science. It reifies the reasoning that existed only as
control flow, and it does one thing the code did not do: it records why each
alternative was **not** chosen. A recommendation without its rejected alternatives
is an assertion, not an argument.

Node kinds, in dependency order:

    observation   a supplied evidence entry or a usable carrier measurement
    hypothesis    a delivery-cascade criterion or a readiness criterion
    failure_mode  a modelled way the programme fails
    decision      the modality go/no-go
    experiment    a ranked next action

Edges carry ``because``: the sentence a reviewer reads instead of the source.
"""

from __future__ import annotations

from typing import Any

from . import evidence as evidence_lib
from . import failure_modes

NODE_ORDER = ("observation", "hypothesis", "failure_mode", "decision", "experiment")


def _node(node_id: str, kind: str, label: str, **fields: Any) -> dict[str, Any]:
    return {"node_id": node_id, "kind": kind, "label": label, **fields}


def _edge(source: str, target: str, relation: str, because: str) -> dict[str, Any]:
    return {"from": source, "to": target, "relation": relation, "because": because}


def build(
    known_evidence: dict[str, Any] | None,
    cascade: dict[str, Any] | None,
    resolution: dict[str, Any] | None,
    gain: dict[str, Any] | None,
    decision: dict[str, Any] | None,
    confidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the traceable graph from artifacts the pipeline already produced."""
    known_evidence = known_evidence or {}
    cascade = cascade or {}
    resolution = resolution or {}
    gain = gain or {}
    decision = decision or {}
    per_criterion = (confidence or {}).get("criteria") or {}

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    # --- observations -------------------------------------------------------
    for key in sorted(known_evidence):
        entry = known_evidence.get(key)
        if entry is None:
            continue
        record = per_criterion.get(key) or {}
        detail = entry if isinstance(entry, dict) else {"finding": entry}
        nodes.append(
            _node(
                f"observation:{key}",
                "observation",
                key,
                direction=evidence_lib._direction(entry),
                source=detail.get("source"),
                tier=record.get("strongest_tier"),
                direction_agreement=record.get("direction_agreement"),
                confidence_band=(record.get("confidence_band") or {}).get("band"),
                caveat=detail.get("caveat"),
            )
        )

    # `usable_observations`, not `observations`: evaluate_cascade never emitted a key
    # by the latter name, so this loop silently produced nothing and the measured
    # evidence layer was absent from every graph. It was invisible on binders with no
    # carrier data, which is exactly when a missing layer looks correct.
    for index, observation in enumerate((cascade.get("usable_observations") or []), start=1):
        nodes.append(
            _node(
                f"observation:measurement_{index}",
                "observation",
                observation.get("measurement", f"measurement_{index}"),
                direction="measured",
                tier="internal_assay",
                confidence=None,
            )
        )

    # --- hypotheses: the cascade criteria -----------------------------------
    for criterion in cascade.get("criteria") or []:
        criterion_id = criterion["criterion_id"]
        nodes.append(
            _node(
                f"hypothesis:{criterion_id}",
                "hypothesis",
                criterion_id,
                status=criterion.get("status"),
                gated_by=criterion.get("gated_by"),
            )
        )

    # --- hypotheses: readiness criteria that map onto failure modes ---------
    for key in sorted(failure_modes.EVIDENCE_TO_MODE):
        if known_evidence.get(key) is None:
            continue
        node_id = f"hypothesis:{key}"
        if not any(node["node_id"] == node_id for node in nodes):
            nodes.append(_node(node_id, "hypothesis", key, status="from_supplied_evidence"))
        edges.append(
            _edge(
                f"observation:{key}",
                node_id,
                "bears_on",
                f"supplied evidence {key} is the only input bearing on this criterion",
            )
        )

    # --- failure modes ------------------------------------------------------
    mode_status: dict[str, str] = {}
    for mode in resolution.get("modes") or []:
        mode_id = mode["mode_id"]
        mode_status[mode_id] = mode["status"]
        nodes.append(
            _node(
                f"failure_mode:{mode_id}",
                "failure_mode",
                mode_id,
                status=mode["status"],
                route_terminating=failure_modes.MODE_INDEX[mode_id]["route_terminating"],
                tree=mode.get("tree"),
                basis=mode.get("basis"),
            )
        )

    # Evidence -> mode edges, using the same table resolve_modes used.
    for key, mapping in sorted(failure_modes.EVIDENCE_TO_MODE.items()):
        entry = known_evidence.get(key)
        if entry is None:
            continue
        direction = evidence_lib._direction(entry)
        for mode_id, resulting in mapping.get(direction, []):
            edges.append(
                _edge(
                    f"hypothesis:{key}",
                    f"failure_mode:{mode_id}",
                    resulting,
                    f"{key} is {direction}, which sets {mode_id} to {resulting}",
                )
            )

    # Cascade -> mode edges.
    for criterion in cascade.get("criteria") or []:
        criterion_id, status = criterion["criterion_id"], criterion.get("status")
        for mode_id, resulting in failure_modes.CASCADE_TO_MODE.get((criterion_id, status), []):
            edges.append(
                _edge(
                    f"hypothesis:{criterion_id}",
                    f"failure_mode:{mode_id}",
                    resulting,
                    f"cascade step {criterion_id} is {status}, which sets {mode_id} to {resulting}",
                )
            )

    # --- decision -----------------------------------------------------------
    verdict = decision.get("decision") or "undetermined"
    nodes.append(
        _node(
            "decision:modality",
            "decision",
            verdict,
            rationale=decision.get("rationale"),
            triggered_rules=decision.get("triggered_conditions") or decision.get("matched_conditions"),
        )
    )
    for mode_id, status in sorted(mode_status.items()):
        if status == failure_modes.STATUS_SUPPORTED:
            edges.append(
                _edge(
                    f"failure_mode:{mode_id}",
                    "decision:modality",
                    "drives",
                    f"{mode_id} is supported"
                    + (
                        " and is route-terminating, so it alone can stop the programme"
                        if failure_modes.MODE_INDEX[mode_id]["route_terminating"]
                        else ""
                    ),
                )
            )

    # --- experiments --------------------------------------------------------
    ranked = gain.get("ranked_experiments") or []
    chosen = gain.get("next_experiment") or {}
    chosen_id = chosen.get("experiment_id")
    for item in ranked:
        experiment_id = item["experiment_id"]
        nodes.append(
            _node(
                f"experiment:{experiment_id}",
                "experiment",
                experiment_id,
                information_gain=item["information_gain"],
                ready_to_run=item["ready_to_run"],
                cost_tier=item["cost_tier"],
                selected=experiment_id == chosen_id,
            )
        )
        for mode_id in item.get("can_overturn_supported_modes") or []:
            edges.append(
                _edge(
                    f"failure_mode:{mode_id}",
                    f"experiment:{experiment_id}",
                    "overturnable_by",
                    f"{mode_id} is currently supported and this experiment can exclude it, "
                    f"which is the highest-weighted action available",
                )
            )
        for mode_id in item.get("resolves_unresolved_modes") or []:
            edges.append(
                _edge(
                    f"failure_mode:{mode_id}",
                    f"experiment:{experiment_id}",
                    "resolvable_by",
                    f"{mode_id} is unresolved and this experiment discriminates it",
                )
            )
    if chosen_id:
        edges.append(
            _edge(
                "decision:modality",
                f"experiment:{chosen_id}",
                "selects",
                f"highest information gain ({chosen.get('information_gain')}) among experiments "
                f"whose prerequisites are met",
            )
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "node_counts": {kind: sum(1 for node in nodes if node["kind"] == kind) for kind in NODE_ORDER},
        "layers": list(NODE_ORDER),
        "why_selected": _why(chosen, mode_status, edges),
        "rejected_alternatives": _rejected(ranked, chosen_id, mode_status),
        "hypotheses_without_observations": _orphans(nodes, edges),
        "method": "reification_of_existing_stage_outputs_no_new_inference",
        "boundary": (
            "The graph reports the pipeline's own reasoning. An edge is as strong as the "
            "observation it starts from; a supported failure mode resting on one patent "
            "sentence produces the same edge as one resting on an animal study, which is why "
            "observation nodes carry tier and confidence."
        ),
    }


def _why(chosen: dict[str, Any], mode_status: dict[str, str], edges: list[dict[str, Any]]) -> dict[str, Any]:
    """The chain a reviewer reads: which observation makes the top experiment decisive."""
    if not chosen:
        return {"selected_experiment": None, "reason": "no experiment is both ready to run and informative"}
    experiment_node = f"experiment:{chosen['experiment_id']}"
    overturns = chosen.get("can_overturn_supported_modes") or []
    resolves = chosen.get("resolves_unresolved_modes") or []
    upstream = [
        edge["from"].split(":", 1)[1]
        for edge in edges
        if edge["to"].startswith("failure_mode:")
        and edge["to"].split(":", 1)[1] in set(overturns)
    ]
    return {
        "selected_experiment": chosen["experiment_id"],
        "information_gain": chosen.get("information_gain"),
        "overturns_supported_modes": overturns,
        "resolves_unresolved_modes": resolves,
        "traces_back_to_criteria": sorted(set(upstream)),
        "chain": [
            "observation(s) on " + (", ".join(sorted(set(upstream))) or "no single criterion"),
            "-> failure mode(s) " + (", ".join(overturns + resolves) or "none"),
            f"-> decision -> experiment {chosen['experiment_id']}",
        ],
        "reason": (
            f"It can exclude {len(overturns)} currently-supported mode(s) and resolve "
            f"{len(resolves)} unresolved one(s), and its prerequisites are met."
        ),
    }


def _rejected(
    ranked: list[dict[str, Any]], chosen_id: str | None, mode_status: dict[str, str]
) -> list[dict[str, Any]]:
    """Why every other experiment was not selected. This is the reviewer's question."""
    chosen_gain = next(
        (item["information_gain"] for item in ranked if item["experiment_id"] == chosen_id), None
    )
    out: list[dict[str, Any]] = []
    for item in ranked:
        if item["experiment_id"] == chosen_id:
            continue
        if not item["ready_to_run"]:
            reason_code = "blocked_by_prerequisite"
            reason = (
                "its result would be uninterpretable: the cascade step(s) "
                f"{', '.join(item['unmet_prerequisites'])} are not established, so this "
                "measurement has no denominator or baseline"
            )
        elif item["information_gain"] == 0:
            reason_code = "no_information_gain"
            reason = (
                "every failure mode it discriminates is already resolved, so running it "
                "cannot change any conclusion"
            )
        else:
            reason_code = "lower_information_gain"
            would_address = (item.get("can_overturn_supported_modes") or []) + (
                item.get("resolves_unresolved_modes") or []
            )
            settled = item.get("already_resolved_modes") or []
            reason = (
                f"informative (gain {item['information_gain']}) but lower than the selected "
                f"experiment (gain {chosen_gain}). It would address "
                + (", ".join(would_address) if would_address else "no open mode")
                + (
                    "; " + ", ".join(settled) + " already resolved, so it re-tests them"
                    if settled
                    else ""
                )
            )
        out.append(
            {
                "experiment_id": item["experiment_id"],
                "information_gain": item["information_gain"],
                "cost_tier": item["cost_tier"],
                "reason_code": reason_code,
                "reason": reason,
            }
        )
    return out


def _orphans(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Hypotheses no observation reaches. These are the dossier's real holes."""
    reached = {edge["to"] for edge in edges if edge["from"].startswith("observation:")}
    return [
        {"criterion": node["label"], "status": node.get("status")}
        for node in nodes
        if node["kind"] == "hypothesis" and node["node_id"] not in reached
    ]
