# ResearchNotebook V1.3 设计文档索引

文档状态：V1.3-0 已通过，V1.3-A Agent Workflow Contract Discovery 已完成 DISABLED_READY，V1.3-B Local Folder Connector dry-run manifest 已完成 PASS_LIMITED，V1.3-C deterministic dry-run runtime 已完成 PASS_LIMITED，V1.3-D SummaryArtifact generation 已完成 PASS_LIMITED，V1.3-E Workflow UI 已完成 PASS_LIMITED，V1.3-F Agent Planner 已完成 PASS_LIMITED，V1.3-G Evidence-backed Summary 已完成 PASS_LIMITED，V1.3-RC Agent Entry Browser Acceptance 已完成 PASS_LIMITED。V1.2 手工验收已按产品决策跳过，最终验收迁移到 V1.3 Agent Workflow 入口。
日期：2026-05-25。

## V1.3 目标

V1.3 的产品目标是让用户用自然语言触发可运行的研究工作流：

```text
用户目标 -> Agent workflow draft -> 用户授权 -> workflow run -> folder summaries -> evidence-backed citations
```

首个目标用例：

```text
递归总结 Desktop/技术分享，每个子文件夹生成一份总结。
```

## 当前执行策略

V1.3 不直接一次性实现完整 Agent 产品，按以下阶段推进：

- V1.3-A Agent Workflow Contract Discovery
- V1.3-B Local Folder Connector Backend
- V1.3-C Deterministic Folder Summary Workflow Runtime
- V1.3-D Folder Summary Generator
- V1.3-E Workflow UI
- V1.3-F Agent Planner
- V1.3-G Evidence-backed Summary
- V1.3-RC Agent Entry ChromeCLI / Manual Acceptance

每个阶段完成后都需要更新 gap、drawio、feature matrix 和对应 smoke / acceptance report。

每个阶段完成后还必须执行规格漂移评估和虚假验收评估；任一风险为 HIGH / BLOCKING 时停止进入下一阶段，由用户主导后续方向。

当前阶段状态：

- V1.3-0 Governance Gate Update：PASS。
- V1.3-A Agent Workflow Contract Discovery：DISABLED_READY。
- V1.3-B Local Folder Connector Backend：PASS_LIMITED。
- V1.3-C Deterministic Folder Summary Workflow Runtime：PASS_LIMITED。
- V1.3-D Folder Summary Generator：PASS_LIMITED。
- V1.3-E Workflow UI：PASS_LIMITED。
- V1.3-F Agent Planner：PASS_LIMITED。
- V1.3-G Evidence-backed Summary：PASS_LIMITED。
- V1.3-RC Agent Entry ChromeCLI / Browser Acceptance：PASS_LIMITED。

暂不声明：

- PDF/PPTX/DOCX/video/audio 原生摄入 ready
- arbitrary Agent tool execution ready
- Assessment / Governance / Cloud collaboration ready

## 文档清单

| 文件 | 用途 |
| --- | --- |
| `v1_3_full_development_plan.md` | V1.3 完整开发计划、子阶段验收标准和最终声明口径。 |
| `v1_3_current_gap_analysis.md` | V1.3 当前 gap、阶段拆分和 ready 边界。 |
| `v1_3_current_gap_analysis.drawio` | V1.3 阶段路线与 NOT_READY 边界图。 |
| `v1_3_agent_workflow_contract.md` | AgentTask / Workflow / WorkflowRun / WorkflowStep / Tool / SummaryArtifact 合同草案。 |
| `v1_3_local_folder_connector_contract.md` | Local Folder Connector 后端合同、授权、skip rules 和 path hygiene。 |
| `v1_3_a_agent_workflow_contract_discovery_report.md` | V1.3-A 阶段验收、规格漂移和虚假验收评估。 |
| `v1_3_b_local_folder_connector_backend_report.md` | V1.3-B 后端 focused tests、adapter tests、风险评估和 V1.3-B-RC 前置要求。 |
| `v1_3_c_workflow_runtime_report.md` | V1.3-C dry-run workflow runtime、step timeline、run report、风险评估和下一阶段边界。 |
| `v1_3_d_folder_summary_generator_report.md` | V1.3-D SummaryArtifact 生成、confirm_extract、relative_path_only evidence_refs 和风险评估。 |
| `v1_3_e_workflow_ui_report.md` | V1.3-E 工作流 UI、step timeline、artifact panel、风险评估和下一阶段边界。 |
| `v1_3_f_agent_planner_report.md` | V1.3-F registered Agent Planner draft、真实 smoke、风险评估和下一阶段边界。 |
| `v1_3_g_evidence_backed_summary_report.md` | V1.3-G SummaryArtifact source_unit_span citation、真实 smoke、风险评估和 RC 边界。 |
| `v1_3_rc_agent_entry_acceptance_report.md` | V1.3-RC Agent 入口浏览器验收、最终声明和剩余 NOT_READY 边界。 |
| `v1_3_prd_coverage_analysis.md` | 基于 Stitch 可读元数据和当前实现的 PRD 覆盖度分析；PRD 原文待补齐后二次审计。 |
| `v1_3_prd_alignment_plan.md` | 基于 Stitch 快照的 PRD 对齐改造计划、阶段边界和风险门禁。 |
| `v1_3_prd_alignment_acceptance_report.md` | PRD 对齐改造验收报告，记录中文化、Agent 入口和证据文案优化。 |
| `feature-route-matrix.md` | V1.3 route / adapter / readiness matrix。 |
