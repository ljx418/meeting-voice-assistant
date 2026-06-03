# V5-3 Target Architecture Delta

文档状态：V5-3 core slice implemented for review。

## New Logical Components

```text
AuditRetentionStore
AuditExportService
SecurityEventLog
MetricsEmitter
AlertRuleEngine
IncidentTimelineBuilder
AuditRedactionBoundary
```

## Data Flow

```text
IdentityContext / ProviderEvidence / RuntimeEvidence
 -> AuditRedactionBoundary
 -> AuditRetentionStore
 -> SecurityEventLog
 -> MetricsEmitter
 -> AlertRuleEngine
 -> AuditExportService
 -> IncidentTimelineBuilder
```

## Runtime Truth Boundary

```text
Audit export is evidence output, not runtime truth.
Incident timeline is read model, not WorkflowInstance truth.
Metrics are observability signals, not policy decisions.
EventBridge payload still cannot construct runtime truth.
```

## Implemented Core Slice

```text
core/observability/audit_export.py
 -> SecurityEventLog
 -> AuditExportService
 -> MetricsEmitter
 -> AlertRuleEngine
 -> IncidentTimelineBuilder
```

The implementation is in-memory and dev/local focused. It validates the DTOs, confirmation gates, redaction boundary, and read-only reporting semantics. It does not create BFF routes or production audit export infrastructure.

## Dependency

V5-3 depends on V5-1 identity boundary and V5-2 provider evidence, but does not upgrade them into production auth or production credential lifecycle.
