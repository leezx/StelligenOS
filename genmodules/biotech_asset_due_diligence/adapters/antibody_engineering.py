"""Read-only adapter for the stabilized antibody GenModule package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..core.artifact_refs import ArtifactRef
from ..core.entities import (
    AssessmentRun,
    Asset,
    AssetVariant,
    DecisionUncertainty,
    EvidenceClaim,
    EvidenceSource,
    ExperimentBranch,
    FailureMode,
    Hypothesis,
    Observation,
    SystemRecommendation,
)
from ..core.ids import stable_id


EXPECTED_MODULE = "antibody_binder_asset_engineering"
SUPPORTED_VERSIONS = {"0.4.0"}
EXPECTED_OUTPUTS = {"AntibodyAssetEngineeringPackage@0.4.0"}
EXPECTED_MANIFESTS = {"AntibodyAssetRunManifest@0.4.0"}


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping: {path}")
    return value


def _source_and_claims(normalized: dict[str, Any], subject_ref: str) -> tuple[list[EvidenceSource], list[EvidenceClaim]]:
    sources: dict[str, EvidenceSource] = {}
    claims: list[EvidenceClaim] = []
    for key, entry in (normalized.get("known_evidence") or {}).items():
        if not isinstance(entry, dict) or not entry.get("finding"):
            continue
        locator = str(entry.get("source") or f"unknown-source:{key}")
        source_id = stable_id("source", locator)
        if source_id not in sources:
            sources[source_id] = EvidenceSource(
                source_id=source_id,
                source_type="reported_evidence_locator" if entry.get("source") else "unknown",
                canonical_locator=locator,
                retrieval_date=None,
                checksum=None,
            )
        claims.append(
            EvidenceClaim(
                claim_id=stable_id("claim", {"source": source_id, "criterion": key, "finding": entry["finding"]}),
                source_id=source_id,
                assertion=str(entry["finding"]),
                subject_ref=subject_ref,
                direction=str(entry.get("direction") or "neutral"),
                directness="analogous" if key in {"tumor_expression", "normal_tissue_risk"} else "unknown",
            )
        )
    return list(sources.values()), claims


def load_validated_artifact(
    input_record: dict[str, Any],
    workspace_root: Path,
) -> tuple[Asset, AssetVariant, AssessmentRun, dict[str, Any]]:
    """Verify the upstream package before reading any evidence from it."""
    asset_data = input_record["asset"]
    variant_data = input_record["variant"]
    asset = Asset(**asset_data)
    variant = AssetVariant(
        variant_id=variant_data["variant_id"],
        asset_id=asset.asset_id,
        variant_kind=variant_data["variant_kind"],
        molecular_identity_refs=tuple(variant_data.get("molecular_identity_refs", [])),
        indication_context_ids=tuple(variant_data.get("indication_context_ids", [])),
        parent_variant_id=variant_data.get("parent_variant_id"),
    )

    manifest_spec = input_record["upstream_manifest"]
    normalized_spec = input_record["upstream_normalized_input"]
    manifest_ref = ArtifactRef(
        artifact_id="artifact:upstream-manifest",
        path=manifest_spec["path"],
        root_env=manifest_spec.get("root_env"),
        sha256=manifest_spec["sha256"],
        bytes=int(manifest_spec["bytes"]),
        producer_contract=str(manifest_spec.get("producer_contract") or "AntibodyAssetRunManifest@0.4.0"),
    )
    normalized_ref = ArtifactRef(
        artifact_id="artifact:upstream-normalized-input",
        path=normalized_spec["path"],
        root_env=normalized_spec.get("root_env"),
        sha256=normalized_spec["sha256"],
        bytes=int(normalized_spec["bytes"]),
        producer_contract=str(normalized_spec.get("producer_contract") or "AntibodyAssetEngineeringPackage@0.4.0"),
    )
    manifest_path = manifest_ref.verify(workspace_root)
    normalized_path = normalized_ref.verify(workspace_root)
    manifest = _load(manifest_path)
    if manifest.get("manifest_contract") not in EXPECTED_MANIFESTS:
        raise ValueError("unsupported upstream antibody manifest contract")
    if manifest.get("module_id") != EXPECTED_MODULE or manifest.get("module_version") not in SUPPORTED_VERSIONS:
        raise ValueError("upstream antibody module identity mismatch")
    if manifest.get("output_contract") not in EXPECTED_OUTPUTS:
        raise ValueError("upstream antibody output contract mismatch")
    if (manifest.get("contract_validation") or {}).get("status") != "passed":
        raise ValueError("upstream artifact has no passed contract validation receipt")
    if len(manifest.get("execution_order", [])) != 14:
        raise ValueError("upstream artifact is not the frozen 14-stage package")
    normalized = _load(normalized_path)
    if normalized.get("input_contract") != "ExistingBinderAssetInput@0.4.0":
        raise ValueError("normalized input contract mismatch")

    assessment_id = stable_id(
        "assessment",
        {"asset": asset.asset_id, "variant": variant.variant_id, "cutoff": input_record.get("evidence_cutoff", "upstream-run")},
    )
    assessment = AssessmentRun(
        assessment_run_id=assessment_id,
        asset_id=asset.asset_id,
        variant_ids=(variant.variant_id,),
        evidence_cutoff=str(input_record.get("evidence_cutoff", "upstream-run")),
        adapter_versions=("antibody_engineering_adapter@0.1.0",),
        policy_versions=("phase1a_recommendation_policy@0.1.0",),
        reviewer_context=input_record.get("reviewer_context"),
        artifact_refs=(manifest_ref, normalized_ref),
    )
    return asset, variant, assessment, {"manifest": manifest, "normalized_input": normalized}


def build_vertical_slice(input_record: dict[str, Any], workspace_root: Path) -> dict[str, Any]:
    asset, variant, assessment, upstream = load_validated_artifact(input_record, workspace_root)
    subject_ref = variant.variant_id
    sources, claims = _source_and_claims(upstream["normalized_input"], subject_ref)
    internalization_claims = [claim for claim in claims if "internal" in claim.assertion.lower()]
    claim_ids = tuple(claim.claim_id for claim in internalization_claims)
    observation_id = stable_id("observation", {"subject": subject_ref, "measurement": "productive_internalization"})
    observation = Observation(
        observation_id=observation_id,
        subject_ref=subject_ref,
        measurement_type="productive_internalization",
        value=None,
        unit=None,
        quality_status="unusable",
        source_claim_ids=claim_ids,
        context={"reason": "narrative evidence lacks structured assay metadata; no value inferred"},
    )
    hypothesis = Hypothesis(
        hypothesis_id=stable_id("hypothesis", {"subject": subject_ref, "question": "productive_payload_delivery"}),
        statement="The antibody construct can deliver payload productively in the intended context.",
        subject_ref=subject_ref,
        state="unresolved",
        supporting_claim_ids=claim_ids,
        observation_ids=(observation.observation_id,),
        falsification_criteria=("validated intracellular payload release is absent", "target-negative control is not selective"),
    )
    failure_mode = FailureMode(
        failure_mode_id=stable_id("failure_mode", {"name": "productive_delivery_unproven", "subject": subject_ref}),
        catalog_ref="dd_phase1a_failure_catalog@0.1.0#productive_delivery_unproven",
        status="unresolved",
        route_terminating=False,
        basis_refs=(hypothesis.hypothesis_id, observation.observation_id),
        blocking_for_advance=True,
    )
    uncertainty = DecisionUncertainty(
        uncertainty_id=stable_id("uncertainty", {"subject": subject_ref, "question": "advance_without_delivery"}),
        decision_question="Can this product branch advance before productive payload delivery is measured?",
        candidate_actions=("advance", "hold_for_evidence", "abandon_route"),
        blocking_refs=(failure_mode.failure_mode_id,),
        resolution_experiment_ids=(),
    )
    experiment = ExperimentBranch(
        experiment_id=stable_id("experiment", {"subject": subject_ref, "question": "productive_delivery_panel"}),
        question="Does the construct show target-dependent intracellular payload delivery with usable controls?",
        hypothesis_ids=(hypothesis.hypothesis_id,),
        readiness_status="ready",
        outcome_branches=(
            {"condition": "productive_delivery_supported", "probability": None, "decision_transition": "advance", "failure_mode_updates": {failure_mode.failure_mode_id: "excluded"}},
            {"condition": "productive_delivery_not_supported", "probability": None, "decision_transition": "abandon_route", "failure_mode_updates": {failure_mode.failure_mode_id: "supported"}},
        ),
    )
    uncertainty = DecisionUncertainty(
        uncertainty_id=uncertainty.uncertainty_id,
        decision_question=uncertainty.decision_question,
        candidate_actions=uncertainty.candidate_actions,
        blocking_refs=uncertainty.blocking_refs,
        resolution_experiment_ids=(experiment.experiment_id,),
    )
    recommendation = SystemRecommendation(
        recommendation_id=stable_id("recommendation", {"assessment": assessment.assessment_run_id, "action": "hold_for_evidence"}),
        assessment_run_id=assessment.assessment_run_id,
        policy_version="phase1a_recommendation_policy@0.1.0",
        action="hold_for_evidence",
        rejected_alternatives=(
            {"action": "advance", "reason": "critical productive-delivery observation is unusable or unmeasured"},
            {"action": "abandon_route", "reason": "the current evidence does not establish failure"},
        ),
        basis_refs=(failure_mode.failure_mode_id, uncertainty.uncertainty_id, experiment.experiment_id),
    )
    return {
        "asset": asset.as_dict(),
        "asset_variant": variant.as_dict(),
        "assessment_run": assessment.as_dict(),
        "upstream": {"module_id": EXPECTED_MODULE, "module_version": upstream["manifest"]["module_version"], "run_id": upstream["manifest"]["run_id"]},
        "sources": [source.as_dict() for source in sources],
        "claims": [claim.as_dict() for claim in claims],
        "observations": [observation.as_dict()],
        "hypotheses": [hypothesis.as_dict()],
        "failure_modes": [failure_mode.as_dict()],
        "decision_uncertainties": [uncertainty.as_dict()],
        "experiments": [experiment.as_dict()],
        "system_recommendation": recommendation.as_dict(),
        "human_decision": None,
    }
