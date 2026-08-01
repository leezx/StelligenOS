# Manual software and data setup

This file is the installation queue for
`epitope_conditioned_de_novo_antibody_discovery@0.1.0`.

The module itself installs no scientific software, downloads no weights or
databases, and never invokes an external design program automatically. Install
each dependency manually, record its version/commit and licence, then expose it
through the environment variables below. Keep tools, weights, databases, and
run outputs outside this source folder.

## Recommended first installation

Do this in four small increments:

1. Core audit: Biopython, ANARCI, AbNumber, BLAST+, and MMseqs2.
2. Structure preparation: PDBFixer, OpenMM, and FreeSASA.
3. Primary de novo adapter: RFantibody on a Linux host with an NVIDIA GPU.
4. Independent check and orchestration: ImmuneBuilder, then Dagster if wanted.

RFantibody is the preferred first design adapter because its official pipeline
already connects antibody-fine-tuned RFdiffusion backbone generation,
ProteinMPNN sequence design, and antibody-fine-tuned RoseTTAFold2 filtering.
Do not separately install every alternative generator before one frozen
RFantibody benchmark can run end to end.

## 1. Core module environment

From an external runtime workspace:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install \
  -r genmodules/epitope_conditioned_de_novo_antibody_discovery/requirements-core.txt
```

Optional Dagster UI:

```bash
.venv/bin/python -m pip install \
  -r genmodules/epitope_conditioned_de_novo_antibody_discovery/requirements-dagster.txt
```

The executable runner only requires Python and PyYAML for its current built-in
control path. The other core packages are declared now so future ranking and
optimization adapters can be added without changing the module contract.

## 2. Sequence, numbering, and prior-art search

| Tool | Use | Registration/check |
|---|---|---|
| ANARCI | antibody numbering and chain-class checks | `ANARCI --help` |
| AbNumber | programmatic antibody numbering | Python `import abnumber` |
| BLAST+ | exact/near sequence prior-art search | `blastp -version` |
| MMseqs2 | large sequence-neighborhood search | `mmseqs version` |

Freeze the exact numbering scheme used in every candidate manifest. A sequence
similarity result is a technical search lead, not a legal FTO conclusion.

## 3. Structure preparation and measurement

| Tool | Use | Registration/check |
|---|---|---|
| PDBFixer | inspect and repair explicit structural omissions | Python `import pdbfixer` |
| OpenMM | restrained preparation or relaxation | Python `import openmm` |
| FreeSASA | solvent accessibility and buried-area features | `freesasa --version` |
| OpenFold | optional target/complex structure adapter | Python `import openfold` |

All repaired or predicted residues must retain provenance. A prepared structure
must keep the target sequence version, construct boundaries, chain map,
epitope/hotspot map, glycan decisions, membrane context, tool commit, model
weights, parameters, and file checksum.

## 4. Primary de novo design adapter: RFantibody

Official project: <https://github.com/RosettaCommons/RFantibody>

The current official setup requires Linux, an NVIDIA CUDA-capable GPU, and
CUDA 11.8 or newer; Ubuntu 22.04 is recommended. The local installation uses
`uv`, downloads RFantibody weights, and creates its own Python 3.10
environment. Docker and Apptainer routes are also documented upstream.

Install RFantibody outside this repository, for example below the workspace
`SOFTWARES` tree. Follow the upstream README rather than copying commands from
an old run log. After installation, register:

```bash
export RFANTIBODY_ROOT="/path/to/frozen/RFantibody"
export DE_NOVO_ANTIBODY_MODEL_ROOT="/path/to/frozen/rfantibody_weights"
```

Before adding an execution adapter, capture:

- repository URL and immutable commit;
- environment lock and CUDA/PyTorch versions;
- every weight filename and SHA-256 checksum;
- target PDB/HLT, framework PDB, hotspot residues, loop-length policy;
- random seeds, number of backbones, sequences per backbone, and RF2 recycles;
- Quiver/PDB outputs and score files without deleting failed candidates;
- software and weight licences reviewed for the intended commercial use.

The v0.1.0 adapter boundary is:

```text
versioned target structure + exact epitope hotspots + negative constraints
  -> RFantibody external run
  -> immutable candidate manifest + sequences + structures + raw scores
  -> GenModule stage 07 ingestion
```

RFantibody output is a designed-candidate hypothesis. It is not proof of
binding, epitope, affinity, specificity, function, or developability.

## 5. Alternative or component adapters

Install these only when the primary route needs a controlled comparison:

| Tool | Role | Registration |
|---|---|---|
| RFdiffusion | alternative backbone-generation component | `RFDIFFUSION_ROOT` |
| RFdiffusion2 | future benchmark/adapter; not v0.1.0 core | adapter-specific path |
| ProteinMPNN | standalone sequence-design component | `PROTEINMPNN_ROOT` |
| LigandMPNN | optional context-aware sequence-design component | `LIGANDMPNN_ROOT` |
| ESM | optional sequence embedding/likelihood features | Python `import esm` |

Official sources:

- RFdiffusion: <https://github.com/RosettaCommons/RFdiffusion>
- RFdiffusion2: <https://github.com/RosettaCommons/RFdiffusion2>
- ProteinMPNN: <https://github.com/dauparas/ProteinMPNN>
- LigandMPNN: <https://github.com/dauparas/LigandMPNN>
- ESM: <https://github.com/facebookresearch/esm>

Do not mix scores from different model versions as though they were calibrated
on one scale. Each adapter needs its own frozen benchmark, version, seeds,
weight hashes, raw outputs, and acceptance thresholds.

## 6. Independent structure and energy checks

| Tool | Role | Important boundary |
|---|---|---|
| ImmuneBuilder | independent antibody structure prediction | predicted structure only |
| IgFold | optional independent antibody prediction | review repository/model terms before commercial use |
| Rosetta/RosettaScripts | optional interface refinement and energy features | commercial use requires appropriate Rosetta licensing |
| FoldX | optional stability/interface features | review licence and calibration |

Official sources:

- ImmuneBuilder: <https://github.com/oxpig/ImmuneBuilder>
- IgFold: <https://github.com/Graylab/IgFold>
- Rosetta licence: <https://docs.rosettacommons.org/docs/latest/LICENSE>

Prediction agreement is a ranking feature, not experimental validation. Do not
promote a candidate to affinity maturation from predicted poses alone.

## 7. Data registration

Suggested roots use workspace variables rather than hard-coded mounts:

```bash
export TARGET_SEQUENCE_REFERENCE_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/target_sequence_reference"
export TARGET_STRUCTURE_REFERENCE_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/target_structure_reference"
export ANTIBODY_ANTIGEN_COMPLEX_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/antibody_antigen_complex_reference"
export THERAPEUTIC_ANTIBODY_REFERENCE_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/therapeutic_antibody_reference"
export COMPETITOR_ANTIBODY_EVIDENCE_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/competitor_antibody_evidence"
export ANTIBODY_PATENT_EXPORT_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/antibody_patent_exports"
export DE_NOVO_ANTIBODY_MODEL_ROOT="${BIOWORKSPACE_ROOT}/SOFTWARES/models/de_novo_antibody"
export NORMAL_TISSUE_ATLAS_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/normal_tissue_atlas"
export ADC_REFERENCE_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/adc_reference"
export DE_NOVO_ANTIBODY_BENCHMARK_ROOT="${BIOWORKSPACE_ROOT}/DATA/1.Databases/de_novo_antibody_benchmark"
export ANTIBODY_EXPERIMENT_ROOT="${BIOWORKSPACE_ROOT}/DATA/antibody/experiments"
```

| Data root | Minimum useful contents |
|---|---|
| Target sequence | accession, exact sequence/version, topology, isoforms, retrieval date |
| Target structure | experimental/predicted structures, chain map, sequence mapping, confidence and checksums |
| Antibody–antigen complexes | structure IDs, sequences, chain/CDR mapping, epitope contacts and provenance |
| Therapeutic antibodies | target, sequence/family, epitope/function, format, clinical status and sources |
| Competitor evidence | molecule/sponsor, epitope, competition, function, status and evidence dates |
| Patent exports | family/publication IDs, claims, sequences, legal status, source and query provenance |
| Model weights | tool/version, filename, checksum, licence and retrieval date |
| Normal tissue atlas | tissue/cell type, assay, expression evidence, release and source |
| ADC reference | target, epitope, internalization/trafficking, construct, outcome and source |
| Design benchmark | frozen positive/negative complexes, candidate families and experimental labels |
| Experimental results | candidate ID, assay protocol, replicate-level observation, units, date and provenance |

Downloaded database snapshots are append-only. Preserve source notes,
licences/terms, manifests, retrieval dates, and checksums.

## 8. Stage-to-resource map

| Stage | Software | Data |
|---|---|---|
| 01 Target biology | built-in/YAML | target sequence, therapeutics, normal tissue, ADC reference |
| 02 Antigen engineering | Biopython | target sequence and construct evidence |
| 03 Epitope engineering | structure viewer/analysis adapters | target structures, antibody–antigen complexes, ADC reference |
| 04 IP/FTO epitope selection | BLAST+, MMseqs2 | therapeutic/competitor evidence and patent exports |
| 05 Structural preparation | PDBFixer, OpenMM, FreeSASA, optional OpenFold | target structure ensemble |
| 06 Negative design | search/structure adapters | normal tissue, paralogs, competitor and patent evidence |
| 07 De novo design | RFantibody first; optional component adapters | prepared structure, model weights and benchmark |
| 08 Computational ranking | ANARCI/AbNumber, structure predictors, energy/scoring tools | raw candidates, complex references and benchmark |
| 09 Asset diversity | pandas/scikit-learn | candidate sequences, structures, families and competitor references |
| 10 Focused wet lab | reporting only | selected candidates and assay capabilities |
| 11 Structural validation | analysis adapters after experiments | experimental epitope/structure results |
| 12 Affinity maturation | optional Rosetta/FoldX/Optuna after eligibility | confirmed binders and experimental labels |
| 13 ADC readiness | reporting/ranking | internalization, trafficking, normal tissue and ADC evidence |
| 14 Patent package | BLAST+/MMseqs2/Jinja2 | sequences, structures, patent exports and dated experiments |
| 15 Asset report | Jinja2, optional Pandoc | all versioned stage outputs |

## 9. Verify the registered environment

```bash
.venv/bin/python \
  genmodules/epitope_conditioned_de_novo_antibody_discovery/run_pipeline.py \
  doctor
```

`missing` means “not registered or not available in the current shell.” It does
not block the built-in planning/audit path. An external adapter must refuse to
run if its exact program, data, weights, or licence record is unresolved.

## 10. Promotion rule

Promote one adapter from “manual installation” to “executable integration” only
after it has:

1. a frozen executable/commit/environment and model-weight checksum;
2. a small positive/negative benchmark with raw outputs retained;
3. a typed input/output adapter contract;
4. deterministic smoke tests where the upstream program permits them;
5. explicit failure behavior and no silent score substitution;
6. licence review for the intended use;
7. independent review before any production threshold is frozen.
