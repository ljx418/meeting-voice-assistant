# V3.6-H Completion Note

文档状态：V3.6-H complete: Business Event Bridge and Workflow Context ready.

当前下一阶段：V3.6-I Workflow Patch / Agent Editing Contract.

## Scope

V3.6-H 完成的是 Business Event Bridge / Workflow Context，不是 workflow patch、dummy pipeline E2E、完整 Workflow Studio 或 AgentTalkWindow。

本阶段冻结能力：

- `workflow.context.get`
- `workflow.context.update`
- `business.event.bind`
- `business.event.emit`
- WorkflowContext 分区：`system`、`business`、`runtime`、`metadata`
- 外部 context update 和 business event binding 只能写 `context.business`
- shallow merge 与 `context.business.*` path set
- `expected_revision` conflict -> `WORKFLOW_CONTEXT_CONFLICT`
- `BusinessEventBinding` MVP：`mode=set`、`target_path=context.business.*`、`payload_path=event.payload.*`
- `event_id` / `idempotency_key` 幂等应用
- live EventBridge events：`business.event.received`、`workflow.context.updated`
- scope / capability guard 和 redaction

## Verification

已执行：

```text
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
65 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
144 passed

./.venv/bin/python -m pytest -q
415 passed, 3 skipped

cd sdk/typescript && npm test
23 passed

drawio XML validation
passed
```

Focused H 测试入口：

```text
tests/test_v3_6_business_event_bridge.py
```

该测试覆盖：

- concrete `business.*` event validation
- `business.*` wildcard rejection
- meeting / knowledge / video canonical event rejection
- `workflow.context.get/update` scope isolation
- `expected_revision` conflict
- `business.event.bind`
- bound context update application
- repeated event idempotency
- no approval/runtime bypass
- EventBridge SSE for `business.event.received` / `workflow.context.updated`
- missing capability denied
- redaction
- no patch / quality / board mutation creep
- no SDK default exposure

## No False Green

V3.6-H 完成后只能声明：

```text
V3.6-H complete: Business Event Bridge and Workflow Context ready.
```

仍不能声明：

```text
workflow patch ready
dummy pipeline E2E ready
V3.6 complete
V4.0 ready
Workflow Studio ready
AgentTalkWindow ready
production workflow automation ready
distributed workflow engine ready
```

