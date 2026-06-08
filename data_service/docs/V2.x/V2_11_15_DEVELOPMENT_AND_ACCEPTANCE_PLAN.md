# V2.11-V2.15 Development and Acceptance Plan

## 1. Shared Development Loop

Each stage must follow this loop:

1. Stage-specific development plan.
2. Stage-specific acceptance plan.
3. Pre-implementation audit.
4. Implementation.
5. Focused tests.
6. Real data_service E2E.
7. Large project E2E when applicable.
8. Artifact inspection.
9. HTTP/MCP/CLI parity.
10. PRD/spec review.
11. False-green audit.
12. Closure audit.

No stage may start implementation with open fatal or major pre-implementation findings.

## 2. V2.11 Coding Agent Actionability

### Development

- Add actionability index artifacts.
- Add AST/LSP/tree-sitter provider abstraction.
- Add definition/reference graph v1.
- Add impact analysis API.
- Add test mapping heuristics.
- Add task-to-edit planning artifact.

### Acceptance

- data_service E2E returns impacted files, symbols, surfaces, tests, and evidence for at least three real tasks.
- HarnessOS or another large project returns either actionable evidence or structured blockers.
- No reference/import edge is labeled as runtime call.
- Every action recommendation has evidence or `needs_review`.

## 3. V2.12 Safe Patch Planning

### Development

- Add patch plan schema.
- Add candidate edit selector.
- Add patch option builder with ranked alternatives.
- Add validation command planner.
- Add rollback plan generator.
- Add readiness scoring.
- Add patch plan persistence under `coding_agent/patch_plans/`.
- Add HTTP/MCP/CLI create and read contracts.
- Add no-source-mutation guard and public payload redaction checks.

### Acceptance

- Patch plan is persisted and readable by HTTP/MCP/CLI.
- No source file is modified by V2.12.
- Every proposed edit has file, symbol or evidence link.
- Rollback plan covers all proposed files.
- Low confidence recommendations are `needs_review`.
- Validation commands are planned but not executed.
- Readiness status is `ready_for_review`, `needs_review`, or `blocked`; low-confidence or incomplete rollback plans cannot be reported as ready.
- Real `data_service` E2E covers at least three tasks that use V2.11 actionability artifacts.
- HarnessOS or another large project returns either a patch plan or structured blockers without project-specific hardcoding.

## 4. V2.13 Controlled Runtime Evidence

### Development

- Add command allowlist registry.
- Add runtime execution descriptor.
- Add test run artifact.
- Add log redaction.
- Add runtime-static evidence alignment.

### Acceptance

- Default state denies command execution.
- Allowlisted test command can run in data_service.
- Non-allowlisted command is blocked with structured error.
- Logs are redacted.
- Runtime evidence is separate from static evidence.

## 5. V2.14 Incremental Intelligence

### Development

- Add file fingerprint index.
- Add snapshot diff artifact.
- Add changed symbol/surface/doc detection.
- Add artifact version diff.
- Add task memory and drift timeline.

### Acceptance

- Modifying one fixture file changes the incremental report.
- generated_at does not affect identity.
- Changed files/symbols are reported with evidence.
- Previous artifacts are not silently mutated.
- Real repo incremental run is faster or more targeted than full rebuild.

## 6. V2.15 Interactive Review Workbench

### Development

- Add backend report payload.
- Add review workbench HTML.
- Add capability graph Mermaid view.
- Add evidence click-through IDs.
- Add blocker board and risk lanes.
- Add context export payload.

### Acceptance

- Workbench renders from persisted backend artifacts only.
- No unpersisted facts appear in HTML/Mermaid.
- needs_review and blockers are visible.
- No absolute paths or secrets appear in public output.
- data_service and HarnessOS reports are human-readable.

## 7. Global False-Green Rejections

Reject closure if:

- mock-only test is used as real E2E;
- import edge is treated as runtime call;
- weak match is accepted as implementation fact;
- patch plan edits code in V2.12;
- non-allowlisted command executes in V2.13;
- incremental run rewrites historical artifacts silently;
- frontend hides blockers;
- accepted recommendation lacks evidence or `needs_review`.

## 8. Final Roadmap Closure

V2.11-V2.15 closes only when all stage coverage matrices have:

- no pending in-scope rows;
- all accepted rows backed by test and artifact evidence;
- all out-of-scope rows explicitly classified;
- no open fatal or major findings.
