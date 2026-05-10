# V3.5 Auth / Capability Token MVP Plan

文档状态：V3.5-B planning artifact。

## 1. Goal

实现 local capability token，支撑 dev/local-first 的外部 App 接入。正式外部 App 接入前，所有 SDK/BFF/EventSource 请求都必须被 token、scope 和 capability 约束。

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

签名方式可先采用 local secret HMAC；后续可扩展为 asymmetric key。

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

## 6. CORS / Scope / Token Linkage

请求必须同时满足：

- Origin 在 AppProfile 或 token `allowed_origins` 中。
- Request scope 与 token scope 一致。
- Method capability 被 token 授权。
- BFF proxy 不得提升 capability。

## 7. Contract Tests

- missing token -> `AUTH_REQUIRED`
- invalid signature -> `AUTH_INVALID`
- expired token -> `AUTH_INVALID`
- origin mismatch -> `AUTH_FORBIDDEN`
- scope mismatch -> `SCOPE_MISMATCH`
- missing capability -> `CAPABILITY_DENIED`
- explicit dev mode allows local-only request and emits warning

