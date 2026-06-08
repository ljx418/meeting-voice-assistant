# V2.14 Implementation Package: Incremental Intelligence

## 1. Goal

Maintain project intelligence across snapshots without requiring every consumer to reason from a full rebuild.

## 2. Development Plan

Implement:

- file fingerprint index;
- snapshot diff builder;
- changed file/symbol/surface/doc claim detection;
- artifact diff report;
- task memory;
- drift timeline.

## 3. Artifact Outputs

```text
coding_agent/incremental/snapshot_diffs/{from}_{to}.json
coding_agent/incremental/task_memory.jsonl
coding_agent/incremental/drift_timeline.jsonl
```

## 4. Public Interface Targets

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/diff
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/diffs/{diff_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/timeline
```

MCP:

```text
knowledge_code_incremental_diff
knowledge_code_incremental_diff_read
knowledge_code_drift_timeline
```

CLI:

```text
knowledge code incremental diff
knowledge code incremental read
knowledge code incremental timeline
```

## 5. Acceptance Plan

- Changing one fixture file produces a changed file entry.
- Changing one fixture function produces a changed symbol entry when parser support exists.
- `generated_at` does not affect diff identity.
- Previous artifacts are not silently overwritten.
- Real repo incremental report is more targeted than full rebuild output.

## 6. Stop Conditions

Stop if:

- old artifacts are mutated without explicit rebuild;
- generated timestamps influence identity;
- diff output claims semantic change without evidence;
- task memory stores secrets or absolute local paths.
