# V5-3 Audit Retention / Export Model

文档状态：V5-3 implementation planning。

## Retention Model

```text
retention_policy_id
tenant_id
workspace_id
evidence_type
retention_days
legal_hold
export_allowed
redaction_required
owner_stage
```

## Export Package

```text
export_id
tenant_id
workspace_id
time_range
requested_by
request_id
correlation_id
included_event_refs
included_evidence_refs
redaction_status
checksum
created_at
```

## Acceptance Rules

```text
export requires user_confirmed=true or admin-confirmed policy
source=agent cannot request export
export package cannot include raw prompt / raw artifact / secret
export links back to evidence refs
export does not mutate WorkflowDraft / WorkflowVersion / WorkflowInstance
```

