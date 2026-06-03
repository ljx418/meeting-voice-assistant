# V5-3 Observability / Audit Export PRD

文档状态：V5-3 core slice implemented for review。本文定义生产观测与审计导出的目标规格，并记录当前只完成 dev/local core slice。

## Stage Goal

V5-3 目标是把 V4/V5-2 的 dev/local evidence 与核心事件，规划为 production observability / audit export baseline。

必须覆盖：

```text
audit retention
audit export
security event log
metrics
alerting
incident timeline
correlation_id / request_id / actor_id coverage
```

## Target Experience

```text
管理员打开 Audit Console
 -> 选择 tenant / workspace / workflow / time range
 -> 查看 security event / operation evidence / provider invocation evidence
 -> 导出审计包
 -> 查看 incident timeline
 -> 检查 metrics / alerting 状态
```

## Acceptance Criteria

```text
audit event has tenant_id / workspace_id / actor_id / request_id / correlation_id
audit export package is generated with redacted evidence
security event log distinguishes auth / credential / workflow / provider events
metrics have owner stage and source refs
alerting rules are explicit and testable
incident timeline links events by correlation_id
raw prompt / raw artifact / token / secret are not exported
```

## No False Green

No False Green：V5-3 不证明：

```text
production-ready external app support
enterprise auth ready
Agent executor ready
controlled executor ready
complete Workflow Studio ready
distributed multi-Agent runtime ready
```

V4 Evidence Chain、V5-1 audit event 和 V5-2 provider evidence 不能被直接写成 production audit export ready。

## Current Implementation Scope

```text
Implemented:
- redacted SecurityEventLog
- AuditRetentionPolicy DTO
- user-confirmed AuditExportService
- source=agent audit export denial
- read-only MetricRecord / AlertEvent
- read-only IncidentTimelineEntry

Not implemented:
- production audit export route
- production retention job
- SIEM integration
- production observability platform
- Agent executor authority
```
