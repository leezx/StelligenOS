# PR #146 Phase B2 Round 1 independent review

- Reviewer: existing ChatGPT Biotech ideas PR review conversation, <https://chatgpt.com/g/g-p-68c041b4df6881918a83a55e2dd7ac70-biotech-ideas/c/6adaebc8-4738-83ea-8a87-894771eda8d6>.
- Reviewed exact HEAD: `6f1679b048abb615c85b1287cfbf0b5216b00ba6`; base `6f91d8be0b6ae1db914e0e7a0d74757537760825`; [PR #146](https://github.com/leezx/StelligenOS/pull/146).
- Independent evidence: GitHub diff (15 files), frozen Phase B0 plan, TGT-07 v2 construction and GateSet contracts, and CI run `39952275926`: Python 3.11/3.12 each 2,049 tests `SUCCESS`, boundary and git-sync `PASS`.
- Verdict: L1 `REQUEST_CHANGES`, L2 `REQUEST_CHANGES`, overall `REQUEST_CHANGES`; four P1 blockers and two P2 findings. No merge, B3, activation or real data authorized.

| Finding | Severity | Reviewer finding | Minimum correction |
|---|---|---|---|
| B2-L1-01 | P1 | Input `evidence_regime=PUBLIC_ONLY` contradicts frozen v2 Instantiation `PUBLIC_PLUS_EXPERIMENTAL`. | Match canonical regime and test YAML parity; keep module source scope separate. |
| B2-L1-02 | P1 | Reused EP parity omits `provenance.retrieved_at` and factual `measurement`. | Check factual measurement/provenance and test drift with whole-round reject. |
| B2-L2-01 | P1 | COMPLETE flags plus unresolved public source can still yield `NEGATIVE/DIRECT`. | Distinguish truthful incomplete/blocked source from false completion; prevent negative without weakening independent positive DIRECT. |
| B2-L2-02 | P1 | TMDD negative lacks detection-limit qualification; free text/unit regex alone is insufficient. | Pin source-grounded limit, controlled concentration unit, measurement identity; insufficient evidence stays UNKNOWN, contradictions reject. |
| B2-L1-03 | P2 | Exceptions from injected ports can bypass `MachineAcceptanceRecord`. | Handle or document as external infrastructure failure, separate from scientific UNKNOWN. |
| B2-L2-03 | P2 | WEAK-only sources produce `INCONCLUSIVE/UNKNOWN` with no proposal refs. | Explain frozen v1 aggregation and preserve weak EPs on the human review surface; scientific ladder change needs separate contract review. |

Review was advisory in ChatGPT, not a formal GitHub review. Round 2 must verify the actual revised PR diff and CI before B2 can be accepted.
