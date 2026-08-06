# StelligenOS

StelligenOS 是一个 biotechnology asset operating system 的实现仓库。

这个仓库只保存操作系统的一种实现、架构契约、运行 Prompt、脚本、代码和少量必要说明。
它不是操作系统本体，也不是数据库。

## 仓库边界

- 允许放入：架构文档、Prompt、Schema、脚本、代码、参考文档，以及少量受控示例材料。
- 允许的示例材料包括：reference examples、toy examples、report templates、demo assets、golden test cases。
- 禁止放入：large datasets、raw sequencing、intermediate files、caches、outputs、temporary artifacts、data-bearing working files。
- 所有数据和数据处理必须放在仓库外部的工作区。

## 本地运行验证

需要 Python 3.11 或更新版本（`src/lifecycle/state_machine.py` 使用 `enum.StrEnum`）。

```bash
python3 -m pip install -r requirements.txt

# 单元测试。PYTHONDONTWRITEBYTECODE 是必须的：
# __pycache__ 会被 boundary check 判为运行产物。
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'

bash tests/test_git_sync.sh            # 需要 rg（ripgrep）
bash scripts/verify_repository_boundary.sh
git diff --check
```

依赖只有 `PyYAML`。`genmodules/` 下 pipeline 代码引用的 `dagster`、`anarci`、`abnumber`、
`biopython`、`ImmuneBuilder` **不是本仓库的依赖**，属于外部受控运行环境；原因见
`requirements.txt` 注释。

`.github/workflows/ci.yml` 在 Python 3.11 与 3.12 上独立复核以上全部检查。

## 当前阶段

- Phase 0 已完成
- Phase 0.5 已完成
- Phase 1 已完成并合并
- Phase 2 已建立核心对象、状态机和外部 Knowledge Ledger 边界并合并
- Phase 3 已建立 AssetGenOS Gate 合同边界并合并
- Phase 4 已建立 Opportunity Generation 外部能力合同并合并
- Phase 5 已建立两条 Binder/ADC 生成路线的外部合同并合并
- Phase 6 已建立 IP/FTO、Due Diligence 和 Portfolio 外部合同并合并
- Phase 7 已建立端到端闭环和 TWEAKR 外部示范引用合同并合并
- Phase 8 已冻结架构并建立发布与后续开发规范
- 当前架构说明审核基线：`STELLIGENOS-ARCH-2026.08.06-v3-draft`
- 当前 `main` 已有 CRC ADC Pool Level 01 Preview，但尚未形成 Accepted pool

## 关键入口

- `architecture.md`
- `docs/architecture/contract.zh-CN.md`
- `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`
- `docs/architecture/versions/README.md`
- `extensions/README.md`
- `extensions/BACKLOG.zh-CN.md`
- `docs/architecture/capabilities.zh-CN.md`
- `docs/architecture/lifecycle.zh-CN.md`
- `docs/architecture/legacy_inventory.zh-CN.md`
- `prompts/system/STELLIGENOS_MIGRATION_MASTER_PROMPT.zh-CN.md`
- `docs/phases/PHASE_0_REPORT.zh-CN.md`
- `docs/phases/PHASE_0_5_REPORT.zh-CN.md`
- `logs/worklog.md`
- `ChatGPT-Codex-talk.md`
- `AGENTS.md`
- `LINKS.md`
- `scripts/verify_repository_boundary.sh`
- `scripts/git_sync.sh`
- `requirements.txt`
- `.github/workflows/ci.yml`
- `src/README.md`
- `genmodules/README.md`
- `docs/phases/PHASE_1_REPORT.zh-CN.md`
- `docs/phases/PHASE_2_REPORT.zh-CN.md`
- `docs/phases/PHASE_3_REPORT.zh-CN.md`
- `docs/phases/PHASE_4_REPORT.zh-CN.md`
- `docs/phases/PHASE_5_REPORT.zh-CN.md`
- `docs/phases/PHASE_6_REPORT.zh-CN.md`
- `docs/phases/PHASE_7_REPORT.zh-CN.md`
- `docs/phases/PHASE_8_REPORT.zh-CN.md`
