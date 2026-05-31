# ResearchNotebook Backend Service Baseline

Date: 2026-05-17

## 1. Decision

The current `data_service` project can serve as the backend / service-side foundation for a new `ResearchNotebook` application-layer repository under the workspace.

This decision assumes `ResearchNotebook` is responsible for end-user product UI, routing, interaction design, and any product-only state, while `data_service` remains the local knowledge governance and retrieval service.

The recommended architecture is:

- `ResearchNotebook`: personal knowledge base application layer.
- `data_service`: complete local backend/service-side knowledge system.
- `/knowledge`: remains the `data_service` service governance console, not the ResearchNotebook end-user app.

## 2. Current Backend Readiness

`data_service` V1.6 has reached final release candidate acceptance.

Current accepted service surface:

- target HTTP route count: 35
- MCP tool count: 40
- CLI top-level commands: `build / graph / quality / query / source / trace / workspace`
- compatibility HTTP: `/api/v1/knowledge/*` retained
- public-surface baseline: V1.5 immutable baseline remains unchanged
- `/knowledge`: service governance console
- correction apply / execution target HTTP: not implemented
- V1.7 ResearchNotebook source-level preview contract: implemented for capability manifest and text source preview
- V1.7+ future capabilities beyond source-level preview: planned only

The backend is suitable for:

- creating and managing knowledge workspaces;
- importing and managing source materials;
- running build/index lifecycle operations;
- querying and distilling knowledge;
- exposing graph inspection and graph query surfaces;
- managing session-scoped research workflows;
- ingesting, querying, and building session knowledge;
- collecting and governing quality feedback / correction rules / review / plan / rules build;
- providing stable non-path artifact references for application consumption;
- exposing a V1.7 source-level preview contract for ResearchNotebook V1.1-B.

## 3. What ResearchNotebook Should Own

ResearchNotebook should own:

- homepage and workbench UI;
- navigation and route structure;
- notebook/project-level product language;
- end-user knowledge consumption views;
- document/card/list layouts;
- upload/import UX;
- search and ask UI;
- reading, preview, and annotation UX if needed;
- graph visualization UX;
- session/research workflow UX;
- local UI preferences and view state;
- product onboarding and empty states.

ResearchNotebook should not require `data_service` to change `/knowledge` into a user-facing app. `/knowledge` remains the backend governance console.

## 4. What Data Service Provides

### Workspace Lifecycle

Use workspace routes for top-level notebooks, libraries, or research spaces.

Routes:

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`

Recommended ResearchNotebook mapping:

- notebook/library create -> `POST /api/workspaces`
- notebook list/homepage -> `GET /api/workspaces`
- notebook overview -> `GET /api/workspaces/{workspace_id}`
- archive notebook -> `POST /api/workspaces/{workspace_id}/archive`

### Source Lifecycle

Use source routes for imported files, notes, references, and source documents.

Routes:

- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- `GET /api/workspaces/{workspace_id}/capabilities`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview`

Recommended ResearchNotebook mapping:

- import document/source -> `POST /api/workspaces/{workspace_id}/sources`
- source library/list -> `GET /api/workspaces/{workspace_id}/sources`
- source detail drawer/page -> `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- remove source -> `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`
- citation / provenance / why-this-result -> `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- source-level preview availability -> `GET /api/workspaces/{workspace_id}/capabilities`
- source-level preview drawer -> `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview`

### Build Lifecycle

Use build routes for indexing/materialization operations triggered by the application.

Routes:

- `POST /api/workspaces/{workspace_id}/build/start`
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

Recommended ResearchNotebook mapping:

- rebuild notebook knowledge -> `POST /api/workspaces/{workspace_id}/build/start`
- operation progress panel -> `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- cancel build -> `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

### Query And Distill

Use query/distill routes for core knowledge search and answer generation.

Routes:

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`

Recommended ResearchNotebook mapping:

- ask/search box -> `POST /api/workspaces/{workspace_id}/query`
- concept/card/summary generation -> `POST /api/workspaces/{workspace_id}/distill`

### Graph Advanced

Use graph routes for graph workbench views.

Routes:

- `GET /api/workspaces/{workspace_id}/graph/neighbors`
- `GET /api/workspaces/{workspace_id}/graph/community`
- `GET /api/workspaces/{workspace_id}/graph/query`
- `GET /api/workspaces/{workspace_id}/graph/session`

Recommended ResearchNotebook mapping:

- entity neighborhood panel -> graph neighbors
- topic/community panel -> graph community
- graph search/filter panel -> graph query
- session graph artifact inspection -> graph session

Boundary:

- graph routes are minimal, bounded surfaces;
- graph routes should not be treated as arbitrary graph traversal DSLs;
- graph session inspection is not session lifecycle.

### Session Lifecycle

Use session routes for research sessions, focused notebooks, temporary investigation contexts, or project workbench sessions.

Routes:

- `POST /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`

Recommended ResearchNotebook mapping:

- start research session -> create session
- recent sessions -> list sessions
- session overview -> get session
- finish session -> close session
- remove/deactivate session -> delete session

### Session Ingest / Query / Build

Use session-scoped routes for research workbench flows.

Routes:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`

Recommended ResearchNotebook mapping:

- add note/snippet to active research session -> session ingest
- ask within current research session -> session query
- build session graph/knowledge artifacts -> session build start
- show session build progress -> session build status
- cancel session build -> session build cancel

Boundaries:

- session ingest is session-scoped write, not workspace source import;
- session query is session-scoped read-only operation;
- session build is session-scoped operation lifecycle, not workspace-level build.

### Quality Governance

Use quality routes for user feedback, correction proposals, review workflows, and plan inspection.

Routes:

- `POST /api/workspaces/{workspace_id}/quality/feedback`
- `GET /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`
- `GET /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`

Recommended ResearchNotebook mapping:

- thumbs up/down or correction suggestion -> quality feedback
- correction rule list -> correction rules list
- propose correction rule -> correction rules write
- approve/reject proposed rule -> correction rule review
- inspect correction plan -> correction plan read
- generate correction plan -> correction plan generate
- rebuild correction-rules artifact from feedback -> correction rules build

Boundaries:

- correction apply / execution is not implemented in V1.6;
- review approval does not mean active/applied;
- correction plan generation does not execute corrections;
- correction rules build does not apply corrections.

## 5. Integration Contract For ResearchNotebook

### Service Role

`data_service` should be treated as the local knowledge backend service.

ResearchNotebook should call target HTTP routes under:

```text
/api/workspaces/...
```

Legacy compatibility routes under `/api/v1/knowledge/*` are retained for compatibility but should not be the primary integration target for a new application.

### Identifier Model

ResearchNotebook should store and pass stable service identifiers:

- `workspace_id`
- `source_id`
- `operation_id`
- `session_id`
- `rule_id`
- stable `artifact_ref` / `artifact_refs`

ResearchNotebook should not depend on:

- workspace filesystem layout;
- raw local paths;
- cache paths;
- artifact physical paths;
- raw GraphRAG or LLMWiki storage layout.

### Artifact References

Artifact references are service-owned stable references. The application should display them only when useful for debugging or evidence, and should not attempt to read filesystem artifacts directly.

Examples of expected stable reference patterns:

- workspace/source/session refs;
- graph refs;
- quality correction rule refs;
- quality correction plan refs;
- session build refs.

### Error Handling

ResearchNotebook should expect normalized error envelopes from target HTTP routes. Application UI should map these to:

- blocked state;
- not found state;
- validation error;
- archived workspace state;
- missing graph/session artifact state;
- operation unavailable state.

ResearchNotebook should not infer failure cause from raw backend exceptions or internal paths.

### Long-Running Operations

Build routes and session build routes return real `operation_id` values. ResearchNotebook should poll operation status routes and provide cancel actions where available.

Recommended UI pattern:

1. call `start`;
2. persist `operation_id` in local UI state;
3. poll status route;
4. render `queued / running / completed / failed / cancelled`;
5. call cancel only for cancellable operations.

## 6. Suggested ResearchNotebook Pages

### Home Page

Backend-backed widgets:

- workspace list: `GET /api/workspaces`
- recent active workspace summary: `GET /api/workspaces/{workspace_id}`
- source count: `GET /api/workspaces/{workspace_id}/sources`
- recent sessions: `GET /api/workspaces/{workspace_id}/sessions`
- quality state summary: correction rules / plan routes where needed

### Workspace Page

Backend-backed widgets:

- workspace metadata: `GET /api/workspaces/{workspace_id}`
- source list: `GET /api/workspaces/{workspace_id}/sources`
- build controls: workspace build routes
- ask/search: workspace query route
- distill/summary: distill route

### Research Workbench Page

Backend-backed widgets:

- session lifecycle: session routes
- session note/snippet ingest: session ingest
- session ask: session query
- session graph build/progress: session build routes
- graph visualization: graph neighbors/community/query/session

### Quality / Governance Page

Backend-backed widgets:

- feedback submission
- correction rule list/write/review
- correction plan read/generate
- correction rules build

This page can be product-facing, while `/knowledge` remains the service governance console.

## 7. Current Gaps For A Full Product App

The backend is sufficient for a serious application-layer prototype and local-first ResearchNotebook MVP, but the following are not provided by `data_service` V1.6:

- user accounts / authentication / multi-user authorization;
- cloud sync;
- collaboration;
- rich text editor storage model;
- document version history;
- tag/folder/favorites as first-class product objects, unless mapped to metadata/source/session conventions;
- correction apply / execution;
- frontend product shell;
- mobile UX;
- hosted SaaS deployment hardening.

If ResearchNotebook requires these, they should be planned as application-layer features or future backend phases with explicit public-surface overlays.

## 8. Development Recommendation

Recommended next step:

1. Create `workspace/ResearchNotebook` as the application-layer repository.
2. Keep `data_service` as a sibling backend service repository.
3. Build the first ResearchNotebook frontend against the 35 accepted target HTTP routes.
4. Do not modify `/knowledge` into the product app.
5. Add a ResearchNotebook API adapter layer that wraps target HTTP calls.
6. Add a feature-to-route matrix before introducing any new backend route.

Suggested first milestone:

- homepage: workspace list + create workspace;
- workbench: source list + source import + build status + query;
- session panel: create session + session ingest + session query;
- graph panel: graph community / neighbors read-only view;
- quality panel: feedback + correction rules read-only list.

## 9. Acceptance Criteria For ResearchNotebook Integration

ResearchNotebook should be considered properly integrated when:

- it uses target HTTP routes rather than legacy compatibility routes for new features;
- it never depends on raw internal paths;
- it treats `artifact_ref` as service-owned stable reference;
- it keeps `/knowledge` as governance console;
- it handles normalized errors;
- it polls operation status for build/session build;
- it does not assume correction apply exists;
- it has a documented mapping from every UI feature to a backend route or app-local state.

## 10. Final Assessment

Current `data_service` satisfies the backend/service-side requirements for starting ResearchNotebook as a personal knowledge base application layer.

The correct product architecture is not to replace `data_service` frontend governance console, but to build ResearchNotebook as a separate application consuming `data_service` target HTTP APIs.

If the Stitch prototype requires only personal knowledge homepage, workspace, source import/list, search/ask, graph exploration, session workbench, and quality feedback/review/plan surfaces, the current backend is sufficient.

If the prototype requires accounts, cloud sync, collaboration, rich document editing, or correction apply, those are outside the current V1.6 backend baseline and should be planned separately.
