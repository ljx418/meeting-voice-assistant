# V4.0 Manual Acceptance: Simple Workflow Run and Agent Node Adjustment

This acceptance case validates the dev/local Workflow Console path for a simple workflow deployment, runtime observation, and governed Agent-assisted node adjustment.

## Scope

- Dev/local validation only.
- The workflow is seeded through the local e2e BFF smoke server.
- The runtime path uses the deterministic V3.6 dummy workflow.
- The Agent window creates a WorkflowPatch proposal only.
- The user must apply the patch from the Editing Panel.
- This does not prove Agent executor, controlled executor, production deployment, or complete Workflow Studio readiness.

## Command

```bash
cd apps/workflow-console
npm run acceptance:workflow-agent-visible
```

## Expected User Journey

1. Chrome opens Workflow Console in headed mode.
2. A simple workflow is already created, published, started, and visible in the instance selector.
3. The station board shows the running workflow state.
4. The artifact panel shows at least one output artifact.
5. The user opens Agent 助手.
6. The user enters: 给这个工作流增加一个质量检查节点。
7. Agent shows a node adjustment proposal.
8. The board does not show 质量检查节点 before apply.
9. The user opens the Editing Panel from Agent handoff.
10. The Patch Diff shows add_station and 质量检查节点.
11. The user confirms apply.
12. The board refreshes from BFF truth and shows 质量检查节点.

## Required Assertions

- No browser request uses `/v1/rpc`.
- No browser request uses `/v1/events/subscribe`.
- Agent does not auto apply or auto publish.
- Apply request contains `user_confirmed: true`.
- Apply request contains `source: editing_panel`.
- Apply request carries a handoff reference when routed from Agent.
- Sensitive fields are absent from DOM and BFF JSON.
- The old runtime instance is not silently rewritten by the proposal.
