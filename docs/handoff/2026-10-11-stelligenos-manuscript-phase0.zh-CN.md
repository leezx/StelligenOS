# Handoff：StelligenOS Manuscript Phase 0 —— 论文总纲与证据契约

## 任务信息

- 任务编号 / 分支：`task_20261011_stelligenos_manuscript_phase0`
- 基线：`main` / `origin/main` @ `1c8ba22`
- PR：[#140](https://github.com/leezx/StelligenOS/pull/140)，已获固定入口 `APPROVE`（0 阻断）。批准范围仅限 framing、PaperSpine intake、E0–E5 证据契约、论文初始结构与仓库边界适配；**不自动放行 Phase 1 research**
- Commit：待提交
- 时间：2026-10-11 17:18 EDT
- 当前门禁：Phase 0，等待 PR 审核；不得开始 PaperSpine research。

## 当前 Phase 目标

把 `manuscript/` 建立为 StelligenOS 的论文源文件与审计材料目录，完成 PaperSpine intake，冻结论文初始定位、证据边界和后续 Phase 路线。

## 本次改动

- 新增 `manuscript/README.md`，定义论文目录用途与 data-free 边界；
- 新增 `manuscript/MANUSCRIPT_CHARTER.zh-CN.md`，记录研究定位、允许/禁止主张、证据层级、暂定结构和 Phase 计划；
- 通过 PaperSpine intake 生成配置与进度文件，并因仓库禁止生成物而显式设置 `word_output: none`；
- 把 `manuscript` 加入 repository boundary 顶层允许清单；
- 在根 `README.md` 增加论文入口；
- 追加 `logs/worklog.md` 审计记录。

## 明确未改动

- 未执行外部文献检索，未生成 research stage 的任何占位文件；
- 未写 `confirmed_motivation.md` 或 `confirmed_contribution.md`；
- 未写论文正文、结果、引用、图表、PDF 或 DOCX；
- 未修改 StelligenOS 架构内核、Gate、Module、Schema 或 runtime；
- 未触碰任务开始前已有的未跟踪文件和目录。

## 工具异常与回退

- PaperSpine GUI launcher 因 AppleScript `-2741` 语法错误失败；
- terminal keyboard UI 因 `termios` 兼容性 `TypeError` 失败；
- 随后使用同一 `intake_wizard.py --no-interactive` 的官方参数接口写入等价配置。

## 验证

```text
已运行：PaperSpine progress_check.py --markdown --write
结果：Intake [DONE]；Next stage = research。

已运行：
- `progress_check.py paper_rewriting_output --gate intake`：PASS；
- `python3 -m json.tool manuscript/paper_rewriting_output/paper_spine_config.json`：PASS；
- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'`：1900 tests，OK；
- `git diff --check`：PASS；
- `bash scripts/verify_repository_boundary.sh`：预期 FAIL，仅报告任务前既有 7 项；`manuscript` 已不再报告为违规。
```

## 未决问题与风险

- 目标期刊待 research 后确定；
- PaperSpine 默认要求在输出目录生成 PDF/DOCX，与仓库禁止 outputs 冲突；本 Phase 已显式关闭仓库内 Word 输出。后续 PDF/DOCX 必须在仓库外构建，只提交源文件、外部路径、摘要与校验信息；
- 当前工作区有任务前既存的 7 个未跟踪边界违规项，不能纳入本 PR：`.DS_Store`、`Stelligen-Assets.xmind`、`pipelines/`、`STELLIGEN_CONSTRAINTS.md`、`CRC Patient Territory Map.png`、`AI_RESULT_ACCEPTANCE.md`、`.claude/scheduled_tasks.lock`。

## 下一步

1. 完成 Phase 0 验证、提交、推送并创建 PR；
2. 由 ChatGPT 审核当前 PR；
3. 只有明确 `APPROVE` 且负责人决定 merge 后，才能开始 Phase 1 research。

## 数据边界声明

本 Phase 没有新增数据、缓存、运行结果或 data-bearing working files。`manuscript/` 只保存论文源文件和小型审计文本；最终生成物留在仓库外部工作区。
