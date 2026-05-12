# Interface Convergence Matrix

更新时间：2026-05-12

## 定位

PhaseG1 固化 MCP / CLI / HTTP 三入口的当前状态和目标迁移方向。PhaseG2/G3 开始按最小能力组收敛内部 service contract。MCP 是默认主入口；CLI 和 HTTP 在当前阶段保持兼容，不做破坏性改名或响应形态变更。

当前稳定兼容入口：

- MCP：`python -m data_service.mcp_stdio`
- CLI：`python -m data_service`
- HTTP：`/api/v1/knowledge/*`
- Target HTTP：`/api/workspaces/{workspace_id}/...` 首批只开放 query / distill / source trace

目标方向：

- MCP 继续作为 primary contract。
- CLI 逐步迁移到 workspace-scoped `knowledge ...` 语义。
- HTTP 逐步迁移到 workspace-scoped `/api/workspaces/{workspace_id}/...` 语义。

## 能力矩阵

| capability | MCP | HTTP | CLI | 当前状态 | 目标 |
| --- | --- | --- | --- | --- | --- |
| workspace | `knowledge_workspace_create/list/describe/archive` | `/api/v1/knowledge/workspaces/*` | `knowledge workspace create/list/describe/archive` | primary | PhaseG25 已开放 workspace write CLI aliases；`workspace_id` first lifecycle contract |
| source | `knowledge_source_import/list/remove` | `/api/v1/knowledge/sources/*` | `knowledge source import/list/remove` | primary | PhaseG26 已开放 source write CLI aliases；source registry with `artifact_ref` / `debug_paths` split |
| build | `knowledge_build_start/status/cancel` | `/api/v1/knowledge/build/*` | `knowledge build start/status/cancel` | primary | PhaseG27 已开放 build write CLI aliases；`operation_id` lifecycle envelope |
| query | `knowledge_query` / `knowledge_query_v2` | `/api/v1/knowledge/query`；target: `/api/workspaces/{workspace_id}/query` | `data_service query` / `knowledge query` | primary | PhaseG30 已开放首批目标 HTTP route；query payload 复用 `run_query_contract` |
| distill | `knowledge_distill_preview` | `/api/v1/knowledge/distill`；target: `/api/workspaces/{workspace_id}/distill` | `data_service distill` | primary | PhaseG30 已开放首批目标 HTTP route；distill payload 复用 `run_distill_contract` |
| graph | `knowledge_graph_snapshot/neighbors/community_summary` | `/api/v1/knowledge/graph` | `knowledge graph snapshot`；planned advanced: `neighbors/community/query/session` | compat | PhaseG22 已开放 knowledge graph snapshot read-only alias；GraphRAG service boundary remains `app.graphrag.service` |
| trace | `knowledge_source_trace` | `/api/v1/knowledge/source/trace`；target: `/api/workspaces/{workspace_id}/sources/{source_id}/trace` | `knowledge trace source` | primary | PhaseG30 已开放首批目标 HTTP route；MCP / HTTP / CLI / target HTTP 复用 `source_trace_payload` |
| quality | `knowledge_quality_*` / `knowledge_correction_*` | `/api/v1/knowledge/quality/*` | `data_service quality *`；entrypoint-ready: `knowledge quality *` | primary | PhaseG15 已提供 knowledge quality entrypoint-ready alias；PhaseG14 已开放写入型命令 |
| session | `knowledge_session_*` / `knowledge_actor_summary` | planned: `/api/v1/knowledge/sessions/*` | planned: `knowledge session *` | primary | session graph lifecycle stays MCP-first |

## PhaseG1 / PhaseG2 / PhaseG3 约束

- 不新增 MCP tool、HTTP route 或 CLI command。
- 不修改现有响应形态。
- 不废弃当前 `data_service` CLI 和 `/api/v1/knowledge/*`。
- PhaseG2 允许新增内部 contract helper 和测试护栏，但公开入口必须保持兼容。
- PhaseG3 不新增 MCP distill tool，只收敛已有 HTTP / CLI distill preview 的内部 contract helper。
- PhaseG4 不新增 MCP / CLI trace 入口，只固化 `source_id` trace 目标 contract 与漂移测试。
- PhaseG7 不新增 CLI quality command，只收敛已有 HTTP low-signal audit 的内部 contract helper。
- PhaseG8 已固化 Quality Summary / Correction Plan；不新增 MCP tool、HTTP route 或 CLI `quality` command，只固化当前 contract 与 drift tests；`/api/v1/knowledge/quality/summary` 不应提前开放。
- PhaseG9 已固化 Quality Feedback / Rules / Review；不新增 MCP tool、HTTP route 或 CLI `quality` command，只固化当前 contract 与 drift tests；现有 quality HTTP 兼容入口保持不变。
- PhaseG10 不新增 MCP tool、HTTP route 或 CLI `quality` command，只把现有 quality HTTP feedback / rules / review 兼容入口迁移到 shared contract helper，响应字段保持不变。
- PhaseG11 不新增 MCP tool、HTTP route 或 CLI `quality` command，只把现有 quality HTTP correction plan 兼容入口迁移到 shared contract helper，响应字段保持不变。
- PhaseG12 已固化 Quality CLI planned 迁移窗口；不新增 MCP tool、HTTP route 或 CLI `quality` command，只文档化目标 `data_service quality ...` / `knowledge quality ...` 入口和 Stage 1-4 兼容窗口。
- PhaseG13 已开放 Quality CLI 只读 preview；不新增 MCP tool 或 HTTP route；只开放 `summary`、`correction-plan`、`feedback-list`、`rules`。
- PhaseG14 已开放 Quality CLI 写入型命令；不新增 MCP tool 或 HTTP route；新增 `feedback`、`rules-build`、`review`，并复用 shared contract helper。
- PhaseG15 已提供 knowledge quality entrypoint-ready alias；不新增 MCP tool 或 HTTP route；`knowledge_main` 复用 `data_service` CLI parser 和 shared helper。
- PhaseG17 已冻结 `knowledge` 顶层公开面；当时 `knowledge` 只开放 `quality`，避免隐式开放 workspace/source/build/query 等 alias。
- PhaseG18 当时开放 `knowledge query` alias；不新增 MCP tool 或 HTTP route；只新增 query 一个能力组 alias，并复用 `run_query_contract`；当时不得一次性开放 `knowledge workspace/source/build/distill/graph/trace`。
- PhaseG19 已开放 knowledge workspace list/describe read-only alias；不新增 MCP tool 或 HTTP route；只转调 `knowledge_workspace_list` / `knowledge_workspace_describe` handler；不开放 `knowledge workspace create/archive`。
- PhaseG20 已开放 knowledge source list read-only alias；不新增 MCP tool 或 HTTP route；只转调 `knowledge_source_list` handler；不开放 `knowledge source import/remove`。
- PhaseG21 已开放 knowledge build status read-only alias；不新增 MCP tool 或 HTTP route；只转调 `knowledge_build_status` handler；不开放 `knowledge build start/cancel`。
- PhaseG22 已开放 knowledge graph snapshot read-only alias；不新增 MCP tool 或 HTTP route；只转调 `knowledge_graph_snapshot` handler；不开放 `knowledge graph neighbors/community/query/session`。
- PhaseG23 已开放 knowledge trace source read-only alias；不新增 MCP tool 或 HTTP route；只复用 `source_trace_payload`；不开放 `knowledge_source_trace` MCP tool。
- PhaseG24 已固化 knowledge graph advanced CLI migration window；不新增 MCP tool、HTTP route 或 CLI command；`knowledge graph` 仍只开放 `snapshot`。
- PhaseG25 已开放 knowledge workspace create/archive write aliases；不新增 MCP tool 或 HTTP route；只转调 `knowledge_workspace_create` / `knowledge_workspace_archive` handler。
- PhaseG26 已开放 knowledge source import/remove write aliases；不新增 MCP tool 或 HTTP route；只转调 `knowledge_source_import` / `knowledge_source_remove` handler。
- PhaseG27 已开放 knowledge build start/cancel write aliases；不新增 MCP tool 或 HTTP route；只转调 `knowledge_build_start` / `knowledge_build_cancel` handler。
- PhaseG28 已开放 MCP knowledge_distill_preview；不新增 HTTP route 或 CLI command；只复用 `run_distill_contract`。
- PhaseG29 已开放 MCP knowledge_source_trace；不新增 HTTP route 或 CLI command；只复用 `source_trace_payload`。
- PhaseG30 已开放首批目标 HTTP route：`/api/workspaces/{workspace_id}/query`、`/api/workspaces/{workspace_id}/distill`、`/api/workspaces/{workspace_id}/sources/{source_id}/trace`；旧 `/api/v1/knowledge/*` 兼容入口不废弃；只复用已有 shared contract。

## 后续 PhaseG 候选

- PhaseG16 已新增 packaging console script：`knowledge = data_service.__main__:knowledge_main`。
- PhaseG24：已固化 `knowledge graph` advanced 子命令迁移窗口，候选 `neighbors/community/query/session` 仍为 planned。
- PhaseG25：已开放 `knowledge workspace create/archive` 写入型 CLI contract。
- PhaseG26：已开放 `knowledge source import/remove` 写入型 CLI contract。
- PhaseG27：已开放 `knowledge build start/cancel` 写入型 CLI contract。
- PhaseG28：已开放 MCP `knowledge_distill_preview`，已复用 `run_distill_contract`。
- PhaseG29：已开放 MCP `knowledge_source_trace`，已复用 `source_trace_payload`。
- PhaseG30：已开放首批目标 HTTP route：query / distill / source trace，旧 `/api/v1/knowledge/*` 保持兼容窗口。
- PhaseG31：V1.5 收口验收已完成，closure status accepted；未新增 MCP tool、HTTP route 或 CLI command，V1.6 candidates 仅记录未实现。
