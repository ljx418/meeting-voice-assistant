# Historical V5-7 Tenant / Policy / Credential Boundary

文档状态：historical / superseded。Distributed multi-Agent runtime 已移动到 V5-8；本文不再是当前控制计划。

## Required Boundary

```text
tenant_id bound to workflow instance
workspace_id bound to run
agent worker scoped to tenant/workspace/app
provider call uses V5-2 credential reference
policy decision recorded per station attempt
source=agent remains subject to policy
```

## Denied Behavior

```text
cross-tenant worker claim
unscoped provider call
raw credential access
unconfirmed high-risk mutation
event payload constructing runtime truth
```
