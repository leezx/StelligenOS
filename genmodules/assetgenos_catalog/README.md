# AssetGenOS Catalog

This module migrates the pure software catalog from AssetGenOS into StelligenOS.
It contains versioned contracts and identity definitions only:

- shared input/output/lifecycle contracts;
- 45 frozen ADC Gate definitions;
- 59 Model definitions bound to those Gates;
- 53 Profile definitions describing graph and binding variants.

The source-relative layout is preserved under `contracts/`, `gates/`,
`models/`, and `profiles/` so references remain auditable. These YAML files
define software behavior and interfaces; they are not runtime data stores.

## Excluded By Design

The migration does not include `model_governance/`, `model_work_packages/`,
historical labels, calibration records, review evidence, datasets, databases,
caches, generated results, model weights, or runners. Those remain external
inputs or operational records and must be supplied through ArtifactRef-style
ports at execution time.

## Source Boundary

- Source workspace: external AssetGenOS workspace.
- Migrated source families: `components/contracts`, `components/gates`,
  `components/models`, `components/profiles`.
- Runtime ownership: StelligenOS owns contracts and orchestration boundaries;
  external workspaces own data, evidence, governance records, and execution.
