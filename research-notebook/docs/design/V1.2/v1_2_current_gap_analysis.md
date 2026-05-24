# ResearchNotebook V1.2 当前差距分析

文档状态：V1.2-A baseline 已建立；V1.2-B 多格式摄入 UI 产品化已接入；V1.2-C markdown/json browser smoke 已通过；V1.2-D 手工验收与最终同步待执行。
配套图：`v1_2_current_gap_analysis.drawio`。

## 一句话结论

V1.2 的目标不是扩大到所有格式，而是把已经通过 V1.1-S3/S4 证明的 `markdown/json` 路径整理成清晰、可验收的产品化体验：

```text
选择格式 -> 导入 Markdown/JSON -> 预览 -> 文档单元 -> 引用点击 -> EvidenceSpan 高亮
```

当前仍不能声明 PDF、PPTX、HTML、video、audio 的 ingestion ready。

## 当前状态

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| V1.2-A Final V1.1 Sync and Baseline | PASS | V1.1-B/C/D、S1、S3/S4 文档和脚本作为 V1.2 基线。 |
| V1.2-B Multi-Format Ingestion UX Contract | PASS | 导入表单改为明确格式选择；text/markdown/json 标为已验证，其他格式标为后端合同待就绪。 |
| V1.2-C Markdown/JSON Product Smoke | PASS | `npm run smoke:v1.2-multiformat-browser` 已通过；markdown/json 均完成浏览器路径。 |
| V1.2-D Manual Acceptance and Release Sync | NOT_STARTED | 等 V1.2-C 结果后更新手工验收和最终同步文档。 |

## 当前可声明

- V1.1 文本源 Source Preview、DocumentUnit、EvidenceSpan、session precision、source trace scoped path 保持原声明。
- markdown/json 第一批多格式路径已有 V1.1-S3/S4 smoke 证据，并已通过 V1.2 浏览器 smoke 复验。
- UI 已避免让用户误以为 PDF/PPTX/HTML/video/audio 已 ready。

## 仍不能声明

| 能力 | 状态 | 原因 |
| --- | --- | --- |
| PDF ingestion ready | NOT_READY | 需要后端合同、fixtures、API smoke、browser smoke。 |
| PPTX ingestion ready | NOT_READY | 需要后端合同、fixtures、API smoke、browser smoke。 |
| HTML ingestion ready | NOT_READY | 需要 sanitizer/escaped rendering 决策和 smoke。 |
| video/audio ingestion ready | NOT_READY | 需要 transcript unit、timestamp locator、EvidenceSpan 合同。 |
| all-source-type precise backjump ready | NOT_READY | 当前只覆盖 text、markdown、json 的受限路径。 |
| Assessment / Mastery | NOT_READY | 不在 V1.2 当前切片。 |
| Quality/Governance console | NOT_READY | 不在 V1.2 当前切片。 |
| Graph editing/governance | NOT_READY | 不在 V1.2 当前切片。 |
| Cloud sync/collaboration | NOT_READY | 不在 V1.2 当前切片。 |

## 剩余开发阶段

| 阶段 | 目标 | 完成条件 |
| --- | --- | --- |
| V1.2-C | 跑通 markdown/json 真实浏览器产品 smoke | 已完成：`npm run smoke:v1.2-multiformat-browser` 通过，fixtures 已保存。 |
| V1.2-D | 手工验收与最终同步 | 待执行：手工验收报告落盘，`npm run check` 通过，文档和 scoped commit/push 完成。 |

## No False Green 规则

- Markdown/JSON 成功不代表 PDF/PPTX/HTML/video/audio 成功。
- Source Preview 成功不代表 EvidenceSpan 高亮成功。
- EvidenceSpan 高亮成功不代表 all-source-type precise backjump ready。
- artifact_ref 永远不能解析成本地路径。
- feature 层不能直接拼后端 route 或直接 fetch。
- markdown/html 后端内容不能通过 `dangerouslySetInnerHTML` 渲染。
