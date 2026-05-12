# Build CLI Contract

更新时间：2026-05-12

## 定位

PhaseG21 开放 `knowledge build status` 的只读 alias，作为 build operation 目标 CLI 的最小阶段。

PhaseG27 已开放 `knowledge build start/cancel` 写入型治理 alias。本阶段不新增 MCP tool，不新增 HTTP route；CLI 只转调现有 MCP build handler，复用 operation envelope、operation_id lifecycle 和 no-internal-path sanitizer。

## 当前开放命令

```text
knowledge build start --workspace-root ./workspaces --workspace-id research-vault --mode full
knowledge build status --workspace-root ./workspaces --workspace-id research-vault --operation-id op_123
knowledge build cancel --workspace-root ./workspaces --workspace-id research-vault --operation-id op_123 --reason manual-stop
```

## 约束

- `knowledge build start/status/cancel` 必须复用 `knowledge_build_start/status/cancel` 的 handler。
- 不新增 MCP tool 或 HTTP route。
- 不改变现有 MCP `knowledge_build_*` 和 HTTP `/api/v1/knowledge/build/*` contract。
- 输出仍使用 MCP envelope 形态：`workspace_id`、`operation_id`、`status`、`warnings`、`artifact_refs`、`next_actions`、`data`。
- operation data 稳定字段保持 `mode`、`stage`、`progress`、`error`、`retryable`、`artifact_refs` / `debug_paths`。
- `start` 仅开放现有 MCP build mode：`full`、`incremental`、`graph_only`、`llmwiki_only`。
- `cancel` 保持既有 soft cancel 语义，不删除 operation artifact。

## 漂移测试要求

- `_build_knowledge_parser()` 顶层 choices 当前必须严格等于 `{"quality", "query", "workspace", "source", "build", "graph", "trace"}`。
- `knowledge build` 子命令当前必须严格等于 `{"start", "status", "cancel"}`。
- E2E 必须调用 `knowledge_main(["build", "start", ...])`、`knowledge_main(["build", "status", ...])` 和 `knowledge_main(["build", "cancel", ...])`。
- E2E 必须验证 CLI alias 调用 `handle_build_tool`，且 handler name 为 `knowledge_build_start`、`knowledge_build_status`、`knowledge_build_cancel`。
