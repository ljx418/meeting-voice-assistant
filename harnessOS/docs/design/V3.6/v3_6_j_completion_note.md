# V3.6-J Completion Note

文档状态：V3.6 complete baseline 已冻结；V3.6/V4.0 preflight hardening complete。

## Scope

V3.6-J 完成的是平台中立 Dummy Pipeline E2E / V4.0 Gate。它不新增单点 runtime 能力，而是通过协议入口消费 V3.6-A 到 V3.6-I 已完成能力，证明 workflow runtime 可以作为 V4.0 Workflow Studio / AgentTalkWindow 的后端事实源。

本阶段冻结能力：

- Runtime E2E：template create、publish V1、start instance、station A/B/C、artifact lineage、approval.required、approval.respond、quality evaluation、board reconstruction、business context update、workflow completed。
- Editing E2E：workflow.patch.propose、diff、apply to draft、publish V2。
- V1 `WorkflowVersion.snapshot` 和已完成 V1 workflow instance 不受 V2 patch/publish 影响。
- patched V2 instance 至少可运行一个 station，证明 patch 产物可被 runtime 消费。
- EventBridge live SSE 覆盖 `approval.required`、`business.event.received`、`workflow.context.updated`、`workflow.patch.proposed`、`workflow.patch.applied`。
- `quality.evaluated` 仍为 trace-only，不作为 V3.6-J live EventBridge 出门条件。
- Board API 可重建 workflow_instance、stations、station_runs、jobs、artifacts、approvals、quality_evaluations、trace_summary、current_station_ids。
- Scope isolation 覆盖 `reference_app/demo_a/local` 与 `reference_app/demo_b/local`。
- 外部 `/v1/rpc` capability smoke 覆盖代表性 read/write allow/deny。
- redaction 覆盖 trace、event、board、quality、failure_context、patch diff 和 expected fixture。

## Verification

新增 J 阶段测试入口：

```text
tests/test_v3_6_dummy_pipeline_e2e.py
tests/fixtures/v3_6/dummy_pipeline/
```

当前 focused regression：

```text
./.venv/bin/python -m pytest tests/test_v3_6_dummy_pipeline_e2e.py -q
6 passed

./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed
```

V3.5 / full / SDK regression：

```text
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

./.venv/bin/python -m pytest -q
443 passed, 3 skipped

cd sdk/typescript && npm test
23 passed

drawio XML validation
passed
```

## Post-J Preflight Hardening

V3.6-J 后执行了 V4.0-0 前置硬化，修复代码检视发现的 scope、governance、EventBridge 和 business event 原子性风险。

新增或补强的证据：

```text
./.venv/bin/python -m pytest tests/test_v3_5_event_bridge.py tests/test_v3_6_business_event_bridge.py tests/test_gateway_platform_startup_neutrality.py -q
23 passed

./.venv/bin/python -m pytest tests/test_v3_6_*.py tests/test_v3_6_preflight_*.py -q
86 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

./.venv/bin/python -m pytest -q
443 passed, 3 skipped

cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V3.6/v3_6_current_gap_analysis.drawio docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

本轮额外锁定：

- `/v1/events/subscribe` follow mode 会轮询新增事件，不再只输出 heartbeat。
- subscription token 绑定 token allowed origins。
- `business.event.emit` 的 idempotency marker 与 context update 原子应用；失败不会消耗 event_id。
- `business.event.bind` 拒绝重复 `binding_id`。

## No False Green

V3.6-J 完成后可以声明：

```text
V3.6 complete: Workflow Runtime Contract & Pipeline Operating Model ready for V4.0 development.
```

仍不能声明：

```text
V4.0 complete
Workflow Studio ready
AgentTalkWindow ready
production workflow automation ready
distributed workflow engine ready
```
