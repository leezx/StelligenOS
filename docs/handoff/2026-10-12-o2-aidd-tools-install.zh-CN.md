# O2 AIDD 工具安装契约交接备忘

## 任务信息

- 任务编号：`task_20261012_o2_aidd_tools_install`
- 分支：`task_20261012_o2_aidd_tools_install`
- PR：https://github.com/leezx/StelligenOS/pull/139
- Contract commit：`e7a2342`
- 时间：`2026-10-12 09:22 EDT`

## 当前 Phase 目标

为 O2 上 BoltzGen、Chai-1、Boltz-2 建立可审计的安装与 GPU 冒烟验收契约；只读核查 Chai-2/Chai-3 是否存在官方公开可安装版本。本 Phase 不运行真实靶点、不进行生产设计，也不把任何模型权重、缓存或结果写入 StelligenOS。

## 已发生事实

- 复用了既有 O2 SSH 会话，没有创建第二个 SSH 连接。
- BoltzGen 已安装到 `/home/zhl595/software/BoltzGen`，固定 commit `a07fea1153111ef453aaea7a15697ee05de9291f`，独立 Python 3.12 环境为 `.venv`，包版本 `0.3.2`。
- `boltzgen --version`、`--help`、Python import 和官方 `boltzgen check example/vanilla_protein/1g13prot.yaml` 通过；预检生成的 `1g13prot.cif` 已删除，源仓库恢复 clean。
- 核心模型缓存位于 `/home/zhl595/software/boltzgen_cache/models`，约 `7.9 GiB`；5 个主要 blob 的 SHA-256 已计算并与 Hugging Face `.refs` 内容哈希一致。
- BoltzGen 环境约 `7.3 GiB`。O2 home 当前为 `89.52/100 GiB`，因此没有下载约 `33 GiB` 的 ESMFold2 扩展。
- GPU canary 尚未执行。登录节点上 `torch 2.14.1+cu130`、`cuequivariance 0.12.0` 可导入；`cuda_available=False` 和缺少 `libcuda.so.1` 是登录节点无 GPU 的预期现象，必须在计算节点复核。

## 官方可用性核查

- Chai-1：官方 `chaidiscovery/chai-lab` 公开，README 指定 PyPI `chai_lab==0.6.1`；Linux、Python `>=3.10`、CUDA+bfloat16，推荐 L40S 48GB 或更大 GPU。计划安装独立环境并以 `CHAI_DOWNLOADS_DIR` 指向外部共享缓存。
- Boltz-2：官方 `jwohlwend/boltz` 公开，当前 package `2.2.1`，Python `>=3.10,<3.13`；官方建议 `pip install boltz[cuda] -U`，默认推理使用最新 Boltz-2。
- Chai-2 / Chai-3：截至本次核查，Chai Discovery 官方 GitHub 组织只有公开的 `chai-lab`（Chai-1）和非模型仓库，没有找到官方公开、可本地安装的 Chai-2 或 Chai-3。因此只记录“当前不可安装”，不安装同名第三方实现。

## 审核后计划

1. 先完成 BoltzGen 单作业 L40S GPU canary；不运行真实靶点。
2. 在不修改 Germinal/BoltzGen 既有环境的前提下安装 Chai-1 独立环境；复用已有 Chai 权重（如内容哈希一致）或在 quota 允许时建立单一共享缓存。
3. 安装 Boltz-2 独立环境；若 BoltzGen 缓存中的 Boltz-2 权重与官方 Boltz-2 内容一致，则复用/链接而不复制。
4. 每个工具依次做 import、CLI、权重完整性和一个 L40S 非生产 canary；始终只允许一个 GPU 作业。
5. 任何时刻预计 home 剩余空间低于 `5 GiB` 即停止，不用删除用户文件换空间。

## 验证与风险

- 安装契约：`manifests/o2_aidd_tools_install_20261012.yaml`
- 尚待验证：BoltzGen GPU；Chai-1/Boltz-2 package、权重及 GPU。
- 主要风险：home 配额只剩约 `10.48 GiB`；Chai-1 和 Boltz-2 的完整独立权重可能无法同时落盘。优先去重，不能保证在现有 quota 下完成全部模型下载。
- 流程偏差：BoltzGen 安装在发现本仓库全局 PR 门禁前已经开始。该偏差已如实留痕；没有执行生产设计。其余外部安装暂停到本 PR 获得明确 `APPROVE`。

## 明确未改动

- 未修改 StelligenOS 架构契约、runtime、schema 或代码。
- 未把 O2 模型、环境、缓存、输入、输出或大型文件复制进仓库。
- 未修改或删除 O2 上既有 Germinal、BindCraft2、RFantibody 环境。
- 未把 Chai-2/Chai-3 的第三方同名仓库当作官方版本安装。

## 数据边界声明

本 PR 只保存安装契约、外部路径、版本、容量和验收摘要。所有软件环境、模型缓存与测试输出均保存在 O2 的仓库外工作区。

## 下一步与门禁

- PR #139 已提交并指向 `main`，等待 ChatGPT 审核。
- ChatGPT 必须对当前 PR 明确给出 `APPROVE` 后，才执行 Chai-1/Boltz-2 安装和 GPU canary。
- `APPROVE_WITH_NONBLOCKING_COMMENTS` 不视为放行。
