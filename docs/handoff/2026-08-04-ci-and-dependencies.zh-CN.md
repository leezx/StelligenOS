# 任务交接备忘：CI 与依赖声明

- 任务编号：`task_20260804_ci-and-dependencies`
- 分支：`task_20260804_ci-and-dependencies`（从 `main` `3708024` 创建）
- 当前状态：`PENDING_CHATGPT_REVIEW`
- 变更性质：新增 CI、依赖声明、边界脚本机制推广、边界行为测试
- Gate 变更：`NO_GATE_CHANGE`
- 内核变更：`NO_KERNEL_CHANGE`（未改动 `src/` 下任何 `.py`）

**本任务不适用「纯文本默认通过」常设授权**，因为包含 CI 配置、依赖声明与脚本逻辑变更。须经
ChatGPT `APPROVE` 后方可合并。

## 要解决的问题

从 PR #15 到 #48，每一份 handoff 与审核记录都带同一条残余风险：仓库没有 GitHub Actions 或
commit status，因此所有测试数字只能由仓库自身的审计记录佐证，无法独立复核。同时仓库没有依赖声明
文件，而多个测试依赖 `pyyaml`——新环境按仓库现有说明无法把测试跑起来。

## 依赖划分：先查清再声明

仓库内实际出现的第三方导入不止 `pyyaml`。逐个映射到文件后结论如下：

| 包 | 出现位置 | 判定 |
|---|---|---|
| `PyYAML` | `tests/` 下 5 个测试模块 + `genmodules/.../contract_validation.py` | **本仓库测试依赖**，写入 `requirements.txt` |
| `dagster` | `genmodules/*/dagster_defs.py` | 外部运行环境依赖，不写入 |
| `anarci`、`abnumber` | `genmodules/antibody_binder_asset_engineering/lib/numbering.py` | 同上 |
| `Bio`（biopython）、`ImmuneBuilder` | `genmodules/antibody_binder_asset_engineering/lib/structure.py` | 同上 |

后五个不写入的理由不是「暂时不装」，而是**装了会造成错误声明**：没有任何测试导入这些模块，仓库内
不执行任何 pipeline，`src/repository/external_runtime.py` 已被降级为 contract-only 且有 6 项防回归
测试。把 pipeline 依赖写进本仓库的依赖文件，等于声称本仓库能跑 pipeline，而它不能。这些依赖属于实现
`ExternalRuntimePort` 的外部受控环境。该判断连同理由写进了 `requirements.txt` 注释，避免将来被当成
遗漏而「补上」。

### 实证

不是靠读代码下的结论。在只装 `PyYAML` 的干净 venv 中跑完整套件：

```text
venv 内已安装：PyYAML==6.0.3（除 pip/setuptools 外无其他包）
结果：Ran 207 tests —— OK
```

### 非 Python 依赖

`tests/test_git_sync.sh` 使用 `rg`（ripgrep），共 3 处。GitHub runner 镜像是否自带 ripgrep 不能假定，
因此 CI 显式安装。**未修改该测试**——它已获批准，为迁就 CI 去改已批准的测试是反向的。

### Python 版本下限

`src/lifecycle/state_machine.py` 使用 `enum.StrEnum`，需要 3.11+。该下限不是只写在文档里：

- CI 矩阵同时跑 3.11 与 3.12，若下限判断有误 3.11 任务会直接失败。
- 本地用 `ast.parse(..., feature_version=(3, 11))` 扫过全部 92 个 `.py` 文件，无 3.11 不兼容语法。
- 扫过 3.12 独有 stdlib API（`itertools.batched`、`typing.override`、PEP 695 `type` 语句等），无命中。

## CI 设计

`.github/workflows/ci.yml`，触发于 `push` 到 `main` 与全部 `pull_request`。

`permissions: contents: read`，只读最小权限。`concurrency` 取消同 ref 的过期运行。

检查顺序**刻意**如下：

1. 单元测试（`PYTHONDONTWRITEBYTECODE=1`）
2. `tests/test_git_sync.sh`
3. `scripts/verify_repository_boundary.sh`
4. 无 `__pycache__` 残留
5. 工作树未被测试运行改动（`git diff --check` + `git status --porcelain` 为空）

后三项放在测试**之后**才有意义——只有套件跑过一遍，才可能留下产物。第 5 项是把 data-free 原则变成
CI 断言：一个 data-free 仓库跑完整套测试后必须与跑之前逐字节相同。

`PYTHONDONTWRITEBYTECODE=1` 是必须的而非讲究：`__pycache__` 会被 `test_assetgenos_modules.py`、
`test_gen_indication_endpoint_target.py` 和 boundary check 判为运行产物，不设该变量 CI 会自己把自己
弄失败。该陷阱在 2026-08-01 已经踩过一次。

## 边界脚本：把 `.claude` 机制推广而非复制

`.github` 与 `requirements.txt` 都不在 `allowed_top_level` 中，CI 文件加入后 boundary check 会先行
失败。

`.github` **没有**被整目录加入 allowlist。PR #43 的 Round 1 审核明确阻断过「整个 `.claude` 目录进
allowlist 过宽」，当时的修法是精确路径豁免。同样的判断适用于 `.github`：CI 目录一旦整体放开，
`CODEOWNERS`、issue 模板、缓存都能随后进来而无人察觉。

因此把原先专用于 `.claude` 的机制推广为共用的 restricted-directory 机制：

```bash
restricted_dirs=( ".claude" ".github" )
allowed_restricted_paths=(
  ".claude/settings.local.json"
  ".github/workflows"
  ".github/workflows/ci.yml"
)
```

顶层循环对 restricted 目录放行，随后逐路径校验其内容；目录与文件都必须精确命中白名单。
`requirements.txt` 作为单个精确文件名加入 `allowed_top_level`。

原脚本注释「A `.claude` file is not exempt」的行为予以保留：豁免针对目录，同名文件不豁免。

## 为什么给边界脚本补测试

`scripts/verify_repository_boundary.sh` 此前没有任何测试，负面用例靠人工核对并记入 worklog。本次
改动了这个脚本的执行规则本身——推广一条强制规则却不留测试，等于此后不再知道它的行为。

新增 `tests/test_repository_boundary.py`，15 项。做法是把脚本复制进临时目录：脚本从自身位置推导
repo_root，于是临时目录成为被测根，全部用例跑在合成树上，**不触碰本仓库**。这一点是必需的——该脚本
的职责就是拒绝越界文件，用「在仓库里造越界文件」的方式测它属于以违规验证合规，也会与 CI 第 5 项断言
直接冲突。

覆盖：合规树通过；顶层散落文件与目录被拒；`requirements.txt` 通过；`.claude` 单一许可文件通过而其他
文件、嵌套目录被拒；同名文件不豁免；CI workflow 通过而第二个 workflow、`.github` 下散落文件与目录
被拒；已允许目录不要求存在；`.csv` 与 `.zip` 即使位于允许目录内也被拒。

## 变异测试证据

还原用文件备份，不用 `git checkout --`：

| 注入的缺陷 | 结果 |
|---|---|
| 把 `.github` 加进 `allowed_top_level` | `OK` ← 见下 |
| 删除 `.claude/settings.local.json` 许可 | `FAILED (failures=1)` |
| 整段跳过 nested restricted-path 扫描 | `FAILED (failures=5)` |
| 从 allowlist 删除 `requirements.txt` | `FAILED (failures=1)` |
| 把 `.github` 从 `restricted_dirs` 移除 | `FAILED (failures=4)` |
| 同时加进 allowlist **且**从 `restricted_dirs` 移除 | `FAILED (failures=3)` |
| 全部还原 | `OK` |

第一行未失败，已单独查明原因：`.github` 仍在 `restricted_dirs` 中，顶层循环先 `continue` 短路，
该 allowlist 条目成为死代码。实测确认——注入后在 `.github/` 下放探针文件仍被拒绝，行为未变。因此这是
**无效变异，不是测试漏洞**；真正危险的组合是同时加白名单并移出 restricted_dirs，即上表最后一条，
已被捕获。

## 变更清单

| 文件 | 变更 |
|---|---|
| `requirements.txt` | 新增。`PyYAML>=6.0,<7`，附依赖划分理由与版本下限说明。 |
| `.github/workflows/ci.yml` | 新增。3.11／3.12 矩阵，5 步检查。 |
| `scripts/verify_repository_boundary.sh` | `.claude` 专用机制推广为 restricted-directory 机制；`requirements.txt` 入 allowlist。 |
| `tests/test_repository_boundary.py` | 新增 15 项行为测试。 |
| `README.md` | 新增「本地运行验证」一节；关键入口补两条。 |

## 明确未改动

- 未改动 `src/` 下任何 `.py`，未改动任何契约、Gate 拓扑、`gate_id`、Model、Profile、生命周期或核心
  对象。
- 未改动 `tests/test_git_sync.sh`（已批准的测试不为迁就 CI 而改）。
- 未改动 `extensions/` 任何文件。
- 未改动 `.gitignore`。
- 未改写任何历史审计记录。
- 未新增数据、缓存、结果或运行产物。

## 验证

```text
命令：PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py'
结果：Ran 207 tests —— OK（192 + 新增 15）

命令：同上，在只装 PyYAML 的干净 venv 中
结果：Ran 207 tests —— OK

命令：bash tests/test_git_sync.sh
结果：git_sync behavior tests passed (A-D).

命令：bash scripts/verify_repository_boundary.sh
结果：Repository boundary check passed.

命令：git diff --check
结果：通过

3.11 语法扫描：92 个 .py 文件，无不兼容
__pycache__：0
工作树：跑完整套件后除本次改动外无变化
```

## 未决问题与风险

- **CI 尚未在真实 GitHub Actions 上跑过。** 本 PR 是引入该 workflow 的 PR，因此它首次实际执行就是在
  本 PR 上。若失败须在同一 PR 内修订。本地已尽可能预演（干净 venv、3.11 语法扫描、逐步骤手工执行、
  YAML 解析校验），但 runner 环境差异无法完全消除。
- CI 只跑 `ubuntu-24.04`。仓库开发实际发生在 macOS（`bash` 3.2），两者的 `find`／`bash` 行为存在差异
  而 CI 不覆盖 macOS。如需可另立任务加 matrix。
- `PyYAML` 采用 `>=6.0,<7` 而非精确钉版。取舍：本仓库不是可分发包，精确钉版会带来持续维护而收益有限；
  上界防止意外跨大版本。若要求完全可复现构建，需另立任务引入锁文件。
- `requirements.txt` 未声明 Python 版本下限（该文件格式不支持）。下限由 CI 矩阵、`README.md` 与
  `requirements.txt` 注释三处表达，但无单一机器可读来源。引入 `pyproject.toml` 可解决，但会暗示本仓库
  是可打包项目，与现状不符，故未做。
- 52 个已合并分支仍未清理；分支删除属破坏性操作，须人类负责人明确授权。
- 「纯文本默认通过」常设授权仍未写入 `AGENTS.md`，对未来会话不可发现。

## 下一步

- 推送并创建 PR 供 ChatGPT 审核。**本 PR 不适用常设授权，须获 `APPROVE` 后由人类负责人决定合并。**
- 合并后，「仓库无 CI，测试数字只能由审计记录佐证」这条残余风险即可从后续 handoff 中移除。历史记录中的
  该表述属既往事实，不回写。
