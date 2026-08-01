# 任务交接备忘：gate_model_rule 迁移

- 任务编号：`task_20260801_gate-model-rule`
- 目标：将 AssetGenOS 的 `gate-model-rule` 主模块迁移为 StelligenOS 的纯软件合同边界。
- 当前状态：已完成第一轮修订，已通过本地验证，准备请求 ChatGPT 复审；PR #14 未合并。

## 已迁移

- `genmodules/gate_model_rule/core/contracts.py`
  - Gate Model Rule 稳定身份和 SemVer 校验。
  - 绑定 StelligenOS 冻结的 45 Gate 拓扑，未知 Gate 拒绝。
  - 历史规则描述、外部适用性评估和审核 bundle 合同。
  - 嵌套 `RuleReview` 与 YAML review 合同一致。
  - 锁定 `external_rule_model` implementation，并由测试验证 YAML/Python 一致性。
  - 强制证据、候选人、审阅人和理由均为外部引用。
- `genmodules/gate_model_rule/contracts/`
  - Gate Model Rule 合同。
  - Historical Rule Reference 合同。
- `genmodules/gate_model_rule/module.yaml`
  - 模块版本、Gate 系统引用、Model 生命周期引用和禁止自动执行政策。
- `genmodules/gate_model_rule/README.md`
  - 软件边界、外部输入输出和排除项说明。

## 明确未迁移

- AssetGenOS 的历史 ADC 规则 JSON/Markdown 和案例记录。
- 规则生成脚本、数据集构建脚本、数据库、缓存、模型权重和运行输出。
- 任何 Gate 执行器、自动评分、自动状态变化或 Profile 绑定逻辑。

## 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 33 passed
- `./scripts/verify_repository_boundary.sh`: passed
- `git diff --check`: passed

## 第一轮审核反馈

- ChatGPT 结论：`REQUEST_CHANGES`。
- 阻断项：YAML `review` 嵌套结构与 Python bundle 不一致；YAML
  `implementation` 未由 Python 表达且缺少一致性测试。
- 修订：已新增 `RuleReview`、implementation 字段和两个 YAML/Python 一致性测试。
- 原始记录：`logs/chatgpt-review-2026-08-01-gate-model-rule-round1.md`。

## 审核重点

1. 是否只迁移身份和合同，而未把历史规则实例或数据带入仓库。
2. 是否严格绑定当前 45 Gate 冻结拓扑。
3. 是否阻止自然语言规则自动改变分数、状态、阈值和 Profile。
4. 是否保持所有运行输入、证据、审核记录和输出位于外部工作区。
