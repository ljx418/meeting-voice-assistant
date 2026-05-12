# PhaseG24-G31 Remaining Development Plan

日期：2026-05-12

## 目标形态

Data Service 的目标形态是 MCP-first 的本地知识治理微服务，而不是终端用户知识消费 App。

目标架构：

```text
External Apps / Agents / CLI / Console
  -> MCP primary contract
  -> CLI: knowledge ...
  -> HTTP: /api/workspaces/{workspace_id}/...
  -> data_service
     - workspace/source/build lifecycle orchestration
     - query/distill/trace/quality shared contracts
     - operation/envelope/error contract
  -> app.llmwiki
     - readable wiki artifacts
  -> app.graphrag.service
     - GraphRAG / session graph / relation extraction
  -> Local Workspace Store
     - internal layout only
```

目标原则：

- MCP 是默认主入口。
- CLI 和 HTTP 必须复用同一 service contract 或现有 MCP handler。
- `data_service` 保留为当前实现层和兼容入口。
- 外部只依赖 `workspace_id`、`source_id`、`session_id`、`operation_id`、`artifact_ref` 等稳定字段。
- 内部 path、workspace layout 只允许作为 debug / console 信息，不成为外部 contract。
- `/knowledge` 是服务治理控制台。
- GraphRAG 算法能力继续由 `app.graphrag.service` 承载，`data_service` 不重新成为图算法大类。

## 当前状态

截至 PhaseG30：

- `knowledge quality ...` 已开放。
- `knowledge query ...` 已开放。
- `knowledge workspace list/describe` 已开放。
- `knowledge source list` 已开放。
- `knowledge build status` 已开放。
- `knowledge graph snapshot` 已开放。
- `knowledge trace source` 已开放。
- `knowledge workspace create/archive` 已开放。
- `knowledge source import/remove` 已开放。
- `knowledge build start/cancel` 已开放。
- MCP `knowledge_distill_preview` 已开放。
- MCP `knowledge_source_trace` 已开放。
- 首批新 HTTP `/api/workspaces/{workspace_id}/...` 已开放：query / distill / source trace。

仍未开放：

- `knowledge graph neighbors/community/query/session`
- workspace/source/build 写入型目标 HTTP route
- graph advanced 目标 HTTP route
- quality 写入型目标 HTTP route
- session 目标 HTTP route

## 后续阶段计划

### PhaseG24：Graph advanced CLI 迁移窗口

目标：评估 `knowledge graph` advanced 子命令是否进入 CLI。

候选范围：

- `knowledge graph neighbors`
- `knowledge graph community`
- `knowledge graph query`
- `knowledge graph session`

交付标准：

- 先固化 graph advanced CLI contract 和迁移窗口。
- 不一次性开放全部 advanced 子命令。
- 不新增 MCP tool 或 HTTP route。
- 明确每个子命令复用现有 handler / service 的路径。
- 完成 drift tests、drawio/md 同步和端到端出门验证。

### PhaseG25：Workspace write CLI contract

目标：评估 `knowledge workspace create/archive`。

交付标准：

- 只复用 `knowledge_workspace_create` / `knowledge_workspace_archive` handler。
- 不新增 MCP tool 或 HTTP route。
- archived workspace 写保护、envelope、debug_paths contract 不变。
- 完成 read/write lifecycle E2E 和对外能力扫描。

### PhaseG26：Source write CLI contract

目标：开放 `knowledge source import/remove`。当前状态：已完成。

交付标准：

- 只复用 `knowledge_source_import` / `knowledge_source_remove` handler。
- 不新增 MCP tool 或 HTTP route。
- 保持 source registry、duplicate、removed、low_signal、ingest_status contract。
- 完成 source import/remove/list E2E 和对外能力扫描。

### PhaseG27：Build write CLI contract

目标：开放 `knowledge build start/cancel`。当前状态：已完成。

交付标准：

- 只复用 `knowledge_build_start` / `knowledge_build_cancel` handler。
- 不新增 MCP tool 或 HTTP route。
- 保持 operation_id lifecycle、queue、cancel、interrupted 和 error code contract。
- 完成 start/status/cancel E2E 和对外能力扫描。

### PhaseG28：MCP distill preview

目标：开放 MCP `knowledge_distill_preview`。当前状态：已完成。

交付标准：

- 必须复用 `run_distill_contract`。
- 不改变 HTTP `/api/v1/knowledge/distill` 和 `data_service distill` 字段集合。
- 补齐 MCP schema、registry、dispatcher 和 E2E。
- 完成 MCP/API/CLI 三入口 payload 一致性验证。

### PhaseG29：MCP source trace

目标：开放 MCP `knowledge_source_trace`。当前状态：已完成。

交付标准：

- 必须复用 `source_trace_payload`。
- 不改变 HTTP `/api/v1/knowledge/source/trace` 和 `knowledge trace source` 字段集合。
- MCP request 以 `workspace_id / source_id / limit` 为稳定目标字段；`workspace` path 仅用于兼容和本地测试。
- 完成 MCP/HTTP/CLI 三入口 payload 一致性验证。

### PhaseG30：目标 HTTP route 设计

目标：设计并开放 `/api/workspaces/{workspace_id}/...` 首批目标 HTTP route。当前状态：已完成。

交付标准：

- 先文档化目标 route 和兼容窗口。
- 首批只开放 query / distill / source trace 三个共享 contract 已成熟的能力。
- 旧 `/api/v1/knowledge/*` 不直接废弃。
- 不破坏当前控制台和旧客户端。
- 明确 route 与 MCP / CLI shared contract 的复用关系。
- 完成 route drift tests 和兼容入口回归。

### PhaseG31：V1.5 收口验收

目标：完成 V1.5 最终收口。当前状态：已完成，closure status accepted。

交付标准：

- 全量后端回归通过。
- 前端 build 通过。
- 必要前端截图验收通过。
- MCP registry / HTTP routes / CLI parser 公开面扫描通过。
- `current-vs-target-gap.md`、`current-vs-target-gap.drawio`、`data-service-v1.5-roadmap.drawio` 信息一致。
- 形成 V1.5 总结报告，明确 V1.6 候选范围。

## 最小闭环版本

PhaseG24、PhaseG25、PhaseG26、PhaseG27、PhaseG28、PhaseG29 与 PhaseG30 已完成后，如果需要缩短 V1.5 收口，可以合并剩余阶段：

- PhaseG31：V1.5 最终收口。

默认仍建议按 G24-G31 拆分，便于每个子阶段完成独立端到端出门验证。
