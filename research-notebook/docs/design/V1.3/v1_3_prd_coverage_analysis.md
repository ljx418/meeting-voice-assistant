# V1.3 PRD 覆盖度分析

日期：2026-05-26

## 读取范围声明

本次审计读取了 Stitch 项目：

```text
https://stitch.withgoogle.com/projects/5501162743214630907
```

Stitch connector 可读取项目元数据、screen 列表、PRD 文件元数据和 design theme，但当前环境未能下载到 PRD Markdown 正文。原始 PRD 文件访问快照已落盘：

```text
docs/design/external/2026-05-14-notebook-ai-product-prd.md
docs/design/external/stitch_project_5501162743214630907_snapshot.md
```

因此，本文件是基于可读取 Stitch 元数据、设计主题、screen 名称和当前本地实现文档的覆盖度分析；不是 PRD 原文逐句审计。拿到 PRD 正文后必须二次审计。

## 当前已完成的功能开发

| 模块 | 当前状态 | 说明 |
| --- | --- | --- |
| 工作区管理 | PASS | 支持创建、进入、归档测试 workspace，已被 V1.1/V1.2/V1.3 smoke 使用。 |
| 来源库 / 来源导入 | PASS_LIMITED | text/markdown/json 受限路径可用；PDF/PPTX/DOCX/video/audio/image 不声明原生正文摄入 ready。 |
| Source Preview | PASS | 来源预览抽屉可展示 source-level preview。 |
| DocumentUnit 导航 | PASS | 可列出 DocumentUnit、选择 unit、加载 unit detail。 |
| EvidenceSpan 高亮 | PASS_LIMITED | workspace/session text-source 证据路径、markdown/json 受限路径已通过 smoke。 |
| Source Trace | LIMITED_PASS | registry source_id-backed sources 的受限 trace 路径通过；不是 all-source-type trace ready。 |
| 多格式摄入 UI | PASS_LIMITED | V1.2 已完成 markdown/json browser smoke；传统手工验收按产品决策跳过。 |
| Agent Workflow 合同 | DISABLED_READY / PASS_LIMITED | V1.3-A 定义 DTO、adapter shell、disabled UI；后续阶段已接入 registered template。 |
| Local Folder Connector | PASS_LIMITED | 授权目录 dry-run manifest，md/txt 范围，relative_path-only，已在 `Desktop/技术分享` 路径验证。 |
| Workflow Runtime | PASS_LIMITED | `folder_summary_v1` deterministic runtime、step timeline、run report 可用。 |
| Folder Summary Artifact | PASS_LIMITED | confirmed md/txt run 可生成每个子文件夹 summary 和 root summary。 |
| Workflow UI | PASS_LIMITED | 工作区内可生成 draft、模拟运行、确认生成总结、查看 step timeline 和 artifact panel。 |
| Agent Planner | PASS_LIMITED | 只支持生成已注册 `folder_summary_v1` draft；不支持任意工具自由调用。 |
| Evidence-backed Summary | PASS_LIMITED | SummaryArtifact 的 `source_unit_span` citation 可回跳 SourcePreview / DocumentUnit / EvidenceSpan。 |
| ChromeCLI / Browser 验收 | PASS_LIMITED | V1.3-RC 通过 Agent 入口走通 `Desktop/技术分享` 受限路径。 |

## PRD 规格覆盖矩阵

| PRD 方向 / 可读规格 | 覆盖程度 | 当前实现证据 | 缺口 |
| --- | --- | --- | --- |
| AI 研究工作台 | PARTIAL | V1.1/V1.2/V1.3 已有工作区、来源库、问答、证据导航、Agent 工作流入口。 | 仍不是完整 Notebook 产品；任意 Agent、协作和治理未完成。 |
| 中文化研究界面 | PARTIAL | V1.3 主流程和文档已中文化；前端多数入口使用中文。 | 仍需全量 UI 文案巡检，清理残留版本号/英文开发态文案。 |
| 工作区主页 | PASS_LIMITED | `WorkspacePage` 集成来源库、Ask、AgentWorkflowPanel、SourcePreviewDrawer。 | 与 Stitch 设计稿的像素级还原未完整验收。 |
| 来源库 / 资料管理 | PASS_LIMITED | source create/list/get、preview、unit、evidence smoke 已覆盖。 | 多格式原生摄入和复杂资产管理未 ready。 |
| 来源预览 | PASS | SourcePreviewDrawer 已实现 source-level preview。 | 不代表 source trace、EvidenceSpan 或多格式 preview 全量 ready。 |
| 文档单元导航 | PASS | DocumentUnit list/detail、unit selection、active state 已实现。 | 仅限 data_service 支持的 source type。 |
| 证据级回跳 / 高亮 | PASS_LIMITED | EvidenceSpan detail、offset 高亮、workspace/session citation、summary citation 路径已 smoke。 | 不代表 all-source-type precise backjump。 |
| 工作区问答 | PASS_LIMITED | workspace query evidence 可回跳；session query 也完成受限路径。 | 未覆盖所有 session、所有来源类型、所有 query 形态。 |
| Agent 驱动工作流 | PASS_LIMITED | 用户可输入 folder-summary 目标，生成 registered workflow draft，确认后运行。 | 不是自由 Agent；不能任意规划和调用工具。 |
| 本地文件夹递归扫描 | PASS_LIMITED | Local Folder Connector 支持授权目录、dry_run、folder tree、skipped files、md/txt。 | 只支持 md/txt；不声明 PDF/PPTX/DOCX/video/audio/image。 |
| 每个子文件夹单独总结 | PASS_LIMITED | V1.3-D/RC 可生成 folder summary artifact 和 root summary。 | 总结质量、覆盖率、长文档规模和失败重试仍需更强验收。 |
| Summary citation 证据支撑 | PASS_LIMITED | `source_unit_span` citation 可打开 SourcePreviewDrawer 并高亮 EvidenceSpan。 | `relative_path_only` evidence 不能回跳；跨格式 citation 未 ready。 |
| 工作流调试 | PASS_LIMITED | step timeline、logs、run report、artifact panel 可见。 | 还不是完整 workflow debugger；缺少丰富断点、重跑单步、版本对比。 |
| 用户确认 / 权限授权 | PASS_LIMITED | V1.3 文档和 UI 均要求用户确认前不读取目录；folder scan 使用 permission/dry-run 模型。 | 浏览器级目录授权体验仍偏工程化。 |
| 低噪音 Productivity Intelligence 设计风格 | PARTIAL | 现有 UI 使用轻量面板、中文说明、抽屉和卡片结构。 | 未做与 Stitch design theme 的完整视觉差距审计；Roboto Flex、移动端 bottom sheet 未完整验证。 |
| 移动端适配 | UNKNOWN / PARTIAL | CSS 有响应式基础。 | 没有基于 PRD/Stitch 的移动端手工或浏览器 smoke。 |
| 图谱上下文 | PASS_LIMITED | 当前可展示只读图谱上下文或 unavailable state。 | Graph editing/governance 未 ready。 |
| Feedback | PASS_LIMITED | 轻量反馈入口/局部状态已有历史 smoke。 | 不是完整质量治理闭环。 |
| Assessment / Mastery | NOT_READY | 无。 | 需要单独产品阶段、合同、UI、验收。 |
| Quality / Governance Console | NOT_READY | 无。 | 需要单独产品阶段。 |
| Cloud Sync / Collaboration | NOT_READY | 无。 | 需要账户、权限、同步和协作合同。 |

## 总体覆盖判断

当前实现已经覆盖 PRD 可读方向中的核心研究链路：

```text
工作区 -> 来源 -> 预览 -> 文档单元 -> 证据高亮 -> Agent 文件夹总结工作流 -> Summary citation 回跳
```

但覆盖范围是受限的：

```text
authorized md/txt local folders
registered folder_summary_v1 workflow
data_service-supported text/markdown/json evidence paths
```

当前不能把项目声明为完整 Agent Notebook、完整多格式 Notebook、完整协作 Notebook 或完整治理平台。

## 风险评估

| 风险 | 等级 | 说明 | 建议 |
| --- | --- | --- | --- |
| PRD 正文不可读导致规格遗漏 | HIGH | 当前只拿到 PRD 元数据和 Stitch design theme，不能逐条核对原始 PRD。 | 导出 PRD Markdown 后二次审计。 |
| Agent ready 口径扩大 | MEDIUM | V1.3 已有 Agent 入口，容易被误解为自由 Agent。 | 所有文档继续使用 registered template / PASS_LIMITED。 |
| 多格式 ready 误判 | MEDIUM | V1.2 有 markdown/json smoke，V1.3 有文件夹扫描，但不代表 PDF/PPTX/DOCX/video/audio。 | 继续保持 NOT_READY，另开后端 extraction contract。 |
| 手工体验质量不足 | MEDIUM | ChromeCLI 验收通过，但真实用户授权、目录选择、调试体验仍偏工程化。 | 下一轮做 UX hardening，而不是扩大能力声明。 |
| 视觉与 Stitch 设计不一致 | MEDIUM | 当前未做像素级或布局级差距审计。 | 单独做 Stitch design parity audit。 |

## 建议下一步

1. 获取或上传 PRD 原文，执行逐条需求覆盖审计。
2. 做一次 Stitch design parity audit，重点检查工作区主页、Agent 入口、来源预览抽屉、workflow timeline。
3. 继续在不扩大 ready 声明的前提下做 UX hardening：目录授权体验、运行态反馈、summary 阅读/复制/导出。
4. 若要继续能力扩展，优先补多格式 extraction backend contract，而不是在前端伪造解析。

## PRD 对齐改造记录

2026-05-26 已新增 PRD 对齐改造计划和验收报告：

```text
docs/design/V1.3/v1_3_prd_alignment_plan.md
docs/design/V1.3/v1_3_prd_alignment_acceptance_report.md
```

本轮已处理：

- Agent 入口从开发态“Agent 工作流 / 阶段状态”调整为用户任务导向的“文件夹总结工作流”。
- 用户可见的 `PASS_LIMITED`、`NOT_READY`、阶段编号等工程态表达从 Agent 主流程移除。
- Summary citation 区分“可打开原文定位”和“仅显示文件路径”。
- 来源预览抽屉中的技术字段改为中文产品表达。
