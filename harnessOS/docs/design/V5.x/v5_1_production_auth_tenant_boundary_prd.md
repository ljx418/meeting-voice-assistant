# V5-1 Production Auth / Tenant Boundary PRD

文档状态：V5-1 pre-implementation planning。本文定义 production auth / tenant boundary 的目标规格，不实现 runtime。

## 1. Current Baseline

```text
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
V4 feature development closed.
V5-0 complete: production productization planning gate ready for review.
```

V5-1 只能在本 PRD、架构增量、ownership model、API/BFF route design、audit fields、test matrix 和 No False Green guard 通过审计后进入实现。

## 2. Product Goal

V5-1 的目标是为 production productization 建立最小可验收的认证与租户边界：

```text
tenant identity
workspace / project / app ownership
human actor and service account identity
scope guard
tenant-bound audit references
cross-scope denial
```

## 3. User Experience

目标体验：

```text
生产用户完成认证
 -> 选择 tenant / workspace / project / app
 -> 创建或查看 workflow
 -> 所有 BFF/API 操作带 server-bound identity context
 -> 越权访问被拒绝
 -> Evidence Chain / Audit Export 记录 actor 与 scope refs
```

## 4. Required Identity Fields

V5-1 必须定义并验证：

```text
tenant_id
workspace_id
project_id
app_id
user_id
actor_type
actor_id
service_account_id
agent_id
session_id
request_id
correlation_id
```

## 5. Core Acceptance Scenarios

```text
cross-tenant denied
same-tenant wrong workspace denied
same-workspace wrong project denied
same-project wrong app denied
same-app wrong workflow resource denied
same-instance wrong agent session denied
service account scoped access allowed only within bound scope
agent identity is not executor identity
audit record contains tenant/workspace/project/app/actor refs
```

## 6. Non-Goals And No False Green

No False Green：V5-1 不得声明：

```text
enterprise auth ready
multi-tenant control plane ready
production-ready external app support
Agent executor ready
controlled executor ready
production controlled executor ready
complete Workflow Studio ready
distributed multi-Agent runtime ready
```

V5-1 不实现 OAuth / SSO / tenant admin console 的完整生产产品化，除非后续拆分阶段单独验收。

## 7. Success Criteria Before Implementation

V5-1 实现前必须满足：

```text
V5-1 PRD reviewed
V5-1 target architecture delta reviewed
identity / tenant / workspace / app ownership model reviewed
API / BFF route design reviewed
audit fields reviewed
test matrix reviewed
No False Green guard reviewed
V4 closure boundary preserved
V5-1 does not claim enterprise auth ready
```
