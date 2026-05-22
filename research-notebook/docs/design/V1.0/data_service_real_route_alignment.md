# ResearchNotebook V1.0-RC6 data_service Real Route Alignment

文档状态：RC6 / V1.1-RC4 source trace re-smoke alignment；2026-05-22。

## 1. Runtime Baseline

| Item | Value |
| --- | --- |
| data_service commit | `c774626a` |
| ResearchNotebook workspace commit | `c774626a` plus RC2-RC6 working-tree updates |
| Startup command | `JWT_DEV_MODE=1 JWT_DEV_BYPASS_AUTH=1 DATA_SERVICE_REQUIRE_API_KEY=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8003` |
| Base URL | `http://127.0.0.1:8003` |
| Required env | `DATA_SERVICE_WORKSPACE_ROOT`, `DATA_SERVICE_REQUIRE_API_KEY=false` for local RC smoke |
| CORS / proxy | data_service enables permissive CORS; no Vite proxy required for RC smoke |
| RC workspace prefix | `rn-release-<timestamp>-workspace` |

## 2. Confirmed Target Routes

| Product wrapper | Real route | RC3/RC6 result | Adapter action |
| --- | --- | --- | --- |
| `workspaces.list` | `GET /api/workspaces` | pass | unwrap `data.items` envelope |
| `workspaces.create` | `POST /api/workspaces` | pass | send `{ name }`; unwrap `data.workspace` |
| `workspaces.get` | `GET /api/workspaces/{workspace_id}` | pass | unwrap `data.workspace` |
| `workspaces.archive` | `POST /api/workspaces/{workspace_id}/archive` | pass | send `{}` or reason; unwrap `data.workspace.status` |
| `sources.list` | `GET /api/workspaces/{workspace_id}/sources` | pass | unwrap `data.items` |
| `sources.create` | `POST /api/workspaces/{workspace_id}/sources` | pass | map minimal text input to `texts[]` |
| `sources.get` | `GET /api/workspaces/{workspace_id}/sources/{source_id}` | pass | unwrap `data.source` |
| `sources.trace` | `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace` | limited pass | route exists; RC6 minimal text registry source `src_2003ad3198c69861` returned 404; after data_service source trace backend fix, V1.1-RC4 repeated the check with registry source `src_cce80f0ca6dad217` and received HTTP 200 with trace/provenance |
| `build.start` | `POST /api/workspaces/{workspace_id}/build/start` | pass | send `{}`; read envelope `operation_id` |
| `build.getOperation` | `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}` | pass | unwrap `data`; status completed |
| `query.workspace` | `POST /api/workspaces/{workspace_id}/query` | pass | send `{ query }`; map `hits` to `AnswerEvidence`; RC3 hits returned llmwiki/sourceRef evidence |
| `sessions.create` | `POST /api/workspaces/{workspace_id}/sessions` | pass | unwrap `data.session` |
| `sessions.ingest` | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest` | pass | map snippet to text ingest payload |
| `sessions.build.start` | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start` | pass | send `{}` |
| `sessions.build.getOperation` | `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}` | pass | normalize `succeeded` to completed |
| `sessions.query` | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query` | pass | send `{ query }`; no-evidence is accepted; graph nodes/edges may be present without evidence items |
| `graph.communities` | `GET /api/workspaces/{workspace_id}/graph/community?include_members=true` | pass | unwrap `data.items`; may provide selectable members |
| `graph.neighbors` | `GET /api/workspaces/{workspace_id}/graph/neighbors?node_id=...` or `?entity_id=...` | pass | only called after node/entity selection |
| `quality.feedback` | `POST /api/workspaces/{workspace_id}/quality/feedback` | pass | map rating to `action`, `target_id`, metadata |

## 3. Request / Response Shape Deviations

- Target HTTP uses envelope payloads: `workspace_id`, `status`, `warnings`, `artifact_refs`, `next_actions`, `data`.
- Lists use `data.items`, not only top-level `workspaces` / `sources` / `sessions`.
- Source create expects `{ texts: [{ title, content, metadata }], metadata }`, not direct `{ title, content }`.
- Workspace query expects `{ query }`, not `{ question }`.
- Workspace query hits may return llmwiki page refs/slugs in `source`; these are display-only `sourceRef` unless exactly matched to registry `source_id`.
- Session ingest expects `content_format`, `source_type`, `title`, and `content`.
- Session query can return graph nodes/edges with zero `items`; frontend treats this as explicit no-evidence for answer citations.
- Feedback expects `target_id` and `action`; frontend rating is mapped inside adapter.
- Session build can return `succeeded`; frontend normalizes it to completed.

## 4. Accepted Degraded States

- Source trace route returned `404 Unknown source_id` for the RC3 and RC6 minimal text registry sources. After the data_service backend fix, V1.1-RC4 returned HTTP 200 for the registry source id `src_cce80f0ca6dad217`. The UI still treats unsupported/failing trace cases as drawer-local and does not clear answer content.
- Session query returned no evidence. This is accepted because explicit no-evidence state is part of V1.0.
- Graph neighbors cannot be called without a selected node/entity. RC3 smoke confirmed node-scoped neighbors work when community members provide `node_id`.

## 5. Boundary Confirmation

- No `/api/v1/knowledge/*` route is used by ResearchNotebook.
- Feature modules still do not call `fetch` directly.
- Real route shape remains isolated in `src/shared/api/dataServiceClient.ts`.
- Real fixtures are sanitized and exclude local absolute paths, cache paths, and artifact physical paths.
