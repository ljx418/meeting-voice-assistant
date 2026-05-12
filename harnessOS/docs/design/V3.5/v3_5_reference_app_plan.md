# V3.5 Reference App Example

文档状态：V3.5-I Reference App complete；V3.5 complete at dev/local Application Adaptation Layer level。

## 1. Goal

V3.5-I 新增平台中立 reference app example，用来证明业务 App 可以通过 SDK + BFF + hooks 接入 harnessOS Core，而不修改 Core/Gateway 业务逻辑。

Reference app 不依赖业务 reference pack 或 legacy RPC。它使用实例化 dummy pack / dummy connector、BFF template、TypeScript SDK hooks 和 Python SDK-backed BFF routes，证明 V3.5 Application Adaptation Layer 本身可用。

## 2. Implemented Directory

```text
examples/reference_app/
  README.md
  bff/
    config.example.json
  frontend/
    package.json
    src/
  pack/
    manifest.json
  connector/
    descriptor.json
  tests/
```

## 3. Implemented Flow

- Reference frontend 默认只调用 `/bff/*`。
- Event subscription 只走 `GET /bff/events/subscribe`，不通过 `/bff/rpc` 调 `events.subscribe`。
- `GET /bff/embed/bootstrap` 返回 BFF-local `eventsourceUrl`，不泄露 upstream `subscription_token`。
- `EmbedDefinition` 不包含 capability token、session id 或 eventsource URL。
- `EmbedBootstrap` 可携带 session/thread/event subscription runtime payload，但不返回 upstream token。
- Frontend 展示 session、turn、events、artifacts、jobs、approvals、pack/connector、embed bootstrap 和 redacted trace summary。
- Approval 只通过 `/bff/approvals/{approval_id}/respond` 调 `approval.respond`。
- Pack 与 connector 分别位于 `examples/reference_app/pack` 和 `examples/reference_app/connector`，通过 external path / descriptor path 注入。

## 4. Safety Boundaries

- Frontend 默认不直接调用 harnessOS `/v1/rpc` 或 `/v1/events/subscribe`。
- Browser 不持有长期 harnessOS capability token。
- `/bff/rpc` 默认拒绝 `events.subscribe`，避免 upstream subscription token 暴露给浏览器。
- `allowedActions` 不包含 `approval.approve`、`approval.reject`、business facade、debug/admin methods 或 `scope_mode=all`。
- `trace` channel 默认关闭；reference app 只展示 redacted trace summary。trace detail 仍要求 `traces.read/debug` capability。
- Fixture 不包含真实 token、真实 signed URL、真实外部服务路径或业务 reference dependency。

## 5. Tests

新增 `tests/test_v3_5_reference_app.py`，覆盖：

- reference app fixture platform-neutral。
- frontend source BFF-only，不含 direct Core/harnessOS calls。
- `/bff/rpc` denylist，包括拒绝 `events.subscribe`。
- BFF session/turn/embed/events/approval/artifact/job/pack/connector smoke。
- embed bootstrap token redaction 与 BFF-local event URL。
- pack/connector external discovery。
- Core/Gateway 无 hardcoded reference app id。
- approval.respond flow。
- scope isolation。
- redacted trace summary。

## 6. Exit Statement

V3.5-I 完成后，若 V3.5-0 到 H 回归保持绿灯，可以声明：

```text
V3.5 complete at dev/local Application Adaptation Layer level.
```

仍不能声明：

- production-ready external app support
- complete AgentTalkWindow
- complete Workflow Studio
- enterprise auth/OAuth/SSO ready
- multi-tenant production control plane ready
