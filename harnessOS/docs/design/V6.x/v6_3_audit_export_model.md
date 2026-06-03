# V6-3 Audit Export Model

文档状态：V6-3 implementation-ready export model。

## AuditExportPackage Required Fields

```text
export_id
tenant_id
workspace_id
requested_by
request_id
correlation_id
retention_policy_id
included_event_refs
included_evidence_refs
event_count
checksum
readonly=true
append_only=true
immutable=true
allowed_actions=view/export/open_evidence
redaction_status
```

## Required Coverage

Each included event must include:

```text
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
request_id
correlation_id
operation
target_refs
source_refs
policy_decision
redaction_status
```

## Denial Matrix

| Scenario | Expected |
| --- | --- |
| source=agent export | DENY |
| missing user confirmation | DENY |
| wrong tenant event | DENY |
| export policy denies export | DENY |
| non-redacted event | DENY |
| valid confirmed export | ALLOW |

## No False Green

AuditExportPackage 只证明 V6-3 pilot export model，不证明 production audit export ready。
