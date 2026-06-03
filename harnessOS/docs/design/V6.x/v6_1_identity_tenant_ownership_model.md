# V6-1 Identity / Tenant Ownership Model

文档状态：V6-1 implementation-ready ownership model。

## Ownership Chain

```text
tenant_id
 -> workspace_id
 -> project_id
 -> app_id
 -> workflow_spec_id / workflow_instance_id / report_id / evidence_id / handoff_id
 -> station_id / station_run_id / artifact_id / quality_evaluation_id
```

## Actor Types

```text
human_user
service_account
agent
system_service
```

Rules:

```text
human_user requires user_id and actor_id
service_account requires service_account_id and actor_id
service_account requires tenant/workspace/project/app binding
service_account requires allowed_operations
agent requires agent_id, session_id, and actor_id
source=agent cannot execute durable mutation
system_service requires explicit internal policy
```

## Service Account Scope

Service account scope must record:

```text
service_account_id
tenant_id
workspace_id
project_id
app_id
allowed_operations
policy_decision
denial_reason
audit_ref
```

## Denial Matrix

| Scenario | Expected |
| --- | --- |
| cross tenant | DENY |
| wrong workspace | DENY |
| wrong project | DENY |
| wrong app | DENY |
| service account missing binding | DENY |
| service account wrong operation | DENY |
| source=agent durable mutation | DENY |
| valid scoped human read | ALLOW |
| valid scoped service account read | ALLOW |

## No False Green

该 ownership model 只证明 V6-1 生产试点级边界合同，不证明完整多租户控制面。
