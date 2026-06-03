# V2.4 Phase 22 Development Plan: Public Views and Interface Completion

> Scope: V2.4 Phase 22 only.
> Baseline: Phase 21 code-derived model and drift artifacts are implemented and accepted.

Date: 2026-06-02

## 1. Goal

Phase 22 adds persisted Mermaid/HTML views for the code-derived architecture model and exposes view reads through HTTP/MCP/CLI.

Quality governance overlay is not implemented in Phase 22 because the current quality target resolver does not yet include V2.4 architecture role/pattern/drift target types. This avoids a false acceptance risk.

## 2. Implementation

- Render `views/code_derived_architecture.mmd`.
- Render `views/code_derived_architecture.html`.
- Add service read method for code-derived views.
- Add HTTP `GET /architecture/code/views/{view_id}`.
- Add MCP `knowledge_code_architecture_view`.
- Add CLI `knowledge code architecture code-view`.

## 3. Out of Scope

- Quality overlay for V2.4 architecture targets.
- Editing source artifacts.
- New frontend page.
- Full graph/static-analysis semantics.
