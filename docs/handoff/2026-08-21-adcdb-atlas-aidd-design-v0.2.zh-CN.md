# Handoff：ADCdb-Atlas-ADC AIDD Design v0.2

## 任务信息

- 任务编号：`task_20260821`
- 分支：`task_20260821_adcdb-aidd-design-v0.2`
- 基线：`origin/main@5b2fa3a`
- 文档：`docs/protocols/ADCdb_Atlas_ADC_AIDD_design.md`
- 版本：`ADCdb_Atlas_ADC_AIDD_Design@0.2.0-draft`
- 时间：`2026-08-21 13:00 EDT`
- 状态：`DESIGN_REVISION_PENDING_CHATGPT_REVIEW_EXECUTION_NOT_AUTHORIZED`

## 人类提供的参考版本

读取了主工作区用户未跟踪文件 `pipelines/ADCdb_Atlas_ADC_AIDD_design.v0.1`。该文件作为设计输入原样保留，未暂存、未改名、未删除，也未被当成数据或 runtime source。

吸收的内容：

- 每个主要 artifact 的最小机器可读 schema；
- immutable provenance envelope；
- fatal-first、no-silent-fallback 和 failure taxonomy；
- AIDD、synthesis、conjugation、focused in-vivo 前的成本跃迁审批；
- ADC assembly 前独立的 experimental antibody-hit validation。

没有直接复制的内容：

- 旧版 S0-S10 编号，因为当前获批架构已经固定 Stage 0-9；
- `ADVANCE/KILL/GO` 等旧 decision authority，因为会与 T12 frozen dispositions、sponsor routing 和现有 Gate 语义冲突；
- 任何具体 target、sequence、数据或实验结果。

## 修复的承重接口

获批 0.1.0 的 Stage 8 要求实测 binding/epitope/internalization evidence，但 Stage 7 只产生 prediction/candidate 和实验计划，Stage 9 又在 assembly 后才验证 binder identity/delivery，形成循环依赖。

v0.2 修复为：

```text
Stage 7A epitope/AIDD design candidate
  -> human synthesis decision
Stage 7B experimental antibody-hit validation
  -> experimental ADC_GRADE_HIT + human conjugation authorization
Stage 8 physical ADC assembly + release QC
Stage 9 post-conjugation binding/delivery retention + progressive validation
```

预测仍不是 binder；只有实验证实的 `ADC_GRADE_HIT` 才能进入 Stage 8。Stage 9A/9B 只验证偶联后 construct 是否保留 binding、internalization 和 trafficking，不再倒置承担 pre-assembly binder qualification。

## 100% 终点与量化进度

100% 终点保持不变：一次版本化、可复现、可审计的外部运行，从 refractory patient territory lock 到至少一个 physically assembled ADC hit，并形成 human-approved `GO/ITERATE/STOP` 决策包；不等于 DevelopmentCandidate、IND 或临床成功。

| Workstream | 权重 | 当前状态 | Blocker | 下一里程碑 |
|---|---:|---|---|---|
| Pipeline 设计与治理 | 10% | 0.1.0 approved；0.2.0 draft，10/10 | v0.2 尚未 `APPROVE` | 设计修订 PR |
| Source admission 与快照 | 10% | 0/10 | `SRCADM-02` ADCdb 未准入 | Stage 0 contract PR |
| Refractory territory lock | 10% | 0/10 | 尚无本 pipeline 输出 | Stage 1 |
| Target prior + crowding/IP | 15% | 0/15 | 依赖 Stage 0/1 | Stage 2/3 |
| Atlas transfer + T-chain | 20% | 0/20 | 依赖 dataset admission/analysis plan | Stage 4/5 |
| Epitope + AIDD binder | 15% | 0/15 | 依赖 commitment、AIDD 与实验平台 | Stage 6/7 |
| ADC assembly | 10% | 0/10 | 依赖 experimental ADC-grade binder | Stage 8 |
| Progressive validation | 10% | 0/10 | 依赖 wet-lab/CRO | Stage 9 |

当前总体进度：`10% -> 10% (+0%)`。工程/设计治理 10%；科学就绪度 0%；实验/运营就绪度 0%。本次修订只提高设计完整性，不增加科学或运行完成度。

## 边界与验证计划

- 未修改 contracts、Gate、lifecycle、core objects 或 GenModule 代码。
- 未执行 ADCdb、Atlas、Gate、AIDD、synthesis、ADC assembly 或实验。
- 未下载或生成数据、cache、result、database、model weights、sequence 或 structure。
- 所有 future artifacts 仍必须写入 `${BIOWORKSPACE_ROOT}/DATA/.../<pipeline_run_id>/` 单一根目录。
- 自检修正：schema appendix 改为严格复用 Stage 3/4 已声明的 `target_crowding_matrix.tsv`、`target_ip_triage.tsv`、`target_route_decisions.tsv` 和 `target_atlas_evidence.tsv`，避免产生第二套 artifact authority。
- 自检修正：Stage 8 明确输出 `manufactured_lot_manifest.json`，并把缺少 Stage 7B `ADC_GRADE_HIT` 写成硬阻断；Stage 9C 删除与 9A 重复的 binding-retention 输出。
- `555 passed, 4019 subtests passed`；repository boundary 通过；`git diff --check` 通过。
- 下一步新建 PR 并沿用 `ADC研发框架优化` ChatGPT 对话审核。

## 下一步

1. 完成 v0.2 文本自检和全量验证。
2. 推送独立 design-revision PR。
3. ChatGPT 明确 `APPROVE` 后才合并；本 PR 不授权 Stage 0。
4. 合并后才另建 Stage 0 source-admission contract PR。
