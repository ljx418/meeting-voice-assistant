# V5-3 Metrics / Alerting Model

文档状态：V5-3 implementation planning。

## Metric Groups

```text
request_count
error_count
latency_ms
policy_denial_count
credential_lifecycle_count
provider_invocation_count
audit_export_count
redaction_failure_count
```

## Alert Rules

```text
redaction_failure
audit_export_failure
credential_revoke_failure
provider_error_rate_high
policy_denial_spike
incident_timeline_gap
```

## Acceptance Rules

```text
metrics carry tenant/workspace labels without secrets
alerts link to redacted event refs
alerts do not create runtime truth
alert notification content is redacted
```

