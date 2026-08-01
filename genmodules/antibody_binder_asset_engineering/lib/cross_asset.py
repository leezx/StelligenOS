"""Cross-asset retrieval: which clinical ADCs is this asset most like, and how does it differ.

The point is not to predict success. It is to stop analysing an asset in isolation
when a curated corpus of clinical ADCs is sitting next to it. A reviewer's first
question about a new TWEAKR-KSPi conjugate is "what else looked like this, and what
happened to it" -- and the answer to *how does it differ* is more actionable than
the similarity score, so both are reported per comparator.

Deliberately not embeddings. Similarity is a weighted match over declared,
human-readable attributes, so every point of it can be argued with. An embedding
would rank comparators without letting a reviewer see which attribute drove the
ranking, which is the opposite of what this layer is for.

Two honesty constraints, both learned from the corpus itself:

1. **The KB folder is not an outcome.** ``Approved/2019-RovaT-DLL3.md`` sits in
   ``Approved/`` and its own text reads "未获批。AbbVie于2019年终止". The folder is a
   KB organisation artifact. This module reports it as ``kb_folder`` and never as a
   result.
2. **Coverage is partial.** Only some case files carry the attribute frontmatter.
   The count of usable versus skipped cases is reported, because retrieving over a
   subset while implying the whole corpus is the easiest way to mislead here.
"""

from __future__ import annotations

import pathlib
import re
from typing import Any

import yaml

CASE_FOLDERS = ("Approved", "PhaseI", "PhaseII", "PhaseIII")
REQUIRED_FIELDS = ("target", "payload", "linker_type")

# Payload chemistry families. First match wins, so order most specific first.
PAYLOAD_FAMILIES: tuple[tuple[str, str], ...] = (
    ("topoisomerase_i_dxd", r"dxd|deruxtecan|exatecan|camptothecin|topoisomerase|top1|sn-38|govitecan"),
    ("pbd_dimer", r"\bpbd\b|pyrrolobenzodiazepine|tesirine|talirine"),
    ("calicheamicin", r"calicheamicin|ozogamicin"),
    ("maytansinoid", r"maytansin|dm1|dm4|emtansine|ravtansine|soravtansine"),
    ("auristatin", r"auristatin|mmae|mmaf|vedotin"),
    ("kinesin_spindle_inhibitor", r"\bksp\b|kif11|kinesin spindle"),
    ("duocarmycin", r"duocarmy|\bdb\b|seco-dux"),
    ("amanitin", r"amanitin"),
    ("protein_toxin", r"pseudomonas|exotoxin|pasudotox|gelonin|saporin|ricin"),
    ("eribulin", r"eribulin"),
    ("tubulysin", r"tubulysin"),
)

CONJUGATION_FAMILIES: tuple[tuple[str, str], ...] = (
    ("site_specific", r"site-specific|定点|glycan|transglutaminase|thiobridge|engineered cysteine"),
    ("cysteine", r"cysteine|半胱氨酸|thiol|巯基|maleimide"),
    ("lysine", r"lysine|赖氨酸|amide|nhs"),
)

# Attribute weights. This tuple is the whole similarity policy.
ATTRIBUTE_WEIGHTS: tuple[tuple[str, int], ...] = (
    ("target", 5),
    ("payload_family", 3),
    ("cleavable", 2),
    ("conjugation_family", 1),
    ("dar_band", 1),
)
TOTAL_WEIGHT = sum(weight for _, weight in ATTRIBUTE_WEIGHTS)


def _family(text: str, table: tuple[tuple[str, str], ...]) -> str | None:
    lowered = (text or "").lower()
    for name, pattern in table:
        if re.search(pattern, lowered):
            return name
    return None


# Generic words that appear in target descriptions and identify nothing. Without
# this, "TWEAK receptor (Fn14)" shares the token "receptor" with ROR1, CD71 and
# FR-alpha, and the retrieval reports them as same-target comparators. A false
# same-target claim is the single most misleading output this layer can produce.
TARGET_STOPWORDS = frozenset(
    {
        "receptor", "receptors", "antigen", "antigens", "protein", "proteins", "cell",
        "cells", "surface", "human", "membrane", "ligand", "factor", "growth", "family",
        "superfamily", "member", "associated", "related", "like", "type", "alpha",
        "beta", "gamma", "delta", "chain", "domain", "molecule", "marker", "tumor",
        "tumour", "cluster", "differentiation", "and", "the", "of", "subunit",
    }
)


def _normalise_target(text: str) -> set[str]:
    """Identifying target tokens, so ``TNFRSF12A`` matches ``TWEAKR`` matches ``Fn14``.

    Generic words are dropped: they would otherwise manufacture same-target matches
    between unrelated antigens.
    """
    lowered = (text or "").lower()
    tokens = {
        token
        for token in re.split(r"[^a-z0-9\-]+", lowered)
        if len(token) > 1 and token not in TARGET_STOPWORDS and not token.isdigit()
    }
    synonyms = {
        "tnfrsf12a": {"tweakr", "fn14", "cd266"},
        "tweakr": {"tnfrsf12a", "fn14", "cd266"},
        "fn14": {"tnfrsf12a", "tweakr", "cd266"},
        "erbb2": {"her2"},
        "her2": {"erbb2"},
        "tacstd2": {"trop2", "trop-2"},
        "trop2": {"tacstd2"},
        "tnfrsf17": {"bcma"},
        "bcma": {"tnfrsf17"},
    }
    for token in list(tokens):
        tokens |= synonyms.get(token, set())
    return tokens


def _dar_band(text: str) -> str | None:
    numbers = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", str(text or ""))]
    if not numbers:
        return None
    value = sum(numbers) / len(numbers)
    if value < 2.5:
        return "low_1_2"
    if value < 5.0:
        return "mid_3_4"
    return "high_5_plus"


def _cleavable(text: Any) -> str | None:
    lowered = str(text or "").strip().lower()
    if lowered in {"yes", "y", "true", "是"}:
        return "cleavable"
    if lowered in {"no", "n", "false", "否"}:
        return "non_cleavable"
    return None


def load_cases(root: pathlib.Path | str) -> dict[str, Any]:
    """Parse the clinical ADC corpus into comparable feature records."""
    root = pathlib.Path(root)
    if not root.exists():
        return {
            "status": "unavailable",
            "detail": f"corpus root not found: {root}",
            "cases": [],
            "coverage": {},
        }

    cases: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for folder in CASE_FOLDERS:
        directory = root / folder
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            text = path.read_text(errors="ignore")
            if not text.startswith("---"):
                skipped.append({"file": f"{folder}/{path.name}", "reason": "no frontmatter"})
                continue
            try:
                front = yaml.safe_load(text.split("---", 2)[1]) or {}
            except yaml.YAMLError as error:
                skipped.append({"file": f"{folder}/{path.name}", "reason": f"unparseable frontmatter: {error}"})
                continue
            if not isinstance(front, dict) or not all(front.get(field) for field in REQUIRED_FIELDS):
                skipped.append(
                    {"file": f"{folder}/{path.name}", "reason": "frontmatter lacks target/payload/linker_type"}
                )
                continue
            cases.append(
                {
                    "case_id": path.stem,
                    "kb_folder": folder,
                    "kb_path": f"{folder}/{path.name}",
                    "name": str(front.get("alias") or path.stem).split(";")[0].strip(),
                    "target_text": str(front.get("target")),
                    "target_tokens": sorted(_normalise_target(str(front.get("target")))),
                    "payload_text": str(front.get("payload")),
                    "payload_family": _family(str(front.get("payload")), PAYLOAD_FAMILIES),
                    "linker_text": str(front.get("linker_type")),
                    "cleavable": _cleavable(front.get("cleavable")),
                    "conjugation_family": _family(str(front.get("conjugation")), CONJUGATION_FAMILIES),
                    "dar_text": str(front.get("dar") or ""),
                    "dar_band": _dar_band(front.get("dar")),
                    "bystander_effect": front.get("bystander_effect"),
                    "latest_clinical_entry": front.get("latest_clinical_entry"),
                    "company": front.get("company"),
                }
            )

    return {
        "status": "available" if cases else "empty",
        "corpus_root": str(root),
        "cases": cases,
        "coverage": {
            "usable_cases": len(cases),
            "skipped_cases": len(skipped),
            "skipped_reasons": _tally(skipped),
            "note": (
                "Retrieval runs over usable cases only. Skipped files are real ADCs whose "
                "frontmatter is not yet filled, so absence from the comparator list is not "
                "evidence that no comparator exists."
            ),
        },
        "kb_folder_caveat": (
            "kb_folder is a KB organisation label, not a regulatory outcome. Approved/ contains "
            "Rova-T, which was terminated in 2019. Verified terminal status exists only for the "
            "curated cases in configs/historical_adc_benchmark.yaml; read outcomes from there."
        ),
    }


def _tally(items: list[dict[str, str]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        out[item["reason"]] = out.get(item["reason"], 0) + 1
    return dict(sorted(out.items()))


def asset_features(binder: dict[str, Any]) -> dict[str, Any]:
    """The same feature shape, computed for the asset under analysis."""
    target = binder.get("target") or {}
    payload = binder.get("payload") or {}
    target_text = " ".join(str(target.get(field) or "") for field in ("gene", "protein"))
    linker = str(payload.get("linker") or "")
    declared = bool(payload.get("declared"))
    return {
        "case_id": binder.get("binder_id"),
        "target_text": target_text.strip(),
        "target_tokens": sorted(_normalise_target(target_text)),
        "payload_text": str(payload.get("payload_class") or ""),
        "payload_family": _family(str(payload.get("payload_class") or ""), PAYLOAD_FAMILIES),
        "linker_text": linker,
        # The corpus records cleavable as a yes/no field; here it is inferred from the
        # declared linker description, and left unknown when nothing is declared.
        "cleavable": ("cleavable" if re.search(r"cleav|legumain|protease|valine|hydrazone|disulf", linker.lower()) else None)
        if declared
        else None,
        "conjugation_family": _family(linker, CONJUGATION_FAMILIES),
        "dar_band": None,
        "dar_text": "",
        "payload_declared": declared,
    }


def _compare(asset: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    matched: list[dict[str, Any]] = []
    differing: list[dict[str, Any]] = []
    uncomparable: list[str] = []
    score = 0

    for attribute, weight in ATTRIBUTE_WEIGHTS:
        if attribute == "target":
            left, right = set(asset["target_tokens"]), set(case["target_tokens"])
            if not left or not right:
                uncomparable.append(attribute)
                continue
            shared = sorted(left & right)
            if shared:
                score += weight
                matched.append({"attribute": attribute, "value": ", ".join(shared), "weight": weight})
            else:
                differing.append(
                    {
                        "attribute": attribute,
                        "asset": asset["target_text"],
                        "comparator": case["target_text"],
                        "weight": weight,
                    }
                )
            continue

        left_value, right_value = asset.get(attribute), case.get(attribute)
        if left_value is None or right_value is None:
            uncomparable.append(attribute)
            continue
        if left_value == right_value:
            score += weight
            matched.append({"attribute": attribute, "value": left_value, "weight": weight})
        else:
            differing.append(
                {"attribute": attribute, "asset": left_value, "comparator": right_value, "weight": weight}
            )

    comparable_weight = TOTAL_WEIGHT - sum(
        weight for attribute, weight in ATTRIBUTE_WEIGHTS if attribute in uncomparable
    )
    similarity = None if comparable_weight == 0 else round(score / comparable_weight, 3)
    return {
        "similarity": similarity,
        "matched_weight": score,
        "comparable_weight": comparable_weight,
        # A ratio over a small denominator inflates: a comparator with four
        # uncomparable attributes and one lucky match scores higher than one compared
        # on everything. Ranking uses matched_weight first for that reason, and this
        # flag tells a reviewer the ratio is not comparable across rows.
        "similarity_is_partial": comparable_weight < TOTAL_WEIGHT,
        "similarity_basis_fraction": round(comparable_weight / TOTAL_WEIGHT, 3),
        "matched_attributes": matched,
        "differing_attributes": differing,
        "uncomparable_attributes": uncomparable,
    }


def retrieve(
    binder: dict[str, Any], corpus: dict[str, Any], top_n: int = 5
) -> dict[str, Any]:
    """Rank the corpus against the asset and report what matches and what differs."""
    if corpus.get("status") != "available":
        return {
            "status": corpus.get("status", "unavailable"),
            "detail": corpus.get("detail"),
            "comparators": [],
            "boundary": "No corpus, so no retrieval. This is a missing input, not a negative result.",
        }

    asset = asset_features(binder)
    scored = []
    for case in corpus["cases"]:
        comparison = _compare(asset, case)
        if comparison["similarity"] is None:
            continue
        scored.append(
            {
                "case_id": case["case_id"],
                "name": case["name"],
                "kb_folder": case["kb_folder"],
                "kb_path": case["kb_path"],
                "target": case["target_text"],
                "payload_family": case["payload_family"],
                "payload_text": case["payload_text"],
                "linker": case["linker_text"],
                "dar": case["dar_text"],
                "latest_clinical_entry": case["latest_clinical_entry"],
                **comparison,
            }
        )

    # Absolute matched weight first: it is evidence of similarity that does not shrink
    # when attributes are missing. The ratio only breaks ties among equally-evidenced rows.
    scored.sort(key=lambda item: (-item["matched_weight"], -item["similarity"], item["case_id"]))
    same_target = [item for item in scored if any(
        entry["attribute"] == "target" for entry in item["matched_attributes"]
    )]
    same_payload = [
        item
        for item in scored
        if item["payload_family"] and item["payload_family"] == asset["payload_family"]
    ]
    for item in scored:
        if any(entry["attribute"] == "target" for entry in item["matched_attributes"]):
            item["comparator_strength"] = "strong_same_target"
        elif item["payload_family"] and item["payload_family"] == asset["payload_family"]:
            item["comparator_strength"] = "moderate_same_payload_class"
        else:
            item["comparator_strength"] = "weak_incidental_attributes_only"

    # A ranked list of rows that agree only on an incidental attribute reads as
    # "here are your comparators" when the true answer is "there aren't any". Say so.
    if same_target:
        precedent = {
            "status": "same_target_precedent_exists",
            "detail": f"{len(same_target)} clinical ADC(s) against the same target are on record",
        }
    elif same_payload:
        precedent = {
            "status": "same_payload_class_precedent_only",
            "detail": (
                f"no clinical ADC against this target in the corpus; {len(same_payload)} share the "
                f"payload class {asset['payload_family']}"
            ),
        }
    else:
        precedent = {
            "status": "no_close_precedent",
            "detail": (
                "no clinical ADC in the corpus shares this target or this payload class. The "
                "remaining comparators agree only on incidental attributes and should not be "
                "used to calibrate expectations. Unprecedented on both axes is a finding: there "
                "is no clinical experience to borrow, and no comparator failure to learn from."
            ),
        }

    return {
        "status": "available",
        "asset_features": asset,
        "corpus_root": corpus.get("corpus_root"),
        "coverage": corpus.get("coverage"),
        "kb_folder_caveat": corpus.get("kb_folder_caveat"),
        "precedent": precedent,
        "comparators": scored[:top_n],
        "same_target_comparators": [item["case_id"] for item in same_target],
        "same_target_count": len(same_target),
        "same_payload_family_comparators": [item["case_id"] for item in same_payload],
        "comparator_strength_counts": {
            level: sum(1 for item in scored if item["comparator_strength"] == level)
            for level in ("strong_same_target", "moderate_same_payload_class", "weak_incidental_attributes_only")
        },
        "attribute_policy": [
            {"attribute": attribute, "weight": weight} for attribute, weight in ATTRIBUTE_WEIGHTS
        ],
        "method": "weighted_declared_attribute_match_no_embedding",
        "boundary": (
            "Retrieval compares declared attributes. It does not predict success: a high "
            "similarity to an approved ADC is not evidence this asset will work, and a high "
            "similarity to a terminated one is not evidence it will fail. The differing "
            "attributes are the useful output, because they are what a comparison cannot "
            "transfer."
        ),
        "gate_vector_retrieval_status": (
            "Not implemented here, deliberately. The 45-Gate label vectors are the natural "
            "retrieval key, but they live in the Gate system and this GenModule is contractually "
            "forbidden from computing Gate scores. Retrieval on gate vectors belongs in the Gate "
            "layer, reading configs/historical_adc_benchmark.yaml, whose curated cases carry "
            "verified terminal status."
        ),
    }
