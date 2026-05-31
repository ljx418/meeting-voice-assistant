# V1.8-D Agent Studio Validation Plan Audit

日期：2026-05-30

## 审计结论

`CONDITIONAL GO`

V1.8-D 可以进入实质开发，但只能验证 Agent-led Studio 四类轻量输出与导出合同，不得把自动 schema 检查写成人工内容质量通过。

## 前置验收

| 前置项 | 状态 | 说明 |
| --- | --- | --- |
| V1.8-B Agent Source Import | PASS_LIMITED | 真实 data_service 导入链路通过 |
| V1.8-C Agent Guide / QA / Citation | PASS_LIMITED | Guide / QA / citation 解析通过 |
| V1.5-C Studio 后端合同 | PASS_LIMITED | Notes / Study Guide / Briefing Doc / FAQ 已有真实 AI smoke |
| V1.6-D Studio Export | PASS_LIMITED_ACCEPTED | Markdown / JSON scoped export 已实现 |

## 必须补强

1. V1.8-D smoke 必须生成 WorkflowRun / ValidationReport。
2. 四类 Studio artifact 必须全部真实生成。
3. 每类 artifact 必须有 top-level evidence_refs。
4. 每个 section 必须有 evidence_refs。
5. FAQ 每条答案必须有 citation 或明确未覆盖。
6. 至少每类 artifact 的一条 citation 可解析到 DocumentUnit / EvidenceSpan。
7. Markdown export 必须包含 title / summary / sections / citation metadata。
8. JSON export 必须包含 artifact_id / artifact_type / sections / evidence_refs / schema_version / exported_at。
9. export / fixtures / reports 不得包含 raw local path、cache path、artifact physical path、API key、stack trace。
10. provider fallback 不得写成 Studio quality PASS。

## 禁止

- 不声明 Studio 普通用户 UX ready。
- 不声明 Studio 人工内容质量 ready。
- 不声明 Audio Overview / PPT / Mindmap / Document comparison ready。
- 不调用 `/api/v1/knowledge/*`。
- 不使用 mock 替代真实 data_service。
- 不把 schema pass 写成质量 pass。

## 风险评估

| 风险 | 等级 | 是否阻塞 | 收敛措施 |
| --- | --- | --- | --- |
| 规格漂移 | LOW-MEDIUM | 否 | 只验证 Agent-led Studio scoped path |
| 虚假验收 | MEDIUM | 否 | 报告明确 schema/export pass 不等于人工质量 pass |
| provider 波动 | MEDIUM | 否 | 使用保守重试并记录 degraded retry |
| UX 债务 | HIGH accepted | 不阻塞 V1.8 | 不声明普通用户 UX ready |

## 审计意见

可以实现 `scripts/v1_8_d_agent_studio_smoke.mjs` 和 `npm run smoke:v1.8-agent-studio`。

完成后必须复跑：

```bash
npm run check
npm run smoke:v1.5-c-studio
npm run smoke:v1.8-agent-studio
```

如果全部通过，V1.8-D 最多进入 `PASS_LIMITED`，下一阶段只能审计 V1.8-E Weak Frontend Shell。
