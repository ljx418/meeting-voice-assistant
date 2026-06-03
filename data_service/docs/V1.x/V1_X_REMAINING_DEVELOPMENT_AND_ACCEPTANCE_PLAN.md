# V1.x Remaining Development and Acceptance Plan

> Generated from repository analysis.
> This document is a planning baseline for V1.x after V1.6 closure.
> Business code is not modified by this document.

Date: 2026-05-31

## 1. Scope and Baseline

V1.6 is closed. The repository documents V1.6 Closure Acceptance as accepted and states that V1.6 has no remaining development plan. Any new backend public surface after that point must be treated as V1.7 or later, not as additional V1.6 scope.

Evidence:

- `docs/V1.6/current-vs-target-gap.md:193-201` states V1.6 remaining development is zero and only V1.7 planning or post-V1.6 backlog triage may follow.
- `docs/V1.6/README.md:3-35` states V1.6 closure accepted and target HTTP route count was 35 at closure.
- `docs/V1.7/README.md:3-10` defines V1.7 as ResearchNotebook source preview backend contract enablement.
- `docs/V1.8/research-notebook-document-unit-contract.md:6-15` defines V1.8 as DocumentUnit target HTTP enablement.
- `docs/V1.6/public-surface-overlays/v1_9_research_notebook_evidence_spans.json:1-11` records a V1.9 EvidenceSpan target HTTP overlay.

## 2. V1.x Product Direction

V1.x after V1.6 should stay focused on ResearchNotebook and knowledge consumption contracts on top of the existing local knowledge governance service. It should not absorb V2 project intelligence work such as codebase assets, repo snapshot, public surface inventory, code symbols, DevWiki, code graph, or Agent Context Pack.

### In Scope

- Source-level preview.
- Document unit list and detail.
- Evidence span lookup and citation backjump support.
- Source-grounded query and research answer hardening.
- Folder and URL ingestion contracts for ResearchNotebook.
- Notebook guide and studio artifact contracts.
- AI provider health and sanitized generation metadata.
- Agent workflow draft contract for supported local workflows.
- V1.x closure audit and public surface freeze.

### Out of Scope

- New MCP tools unless a phase explicitly defines and audits them.
- New CLI commands unless a phase explicitly defines and audits them.
- New compatibility `/api/v1/knowledge/*` routes.
- Codebase asset registry, repo snapshot, symbol index, code graph, DevWiki, Agent Context Pack.
- Graph editing, assessment UI, or front-end product expansion beyond contract validation.

## 3. Cross-Phase Engineering Rules

Every V1.x phase after V1.6 must follow these rules:

1. Add or update a phase-specific development plan before implementation.
2. Add or update a phase-specific acceptance plan before implementation.
3. Add a phase-specific audit report after implementation.
4. Declare exact public surface additions through overlays or equivalent inventory.
5. Run real-data target HTTP tests, not mock-only tests.
6. Verify no internal filesystem paths, cache paths, artifact physical paths, stack traces, provider secrets, or local absolute paths appear in public responses.
7. Verify `/api/v1/knowledge/*` compatibility routes are not expanded unless explicitly approved.
8. Verify MCP tool count and CLI command surface are unchanged unless explicitly approved.
9. Update capability manifest fields when a capability becomes available.
10. Keep V2 project intelligence scope out of V1.x documents and acceptance claims.

## 4. Phase V1.7: Source Preview Contract Closure

Status: implemented, needs closure audit if treated as a formal V1 release milestone.

### Goal

Formalize the minimum source-level preview contract used by ResearchNotebook.

### Delivered Surface

- `GET /api/workspaces/{workspace_id}/capabilities`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview`

Evidence:

- `docs/V1.7/README.md:5-10`
- `docs/V1.7/research-notebook-source-preview-contract.md:8-18`

### Development Plan

- Keep the existing source preview implementation as a target HTTP route.
- Ensure source preview accepts only registry `source_id`, not slugs, artifact refs, local paths, or llmwiki page IDs.
- Ensure imported text sources can be previewed before build.
- Keep unsupported source types as `200 OK` with `preview_available=false`.
- Keep capability manifest fields aligned with the implemented route.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_target_http_source_preview.py`
- `python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_source_preview.py`

Acceptance gates:

- Capability manifest advertises source preview as available.
- Source preview succeeds for text source.
- Unsupported source type returns stable unavailable response.
- Unknown workspace returns 404.
- Unknown registry source returns 404.
- Artifact refs, slugs, and physical paths are rejected.
- No internal path leakage.
- No MCP, CLI, or compatibility route additions.

## 5. Phase V1.8: DocumentUnit Contract Closure

Status: implemented, needs closure audit if treated as a formal V1 release milestone.

### Goal

Formalize unit-level navigation for ResearchNotebook source reading.

### Delivered Surface

- `GET /api/workspaces/{workspace_id}/sources/{source_id}/units`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}`

Evidence:

- `docs/V1.8/research-notebook-document-unit-contract.md:8-15`
- `backend/tests/test_target_http_document_units.py:25-26`

### Development Plan

- Keep deterministic unit generation for text, markdown, JSON, and PDF extracted text where supported by existing tests.
- Keep unit ordering deterministic by `order_index`, then `unit_id`.
- Keep cursor opaque.
- Keep source preview separate from unit list and unit detail.
- Keep `unit_id` backend-generated and source-scoped.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py`
- `python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py`

Acceptance gates:

- Capability manifest advertises `document_units=true`.
- Unit list and detail succeed for supported text-like sources.
- Unsupported source type returns stable empty list.
- Pagination limit and cursor behavior are deterministic.
- Unknown source, unknown unit, cross-source unit, artifact ref, slug, and path inputs fail with stable semantics.
- EvidenceSpan and citation backjump remain disabled in V1.8.
- No MCP, CLI, or compatibility route additions.

## 6. Phase V1.9: EvidenceSpan and Citation Backjump Contract

Status: implementation and tests exist, formal V1.9 documentation is missing.

### Goal

Make query, research, session query, and folder summary references resolvable to source unit evidence spans.

### Planned Surface

- `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}`

Evidence:

- `docs/V1.6/public-surface-overlays/v1_9_research_notebook_evidence_spans.json:1-11`
- `backend/app/api/v1/data_service.py:3346-3360`
- `backend/tests/test_target_http_evidence_spans.py:55-68`

### Development Plan

1. Create `docs/V1.9/README.md`.
2. Create `docs/V1.9/research-notebook-evidence-span-contract.md`.
3. Move V1.9 overlay reference out of the V1.6 mental model by documenting that it is a post-V1.6 overlay.
4. Formalize EvidenceSpan schema:
   - `source_id`
   - `unit_id`
   - `evidence_id`
   - `snippet`
   - `start_offset`
   - `end_offset`
   - `offset_basis`
   - `offset_range`
   - `text_basis`
   - optional locator such as `page_no`
5. Formalize evidence refs returned by:
   - workspace query
   - session query
   - research report
   - notebook guide
   - studio artifacts
   - folder summary workflow
6. Define invalid input rejection:
   - unknown evidence id
   - evidence id from another source
   - evidence id from another unit
   - artifact ref in place of evidence id
   - slug or local path in place of evidence id
7. Confirm capability manifest:
   - `evidence_spans=true`
   - `precise_span_highlight=true`
   - `citation_backjump=true`

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_target_http_evidence_spans.py`
- `python3 -m pytest backend/tests/test_target_http_session_query.py`
- `python3 -m pytest backend/tests/test_target_http_research.py`
- `python3 -m pytest backend/tests/test_target_http_notebook_guide.py`
- `python3 -m pytest backend/tests/test_target_http_folder_summary_workflow.py`
- `python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_target_http_evidence_spans.py`

Acceptance gates:

- Capability manifest advertises evidence spans and citation backjump.
- Query evidence refs resolve through source detail, unit detail, and evidence detail.
- Session query evidence refs resolve with the same ID tuple.
- Research conclusions and conflicts use resolvable evidence refs.
- Folder summary artifacts use resolvable evidence refs.
- PDF-derived evidence preserves locator metadata where available.
- No public response includes internal path or artifact physical path.
- No new MCP tools, CLI commands, or compatibility routes.

## 7. Phase V1.10: Source-Grounded QA and Research Hardening

Status: partially implemented in tests, needs formal phase plan and closure.

### Goal

Make ResearchNotebook query and research answers safe by default: answer from evidence when coverage exists, refuse when evidence is absent or insufficient, and preserve evidence through AI-provider fallback paths.

Evidence:

- `backend/tests/test_target_http_evidence_spans.py:105-140` covers no-source and insufficient-evidence refusal behavior.
- `backend/tests/test_target_http_evidence_spans.py:141-202` covers AI provider use and schema fallback without losing evidence.
- `backend/tests/test_target_http_research.py:13-68` covers research no-source refusal and resolvable evidence refs.
- `backend/tests/test_target_http_research.py:70-147` covers structured conflict labeling.

### Development Plan

1. Create `docs/V1.10/README.md`.
2. Create `docs/V1.10/source-grounded-query-research-contract.md`.
3. Formalize workspace query coverage states:
   - `no_sources`
   - `insufficient_evidence`
   - `source_supported`
4. Formalize answer basis:
   - `source_grounded_refusal`
   - `source_supported`
5. Formalize AI provider fallback:
   - missing key
   - missing provider config
   - provider timeout
   - provider unavailable
   - response schema mismatch
6. Require `key_claims` to include evidence refs when AI-generated answers are used.
7. Require generated research reports to include:
   - supported conclusions
   - conflicts
   - missing evidence
   - evidence refs
   - generation metadata
8. Define conflict labeling boundaries:
   - only label explicit contradictory positions
   - do not infer conflicts from unrelated conclusions
9. Keep provider secrets out of all public payloads.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_target_http_evidence_spans.py backend/tests/test_target_http_research.py`
- `python3 -m pytest backend/tests/test_target_http_ai_provider.py backend/tests/test_target_http_notebook_guide.py backend/tests/test_target_http_studio_artifacts.py`

Acceptance gates:

- Query without sources refuses with suggested source actions.
- Query with unrelated sources refuses with `insufficient_evidence`.
- Query with relevant sources returns source-supported answer and resolvable evidence refs.
- AI schema mismatch falls back without losing evidence refs.
- Research without sources refuses.
- Research with relevant sources returns supported conclusions and resolvable evidence refs.
- Conflicting source positions produce structured conflicts.
- Non-conflicting sources do not produce false conflicts.
- Provider secrets are never serialized.
- No MCP, CLI, or compatibility route additions.

## 8. Phase V1.11: Folder, URL, and PDF Source Intake Hardening

Status: partially implemented in tests, needs formal phase plan and closure.

### Goal

Harden ResearchNotebook source intake beyond direct text import while preserving authorization, privacy, and evidence traceability.

Evidence:

- `backend/tests/test_target_http_folder_collections.py:42-151` covers folder collection scan, authorization, excluded directories, hidden files, unsupported extensions, symlink behavior, and no compatibility route.
- `backend/tests/test_target_http_folder_summary_workflow.py:8-142` covers dry-run folder summary workflow, confirm-extract behavior, and evidence-backed artifacts.
- `backend/tests/test_target_http_url_sources.py:50-118` covers URL source import, preview, units, evidence, unsafe URL rejection, and stable extraction errors.
- `backend/tests/test_target_http_source_preview.py:299-320` covers OCR-required boundary behavior for scanned PDF preview.

### Development Plan

1. Create `docs/V1.11/README.md`.
2. Create `docs/V1.11/source-intake-hardening-contract.md`.
3. Formalize folder collection scan route:
   - dry run first
   - authorized root required
   - permission grant required
   - symlink default skip
   - hidden file and hidden dir skip
   - unsupported extension skip
   - no extract unless explicitly confirmed by workflow phase
4. Formalize folder summary workflow:
   - dry-run planning
   - confirm extract
   - evidence-backed summary artifacts
5. Formalize URL import:
   - public HTTP/HTTPS only
   - localhost/private network blocked
   - stable extraction error codes
   - URL source preview, units, and evidence span compatibility
6. Formalize PDF boundary:
   - text PDF supported when extractor succeeds
   - scanned/OCR-required PDF returns stable unsupported or OCR-required state
   - OCR is not silently claimed unless implemented and accepted

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_target_http_folder_collections.py`
- `python3 -m pytest backend/tests/test_target_http_folder_summary_workflow.py`
- `python3 -m pytest backend/tests/test_target_http_url_sources.py`
- `python3 -m pytest backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py backend/tests/test_target_http_evidence_spans.py`

Acceptance gates:

- Folder scan uses repo-relative or root-relative paths only.
- Folder scan skips hidden files, hidden dirs, excluded dirs, symlinks, unsupported extensions, and oversized files.
- Unauthorized roots are rejected.
- Folder summary requires explicit confirmation before extraction.
- Folder summary artifacts include resolvable evidence refs.
- URL import blocks unsafe/private URLs.
- URL import stable failures do not leak internal details.
- URL sources work with preview, units, query evidence, and evidence span detail.
- Scanned PDF/OCR-required behavior is explicit and not falsely accepted.

## 9. Phase V1.12: Notebook Guide and Studio Artifact Contracts

Status: partially implemented in tests, needs formal phase plan and closure.

### Goal

Make higher-level ResearchNotebook artifacts evidence-aware without converting V1.x into V2 project intelligence.

Evidence:

- `backend/app/api/v1/research_notebook.py:36-58` exposes guide and studio artifact target HTTP routes.
- `backend/tests/test_target_http_notebook_guide.py:39-120` covers guide evidence refs and AI-provider behavior.
- `backend/tests/test_target_http_studio_artifacts.py:13-150` covers studio artifact generation behavior.

### Development Plan

1. Create `docs/V1.12/README.md`.
2. Create `docs/V1.12/notebook-guide-studio-contract.md`.
3. Formalize notebook guide route:
   - source-grounded guide
   - topic summaries
   - evidence refs
   - fallback behavior
4. Formalize studio artifacts:
   - supported artifact types
   - unavailable response when sources do not support artifact generation
   - evidence-backed generated artifacts
   - generation metadata
5. Require every generated conclusion to carry evidence refs or explicit unavailable/needs-source state.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_target_http_notebook_guide.py backend/tests/test_target_http_studio_artifacts.py`
- `python3 -m pytest backend/tests/test_target_http_ai_provider.py backend/tests/test_target_http_evidence_spans.py`

Acceptance gates:

- Notebook guide uses registry source IDs and evidence refs.
- Studio artifact output includes evidence refs when generated.
- Unsupported or no-source inputs return stable unavailable responses.
- AI provider fallback preserves evidence where possible.
- No provider secret leakage.
- No new MCP, CLI, or compatibility route additions.

## 10. Phase V1.13: AI Provider Health and Agent Workflow Contract

Status: partially implemented in tests, needs formal phase plan and closure.

### Goal

Stabilize AI provider health reporting and supported agent workflow draft contracts for external ResearchNotebook orchestration.

Evidence:

- `backend/app/api/v1/research_notebook.py:28-34` exposes AI provider health.
- `backend/app/api/v1/research_notebook.py:128-139` exposes agent workflow draft.
- `backend/tests/test_target_http_ai_provider.py:23-110` covers provider health and secret sanitization.
- `backend/tests/test_target_http_agent_workflows.py:14-57` covers workflow draft and route exposure.

### Development Plan

1. Create `docs/V1.13/README.md`.
2. Create `docs/V1.13/ai-provider-agent-workflow-contract.md`.
3. Formalize AI provider health response:
   - missing API key
   - missing provider config
   - available provider metadata
   - retryable provider errors
   - no secret serialization
4. Formalize supported agent workflow draft:
   - registered `folder_summary_v1` template only
   - task ID generation
   - required permissions
   - next actions
5. Reject unsupported user goals with stable validation error.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_target_http_ai_provider.py backend/tests/test_target_http_agent_workflows.py`
- `python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_v16_closure_acceptance.py`

Acceptance gates:

- Provider health works for missing key, missing config, and success path.
- No API key or provider secret appears in payload.
- Agent workflow draft succeeds only for registered supported template.
- Unsupported workflow goals are rejected.
- No new MCP, CLI, or compatibility route additions.

## 11. Phase V1.x Closure: ResearchNotebook Backend Contract Freeze

Status: planned.

### Goal

Freeze the V1.x ResearchNotebook backend contract and explicitly hand off project intelligence work to V2.

### Development Plan

1. Create `docs/V1.x/README.md`.
2. Create `docs/V1.x/v1_x_research_notebook_backend_contract_freeze.md`.
3. Create a machine-readable V1.x public surface manifest that includes:
   - V1.6 closure target routes
   - V1.7 source preview routes
   - V1.8 DocumentUnit routes
   - V1.9 EvidenceSpan route
   - V1.10 query/research hardening routes
   - V1.11 intake routes
   - V1.12 guide/studio routes
   - V1.13 provider/agent workflow routes
4. Produce an accepted-route count with explicit additions by phase.
5. Re-run all relevant target HTTP and public surface tests.
6. Document known non-goals and V2 handoff:
   - codebase asset
   - repo snapshot
   - project public surface inventory
   - code symbols
   - DevWiki
   - code graph
   - agent context pack

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_public_surface_guard.py`
- `python3 -m pytest backend/tests/test_v16_closure_acceptance.py`
- `python3 -m pytest backend/tests/test_target_http_source_preview.py`
- `python3 -m pytest backend/tests/test_target_http_document_units.py`
- `python3 -m pytest backend/tests/test_target_http_evidence_spans.py`
- `python3 -m pytest backend/tests/test_target_http_research.py`
- `python3 -m pytest backend/tests/test_target_http_notebook_guide.py`
- `python3 -m pytest backend/tests/test_target_http_studio_artifacts.py`
- `python3 -m pytest backend/tests/test_target_http_folder_collections.py`
- `python3 -m pytest backend/tests/test_target_http_folder_summary_workflow.py`
- `python3 -m pytest backend/tests/test_target_http_url_sources.py`
- `python3 -m pytest backend/tests/test_target_http_ai_provider.py`
- `python3 -m pytest backend/tests/test_target_http_agent_workflows.py`
- `python3 -m pytest backend/tests`

Acceptance gates:

- All phase docs exist.
- All route additions are represented in a manifest or overlay.
- Public route count is reconciled.
- No unapproved MCP or CLI expansion.
- Compatibility routes are retained but not expanded.
- No internal path leakage in target HTTP tests.
- No provider secret leakage.
- Evidence refs resolve end to end.
- V1.x closure document explicitly states that V2 governs project intelligence.

## 12. Execution Order

Recommended order:

1. V1.9 EvidenceSpan formalization and closure.
2. V1.10 Source-grounded QA and Research hardening.
3. V1.11 Folder, URL, and PDF source intake hardening.
4. V1.12 Notebook Guide and Studio artifact contracts.
5. V1.13 AI Provider Health and Agent Workflow contract.
6. V1.x ResearchNotebook backend contract freeze.

## 13. Stop Conditions

Stop and request human review if any of these occur:

- A phase requires adding MCP tools or CLI commands unexpectedly.
- A phase requires adding compatibility `/api/v1/knowledge/*` routes.
- Evidence refs cannot be resolved to source, unit, and evidence span.
- Generated answers cannot distinguish no-source, insufficient-evidence, and source-supported states.
- Public responses include local absolute paths, internal storage layout, provider secrets, or stack traces.
- V1.x scope starts overlapping with V2 project intelligence.
- Tests pass only with mocked payloads and no real workspace/source E2E.
