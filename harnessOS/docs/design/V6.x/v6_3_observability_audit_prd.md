# V6-3 Observability / Audit Export PRD

文档状态：V6-3 implementation-ready PRD。

## Current Baseline

```text
V6-1 complete: production identity and tenant boundary pilot slice ready for review.
V6-2 complete: production credential and provider lifecycle pilot slice ready for review.
V6-3 implementation may start only after this PRD, architecture delta, export model, incident model, test matrix, and pre-implementation audit pass.
```

## Goal

V6-3 的目标是建立生产试点级观测与审计导出切片：

```text
SecurityEventLog
AuditRetentionPolicy
AuditExportPackage
MetricSignal
AlertDecision
IncidentTimeline
read-only / append-only audit evidence
correlation_id / request_id / actor_id / tenant_id coverage
```

## User Experience

```text
用户在 Product Console 打开 Audit Export
 -> 系统展示 V6-1 identity event 与 V6-2 provider event
 -> 用户确认后生成只读导出包
 -> 可查看 metric / alert / incident timeline
 -> 所有输出只读，不构造 runtime truth
```

## Non-Goals

```text
production audit export ready
production observability platform ready
production SIEM integration ready
runtime mutation panel
Evidence Chain execution panel
```

## Acceptance

```text
audit export package is JSON valid
audit export package is read-only
audit export package is append-only / immutable
source=agent export mutation denied
user_confirmed required for export
all events include tenant_id, workspace_id, project_id, app_id, actor_id, request_id, correlation_id
metrics are read-only
alerts are read-only
incident timeline is read-only
incident timeline links failure / retry / kill switch / rollback style events
no raw secret / raw prompt / raw payload leakage
No False Green scan PASS
```

## Allowed Claim

```text
V6-3 complete: production observability and audit export pilot slice ready for review.
```

## No False Green

V6-3 不证明 production audit export ready、production observability platform ready、production SIEM integration ready 或 runtime truth construction capability。
