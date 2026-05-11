# V3.5 App Gateway / BFF Template Plan

文档状态：V3.5-D2 implementation baseline with MVP E2E smoke / V3.5-F planning artifact。

## 1. Goal

提供可复用 BFF template，使外部业务 App 不直接处理 harnessOS 内部细节，同时不绕过 Core/Gateway/Governance。

BFF template 不实现完整用户系统。它只提供一个绑定样例：把业务系统已经认证过的 identity 映射为 harnessOS `scope` 和 local capability token。

边界：

- 业务登录、账号体系、组织成员管理由外部业务 App 自己负责。
- BFF template 只接收业务 identity / tenant / workspace context，并生成受限 harnessOS scope。
- BFF template 不能扩大用户在 harnessOS 中的 capability。
- BFF template 不能代理 legacy/debug/admin bypass method。

V3.5-D2 已交付 Minimal BFF Smoke，用于证明 Python SDK proxy、EventSource proxy 和 denylist 可行；MVP E2E 已用真实 Minimal BFF + 真实 Python SDK + harnessOS ASGI/TestClient transport 验证端到端 smoke。V3.5-F 才交付 Full BFF Template。

## 2. Target Directories

```text
templates/bff/
  fastapi/
  node/        # optional
```

## 3. FastAPI Template

V3.5-D2 Minimal BFF Smoke 实现目录：

```text
templates/bff/fastapi_minimal/
```

V3.5-F Full BFF Template 目标目录：

```text
templates/bff/fastapi/
```

内置：

- scope binding
- demo identity / same-origin sample boundary
- server-side configured harnessOS capability token
- RPC proxy
- EventSource proxy
- native EventSource BFF endpoint
- approval respond
- forbidden legacy/debug method denylist

平台中立要求：

- `config.example.json` 默认使用 `reference_app/demo/local`。
- 不硬编码 `meeting` 或 `knowledge`。
- Browser 不持有长期 harnessOS capability token。
- BFF -> harnessOS 通过 Python SDK 和 server-side configured token。
- D2 不实现 token issuance。

## 4. Proxy Rules

Allowed by default：

- SDK default methods
- event subscription
- artifact metadata and lineage
- job list/get
- approval respond

Denied by default：

- `meeting.*`
- `knowledge.*`
- `approval.approve`
- `approval.reject`
- `pack.execute_stub`
- `workflow.execute_stub`
- `method.list(include_forbidden=true)`
- `scope_mode=all`
- admin scope bypass
- debug-only methods

## 5. Acceptance

- request scope from token and route context must match.
- BFF cannot request capabilities not present in token.
- BFF cannot proxy forbidden methods.
- BFF preserves event id/cursor in EventSource proxy.
- native EventSource browser auth works without Authorization header.
- forbidden methods return stable forbidden error.
- BFF runtime does not import GatewayService, RuntimeAdapter, Core Store, or `apps.gateway.service`.
- BFF does not default to `/v1/runs/stream`.
- capability token and subscription token are redacted from error responses.
- upstream auth failure does not open a stream.
- malformed upstream SSE behavior is stable and redacted.
- MVP E2E covers session/turn/events/approval/artifact/job/pack/connector smoke without Meeting/Knowledge or external MCP.
