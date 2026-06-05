# V6-7 Worker Assignment Policy

文档状态：V6-7 complete / ready for review policy contract。

## Required Policy

```text
worker identity must be tenant-bound
worker identity must not be reused across tenants without explicit binding
worker assignment requires tenant_id, workspace_id, worker_id, workflow_instance_id
credential decision is evaluated per worker
policy decision is evaluated per worker
source=agent cannot create worker assignment directly
```

## Denial Cases

```text
worker_wrong_tenant_denied
worker_cross_tenant_reuse_without_binding_denied
worker_missing_credential_decision_denied
worker_missing_policy_decision_denied
source_agent_worker_assignment_denied
```
