# V4.0-V Production Observability / Audit Retention Follow-up Design Plan

阶段定位：V4.0-V 只做 production observability 和 audit retention follow-up design，不实现 observability platform、metrics admin、audit export、incident timeline、SLO/SLA runtime。

允许完成声明：

```text
V4.0-V complete: production observability and audit retention follow-up design ready for review.
```

## PR Slices

1. 新增机器可读 observability gap matrix，覆盖 trace retention、operation evidence retention、governance review export、security audit log、correlation_id、idempotency_key、metrics/alerting 和 error taxonomy。
2. 明确 V4.0-M operation evidence 是 dev/local baseline，不等于 production audit retention/export ready。
3. 新增 forbidden route scan，确保没有 `/audit/export`、observability admin、incident timeline 或 SLO/SLA route。
4. 固化 EventBridge 不构造 audit/evidence truth。
5. 同步核心文档与 completion evidence。

## Test Plan

新增 `tests/test_v4_0_production_observability_audit_retention_design.py` 覆盖合同、gap matrix、evidence boundary 和 forbidden route scan。

## Risk Controls

V 阶段不新增 metrics collector、alert routing、audit export 或 observability admin surface。

## Completion Evidence Format

Completion note 必须记录 allowed claim、observability gap result、audit retention result、route scan result、validation command results 和 No False Green statement。
