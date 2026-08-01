# StelligenOS GenModules

This directory contains software-only generation modules migrated from
AssetGenOS. GenModules belong to the frozen `Asset Generation` lifecycle and
are not lifecycle stages or Gate implementations.

## Active modules

- `antibody_binder_asset_engineering@0.4.0`: engineers an existing binder into
  an antibody/ADC-carrier asset package through 16 internal implementation
  steps mapped to the frozen 14-stage external Binder/ADC route.
- `epitope_conditioned_de_novo_antibody_discovery@0.1.0`: prepares an
  epitope-conditioned de novo antibody asset-discovery package through a
  frozen 15-stage workflow.

## Repository boundary

The modules store only code, contracts, software declarations, and
documentation here. Inputs, evidence, model weights, external tool
environments, observations, candidates, reports, and run directories must be
provided by an external workspace through command-line paths or environment
variables. No module writes to the repository by design.

Both modules keep external scientific execution disabled by default. They do
not write Gate scores, promote lifecycle state, infer experimental evidence,
or claim legal FTO, patentability, clinical safety, clinical efficacy, or ADC
readiness without the required external evidence and review.

## Architecture mapping

The frozen Binder/ADC route contract remains the OS-level boundary:
`src/contracts/binder_adc_routes.yaml` and
`src/capabilities/binder_adc_routes.py`. These modules implement the external
route runtimes described by that contract; they do not replace the route port
or create a second lifecycle.

Run outputs must be placed outside this repository, for example:

```bash
python genmodules/antibody_binder_asset_engineering/run_pipeline.py run \
  --binder /external/workspace/input/binder.yaml \
  --output-root /external/workspace/runs/antibody-binder
```

Do not copy external inputs, generated outputs, databases, caches, model
weights, or virtual environments into this repository.
