# V2.6 Phase 44-48 Detailed Development and Acceptance Plan

> Scope: document-level execution plan for V2.6 remaining work.
> Business code must not be changed by this document.
> V2.6 is architecture abstraction hardening, not full static analysis.

Date: 2026-06-03

## 1. Execution Rule

Phase 44-48 may start only after this document, `V2_6_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md`, `V2_6_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`, and `V2_6_PHASE_44_PRE_IMPLEMENTATION_AUDIT_REPORT.md` have no open fatal or major document findings.

All implementation phases must:

- use real `data_service` repository data;
- use real HarnessOS repository data at `/Users/Zhuanz/Desktop/workspace/harnessOS`;
- write V2.6 artifacts only under `workspace/assets/codebase/{codebase_id}/architecture/`;
- preserve V2.0-V2.5 artifact hashes unless an explicit rebuild is part of the phase plan;
- expose HTTP, MCP, and CLI read paths for accepted public V2.6 artifacts;
- reject false-green results that rely on mocks, path leaks, or unsupported static-analysis claims.

## 2. Phase 44: Architecture Scale Profile

### Development

- Add a focused scale profiler in `backend/data_service/code_assets/architecture/`.
- Build `architecture_scale_profile.json` from existing V2.0/V2.1/V2.4 artifacts.
- Compute file count, LOC, language distribution, artifact sizes, warning counts, confidence distribution, needs_review counts, skipped paths, and `summary_mode_required`.
- Add thin HTTP/MCP/CLI build and read access using the existing architecture interface modules.
- Add prior-artifact hash capture before build and comparison after build.

Implementation modules:

```text
backend/data_service/code_assets/architecture/scale_profile.py
backend/data_service/code_assets/architecture/service.py
backend/app/api/v1/code_assets_architecture.py
backend/data_service/mcp_code_architecture_tools.py
backend/data_service/cli_code_architecture.py
```

Public interface changes:

- add scale build/read HTTP routes;
- add `knowledge_code_architecture_scale_build`;
- add `knowledge_code_architecture_scale_profile`;
- add CLI `scale-build` and `scale-profile`.

Planned focused test:

```text
backend/tests/test_v2_6_architecture_scale_profile.py
```

### Acceptance

- `data_service` E2E generates a non-empty profile.
- HarnessOS E2E generates a non-empty profile.
- Public output uses repo-relative paths only.
- `summary_mode_required` is deterministic from thresholds documented in the artifact schema contract.
- Prior V2.0-V2.5 artifact hashes are unchanged unless the run explicitly rebuilt those artifacts.
- Empty or missing prerequisite artifacts produce structured errors, not fake profiles.
- HTTP/MCP/CLI reads agree on `snapshot_id`, counts, artifact refs, warnings, and needs_review count.

### Required Evidence

- Profile artifact path and JSON sample for both repositories.
- HTTP/MCP/CLI read output samples.
- Hash-gate before/after report.
- Test names and pass results.

## 3. Phase 45: Lightweight Multi-language, Config, Deployment, and Schema Inventory

### Development

- Add lightweight TS/JS/Vue extractor for file, import, export, frontend entrypoint, and API-client hints.
- Persist those facts in `language_facts.jsonl` instead of mixing them into config inventory.
- Add config inventory for package manifests, pyproject, Dockerfile, compose, k8s, CI workflow, env examples, OpenAPI-like files, and database/schema hints.
- Add deployment inventory for deterministic runtime/service/port/dependency hints.
- Add schema inventory for schema-like files without claiming full validation semantics.
- Redact secret-like config values and expose only value summaries.

Implementation modules:

```text
backend/data_service/code_assets/architecture/config_inventory.py
backend/data_service/code_assets/architecture/deployment_inventory.py
backend/data_service/code_assets/architecture/service.py
backend/app/api/v1/code_assets_architecture.py
backend/data_service/mcp_code_architecture_tools.py
backend/data_service/cli_code_architecture.py
```

Public interface changes:

- add inventory build HTTP route;
- add config/deployment/schema HTTP reads;
- add MCP inventory build and read tools;
- add CLI `inventory-build`, `config`, `deployment`, and `schema`.

Planned focused test:

```text
backend/tests/test_v2_6_config_deployment_inventory.py
```

### Acceptance

- `data_service` and HarnessOS both produce non-empty config/deployment inventory.
- At least package manifests and Python config are detected in `data_service` when present.
- HarnessOS detects frontend/package/deployment hints where present.
- Public payload contains no raw secret, token, API key, authorization value, local absolute path, or raw `.env` value.
- Non-Python facts include evidence, confidence, and `needs_review` when unsupported.
- No output claims full semantic analysis, full dependency injection resolution, or runtime topology.
- Unsupported file types are skipped with warnings or `needs_review`, not silent success.

### Required Evidence

- `language_facts.jsonl`, `config_inventory.jsonl`, `deployment_inventory.jsonl`, and `schema_inventory.jsonl` samples.
- Redaction test output.
- Real-repo E2E artifact counts.
- Unsupported-claim audit output.

## 4. Phase 46: Architecture Taxonomy and Review Queue

### Development

- Add persisted `architecture_taxonomy.json` with default role, layer, boundary, pattern, and confidence thresholds.
- Support optional taxonomy override artifact; no UI-only override is accepted.
- Build `architecture_review_queue.jsonl` from low-confidence, missing-evidence, unsupported, conflicting, or ambiguous architecture facts.
- Add thin HTTP/MCP/CLI reads for taxonomy and review queue.

Implementation modules:

```text
backend/data_service/code_assets/architecture/taxonomy.py
backend/data_service/code_assets/architecture/review_queue.py
backend/data_service/code_assets/architecture/service.py
backend/app/api/v1/code_assets_architecture.py
backend/data_service/mcp_code_architecture_tools.py
backend/data_service/cli_code_architecture.py
```

Public interface changes:

- add taxonomy build/read HTTP routes;
- add review queue HTTP build/read;
- add MCP taxonomy/review queue tools;
- add CLI `taxonomy-build`, `taxonomy`, `review-queue-build`, and `review-queue`.

Planned focused test:

```text
backend/tests/test_v2_6_architecture_taxonomy_review_queue.py
```

### Acceptance

- Default taxonomy covers interface, application, domain, infrastructure, governance, runtime, artifact, test, and docs.
- Low-confidence items are excluded from accepted architecture summaries.
- Review queue items include target type, target id, reason, severity, confidence, signals, evidence, and recommended action.
- Override artifact keeps default fallback behavior and never deletes unknown default categories.
- HTTP/MCP/CLI return consistent review counts and stable item ids.
- Review queue generation is deterministic for the same artifact inputs.

### Required Evidence

- Taxonomy artifact.
- Review queue artifact.
- Sample accepted and needs_review split.
- HTTP/MCP/CLI consistency sample.

## 5. Phase 47: Large-project Views and Agent Context Pack Integration

### Development

- Generate `views/architecture_large_project_overview.html` from persisted V2.6 artifacts.
- Generate `views/architecture_key_boundaries.mmd` from persisted node and boundary facts.
- Add architecture summary to Agent Context Pack using scale profile, key roles, key boundaries, patterns, and review risks.
- Enforce token-budget behavior: architecture advice must keep its evidence or be omitted/marked `needs_review`.

Implementation modules:

```text
backend/data_service/code_assets/architecture/large_project_views.py
backend/data_service/code_assets/context/selector.py
backend/data_service/code_assets/context/renderer_markdown.py
backend/data_service/code_assets/context/renderer_json.py
backend/app/api/v1/code_assets_architecture.py
backend/data_service/mcp_code_architecture_tools.py
backend/data_service/cli_code_architecture.py
```

Public interface changes:

- add large-project view build route/tool/CLI command;
- extend architecture view read to support `architecture_large_project_overview.html` and `architecture_key_boundaries.mmd`;
- extend Agent Context Pack output with `architecture_summary`.

Planned focused test:

```text
backend/tests/test_v2_6_large_project_views.py
```

### Acceptance

- HTML and Mermaid views are non-empty for both repositories.
- Every Mermaid node id exists in persisted artifacts.
- Views do not introduce facts absent from persisted artifacts.
- Context Pack contains architecture summary for a large-repo task.
- Small token budget does not retain evidence-free architecture guidance.
- Low-confidence architecture facts are shown only as `needs_review`.
- HTML, Mermaid, JSON, and Markdown outputs must all reference the same artifact ids for displayed facts.

### Required Evidence

- HTML and Mermaid artifact paths.
- Mermaid node integrity check.
- Context Pack JSON/Markdown samples.
- Token-budget trimming test output.

## 6. Phase 48: V2.6 Closure Audit

### Development

- Run final V2.6 real-repo E2E on `data_service`.
- Run final V2.6 real-repo E2E on HarnessOS.
- Inspect persisted artifacts and public outputs.
- Complete `V2_6_FULL_PRD_COVERAGE_MATRIX.md`.
- Produce `V2_6_CLOSURE_AUDIT_REPORT.md`.

Implementation modules:

```text
backend/tests/test_v2_6_closure_acceptance.py
docs/V2.x/V2_6_FULL_PRD_COVERAGE_MATRIX.md
docs/V2.x/V2_6_CLOSURE_AUDIT_REPORT.md
```

No new product behavior should be added in Phase 48. If Phase 48 discovers missing product behavior, return to the relevant implementation phase.

Planned focused test:

```text
backend/tests/test_v2_6_closure_acceptance.py
```

### Acceptance

- All V2.6 focused tests pass.
- Both real-repo E2E flows pass.
- Every accepted PRD row has evidence.
- All unsupported static-analysis claims are marked non-claim or out of scope.
- No open fatal or major audit finding remains.
- Closure report explicitly lists accepted, needs_review, not implemented, out of scope, and non-claim categories.
- `V2_6_FULL_PRD_COVERAGE_MATRIX.md` has no in-scope `not_implemented` rows unless explicitly accepted as deferred by human review.

### Required Evidence

- Test commands and pass summaries.
- Artifact inspection summary.
- Public redaction report.
- PRD coverage matrix.
- Closure audit report.

## 7. Stop Conditions

Stop for human review if:

- HarnessOS cannot be accessed or must be replaced by mock data;
- implementation requires changing V2.0-V2.5 accepted artifact schemas;
- public output leaks secrets or absolute local paths;
- a large-project view requires facts not present in persisted artifacts;
- Agent Context Pack cannot preserve evidence under token limits;
- a phase would need to claim full call graph, data flow, control flow, runtime dispatch, or type inference.

## 8. Failure Handling and Replan Rules

If a phase fails acceptance:

- record failure in the phase audit report;
- classify failure as implementation bug, spec gap, environment blocker, or false-green risk;
- return to the phase development plan before retrying;
- do not continue to the next phase until no fatal or major finding remains.

If a failure reveals a PRD/spec mismatch:

- update the relevant V2.6 document first;
- run document audit again;
- only then resume implementation planning.

If HarnessOS validation fails because HarnessOS is unavailable:

- stop for human review;
- do not substitute another repo without updating `V2_6_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`.
