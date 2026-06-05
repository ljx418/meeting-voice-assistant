# V8 Planning Audit For ChatGPT

文档状态：V8 external audit entrypoint。

## Audit Objective

请审计 V8 是否合理地把项目目标从 V7 的小型工作室与可解释 TUI，推进为：

```text
Station Agent Workflow Pilot
```

重点判断：

```text
是否每个 station 都有独立 Agent 的清晰合同。
是否每个 Agent 的 role / goal / memory / tools / skills / MCP 可审计。
是否 Agent 能力绑定不会绕过 policy / controlled runtime / user confirmation。
是否 Codex / Claude / ChromeCLI 被正确限制为受控 worker / connector。
是否没有把 V8 写成 Agent executor ready 或 full multi-Agent orchestration ready。
```

## Documents To Audit

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
docs/design/V8.x/v8_implementation_readiness_audit.md
```

## Audit Questions

```text
1. V8 是否仍保持 V7 baseline 的 bounded interpretation？
2. V8 是否明确当前 station 不是独立 Agent？
3. StationAgentDescriptor 是否足以指导后续 schema / implementation？
4. Agent context / memory / skill / MCP 边界是否足够清晰？
5. Codex / Claude / ChromeCLI 是否被限制在高风险 connector / worker 边界内？
6. V8-6 / V8-7 是否有独立 human high-risk proceed decision？
7. 验收门槛是否覆盖 source=agent durable mutation denial？
8. No False Green 是否覆盖英文和中文误报？
9. P0 schema / I/O / capability / evidence contracts 是否足以指导 V8-1 到 V8-4 实现？
10. Terminal worker 合同是否足以阻止 Codex / Claude / ChromeCLI 被误写成无限制 Agent executor？
```
