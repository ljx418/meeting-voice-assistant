# V2.15 Acceptance Audit Report

## Result

Accepted for persisted-artifact review workbench, visual report, Mermaid graph, and context export scope.

## Evidence

Focused test command:

```text
PYTHONPATH=backend pytest backend/tests/test_v2_13_15_coding_agent_remaining.py -q
```

Result:

```text
2 passed
```

Regression commands:

```text
PYTHONPATH=backend pytest backend/tests/test_v2_12_safe_patch_planning.py backend/tests/test_v2_11_coding_agent_actionability.py -q
PYTHONPATH=backend pytest backend/tests/test_public_surface_guard.py -q
```

Results:

```text
4 passed
5 passed
```

## Accepted Capabilities

- Workbench JSON payload from persisted actionability, patch plan, runtime run, and incremental diff artifacts.
- HTML review page with sections, graph nodes, risk lanes, blockers, and escaped labels.
- Mermaid capability graph with node integrity checks.
- Context export that preserves evidence or explicit `needs_review`.
- HTTP/MCP/CLI parity for workbench read paths.

## Real data_service Smoke

Current repository smoke used real `data_service` actionability, patch plan, runtime run, and workbench generation:

```text
codebase_id=codebase_data_service
snapshot_id=snap_787592231f2e97e1f417
runtime_status=passed
workbench_id=workbench_f79225a4effba9ad
workbench_nodes=3
```

The smoke wrote only managed workspace artifacts and did not mutate the source repository.

## False-Acceptance Review

| Risk | Result |
| --- | --- |
| HTML introduces new facts | rejected by node/edge integrity assertions. |
| Mermaid contains unresolved nodes | rejected by edge endpoint checks. |
| Context export drops evidence but keeps recommendation | rejected by recommendation evidence/needs-review assertions. |
| Absolute path leak | rejected by serialized payload checks. |

## Open Findings

No fatal or major findings remain. Browser-grade interaction is intentionally not included; V2.15 exposes static HTML/Mermaid and JSON context export.
