# StelligenOS Manuscript

本目录把 StelligenOS 的架构、实现和验证路线组织为一篇可审计、可持续迭代的论文。论文是项目的学术锚点，**不是新的架构权威来源**；发生冲突时，仍以 `docs/architecture/` 下的正式契约为准。

## 边界

允许进入本目录的内容：

- Markdown、LaTeX、BibTeX 等论文源文件；
- 小型、可追溯的引用元数据和图表源代码；
- PaperSpine 的配置、研究记录、claim register、审计报告和进度文件；
- 指向仓库外验证材料的路径、摘要和校验信息。

禁止进入本目录的内容：

- 数据集、原始数据、分析中间文件、缓存、模型权重和运行目录；
- 由真实数据产生的 data-bearing working files；
- LaTeX 临时文件和其他构建缓存；
- PDF、DOCX 等生成性交付物，除非未来通过独立架构变更明确授权。

PDF/DOCX 必须在仓库外部工作区构建。本仓库只记录构建命令、外部路径、摘要、校验值和验证结论。

## 当前工作流

- 工作流：从仓库材料构筑期刊论文；
- 主稿语言：英文；
- 中文完整翻译包：计划生成；
- 目标期刊：待研究后确定；
- 当前阶段：Manuscript Phase 0（framing and evidence contract）；
- PaperSpine 状态：intake 已完成，下一关为 research；
- 审核状态：等待本阶段 PR 和 ChatGPT `APPROVE`，批准前不得开始 research。

配置和进度见 `paper_rewriting_output/`。总体阶段与论文边界见 `MANUSCRIPT_CHARTER.zh-CN.md`。
