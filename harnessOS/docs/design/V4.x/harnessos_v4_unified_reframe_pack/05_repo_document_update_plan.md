# V4 文档更新计划

## 1. 需要新增的文档

建议新增：

```text
docs/design/V4.x/v4_x_unified_experience_prd.md
docs/design/V4.x/v4_x_unified_development_plan.md
docs/design/V4.x/v4_x_experience_state_machine.md
docs/design/V4.x/v4_x_interaction_orchestrator_contract.md
docs/design/V4.x/v4_x_report_schema.md
docs/design/V4.x/v4_x_mission_console_prd.md
docs/design/V4.x/v4_x_unified_experience_acceptance.md
docs/design/V4.x/v4_x_unified_experience_completion_note.md
```

## 2. 需要更新的文档

建议更新：

```text
docs/design/V4.x/00_README.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
docs/design/V4.x/v4_x_headless_first_roadmap.md
docs/design/V4.x/v4_x_headless_api_surface_map.md
docs/design/V4.x/v4_x_tui_drawio_html_report_plan.md
docs/design/V4.1/v4_x_interaction_experience_revised_plan.md
```

## 3. 文档口径修改

### 3.1 原 V4.x 口径

```text
Headless Workflow Core
+ TUI / Command Palette
+ Drawio Workflow Visualization
+ HTML Runtime Reports
+ Thin Web Console
```

### 3.2 新 V4.x 口径

```text
Headless Workflow Core
+ Interaction Orchestrator
+ Experience State Machine
+ Agent Policy Layer
+ Runtime Capability Matrix
+ Report Schema
+ Mission Console
+ Workflow Blueprint
+ Runtime Report
+ Review Console
+ Evidence Chain
```

## 4. README 修改建议

README 应明确：

```text
V4.1-V4.6 已完成 dev/local Headless-first route。
V4 当前进入 Unified Experience Rebaseline。
完整 Web Workflow Studio 不再是当前主线。
Mission Console 是主体验入口。
Drawio / HTML Report / Thin Web Console 是统一状态投影的不同 Head。
```

## 5. Gap 文档修改建议

新增绿色模块：

```text
Interaction Orchestrator【V4-U2】
Experience State Machine【V4-U1】
Agent Policy Layer【V4-U2】
Runtime Capability Matrix【V4-U3】
Report Schema【V4-U3】
Mission Console【V4-U4】
Unified Experience Acceptance【V4-U5】
```

仍为红色禁止误报：

```text
Agent executor ready
controlled executor ready
production-ready external app support
complete Workflow Studio ready
full multi-Agent orchestration ready
```

## 6. API Surface Map 修改建议

新增：

```text
InteractionIntent
InteractionStateProjection
AvailableActionDTO
HandoffRequest
AgentPolicyDecision
RuntimeCapabilityMatrix
WorkflowReportDTO
DrawioProjectionDTO
HtmlReportDTO
```

明确：

```text
这些对象是 BFF / interaction read model，不是 runtime truth。
```

## 7. TUI / Drawio / HTML Report Plan 修改建议

新增：

```text
所有 Head 必须共享 Experience State Machine。
所有 Head 必须共享 Report Schema。
所有 mutation 必须通过 Interaction Orchestrator 和 Agent Policy Layer。
```

## 8. 完成记录模板

每个新增阶段 completion note 必须包含：

```text
Stage Name
Allowed Claim
Forbidden Claims
Implementation Evidence
Validation Commands
Spec Drift Evaluation
False Green Evaluation
Next Stage Audit
Proceed Decision
No False Green Statement
```
