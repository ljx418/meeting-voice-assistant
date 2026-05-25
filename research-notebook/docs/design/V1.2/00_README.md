# ResearchNotebook V1.2 设计文档索引

文档状态：V1.2-A/B 已完成基线整理和多格式摄入产品化壳层；V1.2-C markdown/json 浏览器 smoke 已通过；V1.2-D 手工验收按产品决策跳过，最终验收迁移到 V1.3 Agent 入口。
日期：2026-05-24。

## V1.2 目标

V1.2 只在 V1.1 已完成的证据导航链路上做第一批多格式产品化：

```text
Markdown / JSON 来源 -> Preview -> DocumentUnit -> workspace citation -> EvidenceSpan 高亮
```

V1.2 不进入 Assessment、Quality/Governance console、Graph editing/governance、Cloud sync/collaboration。

## Product Decision

V1.2 不再补传统手工验收体验。当前来源库/导入/问答 UI 的手工体验不足以作为最终验收入口，最终用户验收迁移到 V1.3 Agent Workflow：

```text
用户输入目标 -> Agent 生成 workflow draft -> 用户授权 -> 运行 -> 子文件夹总结 -> evidence citation 回跳
```

V1.2 保留为 V1.3 的技术基线，不再扩大产品 ready 声明。

## 当前边界

- text 路径继承 V1.1 browser-smoke-ready 结果。
- markdown/json 已在 V1.1-S3/S4 通过后端/API 和前端浏览器 smoke，V1.2 将其整理为用户可见的第一批多格式基线。
- PDF/PPTX/HTML/video/audio 仍是后端合同待就绪，不得声明 ready。
- artifact_ref 仍只作为 metadata 展示，不解析成本地路径。
- markdown/html 内容仍按 escaped text 渲染，不使用危险 HTML 注入。

## 文档清单

| 文件 | 用途 |
| --- | --- |
| `v1_2_current_gap_analysis.md` | V1.2 当前状态、剩余阶段和声明边界。 |
| `v1_2_current_gap_analysis.drawio` | V1.2 阶段与 NOT_READY 边界可视化。 |
| `feature-route-matrix.md` | V1.2 多格式 route / capability / UI 状态矩阵。 |
| `v1_2_release_readiness_checklist.md` | V1.2 发布前命令、smoke、文档和边界检查清单。 |
| `v1_2_multiformat_browser_smoke_report.md` | V1.2 markdown/json 浏览器 smoke 报告，当前为 PASS。 |
| `v1_2_manual_acceptance_report.md` | V1.2 手工验收跳过记录；指向 V1.3 Agent 验收。 |
| `v1_2_final_release_sync.md` | V1.2 最终同步和提交范围记录。 |
| `tech_share_manual_import_report.md` | 技术分享目录 Chrome CLI 导入探索报告；作为 V1.3 Agent 验收问题证据，不作为 V1.2 最终验收。 |
