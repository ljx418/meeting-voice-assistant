# V4.0-O Governed Canvas Proposal Workflow Completion Note

文档状态：V4.0-O implementation evidence complete for dev/local validation。

## Allowed Claim

```text
V4.0-O complete: governed canvas proposal workflow ready for expanded dev/local Workflow Console validation.
```

## Forbidden Claims

```text
complete Workflow Studio ready
full low-code canvas editing ready
complete AgentTalkWindow ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
direct canvas-to-runtime mutation ready
production-ready external app support
```

## Implementation Evidence

BFF / API:

```text
apps/api/routers/bff.py
```

Workflow Console frontend:

```text
apps/workflow-console/src/api/types.ts
apps/workflow-console/src/api/workflowConsoleClient.ts
apps/workflow-console/src/api/canvasPatchIntents.ts
apps/workflow-console/src/hooks/useWorkflowConsoleData.ts
apps/workflow-console/src/components/ConsoleShell.tsx
apps/workflow-console/src/components/WorkflowEditingPanel.tsx
```

Tests:

```text
tests/test_v4_0_canvas_patch_queue_bff.py
tests/test_v4_0_canvas_projection_freshness.py
tests/test_v4_0_canvas_edge_contracts.py
tests/test_v4_0_inspector_mapping_v2.py
tests/test_v4_0_node_catalog_versioning.py
tests/test_v4_0_canvas_proposal_scope_redaction.py
tests/test_v4_0_claim_guard.py
apps/workflow-console/src/__tests__/canvasPatchQueue.test.tsx
apps/workflow-console/src/__tests__/canvasProjectionFreshness.test.tsx
apps/workflow-console/src/__tests__/inspectorMappingV2.test.tsx
apps/workflow-console/src/__tests__/nodeCatalogVersioning.test.tsx
apps/workflow-console/e2e/workflow-canvas-patch-queue-smoke.spec.ts
apps/workflow-console/e2e/workflow-inspector-mapping-smoke.spec.ts
apps/workflow-console/e2e/workflow-catalog-versioning-smoke.spec.ts
```

Docs:

```text
docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_plan.md
docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_completion_note.md
```

## Verified Behavior

```text
PatchQueueDTO includes selected_patch stale guard fields and derived stale/blocked status.
CanvasDraftProjection includes freshness marker, patch_queue_revision and stale_reasons.
BFF controlled catalog is exposed via /bff/workflows/{id}/node-catalog.
Frontend node library renders BFF catalog data instead of defining runtime semantics locally.
Inspector mapping V2 rejects unknown, layout, token and raw payload fields.
Edge validation V2 rejects self-loop, duplicate, missing station, cycle, wrong edge id and incompatible artifact schema_ref.
Event payload cannot construct canvas, patch queue, catalog, edge or evidence truth.
DTO, DOM, error response and event payload redaction paths remain covered.
Browser requests remain BFF-only and do not call /v1/rpc or /v1/events/subscribe.
```

## Validation Commands

Focused V4.0-O tests:

```text
./.venv/bin/python -m pytest tests/test_v4_0_canvas_patch_queue_bff.py tests/test_v4_0_canvas_projection_freshness.py tests/test_v4_0_canvas_edge_contracts.py tests/test_v4_0_inspector_mapping_v2.py tests/test_v4_0_node_catalog_versioning.py tests/test_v4_0_canvas_proposal_scope_redaction.py tests/test_v4_0_claim_guard.py -q
18 passed, 5 warnings
```

V4.0 focused tests:

```text
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
134 passed, 5 warnings
```

V3.6 focused regression:

```text
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed, 6 warnings
```

V3.5 focused regression:

```text
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed, 6 warnings
```

Full pytest:

```text
./.venv/bin/python -m pytest -q
575 passed, 3 skipped, 6 warnings
```

Workflow Console npm test:

```text
cd apps/workflow-console && npm test
48 passed
```

Workflow Console build:

```text
cd apps/workflow-console && npm run build
passed
```

Workflow Console e2e:

```text
cd apps/workflow-console && npm run test:e2e
12 passed
```

TypeScript SDK:

```text
cd sdk/typescript && npm test
23 passed
```

Drawio XML validation:

```text
xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

## No False Green

V4.0-O 只证明 governed canvas proposal workflow。

不证明：

```text
complete Workflow Studio
full low-code canvas editing
complete AgentTalkWindow
controlled executor
Agent executor
autonomous workflow editing
direct canvas-to-runtime mutation
production-ready external app support
```
