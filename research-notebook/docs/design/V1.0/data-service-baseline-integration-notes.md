# ResearchNotebook Data Service Baseline Integration Notes

Date: 2026-05-17

Source baseline:

- `../data_service/docs/ResearchNotebook-backend-service-baseline.md`

## 1. Core Understanding

The current `data_service` V1.6 baseline is sufficient to start ResearchNotebook as a separate application-layer repository.

The correct architecture is:

- `research-notebook`: end-user personal knowledge application;
- `data_service`: local backend/service-side knowledge system;
- `/knowledge`: backend governance console, not the ResearchNotebook product UI.

ResearchNotebook should consume the accepted target HTTP routes and should not reshape the existing `/knowledge` console into the product app.

`data_service` should continue as a separate service repository. ResearchNotebook should not implement parser, indexing, retrieval, graph, governance, or assessment engine internals in the frontend repository.

## 2. Backend Readiness

The baseline states that `data_service` V1.6 has reached final release candidate acceptance.

Accepted service surface:

- target HTTP route count: 35;
- MCP tool count: 40;
- CLI top-level commands: `build / graph / quality / query / source / trace / workspace`;
- compatibility HTTP routes under `/api/v1/knowledge/*` retained;
- `/knowledge` remains the service governance console;
- correction apply/execution target HTTP not implemented;
- V1.7 and future capabilities are planned only.

Implication for ResearchNotebook:

- build the app against `/api/workspaces/...`;
- do not use legacy compatibility routes for new features;
- do not assume planned V1.7 behavior exists.
- do not present future parser or assessment capabilities as ready until they appear in the public service contract.

## 3. Service Ownership Boundary

ResearchNotebook owns product experience:

- homepage;
- workbench;
- navigation;
- notebook/workspace language;
- source import UX;
- search and ask UX;
- reading, preview, annotation UX if implemented;
- graph visualization UX;
- research session UX;
- local UI preferences;
- empty states and product onboarding.

`data_service` owns knowledge backend capabilities:

- workspace lifecycle;
- source lifecycle;
- indexing/build lifecycle;
- workspace query;
- distillation;
- graph inspection;
- session lifecycle;
- session ingest/query/build;
- quality feedback and correction rule governance;
- stable artifact references.

ResearchNotebook should not own or infer:

- workspace filesystem layout;
- raw local file paths;
- cache paths;
- artifact physical paths;
- GraphRAG storage internals;
- LLMWiki storage internals.

Product interaction references:

- NotebookLM should guide source-grounded AI interaction: source panel, evidence-backed answers, inline citations, and study-oriented generated outputs.
- Obsidian should guide workspace, graph, backlink, and local-first interaction patterns.
- Obsidian's filesystem coupling should not be copied. ResearchNotebook remains service-identifier based.

## 4. Service Contract Strategy

`data_service` should expose OpenAPI or an equivalent machine-readable schema for the `/api/workspaces/...` target routes.

ResearchNotebook integration should use one of:

- generated TypeScript client from schema;
- runtime validation against schema-derived types;
- contract-tested typed adapter functions.

`shared/api/dataServiceClient.ts` remains the only frontend layer that knows route shapes.

The frontend must include UI states for:

- backend health check failed;
- backend unavailable;
- backend version too old;
- schema mismatch;
- capability missing;
- operation unavailable.

Contract tests should verify:

- target route request/response shapes;
- normalized error envelopes;
- `operation_id` polling lifecycle;
- `artifact_ref` handling;
- absence of new `/api/v1/knowledge/*` calls.

## 5. Capability Manifest Strategy

Future multi-format and preview behavior must be driven by a `data_service` capability manifest or equivalent contract.

The frontend must not hard-code product truth for:

- supported upload formats;
- previewable source types;
- citation locator types;
- parser readiness;
- assessment generation readiness.

Expected capability categories:

- basic source import;
- source preview;
- evidence locator support;
- JSON parsing;
- PPT parsing;
- video parsing/transcription;
- audio parsing/transcription;
- assessment generation.

Unsupported or partially supported capabilities should render explicit UI states instead of hidden failures.

## 6. Identifier And Artifact Model

The application must store and pass stable service identifiers:

- `workspace_id`;
- `source_id`;
- `operation_id`;
- `session_id`;
- `rule_id`;
- `artifact_ref`;
- `artifact_refs`.

Artifact references are service-owned stable references.

Application behavior:

- display artifact refs only when useful for evidence/debugging;
- pass artifact refs back to service routes where appropriate;
- never read artifact files directly from disk;
- never convert artifact refs into local filesystem assumptions.

## 7. Normalized Source Intermediate Model

ResearchNotebook should consume normalized source and evidence data from `data_service`, instead of file-format-specific internals.

Core concepts:

- `Source`: user-imported logical source.
- `DocumentUnit`: backend-normalized unit inside a source, such as page, slide, transcript segment, JSON node, section, or chunk.
- `EvidenceSpan`: evidence range used by answers, summaries, or future assessment questions.
- `artifact_ref`: stable service-owned reference for derived artifacts.

Evidence locators may include:

- `source_id`;
- `unit_id`;
- `page_no`;
- `slide_no`;
- `timestamp`;
- `json_path`.

Frontend rules:

- render absent locator fields gracefully;
- allow source-level fallback when precise spans are unavailable;
- never infer locators from physical file paths;
- use evidence refs for answer citation, citation backjump, source preview, and future assessment review.

## 8. Route Groups And Product Mapping

### Workspace Lifecycle

Routes:

- `POST /api/workspaces`;
- `GET /api/workspaces`;
- `GET /api/workspaces/{workspace_id}`;
- `POST /api/workspaces/{workspace_id}/archive`.

ResearchNotebook mapping:

- create notebook/library;
- list notebooks on Home;
- workspace overview;
- archive notebook.

### Source Lifecycle

Routes:

- `POST /api/workspaces/{workspace_id}/sources`;
- `GET /api/workspaces/{workspace_id}/sources`;
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`;
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`;
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`.

ResearchNotebook mapping:

- import source/document;
- source library;
- source detail;
- remove source;
- citation/provenance/trace view.

### Build Lifecycle

Routes:

- `POST /api/workspaces/{workspace_id}/build/start`;
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`;
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`.

ResearchNotebook mapping:

- rebuild workspace knowledge;
- operation progress panel;
- cancel build.

### Query And Distill

Routes:

- `POST /api/workspaces/{workspace_id}/query`;
- `POST /api/workspaces/{workspace_id}/distill`.

ResearchNotebook mapping:

- ask/search box;
- concept/card/summary generation.

### Graph Advanced

Routes:

- `GET /api/workspaces/{workspace_id}/graph/neighbors`;
- `GET /api/workspaces/{workspace_id}/graph/community`;
- `GET /api/workspaces/{workspace_id}/graph/query`;
- `GET /api/workspaces/{workspace_id}/graph/session`.

ResearchNotebook mapping:

- entity neighborhood panel;
- topic/community panel;
- graph search/filter panel;
- session graph artifact inspection.

Boundary:

- graph routes are bounded service surfaces;
- do not treat them as an arbitrary graph traversal DSL;
- graph session inspection is not session lifecycle.

### Session Lifecycle

Routes:

- `POST /api/workspaces/{workspace_id}/sessions`;
- `GET /api/workspaces/{workspace_id}/sessions`;
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`.

ResearchNotebook mapping:

- start research session;
- list recent sessions;
- session overview;
- finish session;
- remove/deactivate session.

### Session Ingest / Query / Build

Routes:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`;
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`.

ResearchNotebook mapping:

- add note/snippet to active session;
- ask within current session;
- build session graph/knowledge artifacts;
- show session build progress;
- cancel session build.

Boundary:

- session ingest is session-scoped write;
- workspace source import is separate;
- session query is session-scoped read-only behavior;
- session build is session-scoped operation lifecycle.

### Quality Governance

Routes:

- `POST /api/workspaces/{workspace_id}/quality/feedback`;
- `GET /api/workspaces/{workspace_id}/quality/correction-rules`;
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`;
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`;
- `GET /api/workspaces/{workspace_id}/quality/correction-plan`;
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`;
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`.

ResearchNotebook mapping:

- user feedback;
- correction suggestion;
- correction rule list;
- propose correction rule;
- approve/reject rule;
- inspect/generate correction plan;
- rebuild correction-rules artifact.

Boundary:

- correction apply/execution is not implemented in V1.6;
- review approval does not mean active/applied;
- correction plan generation does not execute corrections;
- correction rules build does not apply corrections.

## 9. Assessment Studio Future Phase

Assessment Studio is a future product area for evaluating a user's understanding of imported technical knowledge.

It is not Quality Governance.

Future domain objects:

- `Question`;
- `Assessment`;
- `Attempt`;
- `MasteryProfile`.

Future backend contract requirements:

- question generation from selected sources;
- generation controls for topic, difficulty, and question type;
- each question includes `evidence_refs`;
- answer attempts return score, feedback, weak points, and review sources;
- mastery profile is derived from attempts and evidence-grounded weak points.

ResearchNotebook V1.0 must not claim:

- interview assessment ready;
- mastery profile ready;
- automated scoring ready;
- assessment route availability.

These remain future backend phases until `data_service` exposes public target routes and schema.

## 10. Multi-format Ingestion Roadmap

V1.0:

- basic source import;
- source list/detail/trace;
- build/index lifecycle;
- workspace/session query.

V1.1:

- source preview;
- evidence span rendering;
- citation backjump.

V1.2:

- JSON parser capability;
- PPT parser capability;
- video parser/transcription capability;
- audio parser/transcription capability;
- capability-driven upload and preview UI.

The frontend should be ready to display format capability states, but must not implement parser logic or claim parser readiness before `data_service` exposes it.

## 11. Error Handling Model

ResearchNotebook should expect normalized error envelopes from target HTTP routes.

UI states should include:

- blocked state;
- not found state;
- validation error;
- archived workspace state;
- missing graph artifact state;
- missing session artifact state;
- operation unavailable state;
- generic service unavailable state.

ResearchNotebook should not infer failure causes from:

- raw backend exceptions;
- internal paths;
- stack traces;
- backend implementation-specific messages.

## 12. Long-Running Operation Model

Build routes return real `operation_id` values.

Application operation flow:

1. call the relevant `start` route;
2. persist `operation_id` in app-local state;
3. poll the matching operation status route;
4. render `queued / running / completed / failed / cancelled`;
5. expose cancel only where the route exists and the operation is cancellable.

This should be implemented once as a shared operation polling hook/component and reused for workspace builds and session builds.

## 13. Product Interpretation

The backend baseline enables a serious local-first MVP.

ResearchNotebook should be designed as a personal knowledge application with these first-class workflows:

- create or select a workspace;
- import source material;
- build/index knowledge;
- ask questions against workspace knowledge;
- start a focused research session;
- ingest temporary notes/snippets into the session;
- ask session-scoped questions;
- inspect graph/community context;
- submit feedback and inspect correction governance artifacts.
- preview source/evidence when the backend exposes normalized units and locators;
- later generate study/interview assessment only after backend assessment contracts exist.

The app should avoid promising capabilities not present in V1.6:

- accounts;
- cloud sync;
- collaboration;
- rich editor persistence;
- document version history;
- first-class folders/tags/favorites unless implemented app-local or mapped to metadata;
- JSON/PPT/video/audio full ingestion;
- interview assessment;
- mastery profile;
- correction apply;
- hosted SaaS deployment guarantees.

## 14. Integration Acceptance Criteria

ResearchNotebook integration is acceptable when:

- new product features use target routes under `/api/workspaces/...`;
- no new feature depends on `/api/v1/knowledge/*`;
- UI never depends on raw internal paths;
- artifact refs are treated as service-owned references;
- `/knowledge` remains the service governance console;
- normalized errors are mapped to stable UI states;
- operation status is polled for workspace/session builds;
- correction apply is not assumed;
- every UI feature is documented in a feature-to-route matrix.
- source format support is capability-driven;
- assessment features are marked future backend phase until public routes exist.

## 15. Immediate Documentation Follow-Up

Create and maintain:

- `docs/design/V1.0/feature-route-matrix.md`;
- `docs/design/V1.0/source-intermediate-model.md`;
- `docs/design/V1.0/api-adapter-contract.md`;
- `docs/design/V1.0/error-state-model.md`;
- `docs/design/V1.0/design-system-notes.md`.

These documents should be updated before expanding backend assumptions or adding new product features.
