# V2.14 PRD: Incremental Intelligence

## 1. Product Goal

V2.14 moves the project intelligence system from one-shot rebuilds to incremental project knowledge maintenance. It helps Coding Agents understand what changed between snapshots, which facts may be stale, and what previous tasks or drift events should influence the next development plan.

V2.14 does not promise perfect semantic incremental builds. It produces deterministic changed-file and changed-fact artifacts with evidence or `needs_review`.

## 2. Users and User Experience

Primary users:

- Coding Agent preparing a follow-up task.
- Maintainer reviewing drift between snapshots.
- Architecture Reviewer checking whether docs/code changed since last accepted report.
- Test Agent deciding which validation commands are relevant after a small change.

End-of-phase target experience:

1. User creates a new snapshot.
2. User asks for an incremental diff against a prior snapshot.
3. The service returns changed files, changed symbols, changed surfaces, changed document claims, artifact diffs, and drift timeline entries.
4. User can see whether the result is precise, needs review, or blocked.
5. Prior artifacts remain immutable unless explicitly rebuilt by their owning phase.

## 3. In Scope

- File fingerprint index.
- Snapshot diff artifact.
- Changed file detection.
- Changed symbol/surface/doc claim detection when supporting artifacts exist.
- Artifact diff report.
- Task memory.
- Drift timeline.
- HTTP/MCP/CLI contracts.
- Real `data_service` fixture mutation E2E.

## 4. Out of Scope

- Perfect semantic incremental build.
- Full Git history mining.
- Cross-repository memory federation.
- Runtime performance guarantees beyond targeted reporting.
- Silent mutation of prior artifacts.

## 5. Functional Requirements

### FR-001 Snapshot Diff

Compute a deterministic diff between two snapshots:

- `from_snapshot_id`
- `to_snapshot_id`
- added/modified/deleted files
- changed file hashes
- identity inputs
- warnings and unresolved items

### FR-002 Changed Facts

When source artifacts exist, report:

- changed symbols;
- changed public surfaces;
- changed document claims;
- changed architecture findings;
- changed test mappings.

If a fact cannot be compared, emit `needs_review` or structured blocker.

### FR-003 Task Memory

Persist task memory rows:

- task id;
- task text;
- related snapshot ids;
- patch plan refs;
- runtime evidence refs;
- outcome status;
- redacted summary.

### FR-004 Drift Timeline

Persist timeline rows for important changes:

- snapshot transition;
- changed artifact type;
- drift category;
- evidence refs;
- severity;
- needs_review.

## 6. Completion Definition

V2.14 is complete when:

- one fixture file change produces a changed file entry;
- one function-level change produces changed symbol evidence or `needs_review`;
- timestamp-only changes do not affect diff identity;
- previous artifacts are not silently rewritten;
- task memory and drift timeline artifacts are persisted;
- HTTP/MCP/CLI parity passes;
- real `data_service` E2E passes;
- no open fatal or major finding remains.
