# ChatGPT 审核记录：biotech_asset_due_diligence Round 1

- PR: https://github.com/leezx/StelligenOS/pull/13
- Reviewed tip: `d87bed2`
- 审核方式：网页版 ChatGPT 的“GitHub PR 信息”对话，已通过聊天框 `+` 菜单选中 GitHub 来源。
- 结论：`REQUEST_CHANGES`

## 阻断项

1. `core/artifact_refs.py` 未强制要求外部 `workspace_root`，也未拒绝路径逃逸，因此不能保证输入位于外部运行目录。
2. `core/contract_validation.py` 只做浅层校验，未递归验证嵌套对象和数组元素类型，不满足严格合同验证要求。

## 修订动作

- 强制 ArtifactRef 校验必须使用存在的外部 workspace root，并拒绝 root 外路径。
- 将合同验证改为递归处理对象、数组、`items`、`additionalProperties`、`required`、`enum`、`pattern`、`minItems` 和嵌套类型。
- 增加路径边界和递归合同验证回归测试。
