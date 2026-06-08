# V2.14 Target Architecture: Incremental Intelligence

## 1. Architecture Position

V2.14 consumes snapshots and existing V2 artifacts to build changed-fact reports.

```text
Snapshot A + Snapshot B
  -> Fingerprint Index
  -> Snapshot Diff Builder
  -> Changed Fact Detector
  -> Artifact Diff Reporter
  -> Task Memory Store
  -> Drift Timeline
  -> HTTP / MCP / CLI
```

## 2. Components

### 2.1 Fingerprint Index

Stores deterministic file fingerprints for included files. Identity must not use generated timestamps.

### 2.2 Snapshot Diff Builder

Compares two snapshots and produces added, modified, deleted, and unchanged file sets.

### 2.3 Changed Fact Detector

Consumes existing artifacts when available:

- symbols;
- public surfaces;
- document claims;
- code relationships;
- patch plans;
- runtime evidence.

It emits changed facts with evidence or `needs_review`.

### 2.4 Artifact Diff Reporter

Compares selected artifact summaries across snapshots. It must never rewrite historical artifacts.

### 2.5 Task Memory Store

Stores redacted task history rows. It links tasks to patch plans, runtime evidence, and changed facts.

### 2.6 Drift Timeline

Stores chronological drift events for changed facts and artifacts.

## 3. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/coding_agent/incremental/
  fingerprint_index/{snapshot_id}.json
  snapshot_diffs/{from_snapshot_id}_{to_snapshot_id}.json
  artifact_diffs/{diff_id}.json
  task_memory.jsonl
  drift_timeline.jsonl
```

## 4. Public Error Codes

```text
INCREMENTAL_BASE_SNAPSHOT_NOT_FOUND
INCREMENTAL_TARGET_SNAPSHOT_NOT_FOUND
INCREMENTAL_DIFF_NOT_FOUND
INCREMENTAL_FACT_SOURCE_MISSING
INCREMENTAL_ARTIFACT_IMMUTABILITY_VIOLATION
INCREMENTAL_SCHEMA_INVALID
```

## 5. Safety Boundaries

- Prior artifacts are immutable unless their owning phase explicitly rebuilds them.
- `generated_at` and read timestamps do not affect identity.
- Changed fact output must not claim semantic changes without evidence.
- Task memory must not store secrets or absolute paths.

## 6. Target User Experience

After V2.14, a user can ask "what changed since the last accepted snapshot?" and receive a targeted, evidence-backed report instead of re-reading the whole project.
