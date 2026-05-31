# V2 Phase 2 Acceptance Plan: Repo Snapshot + File Manifest

> Phase: 2 / PR2.
> Acceptance requires real data. Mock-only acceptance is not valid.

## 1. Real Data Scope

Real codebase:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Temporary workspace root:

```text
/private/tmp/data_service_v2_phase2_workspace
```

## 2. Required E2E Flow

1. Create or reuse a temporary workspace.
2. Import the current repo as a codebase through public Phase 1 APIs.
3. Generate snapshot through HTTP.
4. Generate or read snapshot through MCP.
5. Generate or read snapshot through CLI.
6. Inspect artifact files on disk.
7. Repeat snapshot generation without content changes and verify stable `snapshot_id`.
8. Modify a controlled file in a temporary repo copy and verify snapshot identity or changed fingerprint changes.
9. Verify source registry before/after is unchanged.

## 3. Required Assertions

- Snapshot artifacts exist on disk.
- Same content and scan policy produce the same `snapshot_id`.
- Controlled content change produces a different `snapshot_id` or changed fingerprint.
- `snapshot_id` does not depend on `generated_at`.
- `.env`, credentials, private keys, and secret-pattern files are skipped or reported as `SENSITIVE_SKIPPED`.
- `.git`, `.venv`, `node_modules`, `dist`, `build`, `__pycache__`, cache directories, and V2 artifact output directories are excluded.
- If `workspace/assets/codebase/**`, `assets/codebase/**`, or `.data_service/**` is inside the scanned repo, it is excluded.
- Warnings are repo-relative and do not expose absolute paths.
- Binary, oversized, and unreadable files become warnings rather than global failure.
- Important paths include README, docs, backend, frontend, tests, config files, and entrypoints when present.
- Language stats include Python and Markdown for the current repo.
- `lifecycle/sources.json` is not created or modified by snapshot generation.

## 4. Failure Paths

Must test:

- missing codebase ID
- archived codebase or workspace behavior
- non-existent snapshot ID
- invalid scan policy override
- sensitive file skip
- unreadable or oversized file warning
- artifact self-exclusion

## 5. Suggested Commands

Focused Phase 2:

```bash
python3 -m pytest backend/tests/test_v2_codebase_snapshot.py
```

Regression:

```bash
python3 -m pytest backend/tests/test_v2_codebase_registry.py backend/tests/test_v2_codebase_http.py backend/tests/test_v2_codebase_mcp.py backend/tests/test_v2_codebase_cli.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_target_http_source.py
```

Full backend before acceptance:

```bash
python3 -m pytest backend/tests
```

Frontend build is required only if frontend contract files changed:

```bash
npm run build --prefix frontend
```

## 6. Acceptance Decision

Phase 2 passes only if:

- all required tests pass
- artifacts are inspected from disk
- real repo E2E passes
- no public path leak is found
- source registry remains unchanged
- Phase 2 audit report has no open fatal or major findings
