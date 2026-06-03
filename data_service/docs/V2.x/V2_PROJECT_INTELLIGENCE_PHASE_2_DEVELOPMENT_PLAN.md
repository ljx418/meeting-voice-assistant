# V2 Phase 2 Development Plan: Repo Snapshot + File Manifest

> Phase: 2 / PR2.
> Goal: generate stable, inspectable repo snapshots for V2 codebase assets.
> Implementation must not start until `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_2_AUDIT_REPORT.md` has no open fatal or major findings.

## 1. Scope

Phase 2 adds snapshot generation and read access for codebase assets created in Phase 1.

In scope:

- scan codebase files with ignore, sensitive, binary, large-file, and unreadable-file handling
- generate deterministic snapshot artifacts
- record git metadata when available
- compute language/file/LOC stats
- detect important paths
- expose snapshot through HTTP, MCP, and CLI
- validate real repo E2E using `/Users/Zhuanz/Desktop/workspace/data_service`

Out of scope:

- public surface inventory
- Python symbol index
- mapping/evidence trace
- project overview
- agent context pack
- true incremental build semantics

## 2. Implementation Plan

Add a focused snapshot implementation under `backend/data_service/code_assets/`.

Required behavior:

- read `codebase.json` from the Phase 1 registry
- merge stored scan policy with request overrides
- walk the codebase root deterministically
- exclude default ignored directories:
  - `.git`
  - `.venv`
  - `node_modules`
  - `dist`
  - `build`
  - `__pycache__`
  - cache directories
- exclude V2 output directories when they appear under the scanned repo:
  - `workspace/assets/codebase/**`
  - `assets/codebase/**`
  - `.data_service/**`
- skip or warn on sensitive paths:
  - `.env`
  - credentials files
  - private keys
  - secret-pattern files
- skip binary files and oversized files
- record unreadable files as warnings
- compute content-based file fingerprints
- compute `snapshot_id` from content fingerprint, git state if available, and scan policy hash
- exclude `generated_at` and other non-content timestamps from `snapshot_id`
- document dirty fingerprint scope in `snapshot.json`

Required artifacts:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/snapshot.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/files.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/stats.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/warnings.jsonl
```

Required HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots/{snapshot_id}
```

Required MCP:

```text
knowledge_codebase_snapshot
```

Required CLI:

```text
knowledge code snapshot
```

## 3. Data Contract

`snapshot.json` must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `created_at`
- `scan_policy_hash`
- `content_fingerprint`
- `dirty_fingerprint`
- `git`
- `stats`
- `important_paths`
- `artifact_refs`
- `warning_count`

`files.jsonl` records must include:

- `path`
- `kind`
- `language`
- `size_bytes`
- `loc`
- `sha256`
- `included`
- `skip_reason`

`warnings.jsonl` records must include:

- `code`
- `path`
- `message`
- `severity`

Warning paths must be repo-relative.

## 4. Architecture Gates

- Do not add Phase 2 snapshot implementation into `backend/data_service/service.py`.
- Do not add Phase 2 HTTP routes into `backend/app/api/v1/data_service.py`.
- Do not add substantial snapshot CLI logic into `backend/data_service/__main__.py`.
- Do not create or modify `lifecycle/sources.json`.
- Do not return absolute paths in public HTTP/MCP/CLI payloads.

## 5. Expected Files To Add Or Touch

Expected new or modified areas:

- `backend/data_service/code_assets/`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`
- `backend/app/api/v1/code_assets.py`
- `backend/tests/test_v2_codebase_snapshot.py`
- existing V2 codebase HTTP/MCP/CLI tests

Any change to `backend/app/api/v1/data_service.py` or `backend/data_service/service.py` is a major audit finding unless explicitly approved.
