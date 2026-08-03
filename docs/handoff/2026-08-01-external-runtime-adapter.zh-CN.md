# 任务交接备忘：External Runtime Adapter

- 任务编号：`task_20260801_external-runtime-adapter`
- 分支：`task_20260801_external-runtime-adapter`
- PR：**#17**（base 为 `task_20260801_os-boot-smoke`，即 PR #16 的 head）
- 当前状态：`ROUND_1_REQUEST_CHANGES_ADDRESSED_PENDING_REVIEW`
- 目标：为外部工作区拥有的 runtime 提供适配边界，使外部命令可被显式启用地调用，而输入、输出和数据全部留在仓库之外。
- **HEAD 与 aggregate diff 的权威来源是 GitHub PR #17 的实时值**；本文件中的数字均为撰写时快照。

本文件是 PR #17 的独立 handoff。此前该 PR 的内容被并入 `2026-08-01-os-boot-smoke.zh-CN.md`，导致 adapter 被描述为「未来步骤」，与实际流程状态不符。Round 1 审核将此列为阻断，已按要求拆出独立记录。

## 依赖与阻断关系

依赖顺序为 **#15 → #16 → #17**。本 PR 的 base 是 PR #16 的 head，因此 **#15 与 #16 依次获批并合并是本 PR 的前提**。

## 已实现

- `src/repository/external_runtime.py`
  - `ExternalRuntimeRequest`／`ExternalRuntimeResult`／`ExternalRuntimePort` 契约。
  - `SubprocessExternalRuntime`：仅在显式 `execution_enabled` 时运行外部命令。
  - 强制 `runtime_ref`、`input_ref`、`run_context_ref`、`output_ref`、`sandbox_profile_ref` 为 `external:` 引用。
  - 强制 `workspace_path` 与 `output_root_path` 位于仓库之外且必须是目录。
  - 环境变量采用最小允许清单，不继承父进程环境。
  - 运行前后对仓库做内容指纹比对，检测到变更即抛 `RepositoryMutationError`。
- `scripts/run_external_runtime.py`
  - 命令行入口，新增必填 `--sandbox-profile-ref`，仅在 `--execute` 时执行。

## Round 1 `REQUEST_CHANGES` 与修订

ChatGPT 对 HEAD `17404dc` 返回 `REQUEST_CHANGES`，五条阻断（两条安全、三条其他）经核实全部成立。

### 安全阻断 1：可执行任意命令，绝对路径仍可写回仓库

核实成立，且这是本 PR 最实质的问题。`_require_external_path` 只校验 `workspace_path` 与 `output_root_path`；命令本身是任意的，`python -c "open('<repo>/x','w')"` 可以直接写进 StelligenOS。而 `SubprocessExternalRuntime` 的 docstring 当时写的是「with no repository writes」——**这个保证从未被真正强制执行**，问题首先出在这个断言本身。

#### 一处技术判断：为什么没有引入容器沙箱

审核建议「将命令放入仓库不可见或只读挂载的受控外部执行环境」。方向正确，但在本仓库内直接实现有几个硬性代价：

- 本仓库当前**没有任何依赖声明文件**，引入 Docker／podman／bubblewrap 会使其从纯契约仓库变成带容器运行时依赖的仓库。
- 缺少容器运行时的环境（含 CI）将无法运行该测试。
- 真正的写入隔离本质上属于**运行环境**的职责，不是一个 Python 适配器能提供的能力。进程内阻止任意子进程写盘在 Python 中无法可移植地做到。

因此本 PR 不伪造一个做不到的技术保证，改为分层处理，并把每一层的能力边界写清楚：

| 层 | 内容 | 性质 |
|---|---|---|
| 1 | 未显式 `execution_enabled` 则不执行 | 预防 |
| 2 | 必填 `sandbox_profile_ref`，声明命令运行于何种受控环境 | 治理／可审计。仓库无法验证该声明，因此只记录为外部引用，且缺失即拒绝执行 |
| 3 | 环境变量最小允许清单 | 预防（真实生效，见安全阻断 2） |
| 4 | 运行前后仓库内容指纹比对，变更即抛错 | **检测，不是预防**。触发时写入已经发生；作用是让越界失败得响亮，而不是静默通过 |

模块 docstring 现在明确写出：本模块不提供沙箱；真正的写入隔离必须来自 `sandbox_profile_ref` 所指的环境——容器、只读挂载，或干脆是一台没有这个仓库的主机。

如果需要真正的隔离执行环境，建议另立任务，并同时决定该执行器是否应该继续留在本仓库内。

指纹实现细节：对仓库内全部文件做 SHA-256 内容哈希（而非 size+mtime，避免同长度原位改写漏过），排除 `.git`、`__pycache__` 和 `.DS_Store`。

### 安全阻断 2：`os.environ.copy()` 泄漏凭据

核实成立。原实现把父进程全部环境变量交给外部命令，`AWS_SECRET_ACCESS_KEY`、`GITHUB_TOKEN`、`SSH_AUTH_SOCK` 等会一并继承。

已改为最小允许清单 `INHERITED_ENVIRONMENT_KEYS = ("PATH", "LANG", "LC_ALL", "TZ", "TMPDIR")`。

**`HOME` 被刻意排除**：继承它等于暴露 `~/.ssh`、`~/.aws`。改为把 `HOME` 指向外部 workspace，这样写 `$HOME` 的工具也留在仓库之外。

### 阻断 3：`output_root` 只检查存在，未检查是否为目录

核实成立。已改为 `is_dir()`，并对 `workspace` 一并统一为 `NotADirectoryError`。不存在的路径与普通文件都会被拒绝。

### 阻断 4：handoff 仍是 PR #16 的旧状态

核实成立。已拆出本独立文件；`2026-08-01-os-boot-smoke.zh-CN.md` 在 PR #16 中同步更正为「PR #17 已实现且在本 PR 获批前仍被阻断」。

### 阻断 5：测试未覆盖写入仓库、敏感环境隔离与非目录 output root

核实成立。`tests/test_external_runtime.py` 由 3 项增至 17 项：

| 测试组 | 覆盖 |
|---|---|
| `ExternalRuntimeTests` 4 项 | 默认禁用执行、正常运行不产生仓库输出、失败以状态返回而非抛错、结果记录 sandbox 声明 |
| `RepositoryPathRejectionTests` 4 项 | 仓库根与子目录路径被拒、`output_root` 与 `workspace` 必须是目录（文件与不存在两种情形） |
| `SandboxAttestationTests` 2 项 | `sandbox_profile_ref` 必填且必须是 `external:` |
| `RepositoryMutationDetectionTests` 3 项 | **命令写入仓库被检测**（新建文件、修改既有文件两种），干净运行不误报 |
| `EnvironmentIsolationTests` 4 项 | 五类凭据不被继承且其值不出现在子进程环境、`HOME` 被重定向、无父进程变量越过允许清单、运行上下文以引用形式传入 |

#### 关于环境隔离测试的一处实证修正

初版断言「子进程环境的键必须全部落在允许清单内」，实测失败于 `__CF_USER_TEXT_ENCODING`。经验证：即使给子进程传 `env={}`，macOS 仍会注入 `__CF_USER_TEXT_ENCODING`、`SDKROOT`、`CPATH`、`LIBRARY_PATH`、`MANPATH`、`LC_CTYPE`。这属于平台注入，不是父进程泄漏。

因此改为先用 `env={}` 探测**平台注入基线**，再断言子进程环境 ⊆（允许清单 ∪ `STELLIGEN_*` ∪ 平台基线）。这样断言的是「泄漏」这一真正的安全属性，且不硬编码 macOS 特例，换平台仍成立。

### 变异测试证据

为验证新测试确实能捕捉安全回退，逐个撤销修复确认失败，随后从备份还原：

| 撤销的修复 | 结果 |
|---|---|
| 环境退回 `os.environ.copy()` | `FAILED (failures=8)` |
| 移除仓库变更检测 | `FAILED (failures=2)` |
| `output_root` 退回只查 `exists()` | `FAILED (failures=1)` |
| 全部还原 | `OK` |

## 明确未改动

- 未改动 `src/repository/boot.py`、`src/capabilities/`、`src/lifecycle/` 或任何 Gate/Model/Profile 定义。
- 未改动 45-Gate 拓扑、生命周期或核心对象。
- 未引入任何第三方依赖。
- 未改动 `.gitignore` 与 `scripts/verify_repository_boundary.sh`。
- 未执行任何真实外部 runtime；未新增数据、缓存、结果或临时产物。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1，逐模块运行 tests/test_*.py
结果：ALL OK —— 12 modules / 60 tests
      （修订前 46 项；tests/test_external_runtime.py 由 3 项增至 17 项）

命令：scripts/run_external_runtime.py 缺少 --sandbox-profile-ref
结果：error: the following arguments are required: --sandbox-profile-ref

命令：scripts/run_external_runtime.py 带 sandbox ref 但不加 --execute
结果：PermissionError: External runtime execution is disabled; pass an explicit opt-in

命令：git diff --check
结果：通过
```

`scripts/verify_repository_boundary.sh` 在本分支因本地 `.claude` 目录报 exit=1；该目录在本分支创建之后才出现，修复位于已获批的链顶 PR #43，本 PR 不重复修复以避免同文件合并冲突。

## AssetGenOS 运行边界核查

本节内容原先误置于 `2026-08-01-os-boot-smoke.zh-CN.md`（PR #16 的 handoff），实际属于本 PR 的运行边界。Round 1 修订时随独立 handoff 一并迁入此处。

- AssetGenOS 当前 CLI `adc-factory v2 evaluate` 需要明确的 target、gene、indication、endpoint 等业务输入。
- AssetGenOS 运行时会在其外部工作区管理 SQLite、cache、output 和外部数据索引；这些路径不能指向 StelligenOS。
- StelligenOS 不应猜测首个资产、路线或业务输入。实际运行前需要明确选择现有 Binder 路线或 de novo 路线，并提供外部输入引用。

## 未决问题与风险

- **仓库变更检测是检测而非预防。** 触发时写入已经发生。真正的写入隔离必须由 `sandbox_profile_ref` 所指的外部环境提供，本仓库无法验证该声明。
- 指纹会遍历并哈希仓库全部文件。当前规模下开销可忽略，若仓库将来显著增大需重新评估。
- `sandbox_profile_ref` 是新增必填字段，属于对 `ExternalRuntimeRequest` 的破坏性变更。当前调用方只有本仓库的测试与 `scripts/run_external_runtime.py`，均已同步。
- GitHub 上没有 commit status 或 Actions workflow，验证数字无法由 CI 独立复核。建议另立任务引入 CI。
- 合并后 `logs/worklog.md` 会与链上后续分支产生追加式冲突，解决方式是按时间顺序保留两侧。

## 下一步

1. 提交 ChatGPT 复审本 PR。
2. 只有收到 `APPROVE` 后，由人类负责人决定合并，且须在 #15、#16 合并之后。
3. 若需要真正的沙箱执行环境，另立任务，并同时决定该执行器是否应继续留在本仓库内。
