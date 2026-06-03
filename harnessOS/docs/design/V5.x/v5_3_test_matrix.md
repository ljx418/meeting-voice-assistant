# V5-3 Test Matrix

文档状态：V5-3 implementation planning。

## Focused Tests

```text
tests/test_v5_3_observability_event_model.py
tests/test_v5_3_audit_retention_export.py
tests/test_v5_3_metrics_alerting.py
tests/test_v5_3_incident_timeline.py
tests/test_v5_3_redaction.py
tests/test_v5_3_no_false_green.py
```

## Required Coverage

```text
audit event has request_id / correlation_id / actor_id
audit export requires confirmation
source=agent cannot export audit package
security event log rejects raw payload
metrics do not leak sensitive fields
alerts link to redacted event refs
incident timeline is read-only
claim guard blocks production overclaims
```

