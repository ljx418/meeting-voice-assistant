# HarnessOS V4.x Unified Experience Development Plan

文档状态：V4-U5A / V4-U5B 后的 V4.x 统一体验收口开发计划。

## 1. Baseline

当前允许声明：

```text
V4-U5A complete: scenario evidence archive ready for review.
V4-U5B complete: experience state projection read-model ready for shared workflow heads.
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

## 2. V4-U0 Documentation Rebase / 文档重基线

目标：统一 V4.1-V4.6 completion evidence、gap 文档、roadmap、API surface 和统一体验 PRD。

交付：

```text
v4_x_unified_experience_prd.md
v4_x_unified_development_plan.md
v4_x_unified_experience_acceptance.md
v4_x_unified_experience_completion_note.md
更新 00_README / gap / drawio / roadmap / API surface
```

允许声明：

```text
V4-U0 complete: V4 documentation rebaseline ready for unified experience planning.
```

## 3. V4-U1 Experience State Machine / 体验状态机

目标：让 Mission Console、Workflow Blueprint、Runtime Report、Review Console 和 Evidence Chain 共享同一状态语义。

交付：

```text
v4_x_experience_state_machine.md
schemas/experience_state.schema.json
schemas/available_actions.schema.json
```

允许声明：

```text
V4-U1 complete: shared experience state machine ready for dev/local workflow heads.
```

## 4. V4-U2 Interaction Orchestrator Contract / 交互编排合同

目标：统一多 Head 的用户意图入口，避免 TUI、Agent、HTML Report、Thin Web Console 各自解释 mutation。

交付：

```text
v4_x_interaction_orchestrator_contract.md
schemas/interaction_intent.schema.json
schemas/interaction_state_projection.schema.json
schemas/handoff_request.schema.json
```

允许声明：

```text
V4-U2 complete: interaction orchestrator contract ready for multi-head workflow UX.
```

## 5. V4-U3 Report Schema And Projection Unification / 报告与投影统一

目标：统一 Drawio、HTML Report、TUI status 和 Thin Web Console 的数据投影。

交付：

```text
v4_x_report_schema.md
schemas/workflow_report.schema.json
schemas/station_report.schema.json
schemas/artifact_report.schema.json
schemas/quality_report.schema.json
schemas/evidence_report.schema.json
```

允许声明：

```text
V4-U3 complete: shared report projection baseline ready for Drawio, HTML, TUI, and Thin Console.
```

## 6. V4-U4 Mission Console UX / 任务驾驶舱体验统一

目标：把自然语言和 command palette 收敛为主体验入口。

交付：

```text
v4_x_mission_console_prd.md
evidence/unified-experience/mission_console_transcript.txt
```

允许声明：

```text
V4-U4 complete: Mission Console UX baseline ready for dev/local workflow validation.
```

## 7. V4-U5A Scenario Evidence Hardening / 场景证据加固

目标：把 V4.1-V4.6 的证据按 UX-01 到 UX-12 归档，形成可审计 evidence archive。

交付：

```text
evidence/unified-experience/UX-01/result-summary.md
...
evidence/unified-experience/UX-11/result-summary.md
evidence/unified-experience/result-summary.md
```

每个 UX case 的 evidence summary 必须包含：

```text
ux_id
status: PASS / PARTIAL / FAIL / BLOCKED
evidence_scope: real_runtime / deterministic_devlocal / transcript_only / report_only / planned_contract
evidence_refs
runtime_backed: true / false
deterministic_only: true / false
false_green_risk: LOW / MEDIUM / HIGH
notes
```

限制：

```text
UX-08 / UX-09 / UX-10 如果只是 deterministic dev/local，不得写成 full multi-Agent orchestration PASS。
存在 FAIL / BLOCKED 时不能进入 U6。
存在 PARTIAL 时必须写明是否允许进入 U6。
U5A 不得声明 V4 unified complete。
```

允许声明：

```text
V4-U5A complete: scenario evidence archive ready for review.
```

## 8. V4-U5B Experience State Projection / 体验状态投影

目标：把 Experience State Machine 落成共享 read-model projection，让 Mission Console、Runtime Report、Review Console、Evidence Chain 使用同一状态语义。

交付：

```text
ExperienceStateProjection
AvailableAction resolver
State transition validator
refresh_generation
stale_reasons
source_refs
TUI state timeline panel
TUI available actions panel
```

限制：

```text
Experience State Machine 不是 runtime truth。
不得写 WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun。
Interaction Orchestrator 不直接写 runtime。
```

允许声明：

```text
V4-U5B complete: experience state projection read-model ready for shared workflow heads.
```

## 9. V4-U5C Mission Console Closed Loop / 任务驾驶舱闭环

目标：走通用户说目标 -> WorkflowSpec / Diff -> Blueprint -> user confirmation -> Runtime Report -> Evidence Chain。

阶段计划：

```text
docs/design/V4.x/v4_u5c_mission_console_closed_loop_plan.md
```

验收：

```text
transcript 包含 IntentCaptured / SpecDrafted / SchemaValidated / DiffReady / AwaitingConfirmation。
durable mutation 必须 user_confirmed=true。
source=agent 不能执行 mutation。
Mission Console 不能被描述为 Agent executor。
如果运行依赖 V4.2-C controlled runtime，必须标注 runtime_backed=true。
如果只是 transcript-only，必须标注 transcript_only=true。
```

允许声明：

```text
V4-U5C complete: Mission Console closed loop ready for dev/local validation.
```

## 10. V4-U5D Review Console And Evidence Chain / 复核台与证据链

目标：统一 Review Console 和 Evidence Chain 的只读审计与 user-confirmed handoff 语义。

阶段计划：

```text
docs/design/V4.x/v4_u5d_review_console_evidence_chain_plan.md
```

要求：

```text
Review Console 只能发起 user-confirmed handoff，不能直接执行。
Evidence Chain 只读。
Evidence Chain 不得出现 Apply / Publish / Approve / Reject / Execute / Run。
EvidenceReportDTO 只允许 view / export / open_handoff。
ReviewActionDTO 必须包含 operation、source、actor_type、requires_user_confirmation、policy_decision、risk_flags。
source=agent 不能执行 mutation。
```

允许声明：

```text
V4-U5D complete: Review Console and Evidence Chain baseline ready for review.
```

## 11. V4-U5E Real LLM Local Document Workflow / 真实 LLM 本地技术文档工作流

目标：让 V4 完成后可以真实启动本地技术文档解析工作流，并调用真实 LLM 生成总结。

阶段计划：

```text
docs/design/V4.x/v4_u5e_real_llm_local_document_workflow_plan.md
```

验收：

```text
用户确认后工作流真实启动。
实际读取 Desktop/技术分享 或等价 fixture。
Markdown 文件被递归解析。
每个子文件夹生成一份 LLM-backed 总结。
生成总览总结。
quality_report.json 记录 unsupported 文件和空文件夹。
Evidence Chain 记录 provider/model/ref，不泄露 raw prompt 或 raw content。
无 LLM key 时必须标记 BLOCKED 或 fallback_demo_only，不能写成 real_llm PASS。
```

允许声明：

```text
V4-U5E complete: real LLM-backed local technical document workflow ready for dev/local validation.
```

限制：

```text
V4-U5E 不是 Agent executor。
V4-U5E 不是 production filesystem permission。
V4-U5E 不支持 PDF / DOCX / PPTX。
```

## 12. V4-U5 Scenario Path Acceptance Package / 场景路径验收包

目标：按用户体验路径重新验收 V4.1-V4.6。

当前状态：

```text
V4-U5 complete: unified scenario path acceptance package ready for V4-U6 gate review.
V4-U6 is not allowed to start automatically because UX-08, UX-09, and UX-10 remain PARTIAL deterministic_devlocal evidence.
```

阶段计划：

```text
docs/design/V4.x/v4_u5_scenario_path_acceptance_plan.md
```

交付：

```text
v4_x_unified_experience_acceptance.md
evidence/unified-experience/result-summary.md
```

允许声明：

```text
V4-U5 complete: unified scenario path acceptance package ready for V4-U6 gate review.
```

限制：

```text
不要在 U5A/B/C/D 任一阶段声明 V4 unified complete。
不要在 U5A/U5E 尚未完成 UX-01 到 UX-12 全部归档时声明 U5 complete。
```

## 13. V4-U6 V4 Unified Experience Gate / 统一体验收口门禁

目标：判断 V4.x 是否可以作为统一 dev/local Headless AI Workflow OS 体验基线。

阶段计划：

```text
docs/design/V4.x/v4_u6_unified_experience_gate_plan.md
```

通过条件：

```text
UX-01 到 UX-12 全部有 evidence summary。
无 FAIL / BLOCKED。
PARTIAL 已人工确认并记录 proceed decision。
Runtime Capability Matrix 存在并区分 supported / partial / planned / unsupported。
WorkflowSpec Registry 存在并声明不替代 runtime truth。
Mission Console / Runtime Report / Review Console 使用同一 ExperienceStateProjection。
TUI / Command Palette 必须把 ExperienceStateProjection 渲染为可视状态线，而不是自己维护独立状态。
本地技术文档工作流可以实际启动并解析 Markdown 文件。
真实 LLM-backed 总结有 provider/model evidence；无 LLM key 时不得标记 PASS。
Evidence Chain 只读。
No False Green claim scan 通过。
回归测试通过。
```

允许声明：

```text
V4-U6 complete: V4 unified dev/local experience baseline ready for review.
```

声明限定：

```text
Headless workflow core with Mission Console, Workflow Blueprint, Runtime Report, Review Console, and Evidence Chain ready for review.
This does not prove complete Workflow Studio, Agent executor, controlled executor production readiness, production external app support, or full multi-Agent orchestration.
```

## 14. Stage Gate

每个阶段 completion note 必须包含：

```text
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

停止条件：

```text
Spec Drift Risk = HIGH
False Green Risk = HIGH
需要 Agent executor
需要 production controlled executor
需要 production auth
需要 full Web Studio 作为前置
```
