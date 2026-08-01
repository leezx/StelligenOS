# Manual software and data installation

This file is the installation queue for
`antibody_binder_asset_engineering@0.3.1`. Nothing here is installed
automatically.

Use:

```bash
python genmodules/antibody_binder_asset_engineering/run_pipeline.py doctor
```

after each installation. Register large assets through the environment
variables in `config/data_manifest.template.yaml`.

## Installation order

### Tier 0 — run the built-in workflow

Required now:

```bash
python -m pip install -r \
  genmodules/antibody_binder_asset_engineering/requirements-core.txt
```

The caller-provided StelligenOS runtime must provide Python and PyYAML. The
additional packages enable richer sequence tables and later active learning;
the smoke workflow does not require them.

Optional orchestration:

```bash
python -m pip install -r \
  genmodules/antibody_binder_asset_engineering/requirements-dagster.txt
```

Dagster's official installation path uses the `dagster` and
`dagster-webserver` Python packages:
<https://docs.dagster.io/getting-started/installation>.

### Tier 1 — binder identity, numbering, and sequence search

Install first because all later sequence-family and IP work depends on stable
numbering.

1. **ANARCI**
   - Purpose: chain classification, IMGT/Kabat/Chothia/AHo numbering.
   - Official repository: <https://github.com/oxpig/ANARCI>
   - Dependencies include Biopython and HMMER.
   - Typical route: install HMMER through Conda/Bioconda, then install ANARCI.
2. **AbNumber**
   - Purpose: programmatic CDR/framework slicing and aligned sequence families.
   - Documentation: <https://abnumber.readthedocs.io/en/stable/>
   - Typical route: `conda install -c bioconda abnumber`.
3. **NCBI BLAST+**
   - Purpose: exact and near-sequence searches against locally permitted
     sequence exports.
   - Install through Conda/Bioconda or the NCBI distribution.
4. **MMseqs2**
   - Purpose: fast, large sequence-neighborhood searches.
   - Keep its database index outside this source folder.

Acceptance checks:

```bash
ANARCI --help
blastp -help
mmseqs version
python -c "from abnumber import Chain; print('AbNumber OK')"
```

### Tier 2 — antibody structure

Install one antibody-specific predictor first. Do not install every structure
tool before the first binder is ready.

1. **ImmuneBuilder / ABodyBuilder2 — preferred first predictor**
   - Official repository: <https://github.com/oxpig/ImmuneBuilder>
   - Install: PyTorch, OpenMM, pdbfixer, ANARCI, then `pip install ImmuneBuilder`.
   - Supports paired antibodies and nanobodies and returns ensemble uncertainty.
2. **IgFold — optional independent cross-check**
   - Official repository: <https://github.com/Graylab/IgFold>
   - Install: `pip install igfold`; refinement additionally uses PyRosetta or
     OpenMM.
   - **Licence:** the repository states that code and pretrained models are for
     non-commercial use under the JHU Academic Software Licence; commercial
     use requires separate review/licensing. Do not use it for a commercial
     asset workflow until this is resolved.
3. **OpenFold — optional, heavyweight**
   - Official repository: <https://github.com/aqlaboratory/openfold>
   - Use for antigen/complex-supporting work when its large alignment databases,
     GPU environment, and weights are justified. It is not required for the
     first antibody-variable-domain pass.
4. **Rosetta / PyRosetta — optional refinement and interface design**
   - Documentation: <https://docs.rosettacommons.org/docs/latest/getting_started/Getting-Started>
   - **Licence:** Rosetta/PyRosetta non-commercial downloads do not permit
     commercial use. A commercial licence is required for commercial asset
     generation.
5. **FoldX — optional mutation-energy screen**
   - Register the exact executable, version, and licence. Treat its energy
     values as comparative computational evidence only.

Recommended first milestone:

```text
ANARCI/AbNumber → ImmuneBuilder ensemble → structure QA
```

Do not make AlphaFold3 a core dependency. Its availability, parameters, terms,
and compute burden should be evaluated separately for each project.

### Tier 3 — design and multi-objective triage

1. **ProteinMPNN**
   - Official repository: <https://github.com/dauparas/ProteinMPNN>
   - Purpose: structure-conditioned sequence proposals under fixed-residue and
     chain constraints.
   - Register its repository commit, weight checksum, seed, temperature, fixed
     positions, designed chains, and output probabilities.
   - Set `PROTEINMPNN_ROOT` to the checked-out installation.
2. **ESM**
   - Reference repository: <https://github.com/facebookresearch/esm>
   - Purpose: embeddings or language-model baselines—not proof of affinity,
     expression, humanness, or immunogenicity.
   - Verify the exact code and model-weight licence before commercial use.
3. **Rosetta/PyRosetta**
   - Optional for constrained CDR/interface design after commercial licensing.
4. **Pandas, scikit-learn, Optuna**
   - Purpose: Pareto tables, small-N active learning, and experiment selection.
   - Never combine biology, developability, and FTO into a hidden scalar score.

Future adapters—not required for v0.1.0—may include AntiFold, RFdiffusion /
RFantibody, Germinal, MAGE, tFold, and later antibody foundation models. Each
needs an independent licence, version, provenance, and benchmark review before
activation.

### Tier 4 — reporting

- **Jinja2:** report templates.
- **Pandoc:** optional PDF/DOCX export.
- Patent search/export tools selected by the user or counsel.

The workflow may prepare an attorney-facing technical package but never a legal
opinion.

## Data installation

Store reusable datasets below a workspace data root such as
`${BIOWORKSPACE_ROOT}/DATA/1.Databases/`. Store software and model weights under
`${BIOWORKSPACE_ROOT}/SOFTWARES/`. Do not copy them into `genmodules/`.

| Data asset | Steps | Minimum contents | Runtime registration |
|---|---|---|---|
| IMGT germline reference | 01, 06 | V/J germlines, release/version, licence note | `IMGT_GERMLINE_ROOT` |
| SAbDab | 01, 03 | antibody structures, chain/antigen metadata, download date | `SABDAB_ROOT` |
| Thera-SAbDab or equivalent therapeutic reference | 01, 02, 06 | therapeutic sequences, target, status, references | `THERAPEUTIC_ANTIBODY_REFERENCE_ROOT` |
| OAS or another lawfully reusable antibody repertoire | 05, 06 | sequence records, species, chain, study provenance | optional subfolder of therapeutic/reference root |
| PDB/antigen structures | 03, 04 | antigen structures and templates with checksums | `ANTIBODY_STRUCTURE_MODEL_ROOT` |
| Model weights | 03–06 | exact predictor/designer weights and checksums | `ANTIBODY_STRUCTURE_MODEL_ROOT`, `PROTEINMPNN_ROOT` |
| Patent sequence/claim exports | 02, 10 | query, jurisdiction, family, claims, sequences, export date | `ANTIBODY_PATENT_EXPORT_ROOT` |
| Normal-tissue atlas | 09 | HPA/GTEx/Tabula Sapiens or approved alternatives | `NORMAL_TISSUE_ATLAS_ROOT` |
| ADC reference evidence | 09 | target, internalization, trafficking, linker/payload and outcome references | `ADC_REFERENCE_ROOT` |
| Experimental results | 07–11 | raw files, sample/candidate identity, assay version, units, QC | `ANTIBODY_EXPERIMENT_ROOT` |

For every dataset retain:

- source URL and access date;
- exact release or snapshot identifier;
- licence/terms and allowed commercial use;
- raw-file checksums;
- parsing code and derived-data checksums;
- excluded/failed rows;
- dataset limitations.

## Step-by-step dependency map

| Step | Software | Data | Blocking output |
|---|---|---|---|
| 01 Binder intake | ANARCI, AbNumber, Biopython | IMGT, SAbDab, therapeutic reference | numbered VH/VL, immutable sequence identity, provenance |
| 02 IP/FTO | BLAST+, MMseqs2 | patent exports, therapeutic sequences | claim/sequence landscape and design constraints |
| 03 Structure | ImmuneBuilder; optional IgFold/OpenFold/Rosetta/FoldX | SAbDab, PDB, model weights | versioned structural ensemble and uncertainty |
| 04 AI engineering | ProteinMPNN, ESM; optional Rosetta | protected residues, structure, IP constraints | versioned design specification |
| 05 Candidate families | ProteinMPNN or later adapter | parent and generated sequences | 3–5 independent families |
| 06 Triage | ANARCI/AbNumber, ESM, FoldX, Pandas | reference distributions | Pareto table without hidden composite rank |
| 07 Experiments | laboratory/CRO systems | assay protocols and controls | versioned minimum experimental package |
| 08 Active learning | Pandas, scikit-learn, Optuna | QC-passed observations | immutable updated ranking/design proposal |
| 09 ADC readiness | reporting adapters | normal-tissue, ADC and experimental evidence | evidence-gap report submitted to Gates |
| 10 Patent package | BLAST+, MMseqs2, Jinja2 | IP/FTO and experimental evidence | attorney-facing technical package |
| 11 Asset report | Jinja2, optional Pandoc | all prior artifacts | complete versioned asset report |

## What to install first

For the first real binder, install only:

1. ANARCI + AbNumber;
2. BLAST+ + MMseqs2;
3. ImmuneBuilder;
4. ProteinMPNN;
5. Dagster, only if the UI/scheduler is useful immediately.

Defer IgFold, OpenFold, Rosetta/PyRosetta, FoldX, and additional foundation
models until their technical need and commercial licence are resolved.
