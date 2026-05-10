# V3.5 Contract Inventory

文档状态：V3.5-0 planning artifact。

## 1. Purpose

本文件定义 V3.5 Application Adaptation Layer 的 contract inventory：哪些 RPC / events / errors 可进入 SDK 默认面，哪些只能作为 optional 或 legacy/debug，哪些缺口必须在 V3.5-A/C 中补齐。

## 2. Future Directory Plan

后续代码实施时新增：

```text
sdk/
  python/
    harnessos_client/
  typescript/
templates/
  bff/
    fastapi/
    node/        # optional
  pack/
  connector/
examples/
  reference_app/
docs/
  integration/
```

本轮文档工作不创建这些代码目录。

## 3. SDK Default Method Surface

默认 SDK 面只暴露平台中立方法：

| Method | 用途 | V3.5 状态 |
| --- | --- | --- |
| `session.start` | 创建 scoped session。 | baseline |
| `turn.start` | 发起一轮 turn。 | baseline |
| `events.subscribe` | 浏览器/SDK 事件订阅。 | V3.5-A/C 新增 |
| `artifact.list` | 查询 scoped artifacts。 | baseline |
| `artifact.read_metadata` | 读取 artifact metadata。 | baseline |
| `artifact.register_external` | 注册 external-only artifact。 | baseline |
| `artifact.lineage` | 查询 lineage。 | baseline |
| `job.get` | 查询 job。 | baseline |
| `job.list` | 查询 scoped jobs。 | baseline |
| `approval.respond` | 统一审批响应。 | V3.5-A 新增 |
| `connector.health` | 查询 connector health。 | baseline |
| `pack.list` | 查询 packs。 | baseline |
| `pack.get` | 查询 pack assembly。 | baseline |
| `trace.list` | 查询 trace list。 | baseline optional |
| `trace.get` | 查询 trace detail。 | baseline optional |

## 4. SDK Optional Method Surface

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

## 5. Legacy / Debug Forbidden By Default

以下不得进入 SDK/BFF 默认面：

- `meeting.capabilities`
- `meeting.analyze_text`
- `meeting.process_recording`
- `meeting.process_audio_dir`
- `pack.execute_stub`
- `workflow.execute_stub`
- low-level debug or test-only methods
- business-specific facade methods unless explicitly placed under legacy namespace

原则：业务 legacy/reference paths 不能成为 SDK 默认业务模板。

## 6. Event Inventory

V3.5 Event Bridge 至少覆盖：

- chat events：`turn.started`、`item.delta`、`turn.completed`、`turn.failed`
- job events：`job.queued`、`job.running`、`job.completed`、`job.failed`、`job.cancelled`
- artifact events：`artifact.registered`、`artifact.updated`、`artifact.read_blocked`
- approval events：`approval.required`、`approval.approved`、`approval.rejected`
- trace events：`trace.recorded`
- business events：保留 `business.*` namespace，仅由 pack/template 显式声明

## 7. Error Inventory

V3.5 error registry 至少包含：

- `INVALID_PARAMS`
- `METHOD_NOT_FOUND`
- `SESSION_NOT_FOUND`
- `ARTIFACT_READ_BLOCKED`
- `AUTH_REQUIRED`
- `AUTH_INVALID`
- `AUTH_FORBIDDEN`
- `CAPABILITY_DENIED`
- `SCOPE_MISMATCH`
- `EVENT_CURSOR_INVALID`
- `RUNTIME_ERROR`

## 8. V3.5-0 Acceptance

- SDK default surface、optional surface、forbidden surface 已区分。
- event inventory、error inventory 已列出。
- 后续 V3.5-A/C 能直接按本文件补 schema 和 event bridge。
