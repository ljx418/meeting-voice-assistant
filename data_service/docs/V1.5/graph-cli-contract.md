# Graph CLI Contract

更新时间：2026-05-12

## 定位

PhaseG22 开放 `knowledge graph snapshot` 的只读 alias，作为 graph 目标 CLI 的最小阶段。

PhaseG24 固化 `knowledge graph` advanced 子命令迁移窗口。本阶段不新增 MCP tool，不新增 HTTP route，不开放 `knowledge graph neighbors/community/query/session`。CLI 只转调现有 session MCP handler 的 `knowledge_graph_snapshot` 分支，并固定使用 workspace scope。

## 当前开放命令

```text
knowledge graph snapshot --workspace-root ./workspaces --workspace-id research-vault --max-nodes 200
```

## 约束

- `knowledge graph snapshot` 必须复用 `knowledge_graph_snapshot` 的 handler。
- CLI 当前只开放 workspace graph snapshot，不开放 session graph snapshot。
- `knowledge graph neighbors`、`knowledge graph community`、`knowledge graph query` 仍不开放。
- 不新增 MCP tool 或 HTTP route。
- 不改变现有 MCP `knowledge_graph_snapshot` 和 HTTP `/api/v1/knowledge/graph` contract。
- 输出仍使用 MCP envelope 形态：`workspace_id`、`status`、`warnings`、`artifact_refs`、`next_actions`、`data`。
- graph data 稳定字段保持 `scope`、`graph_model_version`、`nodes`、`edges`、`communities`、`stats`。

## PhaseG24 advanced 迁移窗口

planned advanced CLI 子命令：

```text
knowledge graph neighbors --workspace-root ./workspaces --workspace-id research-vault --node-id node-123 --limit 20
knowledge graph community --workspace-root ./workspaces --workspace-id research-vault --community-id community-123
knowledge graph query --workspace-root ./workspaces --workspace-id research-vault "graph question" --top-k 8
knowledge graph session --workspace-root ./workspaces --workspace-id research-vault --session-id session-123 --max-nodes 200
```

PhaseG24 只固化 planned contract，不开放上述子命令。

后续开放任一 advanced 子命令时必须满足：

- 每次只开放一个最小能力组。
- 必须复用现有 GraphRAG / session graph handler 或 service。
- 不新增 HTTP route。
- 不改变 `knowledge graph snapshot` 输出字段。
- 不把 graph 算法逻辑回填到 `data_service`。
- 每个子命令必须有独立 E2E、公开面扫描和 drawio/md 同步。

## 漂移测试要求

- `_build_knowledge_parser()` 顶层 choices 当前必须严格等于 `{"quality", "query", "workspace", "source", "build", "graph", "trace"}`。
- `knowledge graph` 子命令当前必须严格等于 `{"snapshot"}`。
- `knowledge graph neighbors/community/query/session` 必须保持 planned，不得出现在 CLI parser choices。
- E2E 必须调用 `knowledge_main(["graph", "snapshot", ...])`。
- E2E 必须验证 CLI alias 调用 `handle_session_tool`，且 handler name 为 `knowledge_graph_snapshot`。

## PhaseG31 Closure Audit

PhaseG31 只做 V1.5 收口验收。`knowledge graph` 当前仍只开放 `snapshot`；`neighbors/community/query/session` 继续作为 V1.6 candidates 记录，不在 PhaseG31 实现。当前 target HTTP 也不开放 graph advanced route。
