# ChatGPT Review Record: EVGAP-02 contract v0.2.0 and revision 3 retrieval layer

- Review date: 2026-08-06 EDT
- Pull request: #62
- Approved head: `aa3583dc0bc1180504b08c56e7bbeee9a991dbf7`
- Base branch: `main`
- Merge commit: `17c5707`
- Reviewer: ChatGPT
- Decision: `APPROVE` (Round 4)
- Relayed by: human lead
- Record type: **verbatim as relayed by the human lead.** The conclusions quoted
  below are reproduced as received, not paraphrased.
- GitHub review record: **none.** The reviewer attempted to write the formal
  review through the GitHub connector and received `403`. This file is therefore
  the only durable record of the decision.

## Reviewed artefact

External package, never in the repository:

- `gen_iet_evgap_02_crc_linkage_20260805T190453Z_rev3.zip`
- ZIP SHA-256 `81baa45f23f180c68b16d18c83284b60bdee725c017e668e590d4e80b04176e9`
- 46,292 bytes, 8 files plus one directory entry

## Reviewer's verification, as relayed

The reviewer verified the package directly:

- ZIP SHA-256 matches the PR declaration:
  `81baa45f23f180c68b16d18c83284b60bdee725c017e668e590d4e80b04176e9`
- 8 actual files, plus 1 directory entry
- the in-package `verify_package.py` runs independently and passes
- `65/65 MATCH`
- retrieval candidates: 979
- linkage assertions: 0
- pair dispositions: 369
- `L3-00`: 27
- `L3-01`: 342
- `L3-02` through `L3-05`: all 0
- `Undisclosed`, `EDBN`, `AG7`: 9 pairs each, all `L3-00`
- `CA19-9`: all 9 pairs `L3-01`, identity `resolved_as_non_protein_antigen`
- the retrieval table contains no `linkage_class`
- every retrieval candidate carries `linkage_validated=false` and
  `may_support_lock_03=false`
- all three evidence-ref groups empty
- no RETAIN, no EXCLUDE
- every pair HOLD
- `may_advance_to_level_02=false`
- EVGAP-02 not lifted

## Scope of approval, as stated by the reviewer

> 接受 v0.2.0 契约修复，以及 revision 3 作为 L-RETRIEVAL 层产物。

## Explicitly outside the approval, as stated by the reviewer

> * 接受任何 CRC linkage assertion；
> * 解除 EVGAP-02；
> * 生成正式 Level 01 accepted pool；
> * 推进 Level 02。

## Review history

- **Round 1 — `REQUEST_CHANGES`.** The run registered search hits as linkage
  evidence: all 7,067 rows carried `evidence_direction=unknown` yet produced 168
  RETAIN and 9 EXCLUDE. Root cause was in the contract, which required the column
  but never required it to be resolved, and left `linkage_class` unconstrained so
  it came from the query category. Answered by contract v0.2.0 (three layers,
  assertion requirements, identity resolution, per-endpoint admissibility,
  `VAL-L21`..`VAL-L28`) and by downgrading the run to an `L-RETRIEVAL` product.
- **Round 2 — `REQUEST_CHANGES`.** Revision 2 assigned `CA19-9` to `L3-00`
  although the contract declares it `resolved_as_non_protein_antigen`, a status
  `search_complete_definition` accepts. Answered by keying `L3-00` on
  `resolution_status` rather than table membership, moving `CA19-9` to `L3-01`,
  and adding `non_protein_antigen_search_requirements` with `VAL-L29`.
- **Round 3 — `REQUEST_CHANGES`.** The actual review package had not been
  supplied. Answered by freezing all semantics and shipping revision 3 with an
  in-package `verify_package.py`.
- **Round 4 — `APPROVE`.** Recorded above.

## Consequences

`EVGAP-02` remains **unlifted**. `ADC_POOL_LEVEL_01_ACCEPTED` does not hold.
The `L-ASSERTION` layer has not run, and `GAP-P07` (four targets whose identity
needs adjudicating) is registered but not fixed.
