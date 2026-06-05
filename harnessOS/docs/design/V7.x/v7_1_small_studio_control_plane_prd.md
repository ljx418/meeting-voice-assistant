# V7-1 Small Studio Control Plane PRD

文档状态：V7 planning package / V7-1 detailed PRD。

## Goal

V7-1 将 V6 的 production pilot control capabilities 收敛成一个小型工作室控制面。

小型工作室定义：

```text
single organization / studio
multiple workspaces
multiple projects
multiple apps
admin / operator / reviewer roles
provider profile management
credential reference management
quota / rate limit visibility
audit evidence visibility
```

## User Experience

```text
Studio Admin 打开 Product Console 或 CLI
 -> 查看 studio / workspace / project / app
 -> 配置 provider profile
 -> 绑定 credential ref
 -> 分配 operator / reviewer
 -> 查看 quota 和 rate limit
 -> 查看 audit source refs
```

## Required Capabilities

```text
StudioContext
StudioInventory
WorkspaceInventory
ProjectInventory
AppInventory
StudioRoleBinding
ProviderProfileProjection
CredentialRefProjection
QuotaStatusProjection
AuditSourceRefProjection
```

## Governance Boundary

```text
Studio control plane cannot construct workflow runtime truth.
Credential refs cannot expose raw secrets.
Provider profile cannot expose API keys.
Role binding cannot bypass workflow approval.
External app access remains tenant/studio scoped.
```

## Success Criteria

```text
Studio inventory can be rendered.
Workspace/project/app refs are present in evidence.
Provider and credential refs are redacted.
Role and permission projections are auditable.
Quota/rate denials are explainable.
Cross-studio or cross-workspace access is denied.
```

## Allowed Claim

```text
V7-1 complete: small studio production pilot control plane ready for review.
```

## Forbidden Claims

```text
enterprise auth ready
multi-tenant control plane ready
production-ready external app support
full production GA
```

