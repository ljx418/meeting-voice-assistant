# 给 Codex Plan 模式的提示词

请基于当前 V4.1–V4.6 已完成的 Headless-first dev/local 路线，重新制定并落盘一套新的 V4 统一体验开发及验收计划，同时修改对应 PRD 文档。

## 当前基线

当前进展：

- V4.1 本地递归 Markdown 总结工作流 MVP 已完成。
- V4.2 Headless Interaction Pivot + Controlled Runtime MVP 已完成。
- V4.3 串行多 Agent 视频工作流 MVP 已完成。
- V4.4 并行多 Agent 讨论工作流 MVP 已完成。
- V4.5 长时工程工作流 MVP 已完成。
- V4.6 Governed Agent Workflow Builder UX 已完成。

当前允许声明：

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

仍不能声明：

```text
Agent executor ready
controlled executor ready
production-ready external app support
complete Workflow Studio ready
full multi-Agent orchestration ready
complete AgentTalkWindow ready
autonomous workflow editing ready
```

## 核心调整

当前 V4.x 需要重新收口：不要继续把完整 Web 低代码 Workflow Studio 当作主线。

新的目标形态是：

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

请将当前文档从：

```text
Headless Core + TUI + Drawio + HTML Report + Thin Web Console
```

升级为：

```text
Mission Console 驱动工作流任务；
Workflow Blueprint 理解结构；
Runtime Report 观察运行；
Review Console 做确认与恢复；
Evidence Chain 做治理审计；
所有 Head 共享 Experience State Machine 与 Report Schema。
```

## 需要新增文档

请新增以下文档：

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

## 需要更新文档

请更新：

```text
docs/design/V4.x/00_README.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
docs/design/V4.x/v4_x_headless_first_roadmap.md
docs/design/V4.x/v4_x_headless_api_surface_map.md
docs/design/V4.x/v4_x_tui_drawio_html_report_plan.md
docs/design/V4.1/v4_x_interaction_experience_revised_plan.md
```

## 新开发阶段

请制定以下 V4 Unified Experience Rebaseline 阶段：

### V4-U0 Documentation Rebase / 文档重基线

目标：统一 V4.1–V4.6 文档口径，确认 V4.6 是当前 dev/local 基线，保留 forbidden claims。

### V4-U1 Experience State Machine / 体验状态机

交付：

```text
v4_x_experience_state_machine.md
experience_state.schema.json
available_actions.schema.json
```

必须定义：

Workflow-level state:

```text
Idle
IntentCaptured
SpecDrafted
SchemaValidated
DiffReady
AwaitingConfirmation
DraftApplied
Published
RunReady
Running
Blocked
Failed
Recoverable
RerunRequested
Rerunning
Completed
Reviewed
Archived
```

Station-level state:

```text
Pending
Ready
Running
Completed
Failed
WaitingApproval
NeedsInput
Stale
Recoverable
RerunRequested
Rerunning
Skipped
```

Evidence-level state:

```text
NoEvidence
EvidencePending
EvidenceRecorded
ReviewReady
Reviewed
Disputed
Archived
```

每个状态必须定义：

```text
state_id
label
description
available_actions
blocked_actions
requires_user_confirmation
risk_level
evidence_required
visible_in_tui
visible_in_html
visible_in_drawio
visible_in_thin_web
```

### V4-U2 Interaction Orchestrator Contract / 交互编排合同

交付：

```text
v4_x_interaction_orchestrator_contract.md
interaction_intent.schema.json
interaction_state_projection.schema.json
handoff_request.schema.json
available_action.dto.md
```

职责：

```text
接收 TUI / Agent / Thin Web / HTML Report 的用户意图。
映射为 InteractionIntent。
查询 Experience State Machine。
返回 available_actions。
调用 Agent Policy Layer。
不直接执行 runtime mutation。
所有 mutation 仍走 governed BFF / WorkflowPatch / user_confirmed path。
```

### V4-U3 Report Schema And Projection Unification / 报告与投影统一

交付：

```text
v4_x_report_schema.md
workflow_report.schema.json
station_report.schema.json
artifact_report.schema.json
quality_report.schema.json
evidence_report.schema.json
```

报告统一字段：

```text
report_id
workflow_spec_ref
workflow_version_ref
workflow_instance_ref
generated_at
source_refs
stations[]
artifacts[]
quality[]
evidence[]
available_actions[]
redaction_status
```

### V4-U4 Mission Console UX / 任务驾驶舱体验统一

交付：

```text
v4_x_mission_console_prd.md
mission_console_transcript.md
canonical command grammar
```

命令体验：

```text
/create workflow
/explain plan
/show diff
/confirm apply
/publish
/run
/status
/rerun station
/show artifacts
/show quality
/show evidence
/repair proposal
```

规则：

```text
Agent 不自动 apply / publish / run / rerun。
所有 durable mutation 必须 user_confirmed。
transcript 必须体现 Experience State Machine 的状态变化。
```

### V4-U5 Scenario Path Acceptance / 场景体验验收

验收路径：

1. 自然语言创建工作流。
2. 工作流结构可视化。
3. 工作流运行与观察。
4. 工位产物查看与质量监控。
5. 局部失败修复与重跑。
6. 治理证据链审查。
7. 串行多 Agent 视频工作流。
8. 并行多 Agent 罗马广场讨论。
9. 长时工程任务工作流。
10. Agent Workflow Builder。

每条路径必须标记：

```text
PASS | PARTIAL | FAIL | BLOCKED
```

每条路径必须有 evidence。

### V4-U6 V4 Unified Experience Gate / V4 统一体验收口门禁

目标：判断是否可以声明 V4 统一 dev/local 用户体验基线完成。

允许声明：

```text
V4 unified dev/local experience baseline complete: Headless workflow core with Mission Console, Blueprint, Runtime Report, Review Console, and Evidence Chain ready for review.
```

仍禁止声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 新 PRD 要求

请修改或新增 `v4_x_unified_experience_prd.md`，产品定位为：

```text
HarnessOS V4 是一个 Headless-first AI Workflow OS。
它不再把完整 Web Studio 作为唯一入口，而是通过 Mission Console、Workflow Blueprint、Runtime Report、Review Console 和 Evidence Chain，让用户以自然语言和可审查报告的方式定义、运行、观察、修复和审计 AI 工作流。
```

核心体验路径：

1. 自然语言创建工作流。
2. 工作流结构可视化。
3. 工作流运行与观察。
4. 工位产物查看与质量监控。
5. 局部失败修复与重跑。
6. 治理证据链审查。
7. 串行多 Agent 视频工作流。
8. 并行多 Agent 罗马广场讨论。
9. 长时工程任务工作流。
10. Agent Workflow Builder。

## 全局风险控制

必须保留：

```text
source=agent cannot execute mutation
durable mutation requires user_confirmed=true
EventBridge only triggers refresh
WorkflowSpec cannot mutate runtime truth
Drawio is visualization only
HTML Report is read-only
No token/raw payload leakage
No false-green claims
```

## 新增测试建议

请规划新增：

```text
tests/test_v4_unified_experience_state_machine.py
tests/test_v4_interaction_orchestrator_contract.py
tests/test_v4_report_schema_projection.py
tests/test_v4_mission_console_transcripts.py
tests/test_v4_unified_experience_acceptance.py
tests/test_v4_no_false_green_claims.py
```

## 回归命令

规划中必须保留：

```bash
./.venv/bin/python -m pytest tests/test_v4_*.py -q
./.venv/bin/python -m pytest -q
cd apps/workflow-console && npm test -- --runInBand
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
```

## Completion note 模板

每个阶段 completion note 必须包含：

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

## 执行要求

请先输出：

1. revised V4 unified experience roadmap summary
2. new / updated document list
3. PR slices for V4-U0 to V4-U6
4. acceptance matrix
5. risk controls
6. completion evidence format
7. planned test list

不要直接进入代码实现。先完成文档落盘计划和 PRD 修订计划。
```
