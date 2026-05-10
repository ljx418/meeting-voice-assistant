# data_service MCP Lifecycle Tools - Codex Handoff

> Status: superseded handoff. The active data_service project has migrated to
> `/Users/Zhuanz/Desktop/workspace/data_service/backend`; the external agent
> guide now lives at
> `/Users/Zhuanz/Desktop/workspace/data_service/docs/MCP-EXTERNAL-AGENT-GUIDE.md`.
> HarnessOS V3.0-PhaseE has already passed real stdio MCP E2E against the
> migrated service. Keep this document as historical contract background only.

## Purpose

This document is the implementation handoff for another Codex terminal working in:

```text
/Users/Zhuanz/Desktop/workspace/data_service/backend
```

The goal is to extend the existing `data_service.mcp_stdio` server so an external Harness project can manage a knowledge workspace through MCP without understanding internal data_service folders.

The harnessOS side will use **Contract + Connector Stub** in Phase 5-A:

- harnessOS will declare a `data_service_mcp` connector ref and tool contract.
- harnessOS will not implement a real MCP client yet.
- Real MCP client execution is deferred to harnessOS Phase 5-C.

This handoff defines what the data_service MCP server must expose.

## Current Context

Existing data_service MCP tools already include:

- `knowledge_ingest`
- `knowledge_query`
- `knowledge_quality_summary`
- `knowledge_correction_plan`
- `knowledge_quality_feedback`
- `knowledge_correction_rules`
- `knowledge_review_correction_rule`

Keep all existing tools compatible. Add lifecycle tools as a new layer.

Relevant files in the target project:

- `data_service/mcp_stdio.py`
- `data_service/service.py`
- `data_service/security.py`
- `data_service/models.py`
- `tests/test_data_service_mcp.py`
- `docs/MCP-EXTERNAL-AGENT-GUIDE.md`

## Required Tool Contract

All new MCP tools must return a JSON object with this envelope:

```json
{
  "workspace_id": "string",
  "operation_id": "string|null",
  "status": "ok|queued|running|completed|failed|cancelled|blocked",
  "warnings": [],
  "artifact_refs": [],
  "next_actions": [],
  "data": {}
}
```

Rules:

- `workspace_id` is required for workspace-scoped calls.
- `operation_id` is required for long-running build operations.
- `warnings` must be a list of human-readable strings.
- `artifact_refs` must be stable references to workspace artifacts or source records.
- `next_actions` should tell an agent what to do next.
- `data` contains tool-specific payload.

## Tools To Implement

### `knowledge_workspace_create`

Create or register a knowledge workspace.

Input:

```json
{
  "name": "string",
  "root": "string|null",
  "owner": "string|null",
  "tags": ["string"]
}
```

Behavior:

- Create a workspace under `DATA_SERVICE_WORKSPACE_ROOT` unless a valid allowed `root` is provided.
- Initialize the normal `data_service` workspace layout.
- Return stable `workspace_id`, resolved `workspace_path`, and capabilities.

Output `data`:

```json
{
  "workspace_path": "string",
  "capabilities": {
    "ingest": true,
    "query": true,
    "quality_feedback": true,
    "build": true
  }
}
```

### `knowledge_workspace_list`

List allowed knowledge workspaces.

Input:

```json
{
  "owner": "string|null",
  "tag": "string|null",
  "limit": 50
}
```

Behavior:

- Only list workspaces under `DATA_SERVICE_WORKSPACE_ROOT`.
- Enforce a bounded `limit`.

Output `data`:

```json
{
  "items": [
    {
      "workspace_id": "string",
      "name": "string",
      "workspace_path": "string",
      "status": "active|archived",
      "updated_at": "string|null",
      "tags": []
    }
  ]
}
```

### `knowledge_workspace_describe`

Describe one workspace.

Input:

```json
{
  "workspace_id": "string|null",
  "workspace": "string|null"
}
```

Behavior:

- Accept either `workspace_id` or an allowed `workspace` path.
- Return layout, summary status, engine status, latest build status, and quality status.

Output `data`:

```json
{
  "layout": {},
  "summary": {},
  "engines": {
    "llmwiki": {},
    "graphrag": {}
  },
  "latest_build": null,
  "quality": {}
}
```

### `knowledge_source_import`

Import external source files or text payloads into a controlled source area.

Input:

```json
{
  "workspace_id": "string",
  "paths": ["string"],
  "texts": [
    {
      "title": "string",
      "content": "string",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

Behavior:

- Validate all source paths with an allowlist.
- Reject symlink/path traversal bypasses.
- Enforce file size limits.
- Compute `sha256` and handle duplicate imports idempotently.
- Do not write directly into generated LLMWiki / GraphRAG output folders.

Output `data`:

```json
{
  "sources": [
    {
      "source_id": "string",
      "sha256": "string",
      "title": "string",
      "status": "imported|duplicate|blocked",
      "path": "string|null"
    }
  ]
}
```

### `knowledge_source_list`

List workspace sources.

Input:

```json
{
  "workspace_id": "string",
  "status": "string|null",
  "limit": 100
}
```

Output `data`:

```json
{
  "items": [
    {
      "source_id": "string",
      "sha256": "string",
      "title": "string",
      "status": "active|removed|duplicate|blocked",
      "low_signal": {},
      "ingest_status": "pending|built|failed|null"
    }
  ]
}
```

### `knowledge_source_remove`

Soft-remove or deactivate a source.

Input:

```json
{
  "workspace_id": "string",
  "source_id": "string",
  "reason": "string|null"
}
```

Behavior:

- Do not physically delete historical build artifacts by default.
- Mark the source inactive/removed.
- Return updated source state.

### `knowledge_build_start`

Start a build operation.

Input:

```json
{
  "workspace_id": "string",
  "mode": "full|incremental|graph_only|llmwiki_only"
}
```

Behavior:

- Must not block the MCP host for long builds.
- Return an `operation_id` immediately.
- Record operation state in the workspace.
- Supported stages:
  - `source_import`
  - `distill`
  - `llmwiki`
  - `graphrag`
  - `quality_plan`

Output `data`:

```json
{
  "mode": "full",
  "stage": "queued",
  "progress": 0.0
}
```

### `knowledge_build_status`

Poll a build operation.

Input:

```json
{
  "workspace_id": "string",
  "operation_id": "string"
}
```

Output `data`:

```json
{
  "mode": "full|incremental|graph_only|llmwiki_only",
  "stage": "source_import|distill|llmwiki|graphrag|quality_plan|completed|failed|cancelled",
  "progress": 0.0,
  "error": null,
  "retryable": true,
  "artifacts": []
}
```

### `knowledge_build_cancel`

Cancel a build operation.

Input:

```json
{
  "workspace_id": "string",
  "operation_id": "string",
  "reason": "string|null"
}
```

Behavior:

- If already completed, return completed state and add a warning.
- If cancellable, move to `cancelled`.
- Do not leave workspace in a half-written corrupt state.

### `knowledge_workspace_archive`

Archive a workspace.

Input:

```json
{
  "workspace_id": "string",
  "reason": "string|null"
}
```

Behavior:

- Mark workspace read-only / archived.
- Do not physically delete data.

## Security Requirements

- Workspace access must be limited to `DATA_SERVICE_WORKSPACE_ROOT` or an existing explicit allowlist.
- Source imports must use source-path allowlist validation.
- Resolve real paths before checks; reject symlink escapes.
- Enforce bounded limits for `limit`, `top_k`, file count, text length, and file size.
- Do not let any MCP call mutate global workspace state implicitly.
- Each call must independently validate its workspace.
- Reading a correction plan must not implicitly write unless an explicit rebuild flag is provided.
- Existing quality governance semantics must remain read-time and reversible.

## Compatibility Requirements

- Do not remove or rename existing MCP tools.
- Keep per-call `workspace` support for existing tools.
- New lifecycle tools must coexist with:
  - `knowledge_ingest`
  - `knowledge_query`
  - `knowledge_quality_summary`
  - `knowledge_correction_plan`
  - `knowledge_quality_feedback`
  - `knowledge_correction_rules`
  - `knowledge_review_correction_rule`

## Testing Requirements

Add or extend tests in `backend/tests/test_data_service_mcp.py`.

Minimum cases:

- `list_tools` includes all lifecycle tools.
- workspace create/list/describe works under a temporary `DATA_SERVICE_WORKSPACE_ROOT`.
- source import from file returns `source_id` and `sha256`.
- duplicate import is idempotent and does not create duplicate source records.
- source import rejects paths outside allowlist.
- source import rejects symlink escapes.
- build start returns `operation_id` and queued/running status without blocking.
- build status returns stage, progress, artifacts, and retryable error payload.
- build cancel returns cancelled or completed-with-warning.
- workspace archive marks workspace archived and keeps data.
- multi-workspace calls remain isolated.
- existing quality tools still pass.

Suggested command:

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
python3 -m pytest backend/tests/test_llmwiki.py -q
```

## Acceptance Scenario

An external Harness project must be able to use MCP to complete:

```text
create workspace
  -> import source
  -> start build
  -> poll build status
  -> query knowledge
  -> submit quality feedback
  -> review correction rule
  -> read correction plan impact
```

The scenario is accepted when every step returns the shared envelope, no unauthorized path is accessible, duplicate imports are idempotent, and existing MCP quality tools remain compatible.
