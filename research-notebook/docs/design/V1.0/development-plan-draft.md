# ResearchNotebook V1.0 Development Plan Draft

Date: 2026-05-17

## 1. Project Positioning

`research-notebook` is the independent application-layer repository for ResearchNotebook.

It owns:

- end-user UI;
- route structure;
- interaction behavior;
- product state;
- product-facing pages;
- Stitch prototype implementation;
- API integration with the local `data_service` backend.

It does not own:

- local knowledge governance internals;
- retrieval/indexing implementation;
- GraphRAG or LLMWiki storage layout;
- backend governance console behavior under `/knowledge`;
- raw artifact filesystem access.

`data_service` remains the local knowledge governance and retrieval service.

## 2. Source Inputs

This plan is based on:

- `workspace/data_service/docs/ResearchNotebook-backend-service-baseline.md`;
- Stitch project: `https://stitch.withgoogle.com/projects/5501162743214630907`;
- current repository state: empty application repository under `workspace/research-notebook`.
- product interaction references: NotebookLM for source-grounded AI workflow, and Obsidian for workspace, graph, backlink, and local-first interaction patterns.

The Stitch project currently exposes these key screens:

- `工作区主页 - 布局优化版`;
- `工作区主页 - 中文版`;
- `AI 研究工作台 - 中文版精校版`;
- `AI 研究工作台 - 精准还原版`;
- `Notebook AI Workspace Flow`;
- one uploaded PRD markdown artifact.

The Stitch design system is light-mode-first, Material-influenced, uses Roboto Flex, a fixed 280px sidebar, and a fluid main canvas.

## 3. P0 Product And Contract Constraints

These constraints apply before and during all V1.0 implementation work.

### 3.1 Repository Boundary

Keep the repository split:

- `research-notebook`: independent frontend application repository;
- `data_service`: independent backend service repository;
- `/knowledge`: `data_service` governance console, not ResearchNotebook product UI.

ResearchNotebook must:

- call target routes under `/api/workspaces/...`;
- avoid `/api/v1/knowledge/*` for new features;
- avoid raw filesystem paths, cache paths, and artifact physical paths;
- keep `shared/api/dataServiceClient.ts` as the only route-shape layer;
- use `operation_id` polling for long-running build workflows.

### 3.2 Data Service Version And Contract Strategy

`data_service` must expose OpenAPI or an equivalent machine-readable schema before frontend integration becomes broad.

ResearchNotebook must use one of:

- typed client generation from the service schema;
- runtime validation against schema-derived types;
- a checked adapter layer that is contract-tested against representative service responses.

Frontend behavior must include:

- health check state;
- backend unavailable state;
- backend version mismatch state;
- schema/capability mismatch state;
- graceful unsupported-feature state.

Contract tests must cover:

- route availability for target routes;
- normalized error envelope mapping;
- `artifact_ref` handling;
- `operation_id` polling;
- no calls to `/api/v1/knowledge/*` from new product code.

### 3.3 Product Interaction Reference

NotebookLM is the primary reference for source-grounded AI workflows:

- source-first workspace;
- answer grounded in selected/imported sources;
- inline citations and evidence affordances;
- source panel beside AI output;
- study-oriented generated outputs as a future direction.

Obsidian is the secondary reference for knowledge workspace interactions:

- fast workspace switching;
- local-first mental model;
- graph and neighborhood exploration;
- backlinks/contextual references;
- dense but calm research interface.

ResearchNotebook must not copy Obsidian's filesystem coupling. All product behavior must be based on service identifiers such as `workspace_id`, `source_id`, `unit_id`, `artifact_ref`, and `evidence_refs`.

## 4. Recommended Stack

Recommended V1.0 stack:

- Vite;
- React;
- TypeScript;
- React Router;
- TanStack Query;
- Zustand or lightweight React Context for app-local UI state;
- CSS Modules or Tailwind, with explicit design tokens extracted from Stitch;
- Vitest for unit tests;
- Playwright for smoke/e2e checks after interactive pages exist.

Tauri or another desktop shell should be deferred until the web application integration surface is stable.

## 5. Proposed Repository Structure

```text
src/
  app/
    layout/
    providers/
    routes/
  features/
    workspaces/
    sources/
    source-preview/
    build/
    query/
    sessions/
    graph/
    quality/
    assessment/
  shared/
    api/
    components/
    design-system/
    hooks/
    types/
```

Key rules:

- `shared/api/dataServiceClient.ts` is the only layer that knows the backend base URL and route shapes.
- Feature modules call typed API wrappers, not raw `fetch`.
- Pages store stable service identifiers only.
- UI never depends on backend internal paths.
- Long-running operations use a shared polling component or hook.
- Format-specific UI is driven by a `data_service` capability manifest, not hard-coded frontend assumptions.
- `features/assessment/` is a future shell only in V1.0: it may contain type drafts, route placeholders, UI prototypes, and documentation, but must not ship mock question generation, scoring, or mastery profile as product capability.

## 6. Design System Implementation

Create a local token layer from Stitch:

- primary: `#0b57d0`;
- background/surface: `#f8f9fa`, `#ffffff`, `#f3f4f5`, `#edeeef`;
- text: `#191c1d`, `#424654`;
- outline: `#737785`, `#c3c6d6`;
- radius: 4px, 8px, 12px, 16px, 24px;
- spacing base: 8px;
- sidebar width: 280px;
- font: Roboto Flex.

Core layout:

- application shell with fixed left navigation;
- main content canvas;
- optional right evidence/graph panel;
- dense, quiet, work-focused screens;
- no marketing landing page as the first experience.
- NotebookLM-like source/evidence adjacency in AI workflows;
- Obsidian-like graph/backlink affordances without filesystem coupling.

## 7. Page Plan And Backend Mapping

### 7.1 Home / Workspace Home

Purpose:

- top-level ResearchNotebook entry;
- workspace/notebook overview.

Backend routes:

- `GET /api/workspaces`;
- `POST /api/workspaces`;
- `GET /api/workspaces/{workspace_id}`;
- `GET /api/workspaces/{workspace_id}/sessions`.

V1.0 features:

- workspace list;
- create workspace;
- recent active workspace summary;
- recent sessions;
- empty state;
- blocked/error state.

### 7.2 Workspace Page

Purpose:

- manage one workspace's sources, build lifecycle, and workspace-level query.

Backend routes:

- `GET /api/workspaces/{workspace_id}`;
- `GET /api/workspaces/{workspace_id}/sources`;
- `POST /api/workspaces/{workspace_id}/sources`;
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`;
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`;
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`;
- `POST /api/workspaces/{workspace_id}/build/start`;
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`;
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`;
- `POST /api/workspaces/{workspace_id}/query`;
- `POST /api/workspaces/{workspace_id}/distill`.

V1.0 features:

- source list;
- source import;
- source detail drawer/page;
- provenance/trace view;
- build start/status/cancel;
- ask/search UI;
- answer/result rendering with source-level citation affordances;
- citation click opens source trace/provenance drawer;
- missing precise locators degrade to source-level evidence;
- distill/summary action.

### 7.3 Research Workbench

Purpose:

- focused research session workflow matching the Stitch `AI 研究工作台` direction.

Backend routes:

- `POST /api/workspaces/{workspace_id}/sessions`;
- `GET /api/workspaces/{workspace_id}/sessions`;
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`;
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`;
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`.

V1.0 features:

- create session;
- list/switch recent sessions;
- session overview;
- session note/snippet ingest;
- session-scoped ask;
- session build start/status/cancel;
- three-panel workbench layout: source/session context, main conversation/canvas, evidence/graph panel.

### 7.4 Graph Panel

Purpose:

- read-only graph exploration inside workspace or session context.

Backend routes:

- `GET /api/workspaces/{workspace_id}/graph/neighbors`;
- `GET /api/workspaces/{workspace_id}/graph/community`;
- `GET /api/workspaces/{workspace_id}/graph/query`;
- `GET /api/workspaces/{workspace_id}/graph/session`.

V1.0 features:

- entity neighborhood panel;
- topic/community panel;
- graph search/filter;
- session graph artifact inspection;
- missing artifact state.

Graph routes should be treated as bounded read surfaces, not as arbitrary traversal DSLs.

### 7.5 Quality / Governance Page

Purpose:

- lightweight product-facing feedback and correction review surface.
- This is not a primary V1.0 product destination and must not make ResearchNotebook feel like a backend governance console.

Backend routes:

- `POST /api/workspaces/{workspace_id}/quality/feedback`;
- `GET /api/workspaces/{workspace_id}/quality/correction-rules`;
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`;
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`;
- `GET /api/workspaces/{workspace_id}/quality/correction-plan`;
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`;
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`.

V1.0 features:

- thumbs up/down or correction suggestion;
- optional correction rules read-only list behind a secondary entry point.

Post-V1 or advanced features:

- propose correction rule;
- approve/reject proposed rule;
- correction plan view/generate;
- correction rules artifact build.

Important boundary:

- correction apply/execution is not implemented in `data_service` V1.6;
- approval does not mean correction has been applied;
- plan generation does not execute corrections.

### 7.6 Source Preview And Evidence Navigation

Purpose:

- let users inspect imported sources and jump from AI answers back to evidence.

Backend dependency:

- V1.0 can show source metadata and trace data from existing source routes;
- V1.0 must include a degraded source-level evidence flow through source trace/provenance drawers;
- full preview and precise citation backjump require a normalized source intermediate model from `data_service`;
- unsupported preview states must be driven by capability metadata.

Future features:

- source preview panel;
- citation backjump;
- `EvidenceSpan` rendering;
- page/slide/timestamp/json path navigation where provided by backend.

### 7.7 Assessment Studio

Purpose:

- future learning and interview-prep workflow based on imported technical knowledge.

Boundary:

- Assessment is not Quality Governance;
- V1.0 does not implement interview assessment, mastery profile, scoring, or question generation as ready product features.

Future domain objects:

- `Question`;
- `Assessment`;
- `Attempt`;
- `MasteryProfile`.

Future requirements:

- every generated question must include `evidence_refs`;
- generation must support selected sources, topic, difficulty, and question type;
- attempts must produce score, feedback, weak points, and review source links.

## 8. Multi-format Ingestion Roadmap

V1.0:

- basic source import;
- build/index lifecycle;
- workspace/session query;
- no claim of full JSON/PPT/video/audio ingestion readiness.

V1.1:

- source preview;
- citation backjump;
- evidence navigation based on normalized `DocumentUnit` and `EvidenceSpan` data.

V1.2:

- parser capability expansion in `data_service` for JSON, PPT, video, and audio;
- frontend format affordances driven by capability manifest;
- unsupported or partially supported formats shown as explicit UI states.

Frontend rule:

- never hard-code supported source formats as product truth;
- read service capability metadata and adapt upload, preview, and evidence navigation accordingly.

## 9. Normalized Source Intermediate Model

ResearchNotebook should consume normalized source/evidence concepts from `data_service`.

Core concepts:

- `Source`: user-imported logical source;
- `DocumentUnit`: backend-normalized content unit within a source;
- `EvidenceSpan`: answer/question/summary evidence range;
- `artifact_ref`: stable service-owned artifact reference.

Locator fields may include:

- `source_id`;
- `unit_id`;
- `page_no`;
- `slide_no`;
- `timestamp`;
- `json_path`.

Locator presence depends on backend parser capability and source type. The frontend must render absent locator fields gracefully.

## 10. Milestones

V1.0 priority order:

1. Home;
2. Workspace source library;
3. source import;
4. build status;
5. ask with source-level evidence;
6. source trace/provenance drawer;
7. session workbench;
8. graph read-only context;
9. lightweight feedback entry.

Quality/Governance must remain secondary in V1.0.

### M0: Scaffold And Design System

Tasks:

- initialize Vite React TypeScript project;
- configure lint/build/test;
- define app route skeleton;
- create Stitch-derived design tokens;
- implement `AppShell`;
- add static/mocked Home and Workbench screens.

Acceptance:

- local dev server runs;
- build succeeds;
- Home and Workbench shells visually follow the Stitch layout direction;
- design tokens live in a documented file.
- service health/version mismatch UI shell exists, even if backed by mock data before the backend exposes schema metadata.

### M1: API Adapter And Workspace Home

Tasks:

- implement typed `dataServiceClient`;
- implement workspace list/create/detail API wrappers;
- connect TanStack Query;
- render loading, empty, and normalized error states.

Acceptance:

- Home calls `GET /api/workspaces`;
- creating a workspace calls `POST /api/workspaces`;
- app does not call `/api/v1/knowledge/*`;
- no raw backend paths are displayed as application state.
- API adapter has contract tests or runtime validation stubs ready for schema integration.

### M2: Sources, Build, Query

Tasks:

- source list/import/detail;
- source remove;
- source trace/provenance view;
- workspace build start/status/cancel;
- operation polling hook;
- workspace query and result display;
- source-level citations in query results;
- citation click opens source trace/provenance drawer;
- source-level fallback when precise page/slide/timestamp/json locators are unavailable;
- distill action.

Acceptance:

- source lifecycle works against target routes;
- build operation renders `queued / running / completed / failed / cancelled`;
- query results render with evidence/citation affordances;
- query results are not plain chat output: every supported answer view exposes source-level evidence or an explicit "no evidence available" state;
- citation/provenance drawer uses `source_id` and trace route, not raw paths;
- failed operations show user-facing error states.
- no source format support is hard-coded as product truth.

### M3: Research Workbench

Tasks:

- session create/list/detail/close/delete;
- session ingest;
- session query;
- session query results show source-level citation affordances where returned by the service;
- session evidence opens the same source trace/provenance drawer pattern used by workspace query;
- session build lifecycle;
- active session state;
- workbench three-panel UI.

Acceptance:

- session workflow is usable end to end;
- workspace query and session query remain separate;
- session operation polling reuses the shared operation layer.
- AI answer UI reserves room for source-grounded evidence and citation backjump.

### M4: Graph And Quality

Tasks:

- graph community/neighbors/query/session panel;
- lightweight quality feedback entry;
- optional correction rule read-only list as secondary UI;
- defer correction rule write/review, correction plan generate, and correction rules build unless explicitly needed for service validation.

Acceptance:

- missing graph/session artifacts are handled explicitly;
- quality page never implies correction apply exists;
- Quality/Governance does not become a primary navigation destination in V1.0;
- each UI action maps to a documented route or app-local state.

### M5: Source Preview And Evidence Navigation

Tasks:

- add source preview shell;
- render normalized evidence spans when available;
- support citation backjump to source/unit/page/slide/timestamp/json path when backend provides locators;
- show unsupported preview state based on service capability metadata.

Acceptance:

- citation UI never requires raw filesystem paths;
- missing locators degrade to source-level evidence;
- preview availability is capability-driven.

### M6: Multi-format Source Ingestion Foundation

Tasks:

- consume `data_service` capability manifest once available;
- adapt upload affordances to supported/unsupported formats;
- add explicit partial-support states for JSON, PPT, video, and audio;
- document backend parser capability requirements.

Acceptance:

- frontend does not claim JSON/PPT/video/audio full ingestion ready unless service capability says so;
- unsupported formats have clear product states;
- build/query workflow remains stable for basic sources.

### M7: Assessment Studio

Tasks:

- define future frontend domain model for `Question`, `Assessment`, `Attempt`, and `MasteryProfile`;
- design assessment generation UI around selected sources, topic, difficulty, and question type;
- require evidence-backed questions;
- design answer review UI with score, feedback, weak points, and review sources.

Acceptance:

- V1.0 documentation clearly marks Assessment Studio as future backend phase;
- Assessment is not mixed with Quality Governance;
- no mastery profile or interview assessment is presented as ready.

## 11. MVP Scope

Recommended first implementation scope:

- Home: workspace list and create;
- Workspace: source list, source detail, import, build status, ask with source-level evidence, source trace/provenance drawer;
- Workbench: create session, ingest snippet, session query with evidence affordances;
- Graph: read-only community and neighbors;
- Quality: lightweight feedback entry, with correction rules read-only list only if it does not displace source-grounded ask work.

Out of scope for V1.0:

- user accounts;
- authentication;
- cloud sync;
- collaboration;
- rich text editor persistence model;
- document version history;
- first-class tag/folder/favorites backend objects;
- JSON/PPT/video/audio full ingestion readiness;
- interview assessment readiness;
- mastery profile readiness;
- correction apply/execution;
- full mobile UX;
- hosted SaaS hardening.

## 12. Required Documentation

Before adding new backend assumptions, maintain:

- `docs/design/V1.0/feature-route-matrix.md`;
- `docs/design/V1.0/source-intermediate-model.md`;
- `docs/roadmap/multi-format-ingestion-contract.md`;
- `docs/roadmap/assessment-service-contract.md`;
- API adapter type definitions;
- normalized error-state mapping;
- operation polling behavior notes;
- design token source notes.

Every product feature should be classified as one of:

- backed by `data_service` target route;
- app-local state;
- unsupported in V1.0;
- future backend phase.
