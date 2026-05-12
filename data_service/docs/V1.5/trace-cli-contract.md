# Trace CLI Contract

更新时间：2026-05-12

## 定位

PhaseG23 开放 `knowledge trace source` 的只读 alias，作为 Source Trace 目标 CLI 的最小阶段。

PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放 target HTTP `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`。CLI 只复用 `source_trace_payload` shared serializer，输出与当前 HTTP `/api/v1/knowledge/source/trace`、target HTTP 和 MCP `knowledge_source_trace` 保持同字段。

## 当前开放命令

```text
knowledge trace source --workspace-root ./workspaces --workspace-id research-vault --source-id source-123 --limit 12
```

## 约束

- `knowledge trace source` 必须复用 `source_trace_payload`。
- `knowledge_source_trace` MCP tool 已在 PhaseG29 开放，并必须复用 `source_trace_payload`。
- PhaseG23 CLI 阶段不新增 HTTP route；PhaseG30 后 target HTTP trace route 已开放。
- 不改变现有 HTTP `/api/v1/knowledge/source/trace` contract。
- 不改变 target HTTP `/api/workspaces/{workspace_id}/sources/{source_id}/trace` contract。
- 不改变 `data_service` 兼容 CLI 顶层命令。
- 输出稳定字段保持 `workspace`、`source_id`、`source`、`distill`、`llmwiki`、`graphrag`、`trace_summary`。
- `limit` 仍固定为 1-50，默认 12。

## 漂移测试要求

- `_build_knowledge_parser()` 顶层 choices 当前必须严格等于 `{"quality", "query", "workspace", "source", "build", "graph", "trace"}`。
- `knowledge trace` 子命令当前必须严格等于 `{"source"}`。
- `data_service` 兼容 CLI 顶层 choices 不得新增 `trace`。
- E2E 必须调用 `knowledge_main(["trace", "source", ...])`。
- E2E 必须验证 CLI alias 调用 `source_trace_payload`。
