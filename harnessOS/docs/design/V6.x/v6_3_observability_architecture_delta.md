# V6-3 Observability / Audit Architecture Delta

文档状态：V6-3 implementation-ready architecture delta。

## Delta Summary

V6-3 在 V5-3 observability primitives 上增加 V6 production pilot package 语义：

```text
V5-3 SecurityEventLog / AuditExportService
 -> V6-3 ProductionAuditExportPackage
 -> V6-3 append-only export manifest
 -> V6-3 read-only metrics / alerts / incident timeline
 -> V6-3 evidence package
```

## Components

```text
ProductionSecurityEventLog
ProductionAuditExportPackage
AppendOnlyAuditManifest
ProductionMetricSignal
ProductionAlertDecision
ProductionIncidentTimeline
AuditRedactionGuard
```

## Data Flow

```text
V6-1 identity audit evidence
V6-2 provider lifecycle evidence
 -> SecurityEventLog records redacted events
 -> AuditRetentionPolicy validates scope and export allowance
 -> user_confirmed export request
 -> read-only AuditExportPackage with checksum
 -> metrics / alerts / incident timeline read models
```

## Runtime Truth Boundary

Audit export, metrics, alerts, and incident timeline are read models. They cannot write WorkflowDraft, WorkflowVersion, WorkflowInstance, StationRun, CredentialReference, CredentialLease, or Evidence Chain runtime truth.
