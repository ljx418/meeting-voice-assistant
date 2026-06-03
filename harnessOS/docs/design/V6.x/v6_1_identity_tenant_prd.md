# V6-1 Identity / Tenant Control Plane PRD

文档状态：V6-1 implementation-ready PRD。本文定义 V6-1 生产试点身份与租户边界规格。

## Current Baseline

```text
V6-0 complete: production pilot planning gate ready for review.
V6-0 external audit P0 closure complete.
V6-1 implementation may start only after this PRD, architecture delta, ownership model, route design, audit fields, test matrix, and pre-implementation audit pass.
```

## Goal

V6-1 的目标是把 V5-1 core tenant boundary slice 升级为生产试点级 identity / tenant control plane slice：

```text
server-bound identity context
tenant / workspace / project / app ownership chain
human actor and service account actor binding
source=agent identity boundary denial
staging IdP / OIDC status evidence
cross-head audit identity projection
service account scope audit
redacted audit evidence
```

## User Experience

```text
用户或服务账号进入 Mission Console / Product Console / BFF
 -> 服务端解析 tenant / workspace / project / app / actor context
 -> 访问 WorkflowSpec / Runtime Report / Review Console / Evidence Chain
 -> 资源越界时被拒绝并产出审计证据
 -> 合法访问时产出 redacted identity audit refs
```

## Required Fields

```text
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
user_id
service_account_id
agent_id
session_id
request_id
correlation_id
identity_provider
identity_provider_status
identity_provider_evidence_scope
```

## Non-Goals

```text
enterprise auth ready
multi-tenant control plane ready
production tenant isolation ready
production-ready external app support
Agent executor ready
controlled executor ready
complete Workflow Studio ready
```

## Acceptance

V6-1 PASS 需要：

```text
cross-tenant denied
wrong workspace denied
wrong project denied
wrong app denied
service account missing binding denied
service account operation outside allowed scope denied
source=agent durable mutation denied
valid scoped access allowed
all workflow heads receive identity source refs
staging IdP / OIDC status is recorded as staging_only if no real provider is connected
audit evidence contains tenant/workspace/project/app/user/service_account refs
no raw token / secret / raw payload leakage
No False Green scan PASS
```

## Allowed Claim

```text
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
```

## No False Green

V6-1 不证明 enterprise auth ready、多租户控制面完成、生产级租户隔离完成、Agent executor ready、production controlled executor ready、production-ready external app support 或 complete Workflow Studio ready。
