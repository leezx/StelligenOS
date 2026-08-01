# GenModule design

Current version: `0.4.0`. Predecessor: `0.3.1`. Last
archived version: `0.2.0`, at
`genmodules/archive/antibody_binder_asset_engineering/v0.2.0/`.

## Boundary

The GenModule generates and organizes antibody asset candidates. Gates decide
whether the resulting evidence is sufficient. The module never writes Gate scores
or modifies Gate/Model components.

## The two tracks

0.3.0's organising idea is that an ADC carrier is not a more developable naked
antibody plus a payload. The two optima can diverge: a naked antibody may want
strong receptor agonism and Fc effector function where a carrier needs them
silenced; a naked antibody tends to want maximal affinity where a carrier may
trade affinity for tumour penetration and receptor turnover.

    Track A  Binder molecule quality      COMPUTED from sequence and structure
             01 -> 03 -> 04 -> 05 -> 06
             emits sequence_computational_developability_score

    Track B  ADC carrier phenotype        MEASURED from structured observations
             07 -> 08
             emits adc_carrier_quality_score

The tracks are combined **only** by Pareto dominance in `10_pareto_selection`.
`combined_binder_and_carrier_score` is permanently withheld: summing the axes
would let a clean sequence compensate for a molecule that does not deliver
payload, which is the one trade a delivery programme must never make.

## Region definitions and the three risk axes

Added in 0.3.1, after a TPP-2658 run showed 0.3.0 handing out a "low risk, no
binding confirmation needed" substitution in the middle of an affinity-matured
CDR-H2.

**Region risk is the union of IMGT and Kabat.** The two definitions are not
competing truths — IMGT boundaries are structural, Kabat boundaries are
variability-derived — and they disagree at 18 VH and 9 VL positions in a typical
V domain. Under IMGT alone, Kabat CDR-H1 34-35 and the Kabat CDR-H2 tail 58-65
land in FR2/FR3. A position is treated as CDR if **either** definition says so,
and both assignments are reported on every hit and every proposal, with
`region_definitions_agree` marking the contested ones. Framework identity is
still computed over IMGT frameworks only, so humanness numbers stay comparable
with the literature; the union governs risk, not identity.

**Conserved structural anchors are declined, not proposed.** IMGT positions 23,
41, 89, 104 and 118 are invariant landmarks of the V-domain fold. A liability
there is reported — the core tryptophans really are oxidation-prone — but no
substitution is emitted. Every other proposal in the module is a trade a reviewer
could reasonably take; this one is not, because the anchor is invariant across the
fold rather than merely conserved in one lineage. Declined proposals stay in
`rejected_proposals` with a reason, so the liability is visibly seen and visibly
declined, and the guidance points at formulation control instead.

**Burial moves the two risk axes in opposite directions.** 0.3.0 scaled chemical
risk down for buried residues, which is right: solvent, peroxide and light reach
a buried side chain less well. It stopped there, so a buried core substitution
came out as the *cheapest* available fix. Burial also raises the cost of
remediation, because a buried side chain is packed against its neighbours. A
buried liability is therefore the least urgent and the most expensive to fix.

Three risks are tracked separately because different experiments settle them:

| Flag | Meaning | Experiment that settles it |
|---|---|---|
`requires_binding_confirmation` | CDR under IMGT or Kabat | affinity remeasurement |
`requires_fold_confirmation` | buried or partially buried side chain | expression, thermostability |
`reduces_framework_humanness` | the residue removed is the germline residue | none; it is a known cost |

A proposal can carry all three.

**Germline-encoded liabilities are tri-state.** A liability whose residue *is* the
closest human germline residue is shared with every antibody built on that V gene.
Its prevalence across approved products is evidence that the risk is tolerated,
and remediating it lowers framework identity in exchange for a risk the human
repertoire already carries. `germline_encoded` is `true`, `false`, or `null`;
`null` means the position lies outside the V-gene framework alignment (CDR3 is
junctional, FR4 is J-derived) and must not be read as somatic. The engineerable
set is the `somatic` subset.

Two family filters tightened as a consequence. `conservative_liability_removal`
now requires framework under both definitions *and* an unescalated risk tier, so
a buried core change cannot enter the family that claims to be safest.
`germline_reverted` now requires framework under both definitions, so a paratope
change cannot be ordered under a humanisation rationale. Proposals no family
accepts are listed in `proposals_in_no_family` rather than disappearing.

## The evidence layer

Added in 0.4.0. Direction alone (`supportive` / `adverse`) resolves a failure mode
but cannot answer the reviewer's next question, which is always "on what strength of
evidence?". A patent sentence and a repeat-dose animal study both read `supportive`.

Five quantities, reported separately because blending them is what makes a
confidence score untrustworthy:

| Field | Meaning |
|---|---|
`direction_agreement` | tier-weighted signed agreement in [-1, 1] |
`evidence_count` | how many entries bear on the criterion |
`evidence_diversity` | how many distinct tiers they span |
`evidence_freshness` | age of the newest entry, banded |
`confidence_band` | composite label over tier, diversity and freshness |

`direction_agreement` is **scale-free on purpose**: ten agreeing patent sentences
score 1.0, because they are one tier repeated ten times, not stronger evidence.
`confidence_band` is what a reviewer means by confidence, and it stays `weak` in that
case. It is a coarse label rather than a number because the inputs are a tier guess,
a count and a year.

Tier ladder, weakest first: patent, literature, internal_assay, adc_precedent,
animal_efficacy, human_evidence. The order is a **declared programme policy** in
`lib/evidence.py`, reviewable and arguable — an assay on this molecule is more
specific than a precedent set by a different ADC — not a fact about the world.

Freshness is measured against the run manifest timestamp, never the clock, so
re-executing a stage inside an old run directory reproduces its numbers.

## The reasoning graph

`15_evidence_graph` reifies reasoning the module already performed. It infers
nothing. Its one addition over the control flow it replaces is the record of what
was **rejected**: every unselected experiment carries `reason_code`
(`blocked_by_prerequisite`, `no_information_gain`, `lower_information_gain`) and a
sentence. On TPP-2658 this is load-bearing — `lysosomal_flux_quantification` ties the
selected experiment on information gain, and only the prerequisite rule separates
them. Without the rejection record the ranking looks arbitrary.

`hypotheses_without_observations` lists criteria no observation reaches. Those are
the dossier's real holes.

## Cross-asset retrieval

`16_cross_asset_retrieval` compares declared attributes against a clinical ADC
corpus. Deliberately not embeddings: an embedding ranks comparators without letting
a reviewer see which attribute drove the ranking, which is the opposite of the point.

Three honesty constraints, each learned from the corpus:

1. **The KB folder is not an outcome.** `Approved/2019-RovaT-DLL3.md` sits in
   `Approved/` and was terminated in 2019. `kb_folder` is reported as an
   organisation label, never as a result.
2. **Coverage is partial** and is reported: usable versus skipped case counts.
3. **Generic words are stopped.** "TWEAK receptor (Fn14)" shares the token
   `receptor` with ROR1, CD71 and FR-alpha; without a stopword list the retrieval
   reports them as same-target comparators, which is the most misleading output this
   layer can produce.

Similarity over a partial attribute basis inflates, so ranking is by absolute
matched weight and each row carries `similarity_is_partial`.

Gate-vector retrieval is **not** implemented: this GenModule may not compute Gate
scores. It belongs in the Gate layer, reading the historical benchmark whose curated
cases carry verified terminal status.

## Frozen input

`ExistingBinderAssetInput@0.3.1`. Backward compatible with 0.1.0 (scalar evidence
values), 0.2.0 (evidence mappings with `direction`), and 0.3.0. Older records are
normalized to 0.3.1 while their source contract remains recorded in the manifest.

Fields as in 0.2.0, plus:

- `adc_carrier_observations` — a list of structured phenotype observations.
- `payload` — declared linker and payload class, or explicitly undeclared.

### Carrier observation schema

Fifteen measurement types. Eight mandatory metadata fields: `cell_line`,
`endogenous_or_engineered`, `target_density`, `timepoint`, `concentration`,
`assay_method`, `biological_replicates`, `uncertainty`. Plus at least one of
`raw_value` / `normalized_value`.

Three enforcement rules, each of which turns an assertion into data:

1. **Missing metadata makes an observation `unusable`**, not partially credited. A
   measurement whose cell line, timepoint, and concentration are unknown cannot be
   compared with any other measurement.
2. **Fraction-type measurements must declare `normalization_basis`.** The question
   is never "were puncta visible" but "what fraction of surface-bound antibody
   reached the lysosome, in what time". A fraction with no denominator is not a
   fraction.
3. **A killing readout requires an `antigen_negative_counter_screen`** before it
   can support `cytotoxic_sufficiency`. The claim is antigen-dependent killing;
   killing alone does not establish dependence.

### The five-step delivery cascade

`internalization` as a single boolean is prohibited. It collapses five physically
distinct events, any one of which sinks an ADC:

| Step | Criterion | Failure meaning |
|---|---|---|
| 1 | `surface_departure` | Surface retention; nothing enters the cell |
| 2 | `endosomal_entry` | No intracellular pool forms |
| 3 | `lysosomal_delivery` | Recycling dominates degradation |
| 4 | `linker_processing` | Payload stays conjugated and inert |
| 5 | `cytotoxic_sufficiency` | Delivery real but sub-lethal, or not antigen-dependent |

The cascade is sequential: a later step is not credited while an earlier one has
no data, and carries `gated_by`.

## Frozen output

`AntibodyAssetEngineeringPackage@0.3.1` contains everything 0.2.0 emitted, plus:

- the five-step cascade with per-step supporting, refuting, and blocked observations;
- `adc_carrier_quality_score` and a modality decision (7 continue / 8 stop rules);
- two causal failure trees with 15 modes, 6 of them route-terminating;
- experiments ranked by information gain, with overturn credit and prerequisite gating;
- a two-axis Pareto frontier, or an explicit refusal to produce one;
- an ADC product matrix over the three-entity model;
- four construct- and campaign-specification families, distinct from generated sequences.

Added in 0.3.1, on every liability hit and mutation proposal: `imgt_region`,
`kabat_region`, `region_definitions_agree`, `structural_anchor`,
`germline_encoded` (tri-state), `germline_residue`, `remediation_cost_note`,
`requires_fold_confirmation`, `reduces_framework_humanness`,
`engineering_risk_basis`; and on candidate rows `highest_engineering_risk`. The
output contract is bumped rather than treated as a field addition because
`region` changed meaning: it is now the union of IMGT and Kabat, not IMGT alone.

## Execution states

- `planned`: contract emitted; stage not executed.
- `complete`: deterministic built-in work completed.
- `complete_with_gaps`: built-in work completed but external evidence/tools are
  still required.
- `blocked`: frozen input is invalid or a required upstream artifact is absent.

Cascade criteria additionally use `supported` / `refuted` / `no_data` /
`conflicting`, and failure modes use `excluded` / `supported` / `unresolved`.

## Stage order

The declared catalogue is also the execution order. 0.2.0 needed them to diverge
so ADC readiness could precede experimental design; 0.3.0 resolves that
structurally by placing the phenotype and failure-mode stages earlier.

See `STAGE_MIGRATION_FROM_0_2_0` in `stages.py` for the 0.2.0 → 0.3.0 stage map.

## Runtime model

Unchanged from 0.2.0. Two interpreters resolved at run time: the orchestrator
an external orchestrator runtime and the shared scientific runtime
(`SOFTWARES/venvs/antibody_pipeline_shared/py311`, override with
`ANTIBODY_SHARED_PYTHON`). Declared imports are probed in both; executables are
searched on `PATH` then in the shared runtime's `bin`.

Interpreter paths are never resolved through symlinks. Both venvs symlink to the
same framework interpreter, so resolving collapses two environments onto one path
and the shared runtime is silently discarded as a duplicate.

## External execution

`external_execution_policy: disabled_by_default`, unchanged.

- **Declared library computation** — numbering, SASA, liability scanning, scoring,
  phenotype evaluation. Runs by default; each record names tool and version.
- **External execution** — heavyweight model inference, currently
  `predict_structure` via ABodyBuilder2. Requires `--allow-external` and sets
  `external_programs_executed: true`.

## Scores

| Score | Status |
|---|---|
`sequence_computational_developability_score` | Emitted. Track A. Within-run comparability only. `promotion_eligible: false`. |
`adc_carrier_quality_score` | Emitted only with usable observations. `null` means **unmeasured, not poor**. Never inherited by a variant. |
`adc_readiness_score` | Never emitted. |
`dar_estimate` | Never emitted from variable domains. |
`combined_binder_and_carrier_score` | Never emitted. |

`developability_score` was renamed to
`sequence_computational_developability_score` because the short name invited
readers to treat the top-ranked row as the best candidate overall.

## Candidate family kinds

| Kind | Families | Orderable as a gene? |
|---|---|---|
`sequence` | conservative_liability_removal, developability_optimized, germline_reverted | Yes |
`construct_specification` | function_silenced, valency_clustering | Only with constant-region input |
`campaign_specification` | kinetic_ladder | No; needs a scanning or selection campaign |
`product` | conjugation_format | Handled as ADC product entities |

The distinction is load-bearing. Fc sequence and affinity-modulating sequence are
not fabricated: predicting the direction and magnitude of an affinity change
requires an antigen-complex structure or a trained model, and the module has
neither.

## Model-backed design

Deliberately absent, and not the next priority. The bottleneck is the objective
function, not proposal generation: without measurable non-agonism, lysosomal flux,
normal-tissue uptake, and conjugated-state stability, a learned designer would
optimise the wrong target more efficiently. `12_active_learning` therefore fits
nothing and instead enforces a strict data closed loop. The attachment seam is
`design.propose_mutations`.

## Known limitations

- Track B needs real data to be useful; with none, its only output is "measure it".
- Failure trees enumerate modelled modes, not all possible ones. An `excluded`
  mode is excluded only to the strength of its cited evidence.
- Information gain ignores assay difficulty, duration, and cost; `cost_tier` is
  reported for human trade-off.
- Design proposals are rule-based.
- SASA comes from a single predicted conformation of an isolated Fv, so framework
  accessibility is an upper bound, and structure prediction varies run to run.
- No antigen complex is modelled, so every CDR substitution is flagged as
  requiring binding confirmation.
- Product properties all resolve to `requires_input` or `requires_experiment`.
- No machine contract file exists under `components/contracts/`.
- No "with data" example ships, to avoid a fabricated dataset being mistaken for
  real measurements; the positive path is covered by tests.

## Versioning

Any change to stage order, input/output meaning, built-in scoring, command adapter
behavior, or evidence boundary requires a new module version.

0.3.0 changes stage order and numbering, input meaning (carrier observations),
output meaning (two tracks), and built-in scoring (renamed Track A score, new
Track B score), which is why it is a new minor version rather than a patch.

0.3.1 changes built-in scoring — region assignment feeds `functional_consequence`,
which feeds `liability_burden`, so Track A scores differ from 0.3.0 — and adds
output fields. The input shape is unchanged from 0.3.0; the published normalized
contract is `ExistingBinderAssetInput@0.3.1` so module, manifest, and both machine
contracts share one stabilization version.
Because the change is a correction rather than a capability, 0.3.0 was superseded
in place instead of archived: no run should be reproduced against it.
