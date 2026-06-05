# V2.6 Real Repository E2E Acceptance Matrix

> Scope: real-data acceptance matrix for V2.6.
> Business code must not be changed by this document.

Date: 2026-06-03

## 1. Required Repositories

| Repository | Path | Purpose | Mock Allowed |
| --- | --- | --- | --- |
| data_service | `/Users/Zhuanz/Desktop/workspace/data_service` | Self-hosting Project Intelligence validation | No |
| HarnessOS | `/Users/Zhuanz/Desktop/workspace/harnessOS` | Large external project validation | No |

If HarnessOS is unavailable, V2.6 implementation must stop for human review. It must not replace HarnessOS with generated fixtures or mock data.

Recommended acceptance ids:

| Repository | workspace_id | codebase_id |
| --- | --- | --- |
| data_service | `data_service_v26` | `codebase_data_service_v26` |
| HarnessOS | `harnessos_v26` | `codebase_harnessos_v26` |

Implementation may choose equivalent ids only if the phase audit records the actual ids and all artifacts remain traceable.

## 2. Required E2E Flow

Each repository must run the same V2.6 E2E flow:

1. Register or reuse codebase asset.
2. Build or reuse V2.0 snapshot/inventory/symbol/trace prerequisites.
3. Build or reuse V2.4 code-derived architecture artifacts.
4. Capture prior artifact hashes.
5. Build architecture scale profile.
6. Build config/deployment/schema inventory.
7. Build taxonomy and review queue.
8. Build large-project HTML/Mermaid views.
9. Generate Agent Context Pack architecture summary.
10. Read all V2.6 public artifacts through HTTP, MCP, and CLI where applicable.
11. Recheck prior artifact hashes.
12. Run redaction and false-claim checks.

## 3. Minimum Command Shape

The exact command may vary with local test harnesses, but Phase 48 evidence must include equivalent operations for each repository:

```text
knowledge code import --workspace-id <workspace_id> --path <repo_path> --codebase-id <codebase_id>
knowledge code snapshot --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code inventory --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code symbols --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code architecture code-build --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code architecture scale-build --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code architecture inventory-build --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code architecture taxonomy-build --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code architecture large-view-build --workspace-id <workspace_id> --codebase-id <codebase_id>
knowledge code context-pack --workspace-id <workspace_id> --codebase-id <codebase_id> --mode task_context
```

HTTP and MCP checks must read at least:

- scale profile;
- config inventory;
- deployment inventory;
- review queue;
- large-project view.

## 4. Acceptance Matrix

| Capability | data_service Required Result | HarnessOS Required Result | Evidence |
| --- | --- | --- | --- |
| Scale profile | Non-empty `architecture_scale_profile.json` | Non-empty `architecture_scale_profile.json` | artifact path + read output |
| Config inventory | Non-empty or explicit no-config warning | Non-empty | JSONL sample + counts |
| Deployment inventory | Non-empty or explicit no-deployment warning | Non-empty or explicit no-deployment warning | JSONL sample + counts |
| Schema inventory | Non-empty or explicit no-schema warning | Non-empty or explicit no-schema warning | JSONL sample + counts |
| Taxonomy | Default taxonomy persisted | Default taxonomy persisted | JSON artifact |
| Review queue | Queue persisted, count exposed | Queue persisted, count exposed | JSONL sample |
| HTML view | Non-empty and artifact-backed | Non-empty and artifact-backed | file path + integrity check |
| Mermaid view | Node ids exist in artifacts | Node ids exist in artifacts | node integrity check |
| Context summary | Includes V2.6 architecture section | Includes V2.6 architecture section | context pack artifact |
| Public redaction | Pass | Pass | redaction report |
| Hash gate | Pass | Pass | before/after hash report |

## 5. Public Interface Checks

For every public V2.6 artifact:

- HTTP read must return V2 envelope with stable ids and artifact refs.
- MCP read must return the same stable ids and counts.
- CLI read must output valid JSON with the same stable ids and counts.
- Error responses must use stable V2.6 error codes.

## 6. Failure Classification

| Status | Meaning | Can Proceed |
| --- | --- | --- |
| `accepted` | Requirement passed with real evidence | Yes |
| `needs_review` | Evidence exists but confidence or product interpretation needs review | Only with explicit audit note |
| `blocked` | Environment or missing prerequisite prevents validation | No |
| `not_implemented` | Capability has not been implemented | No for in-scope V2.6 rows |
| `false_green_rejected` | Result attempted to pass without valid evidence | No |
| `out_of_scope` | Explicit non-goal or deferred item | Yes if PRD agrees |

## 7. False-Green Rejection

Reject acceptance if:

- either repository is replaced with mock data;
- a phase only checks file existence but not artifact content;
- a public response leaks absolute path or secret-like value;
- a view contains claims absent from persisted artifacts;
- low-confidence facts are counted as accepted architecture facts;
- skipped HarnessOS validation is counted as pass;
- prior V2 artifacts are silently rewritten;
- output claims full call graph, data flow, control flow, runtime dispatch, type inference, or complete design intent recovery.

## 8. Artifact Inspection Checklist

For every produced artifact:

- file exists;
- file parses as JSON, JSONL, HTML, or Mermaid as applicable;
- required ids match workspace/codebase/snapshot;
- evidence paths are repo-relative;
- public sample matches persisted artifact counts;
- redaction marker is present when content was redacted;
- artifact ref in public response points to the persisted file.

## 9. Closure Evidence Format

Each E2E run must produce a short evidence record:

```json
{
  "repository": "data_service",
  "codebase_id": "string",
  "snapshot_id": "string",
  "artifacts": {},
  "public_interface_counts": {},
  "hash_gate": "pass",
  "redaction": "pass",
  "false_claim_guard": "pass",
  "tests": [],
  "status": "accepted"
}
```
