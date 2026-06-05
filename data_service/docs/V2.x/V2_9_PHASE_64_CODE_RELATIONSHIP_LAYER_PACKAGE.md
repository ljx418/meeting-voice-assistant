# V2.9 Phase 64 Package: Code Relationship Layer v2

> Phase-specific development, acceptance, and pre-implementation audit package.

Date: 2026-06-05

## 1. Goal

Phase 64 builds shallow, evidence-backed implementation paths from capability to surface, handler/module, and tests or references. It intentionally does not build a full call graph.

## 2. Required Inputs

- Phase 63 `architecture_public_surface_evidence_v2.jsonl`.
- V2.0 symbols/imports/evidence.
- V2.7 document-code architecture governance artifacts.
- V2.8 code fact chains, graph views, ranking, and intent artifacts.
- Real `data_service` and HarnessOS repositories.

## 3. Output Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_9/
  architecture_code_relationships_v2.jsonl
  architecture_module_clusters_v2.json
```

## 4. Allowed Relationship Types

| Relationship | Status eligibility | Rule |
| --- | --- | --- |
| `capability_implemented_by` | deterministic / heuristic | Capability maps to surface or module with evidence. |
| `surface_handled_by` | deterministic | Surface evidence resolves handler/symbol/file. |
| `handler_uses_module` | heuristic | Handler imports or references local module; not runtime call. |
| `module_referenced_by_test` | deterministic / heuristic | Test file references module/symbol/path. |
| `workflow_uses_step` | deterministic / heuristic | Workflow manifest or code references step implementation. |
| `module_imports_module` | deterministic | Static import edge only. |

Forbidden relationship claims:

```text
runtime_calls
data_flow
control_flow
type_inferred_dependency
production_runtime_topology
```

## 5. Relationship Status Policy

```text
deterministic:
  explicit ids or line-level code evidence exist on both sides
  relation is directly encoded by route/tool/CLI/manifest/import/test reference

heuristic:
  relation is plausible from naming, package proximity, or weak references
  relation must not be used as accepted implementation proof

needs_review:
  relation is ambiguous, incomplete, or inferred from docs only
```

## 6. Semantic Claim Policy

Every relationship row must include `semantic_claim`.

Allowed values:

```text
dependency_evidence
implementation_hint
deterministic_surface_binding
runtime_claim_forbidden
```

Rules:

- `surface_handled_by` may be `deterministic_surface_binding` when both surface and handler have line-level evidence.
- `module_imports_module` is always `dependency_evidence`.
- `handler_uses_module` is `implementation_hint` or `dependency_evidence`; it must not be rendered as a runtime call.
- Any attempted runtime/call/data/control claim must be rejected or marked `runtime_claim_forbidden`.

## 7. Module Cluster Policy

Clusters may group by:

- package;
- capability;
- layer;
- workflow;
- test area.

Every cluster must expose:

- member refs;
- relationship refs;
- evidence refs;
- confidence;
- `needs_review` if any core member is heuristic-only.

## 8. Required Development Work

- Build relationship paths:
  - capability -> public surface -> handler -> module -> test/reference.
- Preserve unresolved gaps instead of dropping them.
- Generate cluster summary metrics:
  - relationship count by type/status;
  - cluster count by type;
  - unresolved path count;
  - HarnessOS blocker count.
- Preserve and expose `semantic_claim` for Phase 66 reports and Phase 67 context packs.
- Expose read/build via HTTP/MCP/CLI parity.

## 9. Acceptance Tests

- `data_service` paths cover source import, query, build, quality, and code architecture capabilities where evidence exists.
- HarnessOS paths cover workflow, console, CLI, TUI, or exact blockers.
- No relationship output contains forbidden runtime/data/control-flow relationship types.
- At least 10 relationship paths can be traced to Phase 63 or earlier evidence refs.
- Import edges are labeled dependency evidence, not runtime calls.
- Module cluster members resolve to persisted refs.
- Report/context consumers can display `semantic_claim` without converting dependency evidence into runtime behavior.

## 10. False-Green Rejection

Reject Phase 64 if:

- import dependency is labeled runtime call;
- `handler_uses_module` is rendered as `calls`, `runtime path`, or `execution flow`;
- relationship path contains unpersisted nodes;
- heuristic relation is used as accepted evidence;
- copied design diagram creates code-derived relation;
- unresolved path is silently omitted;
- `semantic_claim` is missing or invalid;
- HarnessOS relationship status is claimed accepted without evidence or blocker.

## 11. Phase 64 Audit Opinion

Planning status: ready after Phase 63 acceptance.

Open fatal findings: none.

Open major findings: none.

Required closure output:

```text
docs/V2.x/V2_9_PHASE_64_ACCEPTANCE_AUDIT_REPORT.md
```
