# V2.20 Phase 86 MCP Tool Discovery Acceptance Audit Report

## 1. Audit Conclusion

Status: **accepted for Phase 86 implementation closure**.

Phase 86 implemented the V2.20 MCP Tool Catalog and Workflow Guide baseline on top of the existing V2.18 Product Console and V2.19 Artifact Contract layers.

The implementation is accepted because it:

- builds a persisted MCP tool catalog from the live `all_tool_specs()` registry, not from a static fixture;
- generates workflow guides for project reading, coding task preparation, and architecture review;
- verifies workflow guide tool references against the actual catalog;
- exposes matching HTTP, MCP, and CLI read/build contracts;
- uses real `data_service` repository data for E2E validation;
- does not leak absolute local paths in public artifacts;
- does not mutate V2.0-V2.19 source artifacts outside the new platform tool-catalog artifact area.

No fatal or major PRD/spec deviation was found.

## 2. Implemented Scope

Phase 86 adds:

- `backend/data_service/code_assets/platform/tool_catalog.py`
- persisted artifacts:
  - `platform/tool_catalog/mcp_tool_catalog.json`
  - `platform/tool_catalog/workflow_guides.json`
- HTTP endpoints:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog`
- MCP tools:
  - `knowledge_code_platform_tool_catalog_build`
  - `knowledge_code_platform_tool_catalog_read`
- CLI commands:
  - `knowledge code platform tool-catalog-build`
  - `knowledge code platform tool-catalog`

The service intentionally receives the live tool specs from the route/MCP layer instead of importing the registry inside the artifact builder. This keeps artifact construction deterministic while avoiding MCP registry circular-import risk.

## 3. Contract Checks

### Tool Catalog

Required properties verified:

- `schema_version = v2.20`
- `artifact_type = mcp_tool_catalog`
- `tool_count == len(all_tool_specs())`
- `validation_summary.registry_count == validation_summary.catalog_count`
- catalog tool names exactly match the live registry tool names
- group catalog includes platform tools
- public payload includes only repo-safe artifact refs

### Workflow Guides

Required properties verified:

- `schema_version = v2.20`
- `artifact_type = workflow_guides`
- guide count is non-empty and includes:
  - `project_reading`
  - `coding_task_preparation`
  - `architecture_review`
- `missing_tool_refs == []`
- every guide step references an available MCP tool

## 4. Test Evidence

Commands executed:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_20_tool_catalog.py -q
```

Result:

```text
2 passed
```

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q
```

Result:

```text
5 passed
```

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_18_platform_console.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_19_artifact_contracts.py -q
```

Result:

```text
2 passed
2 passed
```

```bash
npm run build
```

Result:

```text
vue-tsc && vite build completed successfully
```

```bash
PYTHONPATH=backend python3 -m pytest backend/tests -q
```

Result:

```text
462 passed, 617 warnings
```

```bash
git diff --check -- .
```

Result:

```text
passed
```

## 5. Real Repository E2E Evidence

Real input:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

E2E flow:

1. Create isolated workspace under `/private/tmp/data_service_v220_e2e`.
2. Import current `data_service` repository as a codebase asset.
3. Generate a repo snapshot.
4. Build MCP tool catalog from live `all_tool_specs()`.
5. Persist catalog and workflow guide artifacts.
6. Verify counts and missing references.
7. Run redaction scan over the generated tool catalog artifact directory.

Observed result:

```json
{
  "workspace_id": "data_service_v220_real_e2e",
  "codebase_id": "codebase_data_service_v220",
  "snapshot_id": "snap_b81da9b00c59c4baeb51",
  "tool_count": 163,
  "registry_count": 163,
  "catalog_count": 163,
  "group_count": 10,
  "guide_count": 3,
  "missing_workflow_tool_count": 0,
  "artifact_refs": 2
}
```

Redaction scan:

```bash
rg "/Users/Zhuanz/Desktop/workspace/data_service|/private/tmp/data_service_v220_e2e" \
  /private/tmp/data_service_v220_e2e/real_ws/assets/codebase/codebase_data_service_v220/platform/tool_catalog
```

Result:

```text
no matches
```

## 6. PRD / Spec Review

Phase 86 is aligned with the V2.18-V2.24 platform productization PRD:

- It improves Agent-facing tool discoverability.
- It gives users and external Agents a structured way to decide which MCP tools to call.
- It adds workflow guides without claiming autonomous orchestration.
- It preserves existing V2.18 and V2.19 platform contracts.
- It keeps HTTP/MCP/CLI access aligned.

No scope expansion was introduced:

- No direct tool execution workflow engine was added.
- No unsupported provider or runtime claim was introduced.
- No UI-only or mock-only catalog was accepted.

## 7. False Acceptance Review

Rejected false-green risks checked:

- **Static catalog risk**: rejected by asserting catalog names equal live `all_tool_specs()`.
- **Missing workflow reference risk**: rejected by asserting `missing_tool_refs == []`.
- **HTTP-only implementation risk**: rejected by MCP and CLI parity tests.
- **Fixture-only acceptance risk**: rejected by real `data_service` repository E2E.
- **Path leakage risk**: rejected by artifact redaction scan.
- **Regression risk**: rejected by full backend test suite and frontend build.
- **Circular import risk**: mitigated by lazy tool-spec provider injection.

## 8. Open Findings

Fatal findings: none.

Major findings: none.

Minor residual risks:

- Workflow guide chains are deterministic curated recommendations, not adaptive workflow execution.
- Catalog grouping is rule-based and may be refined in later phases as product analytics and real user usage data accumulate.

## 9. Exit Decision

Phase 86 can be marked complete.

The next phase may start only after its phase-specific development plan, acceptance plan, and pre-implementation audit close without fatal or major findings.
