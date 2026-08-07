# Handoff：架构说明文档 v4 refresh

- 日期：`2026-08-06`
- 任务分支：`task_20260806_architecture-v4-refresh`
- 基线：`main` @ `4d895d7`
- 交付物类型：**纯文档刷新 + 补登一份审核记录**
- 架构变更：`NO_ARCHITECTURE_CHANGE`（不改代码、契约、测试、Gate 或科学决策）
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、为什么现在做

审核方在批准 PR #72 时明确指示：「合并后开始架构 v4 refresh」。

`v3-draft` 的基线是 `main@8aa7e87`（PR #60），落后 36 个 commit。它记录的三个
开放 PR 全部已结清，测试数、EVGAP 阻断理由都已过时，且**完全没有提到 Phase
1–4 的 sponsor-relative 决策轴**——而那条轴现在已经有一段进入代码强制。

## 二、改了什么

### 1. `docs/architecture/CURRENT_SYSTEM_AND_MODULE_LOGIC_FOR_EXPERT_REVIEW.zh-CN.md`

`v3-draft` -> `v4-draft`，基线 `main@8aa7e87` -> `main@4d895d7`。

**新增第 7 节「Sponsor-relative 决策轴（Phase 1–4）」。** 这是本次刷新的主体。
它把四个合同、Phase 2 的四种路由、Phase 3 的六个结果、Phase 4 的必填字段，以及
PR #72 的绑定写成一节，并明确区分：第 6 节的 45 个 Gate 回答「科学上成不成
立」，第 7 节回答「当前发起方要不要投」。

**新增设计原则 11「发起方判断与科学事实分离」。** 原则表从 10 条增为 11 条。
`OUT_OF_MANDATE` 与 `STOP_FOR_SPONSOR` 不是 KILL，科学成立也不自动构成承诺。
第 8.4 节同时补了一句对照，防止 target-safety 的 `KILL` 与 sponsor 轴的
`STOP_FOR_SPONSOR` 被混用。

**第 13 节运行流程图补上四个控制点**，并写明其中只有
`Program Commitment Review -> ValueInflectionPlan -> external human
authorization -> route selection` 这一段在代码层强制，Phase 1／2 仍只是流程约定。

**更正的事实：**

| 位置 | `v3-draft` | `v4-draft` |
|---|---|---|
| 仓库基线 | `main@8aa7e87` | `main@4d895d7` |
| 单元测试数 | 338 | 413 |
| PR #62 | 未合并 | 已合并 `17c5707` |
| PR #63 | 开放 | 已合并 `98a1698` |
| PR #55 | 开放且 DIRTY | 已关闭，superseded by #56 |
| 开放 PR | 三个 | 无 |
| `EVGAP-01` 阻断理由 | admission 引用未绑定 | **已授权，未执行** |
| `EVGAP-02` 状态 | 只有 retrieval | 同，补 `gap_discharged=false` 与机器可读状态串 |
| `GAP-P07` | 四个实体并列 | 区分三个不可消歧与 `CA19-9` 已解析但须人裁定 |

**第 16 节审核问题 12 条 -> 17 条。** 新增 13–17：`src/contracts/` 的分层归属、
Phase 1／2 无消费者、stop rule 与 `stop_condition_refs` 是否合并、
`authorises_extraction_run_count` 无消费机制、三处 YAML 引号缺陷。

**逐项复核了沿用的数字，未盲抄。** `45` Gate／`59` Model／`53` Profile／
`7` 共享合同均按 `model.yaml`、`profile.yaml` 实际计数核对通过；四个扩展的
`status` 逐个读取 `extension.yaml` 核对；六个模块有 `module.yaml`、
`gen_indication_endpoint_target` 仍无，核对属实；Gate envelope `2.0.0`/`2.1.0`
漂移复核确认仍存在；三处 YAML 引号缺陷逐行读取并解析验证仍存在。

### 2. `logs/chatgpt-review-2026-08-06-sponsor-control-binding.md`（新增）

补登 PR #72 的 `APPROVE`。**记录必须在本 PR 补登，不能在 #72 内补**：审核方的
批准在 PR 内容冻结之后才到，在 `a1b30d6` 上再加文件会改掉被批准的那个 HEAD。

记录含两轮历史（`4d895e2` 与 `a1b30d6`）、审核方核对项、批准范围原文、以及
「仓库只校验 authorization 引用存在、不读取 commitment outcome」这条边界——
后者是本 PR 最容易被后人误读的地方。

### 3. `architecture.md` / `README.md` / `docs/architecture/versions/README.md`

审核基线字符串 `v3-draft` -> `v4-draft`。`versions/README.md` 同时更正：
`v2-draft` 与 `v3-draft` **均未获批，因此都没有快照**，按规则 4 不补造。

## 三、本 PR 不做什么

不修改任何代码、契约、测试、Gate、Model、Profile、lifecycle、core objects 或
target 轴；不解除 `EVGAP-01`／`EVGAP-02`；不执行任何抽取或外部运行；不修复
第 16 节登记的任何缺陷（envelope 漂移、YAML 引号、`authorises_extraction_run_count`
无消费机制、Phase 1／2 无消费者）——**它们只被登记，不在本 PR 修**，符合
第 17 节规则 6。

不把 `v4-draft` 复制进 `versions/`：未获批的 draft 不产出快照。

## 四、验证

```
Ran 413 tests  OK
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
git status --short                      仅本 PR 涉及的文件
```

测试数与文档中写的 413 一致。无数据、cache、result、database、model weights
或实例进入仓库。

## 五、仍欠的审核记录

`#52`／`#53`／`#54`／`#57`／`#58`／`#59`／`#60`／`#61`／`#66` 九份仍未补。
本 PR 只补 #72——它是刚合并且尚无记录的那一份。

早期几份的审核原文需要从 handoff 与 worklog 回溯重建，属二手记录；补登时须
明确标注来源与局限，不得伪装成审核原文。

## 六、后续顺序

1. 本 PR `APPROVE` 并合并。若获批，按第 17 节规则 3 可考虑把 `v4` 复制进
   `versions/` 形成只读快照——**这需要审核方明确说「批准 v4 文档版本」**，
   而不只是批准本 PR 的改动。
2. **执行一次 `EVGAP-01` 抽取**（外部运行，产物不入仓）→ 结果 PR →
   binding PR 解除 `EVGAP-01`。
3. `EVGAP-02` 侧独立推进：先裁定 `GAP-P07`（含 `CA19-9` 是否属于膜蛋白 target
   universe），再执行 `L-ASSERTION` 抽取。
4. **两个缺口都解除后**，才能生成 `ADC_POOL_LEVEL_01_ACCEPTED`。
