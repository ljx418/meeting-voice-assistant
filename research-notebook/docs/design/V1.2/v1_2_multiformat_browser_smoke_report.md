# ResearchNotebook V1.2 Markdown/JSON Browser Smoke Report

文档状态：PASS。

## Environment

| 项目 | 值 |
| --- | --- |
| frontend URL | `http://127.0.0.1:5173` |
| data_service URL | `http://127.0.0.1:8003` |
| command | `npm run smoke:v1.2-multiformat-browser` |
| timestamp | 2026-05-24 |
| frontend commit / branch | `7c2bc4fb` / `main` |
| fixture | `fixtures/real/v1_2/multiformat/v1_2-multiformat-browser-result.json` |

## Smoke Matrix

| 项目 | 状态 | 备注 |
| --- | --- | --- |
| Browser startup | PASS | 页面非空白，无阻塞 console/pageerror。 |
| Workspace create/archive | PASS | `rn-v12-multiformat-1779609883023-workspace` 已归档 cleanup。 |
| Markdown import | PASS | source appears in Source Library。 |
| Markdown Preview/Unit | PASS | Drawer、DocumentUnit、unit detail 可见。 |
| Markdown EvidenceSpan highlight | PASS | `v12markdownanchor evidence should be highlighted from markdown source.` |
| JSON import | PASS | source appears in Source Library。 |
| JSON Preview/Unit | PASS | Drawer、DocumentUnit、unit detail 可见。 |
| JSON EvidenceSpan highlight | PASS | JSON 文本被 escaped 渲染并高亮。 |
| forbidden route guard | PASS | 未观察到 `/api/v1/knowledge/*`。 |
| fixtures saved | PASS | `fixtures/real/v1_2/multiformat/`。 |

## Declaration Decision

当前可以声明：

```text
ResearchNotebook V1.2 markdown/json multi-format evidence navigation is browser-smoke-ready for data_service-supported markdown/json workspace query citations carrying source_id + unit_id + evidence_id.
```

仍不能声明 PDF/PPTX/HTML/video/audio ready。
