# Source CLI Contract

更新时间：2026-05-12

## 定位

PhaseG20 开放 `knowledge source list` 的只读 alias，作为 source registry 目标 CLI 的最小阶段。

PhaseG26 已开放 `knowledge source import/remove` 写入型治理 alias。本阶段不新增 MCP tool，不新增 HTTP route；CLI 只转调现有 MCP source handler，复用 source registry envelope、workspace_id 解析和 no-internal-path sanitizer。

## 当前开放命令

```text
knowledge source import --workspace-root ./workspaces --workspace-id research-vault --path ./docs/a.md
knowledge source import --workspace-root ./workspaces --workspace-id research-vault --text "inline source" --title "Inline Source" --metadata-json '{"stage":"phaseg26"}'
knowledge source list --workspace-root ./workspaces --workspace-id research-vault --status active --limit 100
knowledge source remove --workspace-root ./workspaces --workspace-id research-vault --source-id src_123 --reason duplicate
```

## 约束

- `knowledge source import/list/remove` 必须复用 `knowledge_source_import/list/remove` 的 handler。
- 不新增 MCP tool 或 HTTP route。
- 不改变现有 MCP `knowledge_source_*` 和 HTTP `/api/v1/knowledge/sources/*` contract。
- 输出仍使用 MCP envelope 形态：`workspace_id`、`operation_id`、`status`、`warnings`、`artifact_refs`、`next_actions`、`data`。
- source item 稳定字段保持 `source_id`、`sha256`、`title`、`status`、`low_signal`、`ingest_status`。
- `import` 仅支持 `--path` 重复参数或单条 `--text`；复杂批量导入仍建议直接使用 MCP `knowledge_source_import`。
- `remove` 是 soft remove，不删除原始 source artifact。

## 漂移测试要求

- `_build_knowledge_parser()` 顶层 choices 当前必须严格等于 `{"quality", "query", "workspace", "source", "build", "graph", "trace"}`。
- `knowledge source` 子命令当前必须严格等于 `{"import", "list", "remove"}`。
- E2E 必须调用 `knowledge_main(["source", "import", ...])`、`knowledge_main(["source", "remove", ...])` 和 `knowledge_main(["source", "list", ...])`。
- E2E 必须验证 CLI alias 调用 `handle_source_tool`，且 handler name 为 `knowledge_source_import`、`knowledge_source_remove`、`knowledge_source_list`。
