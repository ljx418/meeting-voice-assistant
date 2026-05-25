# ResearchNotebook V1.3 设计文档索引

文档状态：V1.3-A/B 计划阶段。V1.2 手工验收已按产品决策跳过，最终验收迁移到 V1.3 Agent Workflow 入口。
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

## 当前批准范围

当前只批准：

- V1.3-A Agent Workflow Contract Discovery
- V1.3-B Local Folder Connector Backend

暂不批准：

- 完整 Agent Planner
- 完整 Workflow Runtime
- Workflow UI
- Folder Summary Generator
- Evidence-backed Summary 全量能力
- PDF/PPTX/DOCX/video/audio 原生摄入 ready

## 文档清单

| 文件 | 用途 |
| --- | --- |
| `v1_3_current_gap_analysis.md` | V1.3 当前 gap、阶段拆分和 ready 边界。 |
| `v1_3_current_gap_analysis.drawio` | V1.3 阶段路线与 NOT_READY 边界图。 |
| `v1_3_agent_workflow_contract.md` | AgentTask / Workflow / WorkflowRun / WorkflowStep / Tool / SummaryArtifact 合同草案。 |
| `v1_3_local_folder_connector_contract.md` | Local Folder Connector 后端合同、授权、skip rules 和 path hygiene。 |
| `feature-route-matrix.md` | V1.3 route / adapter / readiness matrix。 |
