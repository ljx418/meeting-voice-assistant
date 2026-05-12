# Workspace CLI Contract

更新时间：2026-05-12

## 定位

PhaseG19 开放 `knowledge workspace` 的只读 alias，作为 workspace lifecycle 目标 CLI 的最小阶段。PhaseG25 开放 `knowledge workspace create/archive` 写入型治理 alias。

本阶段不新增 MCP tool，不新增 HTTP route。CLI 只转调现有 MCP workspace handler，复用 workspace envelope、artifact_ref/debug_paths 分层和 no-internal-path sanitizer。

## 当前开放命令

```text
knowledge workspace create --workspace-root ./workspaces --name "Research Vault" --owner harness --tag project
knowledge workspace list --workspace-root ./workspaces --owner harness --limit 50
knowledge workspace describe --workspace-root ./workspaces --workspace-id research-vault
knowledge workspace describe --workspace /absolute/path/to/workspace
knowledge workspace archive --workspace-root ./workspaces --workspace-id research-vault --reason "done"
```

## 约束

- `knowledge workspace create` 必须复用 `knowledge_workspace_create` 的 handler。
- `knowledge workspace list` 必须复用 `knowledge_workspace_list` 的 handler。
- `knowledge workspace describe` 必须复用 `knowledge_workspace_describe` 的 handler。
- `knowledge workspace archive` 必须复用 `knowledge_workspace_archive` 的 handler。
- 不新增 MCP tool 或 HTTP route。
- 不改变现有 MCP `knowledge_workspace_*` 和 HTTP `/api/v1/knowledge/workspaces/*` contract。
- 输出仍使用 MCP envelope 形态：`workspace_id`、`operation_id`、`status`、`warnings`、`artifact_refs`、`next_actions`、`data`。
- 内部路径只允许出现在 `debug_paths` 或 `artifact_refs[].debug_path`，不能作为稳定字段暴露。
- archive 后 workspace status 必须进入 `archived`，后续写入型 source/build 行为仍由现有 handler 的 archived write-protection 负责。

## 漂移测试要求

- `_build_knowledge_parser()` 顶层 choices 当前必须严格等于 `{"quality", "query", "workspace", "source", "build", "graph", "trace"}`。
- `knowledge workspace` 子命令当前必须严格等于 `{"create", "list", "describe", "archive"}`。
- E2E 必须调用 `knowledge_main(["workspace", "create", ...])`、`knowledge_main(["workspace", "list", ...])`、`knowledge_main(["workspace", "describe", ...])` 和 `knowledge_main(["workspace", "archive", ...])`。
- E2E 必须验证 CLI alias 调用 `handle_workspace_tool`，且 handler name 分别为 `knowledge_workspace_create`、`knowledge_workspace_list`、`knowledge_workspace_describe` 与 `knowledge_workspace_archive`。
