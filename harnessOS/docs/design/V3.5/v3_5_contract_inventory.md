# V3.5 Contract Inventory

文档状态：V3.5-0 human-readable summary。
机器可读 exposure inventory 事实源：`core/protocol/contracts/`。
机器可读 schema 事实源：`core/protocol/schemas/`。

## 1. Purpose

本文件是 V3.5 Application Adaptation Layer 的人类可读 contract inventory 摘要。Phase0 后，以下文件是后续 schema registry、SDK、BFF、EventBridge 的 source of truth：

```text
core/protocol/contracts/
  method_inventory.py
  event_inventory.py
  error_inventory.py
```

`core/protocol/contracts/` 只包含 exposure inventory 和阶段状态 metadata，不注册 handler，不改变运行时行为。V3.5-A 后，`core/protocol/schemas/` 承载 params/result/event/error schema，并通过 contract tests 与 contracts inventory 对齐。

## 2. Phase0 Scope

Phase0 只做合同清单和目录脚手架：

- 新增 `core/protocol/contracts/` 机器可读 inventory。
- 新增 `sdk/`、`templates/`、`examples/reference_app/`、`docs/integration/` README/.gitkeep scaffold。
- 新增 Phase0 contract/scaffold tests。
- 新增 `docs/integration/v3_5_phase0_baseline.md` 记录验证基线。

Phase0 不改变 supported public API，不让 SDK 可用，也不让外部 App 可接入。

## 3. Method Inventory

每个 method entry 固定包含：

```text
method
surface
status
capability
stability
planned_phase
handler_ref
forbidden_reason
```

`surface` 分为：

- `default`：未来 core SDK 默认面。
- `optional`：高级或显式 opt-in 面。
- `forbidden_by_default`：legacy/debug/business facade，SDK/BFF 默认不得暴露。

`status` 分为：

- `implemented`
- `planned`
- `legacy`
- `debug`
- `deprecated`

Phase0 中 `events.subscribe` 和 `approval.respond` 已进入 default surface。V3.5-A 后，`approval.respond` 为 `implemented`；V3.5-C 后，`events.subscribe` 也为 `implemented` 且 `runtime_handler=true`。implemented methods 必须标记 `status=implemented`。legacy/debug/business facade 必须标记 `surface=forbidden_by_default` 并提供 `forbidden_reason`。

## 4. SDK Default Method Surface

默认 SDK 面只暴露平台中立方法：

| Method | Phase0 status | Planned phase |
| --- | --- | --- |
| `session.start` | implemented | baseline |
| `turn.start` | implemented | baseline |
| `events.subscribe` | implemented, runtime_handler=true | V3.5-C browser event bridge |
| `artifact.list` | implemented | baseline |
| `artifact.read_metadata` | implemented | baseline |
| `artifact.register_external` | implemented | baseline |
| `artifact.lineage` | implemented | baseline |
| `job.get` | implemented | baseline |
| `job.list` | implemented | baseline |
| `approval.respond` | implemented | V3.5-A |
| `connector.health` | implemented | baseline |
| `pack.list` | implemented | baseline |
| `pack.get` | implemented | baseline |

## 5. Optional Method Surface

可作为 advanced/debug-aware client 暴露，但不进入默认业务 SDK：

- `method.list`
- `app.list`
- `app.get`
- `connector.list`
- `connector.get`
- `connector.submit`
- `connector.poll`
- `connector.collect`
- `job.events`
- `session.events`
- `workflow.list`
- `policy.evaluate`
- `trace.list`
- `trace.get`

## 6. Forbidden By Default

以下不得进入 SDK/BFF 默认面：

- `meeting.*`
- `knowledge.*`
- `pack.execute_stub`
- `workflow.execute_stub`
- `debug.*`
- `admin.*`
- `test.*`

SDK thin client boundary：

- Core SDK default export 只能暴露平台协议客户端、scope helper、error mapping 和 event subscription helper。
- Core SDK default export 不得包含业务 wrapper，例如 `generateMinutes()`、`ingestDocument()`、`runMeetingWorkflow()`、`generateVideo()`、`analyzePortfolio()`。
- 业务便利层只能放在 BFF、optional extension、pack-generated client 或业务 App SDK。

## 7. Event Inventory

每个 event entry 固定包含：

```text
type
channel
status
replayable
aliases
```

Phase0 冻结 `artifact.registered` 为 canonical artifact event。如历史路径存在 `artifact.created`，只作为 `artifact.registered` 的 alias，不作为新的 canonical default event。

V3.5 Event Bridge 至少覆盖：

- chat：`turn.started`、`item.delta`、`turn.completed`、`turn.failed`
- job：`job.queued`、`job.running`、`job.completed`、`job.failed`、`job.cancelled`
- artifact：`artifact.registered`、`artifact.updated`、`artifact.read_blocked`
- approval：`approval.required`、`approval.approved`、`approval.rejected`
- trace：`trace.recorded`
- business：只保留 `business.*` namespace，不加入 Meeting/Knowledge 具体业务事件

## 8. Error Inventory

每个 error entry 固定包含：

```text
code
status
category
retryable
planned_phase
```

Phase0 error inventory 包含现有错误和 V3.5 planned errors。planned errors 必须带 `planned_phase`。

关键 planned errors：

- `SUBSCRIPTION_TOKEN_INVALID`
- `METHOD_FORBIDDEN`
- `METHOD_DEPRECATED`
- `SCOPE_REQUIRED`
- `APP_PROFILE_NOT_FOUND`
- `PACK_NOT_FOUND`
- `CONNECTOR_NOT_FOUND`
- `APPROVAL_CONFLICT`
- `APPROVAL_NOT_FOUND`
- `APPROVAL_RETRY_CONSUMED`
- `APPROVAL_INVALID_DECISION`

## 9. V3.5-0 Acceptance

- 机器可读 inventory 是 source of truth。
- `docs/design/V3.5/v3_5_contract_inventory.md` 只是人类可读摘要。
- planned default methods 必须有 `planned_phase`。
- forbidden methods 必须有 `forbidden_reason`。
- default/optional/forbidden surfaces 不允许重叠。
- business wrappers 不得出现在 default surface。
- event aliases 不得与 canonical event 冲突。
- error codes 不允许重复。
- SDK scaffold 不暴露可用 API。

Phase0 完成后只能声明：

```text
V3.5 implementation ready
```

不能声明 SDK usable、external app ready 或 V3.5 complete。
