# Handoff：Cancer Vaccine Indication–Neoantigen Portfolio Pipeline Phase 0

## 任务信息

- 任务编号：`task_20260821_cancer_vaccine_phase0`
- 分支：`task_20260821_cancer-vaccine-phase0`
- 基线：`origin/main@a8afcd4f50cf676189e268d1a8c0674972e5d4c6`
- PR：待创建
- Commit：待创建
- Design：`docs/protocols/Cancer_Vaccine_Indication_Neoantigen_Portfolio_design.md`
- Version：`Cancer_Vaccine_Indication_Neoantigen_Portfolio_Design@0.1.0-draft`
- Status：`DESIGN_REVIEW_REQUIRED_EXECUTION_NOT_AUTHORIZED`
- 指定审核对话：ChatGPT `Biotech ideas / moderna癌症疫苗三期`

## 项目背景

本项目在 StelligenOS 中新增一条与 ADCdb–Atlas–ADC AIDD 并列、科学 authority 独立的 cancer-vaccine pipeline：

- ADC 路线寻找适合 ADC 的 patient territory 与 target；
- cancer-vaccine 路线寻找主要免疫失败可被 vaccination 改变的 patient territory，并验证 patient-specific antigen portfolio selection。

Small-Biotech 切入点不是复制 Moderna 的 mRNA/LNP/CMC/clinical operations，也不是再写一个 HLA predictor，而是：

1. Vaccine-Responsive Territory discovery；
2. Clinical Neoantigen Truth Set；
3. blinded shadow trial；
4. high-information prospective immune validation；
5. fixed-platform portfolio comparison。

该背景已在 PR 创建前提交到指定 ChatGPT 对话；ChatGPT 已确认后续所有 PR 在同一对话审核。

## 本 PR 范围

只新增三个本任务文件：

1. Phase 0 pipeline design；
2. task-specific worklog；
3. 本 handoff。

设计定义：

- 唯一 Stage 0–9 critical path；
- Stage 4 `PRIMARY_VACCINE_TERRITORY` / 最多一个 backup / `NO_GO`；
- truth-set admission 与 leakage firewall；
- missing label、selection bias 与 claim boundary；
- blinded shadow trial 和 public baseline comparison；
- prospective presentation/T-cell/tumor-recognition 验证；
- fixed-platform POC；
- failure/unknown taxonomy、人类成本跃迁和 PR 放行顺序。

## 明确未做

- 未修改任何已有文件；
- 未修改 ADC design、contracts、Gate、RuleBook、lifecycle 或 core objects；
- 未写入共享 `logs/worklog.md`、README、LINKS 或根 HANDOFF；
- 未读取、下载、抽取或处理患者数据；
- 未建立 truth-set 实例、运行 pan-cancer ranking 或 neoantigen predictor；
- 未训练模型、解盲 outcome、设计 peptide/mRNA/LNP；
- 未执行实验、CRO、制造、动物或临床工作；
- 未形成任何 disease、territory、vaccine 或 clinical recommendation。

## 并行安全

另一个进程正在修改同一 GitHub 仓库。本任务：

- 使用独立 `/private/tmp/StelligenOS-cancer-vaccine-phase0` worktree；
- 从精确 `main@a8afcd4` 创建独立分支；
- 只新增本任务文件；
- 不依赖未合并分支或外部运行；
- push 前重新检查 remote main、changed-file overlap 与 PR diff；
- 不自动 rebase 会产生语义冲突的 concurrent changes。

## 100% 定义与当前进度

100% endpoint：从 pan-cancer territory universe 产生一个经人类批准、经 human truth set、盲法 shadow trial、prospective immune validation 和固定平台 POC 支持的 `VACCINE_PORTFOLIO_HIT` 决策包；不等于 Development Candidate、IND-ready 或临床成功。

| Workstream | 权重 | 当前状态 | blocker | 下一里程碑 |
|---|---:|---|---|---|
| Design/governance | 10% | 8/10，draft complete | PR/ChatGPT review pending | PR-0 APPROVE |
| Source admission + truth-set structure | 15% | 0/15 | sources/labels 未准入 | PR-A/PR-D contracts |
| Territory discovery + commit | 25% | 0/25 | universe 未运行 | PR-B/PR-C |
| Blinded shadow trial | 20% | 0/20 | truth set/preregistration 缺失 | PR-E/PR-F |
| Prospective immune validation | 20% | 0/20 | retrospective gate/实验授权缺失 | PR-G |
| Fixed-platform POC + hit decision | 10% | 0/10 | platform/CMC/实验未就绪 | PR-H/Stage 9 |

- Overall：`0% -> 8% (+8%)`
- Engineering/design-governance readiness：`8%`
- Scientific readiness：`0%`
- Truth-set readiness：`0%`
- Experimental/operational readiness：`0%`

## 验证

已通过：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/ -q -p no:cacheprovider
bash tests/test_git_sync.sh
bash scripts/verify_repository_boundary.sh
git diff --check
git status --short
```

- Unit tests：`555 passed, 4019 subtests passed`
- `test_git_sync.sh`：A–D passed
- repository boundary：passed
- `git diff --check`：passed
- changed-file audit：没有 modified tracked files；恰好三个 task-owned new files

## 下一步与放行边界

下一步是验证、显式暂存三个新文件、提交/推送、创建 PR，并在同一 ChatGPT 对话附加 PR、背景、HEAD、CI 与 new-file-only 清单进行审核。

在 ChatGPT 对当前 PR 明确 `APPROVE` 前，不得进入 PR-A、建立 source registry、下载数据、运行 territory discovery、建立 truth set 或执行任何后续 stage。
