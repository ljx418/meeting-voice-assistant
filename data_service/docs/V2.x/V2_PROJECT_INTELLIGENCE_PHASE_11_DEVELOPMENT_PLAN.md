# V2 Phase 11 Development Plan: Minimum Read-only Frontend

> Generated before implementation.
> Phase 11 must consume backend V2.1 APIs; the frontend must not become a source of truth.

## 1. Phase Goal

Add a minimum read-only Project Intelligence review surface to the existing Knowledge Console.

The frontend should help humans audit DevWiki, Code Graph, Code Quality, and Agent Context Pack outputs produced by V2.0 and V2.1 backend services.

## 2. Scope

In scope:

- Read-only Project Intelligence panel or section in the existing console.
- Display backend-provided DevWiki page list/detail.
- Display backend-provided Code Graph summary and Mermaid text.
- Display backend-provided Code Quality summary and plan impact.
- Display Agent Context Pack readback or summary.
- Display `evidence`, `needs_review`, `unresolved`, `stale`, `quality_warnings`, `applied_rules`, and `governed_by` if present.
- Use backend API responses as authoritative facts.
- Frontend build and focused static-contract tests.

Out of scope:

- Editing DevWiki pages.
- Editing graph nodes/edges.
- Applying quality rules from the frontend.
- Interactive graph editor.
- Local recomputation of graph, quality, evidence, confidence, or stale state.

## 3. Backend APIs to Consume

Phase 11 should consume existing APIs:

```text
GET  /api/workspaces/{workspace_id}/codebases
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages/{page_slug}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}
```

If a required artifact is missing, the UI must show backend `next_actions` or structured error content instead of hiding the state.

## 4. Frontend Design

Preferred implementation:

- Keep changes in the existing frontend app.
- Add focused Project Intelligence components if the page is already large.
- Avoid frontend-only derived claims.
- Use dense, review-oriented layout, not marketing content.

Suggested component split:

```text
frontend/src/components/project-intelligence/
  ProjectIntelligencePanel.vue
  DevWikiReadOnly.vue
  CodeGraphReadOnly.vue
  CodeQualityReadOnly.vue
  AgentContextReadOnly.vue
```

If introducing new components is too invasive, a single focused section in `KnowledgePage.vue` is acceptable for Phase 11, but it must remain read-only.

## 5. Required UI States

- no workspace selected
- no codebase selected
- artifact missing
- stale artifact
- needs review
- unresolved items
- quality overlay present
- loading
- backend error

## 6. Implementation Steps

1. Inspect current Knowledge Console component boundaries.
2. Add typed API client helpers if existing frontend client patterns support them.
3. Add read-only Project Intelligence section.
4. Wire workspace/codebase selection to backend APIs.
5. Display DevWiki, Graph, Quality, and Context summaries.
6. Display backend-provided risk signals.
7. Add frontend/static tests or contract assertions.
8. Run `npm run build --prefix frontend`.
9. Run backend public surface and full regression tests.

## 7. Stop Conditions

Stop and request human confirmation if:

- frontend needs to invent facts not present in backend payloads
- frontend hides `needs_review`, `unresolved`, or `stale`
- frontend mutates V2.1 artifacts
- implementation requires large unrelated redesign of `KnowledgePage.vue`
- Playwright/screenshot validation shows unreadable or overlapping critical text
