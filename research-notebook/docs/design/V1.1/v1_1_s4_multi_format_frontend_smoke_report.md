# ResearchNotebook V1.1-S4 Multi-Format Frontend Smoke Report

文档状态：S4 markdown/json frontend browser smoke passed。
日期：2026-05-24。

## 结论

S4 验证 ResearchNotebook 前端能消费 S3 已启用的 `markdown/json` 后端合同。

当前可声明：

```text
ResearchNotebook markdown/json source preview, DocumentUnit navigation, and EvidenceSpan highlight are browser-smoke-ready for data_service-supported markdown/json workspace query citations carrying source_id + unit_id + evidence_id.
```

当前仍不能声明：

```text
all-source-type precise backjump ready
native PDF/PPTX/HTML/video/audio ingestion ready
```

## 验证命令

```text
npm run smoke:v1.1-s4-multiformat-browser
```

结果：

```text
S4_MULTI_FORMAT_FRONTEND_DECISION BROWSER_SMOKE_READY_MARKDOWN_JSON
```

## 环境

| 项目 | 值 |
| --- | --- |
| frontend URL | `http://127.0.0.1:5173` |
| data_service URL | `http://127.0.0.1:8003` |
| workspace_id | `rn-v11-s4-multiformat-1779596647207-workspace` |
| fixture | `fixtures/real/v1_1/multi-format-frontend/s4-multiformat-browser-result.json` |
| artifacts | `.smoke-artifacts/v1_1_s4_multiformat/1779596647207/` |

## Markdown 验收

| 检查项 | 状态 |
| --- | --- |
| source import visible | PASS |
| Preview button enabled by manifest | PASS |
| Source Preview Drawer opens | PASS |
| Document Units visible | PASS |
| first unit selectable | PASS |
| workspace query citation jumpable | PASS |
| EvidenceSpan highlight visible | PASS |
| no `/api/v1/knowledge/*` request | PASS |

Observed ids:

```text
source_id: src_ffd1451b13d29307
unit_id: unit_f67bdc0820ab5be5
evidence_id: ev_3e591290d26844a3
```

Highlight:

```text
s4markdownanchor evidence should be highlighted from markdown source.
```

Markdown remains escaped text. No frontend markdown parser was added.

## JSON 验收

| 检查项 | 状态 |
| --- | --- |
| source import visible | PASS |
| Preview button enabled by manifest | PASS |
| Source Preview Drawer opens | PASS |
| json_node Document Units visible | PASS |
| first json unit selectable | PASS |
| workspace query citation jumpable | PASS |
| EvidenceSpan highlight visible | PASS |
| no `/api/v1/knowledge/*` request | PASS |

Observed ids:

```text
source_id: src_0324c4496a30d6e0
unit_id: unit_986ae315e1c1dadf
evidence_id: ev_8efcb16f0f6aea1d
```

Highlight:

```text
{"summary":"s4jsonanchor evidence should be highlighted from json source","status":"supported"}
```

JSON remains escaped text. No frontend JSON parser was added.

## 已接受的浏览器日志

Headless Chrome emitted platform-level stderr messages:

```text
CVDisplayLinkCreateWithCGDisplay failed
PHONE_REGISTRATION_ERROR
Trying to load the allocator multiple times
```

这些不是 page console error，也没有进入 smoke 的 `consoleErrors` / `pageErrors`。Browser guard 结果为 PASS。

## 边界

- S4 只覆盖 `markdown/json` workspace query citation path。
- S4 不覆盖 session query markdown/json path。
- S4 不覆盖 PDF/PPTX/HTML/video/audio。
- S4 不代表 native multi-format ingestion ready。
- S4 不代表 all-source-type precise backjump ready。
- `artifact_ref` 仍只作为 metadata，不解析成本地路径。
- 不新增 frontend parser。
- 不使用 `dangerouslySetInnerHTML`。

## 下一阶段审计

S4 完成后，V1.1 功能开发范围内还剩：

```text
V1.1-FINAL Final Manual Acceptance / Repository Sync
```

FINAL 阶段只做：

- 汇总 B/C/D/RC/S1/S3/S4 验收证据；
- 更新 gap / drawio / checklist；
- 复跑 check 和必要 smoke；
- scoped commit / push。

FINAL 阶段不得新增业务功能，也不得把 markdown/json browser smoke 扩大为 all-source-type ready。
