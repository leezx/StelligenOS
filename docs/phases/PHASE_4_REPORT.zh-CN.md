# Phase 4 报告

## 1. 目标

建立 Opportunity Generation 模块的最小软件合同，明确其与外部知识、处理运行时
和下一生命周期阶段的边界，不在 StelligenOS 内生成或存储机会记录。

## 2. 本次完成

- 建立 Opportunity Generation request/result 外部引用合同。
- 建立外部 `OpportunityGenerationPort`，不提供生成器、调度器或持久化。
- 明确输入包括知识范围、靶点上下文、临床上下文、生成策略和运行上下文引用。
- 明确输出只返回外部 Opportunity、TargetHypothesis、Evidence 和 run 引用。
- 明确进入 Opportunity Validation 需要显式的人类或外部决策，不自动晋级。

## 3. 明确未做

- 未创建 Opportunity、TargetHypothesis 或 Evidence 实例。
- 未接入知识库、模型、Prompt、数据集、数据库、缓存、输出或运行目录。
- 未迁移任何历史 Opportunity Generation 实现或业务数据。
- 未实现候选生成、排序、去重、评分、证据抽取或生命周期推进。

## 4. 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：通过。
- `./scripts/verify_repository_boundary.sh`：通过。
- `git diff origin/main...HEAD --check`：通过。
- `git diff --check`：通过。

## 5. 结论

Phase 4 仅建立 Opportunity Generation 的软件接口和外部数据边界。待 PR 经
ChatGPT 明确 `APPROVE` 后，才允许进入 Phase 5 Binder/ADC 生成路线迁移。
