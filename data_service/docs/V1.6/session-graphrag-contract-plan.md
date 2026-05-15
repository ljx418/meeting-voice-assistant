# V1.6-D1 Session GraphRAG Contract Plan

更新时间：2026-05-15

## 1. Scope

本文件最初由 V1.6-D1 建立，用于 Session GraphRAG public contract inventory 与 hardening。V1.6-D2 已在该基线之上开放 session lifecycle target HTTP minimal surface：create/list/get/close/delete。V1.6-D3 已完成 session ingest/query/build contract planning，但未新增公开面。D2/D3 当时不新增 MCP tool、CLI command 或 CLI subcommand，且不开放 session ingest/query/build target HTTP；D4/D5/D6 后续已分别开放 session ingest、session query、session build minimal target HTTP。V1.6-E1 后 quality feedback target HTTP 已开放；V1.6-E2 后 quality correction rules target HTTP 已开放；V1.6-E3 后 quality correction review target HTTP 已开放；V1.6-E4 后 quality correction plan target HTTP 已开放；V1.6-E5 后 quality correction-rules artifact build target HTTP 已开放；correction apply target HTTP 仍 planned / not opened。

`GET /api/workspaces/{workspace_id}/graph/session` 与 `knowledge graph session` 属于 V1.6-C4 accepted graph-scoped read-only inspection surface。它们不是 session lifecycle target HTTP，也不是完整 Session GraphRAG public contract。

## 2. Stable Contract Rules

Session GraphRAG 外部 contract 只能稳定依赖：

- `workspace_id`
- `session_id`
- `operation_id`，仅当既有 session operation lifecycle 返回真实 operation 时使用
- `artifact_ref` / `artifact_refs`
- `status`
- `node_count`
- `edge_count`
- `community_count`
- `created_at`
- `updated_at`
- `warnings`
- `next_actions`
- normalized `error.code` / `error.message` / `error.retryable`

内部 filesystem path、workspace layout、GraphRAG cache path、raw parquet/json/md physical path、artifact physical path 不能作为 stable external contract。

## 3. Artifact Ref Rules

Session GraphRAG `artifact_ref` 规则：

1. `artifact_ref` 不暴露物理路径。
2. `artifact_ref` 不依赖 workspace filesystem layout。
3. `artifact_ref` 不能是 absolute path。
4. `artifact_ref` 不能是 raw relative filesystem path。
5. `artifact_ref` 不包含 workspace root。
6. `artifact_ref` 不暴露 raw parquet/json/md physical path。
7. 同一 artifact 在 CLI / target HTTP / MCP 相关入口中应尽量保持一致。
8. 外部调用方应通过服务解析 `artifact_ref`，不能直接读文件系统路径。
9. debug / console-only 字段不是 external contract，必须明确标记为 non-contract。

## 4. Surface Matrix

| capability | surface | current status | request schema summary | response schema summary | error schema summary | artifact_ref behavior | operation_id behavior | side effects | path exposure risk | contract owner/helper | next phase candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| session create | MCP `knowledge_session_create` | V1.5 baseline accepted | `workspace_id` or `workspace`, optional external/session metadata | envelope with `session.session_id` and session metadata | existing normalized blocked envelope for invalid workspace or lifecycle errors | `artifact_refs[].type=session` with `session_id`; no physical path | none | writes session registry | metadata may carry debug-only internal values; must not be stable contract | `mcp_session_tools.py` + `SessionKnowledgeService` | D2 may define target HTTP lifecycle |
| session get | MCP `knowledge_session_get` | V1.5 baseline accepted | `workspace_id` or `workspace`, `session_id` or `external_id` | envelope with `session` | unknown session -> normalized blocked error | no physical path required | none | read-only | session metadata must remain non-contract for internal paths | `mcp_session_tools.py` + `SessionKnowledgeService` | D2 may define target HTTP lifecycle |
| session list | MCP `knowledge_session_list` | V1.5 baseline accepted | filters: `status`, `session_type`, `include_disposed`, `limit` | envelope with `items[]` | invalid limit -> existing normalized error | no physical path required | none | read-only | registry metadata must not expose internal layout as stable contract | `mcp_session_tools.py` + `SessionKnowledgeService` | D2 may define target HTTP lifecycle |
| session close/delete | MCP `knowledge_session_close` / `knowledge_session_delete` | V1.5 baseline accepted | `session_id`, optional reopen | envelope with lifecycle status and session | unknown session -> existing normalized error | `artifact_refs[].type=session` with `session_id`; no physical path | none | lifecycle state write | no stable path contract | `mcp_session_tools.py` + `SessionKnowledgeService` | D2 may define target HTTP lifecycle |
| session ingest | MCP `knowledge_session_ingest` | V1.5 baseline accepted | `session_id`, content/records/metadata, optional related ids | envelope with stable `session_id` and `source_id` summary | invalid session / closed write -> existing normalized error | `artifact_refs[].type=session_source` with `session_id` and `source_id` | none | writes session source registry | `related_paths` is input metadata, not stable output contract | `mcp_session_tools.py` + `SessionKnowledgeService` | D2/D3 planning only |
| session build start/status/cancel | MCP `knowledge_session_build_*` | V1.5 baseline accepted | `session_id`, `operation_id` for status/cancel, mode for start | operation envelope with `session_id`, `operation_id`, status/stage/progress/artifacts | unknown operation -> normalized `unknown_operation_id`; unknown session -> normalized session error | operation artifacts are returned as refs; physical paths are not stable contract | real operation id from session operation lifecycle | build operation writes session artifacts when started | artifacts/results must not require external filesystem layout | `mcp_session_tools.py` + `SessionKnowledgeService` | D2/D3 contract hardening candidate |
| session graph snapshot | MCP `knowledge_graph_snapshot` with `scope=session` | V1.5 baseline accepted | `workspace_id`, `scope=session`, `session_id`, max/options | envelope with session graph snapshot | missing graph -> existing session graph status; invalid session -> normalized error | should use service-owned graph artifacts; no physical path as contract | none | read-only | snapshot payload must avoid raw storage paths | `mcp_session_tools.py` + `SessionKnowledgeService.graph_snapshot` | D1 guard; D2 planning |
| session graph neighbors | MCP `knowledge_graph_neighbors` | V1.5 baseline accepted | `session_id`, `node_id`, `depth`, `max_nodes` | envelope with stable graph neighbors payload | unknown node/session -> existing normalized error/status | graph artifact is service-owned; no physical path as contract | none | read-only | node/edge metadata must not expose path layout | `mcp_session_tools.py` + `SessionKnowledgeService.graph_neighbors` | D1 guard |
| session community summary | MCP `knowledge_community_summary` | V1.5 baseline accepted | `session_id`, optional `community_id`, `limit` | envelope with community summaries | unknown session/community -> existing normalized error/status | graph artifact is service-owned; no physical path as contract | none | read-only | member/community metadata must not expose path layout | `mcp_session_tools.py` + `SessionKnowledgeService.community_summary` | D1 guard |
| session query | MCP `knowledge_session_query` | V1.5 baseline accepted | `session_id`, `query`, `top_k`, optional workspace context | envelope with scoped query result | missing graph/session -> existing normalized error/status | graph/query artifacts are service-owned; no physical path as contract | none | read-only query | hits/metadata must not expose physical paths as stable contract | `mcp_session_tools.py` + `SessionKnowledgeService.query_session` | D2/D3 planning |
| actor summary | MCP `knowledge_actor_summary` | V1.5 baseline accepted | `session_id`, `actor_id`, options | envelope with actor summary | missing session/actor -> existing normalized error/status | no physical path as contract | none | read-only | unit metadata must not expose path layout | `mcp_session_tools.py` + `SessionKnowledgeService.actor_summary` | D1 guard |
| graph session inspection | target HTTP `GET /api/workspaces/{workspace_id}/graph/session` | V1.6-C4 accepted | path `workspace_id`; optional `session_id`, `limit`, `include_nodes`, `include_edges`, `node_limit`, `edge_limit` | envelope with list/detail session graph summaries and stable node/edge projection | unknown workspace -> HTTP 404; unknown session -> blocked `unknown_session_id`; missing graph -> blocked `session_graph_no_artifact`; invalid limits -> HTTP 400 | `graph-session://{workspace_id}/{session_id}` or `graph-session://{workspace_id}/sessions`; non-path | none | read-only | low after stable projection; tests prevent internal path keys | `graph_session_contract.py` | D1 guard; not D2 lifecycle |
| graph session inspection | CLI `knowledge graph session` | V1.6-C4 accepted | `--workspace-id` / `--workspace`, optional `--session-id`, limits, include flags, `--json` | JSON envelope matching target HTTP core projection | invalid limits -> exit code 2; missing workspace -> exit code 2; session errors use same payload as helper | same `graph-session://...` ref as target HTTP | none | read-only | low after shared projection; tests compare core fields with target HTTP | `graph_session_contract.py` + CLI runtime | D1 guard |
| compatibility HTTP session surfaces | `/api/v1/knowledge/*` | retained compatibility surface if present; not expanded in D1 | existing compatibility contracts only | existing compatibility payloads only | existing normalized helper behavior | must not require direct filesystem paths | existing semantics only | no D1 changes | not treated as target contract | existing compatibility handlers | future migration review |
| session lifecycle create | target HTTP `POST /api/workspaces/{workspace_id}/sessions` | V1.6-D2 accepted | path `workspace_id`; body `external_id`, `session_type`, `title`, `ephemeral`, `ttl_seconds`, `metadata` | envelope with stable `session.session_id`, `status`, sanitized metadata, `session://...` artifact_ref | archived workspace -> blocked `workspace_archived`; invalid workspace -> existing HTTP error | `session://{session_id}`; non-path | none | writes session lifecycle registry only | metadata sanitized; no internal path/layout stable contract | `session_lifecycle_contract.py` + `SessionKnowledgeService` | D3 may evaluate ingest/query/build |
| session lifecycle list | target HTTP `GET /api/workspaces/{workspace_id}/sessions` | V1.6-D2 accepted | `status`, `session_type`, `include_deleted`, `limit` 1-100 | envelope with `items[]`, default `include_deleted=false` | invalid limit -> HTTP 400; unknown workspace -> existing HTTP error | per-session `session://...` in item payload | none | read-only | no internal path/layout stable contract | `session_lifecycle_contract.py` + `SessionKnowledgeService` | D3 guard |
| session lifecycle get | target HTTP `GET /api/workspaces/{workspace_id}/sessions/{session_id}` | V1.6-D2 accepted | path `workspace_id`, `session_id` | envelope with one stable session payload | unknown / cross-workspace session -> blocked `unknown_session_id` | `session://{session_id}` | none | read-only | no internal path/layout stable contract | `session_lifecycle_contract.py` + `SessionKnowledgeService` | D3 guard |
| session lifecycle close/delete | target HTTP `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close` / `delete` | V1.6-D2 accepted | path `workspace_id`, `session_id` | envelope with stable session status; close -> `closed`; delete -> existing lifecycle `disposed` | unknown / cross-workspace session -> blocked `unknown_session_id`; repeated behavior follows existing lifecycle | `session://{session_id}` | none | lifecycle state write only; no build/index/quality | no internal path/layout stable contract | `session_lifecycle_contract.py` + `SessionKnowledgeService` | D3 guard |
| session ingest target HTTP | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest` | V1.6-D4 accepted | session-scoped content/records ingest request | stable session source payload | normalized target HTTP error envelope | `session-source://...` | none | session-scoped source write only | metadata sanitized; no internal path/layout | `session_ingest_contract.py` | completed in D4 |
| session query target HTTP | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query` | V1.6-D5 accepted | session-scoped query and `top_k` | stable query payload | normalized target HTTP error envelope | `graph-session://...` | none | read-only | raw GraphRAG payload filtered | `session_query_contract.py` | completed in D5 |
| session build target HTTP | `/api/workspaces/{workspace_id}/sessions/{session_id}/build*` | V1.6-D6 accepted | start/status/cancel with `session_id`, real `operation_id`, and mode | stable session operation payload | normalized target HTTP error envelope | `session-build://...` / `session-artifact://...` | real session operation lifecycle id | session-scoped build/materialization only | artifacts/logs/diagnostics sanitized; no internal path/layout | `session_build_contract.py` | completed in D6 |
| quality feedback target HTTP | `POST /api/workspaces/{workspace_id}/quality/feedback` | V1.6-E1 accepted | path `workspace_id`; body target/action/suggestion/reason/metadata | stable feedback payload with `quality-feedback://...` artifact_ref | normalized target HTTP error envelope | non-path `quality-feedback://...` | none | non-destructive governance signal write | metadata sanitized; no internal path/layout | `quality_contract.py` + `DataService.record_quality_feedback` | completed in E1 |
| quality correction rules target HTTP | `GET/POST /api/workspaces/{workspace_id}/quality/correction-rules` | V1.6-E2 accepted | path `workspace_id`; optional list filters; body rule target/action/suggestion/reason/metadata | stable rule payload; `rule_id` primary identifier | normalized target HTTP error envelope | optional non-path ref | none | draft/proposal rules storage only | metadata sanitized; no internal path/layout | `quality_contract.py` | completed in E2 |
| remaining quality target HTTP | `/api/workspaces/{workspace_id}/quality*` except feedback | planned / not opened | not defined in D1 | not defined in D1 | not defined in D1 | N/A | N/A | not opened | N/A | future quality helper | V1.6-E candidate |

## 5. Error Contract Hardening

D1 固化当前实现的错误形态，不创建新的 envelope layout：

- unknown workspace：target HTTP uses current route helper and returns HTTP 404。
- unknown session：C4 graph session returns envelope status `blocked` with `data.error.code = unknown_session_id`。
- known session but graph artifact missing：C4 graph session returns envelope status `blocked` with `data.error.code = session_graph_no_artifact`。
- cross-workspace session：returns normalized not-found / blocked and must not leak the other workspace session graph。
- invalid limit / node_limit / edge_limit：uses existing bounded integer validation and returns HTTP 400 for target HTTP or exit code 2 for CLI。
- invalid operation_id：only applies to existing MCP session build tools; unknown operation remains normalized `unknown_operation_id`。
- artifact unavailable：must be represented as a normalized blocked/error payload, not an automatic build trigger。

## 6. D1 Guard Requirements

D1 accepted state must prove：

- no new MCP tool。
- no new CLI top-level or nested command。
- no new HTTP route。
- target HTTP route count remains 18。
- no `/api/workspaces/{workspace_id}/sessions*` routes。
- no quality target HTTP routes。
- C4 `/graph/session` remains graph-scoped read-only inspection。
- stable projection and `artifact_ref` do not expose path/layout。
- V1.6-D2 session lifecycle create/list/get/close/delete accepted；V1.6-D3 planning accepted with no public surface；V1.6-D4 session ingest target HTTP accepted；V1.6-D5 session query target HTTP accepted；V1.6-D6 session build target HTTP accepted；V1.6-E/F remain planned, not implemented。
