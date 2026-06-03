# HarnessOS V4 重新收口开发及验收计划

## 1. 阶段定位

当前 V4.x 已完成到 dev/local 路线的 V4.6，但整体叙事仍存在两个问题：

1. 容易被误读为“完整 Web Workflow Studio 已经 ready”。
2. TUI、Drawio、HTML Report、Thin Web Console 多个 Head 的体验存在割裂。

因此需要新增一个 **V4 Unified Experience Rebaseline / V4 统一体验收口阶段**，目标不是新增大型 runtime 能力，而是把 V4.1–V4.6 的完成项统一成一个面向用户的产品形态：

```text
Mission Console 驱动任务
Workflow Blueprint 理解结构
Runtime Report 观察运行
Review Console 执行有限用户确认
Evidence Chain 审计复盘
```

## 2. 当前基线

当前允许声明：

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

当前仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 3. 新 V4 目标形态

V4 结束后，用户应获得的体验不是“一个复杂低代码画布”，而是：

```text
我可以把一个复杂目标交给 HarnessOS。
HarnessOS 会生成可审查的工作流方案。
我能看懂工作流结构、运行状态、产物、质量和风险。
关键动作都需要我确认。
失败后我可以局部重跑。
最终我能得到可交付报告和证据链。
```

## 4. 新 V4 开发阶段

### V4-U0 Documentation Rebase / 文档重基线

目标：统一当前 V4.1–V4.6 文档口径，修正历史残留与过度声明风险。

交付：

- 更新 V4.x README。
- 更新 V4.x gap 分析。
- 更新 Headless-first roadmap。
- 更新 API surface map。
- 新增统一体验 PRD。
- 新增统一体验验收矩阵。

验收：

- 文档中不再把完整 Web Studio 作为 V4 主线。
- 文档中明确 V4.6 为当前 dev/local 终点。
- 文档中明确下一阶段为 unified experience hardening / post-V4 production 或 V5 planning。
- 禁止声明仍保持有效。

允许声明：

```text
V4-U0 complete: V4 documentation rebaseline ready for unified experience planning.
```

---

### V4-U1 Experience State Machine / 体验状态机

目标：把 TUI、Drawio、HTML Report、Thin Web Console、Agent Builder 统一到同一套用户体验状态上。

交付：

- `v4_x_experience_state_machine.md`
- `experience_state.schema.json`
- `available_actions.schema.json`
- workflow-level state machine
- station-level state machine
- evidence/review state machine

Workflow-level 状态建议：

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

Station-level 状态建议：

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

Evidence-level 状态建议：

```text
NoEvidence
EvidencePending
EvidenceRecorded
ReviewReady
Reviewed
Disputed
Archived
```

验收：

- 每个状态定义 `state_id`、`label`、`description`、`available_actions`、`blocked_actions`、`requires_user_confirmation`、`risk_level`、`evidence_required`。
- TUI transcript、HTML Report、Drawio、Thin Web Console 至少能引用同一状态 label。
- 不新增 runtime mutation。

允许声明：

```text
V4-U1 complete: shared experience state machine ready for dev/local workflow heads.
```

---

### V4-U2 Interaction Orchestrator Contract / 交互编排合同

目标：定义多 Head 入口如何把用户意图转成标准 InteractionIntent，并在执行前经过策略、确认和状态机。

交付：

- `v4_x_interaction_orchestrator_contract.md`
- `interaction_intent.schema.json`
- `interaction_state_projection.schema.json`
- `handoff_request.schema.json`
- `available_action.dto.md`

职责：

```text
接收 TUI / Agent / Thin Web / HTML Report 的用户意图。
映射为标准 InteractionIntent。
查询 Experience State Machine。
返回 available_actions。
调用 Agent Policy Layer。
不直接执行 runtime mutation。
所有 mutation 仍走 governed BFF / WorkflowPatch / user_confirmed path。
```

验收：

- 任意 mutation action 必须经过 `requires_user_confirmation=true`。
- `source=agent` 请求 mutation 必须被拒绝或转成 proposal/handoff。
- HTML Report 与 Drawio 只能发起 read-only 或 handoff，不得直接 mutation。

允许声明：

```text
V4-U2 complete: interaction orchestrator contract ready for multi-head workflow UX.
```

---

### V4-U3 Report Schema And Projection Unification / 报告与投影统一

目标：统一 Drawio、HTML Report、TUI status、Thin Web Console 的数据投影，避免每个 Head 自己解释 runtime。

交付：

- `v4_x_report_schema.md`
- `workflow_report.schema.json`
- `station_report.schema.json`
- `artifact_report.schema.json`
- `quality_report.schema.json`
- `evidence_report.schema.json`
- report generator fixture

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

验收：

- HTML Report、Drawio、TUI status 至少共享一个 report projection fixture。
- 报告只读。
- 报告不包含 token、secret、raw payload、raw prompt、signed URL。
- 报告明确 data source：spec / draft / version / runtime / artifact / quality / evidence。

允许声明：

```text
V4-U3 complete: shared report projection baseline ready for Drawio, HTML, TUI, and Thin Console.
```

---

### V4-U4 Mission Console UX / 任务驾驶舱体验统一

目标：把 TUI / Command Palette 从“命令行工具”升级为主体验入口：Mission Console。

交付：

- `v4_x_mission_console_prd.md`
- Mission Console command grammar
- canonical transcripts for V4.1 / V4.3 / V4.4 / V4.5 / V4.6 scenarios
- `mission_console_transcript.md`

主命令体验：

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

验收：

- Mission Console 可覆盖“创建与确认 / 运行与观察 / 修复与审计”三段体验。
- Agent 仍不能 auto apply / run / rerun。
- 所有 durable mutation 仍需 user_confirmed。
- transcript 里能体现 Experience State Machine 状态变化。

允许声明：

```text
V4-U4 complete: Mission Console UX baseline ready for dev/local workflow validation.
```

---

### V4-U5 Scenario Path Acceptance / 场景体验验收

目标：按用户体验路径而非技术模块，对 V4.1–V4.6 做重新验收。

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

交付：

- `v4_x_unified_experience_acceptance.md`
- scenario acceptance matrix
- evidence package index
- screenshots / drawio / html / transcript links

验收：

- 每条路径必须标记 PASS / PARTIAL / FAIL / BLOCKED。
- 每条路径必须记录对应 evidence。
- 如果某路径只是 deterministic dev/local MVP，必须明确写出。
- 不得把 deterministic dev/local MVP 写成 production-ready 或 autonomous execution。

允许声明：

```text
V4-U5 complete: unified V4 user experience acceptance package ready for review.
```

---

### V4-U6 V4 Unified Experience Gate / V4 统一体验收口门禁

目标：最终判断当前 V4 是否可以作为一个统一的 dev/local Headless AI Workflow OS 体验基线。

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

验收：

- V4-U0 至 V4-U5 completion notes 均存在。
- 每个 completion note 包含 Spec Drift Evaluation、False Green Evaluation、Next Stage Audit、Proceed Decision。
- 全量测试通过。
- 无 forbidden claim。
- 无 source=agent mutation。
- report / drawio / html / tui 均不泄露敏感字段。

## 5. 统一验收命令

建议命令：

```bash
./.venv/bin/python -m pytest tests/test_v4_*.py -q
./.venv/bin/python -m pytest -q
cd apps/workflow-console && npm test -- --runInBand
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
```

新增建议测试：

```text
tests/test_v4_unified_experience_state_machine.py
tests/test_v4_interaction_orchestrator_contract.py
tests/test_v4_report_schema_projection.py
tests/test_v4_mission_console_transcripts.py
tests/test_v4_unified_experience_acceptance.py
tests/test_v4_no_false_green_claims.py
```

## 6. 风险控制

### 规格漂移风险

主要风险：重新收口时把 V4-U 当成新 runtime 阶段，误改后端运行边界。

控制：

```text
V4-U0 至 V4-U6 主要是体验统一、合同、报告、状态机和验收，不新增 Agent executor、不新增 production 能力。
```

### 虚假验收风险

主要风险：把 deterministic dev/local MVP 写成 full multi-Agent orchestration 或 controlled executor ready。

控制：

```text
所有文档必须保留 forbidden claims。
所有 completion note 必须记录 No False Green Statement。
Runtime Capability Matrix 必须显示 supported / partial / planned / unsupported。
```

### 用户体验割裂风险

主要风险：TUI、Drawio、HTML Report、Thin Web Console 各自为政。

控制：

```text
统一 Experience State Machine。
统一 Report Schema。
统一 Interaction Orchestrator Contract。
统一 Mission Console 主入口叙事。
```

## 7. 交付包建议

最终文档目录建议：

```text
docs/design/V4.x/
  v4_x_unified_experience_prd.md
  v4_x_unified_development_plan.md
  v4_x_experience_state_machine.md
  v4_x_interaction_orchestrator_contract.md
  v4_x_report_schema.md
  v4_x_mission_console_prd.md
  v4_x_unified_experience_acceptance.md
  v4_x_unified_experience_completion_note.md
```
