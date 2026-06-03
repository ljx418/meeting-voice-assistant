# V5-3 API / BFF Route Design

文档状态：V5-3 implementation planning。本文只定义 route design，不新增实际路由。

## Proposed Routes

```text
GET  /bff/v5/audit/events
GET  /bff/v5/audit/events/{event_id}
POST /bff/v5/audit/exports
GET  /bff/v5/audit/exports/{export_id}
GET  /bff/v5/metrics/summary
GET  /bff/v5/alerts
GET  /bff/v5/incidents/{incident_id}/timeline
```

## Required Guards

```text
server-bound IdentityContext required
tenant/workspace/app scope guard required
source=agent denied for audit export
audit export requires user_confirmed=true or admin-confirmed policy
all responses redacted
```

## Stable Error Codes

```text
AUDIT_SCOPE_DENIED
AUDIT_EXPORT_CONFIRMATION_REQUIRED
AUDIT_EXPORT_AGENT_DENIED
AUDIT_EXPORT_REDACTION_FAILED
METRICS_SCOPE_DENIED
INCIDENT_TIMELINE_NOT_FOUND
```

