# ResearchNotebook V1.8 Agent-Led Capability Validation Plan

日期：2026-05-30

## 1. 审查结论

V1.8 可以启动，但必须使用新的范围口径：

- V1.8 是 Agent-led capability validation，不是强前端体验阶段。
- V1.7 人工 UX 验收被策略性跳过，状态为 `SKIPPED_BY_STRATEGY`。
- V1.8 不能声明普通用户 UX ready。
- V1.8 只能在真实数据、真实 backend、真实 AI provider 可用时声明受限路径 smoke-ready。

## 2. 当前基线

- V1.5 真实数据 ChromeCLI 主路径：PASS。
- V1.6 PRD MVP 受限路径：PASS_LIMITED / ACCEPTED。
- V1.7 自动化 UX hardening：PASS。
- V1.7 人工 UX 验收：SKIPPED_BY_STRATEGY。
- 前端策略：weak frontend shell。
- 能力验证主语：Agent / workflow / backend contract。

## 3. V1.8 目标

用户目标语句示例：

递归读取 Desktop/技术分享/11-数字人，导入里面的 Markdown、TXT、PDF 和有限 URL，生成资料导读，基于来源回答数字人产业趋势，生成 Notes / Study Guide / Briefing Doc / FAQ，并输出验收报告。

V1.8 要验证：

1. Agent 能理解任务并生成 draft。
2. 用户确认后才执行本地资料处理。
3. Agent 能编排 source import / build / Guide / QA / Studio / citation validation。
4. Agent 能生成结构化 validation report。
5. 弱前端能展示任务状态、结果和失败原因。
6. 失败时能定位是前端、后端合同、AI provider、source parsing、citation 还是 workflow 编排问题。

## 4. V1.8 子阶段

| 阶段 | 名称 | 目标 | 出门状态 |
| --- | --- | --- | --- |
| V1.8-0 | Scope Rebase | 记录 V1.7 human UX skipped，并冻结 V1.8 弱前端策略 | PASS |
| V1.8-A | Agent Task Contract | 定义 AgentTask / WorkflowRun / WorkflowStep / ValidationReport / ValidationAssertion 合同 | CONTRACT_READY |
| V1.8-B | Agent Source Import | Agent 编排 PDF / TXT / Markdown / limited URL 导入 | PASS_LIMITED |
| V1.8-C | Agent Guide / QA | Agent 验证 Guide、问答、citation 可解析 | PASS_LIMITED |
| V1.8-D | Agent Studio | Agent 验证 Notes / Study Guide / Briefing Doc / FAQ 与导出 | PASS_LIMITED |
| V1.8-E | Weak Frontend Shell | 前端只展示 Agent draft / run / result / errors | PASS_LIMITED |
| V1.8-RC | Agent-led PRD Smoke | 真实数据完整 Agent 编排路径 | AGENT_CAPABILITY_SMOKE_READY |

## 5. 真实数据要求

必须使用真实数据，不允许只用 mock：

- `Desktop/技术分享/11-数字人`
- 数字人 Markdown 资料包
- 数字人 PDF 报告
- 至少 1 个 TXT 样本
- 至少 3 个 URL 样本：
  - 2 个可抽取公开页面
  - 1 个稳定失败页面

## 6. 验收总标准

- `npm run check` PASS。
- Agent workflow 使用真实 data_service。
- Agent workflow 不调用 `/api/v1/knowledge/*`。
- 本地目录读取必须经过用户确认。
- 未确认前不得 scan / import / source read。
- fixtures / reports 只记录 relative_path 或 sanitized label，不写绝对路径。
- ValidationReport 必须记录 step_results、assertions 和 raw_fixture_refs。
- 每个 assertion 必须包含 expected、actual、status 和可选 evidence_ref。
- Guide / QA / Studio 至少包含可解析 evidence_refs。
- 资料外问题必须拒答并建议补源。
- Studio 导出 Markdown / JSON 不含敏感路径。
- 弱前端不声明强 UX ready。

## 7. 完成声明上限

如果 V1.8-RC 通过，只能声明：

ResearchNotebook V1.8 Agent-led PRD MVP capability validation is smoke-ready for validated PDF / TXT / Markdown and limited URL sources on approved datasets.

仍不能声明：

- 普通用户 UX fully ready。
- all websites URL ready。
- all-source-type ready。
- OCR ready。
- Audio Overview ready。
- PPT generation ready。
- Mindmap ready。
- Document comparison ready。
- arbitrary Agent tool execution ready。
- cloud sync / collaboration ready。

## 8. 风险总评

| 风险 | 等级 | 原因 | 收敛措施 |
| --- | --- | --- | --- |
| 规格漂移 | MEDIUM | 从前端体验改为 Agent-led 验证，主语发生变化 | 文档明确 V1.8 不声明 UX ready |
| 虚假验收 | MEDIUM-HIGH | Agent 自动验收可能掩盖人工体验问题 | 输出中保留 accepted UX debt |
| 安全风险 | MEDIUM | Agent 读取本地目录 | 必须用户授权，报告脱敏 |
| 能力夸大 | MEDIUM | limited URL / limited sources 容易被写成全量 ready | 所有声明带限定范围 |

## 9. V1.8-A 合同补强状态

V1.8-A 当前只冻结 AgentTask / WorkflowRun / WorkflowStep / ValidationReport / ValidationAssertion 合同。该阶段不实现本地目录读取、不执行 workflow、不声明 Agent ready。

后续 V1.8-B/C/D/E 必须逐阶段重新审计，不能因为 V1.8-A 合同完成而自动批准。

## 10. V1.8-B 执行状态

V1.8-B Agent-led source import 已通过真实 data_service smoke，状态为 `PASS_LIMITED`。

通过范围：

- Agent draft。
- permission_grant_id 记录。
- 未授权前无 scan / import / source read 断言。
- Markdown / TXT / PDF 导入。
- limited URL 导入。
- stable failing URL。
- build/index。
- source list registry source_id。
- WorkflowRun / ValidationReport 脱敏 fixture。

仍不覆盖：

- Guide / QA / Studio quality。
- citation resolution。
- 普通用户 UX。
- all-source-type。
- all websites URL。

## 11. V1.8-C 执行状态

V1.8-C Agent-led Guide / QA / Citation Validation 已通过真实 data_service 和真实 AI provider smoke，状态为 `PASS_LIMITED`。

通过范围：

- Agent draft。
- 数字人 Markdown / PDF 导入。
- build/index。
- Notebook Guide 结构校验。
- Overview / Key Topics / Suggested Questions 最低结构校验。
- Guide evidence_refs 存在。
- Suggested Question QA。
- 覆盖型固定问题 QA。
- 资料外问题拒答。
- 至少一个 citation 解析到 DocumentUnit。
- 至少一个 citation 解析到 EvidenceSpan。
- EvidenceSpan offset contract 为 `normalized_text / half_open / document_unit_text`。
- WorkflowRun / ValidationReport 脱敏 fixture。

仍不覆盖：

- 人工内容质量评分。
- 普通用户 UX。
- Studio Notes / Study Guide / Briefing Doc / FAQ。
- Research 补源质量。
- all-domain QA。
- all-source-type。

风险评估：

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 仅声明 Agent-led 受限 smoke |
| 虚假验收 | MEDIUM-HIGH | 自动验证不能替代人工质量评分 |
| provider 波动 | MEDIUM | smoke 使用保守重试；报告记录 PASS_WITH_RETRY |

下一阶段只能审计 V1.8-D Agent Studio Validation，不得直接批准 V1.8-E / V1.8-RC。

## 12. V1.8-D 执行状态

V1.8-D Agent-led Studio Output Validation 已通过真实 data_service 和真实 AI provider smoke，状态为 `PASS_LIMITED`。

通过范围：

- Agent studio draft。
- 数字人 Markdown / PDF 导入。
- build/index。
- Studio Notes。
- Studio Study Guide。
- Studio Briefing Doc。
- Studio FAQ。
- 每类 artifact 顶层 evidence_refs。
- 每个 section evidence_refs。
- 每类 artifact 至少一条 citation 解析到 DocumentUnit。
- 每类 artifact 至少一条 citation 解析到 EvidenceSpan。
- Markdown export citation metadata。
- JSON export schema。
- WorkflowRun / ValidationReport 脱敏 fixture。

仍不覆盖：

- 人工内容质量评分。
- 普通用户 UX。
- Phase 2/3 输出能力。
- all-domain Studio quality。
- all-source-type。

风险评估：

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 规格漂移 | LOW-MEDIUM | 仅声明 Agent-led Studio scoped smoke |
| 虚假验收 | MEDIUM | schema/export pass 不等于人工质量 pass |
| provider/schema 波动 | MEDIUM | 首次 smoke 出现 `response_schema_mismatch`，复跑通过并记录 |

下一阶段只能审计 V1.8-E Weak Frontend Shell，不得直接批准 V1.8-RC。

## 13. V1.8-E 执行状态

V1.8-E Weak Frontend Shell 已通过，状态为 `PASS_LIMITED`。

通过范围：

- 生成独立 HTML 展示壳。
- 展示 Agent 计划与授权说明。
- 展示运行状态。
- 展示来源导入汇总。
- 展示 Guide / QA 验证结果。
- 展示 Studio 验证结果。
- 展示错误与恢复建议。
- 展示 citation / evidence 入口。
- HTML 无敏感路径或密钥命中。

仍不覆盖：

- 普通用户 UX ready。
- 完整 workflow editor。
- 任意 Agent 工具执行。
- V1.8-RC 全链路 Agent-led PRD smoke。

风险评估：

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 明确展示壳不是 workflow editor |
| 虚假验收 | MEDIUM | 壳展示成功不等于后端能力或内容质量通过 |
| UX 债务 | HIGH accepted | 不声明普通用户 UX ready |

下一阶段只能审计 V1.8-RC Agent-led PRD Smoke。

## 14. V1.8-RC 执行状态

V1.8-RC Agent-led PRD Smoke 已通过，状态为 `AGENT_CAPABILITY_SMOKE_READY`。

通过范围：

- V1.8-B Source Import 聚合验收。
- V1.8-C Guide / QA / Citation 聚合验收。
- V1.8-D Studio / Export 聚合验收。
- V1.8-E Weak Frontend Shell 聚合验收。
- raw_fixture_refs 存在。
- RC fixture 和 HTML 展示壳无敏感路径或密钥命中。
- 完成声明限定为 validated PDF / TXT / Markdown and limited URL sources on approved datasets。

仍不覆盖：

- 普通用户 UX fully ready。
- all websites URL ready。
- all-source-type ready。
- OCR ready。
- Audio Overview ready。
- PPT generation ready。
- Mindmap ready。
- Document comparison ready。
- arbitrary Agent tool execution ready。
- cloud sync / collaboration ready。

风险评估：

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 限定为 Agent-led PRD MVP capability validation |
| 虚假验收 | MEDIUM-HIGH | 不替代人工 UX / 内容质量验收 |
| UX 债务 | HIGH accepted | 保留 V1.x Final Human UX Acceptance |

V1.8 自动化 Agent-led capability validation 收口完成。
