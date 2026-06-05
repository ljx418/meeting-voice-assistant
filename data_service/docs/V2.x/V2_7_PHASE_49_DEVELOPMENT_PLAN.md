# V2.7 Phase 49 Development Plan: Document Asset Registry

> Phase-specific development plan.
> Business code may start only after this plan and the acceptance plan have no open fatal or major audit findings.

Date: 2026-06-04

## Goal

Implement the V2.7 Document Asset Registry for architecture-relevant project documents.

## Scope

Phase 49 implements:

- document discovery from existing codebase snapshot files;
- document classification for PRD, target architecture, gap, drawio, development plan, acceptance plan, audit report, API matrix, handoff summary, README and unknown architecture docs;
- document authority metadata;
- persisted artifacts:
  - `architecture/docs/architecture_docs.jsonl`
  - `architecture/docs/architecture_doc_sources.jsonl`
- HTTP/MCP/CLI build and read access.

Phase 49 does not implement claim extraction, quality scoring, doc-code alignment, reconstruction reports or governance targets.

## Pre-Gates

- `docs/V2.x/V2_6_CLOSURE_AUDIT_REPORT.md` exists.
- Phase 49 code must not mutate V2.0-V2.6 artifacts or source registry.
- HarnessOS path `/Users/Zhuanz/Desktop/workspace/harnessOS` must be checked during real E2E; missing path cannot be accepted as HarnessOS E2E.
- Missing V2.6 artifacts are allowed to appear as pre-gate warnings, but not as mock replacements.

## Implementation Notes

- Add focused module `backend/data_service/code_assets/architecture/doc_registry.py`.
- Add persistence helpers under existing architecture persistence.
- Add path helpers under `code_assets/artifacts.py`.
- Extend existing architecture HTTP/MCP/CLI modules with thin build/read registration.

## Acceptance

Phase 49 is accepted only if focused tests and real-data checks prove:

- document registry is non-empty for `data_service` and HarnessOS;
- every document row has stable `doc_id`, `doc_type`, `path`, `phase_hint`, `version_hint`, `scope_hint`, `authority_role`, `authority_level`, `supersedes`, `superseded_by`, `evidence`, `confidence`, and `needs_review`;
- V2.7 documents are classified as current target/planning authority;
- V2.5/V2.6 documents are classified as historical or supporting, not current V2.7 target authority;
- public output has no absolute repo path;
- repeated run on same snapshot is stable.
