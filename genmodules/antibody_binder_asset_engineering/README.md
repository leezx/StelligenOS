# Existing-Binder Antibody Asset Engineering GenModule

Module ID: `antibody_binder_asset_engineering`
Version: `0.4.0` (predecessor `0.3.0`, superseded in place; last archived version `0.2.0`)

This GenModule turns a versioned existing binder into an auditable ADC carrier
engineering work package. It is deliberately separate from the 45-Gate decision
graph.

## What changed in 0.4.0

Three layers that answer reviewer questions the earlier versions could not.

| Layer | What it adds |
|---|---|
**Evidence** (`09`) | Every criterion carries `direction_agreement`, `evidence_count`, `evidence_diversity`, `evidence_freshness` and a composite `confidence_band`. Reported separately so volume cannot inflate confidence: ten agreeing patent lines still band as `weak`. |
**Reasoning graph** (`15`) | Observation → Hypothesis → Failure mode → Decision → Experiment, every edge carrying the sentence that justifies it — **and a stated reason for every experiment not selected**. A recommendation without its rejected alternatives is an assertion, not an argument. |
**Cross-asset retrieval** (`16`) | Nearest clinical ADC comparators over a 379-case corpus by declared attribute match, reporting matched, differing and uncomparable attributes, with an explicit `no_close_precedent` verdict. |

`direction_agreement` is named for what it measures. It is **not** epistemic
confidence and must never be read as a probability.

Also fixed: `evaluate_cascade` now emits `usable_observations`, not only their count.
The graph read a key that was never emitted, so the measured-evidence layer was
silently absent — invisible precisely on binders with no carrier data.

## What changed in 0.3.1

0.3.1 fixes four risk-classification defects that a TPP-2658 (anti-TWEAKR, Bayer)
run exposed. Each one made a dangerous substitution look safe, so runs from 0.3.0
should not be trusted for candidate selection.

| Defect in 0.3.0 | Effect | Fix |
|---|---|---|
| Regions assigned from IMGT alone | Kabat CDR-H1 34-35 and CDR-H2 58-65 read as FR2/FR3, so paratope residues got framework's low risk and `requires_binding_confirmation: false` | `region` is now the union of IMGT and Kabat; both are reported |
| No notion of conserved structural anchors | Substitutions proposed at the invariant core tryptophans and the J-TRP, labelled low risk | IMGT anchors 23/41/89/104/118 are declined with a reason, never silently |
| Burial only lowered priority | A buried core substitution ranked as the *safest* fix | Burial now also raises `engineering_risk` and sets `requires_fold_confirmation` |
| Germline-encoded liabilities indistinguishable from somatic ones | "Safe framework fixes" that quietly lower framework identity | `germline_encoded` tri-state on every hit; `reduces_framework_humanness` on every proposal |

The triage table now carries `Risk`, `Binding check`, `Fold check`, and
`Humanness cost` beside the score, because the score cannot express any of them.

## What changed in 0.3.0

0.2.0 was a working antibody **sequence** engineering pipeline. Its limitation was
the objective, not the machinery: it optimised a cleaner, more humanised, more
developable antibody, which is not the same thing as an antibody that delivers a
payload. An ADC carrier may need agonism and Fc effector function silenced, and may
trade affinity for tumour penetration — the opposite of naked-antibody optima.

0.3.0 runs two orthogonal tracks:

| | Track A — binder molecule quality | Track B — ADC carrier phenotype |
|---|---|---|
| Nature | **Computed** from sequence and structure | **Measured** from structured observations |
| Stages | 01, 03, 04, 05, 06 | 07, 08 |
| Emits | `sequence_computational_developability_score` | `adc_carrier_quality_score` |
| Cost | Free | Needs wet lab |

They are combined **only** by Pareto dominance, never summed. Summing would let a
clean sequence compensate for a molecule that does not internalise.

Also new: a five-step delivery cascade replacing the single `internalization`
criterion; causal failure trees with information-gain experiment ranking; four
construct-specification families; and a three-entity ADC product model.

## Capabilities

- IMGT **and** Kabat numbering, region assignment, closest human germline identity;
- position-resolved chemical liabilities with separated chemical, functional, and
  remediation risk axes, region risk taken as the union of IMGT and Kabat, and
  germline-encoded liabilities distinguished from somatic ones;
- conserved structural anchors declined rather than proposed;
- sequence-derived biophysical descriptors;
- optional Fv structure prediction with per-residue SASA, used to down-weight
  buried liabilities;
- traceable mutation proposals and real candidate sequences in three families;
- construct and campaign specifications for four further families, kept visibly
  distinct from generated sequences;
- a five-step ADC delivery cascade with mandatory observation metadata;
- a modality go/no-go decision from 7 continue and 8 stop rules;
- two causal failure trees (15 modes) with experiments ranked by information gain,
  including credit for overturning a currently-blocking finding;
- a two-axis Pareto frontier, or an explicit refusal to name a lead;
- an ADC product matrix over antibody × conjugation variant;
- a tool/data doctor spanning both interpreters.

The module never predicts binding, never emits an ADC-readiness score, never
estimates a DAR from variable domains, and never lets a variant inherit its
parent's phenotype measurement.

## Machine contracts

- `contracts/existing_binder_asset_input.v0.4.0.yaml` accepts source records from
  0.1.0 through 0.4.0 and normalizes them to `ExistingBinderAssetInput@0.4.0`.
- `contracts/antibody_asset_engineering_package.v0.4.0.yaml` fixes the exact
  16-step internal catalogue, manifest identity, stage/root artifact references, SHA-256
  checksums, null semantics, and legacy rejection rules.

Every completed run carries an `AntibodyAssetRunManifest@0.4.0` validation
receipt. Missing or invalid checksums, a different stage catalogue, or a contract
identity mismatch block the run. The external StelligenOS route exposes 14
stages through `list-steps`; internal implementation steps remain inspectable
through `list-internal-steps` and are explicitly mapped in `module.yaml`.

## Quick start

```bash
cd "/path/to/StelligenOS"

.venv/bin/python \
  genmodules/antibody_binder_asset_engineering/run_pipeline.py list-steps

.venv/bin/python \
  genmodules/antibody_binder_asset_engineering/run_pipeline.py list-internal-steps

.venv/bin/python \
  genmodules/antibody_binder_asset_engineering/run_pipeline.py doctor

run_root="/external/workspace/runs/antibody-binder"
.venv/bin/python \
  genmodules/antibody_binder_asset_engineering/run_pipeline.py run \
  --binder /external/workspace/input/binder.yaml \
  --output-root "${run_root}" \
  --mode execute \
  --allow-external
```

Use `--allow-external` unless you have a reason not to. Without it, solvent
exposure is unknown and the module will propose CDR substitutions to fix
liabilities that a structure shows are buried. ABodyBuilder2 downloads weights on
first use; afterwards the full pipeline runs in about 13 seconds.

## Commands

```text
list-steps                          Show the 14 frozen external route stages.
list-internal-steps                 Show the 16 internal implementation steps.
doctor [--json]                     Check interpreters, software, and data roots.
run --binder ... --output-root ...   Execute or plan a versioned run.
    [--mode plan|execute] [--run-id ID] [--allow-external]
```

## Runtime

| Role | Location | Holds |
|---|---|---|
| orchestrator | external runtime selected by the caller | PyYAML, Jinja2, pytest |
| shared scientific runtime | `SOFTWARES/venvs/antibody_pipeline_shared/py311` | ANARCI, abnumber, biopython, ImmuneBuilder, IgFold, ESM, torch, pandas, sklearn |

Override the second with `ANTIBODY_SHARED_PYTHON`. `doctor` reports which
interpreter satisfied each tool, so a missing tool is distinguishable from a tool
installed in an environment that was not searched.

## Output tree

```text
<output-root>/<asset_id>/<run_id>/
├── run_manifest.yaml
├── normalized_input.yaml
├── software_status.yaml
├── 01_binder_intake/result.yaml
├── 03_structural_analysis/
│   ├── result.yaml
│   └── fv_model.pdb                 only with --allow-external
├── 07_adc_carrier_phenotype/result.yaml     Track B
├── 09_adc_failure_mode_analysis/result.yaml
├── 10_pareto_selection/result.yaml
├── ...
└── asset_report.md                  leads with the modality decision
```

## Supplying carrier phenotype data

Track B reads `adc_carrier_observations` from the input. Each observation needs
eight metadata fields, and fraction-type measurements need a declared
`normalization_basis`:

```yaml
adc_carrier_observations:
  - measurement: acid_wash_internalized_fraction
    cell_line: SN12C
    endogenous_or_engineered: endogenous
    target_density: {value: 45000, unit: receptors_per_cell, method: QIFIKIT}
    timepoint: {value: 4, unit: h}
    concentration: {value: 10, unit: ug/mL}
    assay_method: acid wash + flow cytometry
    biological_replicates: 3
    uncertainty: {type: sd, value: 0.05}
    normalized_value: 0.42
    normalization_basis: surface_binding_4c
    construct: PDL192-IgG1
```

An observation missing any of these is reported as `unusable` with the reason. It
is not partially credited: a measurement with unknown context cannot be compared
to anything.

No example with populated observations ships, deliberately — a fabricated dataset
could be mistaken for real measurements. The tests exercise that path with
obviously synthetic values.

## Examples

- `examples/binder.example.yaml` — synthetic demonstration input, 0.1.0 shape.
- `examples/enavatuzumab.yaml` — enavatuzumab (PDL192), anti-TWEAKR/Fn14, with
  sequences from patent US20090074762 and evidence fields carrying per-field
  sources, directions, and caveats. Reference example for the 0.3.0 input shape.
  Its `adc_carrier_observations` list is empty, which is a finding rather than an
  omission; see `GUIDE.zh-CN.md` §14.

## Documentation map

| Document | Language | Contents |
|---|---|---|
| [README.md](README.md) | EN | Quick start, commands, runtime |
| [DESIGN.md](DESIGN.md) | EN | Contract, boundary, scores, versioning |
| [WORKLOG.md](WORKLOG.md) | EN | Defect list, verification, known gaps |
| [GUIDE.zh-CN.md](GUIDE.zh-CN.md) | 中文 | 完整说明：双轨架构、14 个 stage、五大核心机制原理 |
| [WORKLOG.zh-CN.md](WORKLOG.zh-CN.md) | 中文 | 中文工作日志 |

`GUIDE.zh-CN.md` is the most detailed explanation of why each mechanism is built
the way it is, including why the two tracks must not be summed, why `null` carrier
quality means unmeasured rather than poor, and why overturn credit and prerequisite
gating were needed in the information-gain metric. Read it before changing scoring,
phenotype, or failure-mode logic.

## Installation

Read [SOFTWARE_AND_DATA.md](SOFTWARE_AND_DATA.md), then fill a local copy of
`config/data_manifest.template.yaml`. Large databases and model weights belong
under workspace `DATA/` or `SOFTWARES/`, never in this module folder.

## Dagster

```bash
export ANTIBODY_GENMODULE_BINDER_CONFIG="$PWD/genmodules/antibody_binder_asset_engineering/examples/enavatuzumab.yaml"
export ANTIBODY_GENMODULE_OUTPUT_ROOT="$(mktemp -d)"
export ANTIBODY_GENMODULE_ALLOW_EXTERNAL=1
dagster dev -f genmodules/antibody_binder_asset_engineering/dagster_defs.py
```

The op chain is generated from `EXECUTION_ORDER`, so it cannot drift from the CLI.
