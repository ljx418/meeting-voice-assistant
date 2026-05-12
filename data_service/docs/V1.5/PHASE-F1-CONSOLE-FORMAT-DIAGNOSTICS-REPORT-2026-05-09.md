# PhaseF1 Console Format Diagnostics Report

日期：2026-05-09

## 目标

进入 PhaseF 控制台产品化首段，把 PhaseE2 已经产出的 format diagnostics 显示到 `/knowledge` 控制台，避免治理字段只停留在 JSON payload 中。

## 已完成

- Overview 指标栏新增 `Formats` 指标，展示当前 workspace 的格式数量和主要格式。
- Source 台账新增 format / extractor chips。
- 当前 Source 工作流新增 Format 与 Extractor 状态卡。
- Distill Detail 顶部 pills 显示当前 source 的 format / extractor。
- Distill Quality 新增：
  - `Format Diagnostics`
  - `format_counts`
  - `extractor_counts`
  - `format_issue_sources`
- TypeScript `KnowledgeSourceRecord` 补齐 `source_format`、`extractor_name`、`extractor_available`。
- Vite 构建产物已输出到 `backend/app/static/knowledge_console`。

## 出门验证

```bash
npm run build
```

结果：通过；生成：

- `backend/app/static/knowledge_console/index.html`
- `backend/app/static/knowledge_console/assets/index-CsIWnFa_.css`
- `backend/app/static/knowledge_console/assets/index-n1AtCuir.js`

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：`103 passed`。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI 参数。
- 只消费既有 `/summary`、`/distill`、`/sources/list` 响应中的附加治理字段。
- 静态控制台产物更新，不改变 API contract。

## 下一步

继续 PhaseF2：补控制台 build/source/quality 的更清晰工作流态势，特别是 failed/unreadable/low-signal drilldown 和 MCP Debugger 入口。
