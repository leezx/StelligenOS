# WORKLOG — antibody_binder_asset_engineering

Module-scoped log. Append-only: add corrections as new entries rather than
rewriting earlier ones.

Chinese version: [WORKLOG.zh-CN.md](WORKLOG.zh-CN.md). Architecture and algorithm
rationale in Chinese: [GUIDE.zh-CN.md](GUIDE.zh-CN.md).

---

## 2026-07-30 — v0.1.0 → v0.2.0, driven by an enavatuzumab (PDL192) run

**Purpose.** Run the GenModule against a real binder — enavatuzumab, targeting
TWEAK receptor / Fn14 / TNFRSF12A — debug what the run exposed, and upgrade the
module from a work-package outline into something that actually computes, with
the ADC question as the driving use case.

### 1. Baseline state of v0.1.0

Confirmed working before any change: 5/5 tests passed and a run of the bundled
example reported `status: complete`.

That status was misleading. Every scientific field in the output was `None`:
`triage.ranking`, `adc_readiness_score`, and every per-candidate prediction. The
stages emitted static checklists of work to be done. `05_candidate_family_generation`
returned exactly one "candidate" — the unmodified input. The module was a
scaffold that reported success for producing a table of contents.

### 2. Defects found, with evidence

| # | Defect | Evidence | Fix |
|---|---|---|---|
| 1 | `doctor` probed only the orchestrator venv, reporting the entire installed scientific stack as missing | `doctor` said 6/21 tools available; the shared venv actually held ANARCI 2026.2.13.2, abnumber 0.4.4, biopython 1.87, ImmuneBuilder 1.2, IgFold 0.4.0, ESM 3.2.3, torch 2.13.0, pandas 2.3.3, sklearn 1.9.0 | Probe declared imports across both interpreters; report which one satisfied each. Now 17/21 |
| 2 | Interpreter paths were resolved through symlinks, collapsing two venvs into one | Both `.venv/bin/python` and the shared `bin/python` resolve to `/Library/Frameworks/.../python3.12`, so the dedup check discarded the shared runtime as a duplicate and no science could run | Never resolve interpreter paths; a venv's identity is its own unresolved path |
| 3 | Executable checks searched only `PATH` | `ANARCI` is installed in the shared venv's `bin`, not on `PATH`, so it reported missing while being present | Search `PATH`, then the shared runtime's `bin` |
| 4 | Motif scan used non-overlapping `re.finditer` on whole motifs, and returned matched strings with no positions | Adjacent and overlapping reactive residues were consumed by the previous match; a bare list of motif strings cannot drive engineering | Match the reactive residue with a lookahead for context; emit position, scheme position, and region. Regression test: `AANGSTAA` yields both an NG deamidation and an N-G-S sequon on Asn3; `AANNSAA` yields both adjacent asparagines |
| 5 | `unpaired_cysteine_flag_count` was a parity bit named as a count | `counts["C"] % 2` is 0 for four cysteines, hiding two free thiols | Real audit against the canonical intradomain pair, reporting positions and the count beyond canonical |
| 6 | `candidate_sequences` accepted unvalidated | A supplied candidate with invalid residues reached the triage stage unchecked | Validate residues, shape, and the mutation budget in `validate_binder` |
| 7 | Report hardcoded `@0.1.0` | Version string would silently go stale on any bump | Read module id/version from the manifest and pass through run context |
| 8 | `finalize_run` reported which run was blocked but not which stage | Debugging a blocked run required opening the manifest by hand | Added `blocked_stages` |

### 3. Defect found in my own v0.2.0 work, by verification

Worth logging because it was caught by checking output rather than by a failing
test, and because the fix changed a scientific conclusion.

- **Per-candidate humanness was estimated, not computed.** First implementation
  added a flat `+0.55%` per germline reversion to the parent value. Arbitrary, and
  structurally unable to *lower* the value when a substitution moves away from
  germline. Replaced with exact recomputation: `numbering` now emits the germline
  residue at every compared framework position, and framework identity is
  recounted from each candidate's own residues, pooled across chains by position
  count. Verified: parent 148/159 = 93.08%; each single reversion 149/159 = 93.71%;
  the 8-reversion combination 156/159 = 98.11%; and the developability combination
  correctly *drops* to 90.57% for moving four framework positions away from germline.

- **A substitution justified by two rationales was attributed to only one, and
  silently vanished from the other family.** `VL-M37L` removes a methionine
  oxidation site *and* restores the human germline residue at the same position.
  Deduplicating proposals by keeping the higher-priority rationale dropped it out
  of the germline-reverted family entirely — hiding the single most valuable
  substitution in the set. Proposals now carry a merged `sources` list, a
  `dual_benefit` flag, and a priority bonus; families test membership against the
  list. `VL-M37L` is the one dual-benefit substitution found for this binder.

### 4. What v0.2.0 computes

New `lib/` package, each record carrying an explicit `method` and tool version:

- `runtime.py` — interpreter discovery, cross-interpreter import probing, JSON
  sidecar delegation, and the external-execution gate.
- `numbering.py` — ANARCI/abnumber IMGT **and** Kabat numbering, region
  assignment, position maps, closest human germline V/J, framework identity, and
  the per-position germline residues that make humanness exactly recomputable.
- `liabilities.py` — position-resolved, overlap-safe motif scan across 11 rules,
  with three *separated* risk axes: `chemical_risk` (will the chemistry happen,
  scaled by solvent exposure), `functional_consequence` (does it matter where it
  is), `remediation_risk` (how dangerous is it to engineer away). Folding these
  into one number hides the trade-off the designer has to make.
- `biophysics.py` — pI by Henderson-Hasselbalch bisection, net charge, GRAVY,
  extinction coefficient, hydrophobic windows. Every constant table names its
  published source at point of use.
- `structure.py` — ABodyBuilder2 prediction and per-residue absolute/relative
  SASA via biopython Shrake-Rupley against Tien 2013 reference accessibilities.
- `design.py` — rule-based proposer. Every proposal traces to a named liability
  or a named germline deviation and carries its rationale, engineering risk, and
  whether it needs binding confirmation. Builds three independent families as
  real sequences, enforcing the mutation budget, protected positions, and the
  forbidden-motif screen.
- `scoring.py` — multi-objective min-max normalised weighted sum over six
  computed axes, with a versioned policy.
- `adc.py` — 12-criterion readiness matrix with gating flags and the
  satisfied/gap/**adverse** distinction, plus a conjugation inventory.

Also: `execution_order` now differs from the declared stage catalogue in one
place — `09_adc_readiness` runs before `07_experimental_design`, so the
experimental package leads with the experiments that resolve gating ADC
requirements. The declared catalogue and numbering are unchanged.

### 5. Enavatuzumab input of record

`examples/enavatuzumab.yaml`. VH/VL transcribed from US20090074762 /
WO2009020933A2 (PDL BioPharma, inventor Patricia Culp, filed 2008-08-04,
earliest priority 2007-08-03), SEQ ID NO:3 and NO:4.

Sequence validated three independent ways:

1. Assembled from the per-region FR/CDR tables (VH: SEQ 31/13/40/19/49/25/58;
   VL: SEQ 84/66/93/72/102/78/111) and matched against the inline SEQ ID NO:3/4
   listing. The OCR of the inline listing drops the leading `R` of FR3 into a
   parenthesis; the region table supplies it.
2. ANARCI assigns VH → IGHV3-23*04 / IGHJ3*01 and VL → IGKV1-39*01 / IGKJ4*01.
   Human germline assignment is the expected result for a CDR-grafted humanized
   antibody and would not hold for a mis-transcribed sequence.
3. The detected framework deviations from germline include VH `H82`/`H86` and VL
   `L55`, which correspond to the humanization back-substitutions the patent
   documents at Kabat heavy 73/74 and light 49. The pipeline rediscovered them
   from sequence alone.

Evidence fields populated from the local corpus with per-field sources and
caveats, including the cross-source conflicts (mechanism of growth inhibition;
whether a NOAEL was identified in the 13-week cynomolgus study; whether Fn14 is
detectable on healthy hepatocytes).

`constraints.preserve_residues` is deliberately empty: the epitope is defined on
the *target* (Arg56) and no co-crystal exists, so which antibody residues make
contact is unknown. Rather than guess a paratope and silently suppress proposals,
every CDR proposal is emitted and individually flagged.

### 6. Run results

Both runs `status: complete`, no blocked stages.

Sequence-only run:

- 16 liability flags, 3 in CDRs, burden 44.0. No NG or DG motif — the parent is
  chemically clean at the high-severity tier.
- Framework identity VH 92.5%, VL 93.7% (pooled 93.08%).
- 42 proposals (32 liability remediation, 10 germline reversion), 17 requiring
  binding confirmation, 1 dual-benefit.
- 28 candidates across 3 independent families. Parent ranks #15 of 28.

Structure-informed run (`--allow-external`, ABodyBuilder2 + OpenMM refinement):

- **11 of 16 flags downgraded by real solvent exposure; burden 44.0 → 28.82.**
  This is the substantive scientific gain: it identifies which flags to ignore.
- Notably the CDR-H3 methionine (`H115`, relSASA 0.017, buried) drops from a
  top-priority liability to low risk, and the M106 substitutions fall out of the
  top five. Sequence-only analysis would have spent CDR-H3 mutations — the
  highest-risk position in the molecule — on a non-problem.
- Ground-truth check: all four canonical cysteines return buried (relSASA
  ≤ 0.008), as an intradomain disulfide must be.
- Top substitutions become the genuinely exposed tryptophans `W33F/Y`, `W96F/Y`
  and the deamidation sites `N79Q`, `N86Q`.

### 7. ADC verdict for enavatuzumab

`verdict: adverse_evidence_on_a_gating_criterion`. Three gating criteria carry
evidence pointing *against* feasibility, and three more are open gaps:

- **internalization — adverse.** No positive internalisation or lysosomal
  delivery evidence exists in any source reviewed. The only direct statement
  reports the opposite: antibody binding *maintains* TweakR surface expression
  (Purcell 2014, as data not shown). For a payload-delivering ADC this is the
  wrong direction on the single most important requirement. It is weak evidence —
  unshown, no assay described — which is exactly why the resolving experiment is
  ranked decisive rather than treated as settled.
- **naked_antibody_tolerability — adverse.** Phase I MTD 1.0 mg/kg q2w with
  hepatopancreatic DLTs including a Hy's-Law-criteria case, 43% grade ≥3
  drug-related events, and 0% ORR. Toxicity is attributed to agonist signalling
  through the receptor, not ligand blockade. Very little exposure headroom
  remains for a payload.
- **target_expression_normal_tissue — adverse.** On-target expression in exactly
  the organs that produced the clinical DLTs (kidney Bowman's capsule, pancreas,
  bile duct in inflamed liver).
- Gaps: `lysosomal_trafficking`, `adc_in_vivo_activity`, `receptor_turnover`.
- `conjugate_freedom_to_operate` — adverse: the patent of record claims the
  epitope independently (claim 1, any antibody binding Arg56) *and* conjugates
  with cytotoxic agents naming auristatin E/F (claims 24-28). Technical
  observation only; not an FTO opinion.

The honest conclusion, and what the report now says: the sequence-engineering
output is real and usable, but it optimises a molecule whose modality is not yet
justified. The decisive experiment is a quantitative internalisation time course
with a surface-retention control, and it should run before any optimisation
spend. This is why `07_experimental_design` now executes after
`09_adc_readiness` and leads with the gating experiments at priority 0.

Two evidence-grounded strategic notes recorded in the input rather than asserted
as conclusions: agonism is cross-linking/FcγR dependent, so Fc silencing is a
plausible toxicity mitigation (though alternative-NF-κB agonism reportedly
persists when Fc is silenced); and cynomolgus is the only qualified toxicology
species, since mouse TweakR carries Pro56 — and it under-predicted the human
toxicity.

### 8. Verification

```
.venv/bin/python -m pytest genmodules/antibody_binder_asset_engineering/tests/ -q
40 passed
```

Suite grew from 5 to 40 tests. New coverage includes: interpreter
non-collapse, external-execution gating, overlap-safe motif detection, burial
lowering risk without dropping the flag, cysteine audit, candidate-sequence
validation, budget enforcement, forbidden-motif rejection, wild-type verification
on mutation apply, the three constraint selector forms, dual-source proposal
merging, exact framework-identity recomputation in both directions, the
gap-versus-adverse distinction, refusal to emit a readiness score even when all
evidence is supplied, refusal to estimate DAR from variable domains, and
end-to-end checks that every generated candidate is a valid distinct sequence
whose declared substitutions match its emitted residues.

Two assertions in the old suite were deliberately inverted, because the contract
changed and that is what the version bump is for: `triage["ranking"] is None` and
the absence of a candidate ranking. `adc_readiness_score is None` was **kept** —
that boundary did not change and is now asserted in more places.

One test failure during development was my assertion being wrong rather than the
code: I wrote position 4 for the Asn in `AANGSTAA`, which is at position 3. Test
corrected; code was right.

### 9. Not done / next steps

- No learned designer is wired in. Proposals are rule-based. The seam is
  `design.propose_mutations`; ProteinMPNN, ESM, and FoldX/Rosetta remain
  unconfigured (`proteinmpnn`, `rosetta`, `foldx`, `openfold` still report
  missing).
- All 8 declared data roots are unregistered, so `02_ip_fto_landscape` and
  `10_patent_package` remain search plans rather than executed searches.
- Structure is a single conformation, not an ensemble, and framework exposure is
  an upper bound because the Fv is modelled in isolation without CH1/CL packing.
- Conjugation analysis needs the input extended with full-length chains before it
  can say anything about DAR or site-specific chemistry.
- `08_active_learning` fits nothing, correctly, because no experimental
  observation exists yet.
- The `AntibodyAssetEngineeringPackage@0.2.0` output contract is described in
  `DESIGN.md` but has no machine contract file under `components/contracts/`.

---

## 2026-07-30 (second entry) — v0.2.0 → v0.3.0, two-track phenotype rework

**Purpose.** Act on the assessment in
`Zhixins-KB/antibody_binder_asset_engineering v0.2.0优化指南.md`: move the module from
sequence-centric developability optimisation to phenotype-conditioned ADC carrier
engineering, and archive v0.2.0.

The load-bearing critique, which I agree with: v0.2.0 optimises a cleaner, more
humanised, more developable **antibody**, not an antibody that can safely and
effectively **deliver a payload**. For a plain therapeutic antibody it was close
to adequate; for ADC asset engineering it lacked the phenotype layer entirely.

### Archived

v0.2.0 copied verbatim to `genmodules/archive/antibody_binder_asset_engineering/v0.2.0/`
with a `FROZEN.md`. Added `SKIP_DIRS = {"scripts", "archive"}` to
`genmodules/scripts/update_readme.py`: the archived tree contains a complete
`module.yaml` and could be discovered as an active module. The current nesting
happens to avoid it, but that is the kind of thing that breaks later, so it is now
explicit and covered by a test.

### Six structural changes

1. **Two orthogonal tracks.** Track A (binder molecule quality, computed) and
   Track B (ADC carrier phenotype, measured). They meet only at a Pareto frontier.
   `combined_binder_and_carrier_score` is listed as permanently withheld: summing
   them lets a clean sequence compensate for a molecule that does not internalise,
   which is the one trade a delivery programme must never make.
2. **`lib/phenotype.py`** — the single `internalization` criterion becomes a
   five-step cascade (surface departure, endosomal entry, lysosomal delivery,
   linker processing, cytotoxic sufficiency). 15 measurement types, 8 mandatory
   metadata fields. An observation missing metadata is `unusable`, not
   partially credited. Fractions must declare a `normalization_basis`. Killing
   requires an antigen-negative counter-screen. `adc_carrier_quality_score` is
   `null` when unmeasured, never 0, so missing data cannot read as a negative.
3. **`lib/failure_modes.py`** — two causal trees, 15 modes, 6 route-terminating,
   11 experiments each declaring what it can exclude or support. Output is the
   next experiment by information gain, not a gap count.
4. **`lib/pareto.py`** — dominance over both axes; a missing axis is
   `incomparable`, not zero; with no carrier data the module refuses to name a
   lead. Carrier quality is never inherited by a variant from its parent.
5. **Four construct-specification families** (function-silenced, valency,
   kinetic ladder, conjugation format), kept visibly separate from generated
   sequences. Fc sequence and affinity-modulating sequence are not fabricated.
6. **`lib/product.py`** — AntibodyCandidate x ConjugationVariant ->
   ADCProductCandidate. No product property is estimated.

### Defect found in this work, which changed a scientific conclusion

The naive information-gain metric ranked `lysosomal_flux_quantification` (gain 4)
above `modality_kill_internalization_panel` (gain 3). Wrong twice over:

- **No overturn credit.** `surface_retention` was already `supported` by one
  "data not shown" sentence, so a naive unresolved-mode count treated it as
  settled and awarded the assay that directly tests it zero. A supported
  route-terminating mode is precisely what must be tested, especially when the
  evidence behind it is far weaker than the evidence needed to act on it. Fixed:
  excluding a currently-supported mode now scores highest (4 route-terminating, 2
  otherwise).
- **No prerequisite structure.** The cascade is sequential, so a step-3 fraction
  is uninterpretable without the step-1 denominator and baseline. Fixed:
  experiments declare `prerequisite_steps`; unmet ones rank after ready ones
  regardless of raw gain.

After the fix the order matches the guide's Phase 0: internalisation panel (gain
7, overturns `surface_retention`), then construct signalling comparison (gain 5),
then normal-cell uptake (gain 4), with the three downstream cascade assays
correctly blocked. Also added: a supported failure mode is never downgraded to
excluded by weaker evidence.

Secondary fix: the report listed only `resolves_unresolved_modes` for the top
experiment, omitting `can_overturn_supported_modes` — the actual reason it ranks
first. The report now highlights the overturnable blocking finding and the
critical-path table carries a `Ready` column.

### Renames

`developability_score` -> `sequence_computational_developability_score`;
`04_ai_guided_engineering` -> `04_binder_engineering_design` (it is rule-based, so
"AI-guided" was misleading); `06_computational_triage` ->
`06_binder_quality_triage`; `09_adc_readiness` -> `09_adc_failure_mode_analysis`.
Full v0.2.0 -> v0.3.0 stage map in `STAGE_MIGRATION_FROM_0_2_0`.

### Deliberately not done

No learned sequence designer. The bottleneck is the objective function, not
proposal generation: without measurable non-agonism, lysosomal flux, and
conjugated-state stability, a model would optimise the wrong target more
efficiently. `12_active_learning` still fits nothing and instead becomes a strict
data closed loop. No fabricated "with data" example is shipped; the positive path
is covered by tests using obviously synthetic values.

### Verification

`pytest -q` → **63 passed** (was 40). One enavatuzumab run,
`status: complete`, no blocked stages.

Enavatuzumab result: 0 usable carrier observations (a finding, not an omission —
every available trafficking statement is a text summary or unshown data and none
carries the required metadata), so the cascade is `no_data` from step 1,
`adc_carrier_quality_score` is null, there is no Pareto frontier, and the modality
decision is `modality_unproven_run_kill_experiment` with 0 of 7 continue
conditions met. Three route-terminating failure modes are actively supported:
`surface_retention`, `receptor_agonism`, `normal_tissue_target_expression`. 48
product candidates enumerated, 0 buildable. Sole computed conjugation finding:
`H59` is a CDR-accessible lysine, so a site-specific chemistry is recommended.

### Remaining work

Track B needs real data to be useful; half of v0.3.0's value is in what it
refuses to do. Failure trees are enumerated, not exhaustive. Information gain
ignores assay difficulty. Product properties all await input or experiment.
Construct specifications need constant regions; the kinetic ladder needs a
campaign. SASA is still a single isolated-Fv conformation with run-to-run
variation. Data roots remain unregistered. No machine contract file for
`AntibodyAssetEngineeringPackage@0.3.0`.

### Pre-existing issue, still not fixed

`configs/historical_adc_benchmark.yaml:4` still points at the old KB path. Carried
forward from the previous entry; unchanged for the same reason.

---

## 2026-07-30 — v0.3.0 → v0.3.1, driven by a TPP-2658 (anti-TWEAKR, Bayer) run

**Purpose.** Optimise TPP-2658 with the sequence in hand. The run instead exposed
four risk-classification defects in 0.3.0, each of which made a dangerous
substitution look safe. Fixing them changed the answer for TPP-2658 completely,
which is why they are recorded as defects rather than refinements.

### 1. Baseline: what 0.3.0 recommended for TPP-2658

23 candidates in three families. Rank 2 (`DEV-C01`, score 0.5991) bundled
`VH-D62E` and `VH-W110F`. A `germline_reverted` family of 4 candidates was built
from `VH-I35S`, `VH-Y50A`, `VH-H59Y`. Of 26 proposals, 4 were marked as needing
binding confirmation.

Every one of those specific outputs was wrong.

### 2. Defect: region assignment used IMGT alone

`numbering.position_maps(raw, "imgt")` fed `region` into
`liabilities.FUNCTIONAL_CONSEQUENCE` and `design.RISK_TIER_BY_REGION`. IMGT and
Kabat disagree at 18 VH and 9 VL positions in TPP-2658, verified residue by
residue. Under IMGT, Kabat CDR-H1 34-35 and the Kabat CDR-H2 tail 58-65 fall in
FR2/FR3.

Concretely: `VH-D62E` was the second-highest-priority proposal, marked region FR3,
`engineering_risk: low`, `requires_binding_confirmation: false`. D62 sits inside
`YISPSGGSTHYADSVKG` — the patent's own CDR-H2 consensus formula for this antibody.
The module was offering a substitution in the middle of an affinity-matured CDR as
a framework tidy-up needing no affinity check.

**Fix.** `numbering._union_map` merges the two maps on linear position, asserting
residue identity and degrading to IMGT if they do not align. `region` becomes
whichever assignment costs more to disturb; `imgt_region`, `kabat_region`, and
`region_definitions_agree` are reported on every hit and proposal. Framework
identity still uses IMGT frameworks only, so humanness stays comparable.

`VH-D62E` is now CDR2, `engineering_risk: high`, `requires_binding_confirmation:
true`, and excluded from the conservative family.

### 3. Defect: no notion of conserved structural anchors

The module proposed `VH-W36F/Y` (IMGT H41), `VH-W110F/Y` (IMGT H118), and
`VL-W35F/Y` (IMGT L41), all at `engineering_risk: low`. These are the two core
tryptophans and the J-region TRP: invariant landmarks of the immunoglobulin fold.
`VH-W110F` was inside the rank-2 combined candidate.

**Fix.** `numbering.STRUCTURAL_ANCHORS` covers IMGT 23, 41, 89, 104, 118.
Proposals there are declined into `rejected_proposals` with the anchor name and
guidance to control oxidation by formulation rather than sequence. Declined rather
than flagged, because unlike every other proposal here it is not a trade a
reviewer could reasonably take; kept in the record so the liability is visibly
seen and visibly refused. `remediation_risk` is pinned at 3 for anchors.

### 4. Defect: burial lowered priority without raising risk

`_exposure_factor` scaled chemical risk down for buried residues — correct, since
solvent and peroxide access is lower — and did nothing else. So a buried core
substitution emerged as the *cheapest* fix available, at `engineering_risk: low`
with no confirmation required.

The two axes move in opposite directions. Burial lowers chemical urgency and
raises remediation cost, because a buried side chain is packed against its
neighbours. A buried liability is the least urgent and most expensive to fix.

**Fix.** `REMEDIATION_COST_BY_EXPOSURE` adds a burial penalty to
`remediation_risk`. `FOLD_RISK_ESCALATION` escalates `engineering_risk` by tier
and sets `requires_fold_confirmation`, deliberately not
`requires_binding_confirmation`: burial is settled by expression and
thermostability, not by an affinity assay.

`VH-W47F`, `VH-M83L`, `VH-D90E` went from `low` to `high`. `VL-M4L` went from
`low` to `moderate`.

### 5. Defect: germline-encoded liabilities looked like antibody defects

The three FR3 deamidation fixes `VH-N74Q/N77Q/N84Q` were the whole
`conservative_liability_removal` family — "the safest way to improve the parent".
The triage then scored all three *below* the unmodified parent, which is what
prompted the check: N82, N85 and N92 (IMGT) are the IGHV3-23 germline residues.
Removing them lowers framework identity. The score priced that correctly at
weights 0.20 humanness against 0.35 burden, but nothing in the output said so, so
the ranking looked like a scoring artefact rather than a finding.

**Fix.** `germline_encoded` is carried on every hit as a tri-state, and
`reduces_framework_humanness` on every proposal, with the rationale text extended
to name the cost. `null` means the position is outside the V-gene framework
alignment — CDR3 is junctional and FR4 is J-derived — and must not be read as
somatic; this follows the module's existing rule that missing data is not a
negative result. Summary counts split into `germline_encoded_hits`,
`somatic_hits`, and `germline_comparison_unavailable_hits`.

For TPP-2658 this is decisive: **11 germline-encoded, 0 somatic, 2 not
comparable.**

### 6. Consequences for the candidate families

- `conservative_liability_removal` now requires framework under both definitions
  *and* an unescalated risk tier, so a buried core change cannot enter the family
  that claims to be safest.
- `germline_reverted` now requires framework under both definitions. All three of
  TPP-2658's IMGT-framework germline deviations are Kabat CDR residues, so the
  family is **correctly empty** — the module previously manufactured 4 candidates
  that should not exist.
- `proposals_in_no_family` was added so tightening the filters does not make live
  proposals vanish between stage 04 and stage 05.

### 7. The score cannot express any of this

Track A weights liability burden at 0.35, so a combined candidate that bundles
several substitutions ranks well almost regardless of what it bundles. `DEV-C01`
still ranks 2nd at 0.66. The fix is not to re-weight the score — it is a computed
descriptor comparison with `promotion_eligible: false` — but to put the flags in
the same table. `highest_engineering_risk`, `requires_fold_confirmation` and
`reduces_framework_humanness` now travel on each triage row and in the report,
with a note that the score does not include them.

### 8. Verification

81 tests pass, up from 63. New tests cover: the union map promoting a Kabat CDR
call, falling back to IMGT on residue mismatch, and the tri-state germline flag;
anchor liabilities being reported but never proposed; burial moving the two axes
in opposite directions; buried substitutions asking for a fold check and not a
binding check; the humanness-cost rationale; and five TPP-2658 integration
assertions including the empty germline family and D62E's contested region.

The version test now reads the version from `module.yaml`, and the report
assertion does too, so a bump cannot break the tests while leaving the report
stamped wrong.

### 9. Known gaps unchanged by this release

- Track B still has no data for TPP-2658. `adc_carrier_quality_score` is `null`,
  meaning unmeasured.
- `STRUCTURAL_ANCHORS` covers the five IMGT landmarks. Positions that are highly
  conserved without being IMGT anchors — VH 47 is the clearest case — are caught
  only by burial, not by conservation. A per-position germline-frequency table
  would cover them properly.
- Region union is computed from IMGT and Kabat only. Chothia and contact
  definitions are not consulted.
- `configs/historical_adc_benchmark.yaml:4` still points at a moved ADC drugs
  tree, so `tests/test_historical.py` has 4 pre-existing failures. Shared config
  outside this module; reported, not changed.

## 2026-07-31 — v0.3.1 formal contract stabilization

- Froze the formal module at 14 stages. Evidence-graph and cross-asset retrieval
  remain preserved prototypes but are not registered or emitted by v0.3.1.
- Published executable input/output YAML contracts at v0.3.1 and integrated
  source-version normalization, manifest identity, catalogue hashing, per-artifact
  SHA-256 references, and final package validation into the runner.
- The active release identity is consistently module 0.3.1, input 0.3.1, output
  0.3.1, manifest 0.3.1, and 14 stages.
- Preserved the legacy TPP-2658 run unchanged and reran it as
  `v031-tpp2658-contract-consistent`; the replacement contract validation passed.
- Regression result: 107 tests passed.

---

## 2026-07-31 — v0.3.1 → v0.4.0, three evidence layers

**Purpose.** The pipeline could produce a recommendation but not defend it. It would
report `internalization = adverse`, rank a kill experiment first, and leave a reviewer
asking *why that one and not lysosomal trafficking* with nowhere to look but the
ranking function. It also analysed each asset in isolation next to a curated corpus of
379 clinical ADCs.

Three layers, no new science in the first one by design.

### 1. Evidence tiers and confidence propagation

`lib/evidence.py`. Six tiers, weakest first: patent, literature, internal_assay,
adc_precedent, animal_efficacy, human_evidence. The order is declared programme
policy, arguable and reviewable in one tuple, not a fact about the world.

Five quantities reported **separately**, because blending them is what makes a
confidence score untrustworthy:

    direction_agreement   tier-weighted signed agreement in [-1, 1]
    evidence_count        how many entries bear on the criterion
    evidence_diversity    how many distinct tiers they span
    evidence_freshness    age of the newest entry, banded
    confidence_band       composite over tier, diversity and freshness

`direction_agreement` is scale-free on purpose: ten agreeing patent sentences score
1.0 because they are one tier repeated ten times. `confidence_band` stays `weak` in
that case, which is the point of having both.

Freshness uses the run manifest timestamp, never the clock, so re-executing a stage
in an old run directory reproduces its numbers.

### 2. The reasoning graph

`lib/evidence_graph.py`, stage `15_evidence_graph`. Observation → Hypothesis →
Failure mode → Decision → Experiment. Every edge carries `because`.

It infers nothing; every edge was already computed by stages 07 and 09 and was
visible only as control flow. Its one genuine addition is `rejected_alternatives`:
every unselected experiment gets a `reason_code` and a sentence. On TPP-2658 that is
load-bearing — `lysosomal_flux_quantification` **ties** the selected experiment on
information gain (4 vs 4) and is separated only by an unmet prerequisite. Without the
rejection record the ranking looks arbitrary.

`hypotheses_without_observations` lists criteria no observation reaches.

### 3. Cross-asset retrieval

`lib/cross_asset.py`, stage `16_cross_asset_retrieval`. 379-case corpus, 219 with
usable attribute frontmatter. Weighted match over target, payload family, cleavable,
conjugation family and DAR band; matched, differing and uncomparable attributes are
all reported, because *how it differs* is the actionable half.

Not embeddings, deliberately: an embedding ranks comparators without showing which
attribute drove the ranking.

Validation probe in the suite: a HER2 + DXd input must return Enhertu first at
matched weight 11 of 12. If it does not, the layer is broken.

### Defects found and fixed while building this

1. **The `internal_assay` keyword matched "internalisation".** A literature finding
   was tiered as in-house assay data. Fixed with word boundaries and phrase anchors.
2. **Generic target words manufactured same-target matches.** "TWEAK receptor (Fn14)"
   shares the token `receptor` with ROR1, CD71 and FR-alpha, and retrieval reported
   all three as same-target comparators. This is the most misleading output the layer
   can produce. Fixed with `TARGET_STOPWORDS`.
3. **Similarity inflated on a partial basis.** A comparator with four uncomparable
   attributes and one lucky match outranked one compared on everything. Ranking now
   uses absolute matched weight; rows carry `similarity_is_partial`.
4. **A ranked list of ties read as "here are your comparators" when the answer was
   "there aren't any".** TPP-2658 has no same-target and no same-payload-class
   comparator in the corpus. Added an explicit `no_close_precedent` verdict, because
   unprecedented on both axes is a finding.
5. **`evaluate_cascade` never emitted a key named `observations`**, which is what the
   graph read. The measured-evidence layer was therefore absent from every graph, and
   invisible precisely on binders with no carrier data, where a missing layer looks
   correct. `evaluate_cascade` now emits `usable_observations`.

Defects 1, 2 and 5 were caught by inspecting output rather than by a failing test.
Defect 5 was raised as an objection during review of the prototypes and was right.

### The naming objection, and why it was right

A review of the prototypes objected that "the signed evidence direction is not an
epistemic-confidence contract". Correct. A field called `confidence` that measures
whether sources agree invites exactly the misreading it should prevent. Renamed to
`direction_agreement`, with the semantics string saying so, and `confidence_band`
added as the composite a reviewer actually means.

### Contracts

`ExistingBinderAssetInput@0.4.0` (shape unchanged; the version tracks the module so a
consumer pins one pair) and `AntibodyAssetEngineeringPackage@0.4.0`, which moves the
two stages out of `explicitly_not_registered` into the accepted catalogue, adds their
required fields, adds `evidence_confidence` to stage 09, and declares
`evidence_semantics` so a consumer cannot read `direction_agreement` as a probability.

### Verification

108 passed, 1 skipped. Both example antibodies run all 16 stages with
`contract_validation.status: passed` and `errors: []`.

The skip: `test_archived_v0_2_0_is_frozen_and_not_discoverable` now skips its second
half because `genmodules/scripts/update_readme.py` has been removed from the
workspace. The freeze assertions still run; the discoverability check re-arms if the
generator returns. **The generator's absence means `genmodules/README.md` is no longer
regenerable — reported, not fixed, as it is outside this module.**

### Known gaps

- Retrieval reads attribute frontmatter only. 160 of 379 corpus files have none, so
  absence from a comparator list is not evidence that no comparator exists.
- Gate-vector retrieval is not implemented and should not be: this module may not
  compute Gate scores. It belongs in the Gate layer.
- Tier inference is keyword-based on source text. `evidence_tier` in the input
  overrides it, and should be used wherever the tier matters.
- `confidence_band` thresholds are a rule, not a calibration.
