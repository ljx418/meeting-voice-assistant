# V4.0-N Canvas Editing Readiness Completion Note

状态：V4.0-N complete；dev/local Workflow Console canvas editing readiness baseline 已完成。完整回归结果见本文件 Validation Commands。

允许声明：

```text
V4.0-N complete: canvas editing readiness baseline ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete Workflow Studio ready
full low-code canvas editing ready
direct canvas-to-runtime mutation ready
complete AgentTalkWindow ready
controlled executor ready
autonomous workflow editing ready
production-ready external app support
```

## Implementation Evidence

新增 / 更新代码：

```text
apps/api/routers/bff.py
apps/workflow-console/src/api/canvasPatchIntents.ts
apps/workflow-console/src/api/types.ts
apps/workflow-console/src/api/workflowConsoleClient.ts
apps/workflow-console/src/hooks/useWorkflowConsoleData.ts
apps/workflow-console/src/components/ConsoleShell.tsx
apps/workflow-console/src/components/StationBoard.tsx
apps/workflow-console/src/components/WorkflowEditingPanel.tsx
```

新增 BFF route：

```text
GET /bff/instances/{instance_id}/canvas-projection
```

新增 / 更新 tests：

```text
tests/test_v4_0_canvas_editing_readiness_bff.py
tests/test_v4_0_canvas_editing_readiness_contract.py
tests/test_v4_0_canvas_editing_readiness_scope.py
tests/test_v4_0_canvas_editing_readiness_redaction.py
apps/workflow-console/src/__tests__/canvasEditingReadiness.test.tsx
apps/workflow-console/e2e/workflow-canvas-editing-readiness-smoke.spec.ts
```

## Verified Behavior

- Node catalog 使用受控 descriptor contract；BFF 校验 catalog id、版本、station kind、schema version 和 allowed refs。
- Node click/drag 只生成 ghost node 与 patch proposal；Apply 前 board/status/draft revision 不变。
- Canvas projection 从 draft/template、board/status 和 patch diff 派生；runtime state 仍来自 BFF truth。
- Edge creation 只使用 `update_edge`，并拒绝 self-loop、duplicate、missing station、cycle 和 MVP artifact contract 不兼容。
- Inspector typing 不调用网络；“生成 Patch”才发 BFF proposal request。
- Layout state 不进入 patch payload 或 V3.6 runtime object。
- Apply/reject/publish 继续走 V4.0-G governed Editing Panel，要求 `user_confirmed=true`。
- Agent 仍不能 auto apply/publish/respond/update/emit/start/rerun。
- DTO / DOM 不泄露 token、Authorization、raw trace、raw artifact 或 raw connector payload。

## Validation Commands

本阶段已执行：

```text
./.venv/bin/python -m pytest tests/test_v4_0_canvas_editing_readiness_*.py -q
11 passed, 5 warnings

cd apps/workflow-console && npm test
39 passed

cd apps/workflow-console && npm run build
passed

./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
116 passed, 5 warnings

./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed, 6 warnings

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed, 6 warnings

./.venv/bin/python -m pytest -q
First run: 1 failed, 556 passed, 3 skipped, 6 warnings
Rerun: 557 passed, 3 skipped, 6 warnings
Targeted rerun for first-run failure:
./.venv/bin/python -m pytest tests/test_gateway_protocol.py::test_gateway_connector_execution_submit_poll_collect_and_cancel -q
1 passed, 5 warnings

cd apps/workflow-console && npm run test:e2e
9 passed

cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

## No False Green

V4.0-N 只证明 canvas editing readiness baseline。它不证明完整 Workflow Studio、完整低代码编辑器、直接 canvas-to-runtime mutation、完整 AgentTalkWindow、controlled executor、autonomous workflow editing 或 production-ready external app support。
