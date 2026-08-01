# Phase 5 报告

## 1. 目标

建立两条 Binder/ADC 生成路线的最小软件合同：Existing-Binder Asset Engineering
和 Epitope-Conditioned de novo Antibody Discovery。只迁移路线身份、阶段目录和
外部运行边界，不迁移科学数据或生成实现。

## 2. 本次完成

- 固化两条路线 ID 和分别 14、15 个阶段的目录合同。
- 建立统一 Binder/ADC route request/result 外部引用接口。
- 明确 Existing-Binder 的计算质量与 ADC carrier phenotype 是两个不可相加的轴。
- 明确 de novo 路线的外部科学工具不得自动调用。
- 明确两条路线均不得写 Gate 分数、混合路线或自动推进生命周期。

## 3. 明确未做

- 未迁移序列、结构、观察、训练数据、模型权重、专利材料、案例或运行输出。
- 未迁移任何 GenModule 代码、Prompt、示例输入、虚拟环境或科学工具。
- 未实现 Binder 工程、de novo 设计、排序、Pareto 选择、ADC readiness 或报告生成。
- 未创建数据库、缓存、结果目录、候选记录或内部运行时。

## 4. 验证

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`：通过。
- `./scripts/verify_repository_boundary.sh`：通过。
- `git diff origin/main...HEAD --check`：通过。
- `git diff --check`：通过。

## 5. 结论

Phase 5 仅建立两条 Binder/ADC 生成路线的架构合同和外部端口。待 PR 经 ChatGPT
明确 `APPROVE` 后，才允许进入 Phase 6 IP/FTO、Due Diligence 和 Portfolio 能力迁移。
