# V3.6/V4.0 Preflight Hardening Note

文档状态：V3.6/V4.0 preflight hardening complete。正式 V4.0-0 开发仍需由后续任务显式启动。

## Scope

本轮收口不是 V4.0 开发，也不是新增 Workflow Studio / AgentTalkWindow。它只修复 V3.6 complete baseline 进入 V4.0 前代码检视发现的 scope、governance、EventBridge 和业务事件原子性风险。

已完成硬化：

- `session.close` / `session.resume` 增加 scope guard，direct Gateway RPC 与 `/v1/rpc` 均防跨 scope。
- `memory.get` 增加 scope ownership check，外部 auth guard 增加 memory_id resource ownership check。
- 高风险 workflow patch apply 收紧为 `WORKFLOW_ACTION_FORBIDDEN`，后续必须通过正式 patch approval flow。
- workflow-bound approval 禁止 legacy `approval.approve/reject` 继续 workflow，`approval.respond` 是唯一 continuation path。
- `workflow.board.get` / `workflow.instance.status` 读取 job 时做 scope double-check。
- business EventBridge channel 需要 `business_events.read`，workflow_context channel 需要 `workflow_context.read`。
- `/v1/events/subscribe` follow mode 会轮询新增事件，不再只输出 heartbeat。
- subscription token 绑定 token allowed origins，native EventSource signed URL 不能跨 origin 滥用。
- `business.event.emit` 的 idempotency marker 与 context update 原子应用，context update 失败不会消耗 event_id。
- `business.event.bind` 拒绝重复 `binding_id`，避免覆盖旧 binding。
- Gateway 平台启动路径不在模块顶层 hard import Meeting/Knowledge/Video workflow。
- Reference App 默认走 BFF structured helper，避免 `/bff/v1/rpc` 误路径。
- V4.0 drawio protocol 已对齐 V3.6 冻结 API 名称。

## Verification

Focused hardening tests：

```text
./.venv/bin/python -m pytest tests/test_v3_5_event_bridge.py tests/test_v3_6_business_event_bridge.py tests/test_gateway_platform_startup_neutrality.py -q
23 passed
```

V3.6 / V3.5 / full regression：

```text
./.venv/bin/python -m pytest tests/test_v3_6_*.py tests/test_v3_6_preflight_*.py -q
86 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

./.venv/bin/python -m pytest -q
443 passed, 3 skipped
```

TypeScript SDK and drawio validation：

```text
cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V3.6/v3_6_current_gap_analysis.drawio docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

## No False Green

可以声明：

```text
V3.6/V4.0 preflight hardening complete.
```

仍不能声明：

```text
Workflow Studio ready
AgentTalkWindow ready
production-ready external app support
distributed workflow engine ready
```
