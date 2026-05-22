# ResearchNotebook V1.0 Feature Route Matrix

Date: 2026-05-19

## 1. Classification

Every product feature must be marked as one of:

- `backed by data_service target route`;
- `app-local state`;
- `unsupported in V1.0`;
- `future backend phase`.

Rules:

- new features must use `/api/workspaces/...` target routes;
- do not use `/api/v1/knowledge/*` for new work;
- do not read raw filesystem paths, cache paths, or artifact physical paths;
- route shapes belong only in `shared/api/dataServiceClient.ts`;
- long-running build flows must use `operation_id` polling.

## 2. V1.0 Workspace And Source Features

| Feature | Status | Backend route or dependency | Notes |
| --- | --- | --- | --- |
| Workspace list | backed by data_service target route | `GET /api/workspaces` | Home page notebook/workspace list. |
| Workspace create | backed by data_service target route | `POST /api/workspaces` | Create notebook/library/workspace. |
| Workspace detail | backed by data_service target route | `GET /api/workspaces/{workspace_id}` | Workspace overview. |
| Workspace archive | backed by data_service target route | `POST /api/workspaces/{workspace_id}/archive` | Optional V1.0 action. |
| Recent workspace selection | app-local state | local preference/state | Store stable `workspace_id` only. |
| Source list | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources` | Workspace source library. |
| Source import | backed by data_service target route | `POST /api/workspaces/{workspace_id}/sources` | V1.0 basic import only. |
| Source detail | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}` | Detail page or drawer. |
| Source remove | backed by data_service target route | `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove` | Soft/remove semantics owned by service. |
| Source trace | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace` | RC3/RC6 real smoke returned 404; after data_service backend fix, V1.1-RC4 registry `source_id` trace returned HTTP 200. V1.0 may claim scoped registry source trace for the RC4-covered path only. |
| Source trace/provenance drawer | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace` | Required V1.0 evidence flow; failure must remain drawer-local and must not clear answer. |
| Source-level citation affordance | backed by data_service target route | query response + source trace route | Query hit slugs/page refs render as non-clickable `sourceRef`; registry IDs render as traceable citations. |
| Source preview | future backend phase | capability manifest + source preview route | V1.1 docs own this surface. V1.1-B frontend integration has passed source-level text preview smoke; V1.0 release status remains unchanged and must not claim preview ready. |
| DocumentUnit outline | future backend phase | normalized `DocumentUnit` model/route | V1.1-C-A disabled shell is ready; full unit navigation remains not V1.0 ready. |
| EvidenceSpan highlight | future backend phase | normalized `EvidenceSpan` + offset semantics | V1.1-D has passed the supported text-source workspace query path smoke; V1.0 status remains unchanged. |
| Precise citation backjump | future backend phase | normalized `EvidenceSpan` locators | V1.1-D has passed a limited text-source workspace query path; session/all-source coverage remains NOT_READY. |

## 3. Build, Query, Session, Graph

| Feature | Status | Backend route or dependency | Notes |
| --- | --- | --- | --- |
| Workspace build start | backed by data_service target route | `POST /api/workspaces/{workspace_id}/build/start` | Returns `operation_id`. |
| Workspace build status | backed by data_service target route | `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}` | Poll queued/running/completed/failed/cancelled. |
| Workspace build cancel | backed by data_service target route | `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel` | Show only when cancellable. |
| Workspace query | backed by data_service target route | `POST /api/workspaces/{workspace_id}/query` | Core ask/search. |
| Workspace ask with evidence | backed by data_service target route | `POST /api/workspaces/{workspace_id}/query` + source trace route | V1.0 primary product flow. |
| Workspace distill | backed by data_service target route | `POST /api/workspaces/{workspace_id}/distill` | Summary/card generation. |
| Session create | backed by data_service target route | `POST /api/workspaces/{workspace_id}/sessions` | Start research session. |
| Session list | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sessions` | Recent sessions. |
| Session detail | backed by data_service target route | `GET /api/workspaces/{workspace_id}/sessions/{session_id}` | Session overview. |
| Session close | backed by data_service target route | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close` | Finish session. |
| Session delete | unsupported in V1.0 | deferred route contract | M3 selected close-only; delete is not a release-gate capability. |
| Session ingest | backed by data_service target route | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest` | Session-scoped write. |
| Session query | backed by data_service target route | `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query` | Session-scoped ask. |
| Session ask with evidence | backed by data_service target route | session query route + source trace route | V1.0 workbench product flow. |
| Session build lifecycle | backed by data_service target route | session build start/status/cancel routes | Uses shared polling hook. |
| Active session selection | app-local state | local UI state | Store stable `session_id` only. |
| Graph neighbors | backed by data_service target route | `GET /api/workspaces/{workspace_id}/graph/neighbors?node_id=...` or `?entity_id=...` | RC3 confirmed node-scoped neighbors pass when community members provide node ids; overview never calls neighbors without selection. |
| Graph community | backed by data_service target route | `GET /api/workspaces/{workspace_id}/graph/community?include_members=true` | Read-only topic/community view; members enable node-scoped neighbor inspection when present. |
| Graph query builder / DSL | unsupported in V1.0 | no product route in M4 | M4 is read-only context only. |
| Graph session context | backed by data_service target route | `GET /api/workspaces/{workspace_id}/graph/session` | Read-only session graph context; does not block session ask. |

## 4. Quality And Governance

| Feature | Status | Backend route or dependency | Notes |
| --- | --- | --- | --- |
| Quality feedback | backed by data_service target route | `POST /api/workspaces/{workspace_id}/quality/feedback` | Lightweight secondary V1.0 entry. |
| Correction rules list | future backend phase | governance route, not product UI | Not part of V1.0 release gate. |
| Correction rule propose | unsupported in V1.0 | governance route, not product UI | Do not expose CRUD. |
| Correction rule review | unsupported in V1.0 | governance route, not product UI | Do not expose review workflow. |
| Correction plan read | future backend phase | governance route, not product UI | Post-MVP secondary governance view only if explicitly requested. |
| Correction plan generate | unsupported in V1.0 | governance route, not product UI | Do not expose governance generation. |
| Correction rules build | unsupported in V1.0 | governance route, not product UI | Do not expose governance rebuild. |
| Correction apply/execution | unsupported in V1.0 | no V1.6 target route | Do not imply approved corrections are applied. |

## 5. Productization And Future Features

| Feature | Status | Backend route or dependency | Notes |
| --- | --- | --- | --- |
| Backend health check UI | future backend phase | service health/version route or equivalent | UI state should exist once contract is exposed. |
| Backend version mismatch UI | future backend phase | service version/schema metadata | Required before broad integration. |
| Capability manifest | future backend phase | service capability contract | V1.1-B frontend integration now consumes the manifest; V1.0 release status remains unchanged. |
| OpenAPI/schema client generation | future backend phase | OpenAPI or equivalent schema | Required for durable typed integration. |
| Runtime response validation | app-local state | schema-derived validators | May be added before generated client. |
| NotebookLM-style source-grounded layout | app-local state | UI implementation | Interaction reference, not backend route. |
| Obsidian-style graph/backlink affordances | app-local state | UI implementation + graph routes | No filesystem coupling. |
| JSON full ingestion | future backend phase | capability manifest + parser route/contract | Not V1.0 ready. |
| PPT full ingestion | future backend phase | capability manifest + parser route/contract | Not V1.0 ready. |
| Video ingestion/transcription | future backend phase | capability manifest + parser route/contract | Not V1.0 ready. |
| Audio ingestion/transcription | future backend phase | capability manifest + parser route/contract | Not V1.0 ready. |
| Rich editor persistence | unsupported in V1.0 | future app/backend design | Do not present as ready. |
| Cloud sync | unsupported in V1.0 | future backend/platform design | Out of current local-first MVP. |
| Collaboration | unsupported in V1.0 | future backend/platform design | Out of current local-first MVP. |
| Assessment Studio | future backend phase | future assessment routes/schema | V2.0 direction. |
| Question generation | future backend phase | `Question` domain + evidence refs | Not Quality Governance. |
| Attempt scoring | future backend phase | `Attempt` domain | Not V1.0 ready. |
| Mastery profile | future backend phase | `MasteryProfile` domain | Not V1.0 ready. |
