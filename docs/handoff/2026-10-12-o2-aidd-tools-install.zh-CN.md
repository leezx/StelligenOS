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

1. 每次创建环境或下载权重前，重新读取 quota，并分别估计环境、模型、包管理器/框架缓存、临时下载和解包的新增峰值；只有整个步骤峰值后仍剩至少 `5 GiB` 才能开始。无法估计或预计不足即停止，不先下载再观察。
2. 固定共享缓存：`/home/zhl595/software/aidd_shared_cache/{uv,pip,huggingface,torch,tmp}`。模型只有内容哈希一致才复用；不得为了腾空间删除或修改任何既有用户环境/文件，只能清理本任务创建且可重新下载的临时文件。
3. 先完成 BoltzGen 单作业 L40S 验收；不运行真实靶点。CUDA、tensor 与 compute-node import 通过只记为 `GPU_RUNTIME_PASS`；必须实际完成一次官方最小非生产模型运行，并记录 exit code、耗时和输出完整性，才记为 `MODEL_CANARY_PASS`。
4. 如果 15 分钟不足、权重缺失或空间门禁阻止下载，只记为 `MODEL_CANARY_PENDING`，不得声称模型已通过 GPU 验证或完整可用。
5. 在不修改 Germinal/BoltzGen 既有环境的前提下安装 Chai-1 独立环境；复用已有 Chai 权重（仅限内容哈希一致）或在 quota 允许时建立单一共享缓存。
6. 安装 Boltz-2 独立环境；若 BoltzGen 缓存中的 Boltz-2 权重与官方 Boltz-2 内容一致，则复用/链接而不复制。
7. 每个工具依次做 package/artifact、`GPU_RUNTIME_PASS` 和 `MODEL_CANARY_PASS` 验收；始终只允许一个 GPU 作业。

## 验证与风险

- 安装契约：`manifests/o2_aidd_tools_install_20261012.yaml`
- 尚待验证：BoltzGen GPU；Chai-1/Boltz-2 package、权重及 GPU。
- 主要风险：home 配额只剩约 `10.48 GiB`；Chai-1 和 Boltz-2 的完整独立权重可能无法同时落盘。优先去重，不能保证在现有 quota 下完成全部模型下载。
- 状态语义：package/artifact 通过可记“已安装”；`GPU_RUNTIME_PASS` 仅证明 CUDA runtime；只有 `MODEL_CANARY_PASS` 才能记“模型已在 GPU 上验证可用”。`MODEL_CANARY_PENDING` 不是通过。
- 流程偏差：BoltzGen 安装在发现本仓库全局 PR 门禁前已经开始。该偏差已如实留痕；没有执行生产设计。其余外部安装暂停到本 PR 获得明确 `APPROVE`。

## 明确未改动

- 未修改 StelligenOS 架构契约、runtime、schema 或代码。
- 未把 O2 模型、环境、缓存、输入、输出或大型文件复制进仓库。
- 未修改或删除 O2 上既有 Germinal、BindCraft2、RFantibody 环境。
- 未把 Chai-2/Chai-3 的第三方同名仓库当作官方版本安装。

## 数据边界声明

本 PR 只保存安装契约、外部路径、版本、容量和验收摘要。所有软件环境、模型缓存与测试输出均保存在 O2 的仓库外工作区。

## 下一步与门禁

- PR #139 round 1 为 `REQUEST_CHANGES`；空间峰值门禁和 GPU 状态语义两项阻断已在 commit `d411a32` 修正。
- Round 2 对 `d411a326ab698eef66f4b766485fa8d0a8c042e2` 明确给出 `APPROVE`，允许按契约执行有限安装与 canary。
- `2026-10-12 10:15 EDT` 按负责人明确确认，删除三个可重新下载缓存：`/home/zhl595/.cache/pip`（18 GiB）、`/home/zhl595/software/rfantibody_cache/uv`（6.6 GiB）、`/home/zhl595/software/boltzgen_cache/huggingface`（382 MiB）。三个路径均已确认不存在；RFantibody/BoltzGen 正式 `.venv` 和 BoltzGen 主模型缓存均确认存在。
- `owner_authorized_contract_deviation`：上述三个缓存目录并非本任务创建的临时文件；为执行删除而进行的新 Duo 登录也越过了 `d411a32` 将再次认证列为 stop condition 的限制。两类操作均由负责人在执行前另行明确授权。本记录是事后如实披露，不表示先前 ChatGPT `APPROVE` 已覆盖这些例外，也不修改原限制；后续再次发生例外须先取得对应门禁批准。
- 删除后的 `quota-v2` 尚未刷新，仍返回 10:12:26 的删除前快照 `97.74/100 GiB`。在获得时间戳晚于删除动作的新 quota 快照且峰值空间预检通过之前，不启动 Chai-1/Boltz-2 安装。
