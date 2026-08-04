# Target Safety and Therapeutic-Window Pre-screen Handoff

## Status

- Branch: `task_20260804_target-safety-prescreen`
- Base: latest `origin/main` at task start
- Review: implementation complete; PR and ChatGPT review are required before merge
- Data boundary: no source data, cache, result, model weight, or runtime output in the repository

## Scope

This GenModule is a target-level public-evidence pre-screen for ADC development.
It asks whether public evidence contains a target-intrinsic hazard strong enough
to kill, hold, or downgrade investment before antibody discovery and ADC assembly.
It does not claim product-specific therapeutic-window prediction.

## Implemented

- Six evidence axes: normal tissue expression, surface accessibility, antigen density, soluble antigen/shedding/sink, existing modality toxicity, and tissue consequence/recoverability.
- Evidence levels `A/B/C/D/U` and explicit risk directions.
- Fatal-first rules for critical surface hazard, confirmed severe on-target toxicity, non-lower normal density, clinically demonstrated sink/exposure failure, and no exploitable differential.
- Decision semantics: `KILL`, `HOLD`, `CONDITIONAL_GO`, `GO`.
- Unknown, unresolved, and conflicting claims remain visible and produce next-experiment references.
- All cross-boundary identities and evidence references require `external:` references.
- Runtime location is declared as `${BIOWORKSPACE_ROOT}/DATA/target_safety_therapeutic_window_prescreen/{raw,processed,result}`; no runtime writer is enabled in the repository.

## Validation

- Module tests pass.
- Full suite: 212 tests pass.
- `scripts/verify_repository_boundary.sh` passes.
- `git diff --check` passes.
- No `__pycache__` directory remains.

## Known limitations

- Evidence retrieval, source normalization, citation resolution, scoring calibration, and persistence remain external runtime responsibilities.
- The first ruleset is deterministic and conservative; it is not a clinical safety model and must not be used as a product-level therapeutic-window claim.
- The next implementation phase should add an external runtime adapter and benchmark fixtures under `DATA`, only after this contract PR is reviewed.
