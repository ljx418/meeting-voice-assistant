# V3.5 App Gateway / BFF Template Plan

文档状态：V3.5-F planning artifact。

## 1. Goal

提供可复用 BFF template，使外部业务 App 不直接处理 harnessOS 内部细节，同时不绕过 Core/Gateway/Governance。

BFF template 不实现完整用户系统。它只提供一个绑定样例：把业务系统已经认证过的 identity 映射为 harnessOS `scope` 和 local capability token。

边界：

- 业务登录、账号体系、组织成员管理由外部业务 App 自己负责。
- BFF template 只接收业务 identity / tenant / workspace context，并生成受限 harnessOS scope。
- BFF template 不能扩大用户在 harnessOS 中的 capability。
- BFF template 不能代理 legacy/debug/admin bypass method。

## 2. Target Directories

```text
templates/bff/
  fastapi/
  node/        # optional
```

## 3. FastAPI Template

内置：

- scope binding
- local capability token validation
- CORS
- RPC proxy
- EventSource proxy
- native EventSource cookie / signed URL auth sample
- fetch stream bearer auth sample
- approval respond
- forbidden legacy/debug method denylist

## 4. Proxy Rules

Allowed by default：

- SDK default methods
- event subscription
- artifact metadata and lineage
- job list/get
- approval respond

Denied by default：

- `meeting.*`
- `pack.execute_stub`
- `workflow.execute_stub`
- admin scope bypass
- debug-only methods

## 5. Acceptance

- request scope from token and route context must match.
- BFF cannot request capabilities not present in token.
- BFF cannot proxy forbidden methods.
- BFF preserves event id/cursor in EventSource proxy.
- native EventSource browser auth works without Authorization header.
- forbidden methods return stable forbidden error.
