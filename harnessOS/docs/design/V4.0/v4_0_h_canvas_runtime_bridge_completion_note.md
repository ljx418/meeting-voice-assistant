# V4.0-H Canvas-to-runtime Bridge Completion Note

文档状态：V4.0-H completion evidence recorded。

允许完成声明：

```text
V4.0-H complete: canvas-to-runtime patch bridge ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full low-code canvas editing ready
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
```

## Evidence Checklist

已完成验证：

```text
apps/workflow-console npm test: 24 passed
apps/workflow-console npm run build: passed
apps/workflow-console npm run test:e2e: 3 passed
pytest tests/test_v4_0_canvas_runtime_bridge_*.py -q: 8 passed
pytest tests/test_v4_0_*.py -q: 62 passed
pytest tests/test_v3_6_*.py -q: 86 passed
pytest tests/test_v3_5_*.py -q: 146 passed
pytest -q: 503 passed, 3 skipped
cd sdk/typescript && npm test: 23 passed
xmllint drawio: passed
```

## Implemented Scope

- Node library click/drag creates a ghost proposal state and a `NodeAddIntent`.
- Edge proposal uses `operation=update_edge` and `edge_patch.action=add/remove/update`; no arbitrary `add_edge` RPC surface was added.
- Inspector edits stay local until the user clicks `生成 Patch`.
- BFF uses unified `POST /bff/workflows/{workflow_template_id}/patches`.
- Proposal payload validation rejects UI layout fields and sensitive/raw payload fields.
- Apply / Reject / Publish remain governed by V4.0-G routes and still require explicit user confirmation.
- Browser smoke verifies no direct `/v1/rpc` or `/v1/events/subscribe` calls and no token/raw payload DOM leakage.

## No False Green

This completion note only supports:

```text
V4.0-H complete: canvas-to-runtime patch bridge ready for dev/local Workflow Console.
```

It does not support:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full low-code canvas editing ready
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
```
