# ResearchNotebook V1.0-RC1 data_service Real Route Alignment

文档状态：RC1 real-route alignment；2026-05-18。

## 1. Runtime Baseline

| Item | Value |
| --- | --- |
| data_service commit | `a50027e6` |
| ResearchNotebook workspace commit | `a50027e6` |
| Startup command | `DATA_SERVICE_WORKSPACE_ROOT=/tmp/research-notebook-rc1-workspaces DATA_SERVICE_REQUIRE_API_KEY=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003` |
| Base URL | `http://127.0.0.1:8003` |
| Required env | `DATA_SERVICE_WORKSPACE_ROOT`, `DATA_SERVICE_REQUIRE_API_KEY=false` for local RC smoke |
| CORS / proxy | data_service enables permissive CORS; no Vite proxy required for RC smoke |
| RC workspace prefix | `rn-rc1-<timestamp>-workspace` |

## 2. Confirmed Target Routes

| Product wrapper | Real route | RC1 result | Adapter action |
| --- | --- | --- | --- |
| `workspaces.list` | `GET /api/workspaces` | pass | unwrap `data.items` envelope |
| `workspaces.create` | `POST /api/workspaces` | pass | send `{ name }`; unwrap `data.workspace` |
| `workspaces.get` | `GET /api/workspaces/{workspace_id}` | pass | unwrap `data.workspace` |
| `workspaces.archive` | `POST /api/workspaces/{workspace_id}/archive` | pass | send `{}` or reason; unwrap `data.workspace.status` |
| `sources.list` | `GET /api/workspaces/{workspace_id}/sources` | pass | unwrap `data.items` |
| `sources.create` | `POST /api/workspaces/{workspace_id}/sources` | pass | map minimal text input to `texts[]` |
| `sources.get` | `GET /api/workspaces/{workspace_id}/sources/{source_id}` | pass | unwrap `data.source` |
| `sources.trace` | `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace` | degraded | route exists; RC text source returned 404 |
| `build.start` | `POST /api/workspaces/{workspace_id}/build/start` | pass | send `{}`; read envelope `operation_id` |
| `build.getOperation` | `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}` | pass | unwrap `data`; status completed |
| `query.workspace` | `POST /api/workspaces/{workspace_id}/query` | pass | send `{ query }`; map `hits` to `AnswerEvidence` |
| `sessions.create` | `POST /api/workspaces/{workspace_id}/sessions` | pass | unwrap `data.session` |
| `sessions.ingest` | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest` | pass | map snippet to text ingest payload |
| `sessions.build.start` | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start` | pass | send `{}` |
| `sessions.build.getOperation` | `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}` | pass | normalize `succeeded` to completed |
| `sessions.query` | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query` | pass | send `{ query }`; no-evidence is accepted |
| `graph.communities` | `GET /api/workspaces/{workspace_id}/graph/community` | pass | unwrap `data.items` |
| `graph.neighbors` | `GET /api/workspaces/{workspace_id}/graph/neighbors` | degraded | backend requires `node_id` or `entity_id`; M4 overview has no selected node |
| `quality.feedback` | `POST /api/workspaces/{workspace_id}/quality/feedback` | pass | map rating to `action`, `target_id`, metadata |

## 3. Request / Response Shape Deviations

- Target HTTP uses envelope payloads: `workspace_id`, `status`, `warnings`, `artifact_refs`, `next_actions`, `data`.
- Lists use `data.items`, not only top-level `workspaces` / `sources` / `sessions`.
- Source create expects `{ texts: [{ title, content, metadata }], metadata }`, not direct `{ title, content }`.
- Workspace query expects `{ query }`, not `{ question }`.
- Session ingest expects `content_format`, `source_type`, `title`, and `content`.
- Feedback expects `target_id` and `action`; frontend rating is mapped inside adapter.
- Session build can return `succeeded`; frontend normalizes it to completed.

## 4. Accepted Degraded States

- Source trace route exists but returned `404 Unknown source_id` for the RC minimal text source. The UI already treats trace failure as drawer-local and does not clear answer content.
- Session query returned no evidence. This is accepted because explicit no-evidence state is part of V1.0.
- Graph neighbors overview cannot be called without a selected node. M4 graph context can rely on community rendering and missing/unavailable state until a node-scoped UX is introduced.

## 5. Boundary Confirmation

- No `/api/v1/knowledge/*` route is used by ResearchNotebook.
- Feature modules still do not call `fetch` directly.
- Real route shape remains isolated in `src/shared/api/dataServiceClient.ts`.
- Real fixtures are sanitized and exclude local absolute paths, cache paths, and artifact physical paths.
