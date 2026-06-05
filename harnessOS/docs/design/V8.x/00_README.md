# V8.x Design Index

文档状态：V8 station-agent workflow pilot complete / ready for review。本文是 V8.x canonical index。

## Current Baseline

V8 继承 V7 的最终收口口径：

```text
V7 complete: small studio production pilot and explainable TUI baseline ready for review.
```

该 baseline 只能解释为：

```text
小型工作室生产试点与可解释 TUI 基线 ready for review。
```

它不得被反向升级为：

```text
production ready
full production GA
complete Workflow Studio ready
Agent executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## V8 Goal

V8 的目标是把 V7 的“自然语言创建与运行工作流”升级为：

```text
Station Agent Workflow Pilot
```

也就是：

```text
每个 station 上有独立 Agent 在岗。
每个 Agent 有独立 role / goal / memory / model / tools / skills / MCP。
每个 Agent 按 station 描述执行、解释、产出和留痕。
Codex / Claude / ChromeCLI 只能作为受治理 connector / worker 接入。
```

## Canonical Documents

| File | Purpose |
| --- | --- |
| `v8_target_prd.md` | V8 总 PRD，定义工位 Agent、能力定制、终端 worker 和体验目标。 |
| `v8_target_architecture.md` | V8 目标架构，定义 Station Agent Operating Layer。 |
| `v8_current_gap_analysis.md` | V7 到 V8 的 gap 分析。 |
| `v8_current_gap_analysis.drawio` | V8 中文项目规划图。 |
| `v8_development_and_acceptance_plan.md` | V8 开发与验收总计划。 |
| `v8_milestone_roadmap.md` | V8 项目里程碑、阶段依赖和出门条件。 |
| `v8_acceptance_gate_matrix.md` | V8 阶段验收门槛矩阵。 |
| `v8_no_false_green_claim_guard.md` | V8 禁止声明与误报扫描规则。 |
| `v8_planning_audit_for_chatgpt.md` | 给 ChatGPT / 外部审计的审计入口。 |
| `v8_schema_contract_pack.md` | V8 Station Agent DTO / schema 合同包。 |
| `v8_station_agent_runtime_io_contract.md` | V8 工位 Agent runtime I/O 合同。 |
| `v8_skill_mcp_tool_contract.md` | V8 Skill / MCP / Tool 能力绑定合同。 |
| `v8_terminal_worker_high_risk_contract.md` | V8 Codex / Claude / ChromeCLI 高风险 worker 合同。 |
| `v8_agent_explainability_tui_contract.md` | V8 Agent 可解释 TUI 合同。 |
| `v8_evidence_package_contract.md` | V8 evidence package 与最终验收数据合同。 |
| `v8_implementation_readiness_audit.md` | V8 当前文档是否足以支撑开发的自审结论。 |
| `v8_0_station_agent_planning_gate.md` | V8-0 文档冻结与实现前门禁。 |
| `v8_1_station_agent_contract_plan.md` | V8-1 工位 Agent 合同计划。 |
| `v8_2_agent_context_memory_plan.md` | V8-2 Agent 上下文与记忆计划。 |
| `v8_3_skill_mcp_capability_binding_plan.md` | V8-3 Skill / MCP / Tool 能力绑定计划。 |
| `v8_4_station_agent_runtime_pilot_plan.md` | V8-4 工位 Agent 运行试点计划。 |
| `v8_4_station_agent_runtime_completion_note.md` | V8-4 真实运行验收与完成说明。 |
| `v8_5_terminal_worker_design_gate.md` | V8-5 Codex / Claude / ChromeCLI 终端 worker 设计门禁。 |
| `v8_5_terminal_worker_design_gate_completion_note.md` | V8-5 高风险设计门禁完成说明。 |
| `v8_6_controlled_terminal_worker_pilot_plan.md` | V8-6 受控终端 worker 试点计划。 |
| `v8_6_controlled_terminal_worker_completion_note.md` | V8-6 受控终端 worker 试点完成说明。 |
| `v8_7_multi_agent_project_workflow_pilot_plan.md` | V8-7 多 Agent 项目开发工作流试点计划。 |
| `v8_7_pre_implementation_audit.md` | V8-7 实现前审计与高风险闭环。 |
| `v8_8_agent_explainability_tui_plan.md` | V8-8 Agent 可解释 TUI 计划。 |
| `v8_8_agent_explainability_tui_completion_note.md` | V8-8 只读可解释 TUI 完成说明。 |
| `v8_9_final_acceptance_plan.md` | V8-9 最终验收计划。 |
| `v8_9_final_acceptance_framework_note.md` | V8-9 最终验收框架与阻断说明。 |

## Stage Order

```text
V8-0 Station Agent Planning Gate
 -> V8-1 Station Agent Contract
 -> V8-2 Agent Context And Memory
 -> V8-3 Skill / MCP / Tool Capability Binding
 -> V8-4 Station Agent Runtime Pilot
 -> V8-5 Terminal Worker Design Gate
 -> V8-6 Controlled Terminal Worker Pilot
 -> V8-7 Multi-Agent Project Workflow Pilot
 -> V8-8 Agent Explainability TUI
 -> V8-9 Final Acceptance
```

## Current Go / No-Go

| Area | Decision | Reason |
| --- | --- | --- |
| V7 baseline for V8 planning | GO | V7 supports bounded small studio and explainable TUI baseline only. |
| V8-0 documentation planning | COMPLETE FOR REVIEW | V8 PRD, architecture, gap, drawio, plan and claim guard exist. |
| V8-1 station-agent contract | COMPLETE FOR REVIEW | StationAgentDescriptor and registry tests pass. |
| V8-2 context / memory contract | COMPLETE FOR REVIEW | StationAgentContextEnvelope is station-scoped and redacted. |
| V8-3 skill / MCP / tool binding | COMPLETE FOR REVIEW | Capability resolver enforces allowlist and source policy. |
| V8-4 station-agent runtime pilot | PASS | Real MiniMax-backed fixture run produced station-agent evidence. |
| V8-5 terminal worker design gate | COMPLETE FOR REVIEW | Terminal worker remains blocked as high-risk design-only gate. |
| V8-6 controlled terminal worker pilot | PASS | User high-risk proceed decision was recorded; evidence is workspace-scoped readonly shell and handoff proposal only. |
| V8-7 multi-agent project workflow implementation | PASS | User high-risk proceed decision was recorded; bounded runtime fixture produced per-station project Agent, attempt history, handoff and evidence package. |
| V8-8 explainability TUI implementation | PASS | Read-only TUI evidence generated from V8-4 / V8-6 evidence. |
| V8-9 final claim | PASS | V8-4 / V8-6 / V8-7 / V8-8 evidence packages are PASS; final framework allows bounded V8 claim only. |

## Allowed Claims

```text
V8-0 complete: station-agent workflow planning gate ready for review.
V8-1 complete: station agent contract baseline ready for review.
V8-2 complete: station agent context and memory contract ready for review.
V8-3 complete: station agent skill and MCP capability binding baseline ready for review.
V8-4 complete: station-agent local document workflow pilot ready for review.
V8-5 complete: terminal worker design gate ready for review.
V8-6 complete: controlled terminal worker pilot ready for review.
V8-7 complete: multi-agent project workflow pilot ready for review.
V8-8 complete: agent explainability TUI baseline ready for review.
V8 complete: station-agent workflow pilot ready for review.
```

## Forbidden Claims

```text
Agent executor ready
production Agent executor ready
autonomous coding workflow ready
autonomous workflow editing ready
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
complete Workflow Studio ready
production-ready external app support
unrestricted terminal worker ready
ChromeCLI production automation ready
Codex terminal executor production ready
Claude terminal executor production ready
```

## Recommended External Audit Paths

```text
docs/design/V8.x/00_README.md
docs/design/V8.x/v8_target_prd.md
docs/design/V8.x/v8_target_architecture.md
docs/design/V8.x/v8_current_gap_analysis.md
docs/design/V8.x/v8_current_gap_analysis.drawio
docs/design/V8.x/v8_development_and_acceptance_plan.md
docs/design/V8.x/v8_acceptance_gate_matrix.md
docs/design/V8.x/v8_milestone_roadmap.md
docs/design/V8.x/v8_schema_contract_pack.md
docs/design/V8.x/v8_station_agent_runtime_io_contract.md
docs/design/V8.x/v8_skill_mcp_tool_contract.md
docs/design/V8.x/v8_terminal_worker_high_risk_contract.md
docs/design/V8.x/v8_agent_explainability_tui_contract.md
docs/design/V8.x/v8_evidence_package_contract.md
docs/design/V8.x/v8_no_false_green_claim_guard.md
docs/design/V8.x/v8_planning_audit_for_chatgpt.md
docs/design/V8.x/v8_implementation_readiness_audit.md
```
