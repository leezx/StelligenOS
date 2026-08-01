# Biotech Asset Due Diligence

This repository contains the software contract boundary for the Phase 1A
modality-neutral due-diligence vertical slice. It is intentionally code and
small contracts only; inputs, upstream artifacts, reports, and run manifests
remain in external runtime folders.

## Software boundary

The package models the auditable chain:

```text
Asset -> AssetVariant -> AssessmentRun -> ArtifactRef
  -> EvidenceSource/Claim -> Observation -> Hypothesis -> FailureMode
  -> DecisionUncertainty -> ExperimentBranch -> SystemRecommendation
```

`HumanDecision` is a separate record and is never created as a side effect of a
system recommendation. The adapter verifies immutable, externally supplied
Binder `0.4.0` artifacts and consumes no repository-local example or dataset.

## Runtime rule

There is deliberately no runner in this repository. A future runtime may call
the pure adapter with an external input record and an external workspace root,
but it must write package outputs outside StelligenOS. No data, result, cache,
archive, model weight, or fixture belongs here.
