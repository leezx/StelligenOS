# 任务交接备忘：OS Boot Smoke

- 任务编号：`task_20260801_os-boot-smoke`
- 目标：根据冻结 architecture 建立无数据 OS 启动入口，证明架构可以被加载并准备接入外部 runtime。
- 当前状态：Boot Smoke 已完成；外部 Runtime Adapter 已在后续任务分支实现，待创建 PR 并提交 ChatGPT 审核。

## 已实现

- `src/repository/boot.py`
  - 加载四个生命周期阶段、9 个能力、3 个 Gate Group 和 2 条 Binder/ADC 路由。
  - 强制 workspace、run context、policy 使用 `external:` 引用。
  - 只返回静态 BootReport，不执行模型、不写入仓库、不生成结果。
- `scripts/boot_os.py`
  - 提供命令行启动入口并打印 JSON 架构计划。
- `tests/test_os_boot.py`
  - 覆盖正常启动、拒绝本地引用和 CLI 启动。

后续分支新增 `src/repository/external_runtime.py` 和
`scripts/run_external_runtime.py`，仅在显式 `--execute` 时运行外部命令，并
拒绝仓库内 workspace/output 路径。

## 验证

- Boot Smoke 基线：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 43 passed
- 加入 External Runtime Adapter 后：46 passed
- `./scripts/verify_repository_boundary.sh`: passed
- `git diff --check`: passed

## 下一步

- 先通过 ChatGPT 审核本 PR。
- 审核通过后，再新增外部 AssetGenOS runtime adapter；adapter 只能读取外部 workspace 并通过现有 capability ports 返回外部引用。
