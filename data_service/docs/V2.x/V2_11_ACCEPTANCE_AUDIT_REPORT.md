# V2.11 Acceptance Audit Report

## Conclusion

Conditionally accepted for V2.11 Coding Agent actionability.

The V2.11 implementation passes focused service/HTTP/MCP/CLI tests, public surface guard, neighboring V2.10 regression, syntax compilation, and a controlled real data_service E2E run. HarnessOS large-project E2E produced a structured performance blocker instead of accepted evidence; this is allowed by the V2.11 plan, but it remains a follow-up scalability item for later stages.

## Implemented Capabilities

| Capability | Status | Evidence |
| --- | --- | --- |
| Actionability index | accepted | `coding_agent/actionability/index.json`, definitions, references, test mapping artifacts. |
| AST provider mandatory | accepted | `python_ast` reports `available`; optional tree-sitter/LSP report `unavailable`. |
| Definition/reference graph v1 | accepted | Definitions and shallow references are generated from AST; forbidden relation count is 0. |
| Impact analysis | accepted | Three real data_service tasks return impacted candidates. |
| Test mapping | accepted | Test mapping artifact is generated with accepted/needs_review status. |
| Task-to-edit plan | accepted | Recommendations include evidence or `needs_review`; source mutation and runtime execution are false. |
| HTTP/MCP/CLI access | accepted | Focused test covers all three access paths. |
| Large-project E2E | structured_blocker | HarnessOS controlled run exceeded the acceptance runtime window and was not claimed as accepted. |

## Test Results

```text
pytest backend/tests/test_v2_11_coding_agent_actionability.py -q
Result: 1 passed

pytest backend/tests/test_public_surface_guard.py -q
Result: 5 passed

pytest backend/tests/test_v2_10_pattern_evidence.py -q
Result: 2 passed

python3 -m py_compile backend/data_service/code_assets/coding_agent/*.py backend/app/api/v1/code_assets_coding_agent.py backend/data_service/mcp_code_coding_agent_tools.py backend/data_service/cli_code_coding_agent.py
Result: passed
```

## Real data_service E2E

Input repo:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Controlled scan policy:

```text
include: backend/**/*.py, docs/V2.x/V2_11*.md, docs/V2.x/V2_11*.drawio
exclude: frontend/**, workspace/**, backend/app/static/**, node_modules/**, .git/**, __pycache__/**, examples/**
```

Observed result:

```json
{
  "codebase_id": "codebase_data_service",
  "snapshot_id": "snap_8fa092874a50a1dc6917",
  "files": 300,
  "definitions": 3736,
  "references": 31363,
  "test_mappings": 4328,
  "forbidden_relations": 0,
  "impact_counts": [3313, 2757, 2720],
  "task_plan_recommendations": [12, 12, 12]
}
```

## HarnessOS Large-Project Result

Input repo:

```text
/Users/Zhuanz/Desktop/workspace/harnessOS
```

Result:

```text
structured_blocker: HARNESSOS_CONTROLLED_E2E_TIMEOUT
```

Reason:

The controlled HarnessOS E2E run exceeded the runtime window. V2.11 does not claim HarnessOS accepted evidence. The blocker is a scalability signal for later large-project actionability work and does not invalidate the accepted data_service V2.11 capability.

## PRD/Spec Review

No major PRD deviation was found.

V2.11 does not:

- mutate source files;
- execute runtime commands;
- claim full call graph;
- claim data flow, control flow, runtime topology, or type inference;
- treat tree-sitter/LSP as available without configuration;
- treat token-only matching as accepted actionability evidence.

## Open Findings

| Severity | Finding | Disposition |
| --- | --- | --- |
| major | None | closed |
| fatal | None | closed |
| minor | HarnessOS controlled run needs a faster large-project profile. | deferred to follow-up scalability hardening |
