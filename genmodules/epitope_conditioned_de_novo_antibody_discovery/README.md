# Epitope-Conditioned de novo Antibody Asset Discovery

Module ID: `epitope_conditioned_de_novo_antibody_discovery`
Version: `0.1.0`

This GenModule starts from a therapeutic antigen and a user-defined epitope and
builds a versioned de novo antibody-asset discovery package. It is not a Gate
and does not write Gate scores.

The module executes 15 steps:

1. target biology;
2. antigen engineering;
3. epitope engineering;
4. IP/FTO-guided epitope selection;
5. structural preparation;
6. negative design;
7. epitope-conditioned de novo design;
8. computational ranking;
9. asset-diversity optimization;
10. focused wet-lab design;
11. structural validation;
12. affinity maturation;
13. ADC readiness;
14. patent package;
15. asset report.

Without external AI tools it still validates the antigen/epitope contract,
checks residue positions, extracts the epitope sequence, freezes positive and
negative constraints, creates the experiment/validation package, and writes an
auditable report. It does not invent antibody sequences.

## Quick start

```bash
cd "/path/to/StelligenOS"

.venv/bin/python \
  genmodules/epitope_conditioned_de_novo_antibody_discovery/run_pipeline.py \
  list-steps

.venv/bin/python \
  genmodules/epitope_conditioned_de_novo_antibody_discovery/run_pipeline.py \
  doctor

run_root="/external/workspace/runs/epitope-discovery"
.venv/bin/python \
  genmodules/epitope_conditioned_de_novo_antibody_discovery/run_pipeline.py \
  run \
  --input /external/workspace/input/epitope_discovery.yaml \
  --output-root "${run_root}" \
  --mode execute
```

External scientific programs are never invoked automatically in v0.1.0.

## Dagster

After manually installing Dagster:

```bash
export EPITOPE_GENMODULE_INPUT_CONFIG="$PWD/genmodules/epitope_conditioned_de_novo_antibody_discovery/examples/epitope_design.example.yaml"
export EPITOPE_GENMODULE_OUTPUT_ROOT="$(mktemp -d)"
dagster dev -f genmodules/epitope_conditioned_de_novo_antibody_discovery/dagster_defs.py
```

See [SOFTWARE_AND_DATA.md](SOFTWARE_AND_DATA.md) before installing RFantibody,
RFdiffusion, Rosetta, IgFold, or model weights.
