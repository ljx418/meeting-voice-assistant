# V6-3 Production Observability And Audit Export Development And Acceptance Plan

文档状态：V6-3 implementation-ready plan。V6-3 detailed PRD、架构增量、audit export model、incident timeline model、test matrix 和 pre-implementation audit 已补齐。本文定义 V6-3 最小实现和验收门槛。

## Allowed Claim

```text
V6-3 complete: production observability and audit export pilot slice ready for review.
```

## Goal

建立生产试点级观测与审计导出：audit retention policy、audit export package、security event log、metrics、alerting、incident timeline。

## Non-Goals

```text
production audit export ready
production observability platform ready
production SIEM integration ready
```

## Development Scope

- AuditRetentionPolicy：定义 retention period、tenant scope、export scope。
- AuditExportPackage：可校验、可下载、只读、immutable 或 append-only，不构造 runtime truth。
- SecurityEventLog：记录 auth、credential、executor、external app、distributed runtime 事件。
- MetricSignal / AlertDecision：只读观测输出。
- IncidentTimeline：关联 request_id、correlation_id、actor_id、runtime_result_ref。

## Acceptance Gates

- audit export package XML/JSON valid。
- correlation_id / request_id / actor_id / tenant_id 覆盖所有 production pilot action。
- source=agent export mutation denied。
- audit export read-only；source=agent export mutation denied。
- incident timeline 可追溯 failure、retry、kill switch、rollback。
- metrics、alerting、incident timeline 均为 read model，不能构造 runtime truth。
- redaction scan PASS。

## Evidence Package

```text
docs/design/V6.x/evidence/v6-3-observability-audit/
  index.html
  acceptance-data.json
  result-summary.md
  claims-scan.md
  raw/
```

## Stop Conditions

- Audit Export 被写成 runtime mutation panel。
- Evidence Chain 或 Runtime Report 构造 runtime truth。
- audit export 缺少 tenant / actor / request refs。
- Forbidden claim scan 失败。

## Detailed Control Documents

```text
docs/design/V6.x/v6_3_observability_audit_prd.md
docs/design/V6.x/v6_3_observability_architecture_delta.md
docs/design/V6.x/v6_3_audit_export_model.md
docs/design/V6.x/v6_3_incident_timeline_model.md
docs/design/V6.x/v6_3_test_matrix.md
docs/design/V6.x/v6_3_pre_implementation_audit.md
```
