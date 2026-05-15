# V1.6-D3 Session Ingest / Query / Build Contract Plan

更新时间：2026-05-15

## 1. Scope

D3 is a planning and contract hardening phase only. It opens no public surface.

V1.6-D3 只做 session ingest / query / build 的 contract inventory、future target HTTP contract planning、guard 和文档同步。D3 不新增 MCP tool、CLI top-level command、CLI nested command 或 HTTP route。

D3 不开放：

- session ingest target HTTP
- session query target HTTP
- session build start/status/cancel target HTTP
- quality target HTTP

V1.6-D4 accepted 后，D3 的 planning baseline 继续保留，但 session ingest 已按 D4 单独阶段开放为最小 target HTTP surface。V1.6-D5 accepted 后，session query 已按 D5 单独阶段开放为最小 read-only target HTTP surface。V1.6-D6 accepted 后，session build 已按 D6 单独阶段开放为 start/status/cancel 最小 target HTTP surface。D4 accepted 只新增 session ingest；D5 accepted 只新增 `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`；D6 accepted 只新增 session build start/status/cancel，不开放 quality target HTTP。

## 2. Current Boundary

D2 已开放 session lifecycle minimal target HTTP：

- `POST /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`

D6 accepted 后当前已开放：

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`

Quality feedback target HTTP is accepted in E1. Quality correction rules target HTTP is accepted in E2. Quality correction review target HTTP is accepted in E3. Quality correction plan target HTTP is accepted in E4. Quality correction-rules artifact build target HTTP is accepted in E5. Correction apply target HTTP remains planned / not opened.

Boundary rules:

- D2 create session is not ingest.
- D2 get session is not query.
- D2 close/delete session is not build cancel.
- C4 `/api/workspaces/{workspace_id}/graph/session` is graph-scoped artifact inspection, not session query or session build.
- D3 is not full Session GraphRAG public contract implementation.

## 3. Contract Matrix

| capability | existing MCP tool | CLI surface | compatibility HTTP surface | target HTTP status | planned target HTTP route | request fields | response fields | operation_id behavior | artifact_ref behavior | side effects | error cases | path leakage risk | contract owner/helper | future phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| session lifecycle create/list/get/close/delete | `knowledge_session_create`, `knowledge_session_list`, `knowledge_session_get`, `knowledge_session_close`, `knowledge_session_delete` | no dedicated session lifecycle CLI in D2; graph CLI is separate | no new D2 compatibility route; `/api/v1/knowledge/*` retained | accepted in D2 | already open as D2 lifecycle routes | `workspace_id`, `session_id`, lifecycle metadata | stable session payload with sanitized metadata and `session://...` ref | none | `session://{session_id}` | lifecycle registry write for create/close/delete; read-only for list/get | unknown workspace/session, archived workspace create, repeated close/delete | metadata must be sanitized; no storage path contract | `session_lifecycle_contract.py`, `SessionKnowledgeService` | completed in D2 |
| session ingest | `knowledge_session_ingest` | not open as a CLI nested command in D4 | no compatibility session ingest expansion in D4 | accepted in D4 | D4 accepted: `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest` | `session_id`, `source_type`, `content_format`, `title`, exactly one of `content` or `records`, `metadata`, `related_source_ids`, `source_refs`, `auto_link`, `allow_closed_write`; `related_paths` rejected by default | stable `workspace_id`, `session_id`, session-scoped `source_id` / `session_source_id`, `source_scope=session`, `record_count`, status, `session-source://...`, warnings, next actions, normalized error | default does not create `operation_id`; if one ever appears it must be real lifecycle id, never fake | `session-source://{session_id}/{source_id}`; no physical paths | writes session-scoped source storage only; does not trigger query/build/GraphRAG index/materialization/quality | unknown workspace/session, closed/deleted session, invalid content/records/content_format/source_type, payload too large | metadata and nested fields sanitized; `related_paths` not echoed; no raw path/layout | `session_ingest_contract.py`, `SessionKnowledgeService.ingest` | completed in V1.6-D4 |
| session query | `knowledge_session_query` | not open as a CLI nested command in D5; `knowledge graph session` is inspection only | no compatibility session query expansion in D5 | accepted in D5 | D5 accepted: `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query` | `session_id`, `query`, `top_k`; `include_workspace_context` is not part of D5 target HTTP contract | stable `workspace_id`, `session_id`, `query`, `top_k`, answer, sanitized results/items/nodes/edges/communities, `graph-session://...`, warnings, next actions, normalized error | no operation_id; D5 never returns fake operation_id | returns existing session graph refs only; no raw graph paths | read-only; does not write session/source/graph/quality state | unknown session, missing graph artifact, empty query, disposed session, cross-workspace isolation | graph hit metadata is sanitized; raw GraphRAG rows/prompts/messages/vectors are not returned | `session_query_contract.py`, `SessionKnowledgeService.query_session` | completed in V1.6-D5 |
| session build start | `knowledge_session_build_start` | not open as a CLI nested command in D6 | no compatibility session build expansion in D6 | accepted in D6 | D6 accepted: `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start` | `session_id`, `mode`; exact modes from existing `SESSION_BUILD_MODES` | operation envelope with real `operation_id`, status, stage, progress, warnings, stable artifact refs | must use real operation_id from existing session operation lifecycle | `session-build://...` and `session-artifact://...`; no physical paths | starts session-scoped build lifecycle and may materialize session graph according to existing MCP behavior | unknown session, disposed session, no session sources, concurrent build, invalid mode | operation artifacts/results/logs/diagnostics are sanitized | `session_build_contract.py`, `SessionKnowledgeService.start_build` | completed in V1.6-D6 |
| session build status | `knowledge_session_build_status` | not open as a CLI nested command in D6 | no compatibility session build expansion in D6 | accepted in D6 | D6 accepted: `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}` | `session_id`, `operation_id` | operation envelope with status/stage/progress/results/stable artifact refs | required; operation_id must belong to the workspace/session | artifact refs only; no raw artifact path | read-only | unknown session, unknown operation, cross-workspace/cross-session operation | operation metadata/results/logs/diagnostics are sanitized | `session_build_contract.py`, `SessionKnowledgeService.get_operation` | completed in V1.6-D6 |
| session build cancel | `knowledge_session_build_cancel` | not open as a CLI nested command in D6 | no compatibility session build expansion in D6 | accepted in D6 | D6 accepted: `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel` | `session_id`, `operation_id`, optional `reason` | operation envelope with cancelled or terminal lifecycle status | required; terminal cancel behavior reuses existing lifecycle | artifact refs only; no raw path | lifecycle operation state write only | unknown operation, terminal operation cancel, cross-workspace/cross-session operation | operation metadata is sanitized | `session_build_contract.py`, `SessionKnowledgeService.cancel_operation` | completed in V1.6-D6 |
| graph-scoped session inspection | MCP graph/session tools and C4 target HTTP/CLI | `knowledge graph session` | compatibility retained only | accepted in C4; unchanged in D3 | `GET /api/workspaces/{workspace_id}/graph/session` already open | `session_id`, limits, include flags | graph artifact summaries, node/edge projections | none | `graph-session://...` | read-only; no lifecycle state change | unknown session, missing graph artifact, invalid limits | graph metadata must remain sanitized | `graph_session_contract.py`, `SessionKnowledgeService.graph_snapshot` | completed in C4; guarded by D3 |
| quality feedback target HTTP | `knowledge_quality_feedback` exists in V1.5 MCP baseline | quality CLI/compatibility capabilities exist outside D3 | compatibility retained | accepted in E1 | E1 accepted: `POST /api/workspaces/{workspace_id}/quality/feedback` | target/action/suggestion/reason/metadata | stable feedback payload with non-path artifact_ref | none | `quality-feedback://...` | non-destructive feedback write | invalid workspace/target/action; archived workspace | metadata sanitized; no path/layout | `quality_contract.py` | completed in V1.6-E1 |
| quality correction rules target HTTP | `knowledge_correction_rules` exists in V1.5 MCP baseline | quality CLI/compatibility capabilities exist outside D3 | compatibility retained | accepted in E2 | E2 accepted: `GET/POST /api/workspaces/{workspace_id}/quality/correction-rules` | target/action/suggestion/reason/metadata for write; filters for read | stable correction rule payload | none | optional non-path ref | draft/proposal rules storage only | invalid workspace/target/action/status | metadata sanitized; no path/layout | `quality_contract.py` | completed in V1.6-E2 |
| remaining quality target HTTP | quality MCP/CLI/compatibility capabilities exist outside D3 | quality CLI exists | compatibility retained | planned / not opened | future V1.6-E only | not defined in D3 | not defined in D3 | not defined in D3 | not defined in D3 | not opened | not opened | N/A | `quality_contract.py` in future | V1.6-E candidate |

## 4. Future Phase Split

D3 intentionally did not implement ingest/query/build. D4 later implemented ingest only. D5 later implemented read-only query only. Remaining work must stay split:

- D4 completed: Session Ingest Target HTTP Minimal Surface. D4 accepted only this route and did not open query/build.
- D5 completed: Session Query Target HTTP Minimal Surface. D5 accepted only this read-only route and did not open build.
- D6 completed: Session Build Target HTTP Minimal Surface.

Historical phase boundaries remain part of the accepted contract: D4 opened only ingest, D5 opened only query, and D6 opened only session build. D6 must not be reinterpreted as quality target HTTP or full Session GraphRAG public contract.

## 5. Guard Requirements

D6 accepted state must prove:

- target HTTP route count is 28.
- HTTP diff from D5 accepted surface is exactly three D6 session build routes.
- MCP tool count remains 40.
- MCP diff is none.
- CLI top-level and nested diff is none.
- no quality target HTTP routes exist.
- session build operation_id is a real lifecycle id.
- session build remains session-scoped and does not trigger workspace-level build.
- D2 lifecycle routes still pass.
- C4 graph session remains graph-scoped inspection.
- E/F remain planned, not implemented.
