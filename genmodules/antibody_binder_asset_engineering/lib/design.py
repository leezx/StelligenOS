"""Deterministic, auditable engineering-design engine.

This engine is rule-based on purpose. It proposes only substitutions that a
reviewer can trace to a named liability or a named germline deviation, and it
records for every proposal what evidence supports it and what risk it carries.
It does not predict binding, affinity, or expression, and it never claims a
variant is improved: every candidate it emits is a hypothesis for the wet lab.

The seam for a learned designer (ProteinMPNN, ESM, a structure-conditioned
model) is ``propose_mutations``. A model-backed proposer can be added alongside
the rule proposer and merged into the same proposal schema, so downstream stages
do not change when one is introduced.
"""

from __future__ import annotations

import re
from typing import Any

# Conservative substitution rationales. Each entry says why the replacement is
# chemically reasonable, so a reviewer is not asked to trust a lookup table.
SUBSTITUTION_RATIONALE = {
    ("N", "Q"): "Isosteric amide extension; removes the Asn deamidation centre while preserving polarity and H-bonding.",
    ("N", "S"): "Removes the deamidation centre; smaller and still polar, but loses the amide H-bond donor.",
    ("N", "A"): "Removes the deamidation centre; loses polarity, so only appropriate where the side chain is not engaged.",
    ("D", "E"): "Retains the negative charge while blocking succinimide formation at the Asp carbonyl.",
    ("G", "A"): "Blocks the permissive n+1 geometry that accelerates succinimide chemistry; adds a methyl and rigidifies the backbone.",
    ("M", "L"): "Removes the oxidisable thioether; near-isosteric and comparably hydrophobic.",
    ("M", "F"): "Removes the oxidisable thioether; larger aromatic, so packing must be checked.",
    ("M", "V"): "Removes the oxidisable thioether; beta-branched, which may perturb local backbone geometry.",
    ("W", "F"): "Removes the oxidation-prone indole while retaining aromatic bulk and stacking capacity.",
    ("W", "Y"): "Removes the indole while retaining an aromatic ring plus a H-bond donor.",
    ("S", "A"): "Removes the sequon hydroxyl acceptor, abolishing N-linked glycosylation at the paired Asn.",
    ("T", "A"): "Removes the sequon hydroxyl acceptor, abolishing N-linked glycosylation at the paired Asn.",
    ("C", "S"): "Removes a free thiol; isosteric hydroxyl avoids disulfide scrambling and conjugation competition.",
    ("C", "A"): "Removes a free thiol; smaller and apolar.",
}

RISK_TIER_BY_REGION = {"CDR1": "high", "CDR2": "high", "CDR3": "high", "FR1": "low", "FR2": "low", "FR3": "low", "FR4": "low"}

RISK_TIER_ORDER = ("low", "moderate", "high")
# Burial escalates engineering risk because the substitution is a core-packing
# change. It does not escalate binding risk, which is why it raises the tier and
# sets ``requires_fold_confirmation`` rather than ``requires_binding_confirmation``:
# the experiment that settles it is expression and thermostability, not an affinity
# assay.
FOLD_RISK_ESCALATION = {"buried": 2, "partially_buried": 1, "exposed": 0, "unknown": 0}


def _escalate(tier: str, steps: int) -> str:
    if steps <= 0:
        return tier
    try:
        index = RISK_TIER_ORDER.index(tier)
    except ValueError:
        return tier
    return RISK_TIER_ORDER[min(len(RISK_TIER_ORDER) - 1, index + steps)]


def _parse_remediation(option: str) -> tuple[int, str, str] | None:
    """Parse ``"N->Q"``, ``"G+1->A"``, ``"S/T+2->A"`` into (offset, expected_wt, mutant)."""
    match = re.fullmatch(r"([A-Z](?:/[A-Z])*)(?:\+(\d+))?->([A-Z])", option)
    if not match:
        return None
    expected, offset, mutant = match.group(1), int(match.group(2) or 0), match.group(3)
    return offset, expected, mutant


def propose_mutations(
    chains: dict[str, str],
    liabilities: list[dict[str, Any]],
    germline: dict[str, dict[str, Any]] | None = None,
    constraints: dict[str, Any] | None = None,
    position_maps: dict[str, dict[int, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Generate point-mutation proposals from liabilities and germline deviations."""
    constraints = constraints or {}
    germline = germline or {}
    position_maps = position_maps or {}
    protected = _protected_positions(constraints, position_maps)

    proposals: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for hit in liabilities:
        chain = hit["chain"]
        sequence = chains.get(chain) or ""
        for option in hit.get("remediation_options", []):
            parsed = _parse_remediation(option)
            if parsed is None:
                continue
            offset, expected, mutant = parsed
            target = hit["position"] + offset
            if not 1 <= target <= len(sequence):
                continue
            wild_type = sequence[target - 1]
            if wild_type not in expected.split("/"):
                continue
            annotation = position_maps.get(chain, {}).get(target, {})
            region = annotation.get("region", hit["region"])
            key = (chain, target)
            if key in protected:
                rejected.append(
                    {
                        "chain": chain,
                        "position": target,
                        "wild_type": wild_type,
                        "mutant": mutant,
                        "reason": "position is listed in constraints.preserve_residues",
                    }
                )
                continue
            anchor = annotation.get("structural_anchor")
            if anchor:
                # Rejected rather than emitted with a warning. Every other proposal in
                # this module is a trade a reviewer could reasonably take; this one is
                # not, because the anchor is invariant across the fold rather than
                # merely conserved in this lineage. It stays in the record so the
                # liability is visibly seen and visibly declined.
                rejected.append(
                    {
                        "chain": chain,
                        "position": target,
                        "scheme_position": annotation.get("label"),
                        "wild_type": wild_type,
                        "mutant": mutant,
                        "addresses_liability": hit["liability_id"],
                        "reason": f"position is a conserved immunoglobulin structural anchor ({anchor})",
                        "guidance": (
                            "Report the liability, do not substitute. Control the oxidation risk by "
                            "formulation, headspace, and light protection rather than by sequence."
                        ),
                    }
                )
                continue
            exposure_class = hit.get("exposure_class") or "unknown"
            fold_steps = FOLD_RISK_ESCALATION.get(exposure_class, 0)
            base_risk = RISK_TIER_BY_REGION.get(region, "moderate")
            germline_residue = annotation.get("germline_residue")
            # Mutating away from the germline residue costs framework identity. The
            # triage score already prices that in; naming it here stops a reviewer
            # reading "conservative liability removal" as free.
            humanness_cost = bool(germline_residue) and germline_residue == wild_type and mutant != germline_residue
            rationale = SUBSTITUTION_RATIONALE.get(
                (wild_type, mutant), "Conservative substitution at a flagged liability position."
            )
            if humanness_cost:
                rationale += (
                    f" Note that {wild_type} is the closest human germline residue at this position, so this "
                    "liability is encoded by the human germline and shared with every antibody on this V gene. "
                    "Removing it lowers framework identity in exchange for a risk the human repertoire carries."
                )
            proposals.append(
                {
                    "proposal_id": f"{chain.upper()}-{wild_type}{target}{mutant}",
                    "chain": chain,
                    "position": target,
                    "scheme_position": annotation.get("label") or hit.get("scheme_position"),
                    "region": region,
                    "imgt_region": annotation.get("imgt_region", region),
                    "kabat_region": annotation.get("kabat_region"),
                    "region_definitions_agree": annotation.get("region_definitions_agree", True),
                    "wild_type": wild_type,
                    "mutant": mutant,
                    "source": "liability_remediation",
                    "addresses_liability": hit["liability_id"],
                    "mechanism_addressed": hit["mechanism"],
                    "chemical_risk_removed": hit["chemical_risk"],
                    "relative_sasa": hit.get("relative_sasa"),
                    "exposure_class": exposure_class,
                    "rationale": rationale,
                    # Tri-state passthrough: None means the position is outside the
                    # V-gene framework alignment, not that the residue is somatic.
                    "germline_encoded_liability": hit.get("germline_encoded"),
                    "reduces_framework_humanness": humanness_cost,
                    "engineering_risk": _escalate(base_risk, fold_steps),
                    "engineering_risk_basis": (
                        f"{base_risk} from region {region}"
                        + (f", escalated for a {exposure_class} side chain" if fold_steps else "")
                    ),
                    "requires_binding_confirmation": region.startswith("CDR"),
                    "requires_fold_confirmation": fold_steps > 0,
                    "priority": round(hit["chemical_risk"] * hit["functional_consequence"], 2),
                }
            )

    for chain, record in sorted(germline.items()):
        for deviation in record.get("framework_deviations_from_germline", []) or []:
            target = deviation.get("linear_position")
            sequence = chains.get(chain) or ""
            if not target or not 1 <= target <= len(sequence):
                continue
            wild_type = deviation["binder_residue"]
            mutant = deviation["germline_residue"]
            if wild_type == mutant or sequence[target - 1] != wild_type:
                continue
            if (chain, target) in protected:
                rejected.append(
                    {
                        "chain": chain,
                        "position": target,
                        "wild_type": wild_type,
                        "mutant": mutant,
                        "reason": "position is listed in constraints.preserve_residues",
                    }
                )
                continue
            # Region comes from the union map, not from the germline record. Framework
            # identity is computed over IMGT frameworks for comparability, so every
            # deviation arrives labelled FR -- including deviations at positions Kabat
            # places inside CDR-H1 or CDR-H2. Those are affinity-maturation residues,
            # and reverting one is a paratope change wearing a humanisation label.
            annotation = position_maps.get(chain, {}).get(target, {})
            region = annotation.get("region") or deviation.get("region", "FR")
            contested_cdr = region.startswith("CDR")
            anchor = annotation.get("structural_anchor")
            if anchor:
                rejected.append(
                    {
                        "chain": chain,
                        "position": target,
                        "scheme_position": annotation.get("label"),
                        "wild_type": wild_type,
                        "mutant": mutant,
                        "reason": f"position is a conserved immunoglobulin structural anchor ({anchor})",
                    }
                )
                continue
            proposals.append(
                {
                    "proposal_id": f"{chain.upper()}-{wild_type}{target}{mutant}",
                    "chain": chain,
                    "position": target,
                    "scheme_position": deviation.get("scheme_position"),
                    "region": region,
                    "imgt_region": annotation.get("imgt_region") or deviation.get("region"),
                    "kabat_region": annotation.get("kabat_region"),
                    "region_definitions_agree": annotation.get("region_definitions_agree", True),
                    "wild_type": wild_type,
                    "mutant": mutant,
                    "source": "germline_reversion",
                    "mechanism_addressed": (
                        "Deviation from the closest human germline V gene at a position Kabat assigns to "
                        f"{annotation.get('kabat_region')}, i.e. an affinity-maturation residue rather than a "
                        "framework one."
                        if contested_cdr
                        else "Framework deviation from the closest human germline V gene."
                    ),
                    "addresses_liability": None,
                    "chemical_risk_removed": 0.0,
                    "relative_sasa": None,
                    "exposure_class": None,
                    "rationale": (
                        f"Reverts to the human germline residue ({mutant}). IMGT places this position in "
                        f"{annotation.get('imgt_region')}, but Kabat places it in {annotation.get('kabat_region')}, "
                        "so it is a CDR residue by the definition this antibody was matured under. The humanness "
                        "gain is marginal and the affinity risk is real; treat this as a paratope experiment, not "
                        "a humanisation step."
                        if contested_cdr
                        else f"Reverts a framework position to the human germline residue ({mutant}), raising "
                        "framework identity. Humanisation back-mutations were often introduced to support "
                        "binding, so each reversion must be tested rather than assumed neutral."
                    ),
                    # A reversion moves toward the germline by construction, so it can
                    # only raise framework identity.
                    "germline_encoded_liability": False,
                    "reduces_framework_humanness": False,
                    "engineering_risk": "high" if contested_cdr else "moderate",
                    "engineering_risk_basis": (
                        "CDR under Kabat although FR under IMGT" if contested_cdr else "framework under both definitions"
                    ),
                    "requires_binding_confirmation": True,
                    "requires_fold_confirmation": False,
                    "priority": 0.5,
                }
            )

    # One substitution can be justified by more than one rationale: a Met->Leu can
    # both remove an oxidation site and restore the human germline residue. Keeping
    # only the highest-priority rationale would drop that substitution out of the
    # other family entirely and hide the fact that it is a dual-benefit change,
    # which is exactly the kind of mutation a reviewer most wants to see. Merge
    # instead of overwrite.
    deduplicated: dict[str, dict[str, Any]] = {}
    for proposal in proposals:
        existing = deduplicated.get(proposal["proposal_id"])
        if existing is None:
            merged = dict(proposal)
            merged["sources"] = [proposal["source"]]
            merged["addresses_liabilities"] = (
                [proposal["addresses_liability"]] if proposal["addresses_liability"] else []
            )
            merged["rationales"] = [proposal["rationale"]]
            deduplicated[proposal["proposal_id"]] = merged
            continue
        if proposal["source"] not in existing["sources"]:
            existing["sources"].append(proposal["source"])
        if proposal["addresses_liability"] and proposal["addresses_liability"] not in existing["addresses_liabilities"]:
            existing["addresses_liabilities"].append(proposal["addresses_liability"])
        if proposal["rationale"] not in existing["rationales"]:
            existing["rationales"].append(proposal["rationale"])
        if proposal["priority"] > existing["priority"]:
            # Promote the stronger rationale to primary, preserving merged fields.
            carried = {
                key: existing[key] for key in ("sources", "addresses_liabilities", "rationales")
            }
            existing.clear()
            existing.update(proposal)
            existing.update(carried)
        existing["chemical_risk_removed"] = max(
            existing.get("chemical_risk_removed") or 0.0, proposal.get("chemical_risk_removed") or 0.0
        )

    for proposal in deduplicated.values():
        proposal["sources"] = sorted(proposal["sources"])
        proposal["dual_benefit"] = len(proposal["sources"]) > 1
        if proposal["dual_benefit"]:
            # A dual-benefit change is strictly preferable to either rationale alone.
            proposal["priority"] = round(proposal["priority"] + 1.0, 2)

    ordered = sorted(
        deduplicated.values(),
        key=lambda item: (-item["priority"], item["chain"], item["position"], item["mutant"]),
    )
    return {
        "proposals": ordered,
        "dual_benefit_proposals": [item["proposal_id"] for item in ordered if item["dual_benefit"]],
        "rejected": rejected,
        "protected_positions": sorted(f"{chain}:{position}" for chain, position in protected),
        "method": "rule_based_liability_and_germline_proposer",
        "boundary": (
            "Proposals are chemically motivated hypotheses. No binding, stability, or expression "
            "prediction supports them; every proposal needs experimental confirmation."
        ),
    }


def _protected_positions(
    constraints: dict[str, Any], position_maps: dict[str, dict[int, dict[str, Any]]]
) -> set[tuple[str, int]]:
    """Resolve ``constraints.preserve_residues`` into ``(chain, linear_position)`` pairs.

    Accepts ``"vh:33"`` (linear), ``"vh@H33"`` (scheme label), and ``"vh:CDR3"``
    (whole region), so a reviewer can protect a paratope without hand-listing it.
    """
    protected: set[tuple[str, int]] = set()
    for entry in constraints.get("preserve_residues") or []:
        text = str(entry).strip()
        if "@" in text:
            chain, _, label = text.partition("@")
            chain = chain.strip().lower()
            for position, annotation in position_maps.get(chain, {}).items():
                if annotation.get("label") == label.strip():
                    protected.add((chain, position))
            continue
        chain, _, selector = text.partition(":")
        chain = chain.strip().lower()
        selector = selector.strip()
        if selector.isdigit():
            protected.add((chain, int(selector)))
        elif selector:
            for position, annotation in position_maps.get(chain, {}).items():
                if annotation.get("region", "").upper() == selector.upper():
                    protected.add((chain, position))
    return protected


def _apply(chains: dict[str, str], mutations: list[dict[str, Any]]) -> dict[str, str | None]:
    """Apply mutations to a copy of the chains, verifying each wild-type residue."""
    mutated = {name: list(sequence or "") for name, sequence in chains.items()}
    for mutation in mutations:
        chain, position = mutation["chain"], mutation["position"]
        sequence = mutated.get(chain)
        if sequence is None or not 1 <= position <= len(sequence):
            raise ValueError(f"{mutation['proposal_id']}: position outside {chain}")
        if sequence[position - 1] != mutation["wild_type"]:
            raise ValueError(
                f"{mutation['proposal_id']}: expected {mutation['wild_type']} at {chain}:{position}, "
                f"found {sequence[position - 1]}"
            )
        sequence[position - 1] = mutation["mutant"]
    return {name: ("".join(sequence) if sequence else None) for name, sequence in mutated.items()}


FAMILY_SPECIFICATIONS = (
    {
        "family": "conservative_liability_removal",
        "purpose": (
            "Remove exposed framework liabilities only. Lowest functional risk; the safest way to improve the "
            "parent. Requires framework under both CDR definitions and an unescalated risk tier, so a buried "
            "core substitution cannot enter the family that claims to be safest."
        ),
        "accepts": lambda proposal: (
            "liability_remediation" in proposal["sources"]
            and not proposal["region"].startswith("CDR")
            and proposal.get("engineering_risk") == "low"
            and (proposal["chemical_risk_removed"] or 0.0) >= 1.0
        ),
    },
    {
        "family": "developability_optimized",
        "purpose": "Remove the highest-burden liabilities wherever they sit, including CDRs. Highest developability gain, highest binding risk.",
        "accepts": lambda proposal: (
            "liability_remediation" in proposal["sources"] and (proposal["chemical_risk_removed"] or 0.0) >= 1.0
        ),
    },
    {
        "family": "germline_reverted",
        "purpose": (
            "Revert framework positions to the closest human germline. Targets humanness, independent of "
            "chemical liabilities. Restricted to positions both CDR definitions call framework: a reversion at "
            "a Kabat-CDR position is an affinity experiment, and putting it here would let a paratope change "
            "be ordered under a humanisation rationale."
        ),
        "accepts": lambda proposal: (
            "germline_reversion" in proposal["sources"] and not proposal["region"].startswith("CDR")
        ),
    },
)


def generate_candidates(
    binder: dict[str, Any],
    proposals: list[dict[str, Any]],
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the parent plus three independent candidate families.

    Each family yields single-mutation members (so an assay can attribute an
    effect to one change) and one combined member within the mutation budget.
    """
    constraints = constraints or {}
    budget = int(constraints.get("maximum_mutations_per_candidate") or 8)
    forbidden = [motif for motif in (constraints.get("forbidden_motifs") or []) if motif]
    parent_chains = {"vh": binder["sequences"]["vh"], "vl": binder["sequences"].get("vl")}
    binder_id = binder["binder_id"]

    candidates: list[dict[str, Any]] = [
        {
            "candidate_id": f"{binder_id}-PARENT",
            "family": "parent",
            "vh": parent_chains["vh"],
            "vl": parent_chains["vl"],
            "mutations": [],
            "mutation_count": 0,
            "generation_method": "input binder, unmodified",
        }
    ]
    excluded: list[dict[str, Any]] = []

    for specification in FAMILY_SPECIFICATIONS:
        selected = [proposal for proposal in proposals if specification["accepts"](proposal)]
        selected.sort(key=lambda item: (-item["priority"], item["chain"], item["position"]))
        family = specification["family"]

        for index, proposal in enumerate(selected[:budget], start=1):
            record = _build_candidate(
                f"{binder_id}-{_family_code(family)}-S{index:02d}",
                family,
                parent_chains,
                [proposal],
                f"single {proposal['source']} substitution",
                forbidden,
            )
            (candidates if "error" not in record else excluded).append(record)

        combined = _select_within_budget(selected, budget)
        if len(combined) > 1:
            record = _build_candidate(
                f"{binder_id}-{_family_code(family)}-C01",
                family,
                parent_chains,
                combined,
                f"combined {len(combined)} substitutions within the mutation budget",
                forbidden,
            )
            (candidates if "error" not in record else excluded).append(record)

    # A proposal that no family accepts is still a proposal. Tightening the family
    # filters would otherwise make live proposals vanish between stage 04 and 05,
    # which reads as "the module found nothing" instead of "the module found this
    # and declined to package it".
    unfamilied = [
        {
            "proposal_id": proposal["proposal_id"],
            "region": proposal["region"],
            "imgt_region": proposal.get("imgt_region"),
            "kabat_region": proposal.get("kabat_region"),
            "engineering_risk": proposal.get("engineering_risk"),
            "sources": proposal["sources"],
            "reason": (
                "accepted by no candidate family; emitted as a standalone proposal requiring individual review"
            ),
        }
        for proposal in proposals
        if not any(specification["accepts"](proposal) for specification in FAMILY_SPECIFICATIONS)
    ]

    families_built = sorted({candidate["family"] for candidate in candidates} - {"parent"})
    return {
        "candidates": candidates,
        "excluded": excluded,
        "proposals_in_no_family": unfamilied,
        "families_built": families_built,
        "independent_family_count": len(families_built),
        "mutation_budget": budget,
        "forbidden_motifs_screened": forbidden,
        "method": "deterministic_application_of_rule_based_proposals",
        "boundary": (
            "Candidate sequences are constructed, not validated. None has been expressed, "
            "and no binding or developability measurement exists for any of them."
        ),
    }


def _family_code(family: str) -> str:
    return {
        "conservative_liability_removal": "CONS",
        "developability_optimized": "DEV",
        "germline_reverted": "GERM",
        "function_silenced": "SIL",
        "kinetic_ladder": "KIN",
        "valency_clustering": "VAL",
    }.get(family, family[:4].upper())


# ------------------------------------------------ construct-specification families

# The three sequence families above emit real sequences: a variant differing from
# the parent by named point substitutions, which can be ordered as a gene today.
#
# The four families below cannot. Function silencing lives in the Fc, valency is a
# format change, and an affinity ladder needs a selection campaign or a trained
# model to produce reliably. Emitting invented sequences for them would be
# fabrication, so they are emitted as *construct specifications*: what to build,
# why, and what has to be supplied or run first.
#
# Keeping the two kinds visibly separate is the point. A wet-lab reader must be
# able to tell at a glance what is orderable and what is a campaign.

FUNCTION_SILENCED_SPECIFICATIONS: tuple[dict[str, Any], ...] = (
    {
        "construct_id": "P0-parent-IgG1",
        "format": "IgG1",
        "fc_modification": None,
        "valency": 2,
        "purpose": "Reference. Reproduces the clinical molecule's biology, including its agonism.",
    },
    {
        "construct_id": "P1-Fc-silent",
        "format": "IgG1",
        "fc_modification": "Fc-silenced (e.g. LALA-type substitutions in CH2)",
        "valency": 2,
        "purpose": "Removes FcgammaR-dependent crosslinking and effector function while keeping bivalent binding.",
    },
    {
        "construct_id": "P2-Fab",
        "format": "Fab",
        "fc_modification": "not applicable",
        "valency": 1,
        "purpose": "Monovalent, Fc-free. Isolates whether binding alone drives internalisation and signalling.",
    },
    {
        "construct_id": "P3-F(ab')2",
        "format": "F(ab')2",
        "fc_modification": "not applicable",
        "valency": 2,
        "purpose": "Bivalent without Fc. Separates receptor clustering from FcgammaR engagement.",
    },
)

VALENCY_SPECIFICATIONS: tuple[dict[str, Any], ...] = (
    {
        "construct_id": "V1-monovalent-Fab",
        "format": "Fab",
        "valency": 1,
        "purpose": "No clustering possible. Baseline for clustering-dependent effects.",
    },
    {
        "construct_id": "V2-bivalent-IgG",
        "format": "IgG1",
        "valency": 2,
        "purpose": "Standard bivalent clustering.",
    },
    {
        "construct_id": "V3-bivalent-Fc-silent",
        "format": "IgG1",
        "fc_modification": "Fc-silenced",
        "valency": 2,
        "purpose": "Bivalent clustering without FcgammaR contribution.",
    },
    {
        "construct_id": "V4-controlled-multivalent",
        "format": "engineered multivalent",
        "valency": 4,
        "purpose": "Positive control for clustering-driven internalisation and agonism.",
    },
)

KINETIC_LADDER_BANDS: tuple[dict[str, Any], ...] = (
    {"band_id": "K0-parent-like", "target_fold_change": "1x", "purpose": "Reference affinity."},
    {"band_id": "K1-moderately-weakened", "target_fold_change": "3-10x weaker", "purpose": "Tests whether lower affinity improves tumour penetration and reduces antigen sink."},
    {"band_id": "K2-moderately-strengthened", "target_fold_change": "3-10x stronger", "purpose": "Tests whether higher affinity increases uptake or instead worsens the binding-site barrier."},
)

KINETIC_LADDER_READOUTS = (
    "internalised amount per unit surface binding",
    "lysosomal delivery fraction",
    "receptor recycling fraction",
    "spheroid or 3D penetration depth",
    "antigen sink consumption",
    "conjugated cytotoxicity",
)


def construct_specifications(
    binder: dict[str, Any],
    cdr_scan_positions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Emit the four construct-specification families.

    Nothing here is a generated sequence. Each entry states what must be built or
    run, and what input the module still lacks in order to express it as sequence.
    """
    binder_id = binder["binder_id"]
    isotype = binder.get("isotype")
    constant_supplied = bool(binder.get("constant_regions_supplied"))

    sequence_blocker = (
        None
        if constant_supplied
        else "Constant-region sequences are not supplied, so these constructs cannot be emitted as sequences."
    )

    function_silenced = [
        {
            "candidate_id": f"{binder_id}-{_family_code('function_silenced')}-{spec['construct_id']}",
            "family": "function_silenced",
            "entry_kind": "construct_specification",
            "format": spec["format"],
            "fc_modification": spec["fc_modification"],
            "valency": spec["valency"],
            "fv_source": "parent, unmodified",
            "purpose": spec["purpose"],
            "carrier_candidate": True,
            "sequence_available": constant_supplied,
            "sequence_blocker": sequence_blocker,
        }
        for spec in FUNCTION_SILENCED_SPECIFICATIONS
    ]

    valency = [
        {
            "candidate_id": f"{binder_id}-{_family_code('valency_clustering')}-{spec['construct_id']}",
            "family": "valency_clustering",
            "entry_kind": "construct_specification",
            "format": spec["format"],
            "fc_modification": spec.get("fc_modification"),
            "valency": spec["valency"],
            "fv_source": "parent, unmodified",
            "purpose": spec["purpose"],
            "carrier_candidate": True,
            "sequence_available": constant_supplied,
            "sequence_blocker": sequence_blocker,
        }
        for spec in VALENCY_SPECIFICATIONS
    ]

    kinetic = [
        {
            "candidate_id": f"{binder_id}-{_family_code('kinetic_ladder')}-{band['band_id']}",
            "family": "kinetic_ladder",
            "entry_kind": "campaign_specification",
            "target_fold_change": band["target_fold_change"],
            "purpose": band["purpose"],
            "carrier_candidate": True,
            "sequence_available": False,
            "sequence_blocker": (
                "No affinity-modulating sequence is proposed. Predicting the direction and magnitude of an "
                "affinity change requires an antigen-complex structure or a trained model, and this module "
                "has neither. Generate this band by CDR substitution scanning or display selection."
            ),
            "candidate_scan_positions": cdr_scan_positions or [],
        }
        for band in KINETIC_LADDER_BANDS
    ]

    return {
        "families": {
            "function_silenced": {
                "purpose": (
                    "Separate the sources of toxicity and of internalisation: plain antigen binding, "
                    "bivalent receptor clustering, FcgammaR crosslinking, Fc effector function, and payload. "
                    "These are distinguishable only by comparing constructs."
                ),
                "constructs": function_silenced,
                "must_measure_together": [
                    "canonical NF-kB",
                    "alternative NF-kB",
                    "cytokine release",
                    "receptor clustering",
                    "internalisation",
                    "lysosomal trafficking",
                    "conjugate cytotoxicity",
                ],
                "caveat": (
                    "Fc silencing can remove FcgammaR-dependent agonism but is not guaranteed to remove "
                    "agonism arising from receptor clustering by the bivalent Fv itself. Signalling must be "
                    "measured on every construct, not assumed from the format."
                ),
            },
            "valency_clustering": {
                "purpose": "Decouple binding, internalisation, and agonism, which valency affects differently.",
                "constructs": valency,
                "especially_relevant_for": "TNF-receptor-superfamily targets, where clustering drives signalling",
            },
            "kinetic_ladder": {
                "purpose": (
                    "Test the assumption that higher affinity is better. For a carrier, affinity trades "
                    "against tumour penetration, receptor recycling, and antigen sink."
                ),
                "bands": kinetic,
                "readouts": list(KINETIC_LADDER_READOUTS),
                "warning": (
                    "Do not default to maximising affinity. The optimum for payload delivery is not "
                    "necessarily the optimum for binding."
                ),
            },
            "conjugation_format": {
                "purpose": "Compare conjugation chemistries on the same Fv.",
                "handled_by": "lib.product.assemble; conjugation variants are product entities, not antibody entities",
            },
        },
        "isotype_declared": isotype,
        "constant_regions_supplied": constant_supplied,
        "entry_kind_legend": {
            "construct_specification": "A construct to build; requires constant-region sequence input to emit as sequence.",
            "campaign_specification": "Not a single construct; requires a scanning or selection campaign to produce.",
        },
        "boundary": (
            "These families are specifications, not sequences. The module does not fabricate Fc, hinge, or "
            "affinity-modulating sequence it has not been given and cannot predict."
        ),
    }


def _select_within_budget(proposals: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    """Highest-priority proposals, at most one per position, within budget."""
    chosen: list[dict[str, Any]] = []
    occupied: set[tuple[str, int]] = set()
    for proposal in proposals:
        key = (proposal["chain"], proposal["position"])
        if key in occupied:
            continue
        chosen.append(proposal)
        occupied.add(key)
        if len(chosen) >= budget:
            break
    return chosen


def _build_candidate(
    candidate_id: str,
    family: str,
    parent_chains: dict[str, str | None],
    mutations: list[dict[str, Any]],
    method: str,
    forbidden_motifs: list[str],
) -> dict[str, Any]:
    try:
        mutated = _apply(parent_chains, mutations)
    except ValueError as error:
        return {"candidate_id": candidate_id, "family": family, "error": str(error)}

    introduced = [
        motif
        for motif in forbidden_motifs
        if any(motif in (sequence or "") for sequence in mutated.values())
        and not any(motif in (sequence or "") for sequence in parent_chains.values())
    ]
    if introduced:
        return {
            "candidate_id": candidate_id,
            "family": family,
            "error": f"introduces forbidden motif(s): {', '.join(introduced)}",
        }

    return {
        "candidate_id": candidate_id,
        "family": family,
        "vh": mutated["vh"],
        "vl": mutated.get("vl"),
        "mutations": [
            {
                "proposal_id": mutation["proposal_id"],
                "chain": mutation["chain"],
                "position": mutation["position"],
                "scheme_position": mutation["scheme_position"],
                "region": mutation["region"],
                "substitution": f"{mutation['wild_type']}{mutation['position']}{mutation['mutant']}",
                "source": mutation["source"],
                "sources": mutation.get("sources", [mutation["source"]]),
                "dual_benefit": mutation.get("dual_benefit", False),
                "addresses_liability": mutation["addresses_liability"],
                "addresses_liabilities": mutation.get("addresses_liabilities", []),
                "engineering_risk": mutation["engineering_risk"],
                "imgt_region": mutation.get("imgt_region"),
                "kabat_region": mutation.get("kabat_region"),
            }
            for mutation in mutations
        ],
        "mutation_count": len(mutations),
        # Carried at candidate level so the triage ranking shows its own caveats. The
        # Track A score weights liability burden above humanness, so a combined
        # candidate that bundles several changes always ranks well; these flags are
        # what stop a high rank from reading as a recommendation.
        "requires_binding_confirmation": any(mutation["requires_binding_confirmation"] for mutation in mutations),
        "requires_fold_confirmation": any(
            mutation.get("requires_fold_confirmation") for mutation in mutations
        ),
        "reduces_framework_humanness": any(
            mutation.get("reduces_framework_humanness") for mutation in mutations
        ),
        "highest_engineering_risk": (
            max(
                (mutation["engineering_risk"] for mutation in mutations),
                key=lambda tier: RISK_TIER_ORDER.index(tier) if tier in RISK_TIER_ORDER else 0,
            )
            if mutations
            else None
        ),
        "generation_method": method,
    }
