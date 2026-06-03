# V5-1 Identity / Tenant / Workspace / App Ownership Model

文档状态：V5-1 pre-implementation planning。本文定义 ownership model，不实现数据迁移。

## 1. Ownership Chain

V5-1 目标 ownership chain：

```text
tenant_id
 -> workspace_id
 -> project_id
 -> app_id
 -> workflow_template_id / workflow_draft_id / workflow_version_id / workflow_instance_id
 -> station_id / station_run_id / artifact_id / evidence_id / report_id / handoff_id
```

## 2. Actor Model

V5-1 actor types：

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
agent requires agent_id, session_id, and actor_id
system_service requires explicit internal service policy
agent identity is not executor identity
source=agent cannot bypass user confirmation or policy
```

## 3. Scope Denial Matrix

| Scenario | Expected Result |
| --- | --- |
| cross-tenant resource access | DENY |
| same-tenant wrong workspace | DENY |
| same-workspace wrong project | DENY |
| same-project wrong app | DENY |
| same-app wrong workflow resource | DENY |
| same-instance wrong agent session | DENY |
| service account outside bound scope | DENY |
| agent attempts durable mutation without user confirmation | DENY |
| valid actor within bound scope | ALLOW |

## 4. Resource Binding Requirements

Every production-accessed resource must be resolvable to:

```text
tenant_id
workspace_id
project_id
app_id
resource_type
resource_id
owner_ref
created_by
updated_by
```

## 5. No False Green

No False Green：该 ownership model 是 V5-1 设计合同，不证明 multi-tenant control plane ready 或 enterprise auth ready。
