# 任务交接备忘：External Runtime Adapter

- 任务编号：`task_20260801_external-runtime-adapter`
- 分支：`task_20260801_external-runtime-adapter`
- PR：**#17**（base 为 `task_20260801_os-boot-smoke`，即 PR #16 的 head）
- 当前状态：`ROUND_3_REQUEST_CHANGES_ADDRESSED_PENDING_REVIEW`
- 任务性质：**contract-only**（Round 2 后已移除仓库内执行器）
- 目标：为外部工作区拥有的 runtime 定义请求／结果信封与 Port 契约。**本仓库不执行任何命令**，执行由外部受控运行环境实现该 Port。
- **HEAD 与 aggregate diff 的权威来源是 GitHub PR #17 的实时值**；本文件中的数字均为撰写时快照。

本文件是 PR #17 的独立 handoff。此前该 PR 的内容被并入 `2026-08-01-os-boot-smoke.zh-CN.md`，导致 adapter 被描述为「未来步骤」，与实际流程状态不符。Round 1 审核将此列为阻断，已拆出独立记录。

## 依赖与阻断关系

依赖顺序为 **#15 → #16 → #17**。本 PR 的 base 是 PR #16 的 head，因此 **#15 与 #16 依次获批并合并是本 PR 的前提**。

## 当前形态（Round 2 后）

- `src/repository/external_runtime.py` —— **纯契约，无执行能力**
  - `ExternalRuntimeRequest`：强制 `runtime_ref`、`input_ref`、`run_context_ref`、`output_ref`、`sandbox_profile_ref` 为 `external:` 引用；`workspace_path` 与 `output_root_path` 必须位于仓库之外；命令非空；timeout 为正。
  - `ExternalRuntimeRequest.envelope`：交给外部运行环境的交接载荷，显式声明 `executed_by: external_controlled_runtime` 与 `executed_in_repository: false`。
  - `ExternalRuntimeResult`：状态受限于 `completed`／`failed`，全部引用必须外部，且 **`status` 与 `exit_code` 必须一致**（`completed` 必须 `exit_code == 0`，`failed` 必须非零）。
  - `ExternalRuntimePort`：Protocol，方法体为 `...`，由外部**具备真实隔离能力**的运行环境实现。
- `scripts/run_external_runtime.py` —— **只校验并打印交接信封，不执行**
  - 与 `scripts/boot_os.py` 同形态：校验契约后输出 JSON，不调用任何子进程。
  - 已移除 `--execute` 与全部执行路径。

契约校验在这里是**契约校验，不是安全控制**。它规定什么样的请求算合规；命令运行期间的隔离由实现方负责。

## Round 1 `REQUEST_CHANGES` 与修订

ChatGPT 对 HEAD `17404dc` 返回 `REQUEST_CHANGES`，五条阻断经核实全部成立：`os.environ.copy()` 泄漏凭据、`output_root` 只查 `exists()`、缺独立 handoff、测试未覆盖三类情形，以及「可执行任意命令、绝对路径仍可写回仓库」。

Round 1 的做法是保留执行器并加四层防护（显式启用、必填沙箱声明、环境允许清单、运行前后仓库指纹比对），同时把每层是预防还是检测写明。环境隔离、目录校验、独立 handoff 与测试扩充这几项在 Round 2 被确认为真实修复并保留至今；执行器相关的部分已在 Round 2 整体移除，详见下节。

其中一处实证修正值得保留记录：环境隔离测试初版断言「子进程环境键必须全在允许清单内」，实测失败于 `__CF_USER_TEXT_ENCODING`。经验证即使传 `env={}`，macOS 仍注入 `__CF_USER_TEXT_ENCODING`、`SDKROOT`、`CPATH`、`LIBRARY_PATH`、`MANPATH`、`LC_CTYPE`，属平台注入而非父进程泄漏。当时改为先探测平台基线再断言「无泄漏」。该测试随执行器一并移除，但这一判断方法在将来实现真正沙箱时仍适用。

## Round 2 `REQUEST_CHANGES` 与修订：降级为 contract-only

Round 2 确认 Round 1 的环境隔离、目录校验、独立 handoff 与测试扩充均已真实修复，但指出仍有一个**实质性安全阻断**：`sandbox_profile_ref` 只是一个未经验证的字符串，`SubprocessExternalRuntime` 并未据此建立容器或只读挂载，仍然直接执行任意子进程。

### 四条攻击路径，其中两条已实证复现

| 攻击路径 | 实证结果 |
|---|---|
| 写入仓库后被事后检测 —— 损害已发生 | 成立（Round 1 即已承认指纹是检测非预防） |
| **修改 `.git/`，因 `.git` 被指纹排除而完全不被发现** | **实证成立**。写入 `.git/hooks/evil-probe` 后 `status=completed`、未抛错、文件确实存在。git hook 会在后续 checkout／commit 时执行，等于任意代码执行 |
| **结束前还原被修改文件，绕过运行后指纹比较** | **实证成立**。命令「写入 `README.md` → 读走原内容到 `/tmp/exfil` → 还原」后 `status=completed`、未抛错，且仓库内容已被完整读出 |
| 直接读取宿主机凭据或其他文件；环境白名单不提供文件系统隔离 | 成立。上一条的实证同时证明了这一点 |

第二条是 Round 1 修订**引入的漏洞**：为避免 `.git` 频繁变动造成误报而将其排除，结果留下了最危险的一块。这不是取舍失当，是漏掉了 `.git/hooks` 这个攻击面。

### 采纳「方案 1：降级为 contract-only」

审核给出两个选项，采纳推荐的方案 1，理由是它让本模块与整个仓库的设计一致，而不再是例外：

- `src/` 现有约 2000 行几乎全部是 frozen dataclass 与方法体为 `...` 的 Protocol。**`SubprocessExternalRuntime` 是唯一的真实执行器，本身就是异类。**
- 架构契约要求一切数据处理发生在仓库之外；仓库内自带执行器与该原则冲突。
- 方案 2 需要引入容器运行时依赖，而本仓库无任何依赖声明文件，且缺容器运行时的环境（含尚不存在的 CI）无法运行其测试。
- Round 1 的 handoff 已把「该执行器是否应继续留在本仓库内」列为未决问题。本轮审核给出了答案：不应该。

具体改动：

| 移除 | 保留 |
|---|---|
| `SubprocessExternalRuntime` | `ExternalRuntimeRequest`／`Result`／`Port` |
| `RepositoryMutationError`、`_repository_fingerprint`、`_describe_mutations` | 全部契约校验（外部引用、仓库外路径、非空命令、正 timeout） |
| `INHERITED_ENVIRONMENT_KEYS` 及环境构造 | `sandbox_profile_ref`（改为契约字段，声明实现方必须满足的隔离要求） |
| `os`／`subprocess`／`hashlib` 导入 | 新增 `envelope` 交接载荷 |
| CLI 的 `--execute` 与全部执行路径 | CLI 的契约校验与 JSON 输出 |

`sandbox_profile_ref` 在 contract-only 形态下不再假装是执行期防护，而是交接契约的一部分：它声明实现方必须在何种受控环境中执行，仓库只负责记录与传递。这样它作为「未经验证的字符串」不再构成安全问题，因为仓库不再据它做任何放行决定。

### 依赖影响核查

移除前已确认链上后续分支（`gen-iet-phase0`、`crc-target-enumeration`、`architecture-extensions` 等）中，只有这三个文件本身引用 `SubprocessExternalRuntime`，**没有任何其他模块导入它**，因此移除不会破坏上层分支。

### 降级后的复测

```text
SubprocessExternalRuntime 存在: False
RepositoryMutationError 存在:   False
模块源码含 'subprocess' / 'os.environ' / 'hashlib': False / False / False
CLI 传入会写文件的命令 -> 探针文件未被创建（CLI 不执行任何命令）
```

新增 `NoExecutionCapabilityTests` 6 项作为防回归闸门：模块不得导出 `SubprocessExternalRuntime`、不得 `import subprocess`／`os`／`hashlib`、不得再定义指纹与 `RepositoryMutationError`、公开符号集合被精确固定、Port 方法体为 stub、CLI 源码不得出现 `subprocess`／`--execute`／`execution_enabled`。

## Round 3 `REQUEST_CHANGES` 与修订：结果合同的矛盾状态

Round 3 确认执行安全阻断已正确解决（执行器完全移除、CLI 只生成交接信封、仓库内不存在 subprocess／指纹／伪沙箱逻辑），但指出**结果合同仍存在一个真实的矛盾状态漏洞**。

`ExternalRuntimeResult` 当时只校验 `status ∈ {completed, failed}`，未校验它与 `exit_code` 的一致性。实证确认两种矛盾组合都能合法构造：

```text
status='completed', exit_code=3  -> 可构造（应被拒）
status='failed',    exit_code=0  -> 可构造（应被拒）
```

这个漏洞是**降级为 contract-only 之后才变得重要的**，审核指出的因果关系准确：以前结果由仓库内执行器生成，`status` 由 `exit_code` 派生，两者不可能不一致；现在结果完全由外部实现提交，属于**不可信入站输入**，StelligenOS 必须在合同入口拒绝矛盾结果，否则会把自相矛盾的运行结论当成事实记录下来。

修订：`ExternalRuntimeResult.__post_init__` 增加两条一致性约束——`completed` 必须 `exit_code == 0`，`failed` 必须 `exit_code != 0`。docstring 说明这是入站合同、以及为何在移除执行器后必须补上这项校验。

新增 4 项测试（`test_external_runtime.py` 20 → 24 项）：

| 测试 | 覆盖 |
|---|---|
| `test_completed_with_a_non_zero_exit_code_is_rejected` | `completed` 配 `1`／`3`／`255`／`-9` 全部拒绝 |
| `test_failed_with_a_zero_exit_code_is_rejected` | `failed` 配 `0` 拒绝 |
| `test_consistent_results_are_accepted` | `completed/0` 与 `failed/3` 接受 |
| `test_signal_termination_is_a_valid_failure` | `failed/-9` 接受——被信号杀死的进程返回 `-N`，属非零，不应误拒 |

最后一项是刻意加的：如果把「非零」错写成「正数」，信号终止的合法结果会被拒绝。实测五种组合行为全部正确。

## AssetGenOS 运行边界核查

本节内容原先误置于 `2026-08-01-os-boot-smoke.zh-CN.md`（PR #16 的 handoff），实际属于本 PR 的运行边界，Round 1 修订时随独立 handoff 迁入此处。

- AssetGenOS 当前 CLI `adc-factory v2 evaluate` 需要明确的 target、gene、indication、endpoint 等业务输入。
- AssetGenOS 运行时会在其外部工作区管理 SQLite、cache、output 和外部数据索引；这些路径不能指向 StelligenOS。
- StelligenOS 不应猜测首个资产、路线或业务输入。实际运行前需要明确选择现有 Binder 路线或 de novo 路线，并提供外部输入引用。

降级为 contract-only 后，上述运行本身将由外部受控环境执行；本仓库只产出经校验的交接信封。

## 明确未改动

- 未改动 `src/repository/boot.py`、`src/capabilities/`、`src/lifecycle/` 或任何 Gate/Model/Profile 定义。
- 未改动 45-Gate 拓扑、生命周期或核心对象。
- 未引入任何第三方依赖。
- 未改动 `.gitignore` 与 `scripts/verify_repository_boundary.sh`。
- 未执行任何真实外部 runtime；未新增数据、缓存、结果或临时产物。

## 验证

### 当前验证（Round 2，权威）

```text
命令：PYTHONDONTWRITEBYTECODE=1，逐模块运行 tests/test_*.py
结果：ALL OK —— 12 modules / 89 tests
      tests/test_external_runtime.py 24 项（形态已完全改变，非 Round 1 的 17 项之增量）

命令：scripts/run_external_runtime.py 传入会写文件的命令
结果：探针文件未被创建；CLI 只输出交接信封，不执行任何命令

命令：scripts/run_external_runtime.py 缺 --sandbox-profile-ref
结果：argparse 报缺失必填参数

命令：scripts/run_external_runtime.py 以仓库根为 workspace
结果：must be outside the StelligenOS repository

命令：git diff --check
结果：通过
```

`scripts/verify_repository_boundary.sh` 在本分支因本地 `.claude` 目录报 exit=1。该目录是本地 Claude Code 工具配置、被用户全局 gitignore 忽略，在本分支创建之后才出现，**不在本 PR 的提交树中**；干净 clone 上本分支的边界检查通过。对应修复位于已获批的链顶 PR #43，本 PR 不重复修复以避免同文件合并冲突。

### 历史验证数字（仅供追溯，不作为审核依据）

| 轮次 | 模块 / 总项数 | `test_external_runtime.py` | 形态 |
|---|---|---:|---|
| 初始 | 12 / 46 | 3 | 含 subprocess 执行器 |
| Round 1 | 12 / 60 | 17 | 执行器 + 四层防护 |
| Round 2 | 12 / 85 | 20 | contract-only，无执行能力 |
| **Round 3（当前）** | **12 / 89** | **24** | **contract-only + 结果一致性校验** |

验证数字的权威来源是当前 HEAD 上实际运行的结果。

## 未决问题与风险

- **本仓库现在完全不具备执行外部 runtime 的能力。** 这是本轮的有意结果，但也意味着真实运行需要先有一个实现 `ExternalRuntimePort` 的外部受控环境。该环境尚不存在，需另立任务建设。
- 该外部实现必须真正做到仓库对命令不可见或只读、且宿主凭据不可达。本仓库无法验证这一点，只能在契约中声明要求。
- `sandbox_profile_ref` 与移除 `execution_enabled` 都是对 `ExternalRuntimeRequest` 的破坏性变更。当前调用方只有本仓库测试与 `scripts/run_external_runtime.py`，均已同步。
- GitHub 上没有 commit status 或 Actions workflow，验证数字无法由 CI 独立复核。建议另立任务引入 CI。
- 合并后 `logs/worklog.md` 会与链上后续分支产生追加式冲突，解决方式是按时间顺序保留两侧。

## 下一步

1. 提交 ChatGPT 复审本 PR。
2. 只有收到 `APPROVE` 后，由人类负责人决定合并，且须在 #15、#16 合并之后。
3. 真正的外部受控执行环境另立任务建设，并实现 `ExternalRuntimePort`。
