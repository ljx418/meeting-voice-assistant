# V1.8 Plan Self-Audit

日期：2026-05-30

## 自审结论

V1.8 计划初稿可以提交外部审计，但在进入实质开发前需要重点确认 Agent 合同和授权边界。

## 已闭环的审计意见

| 问题 | 初稿风险 | 修正 |
| --- | --- | --- |
| V1.7 人工 UX 被跳过可能被误写成 PASS | 虚假验收 | 明确写为 `SKIPPED_BY_STRATEGY` 和 accepted UX debt |
| Agent smoke 可能被误当成普通用户体验 ready | 规格漂移 | 完成声明只允许 Agent-led capability smoke-ready |
| 本地目录读取有越权风险 | 安全风险 | 每个阶段都要求用户授权后执行 |
| URL 支持范围容易扩大 | 能力夸大 | 明确 limited URL，不声明 all websites |
| citation 自动解析可能掩盖质量问题 | 虚假验收 | 要求 citation route 可解析，并保留人工质量风险 |
| Phase 2/3 容易膨胀 | 范围膨胀 | V1.8 不实现 Phase 2/3，只保留 NOT_READY 边界 |
| V1.8-A 缺少 WorkflowRun | 合同不完整 | 增加 WorkflowRun DTO，串联 task、steps、artifacts、validation report |
| AgentTask 暴露 raw target paths | 路径泄露 | 改为 `target_path_labels` / `target_path_refs`，最终 report / fixtures 禁止 raw path |
| ValidationReport 只写结果不写证据 | 虚假验收 | 增加 `step_results`、`assertions`、`raw_fixture_refs` |
| assertion 口径不稳定 | 验收不可复核 | 增加 expected / actual / status / evidence_ref |

## 剩余待外部审计问题

1. V1.8-B 是否需要先落独立 AgentTask 后端 route，还是先用 ResearchNotebook script smoke。
2. Agent task draft 是否应写入 data_service，还是 ResearchNotebook 本地 artifacts 即可。
3. 用户授权目录读取的 UI/CLI 交互是否足够。
4. V1.8-RC 是否需要保留少量人工质量抽查。
5. 弱前端是否会影响 PRD 的产品体验目标，需要在 V1.x final 另开 UX 阶段。

## 风险评估

| 风险 | 等级 | 是否阻塞 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 否，但需外部审计 |
| 虚假验收 | MEDIUM-HIGH | 条件阻塞，必须确认验收口径 |
| 本地文件授权 | MEDIUM | 否，需合同约束 |
| all-source / all-URL 误声明 | MEDIUM | 否，文档已限定 |
| 弱前端体验债务 | HIGH accepted | 不阻塞 V1.8，但阻塞普通用户 UX ready 声明 |

## 自审最终意见

V1.8-A 合同补强已闭环到文档层。V1.8-B 已按逐阶段审计口径执行并通过 `PASS_LIMITED` smoke。V1.8-C 已完成 Agent-led Guide / QA / Citation Validation，并通过真实数字人数据、真实 data_service、真实 AI provider smoke，状态为 `PASS_LIMITED`。V1.8-D 已完成 Agent-led Studio Output Validation，并通过四类 Studio 输出、citation 解析和 Markdown / JSON export smoke，状态为 `PASS_LIMITED`。

V1.8-C 风险评估：

| 风险 | 等级 | 是否阻塞 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 否，已限定为 Agent-led 受限 smoke |
| 虚假验收 | MEDIUM-HIGH | 条件不阻塞，但不得替代人工质量审查 |
| provider 波动 | MEDIUM | 否，已记录重试通过 |
| 普通用户 UX 债务 | HIGH accepted | 不阻塞 V1.8，但继续阻塞 UX ready 声明 |

下一步只允许审计 V1.8-D Agent Studio Validation；不得直接批准 V1.8-E/RC。

V1.8-D 风险评估：

| 风险 | 等级 | 是否阻塞 |
| --- | --- | --- |
| 规格漂移 | LOW-MEDIUM | 否，已限定为 Agent-led Studio scoped smoke |
| 虚假验收 | MEDIUM | 否，但不得替代人工内容质量审查 |
| provider/schema 波动 | MEDIUM | 否，已记录一次 schema mismatch 后复跑通过 |
| 普通用户 UX 债务 | HIGH accepted | 不阻塞 V1.8，但继续阻塞 UX ready 声明 |

下一步只允许审计 V1.8-E Weak Frontend Shell；不得直接批准 V1.8-RC。

V1.8-E 已完成独立弱前端展示壳，状态为 `PASS_LIMITED`。该壳读取 V1.8-B/C/D 真实 fixtures，生成可读 HTML 报告，展示 Agent plan、授权、运行状态、来源导入、Guide / QA、Studio、错误恢复和 evidence 入口。

V1.8-E 风险评估：

| 风险 | 等级 | 是否阻塞 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 否，已限定为 validation report shell |
| 虚假验收 | MEDIUM | 否，报告明确壳展示不等于 UX ready |
| 普通用户 UX 债务 | HIGH accepted | 不阻塞 V1.8，但继续阻塞 UX ready 声明 |

下一步只允许审计 V1.8-RC Agent-led PRD Smoke。

V1.8-RC 已完成 Agent-led PRD smoke 聚合验收，状态为 `AGENT_CAPABILITY_SMOKE_READY`。RC 聚合 V1.8-B/C/D/E 的真实 fixtures 和弱前端 HTML 展示壳，确认 V1.8 Agent-led PRD MVP capability validation 可声明受限 smoke-ready。

V1.8-RC 风险评估：

| 风险 | 等级 | 是否阻塞 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 否，已限定声明边界 |
| 虚假验收 | MEDIUM-HIGH | 否，但不能替代人工 UX / 内容质量验收 |
| 普通用户 UX 债务 | HIGH accepted | 不阻塞 V1.8，但继续阻塞普通用户 UX ready |

V1.8 自动化阶段完成。下一步不应继续把 Agent smoke 扩大为普通用户体验 ready；需要进入 V1.x Final Human UX Acceptance 或后续 V1.9 规划审计。
