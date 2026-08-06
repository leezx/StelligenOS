# ChatGPT Review Record: SRCADM-01 surfaceome source admission audit

- Review date: 2026-08-06 EDT
- Pull request: #63
- Approved head: `ae4dca32ff06f1a77e2a4e4dcc13dd6b16261eeb`
- Base branch: `main`
- Merge commit: `98a1698`
- Reviewer: ChatGPT
- Decision: `APPROVE` (Round 3)
- Relayed by: human lead
- Record type: **verbatim as relayed by the human lead.** The conclusions quoted
  below are reproduced as received, not paraphrased.
- GitHub review record: **none.** The reviewer attempted to write the formal
  review through the GitHub connector and received `403`. This file is therefore
  the only durable record of the decision.
- **This is the record `admission_record_ref` is to point at.**

## Reviewed artefact

External audit bundle, never in the repository:

- `gen_iet_srcadm_01_audit_bundle_20260806T000000Z.zip`
- ZIP SHA-256 `49d56c395661e7c71ba4caa60657126596cf4f784430ff462ab4512fdb0237b4`
- 2,666,041 bytes, 13 files plus one directory entry

## Reviewer's verification, as relayed

- ZIP SHA-256 matches the PR declaration:
  `49d56c395661e7c71ba4caa60657126596cf4f784430ff462ab4512fdb0237b4`
- 13 actual files, plus 1 directory entry
- `verify_audit.py` runs independently and passes
- `72/72 MATCH`
- builder, manifest, three complete processed tables and the target axis are all
  in the bundle
- raw manifest SHA-256 reconciles
- dataset version and snapshot agree
- the 19 sources and the licence manifest reconcile
- GOA and UniProt fall into the same `curated_knowledge` family
- `GUCY2C` still counts 1 family despite two same-origin sources
- HPA covered genes, the false state and the imaging mis-count reconcile across
  all three readings
- source-evidence duplicate keys: 6
- topology duplicate keys: 5
- the 11 affected genes do not intersect the 41-target axis
- consensus gene symbols are unique
- the 41 targets' family count agrees with their family list
- `CDH17`, `CEACAM5`, `GUCY2C` provenance is complete
- licence-ambiguous sources did not enter the permitted source-evidence scope
- the builder has no random process
- processed table hashes, byte counts and row counts all reconcile
- byte-level recomputation of the 19 raw files remains limited by `COND-03`;
  the reviewer noted this **was disclosed rather than concealed**

## Accepted conclusion, as stated by the reviewer

> ADC_surfaceome_reference@0.3.0 / 2026-07-29-quant-topology-mm 可以在四项条件下准入。

## The four conditions remain in force

| ID | Condition |
|---|---|
| `COND-01` | This snapshot only |
| `COND-02` | PR #59's field whitelist only |
| `COND-03` | Rests on the archived raw snapshot, not on upstream reproducibility |
| `COND-04` | Re-audit if the target axis grows or duplicate keys reach the criteria |

## What this approval does not do, as stated by the reviewer

> * 填写 admission_record_ref；
> * 授权 EVGAP-01 extraction；
> * 解除 EVGAP-01；
> * 执行 Level 01。

## Next step, as stated by the reviewer

> 下一步应是一个极小的 admission binding PR，然后再执行 EVGAP-01 extraction。

## Review history

- **Round 1 — `REQUEST_CHANGES`.** The audit's core facts all came from files
  outside the repository, and the in-repo tests only proved the audit document
  was internally consistent. Answered by shipping a recomputable audit bundle.
- **Round 2 — `REQUEST_CHANGES`.** The actual bundle had not been supplied, and
  the verifier had to recompute rather than read pre-written verdicts. Answered
  by shipping the package, moving the claims into `audit_expected.json`, adding
  `license_manifest.json`, and extending the recomputation to processed-table
  digests and per-source licence checks — 48 checks became 72, with none removed.
- **Round 3 — `APPROVE`.** Recorded above.

## Note recorded during Round 2

Recomputation exposed an ambiguity in the audit's own wording. "11,334 genes with
an HPA row but `hpa_plasma_membrane=false`" is correct — HPA covers 13,597 genes
and 11,334 of them are false — but 18,534 consensus rows carry that value, most
because HPA never covered the gene. The phrase "with an HPA row" carried the
whole distinction. All three figures are now reported. Under either reading zero
genes wrongly credit the imaging family, so `AUD-05` stands unchanged.
