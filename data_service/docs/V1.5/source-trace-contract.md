# Source Trace Contract

更新时间：2026-05-12

## 定位

Source Trace 用于把一个 `source_id` 贯穿到 distill units、LLMWiki pages、GraphRAG nodes / edges / communities 和汇总统计。PhaseG4 已固化目标 contract 和漂移测试，PhaseG5 已抽取 shared serializer，PhaseG6 已补齐 schema 示例和迁移说明，PhaseG23 开放 `knowledge trace source` CLI alias，PhaseG29 开放 MCP `knowledge_source_trace`。

当前公开入口：

- HTTP：`POST /api/v1/knowledge/source/trace`
- CLI：`knowledge trace source --workspace-id <workspace_id> --source-id <source_id>`
- MCP：`knowledge_source_trace`

## 请求 Contract

当前 HTTP 请求字段：

| field | required | type | contract |
| --- | --- | --- | --- |
| `workspace` | yes | string | 当前兼容入口使用 workspace path，后续目标迁移到 `workspace_id`。 |
| `source_id` | yes | string | 稳定 source identity。 |
| `limit` | no | integer | 1-50，默认 12。 |

当前 MCP / 当前 CLI 请求字段：

| field | required | type | contract |
| --- | --- | --- | --- |
| `workspace_id` | yes | string | MCP-first 目标入口使用 workspace_id。 |
| `source_id` | yes | string | 稳定 source identity。 |
| `limit` | no | integer | 1-50，默认 12。 |

当前 HTTP request schema 示例：

```json
{
  "workspace": "/absolute/path/to/workspace",
  "source_id": "source-123",
  "limit": 12
}
```

当前 MCP request schema 示例：

```json
{
  "workspace_id": "research-vault",
  "source_id": "source-123",
  "limit": 12
}
```

当前 CLI 参数示例：

```bash
knowledge trace source --workspace-root ./workspaces --workspace-id research-vault --source-id source-123 --limit 12
```

## 响应 Contract

稳定顶层字段：

- `workspace`
- `source_id`
- `source`
- `distill`
- `llmwiki`
- `graphrag`
- `trace_summary`

稳定子字段：

- `distill.units`
- `distill.unit_count`
- `distill.provenance_summary`
- `distill.profile_debug`
- `llmwiki.pages`
- `llmwiki.page_count`
- `graphrag.nodes`
- `graphrag.edges`
- `graphrag.communities`
- `graphrag.node_count`
- `graphrag.edge_count`
- `graphrag.community_count`
- `graphrag.graph_model_version`
- `trace_summary.source_title`
- `trace_summary.unit_count`
- `trace_summary.llmwiki_page_count`
- `trace_summary.graph_node_count`
- `trace_summary.graph_community_count`

响应 schema 示例：

```json
{
  "workspace": "/absolute/path/to/workspace",
  "source_id": "source-123",
  "source": {
    "source_id": "source-123",
    "title": "Example Source"
  },
  "distill": {
    "units": [],
    "unit_count": 0,
    "provenance_summary": {},
    "profile_debug": {}
  },
  "llmwiki": {
    "pages": [],
    "page_count": 0
  },
  "graphrag": {
    "nodes": [],
    "edges": [],
    "communities": [],
    "node_count": 0,
    "edge_count": 0,
    "community_count": 0,
    "graph_model_version": "string-or-null"
  },
  "trace_summary": {
    "source_title": "Example Source",
    "unit_count": 0,
    "llmwiki_page_count": 0,
    "graph_node_count": 0,
    "graph_community_count": 0
  }
}
```

## PhaseG4 约束

- 不新增 `knowledge_source_trace` MCP tool。
- 当时不新增 `knowledge trace source` CLI command；PhaseG23 后该 CLI alias 已开放。
- 不新增 HTTP route。
- 不改变当前 `/api/v1/knowledge/source/trace` 响应字段集合。
- 只增加文档和 drift tests。

## PhaseG5 约束

- `POST /api/v1/knowledge/source/trace` 复用 `backend/data_service/source_trace_contract.py` 中的 `source_trace_payload`。
- 不新增 `knowledge_source_trace` MCP tool。
- 当时不新增 `knowledge trace source` CLI command；PhaseG23 后该 CLI alias 已开放。
- 不新增 HTTP route。
- 不改变当前 `/api/v1/knowledge/source/trace` 响应字段集合。

## PhaseG6 约束

- request / response schema 示例必须与 `source_trace_payload` 的稳定字段集合一致。
- `limit` contract 固定为 1-50，默认 12。
- HTTP 兼容入口继续使用 `workspace` path；PhaseG23/PhaseG29 后，CLI / MCP 同时支持 `workspace_id` 与本地测试用 `workspace` path。
- 当时 planned 的 MCP / CLI 入口现已开放，且必须复用 `source_trace_payload`，不得重新实现 trace payload 组装逻辑。
- 不新增 `knowledge_source_trace` MCP tool。
- 当时不新增 `knowledge trace source` CLI command；PhaseG23 后该 CLI alias 已开放。
- 不新增 HTTP route。

## PhaseG23 约束

- PhaseG23 开放 `knowledge trace source` CLI alias。
- `knowledge trace source` 必须复用 `source_trace_payload`，不得重新实现 trace payload 组装逻辑。
- 不新增 `knowledge_source_trace` MCP tool。
- 不新增 HTTP route。
- 不改变当前 `/api/v1/knowledge/source/trace` 响应字段集合。
- 不改变 `data_service` 兼容 CLI 顶层命令。

## PhaseG29 约束

- PhaseG29 开放 MCP `knowledge_source_trace`。
- `knowledge_source_trace` 必须复用 `source_trace_payload`，不得重新实现 trace payload 组装逻辑。
- 不新增 HTTP route。
- 不新增 CLI command。
- 不改变当前 `/api/v1/knowledge/source/trace` 和 `knowledge trace source` 响应字段集合。

## PhaseG30 / PhaseG31 状态

- PhaseG30 已开放 target HTTP `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`。
- target HTTP trace 必须复用 `source_trace_payload`，不得重新实现 trace payload 组装逻辑。
- PhaseG31 只做 V1.5 closure acceptance，不新增 trace 能力，不新增 CLI command，不改变旧 HTTP、target HTTP、MCP 或 CLI trace 响应字段集合。

## 后续迁移

HTTP / target HTTP / MCP / CLI 均复用 `source_trace_payload`。旧 HTTP 入口进入兼容窗口，不直接废弃。

迁移窗口要求：

- Stage 1：保持当前 HTTP `/api/v1/knowledge/source/trace` 不变，继续服务控制台和旧客户端。
- Stage 2：PhaseG29 已开放 MCP `knowledge_source_trace`，内部解析到 workspace 后调用 `source_trace_payload`。
- Stage 3：PhaseG23 已开放 CLI `knowledge trace source`，与目标 MCP 参数保持一致，输出与 HTTP payload 同字段。
- Stage 4：PhaseG30 已开放 target HTTP `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`，输出与旧 HTTP payload 同字段。
- Stage 5：HTTP 入口进入兼容窗口后，只允许增加 deprecation metadata，不移除现有字段。
