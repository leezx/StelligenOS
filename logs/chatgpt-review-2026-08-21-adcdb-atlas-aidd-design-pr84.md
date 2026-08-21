# ChatGPT Review Record: ADCdb-Atlas-ADC AIDD Design PR #84

- Review date: 2026-08-21 EDT
- Pull request: https://github.com/leezx/StelligenOS/pull/84
- Round 1 reviewed head: `a66c3d2296af8c60551b531e406586462d6ca5dc`
- Round 2 approved head: `00f3053894c32ee759777aa49ee458a05e3a3666`
- Base: `main@2eeb2985`
- Merge commit: `c0ceae8052a8e2385a6453a74415d50249a0e04e`
- Reviewer: ChatGPT via the Chrome web conversation `ADC研发框架优化`
- GitHub source: explicitly selected in the ChatGPT composer
- Decision history: Round 1 `REQUEST_CHANGES`; Round 2 `APPROVE`
- Record type: `direct_verbatim_review`
- Execution authorization: none

## Reviewer verdict

> REQUEST_CHANGES

The reviewer verified that PR #84 was open, non-draft and mergeable; it was two
commits ahead and zero behind its base. The aggregate diff contained only
`LINKS.md`, the design document, the task handoff and the worklog. No functional
code or data file was present. CI run #109 succeeded on the reviewed head,
including Python 3.11 and 3.12 unit tests, git-sync behavior, repository-boundary,
no-bytecode and unchanged-worktree checks. The reported `555 passed, 4019
subtests passed` matched the handoff and worklog.

## Blocking finding, verbatim

> 整体设计质量已经很高，11 个检查项里绝大多数通过。但有一个当前设计层的真实阻断：Stage 5 -> Stage 6 -> Stage 7 的放行语义还没有完全对齐当前 frozen architecture。
>
> Stage 7 的放行条件只写了“human-approved Program Commitment + ValueInflectionPlan”，没有显式要求当前架构中已经冻结并绑定到 `ProgramCommitmentReview@0.2.0` 的 `SponsorFitAssessment`，也没有明确要求只有 asset-directed commitment outcomes 才能继续。
>
> 当前 main 上 `ProgramCommitmentReview` 已经是 `@0.2.0`，并且 `sponsor_fit_assessment_ref` 是无默认值必填 external ref。更重要的是，冻结语义明确规定：`MONITOR`、`DATA_PACKAGE_ONLY`、`STOP_FOR_SPONSOR` 必须是 `BLOCKED_NO_COMMITMENT`；而 `SELF_DEVELOP`、`CO_DEVELOP`、`PARTNER_NOW` 才要求 `EXTERNAL_HANDOFF_REQUIRED`。
>
> 这不是未来实现细节，而是当前 pipeline 的承重接口。如果设计按现在文字冻结，Stage 0-9 contract PR 后面很容易把一个合法但 non-asset-directed commitment 误当成 AIDD 授权。

## Required minimum correction, verbatim

> - Stage 6 输入补 `SponsorFitAssessment` ref，或明确 `ProgramCommitmentReview@0.2.0` 已强制消费它；
> - Stage 6 放行条件改成：只有 `SELF_DEVELOP`、`CO_DEVELOP`、`PARTNER_NOW`，且 `downstream_status = EXTERNAL_HANDOFF_REQUIRED`、human decision/authorization 已存在、ValueInflectionPlan 完整，才允许进入 Stage 7；
> - 明确 `MONITOR`、`DATA_PACKAGE_ONLY`、`STOP_FOR_SPONSOR` 必须停在 `BLOCKED_NO_COMMITMENT`，不得进入 epitope/AIDD；
> - Stage 16 的 Stage 6->7 接口同步写成上述条件，而不是泛化的 “human-approved Program Commitment”；
> - 最好把 `ProgramCommitmentReview@0.2.0` 版本写明，避免未来按旧 0.1.0 语义实现。

## Checks that passed

The reviewer explicitly accepted the following parts of the reviewed design:

- the 100% endpoint and the current 8% design-only checkpoint were honest;
- scientific and experimental/operational readiness remained 0%;
- MSS/pMMR refractory mCRC was the CRC pilot territory, while other cancers
  must define their own disease-specific refractory territory;
- Stage 0-9 each had inputs, outputs, release, STOP/BLOCK and prohibited claims;
- the contract-PR, explicit-APPROVE, external-run, result-PR, APPROVE state
  machine did not treat `APPROVE_WITH_NONBLOCKING_COMMENTS` as authorization;
- `SRCADM-02` remained the ADCdb source-admission blocker;
- crowding, target/antibody/epitope IP and linker-payload/conjugation FTO were
  separated;
- ADCdb precedent remained a prior and did not auto-pass indication transfer,
  accessibility, internalization, T7/T9/T11, safety or therapeutic window;
- the T12 dispositions matched the frozen values;
- AIDD output remained prediction/candidate evidence;
- Stage 8 required a real manufactured lot and release QC;
- Stage 9 required progressive validation, controls, reproducibility and a
  human `GO/ITERATE/STOP` decision;
- the external DATA single-root boundary and design-only repository scope were
  preserved.

## Non-blocking observations

- The 8% label could be called design/governance readiness rather than
  engineering readiness, but the current explanation was not misleading.
- Stage 3 should eventually clarify whether its target-level sponsor routing
  reuses the existing SearchSpaceAdmission vocabulary or defines a separate
  authority. This belongs to the later Stage 3 contract PR and does not block
  this design PR.

## Approval boundary

The reviewer stated that a future `APPROVE` would authorize only merging the
design architecture and opening a separate Stage 0 contract PR. It would not
authorize ADCdb retrieval, Atlas analysis, target ranking, Gate execution,
AIDD, ADC manufacture, CRO work or any external run.

## Round 2 final review

The same ChatGPT conversation re-reviewed the GitHub PR at exact head
`00f3053894c32ee759777aa49ee458a05e3a3666` after CI run #110 succeeded.
The reviewer restricted the re-review to the Round 1 blocker, the Stage 16
interface, the direct review record, handoff/worklog and current CI.

> APPROVE

The reviewer confirmed that:

- `SponsorFitAssessment@0.1.0` is now an explicit external input and
  `ProgramCommitmentReview@0.2.0` must consume its non-default
  `sponsor_fit_assessment_ref`;
- `SELF_DEVELOP`, `CO_DEVELOP` and `PARTNER_NOW` map to
  `EXTERNAL_HANDOFF_REQUIRED`;
- `MONITOR`, `DATA_PACKAGE_ONLY` and `STOP_FOR_SPONSOR` map to
  `BLOCKED_NO_COMMITMENT` and cannot enter epitope/AIDD;
- Stage 7 requires an asset-directed outcome, human decision/authorization,
  complete ValueInflectionPlan, non-empty stop conditions and explicit
  AIDD/platform capability sources;
- Stage 7 inputs and the Stage 16 interface carry the same conditions;
- the Round 1 review record, handoff and worklog accurately preserved the
  blocker and did not expand execution authorization;
- the final aggregate diff contained five text/governance files and no code,
  contract, data, cache, result, model weight or runtime instance;
- Python 3.11 and 3.12 CI checks passed.

> 上一轮唯一 blocker 已完整修复，没有引入新的范围扩张。
>
> PR #84 的 design architecture 可以合并；合并后允许另开 Stage 0 source-admission contract PR。
>
> PR #84 可以合并。

The final approval explicitly did **not** authorize ADCdb retrieval or parsing,
Atlas analysis, target scoring/ranking, T0-T12 Gate execution, AIDD,
antibody/epitope generation, ADC assembly/manufacturing, CRO/wet-lab work, or
any external DATA run.
