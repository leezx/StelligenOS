# Handoff：ADCdb–Atlas–ADC AIDD Pipeline 设计

## 任务信息

- 任务编号：`task_20260821`
- 分支：`task_20260821_adcdb-atlas-adc-aidd-design`
- 基线：`origin/main@2eeb298`
- PR：https://github.com/leezx/StelligenOS/pull/84
- Commit：`3d3d6c5`、`a66c3d2`、`5ac8595`
- 时间：`2026-08-21 12:30 EDT`
- 状态：`ROUND_1_REQUEST_CHANGES_FIXED_PENDING_REVIEW`

## 任务目标

将人类负责人给定的 Small Biotech 路线写成一条可分阶段执行的 pipeline：从 MSS/pMMR refractory mCRC patient territory 出发，以 ADCdb 的已去风险 target universe 为先验，经 crowding/IP triage、CRC Atlas indication-transfer validation、T0–T12 Gate、Program Commitment、new-epitope AIDD、成熟 ADC platform 组装和逐级验证，最终形成 ADC hit 的 `GO/ITERATE/STOP` 决策包。

## 本次改动

- 新增 `docs/protocols/ADCdb_Atlas_ADC_AIDD_design.md`。
- 固定 100% 终点、10 个 Stage、统一状态机、单一外部结果根目录和 Stage 间承重接口。
- 为每个 Stage 定义输入、输出、放行条件、STOP/BLOCK 和禁止结论。
- 明确区分 target crowding、target/antibody/epitope IP whitespace 与 linker-payload/conjugation FTO。
- 明确 ADCdb 先例不能替代 CRC Atlas、internalization、Gate、construct QC 或实验验证。
- 新增量化 progress table，并区分工程、科学和实验/运营就绪度。
- 更新 `LINKS.md` 导航和 `logs/worklog.md`。

## 100% 终点与当前进度

100% 定义：完成一次可复现、可审计的外部运行，从 patient territory lock 到至少一个组装后的 ADC hit，并形成经人类批准的 `GO`、`ITERATE` 或 `STOP` 决策包；不等于临床候选物或临床成功。

| Workstream | 权重 | 当前状态 | Blocker | 下一里程碑 |
|---|---:|---|---|---|
| Pipeline 设计与治理 | 10% | draft complete，8/10 | ChatGPT 尚未 `APPROVE` | 本 PR 审核并合并 |
| Source admission 与快照 | 10% | 0/10 | `SRCADM-02` ADCdb 未准入 | Stage 0 contract PR |
| Refractory territory lock | 10% | 0/10 | 尚未固化为本 pipeline 输出 | Stage 1 |
| Target prior + crowding/IP | 15% | 0/15 | 依赖 Stage 0/1 | Stage 2/3 |
| Atlas transfer + T-chain | 20% | 0/20 | 依赖 dataset admission/analysis plan | Stage 4/5 |
| Epitope + AIDD binder | 15% | 0/15 | 依赖 Program Commitment/工具平台 | Stage 6/7 |
| ADC assembly | 10% | 0/10 | 依赖 binder 实验和 ADC 平台 | Stage 8 |
| Progressive validation | 10% | 0/10 | 依赖 wet-lab/CRO | Stage 9 |

当前总体进度：`0% → 8% (+8%)`。工程/基础设施 8%；科学就绪度 0%；实验/运营就绪度 0%。

## 已核实的现有基础设施

- 已有 `ADC_competitive_landscape_reference@0.1.0`、`ADC_epitope_realizability_reference@0.1.0` 和 ADC patent reference，可作为未来 Stage 的候选输入来源。
- 已有 T0–T12、P0–P15、C0–C15 Gate topology。
- 已有 `target_safety_therapeutic_window_prescreen`、`epitope_conditioned_de_novo_antibody_discovery`、`antibody_binder_asset_engineering` 和 `biotech_asset_due_diligence` 软件模块。
- 这些资源“已存在”不等于已为本 pipeline 准入、已运行或已形成科学结论。

## 当前阻断

- `ADCdb` 在既有治理记录中仍是 `SRCADM-02` 待准入。本设计不能解除它。
- 尚未把人类给定的 MSS/pMMR refractory mCRC 约束固化为本 pipeline 的版本化 ClinicalHypothesis 输出。
- 尚未落实 AIDD 外部工具执行、ADC platform、CRO、专利律师或 wet-lab 资源。

## 明确未改动和未执行

- 未修改 45-Gate topology、lifecycle、core objects、contracts 或 GenModule 代码。
- 未读取 ADCdb 内容产生新结果，未执行 Atlas、Gate、ranking、AIDD 或 ADC assembly。
- 未生成 target、epitope、antibody sequence、structure、linker-payload 或 ADC hit。
- 未下载数据，未新增 cache、result、database、model weight 或 runtime instance。
- 未暂存或修改主工作区中的用户未跟踪文件。

## 验证与审核

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/ -q -p no:cacheprovider`：`555 passed, 4019 subtests passed`。
- `bash scripts/verify_repository_boundary.sh`：通过。
- `git diff --check`：通过。
- 自检修正：将泛化的 T12 `ADVANCE/REJECT` 表述改为冻结的 `PROVISIONAL_ADVANCE`、`EXPLORATION`、`HOLD`、`FAIL`。
- 创建 PR 后，沿用本项目指定的同一 ChatGPT 网页审核对话。
- Round 1：在聊天框 `+` 中显式选择 GitHub 来源，ChatGPT 直接核对 PR #84 HEAD `a66c3d2`、4 个 changed files、aggregate diff 和 CI run #109，结论为 `REQUEST_CHANGES`。
- 唯一阻断：Stage 6->7 未显式消费 `SponsorFitAssessment`，且未把 non-asset-directed commitment 固定为 `BLOCKED_NO_COMMITMENT`。
- 修复：补齐 `SponsorFitAssessment@0.1.0 -> ProgramCommitmentReview@0.2.0 -> ValueInflectionPlan@0.1.0 -> human authorization -> asset-directed route` 承重链；只有 `SELF_DEVELOP`、`CO_DEVELOP`、`PARTNER_NOW` 且状态为 `EXTERNAL_HANDOFF_REQUIRED` 才能进入 Stage 7。
- 完整审核记录：`logs/chatgpt-review-2026-08-21-adcdb-atlas-aidd-design-pr84.md`。
- 只有明确 `APPROVE` 并合并后，设计里程碑才由 8% 升至 10%，才允许另建 Stage 0 contract PR。

## 下一步

1. 重新运行全量测试、repository boundary 和 `git diff --check`。
2. 将最小修复推送到同一 PR #84，并在同一 ChatGPT 对话复审最终 HEAD。
3. 明确 `APPROVE` 并合并后，再开始 Stage 0 ADCdb source-admission contract；本 PR 不授权真实运行。

## 数据边界声明

本仓库只保存设计、架构、代码和小型治理文本；所有未来输入、分析、模型输出、候选和实验结果必须保存在 `${BIOWORKSPACE_ROOT}/DATA/...` 的外部单一运行根目录。
