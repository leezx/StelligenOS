# miniPC 性能报告交接记录

## 目标与来源

负责人希望在 Ubuntu home 留存既有 miniPC 性能结果，以便之后据此选择任务。报告依据已审核的 [PR #149](https://github.com/leezx/StelligenOS/pull/149) 脱敏摘要整理；没有重连设备或重复基准测试。

## 报告文件

- 仓库内报告：`docs/MINIPC_CAPABILITY_REPORT.zh-CN.md`。它只包含报告正文，不包含会随 PR 生命周期变化的状态或交付记录。
- Ubuntu home 目标：`/home/stelligen/MINIPC_CAPABILITY_REPORT.md`。
- 仅复制报告正文，不复制主机原始日志/输出。PR exact-head 获得 GPT/ChatGPT `APPROVE` 后才能写入目标机。

## 当前审核状态

- 独立 PR：[PR #151](https://github.com/leezx/StelligenOS/pull/151)，base `main`，branch `task_20261023_minipc_capability_report`。最新报告/审计提交复核结果和 home 上传记录见本文件与 `logs/worklog.md`。
- 对此前 exact HEAD `22e3b7deb3c843b9f22ff678e5d0172a645ff059` 的报告内容审查为 `APPROVE`；此后复核 exact HEAD `d4ca45377bf4de5a03a5e6e2dd1d9fa66ba7ea86` 时发现交付状态文字过期，并指出上传 hash 指向旧版本。按反馈将纯报告正文与交接状态分离；本轮修订提交 `481bf75506bc193fbade5ce2c617f1768b54af7f` 已推送到同一 PR，等待对最新 exact HEAD 审核。新报告获批后才替换目标 home 文件。
- 新报告已于 2026-10-23 17:38 EDT 覆盖写入 `/home/stelligen/MINIPC_CAPABILITY_REPORT.md`。来源 PR exact HEAD `b5a5f81548bb318a30433b37445c94371906a28f` 已获独立 GPT `APPROVE`。本地与远端 SHA256 均为 `2011e4bb3d910cb55a9a74309529662a6dcce2297f7c15146db2a11469a20dfb`；权限 `-rw-r--r--`，属主 `stelligen:stelligen`，大小 3874 bytes。已替换旧版；只写入该报告文件，没有运行基准或更改系统配置。
- 新版本上传后更新的 handoff/worklog 提交尚需在同一 PR 对最新 exact HEAD 做复核。

## 保护边界

只包含脱敏基准汇总，不含原始主机输出、日志、账户、Tailscale 地址、Wi-Fi 信息、个人文件或序列号。之后仅执行获批的单文件写入并校验 SHA256；不运行基准或更改系统配置。
