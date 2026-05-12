# Data Service V1.6 Development Plan

更新时间：2026-05-12

## Summary

V1.6 从 V1.5 accepted baseline 出发，按最小能力组推进。每个阶段完成后必须做端到端出门验证、公开面扫描和文档同步。

## Phase V1.6-A: Public Surface Guard

目标：把 V1.5 closure audit 转成可重复的阶段护栏。

交付：

- MCP registry count guard。
- CLI top-level command guard。
- HTTP route inventory guard。
- target HTTP route allowlist guard。
- `/api/v1/knowledge/*` compatibility retention check。

验收：

- MCP baseline remains 40 unless phase explicitly opens a tool。
- target HTTP baseline starts from exactly 3 routes。
- no hidden route/tool/command expansion。

## Phase V1.6-B: Lifecycle Target HTTP

目标：为 workspace/source/build lifecycle 设计并分阶段开放 target HTTP write routes。

交付：

- workspace target HTTP write contract。
- source target HTTP write contract。
- build target HTTP write contract。
- operation envelope consistency tests。

验收：

- new routes use `workspace_id` / `source_id` / `operation_id`。
- no internal path/layout as stable contract。
- compatibility HTTP remains retained。

## Phase V1.6-C: Graph Advanced Minimal Surface

目标：不新增 V1.5 已存在的 MCP graph tools；按最小子能力开放尚未开放的 graph advanced target HTTP / CLI surfaces。

候选顺序：

- graph neighbors target HTTP / CLI surface where not yet open
- graph community target HTTP / CLI surface where not yet open
- graph query target HTTP / CLI surface where not yet open
- graph session target HTTP / CLI surface where not yet open

验收：

- each subcommand or route has its own contract test。
- `snapshot` behavior remains compatible。
- GraphRAG internals stay behind `app.graphrag.service`。

## Phase V1.6-D: Session GraphRAG Public Contract

目标：不新增 V1.5 已存在的 MCP session tools；固化 Session GraphRAG 跨 MCP / CLI / HTTP / target HTTP 的稳定外部 contract。

交付：

- session graph request / response schema。
- session operation lifecycle envelope。
- session trace / artifact reference rules。

验收：

- uses `session_id` and `operation_id` as stable IDs。
- no dependency on upper-layer meeting or ASR modules。
- internal session storage paths remain debug-only。

## Phase V1.6-E: Quality Target HTTP Write Routes

目标：把 quality write 能力迁移到 target HTTP，而不是扩大旧 compatibility route。

交付：

- quality feedback target route contract。
- correction rules / review target route contract。
- correction plan target route contract。

验收：

- non-destructive governance semantics retained。
- shared helper reused。
- compatibility HTTP remains retained。

## Phase V1.6-F: Console Governance Polish

目标：让 `/knowledge` 更清楚地呈现服务治理状态和 V1.6 contract evidence。

交付：

- public surface baseline view。
- target HTTP migration state view。
- graph/session/quality contract evidence view。

验收：

- frontend build passes。
- screenshot acceptance passes。
- page remains governance console, not end-user knowledge app。
