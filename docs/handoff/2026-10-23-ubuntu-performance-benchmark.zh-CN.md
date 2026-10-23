# Ubuntu miniPC 性能评估交接

## 目标

对负责人新装的 Ubuntu miniPC 做一次短时、可控的本机性能评估，并据此说明适合的任务级别。重点查看 CPU、内存、存储和 GPU 能力；性能数字只代表本机合成基准，不外推为应用 SLA。

## 执行范围

- 读取 CPU 型号/拓扑、内存与 swap、根盘和磁盘型号/空间、GPU/加速设备、系统负载与温度（若系统已有传感器工具）。
- 不安装软件、不升级软件、不改系统/网络/防火墙配置、不重启、不跑外网测速。
- CPU：Python 标准库构造固定块 `bytes(range(256)) * 4096`（恰好 1 MiB），用 `multiprocessing` 的 `spawn` 进程 worker 反复计算 `hashlib.sha256(block).digest()`。worker 数依次为 1、2、4、8，并过滤掉大于在线逻辑 CPU 数的档位；所有进程通过 barrier 统一开始，按 `time.monotonic()` 的共同 2 秒窗口计数。总吞吐量定义为 `所有 worker 的 hash 次数 × 1 MiB / 2 秒`；进程启动时间单独记为准备时间，不计入分数。目标机 8 CPU 时总 CPU 时间上限为 30 核秒。
- 内存：先读 `/proc/meminfo` 的 `MemAvailable` 和 swap 使用；仅在 `MemAvailable >= 4 GiB`、swap 未增长且负载正常时执行。申请大小为 `min(256 MiB, MemAvailable/16)`，最低 128 MiB；对 4 KiB 页逐页写入，再顺序读回校验，最多 5 遍或 5 秒即停止。记录“页读/写操作数/秒”，不将其称为裸 DRAM 带宽；前后比较 swap 与 OOM 计数，变化则停止。
- 磁盘：先以 `findmnt -T /tmp` 和 `findmnt -T /` 确认 `/tmp` 的挂载类型/来源；仅当 `/tmp` 与根目录是同一、可确认的持久块设备挂载（ext4、xfs 或 btrfs）时继续，tmpfs、overlay、来源不同或无法确认一律跳过物理盘测试并注明。再确认至少有 2 GiB 可用，用 `dd` 以 4 MiB 块从 `/dev/zero` 写入 64 块（256 MiB），用 `oflag=direct,conv=fdatasync` 计时；随后以 `iflag=direct` 顺序读入 `/dev/null` 计时。若 direct I/O 不被文件系统支持则记录跳过，不把 page-cache 命中结果冒充物理盘速度；完成后删除临时文件。
- 运行中若 SSH 变慢、系统开始 swap、温度工具显示超过 85°C、磁盘空间低于门槛或出现错误，立即停止并清理临时文件。
- 结果只写入 PR 的脱敏摘要；不保存完整主机输出、账号、地址、证书或个人文件。

## 数据解释

基准测试用于比较 CPU 单线程与并行吞吐、可用内存触碰吞吐和本地直接 I/O；合成分数不等于具体应用性能。任务分级按可核对证据给出：当前盘点已知 8 个 CPU、14 GiB RAM、根盘 232.22 GiB，完成本轮后补 CPU 型号、实际可用盘、GPU/显存和基准结果。该资源级别支持常驻轻量服务、开发/自动化与少量并行任务；若未发现可用 GPU/显存，则本地模型只列为 CPU 上的小型量化推理实验，不承诺交互速度或并发。模型大小必须按具体量化格式、运行时、KV cache 和剩余内存核算；本次不推断参数量上限。训练大型模型、GPU 密集任务及大型模型高并发服务不列为适用任务。存储/I/O 只用于判断本地构建、缓存或数据扫描瓶颈，不代表网络存储性能。

## 审核与状态

- 独立任务分支：`task_20261023_ubuntu_performance_check`，从 `origin/main` 创建。独立 PR：[PR #149](https://github.com/leezx/StelligenOS/pull/149)，base `main`。
- 当前 PR 仅含本 handoff 和 `logs/worklog.md`；取得当前 exact HEAD 的 GPT/ChatGPT `APPROVE` 前不在目标主机运行基准。
- 首轮独立 GPT 审核对 HEAD `382dba92b931cfe8d4de2ccad39b4e21bc58920b` 给出 `REQUEST_CHANGES`：要求精确定义 workload、降低内存压力、建立硬件证据到任务分级的边界。当前修订仅回应这三项；正式 GitHub review event 因 connector 403 未创建。
- Round 2 对 HEAD `c0eaea70c61b2b6bdfb16ea6debe6e376338488d` 给出 `REQUEST_CHANGES`，要求固定 CPU 字节块/进程/计时聚合规则，并确认 `/tmp` 是否根盘持久挂载。Round 3 对 HEAD `27b762d03ac399f1d336baeef6d7cc2ecd0d2525` 确认这两项已解决，但发现 PR 描述仍写 2 GiB，与 handoff 256 MiB 不一致。已按意见修正 PR 描述和留痕，等待最终 exact-head 复审。各轮 GitHub review API 均因 403 未产生平台 review event。
- 独立 GPT reviewer 已对 HEAD `5827a2a35aebca777f012c3137f65563484e970f` 给出 `APPROVE`：批准范围仅为 PR 描述列出的短时只读硬件盘点、CPU benchmark、最多 256 MiB 内存触碰测试及符合挂载条件时的临时 `/tmp` I/O 测试；不含安装、配置修改或重启。正式 GitHub review event 因 connector 403 未创建。该审核记录产生新 HEAD，执行前需再确认最终 HEAD。
- 此任务未获批之前不依赖、也不等待先前基线更新 PR #148；不会执行安装或配置变更。
- 用户提出该性能评估前，之前 SSH 会话停在 sudo 密码提示；已取消提示并正常退出 SSH。未输入或读取密码，未在主机执行升级、安装或基准命令。
- GitHub connector 创建 PR 时返回 `403 Resource not accessible by integration`；使用已认证 GitHub CLI 创建 PR #149 成功。PR 创建过程已记入 worklog。
- 统一内存上限：PR 描述与 handoff 均为最多 256 MiB，实际申请仍受 `MemAvailable/16` 限制。
- 主机测试已完成，结果如下；测试方法、停止条件和限制均与原批准范围一致：
  - CPU：Intel Core i3-N305，8 核/8 线程。SHA-256 固定 1 MiB 块聚合吞吐：1/2/4/8 worker 分别为 2,335.5/4,560.5/8,158.5/14,350 MiB/s；8 worker 相对单 worker 约 6.1 倍。该值只代表 SHA-256 合成负载。
  - 内存：触碰 256 MiB，完成 377 遍页写入/读回校验，5.01 秒内约 9.86 百万次 4 KiB 页读/写操作/秒；checksum 通过，swap 变化 0，OOM 计数变化 0。此值不是 DRAM 带宽。
  - GPU：发现 Intel UHD 集成显卡，DRI 节点可用；未发现独立 NVIDIA GPU/VRAM 证据。
  - 存储：NVMe 型号报告为 JUMPER 512G，根分区 ext4 233 GiB、运行后可用约 213 GiB。另检测到约 238.5 GiB USB 磁盘，未测试。`/tmp` 是 7.5 GiB tmpfs，与根块设备不同，故按方案跳过物理盘 I/O 测试。
  - 温度监控限制：初始 `thermal_zone` 读数为 27.8/43/50°C；基准脚本的实时温度扫描因 sysfs 链接未取到数据，CPU 各档仍按短时负载完成。结束后的只读读数为 27.8/41/42°C，未见超过 85°C，但无法确认测试峰值温度。未重复施加负载。
  - 结束核查：未发现遗留临时基准文件；内存约 14.8 GB 可用、4 GiB swap 全部空闲；根分区仍约 213 GiB 可用。无软件包、配置或网络变更，无重启。
- 能力判断：适合作为常驻轻量服务/个人助手编排节点、浏览器自动化、脚本和轻量开发机；可以做少量并行 CPU 工作。CPU-only 小型量化模型可做实验，但速度与并发必须针对具体模型实测；不适合作为大型模型训练、高并发模型服务或 GPU 计算主机。benchmark 不测浏览器/邮件软件，也不构成其应用性能承诺。
- 后续外部运行完成后，将脱敏结果追加到本 handoff 与 worklog，并在同一 PR 复审。

## 验收标准

- 记录完整硬件/系统识别摘要与每项基准实际方法、时长、成绩、跳过项和停止条件。
- 有明确且有证据的适用任务分级、主要瓶颈和不适用场景。
- 无软件包、配置、网络或防火墙变更，临时文件已清理，PR 与 worklog 留痕完整。
