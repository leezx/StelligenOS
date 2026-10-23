# TGT-07 v2 Phase B2 交接

状态：**待本 PR 的 CI 与 ChatGPT L1/L2 审核；未激活、未运行真实数据。**

## 来源与变更

- 人类于 2026-10-23 指示“继续”，B1 [PR #145](https://github.com/leezx/StelligenOS/pull/145) 已在 08:10 EDT 合并（merge commit `6f91d8be0b6ae1db914e0e7a0d74757537760825`），作为 B2 的人工 L3 放行。
- 依据已批准的 `docs/architecture/TGT05_TGT07_V2_PHASE_B_EXECUTION_PLAN.zh-CN.md` 与 `src/contracts/gate_modules/tgt07_shedding_soluble_antigen_sink_liability_v2.yaml`，新增独立 `gate_modules/tgt07_shedding_soluble_antigen_sink_liability_v2/`。v1 源码与测试不改；v2 binding 仍为 `0.0.0`，Instantiation 仍 `HOLD`。
- v2 保留经验证的分型、完成度审计、单事件 EP、同/异暴露场景冲突、fatal review 框架；新增 program 与 intended construct 身份、TMDD 定量输入依据、assay unit/LoD 依据、完整来源 ID 核对、拒绝时零 EP 输出，以及逐场景和冲突双方 EP 的审阅表面。无网络、数据、canonical Assessment 或 Decision。

## 验证与门槛

- B2 合成测试 101 项通过；全库 `PYTHONDONTWRITEBYTECODE=1 /tmp/stelligenos-pr143-venv/bin/python -m unittest discover -s tests -q`：2,049 项通过。此前系统 Python 的 pytest 生成 `__pycache__` 导致 4 项仓库卫生测试失败，清理缓存后同一全量套件通过。
- 本 PR 仍需提交并等待 ChatGPT 对 exact HEAD 明确 `APPROVE`；之后仍需人工 L3 决定合并和进入 B3。B2 本身不授权外部数据运行。webReport 的采集/运行还需其独立 PR 与 Git remote。

## PR #146 首轮审核与定向修订

- 初版 HEAD `6f1679b048abb615c85b1287cfbf0b5216b00ba6`，CI run `39952275926` Python 3.11/3.12 各 2,049 tests SUCCESS。ChatGPT L1/L2/整体 `REQUEST_CHANGES`：4 项 P1、2 项 P2，详情见 `logs/chatgpt-review-2026-10-23-tgt07-phase-b2-round1.md`。
- 同一 PR 内定向修订：输入 `evidence_regime` 精确匹配冻结 v2 Instantiation；EP reuse 比对 factual measurement、`retrieved_at` 和 study context；已知公共来源未抓取而宣称 COMPLETE 为 hard reject，访问受阻的未解项阻止限定阴性但不抹掉独立 material DIRECT；TMDD 阴性补检测限数值/单位、analyte、同源依据和受控浓度单位。P2 说明弱 EP 仍留在 accepted run，port 异常属于外部运行器基础设施失败。
- 新合成反例及全量 CI 待确认；未合并、未进入 B3/激活/真实数据运行。
