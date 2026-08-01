# experimental/

## Status change, 2026-07-31

`lib/evidence.py`, `lib/evidence_graph.py` and `lib/cross_asset.py` were held here as
non-registered prototypes during 0.3.1. They are **registered stages in 0.4.0**:

- `15_evidence_graph` and `16_cross_asset_retrieval` are members of `STAGES` and
  `STAGE_FUNCTIONS`;
- both declare required fields in
  `contracts/antibody_asset_engineering_package.v0.4.0.yaml`;
- `09_adc_failure_mode_analysis` additionally emits `evidence_confidence`.

Two objections raised while they were held here were valid and are fixed:

1. **"The signed evidence direction is not an epistemic-confidence contract."**
   Correct. The field is now named `direction_agreement` and says in its own
   semantics string that ten agreeing patent sentences score 1.0 and justify
   nothing. `confidence_band` is the composite a reviewer means, derived from tier,
   diversity and freshness, and it is a coarse label because the inputs are a tier
   guess, a count and a year.
2. **"`evidence_graph.py` does not receive the usable carrier observation
   collection."** Also correct, and it was a live defect: `evaluate_cascade` never
   emitted a key named `observations`, which is what the graph read, so the measured
   evidence layer was absent from every graph. Invisible on binders with no carrier
   data, which is when a missing layer looks correct. `evaluate_cascade` now emits
   `usable_observations` and the graph consumes it; covered by
   `test_usable_carrier_observations_reach_the_graph`.

## Ownership

The `experimental/README.md` of 0.3.1 argued that production evidence-graph and
cross-asset reasoning belong to a future `biotech_asset_due_diligence` GenModule.
That remains a reasonable destination and is **not settled by this release**. What
0.4.0 registers is deliberately narrow:

- the graph reifies *this module's own* reasoning and infers nothing new;
- retrieval compares declared attributes and is explicitly barred from predicting
  outcomes;
- gate-vector retrieval is **not** implemented here, because this GenModule is
  contractually forbidden from computing Gate scores. That belongs in the Gate
  layer, reading `configs/historical_adc_benchmark.yaml`, whose curated cases carry
  verified terminal status.

If the due-diligence module is built, these three libraries are the natural thing to
move; nothing in 0.4.0 depends on them staying here.
