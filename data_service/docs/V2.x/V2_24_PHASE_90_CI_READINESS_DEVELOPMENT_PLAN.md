# V2.24 Phase 90 Production Readiness & CI Hardening Development Plan

## 1. Phase Goal

Phase 90 closes V2.18-V2.24 by turning the existing test, contract, artifact, frontend, and real-repo checks into a structured production-readiness artifact.

This phase does **not** build a hosted CI system. It produces local artifacts that CI and release workflows can consume.

## 2. Product Scope

In scope:

- CI readiness report.
- Release readiness Markdown report.
- test layer command registry.
- warning budget summary.
- public payload redaction gate.
- artifact validation gate.
- HTTP/MCP/CLI read parity for readiness artifacts.
- real `data_service` repository E2E acceptance.

Out of scope:

- hosted CI runner provisioning;
- GitHub Actions migration;
- automatic dependency upgrades;
- automatic warning cleanup;
- production deployment automation.

## 3. Inputs

Phase 90 consumes the accepted V2.18-V2.23 platform artifacts:

```text
platform/console/platform_console.json
platform/contracts/artifact_contract_registry.json
platform/contracts/validation_report.json
platform/tool_catalog/mcp_tool_catalog.json
platform/tool_catalog/workflow_guides.json
platform/incremental/incremental_build_plan.json
platform/providers/provider_capabilities.json
platform/providers/provider_execution_contract.json
platform/governance/overlay_report.json
```

It also consumes real command evidence from the current worktree:

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_18_platform_console.py ... -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q
npm run build
PYTHONPATH=backend python3 -m pytest backend/tests -q
git diff --check -- .
```

## 4. Outputs

```text
workspace/assets/codebase/{codebase_id}/platform/ci/ci_readiness_report.json
workspace/assets/codebase/{codebase_id}/platform/ci/release_readiness_report.md
```

## 5. Implementation Design

Add a focused platform CI module:

```text
backend/data_service/code_assets/platform/ci.py
```

Responsibilities:

1. Build test layer registry.
2. Read and summarize command evidence supplied by the caller.
3. Classify skipped / passed / failed / not_run.
4. Enforce warning budget.
5. Run public payload redaction checks over platform artifacts.
6. Verify required platform artifacts exist.
7. Render release readiness Markdown.

Persistence additions:

```text
backend/data_service/code_assets/platform/persistence.py
  ci_dir
  ci_readiness_report_path
  release_readiness_report_path
  ci_artifact_refs
  write_ci_readiness_report
  read_ci_readiness_report
  read_release_readiness_report
```

Public entrypoints:

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/readiness/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/readiness
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/release-report

MCP:
knowledge_code_platform_ci_readiness_build
knowledge_code_platform_ci_readiness_read
knowledge_code_platform_ci_release_report

CLI:
knowledge code platform ci-readiness-build
knowledge code platform ci-readiness
knowledge code platform ci-release-report
```

## 6. CI Readiness Schema

Minimum JSON shape:

```json
{
  "schema_version": "v2.24",
  "artifact_type": "ci_readiness",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "optional",
  "overall_status": "ready | blocked | needs_review",
  "test_layers": {
    "unit": {"status": "passed | failed | skipped | not_run", "command": "string"},
    "contract": {"status": "passed | failed | skipped | not_run", "command": "string"},
    "artifact": {"status": "passed | failed | skipped | not_run", "command": "string"},
    "frontend": {"status": "passed | failed | skipped | not_run", "command": "string"},
    "real_repo_e2e": {"status": "passed | failed | skipped | not_run", "command": "string"},
    "slow_nightly": {"status": "skipped | not_run", "reason": "string"}
  },
  "warning_budget": {
    "current": 0,
    "budget": 0,
    "over_budget": false
  },
  "security_gate": {
    "redaction": "passed | failed",
    "absolute_path_leak_count": 0,
    "secret_leak_count": 0
  },
  "artifact_gate": {
    "required_artifact_count": 0,
    "present_artifact_count": 0,
    "missing_artifacts": []
  },
  "release_gate": {
    "ready": true,
    "blockers": [],
    "needs_review": []
  },
  "artifact_refs": []
}
```

## 7. Development Tasks

1. Add CI persistence helpers.
2. Add `PlatformCIReadinessService`.
3. Add release Markdown renderer.
4. Add HTTP/MCP/CLI thin wrappers.
5. Add focused tests for:
   - readiness build/read;
   - skipped not counted as passed;
   - redaction failure blocks readiness;
   - missing artifact blocks readiness;
   - HTTP/MCP/CLI parity.
6. Run real `data_service` E2E using actual command evidence.

## 8. Architecture Guardrails

- Do not add Phase 90 core logic to `backend/app/api/v1/data_service.py`.
- Do not add Phase 90 core logic to `backend/data_service/service.py`.
- Do not mutate V2.18-V2.23 source artifacts.
- Do not mark skipped or not-run layers as passed.
- Do not hide release blockers behind a single score.

## 9. Exit Criteria

Phase 90 may exit implementation only after:

- focused tests pass;
- real repo E2E builds readiness artifacts;
- frontend build passes;
- full backend regression passes;
- public redaction gate passes;
- release report references real command evidence;
- acceptance audit report is written.
