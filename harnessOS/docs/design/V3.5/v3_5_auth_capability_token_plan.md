# V3.5 Auth / Capability Token MVP Plan

文档状态：V3.5-B implementation baseline。

## 1. Goal

实现 local capability token，支撑 dev/local-first 的外部 App 接入。正式外部 App 接入前，所有 SDK/BFF/EventSource 请求都必须被 token、scope 和 capability 约束。

V3.5-B 完成后只能声明 `local capability token and external auth contract ready`，不能声明 SDK 可用、外部 App ready、V3.5-MVP complete 或 production-ready auth。

## 2. Token Envelope

Token payload 至少包含：

- `token_id`
- `issued_at`
- `expires_at`
- `app_id`
- `project_id`
- `workspace_id`
- `capabilities`
- `allowed_origins`
- `embed_policy`
- `audience`
- `issuer`

签名方式当前采用 local secret HMAC SHA-256；后续可扩展为 asymmetric key。

Token 签发只允许 CLI/local admin/internal test helper。V3.5-B 不开放匿名 HTTP token issuance，签发 helper 不是 public external API。

缺 secret 行为：

- verify token 时返回 `AUTH_INVALID`，`reason=auth_not_configured`。
- issue token 时返回 `AUTH_INVALID`，`reason=auth_not_configured`。

## 3. Capability Model

capability 应与 method registry 对齐：

- `sessions`
- `turns`
- `events`
- `artifacts`
- `jobs`
- `approvals`
- `connectors.read`
- `packs.read`
- `traces.read`

method -> capability 映射必须来自 method inventory / method schema registry / router metadata，不允许在 auth guard 中散落手写业务映射。关键映射：

- `approval.respond` -> `approvals`
- `connector.health` -> `connectors.read`
- `pack.list` / `pack.get` -> `packs.read`

默认不授予：

- connector execution
- policy evaluation
- legacy/debug methods
- admin `scope_mode=all`

## 4. AppProfile Extensions

AppProfile 增加：

- `allowed_origins`
- `default_capabilities`
- `embed_policy`

AppProfile 是权限上界：

- `token.allowed_origins` 必须是 `AppProfile.allowed_origins` 的子集。
- 有效 origin 集合是 token 与 AppProfile 的交集。
- `token.capabilities` 必须是 AppProfile default capabilities 的子集。
- token 不得扩大 AppProfile 权限。

`embed_policy` 建议字段：

- `allow_iframe`
- `allowed_parent_origins`
- `event_channels`
- `artifact_preview`
- `approval_interaction`

## 5. Dev Mode Rule

- 无 token 外部接入只允许在显式 dev mode 下启用。
- dev mode 必须由环境变量或 config 显式声明。
- dev mode response 必须包含 warning metadata，便于测试发现。
- dev mode 无 token 只允许 localhost / 127.0.0.1 origin；非本地 origin 返回 `AUTH_FORBIDDEN`。

## 6. CORS / Scope / Token Linkage

外部入口必须保护：

- `/v1/rpc`
- `/v1/runs`
- `/v1/runs/stream`
- `/v1/sessions*`
- `/api/agents`
- `/api/routing`

请求必须同时满足：

- Origin 在 token 与 AppProfile 的交集内。
- Request scope 与 token scope 一致。
- Method capability 被 token 授权。
- BFF proxy 不得提升 capability。
- `scope_mode=all` 在 external auth guard 直接拒绝。
- `method.list(include_forbidden=true)` 需要 admin/debug/internal capability。
- `/v1/runs/stream` 必须在打开 stream 前完成 token/scope/capability 校验。

Authorization header 和 token 字符串不得进入 trace、error data、job failure_context、approval 或 artifact metadata。

## 7. Contract Tests

- missing token -> `AUTH_REQUIRED`
- invalid signature -> `AUTH_INVALID`
- expired token -> `AUTH_INVALID`
- origin mismatch -> `AUTH_FORBIDDEN`
- scope mismatch -> `SCOPE_MISMATCH`
- missing capability -> `CAPABILITY_DENIED`
- explicit dev mode allows local-only request and emits warning
- token cannot broaden AppProfile origins/capabilities
- method capability mapping tests
- include_forbidden auth tests
- legacy/debug route auth tests
- nested scope conflict tests
- token redaction tests
- dev mode non-local origin rejection
- `/v1/runs/stream` pre-auth rejection
