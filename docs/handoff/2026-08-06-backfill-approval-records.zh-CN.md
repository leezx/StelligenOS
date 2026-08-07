# Handoff：补登九份历史审核记录

- 日期：`2026-08-06`
- 任务分支：`task_20260806_backfill-approval-records`
- 基线：`main` @ `9756982`
- 交付物类型：**审计记录补登（无功能变更）**
- 架构变更：`NO_ARCHITECTURE_CHANGE`
- 审核状态：等待 ChatGPT `APPROVE`。**本 PR 不适用 `AGENTS.md`「审核豁免」。**

## 一、补的是哪九份

`#52`／`#53`／`#54`／`#57`／`#58`／`#59`／`#60`／`#61`／`#66`。

九个 PR 全部已合并进 `main`，但仓库内没有任何一份批准记录，GitHub 上也没有——
`gh pr view --json reviews` 对九个全部返回空。任何后续审核者读到的都是
「`REQUEST_CHANGES` 之后直接进 `main`」，正是 `#46` 与 `#52` 各自修复过的那类
审计断层。

## 二、必须先说清楚的一件事：这些记录不是审核原文

**其中八份的审核方最终批准原文已不可恢复。** 它们从未写入 GitHub，从未转述进
`logs/`，仓库内也没有逐字副本。

因此八份统一标注 `Record type: reconstructed_secondary`，并在文件头部写明：
「**不要把『Accepted conclusion』一节当作审核方的话**」——那一节陈述的是幸存
证据支持的较窄结论，即「给出过批准且 PR 已合并」。

**可恢复的部分是完整且一手的**：各轮 `REQUEST_CHANGES` 的阻断条目当时就被逐条
写进了 `docs/handoff/` 与 `logs/worklog.md`，多份 handoff 还把审核原文置于文首
并注明「下方原文一字未删」。这些在记录中明确标为一手材料。

第九份 `#66` 标注 `relayed_verbatim_conclusion`：审核结论与非阻断意见由人类
负责人转述，逐字引用。它比另外八份强，但仍然不是 GitHub review。

`#66` 当时未能补登的原因也写进了记录：当时的指令是「不要再开新 PR 了」。

## 三、核对而非誊抄，发现并更正一处

`logs/worklog.md` 2026-08-05 的条目把 `#54` 记为「`8992563`／`58984e7`」，
即把 `58984e7` 当作 merge commit。逐个 SHA 回查 git 后确认：

```
8992563  task_20260804: re-measure test count after merging main (228 tests)   ← 获批 head
58984e7  Merge remote-tracking branch 'origin/main' into task_..._playbook     ← 分支最终 head
e7092d5  Merge pull request #54 from leezx/task_20260804_adc-seed-playbook     ← 真正的 merge commit
```

记录里写的是核对后的值，并在 `#54` 的记录中说明这处差异。**worklog 原文未改**
——它是历史记录，更正写在新记录里，与此前处理 `#57` `BLOCK-02` 的做法一致。

同类情况另有三处，均已核对并在记录中说明：`#54`、`#57`、`#60` 的分支最终 head
都是「把 `main` 合并进分支」的提交，与获批 head 不同，差异仅为 `main` 进入。

九份记录的 PR 号、获批 head、merge commit 全部以脚本对照 `gh pr view` 复核通过。

## 四、每份记录保留了什么

不是简单的「已批准」四个字。各份按其实际历史保留了：

- **`#53`／`#54`**：这两份最容易被误读，故在文首即声明——**被批准的是隔离修订，
  不是那次外部运行**。运行状态是 `UNAUTHORIZED_QUARANTINED_NOT_ACCEPTED`。
  两份逐条保留了四条与五条阻断，以及「不接受内容清单」。`#54` 保留了污染点的
  具体位置：该运行消费了 `#53` 的 anchor clinical context，M5 的 `AE-01` 正是
  据此把三个靶点全标 `MET`。
- **`#57`**：保留了它自己 `BLOCK-02` 的表述错误，以及在 `#58` 中作出的更正
  （2026-08-02 枚举早已由 `#29` 批准，存在完整未隔离输入链，**不需要任何新的
  枚举运行**）。也保留了 15 项变异检验。
- **`#58`**：三轮 `REQUEST_CHANGES`。第二轮的两个科学语义阻断正是把这个 PR
  降级为 `raw_axis_binding_only` 的原因，并由此登记出 `EVGAP-01` 与 `EVGAP-02`。
- **`#59`**：保留了那个关键发现——所需数据一直在本地，而**那个库从未被批准**；
  以及「派生数据库不能靠自声明加哈希纳入」这条裁决如何催生了 `SRCADM-01`。
- **`#60`**：保留了执行者写反的生成逻辑，以及第二轮「交付包版本不匹配」的裁决。
  该裁决确立的规则——**每次交付必须出带校验和的包、每个修订各带自己的
  SHA-256**——是后来 `#62` 的 `verify_package.py` 与 `#63` 的 `verify_audit.py`
  的直接来源。也如实保留了 `git stash -u` 那次执行者失误。
- **`#61`**：保留了 `0.1.0` 契约里那个后来引发 `#62` 阻断的洞——
  `evidence_direction` 只被要求作为列存在，从未被要求**解析**，
  `linkage_class` 无约束，因此一次**完全合规**的执行产出了 168 条 RETAIN。
  缺陷记在 `#61` 名下，因为契约是在这里获批的。
- **`#66`**：保留了 `authorises_extraction_run_count` 无消费机制这条非阻断意见
  （**至今仍未解决**，已登记为 `v4-draft` 问题 16），以及 PR 内修掉一处 YAML
  引号缺陷、另三处作为无关改动未修（已登记为问题 17）。

## 五、本 PR 不做什么

不修改任何代码、契约、测试、Gate、lifecycle、core objects 或 target 轴；
不回写任何已获批准的历史文本；不修复记录中提到的任何缺陷；不解除任何缺口；
不执行任何抽取或外部运行；不新增任何 PR 之外的范围。

**只新增九个 `logs/` 文件、本 handoff 与一条 worklog。**

## 六、验证

```
Ran 413 tests  OK
scripts/verify_repository_boundary.sh   通过
git diff --check                        通过
九份记录的 PR 号／head／merge commit     对照 gh pr view 全部通过
```

## 七、这之后不再欠审核记录

补完这九份后，`#1` 至 `#73` 中所有已合并且需要记录的 PR 都有了在仓库内的批准
记录。后续每个 PR 应在合并后立即补登，避免再次积压。

由于审核方的 GitHub 连接器持续返回 `403`，**仓库内记录是唯一可长期引用的载体**
——这一点在 `#62`／`#63`／`#65`／`#66`／`#72` 上已反复出现，不是偶发。
