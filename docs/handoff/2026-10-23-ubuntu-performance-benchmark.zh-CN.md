# Ubuntu miniPC 性能评估交接

## 目标

对负责人新装的 Ubuntu miniPC 做一次短时、可控的本机性能评估，并据此说明适合的任务级别。重点查看 CPU、内存、存储和 GPU 能力；性能数字只代表本机合成基准，不外推为应用 SLA。

## 执行范围

- 读取 CPU 型号/拓扑、内存与 swap、根盘和磁盘型号/空间、GPU/加速设备、系统负载与温度（若系统已有传感器工具）。
- 不安装软件、不升级软件、不改系统/网络/防火墙配置、不重启、不跑外网测速。
- CPU：用 Python 标准库 `hashlib.sha256` 反复处理固定的 1 MiB 字节块；worker 数依次为 1、2、4、8（不超过在线逻辑 CPU 数），每档 2 秒，记录所有 worker 完成的总 MiB/s。初始化/进程启动时间单独记录，不计入算法吞吐量。总 CPU 时间上限为 30 核秒。
- 内存：先读 `/proc/meminfo` 的 `MemAvailable` 和 swap 使用；仅在 `MemAvailable >= 4 GiB`、swap 未增长且负载正常时执行。申请大小为 `min(256 MiB, MemAvailable/16)`，最低 128 MiB；对 4 KiB 页逐页写入，再顺序读回校验，最多 5 遍或 5 秒即停止。记录有效触碰吞吐量，不将其称为裸 DRAM 带宽；前后比较 swap 与 OOM 计数，变化则停止。
- 磁盘：确认 `/tmp` 所在分区至少有 2 GiB 可用后，用 `dd` 以 4 MiB 块写入至多 256 MiB，并用 `oflag=direct,conv=fdatasync` 计时；随后尝试 `iflag=direct` 顺序读入 `/dev/null` 计时。若 direct I/O 不被文件系统支持则记录跳过，不把 page-cache 命中结果冒充物理盘速度；完成后删除临时文件。
- 运行中若 SSH 变慢、系统开始 swap、温度工具显示超过 85°C、磁盘空间低于门槛或出现错误，立即停止并清理临时文件。
- 结果只写入 PR 的脱敏摘要；不保存完整主机输出、账号、地址、证书或个人文件。

## 数据解释

基准测试用于比较 CPU 单线程与并行吞吐、可用内存触碰吞吐和本地直接 I/O；合成分数不等于具体应用性能。任务分级按可核对证据给出：当前盘点已知 8 个 CPU、14 GiB RAM、根盘 232.22 GiB，完成本轮后补 CPU 型号、实际可用盘、GPU/显存和基准结果。该资源级别支持常驻轻量服务、开发/自动化与少量并行任务；若未发现可用 GPU/显存，则本地模型只列为 CPU 上的小型量化推理实验，不承诺交互速度或并发。模型大小必须按具体量化格式、运行时、KV cache 和剩余内存核算；本次不推断参数量上限。训练大型模型、GPU 密集任务及大型模型高并发服务不列为适用任务。存储/I/O 只用于判断本地构建、缓存或数据扫描瓶颈，不代表网络存储性能。

## 审核与状态

- 独立任务分支：`task_20261023_ubuntu_performance_check`，从 `origin/main` 创建。独立 PR：[PR #149](https://github.com/leezx/StelligenOS/pull/149)，base `main`。
- 当前 PR 仅含本 handoff 和 `logs/worklog.md`；取得当前 exact HEAD 的 GPT/ChatGPT `APPROVE` 前不在目标主机运行基准。
- 首轮独立 GPT 审核对 HEAD `382dba92b931cfe8d4de2ccad39b4e21bc58920b` 给出 `REQUEST_CHANGES`：要求精确定义 workload、降低内存压力、建立硬件证据到任务分级的边界。当前修订仅回应这三项；正式 GitHub review event 因 connector 403 未创建。
- 此任务未获批之前不依赖、也不等待先前基线更新 PR #148；不会执行安装或配置变更。
- 用户提出该性能评估前，之前 SSH 会话停在 sudo 密码提示；已取消提示并正常退出 SSH。未输入或读取密码，未在主机执行升级、安装或基准命令。
- GitHub connector 创建 PR 时返回 `403 Resource not accessible by integration`；使用已认证 GitHub CLI 创建 PR #149 成功。PR 创建过程已记入 worklog。
- 后续外部运行完成后，将脱敏结果追加到本 handoff 与 worklog，并在同一 PR 复审。

## 验收标准

- 记录完整硬件/系统识别摘要与每项基准实际方法、时长、成绩、跳过项和停止条件。
- 有明确且有证据的适用任务分级、主要瓶颈和不适用场景。
- 无软件包、配置、网络或防火墙变更，临时文件已清理，PR 与 worklog 留痕完整。
