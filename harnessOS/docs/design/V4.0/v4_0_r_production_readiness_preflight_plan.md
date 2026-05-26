# V4.0-R Production Readiness Preflight Plan

文档状态：V4.0-R implemented as preflight gate. 本阶段只做 production readiness gap / audit / preflight，不实现 production-ready external app support、enterprise auth、OAuth/SSO、tenant control plane、production external app onboarding、production secret manager、production observability platform、production audit export、Agent executor 或 controlled executor。

允许完成声明：

```text
V4.0-R complete: production readiness preflight ready for review.
```

禁止完成声明：

```text
production-ready external app support
complete Workflow Studio ready
complete AgentTalkWindow ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
full low-code canvas editing ready
enterprise auth ready
multi-tenant control plane ready
```

## 1. Implementation Summary

V4.0-R 在 V4.0-Q Controlled Executor Design Gate 之上建立生产化预检门禁：

- 新增机器可读 production readiness gap register。
- 审计 auth / SSO / OAuth、tenant boundary、capability token lifecycle、secret hygiene、observability、audit retention、external app onboarding、rate limit、data governance 和 incident recovery。
- 继续验证 dev/local scope guard、same-scope wrong-resource guard 和 redaction guard。
- 扫描 BFF / frontend source，确认未新增 OAuth、SSO、tenant admin、production onboarding、token rotate/revoke、quota 或 audit export route。
- 扩展 claim guard，防止把 R 阶段误写成 production-ready。

## 2. PR Slices

### R-PR1 Production Readiness Gap Register

新增 `v4_0_r_production_readiness_preflight_contract.json`。该文件只作为审计输入，不作为运行时配置读取。

每个 gap 必须包含：

```text
gap_id
category
current_state
required_production_state
risk_level
blocking_for_production
evidence_source
owner_area
recommended_next_phase
status
```

必须覆盖：

```text
auth_sso_oauth
multi_tenant_isolation
capability_token_lifecycle
secret_management
audit_retention
observability_metrics_alerting
rate_limit_abuse_control
data_residency_export_deletion
external_app_onboarding
incident_recovery
```

### R-PR2 Auth And Tenant Boundary Preflight

不实现 production auth、OAuth、SSO 或 tenant admin route。合同列出 `tenant_id/app_id/project_id/workspace_id/user_id/actor_type/actor_id/service_account_id/agent_id/session_id`，并明确当前只能声明 dev/local scope guard exists。

### R-PR3 Capability Token Lifecycle Preflight

单独列出 issuance、expiration、rotation、revocation、origin binding、audience binding、scope binding、capability downgrade、emergency revoke 和 token audit gap。不实现 token rotation / revoke route。

### R-PR4 Secret And Token Hygiene Preflight

继续检查 `capability_token`、`subscription_token`、`Authorization`、`Bearer`、`secret`、`raw_trace_payload`、`raw_artifact_content`、`raw_connector_payload`、`raw prompt` 和 `upstream signed URL` 不进入 BFF DTO、error response、event payload、frontend DOM / HTML 或 audit summary。

### R-PR5 Observability And Audit Preflight

只登记 trace retention、operation evidence retention、governance review export、security audit log、correlation_id、idempotency_key、actor_id、request_id、error taxonomy、metrics、alerting、incident timeline 和 SLO/SLA gap。V4.0-M operation evidence 仍是 dev/local baseline，不等于 production audit retention/export ready。

### R-PR6 External App Production Boundary

明确 V3.5 SDK / BFF / Embed 仍是 dev/local baseline。生产缺口包括 app registration、domain verification、origin allowlist review、tenant provisioning、service account lifecycle、token rotation / revocation、SDK versioning policy、API compatibility policy、quota / rate limit、abuse detection、customer offboarding、data export / deletion 和 support runbook。

### R-PR7 Forbidden Route And Implementation Scan

R 阶段不得新增：

```text
/oauth/*
/sso/*
/tenant/*
/admin/tenant/*
/production/onboarding
/token/rotate
/token/revoke
/quota/*
/audit/export
```

### R-PR8 Claim Guard Extension

扫描 docs/source/UI copy/completion note，阻止 production-ready、enterprise auth、multi-tenant ready、executor ready、complete Studio / AgentTalkWindow 等过度声明。

## 3. Test Plan

新增：

```text
tests/test_v4_0_production_readiness_preflight.py
tests/test_v4_0_production_auth_gap.py
tests/test_v4_0_production_secret_hygiene.py
tests/test_v4_0_production_observability_gap.py
tests/test_v4_0_production_external_app_boundary.py
tests/test_v4_0_production_claim_guard.py
apps/workflow-console/src/__tests__/productionReadinessPreflight.test.tsx
apps/workflow-console/src/__tests__/productionNoFalseGreen.test.tsx
```

Browser smoke 不新增生产化场景；现有 e2e 只作为回归。

## 4. Risk Controls

- R 只新增 gap/audit/preflight 合同、文档和门禁测试。
- 不新增 production auth、OAuth/SSO、tenant admin、token rotation/revocation、quota、audit export 或 onboarding route。
- 不改变现有 scope guard、capability guard、redaction guard、EventBridge refresh-only truth 边界。
- 不把 V4.0-M operation evidence 误写成 production audit export/retention ready。
- 不把 V3.5 SDK/BFF/Embed 误写成 production external app support。
- 不新增 controlled executor 或 Agent executor。

## 5. Completion Evidence Format

Completion note 必须记录：

```text
allowed claim
forbidden claims
actual files changed
tests added
docs updated
production gap categories
auth / tenant boundary result
token lifecycle gap result
secret hygiene result
observability gap result
external app boundary result
forbidden route scan result
claim guard result
validation command results
No False Green statement
```
