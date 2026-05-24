# ResearchNotebook V1.1-S3 Multi-Format Backend Contract Readiness

文档状态：S3 backend contract enablement 已完成第一批格式；范围仅限 `markdown` 和 `json`。
日期：2026-05-24。

## 结论

S3 不是前端多格式 UI 阶段。本阶段只验证 `data_service` 是否能为非纯文本格式提供稳定后端合同。

当前可声明：

```text
data_service multi-format backend contract is API-smoke-ready for markdown and json sources.
```

当前不能声明：

```text
ResearchNotebook multi-format frontend is ready.
PDF/PPTX/video/audio/html ingestion is ready.
all-source-type precise backjump is ready.
```

## 验证命令

后端 focused tests：

```text
python3 -m pytest tests/test_target_http_source_preview.py tests/test_target_http_document_units.py tests/test_target_http_evidence_spans.py tests/test_target_http_multi_format.py -q
```

结果：

```text
20 passed
```

ResearchNotebook 真实 HTTP smoke：

```text
npm run smoke:v1.1-s3-multiformat
```

结果：

```text
S3_MULTI_FORMAT_BACKEND_DECISION READY_MARKDOWN_JSON
```

## 合同状态

Capability manifest 当前声明：

```text
text: unit
markdown: unit
json: unit
```

`markdown` 后端合同：

- source preview: PASS
- DocumentUnit list/detail: PASS
- workspace query evidence ids: PASS
- EvidenceSpan detail: PASS
- content_type: `text/markdown`
- locator: offset

`json` 后端合同：

- source preview: PASS
- DocumentUnit list/detail: PASS
- workspace query evidence ids: PASS
- EvidenceSpan detail: PASS
- unit_type: `json_node`
- locator: `json_path`

仍未就绪：

- PDF native ingestion / preview / units / evidence
- PPTX native ingestion / preview / units / evidence
- HTML native ingestion / preview / units / evidence
- video/audio transcript ingestion / preview / units / evidence

## Smoke 证据

workspace:

```text
rn-v11-s3-multiformat-1779595456314-workspace
```

markdown:

```text
source_id: src_1101fe581e2adfbf
unit_id: unit_0a09dca106df27fe
evidence_id: ev_36addc38d2a2aae9
```

json:

```text
source_id: src_87b95b9c07184aaa
unit_id: unit_ed42c82daf11f1bd
evidence_id: ev_bbeec37ecd14c0d8
```

fixtures:

```text
fixtures/real/v1_1/multi-format-backend/
```

保存内容：

- capability manifest
- markdown source create / preview / units / unit detail / query evidence / EvidenceSpan
- json source create / preview / units / unit detail / query evidence / EvidenceSpan
- S3 summary result

fixtures 已脱敏；不得包含 raw filesystem path、cache path、artifact physical path、stack trace 或私有内容。

## 已接受的边界

S3 smoke 中 workspace query payload 仍可能包含既有 GraphRAG engine payload 字段，例如内部 db path。S3 smoke 的 raw-path 断言已收窄到本阶段合同面：

- source create response
- source preview response
- DocumentUnit list/detail response
- query evidence items
- EvidenceSpan response

该既有 GraphRAG payload 泄漏风险不属于 markdown/json preview/unit/evidence 合同本身，但仍应在后续 hardening 中单独处理。

## 下一阶段审计

S3 完成后，不能直接声明多格式前端 ready。正确下一阶段是：

```text
V1.1-S4 Multi-Format Frontend Integration for Markdown/JSON
```

S4 目标：

- 前端读取 capability manifest 中的 `markdown/json` 支持状态；
- Source Library / Source Detail 对 markdown/json 启用 Preview；
- Source Preview Drawer 安全渲染 markdown/json source-level preview；
- DocumentUnit outline 显示 markdown sections 和 json_node units；
- EvidenceSpan highlight 对 markdown/json 可解析 citation 做浏览器 smoke；
- 不增加前端 parser；
- 不把 HTML/Markdown 当 HTML 渲染；
- 不声明 PDF/PPTX/video/audio ready。

## 仍然 NOT_READY

- all-source-type precise backjump
- all-source-type source trace
- native PDF/PPTX/video/audio ingestion
- frontend markdown/json browser-ready
- Assessment / Mastery
- Quality/Governance console
- Graph editing/governance
- Cloud sync/collaboration
