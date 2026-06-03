# V5-3 Incident Timeline Model

文档状态：V5-3 implementation planning。

## Timeline Entry

```text
timeline_entry_id
incident_id
event_ref
evidence_ref
tenant_id
workspace_id
operation
severity
created_at
correlation_id
redaction_status
```

## Timeline Sources

```text
security event log
credential lifecycle event
provider invocation evidence
workflow runtime evidence
audit export event
alert event
```

## Acceptance Rules

```text
timeline is read-only
timeline links evidence by correlation_id
timeline does not expose raw prompt / raw content / token
timeline cannot approve, apply, run, rerun, or publish
```

