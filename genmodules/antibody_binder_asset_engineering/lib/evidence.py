"""Evidence tiers and confidence propagation.

0.3.1 and earlier reported evidence as a direction: ``supportive``, ``adverse``, or
absent. That is enough to resolve a failure mode but not enough for a reviewer to
ask the next question, which is always "on what strength of evidence?". A patent
sentence and a repeat-dose animal study both read as ``supportive``.

This module keeps direction and adds four separately reported quantities, because
collapsing them into one number is what makes a confidence score untrustworthy:

    direction_agreement  signed agreement among the evidence, in [-1, 1]
    evidence_count       how many entries bear on the criterion
    evidence_diversity   how many distinct tiers those entries span
    evidence_freshness   how old the newest entry is
    confidence_band      a qualitative label derived from all four

``direction_agreement`` is emphatically **not** epistemic confidence in the claim.
Ten patent sentences that agree with each other score 1.0 and justify nothing. It
answers only "do the sources point the same way". ``confidence_band`` is the
composite a reviewer actually means, and it is a coarse label rather than a number
because the inputs do not support more precision than that.

Volume is deliberately *not* folded into ``direction_agreement``. Ten patent
sentences agreeing with each other is not stronger than one animal study; it is one
tier repeated ten times. Diversity and count carry that, so a reviewer can see
"agreement 1.0, one entry, patent tier, 10 years old" and treat it correctly.

``null`` means unmeasured throughout, never poor -- the same rule the carrier
score follows.
"""

from __future__ import annotations

import re
from typing import Any

# The evidence ladder, weakest first. Weight is the only tunable, and this tuple is
# the single place to change the policy.
#
# Ordering note: an internal assay sits below ADC precedent here because that is the
# declared programme policy for this module. It is arguable the other way -- an assay
# on *this* molecule is more specific than a precedent set by a different ADC -- so
# treat the order as a reviewable decision, not a fact about the world.
EVIDENCE_TIERS: tuple[dict[str, Any], ...] = (
    {
        "tier_id": "patent",
        "weight": 1,
        "meaning": "A statement in a patent or application. Written to claim scope, not to report a measurement.",
    },
    {
        "tier_id": "literature",
        "weight": 2,
        "meaning": "Peer-reviewed or conference report on this molecule or its class.",
    },
    {
        "tier_id": "internal_assay",
        "weight": 3,
        "meaning": "An in-house measurement on this molecule with a declared method.",
    },
    {
        "tier_id": "adc_precedent",
        "weight": 4,
        "meaning": "Behaviour established for a comparable ADC, transferred by analogy.",
    },
    {
        "tier_id": "animal_efficacy",
        "weight": 5,
        "meaning": "In vivo efficacy or tolerability in an animal model.",
    },
    {
        "tier_id": "human_evidence",
        "weight": 6,
        "meaning": "Clinical observation in humans.",
    },
)

TIER_INDEX = {tier["tier_id"]: tier for tier in EVIDENCE_TIERS}
MAX_TIER_WEIGHT = max(tier["weight"] for tier in EVIDENCE_TIERS)

# Keyword inference, used only when the input does not declare `evidence_tier`.
# Ordered most specific first; the first match wins.
TIER_PATTERNS: tuple[tuple[str, str], ...] = (
    ("human_evidence", r"phase\s*(i|ii|iii|1|2|3)\b|clinical|patient|nct\d|first-in-human"),
    ("animal_efficacy", r"xenograft|pdx|in vivo|mouse|murine|mice|rat\b|cynomolgus|non-human primate|tolerab"),
    ("adc_precedent", r"adcdb|precedent|class effect|comparable adc|approved adc"),
    # Word-bounded and phrase-anchored: a bare "internal" matches the word
    # "internalisation", which mis-tiered a literature finding as an in-house assay.
    ("internal_assay", r"\bin-house\b|\binternal (?:assay|data|measurement|study|result)s?\b|\bunpublished\b"),
    ("patent", r"\bwo\d|\bus\d|\bep\d|patent|claim set|sequence listing"),
    ("literature", r"\d{4}|et al|j\s|nature|science|cancer|aacr|angew|chem|oncoimmunology|pubmed|doi"),
)

# Freshness bands, in years since the newest entry.
FRESHNESS_CURRENT = 2
FRESHNESS_AGING = 5

# The composite band. Deliberately coarse and rule-based: the inputs are a tier
# guess, a count and a year, which do not support a continuous score.
def confidence_band(strongest_tier: str | None, diversity: int, freshness_band: str) -> dict[str, Any]:
    """Qualitative confidence from tier, diversity and freshness together."""
    if strongest_tier is None:
        return {"band": "unassessable", "reason": "no evidence tier could be assigned"}
    weight = TIER_INDEX[strongest_tier]["weight"]
    if weight <= TIER_INDEX["patent"]["weight"] and diversity <= 1:
        return {
            "band": "weak",
            "reason": "rests on a single patent-tier source; a claim drafted for scope is not a measurement",
        }
    if weight >= TIER_INDEX["animal_efficacy"]["weight"] and diversity >= 2 and freshness_band != "stale":
        return {"band": "strong", "reason": "in vivo or clinical evidence corroborated across tiers and not stale"}
    if freshness_band == "stale":
        return {
            "band": "moderate_but_stale",
            "reason": f"{strongest_tier} evidence, but the newest entry is more than {FRESHNESS_AGING} years old",
        }
    return {"band": "moderate", "reason": f"{strongest_tier} evidence across {diversity} tier(s)"}


DIRECTION_SUPPORTIVE = "supportive"
DIRECTION_ADVERSE = "adverse"
ADVERSE_ALIASES = {"adverse", "negative", "absent_with_negative_indication"}


def classify_tier(entry: Any) -> tuple[str | None, str]:
    """Return ``(tier_id, basis)`` for one evidence entry.

    An explicit ``evidence_tier`` in the input always wins, so a reviewer can
    override the inference without editing this module.
    """
    if not isinstance(entry, dict):
        return None, "entry is not a mapping; no tier assigned"
    declared = entry.get("evidence_tier")
    if declared:
        tier = str(declared).strip().lower()
        if tier in TIER_INDEX:
            return tier, "declared in input as evidence_tier"
        return None, f"declared evidence_tier {declared!r} is not a known tier"
    haystack = " ".join(
        str(entry.get(field) or "") for field in ("source", "version", "finding")
    ).lower()
    for tier_id, pattern in TIER_PATTERNS:
        if re.search(pattern, haystack):
            return tier_id, f"inferred from source text by the {tier_id} pattern"
    return None, "no tier could be inferred from the source text"


def _direction(entry: Any) -> str:
    if not isinstance(entry, dict):
        return DIRECTION_SUPPORTIVE
    value = str(entry.get("direction", DIRECTION_SUPPORTIVE)).strip().lower()
    return DIRECTION_ADVERSE if value in ADVERSE_ALIASES else DIRECTION_SUPPORTIVE


def _year(entry: Any) -> int | None:
    """Newest four-digit year mentioned in ``version``, else in ``source``."""
    if not isinstance(entry, dict):
        return None
    for field in ("version", "source"):
        # The group must wrap the whole year: re.findall returns groups, not matches.
        years = [int(match) for match in re.findall(r"\b((?:19|20)\d{2})\b", str(entry.get(field) or ""))]
        if years:
            return max(years)
    return None


def score_entry(entry: Any, reference_year: int | None = None) -> dict[str, Any]:
    """Tier, direction, year and weight for one evidence entry."""
    tier_id, basis = classify_tier(entry)
    tier_weight = TIER_INDEX[tier_id]["weight"] if tier_id else 0
    year = _year(entry)
    age = None if (year is None or reference_year is None) else max(0, reference_year - year)
    return {
        "tier": tier_id,
        "tier_basis": basis,
        "tier_weight": tier_weight,
        "direction": _direction(entry),
        "year": year,
        "age_years": age,
        "source": entry.get("source") if isinstance(entry, dict) else None,
        "has_caveat": bool(isinstance(entry, dict) and entry.get("caveat")),
    }


def _freshness(ages: list[int]) -> dict[str, Any]:
    if not ages:
        return {"newest_age_years": None, "band": "unknown", "note": "no dated evidence"}
    newest = min(ages)
    if newest <= FRESHNESS_CURRENT:
        band = "current"
    elif newest <= FRESHNESS_AGING:
        band = "aging"
    else:
        band = "stale"
    return {
        "newest_age_years": newest,
        "band": band,
        "note": f"newest supporting entry is {newest} year(s) old",
    }


def confidence_of(entries: list[Any], reference_year: int | None = None) -> dict[str, Any]:
    """Confidence, count, diversity and freshness for a set of evidence entries.

    ``confidence`` is signed agreement weighted by tier: ``(support - adverse) /
    (support + adverse)``. It is scale-free on purpose, so it cannot be inflated by
    piling up entries from one weak tier. ``None`` when nothing bears on the
    criterion -- unmeasured, not low.
    """
    scored = [score_entry(entry, reference_year) for entry in entries if entry is not None]
    if not scored:
        return {
            "direction_agreement": None,
            "confidence_band": {"band": "unassessable", "reason": "no evidence bears on this criterion"},
            "semantics": "null means no evidence bears on this criterion, not low confidence",
            "evidence_count": 0,
            "evidence_diversity": 0,
            "tiers_present": [],
            "evidence_freshness": _freshness([]),
            "strongest_tier": None,
            "entries": [],
        }

    support = sum(item["tier_weight"] for item in scored if item["direction"] == DIRECTION_SUPPORTIVE)
    adverse = sum(item["tier_weight"] for item in scored if item["direction"] == DIRECTION_ADVERSE)
    total = support + adverse
    agreement = None if total == 0 else round((support - adverse) / total, 3)

    tiers = sorted({item["tier"] for item in scored if item["tier"]}, key=lambda t: TIER_INDEX[t]["weight"])
    ages = [item["age_years"] for item in scored if item["age_years"] is not None]
    freshness = _freshness(ages)
    strongest = tiers[-1] if tiers else None
    return {
        "direction_agreement": agreement,
        "semantics": (
            "direction_agreement is tier-weighted signed agreement in [-1, 1]. It says whether the "
            "sources point the same way, NOT how much to believe them: ten agreeing patent lines "
            "score 1.0. Read confidence_band, which combines tier, diversity and freshness."
        ),
        "confidence_band": confidence_band(strongest, len(tiers), freshness["band"]),
        "evidence_count": len(scored),
        "evidence_diversity": len(tiers),
        "tiers_present": tiers,
        "strongest_tier": strongest,
        "support_weight": support,
        "adverse_weight": adverse,
        "untiered_entries": sum(1 for item in scored if not item["tier"]),
        "entries_with_caveats": sum(1 for item in scored if item["has_caveat"]),
        "evidence_freshness": freshness,
        "entries": scored,
    }


def propagate(
    known_evidence: dict[str, Any] | None, reference_year: int | None = None
) -> dict[str, Any]:
    """Per-criterion confidence for every supplied evidence key, plus an aggregate.

    Each criterion here carries at most one entry in the frozen input, so the
    per-criterion figures are mostly a tier readout; the aggregate is where count,
    diversity and freshness become informative about the dossier as a whole.
    """
    known_evidence = known_evidence or {}
    criteria: dict[str, Any] = {}
    for key in sorted(known_evidence):
        criteria[key] = confidence_of([known_evidence.get(key)], reference_year)

    populated = [entry for entry in known_evidence.values() if entry is not None]
    aggregate = confidence_of(populated, reference_year)
    weakest = [
        key
        for key, record in criteria.items()
        if record["evidence_count"] and record["strongest_tier"] == "patent"
    ]
    return {
        "reference_year": reference_year,
        "tier_policy": [
            {"tier_id": tier["tier_id"], "weight": tier["weight"], "meaning": tier["meaning"]}
            for tier in EVIDENCE_TIERS
        ],
        "criteria": criteria,
        "aggregate": {key: value for key, value in aggregate.items() if key != "entries"},
        "criteria_resting_on_patent_text_only": weakest,
        "unpopulated_criteria": sorted(key for key, value in known_evidence.items() if value is None),
        "method": "tier_weighted_signed_agreement_with_separate_volume_and_freshness",
        "boundary": (
            "These figures describe the evidence, not the molecule, and they are not an "
            "epistemic-confidence contract. direction_agreement measures only whether sources "
            "point the same way; confidence_band is a coarse rule over tier, diversity and "
            "freshness. Neither substitutes for the experiment."
        ),
    }
