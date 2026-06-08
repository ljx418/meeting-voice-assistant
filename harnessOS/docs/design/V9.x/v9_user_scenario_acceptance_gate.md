# V9 User Scenario Acceptance Gate

文档状态：V9 user scenario acceptance gate / required before final acceptance.

## 1. Purpose

V9 技术验收不能只证明 schema、fixture 或单元测试通过，还必须证明用户能理解、触发、观察和审计关键体验路径。

本门槛是 V9-8 final acceptance 的前置硬门槛，不新增 V9 阶段，也不替代 V9-3 / V9-4 / V9-5 / V9-6 / V9-7 的技术验收。

## 2. Global Rule

每个用户场景必须输出以下字段：

```text
scenario_id
title
owner_stage
user_goal
user_entry
user_steps
expected_user_visible_outputs
expected_audit_outputs
runtime_evidence_required
evidence_scope
runtime_backed
allowed_status
evidence_refs
dashboard_or_report_ref
claim_guard_notes
redaction_guard_notes
```

场景 PASS 的最低条件：

```text
用户能看到目标、Agent 分工、运行状态、产物和证据链。
用户能打开 HTML 看板或报告审计结果。
用户能区分 ready for review，且不得把它理解为 ready / production ready。
runtime-backed 场景必须引用真实 runtime fixture 或 real runtime evidence。
planning docs、transcript-only、report-only 不得满足 runtime-backed 用户场景 PASS。
```

## 2.1 User-Facing Capability Boundary

截至当前 V9-2，用户可以真实体验和审计的能力是：

```text
用户可以打开 V9-2 evidence dashboard。
用户可以看到 workflow.instance.start / station.rerun / artifact.write / quality.evaluation.create 四类受控动作。
用户可以看到 policy / capability / HumanAuthorizationRef / approval / kill switch / idempotency / timeout / rollback / evidence chain。
用户可以确认 source=agent direct durable mutation 被拒绝。
用户可以确认 connector.call / external_llm.call / git.commit / git.push / production.deploy 仍被拒绝。
```

这说明项目已经具备“受控动作执行切片”的审计体验，但仍不能解释为：

```text
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
autonomous workflow editing ready
complete Workflow Studio ready
production ready
```

当前下一开发阶段 V9-3 完成后的目标体验是：

```text
用户用自然语言触发一个多 Agent 编排 runtime slice。
系统展示 station-bound Agents、Agent 角色、串行依赖、并行分支、fan-out、fan-in、失败恢复、attempt history 和 artifact lineage。
用户可以打开 runtime dashboard / evidence chain 审计每个 Agent 的产物来源、producer_agent_id、producer_attempt_id 和 redacted evidence refs。
```

V9 全阶段完成后的目标用户体验是：

```text
用户提出目标。
系统生成工作流、Agent 分工、Blueprint 和 Diff。
用户确认高风险动作。
Agent 在受控边界内执行、协作、产出方案、产物或代码建议。
Studio / TUI 展示 Agent 身份、运行状态、产物血缘、Runtime Report 和 Evidence Chain。
最终验收看板展示每个阶段和每个用户场景的 PASS / PARTIAL / FAIL / BLOCKED。
```

该体验最多支持 `ready for review`，不得被摘要为 production ready、complete Studio 或 unrestricted Agent executor。

## 3. Required User Scenarios

| Scenario | Stage | User Goal | Acceptance Gate |
| --- | --- | --- | --- |
| US-V9-01 | V9-2 | 用户作为技术负责人，审查“受控执行器是否真的只执行四类允许动作” | V9-2 evidence dashboard shows allowed operations, excluded operations, source=agent denial and evidence chain |
| US-V9-02 | V9-3 | 用户输入“让多个 Agent 并行评审本地技术方案并合成结论”，审查多 Agent 编排路径 | runtime fixture shows serial, parallel, fan-out, fan-in, recovery, attempt history and lineage |
| US-V9-03 | V9-4 | 用户输入“针对一个小型代码修改任务生成方案、diff、测试和 review”，审查代码工作流不自动提交 | dashboard shows proposal-only diff, sandboxed tests, review summary and no auto commit / push / deploy evidence |
| US-V9-04 | V9-5 | 用户要求 Agent 读取 workspace、运行受控测试命令并生成 diff proposal，审查终端 sandbox 边界 | dashboard shows workspace boundary, command tier, transcript, diff capture and denied escape attempts |
| US-V9-05 | V9-6 | 用户在 Studio 打开同一工作流，查看 Agent 分工、运行状态、产物和证据链 | browser evidence shows BFF/DTO usage, read-only review panels and no direct runtime truth write |
| US-V9-06 | V9-8 | 用户打开最终验收看板，确认 V9 是否只能进入 ready-for-review 结论 | final dashboard aggregates all stage evidence, user scenario results, claim scan, redaction scan and drawio XML result |
| US-V9-07 | V9-3 | 用户输入“罗马广场：让不同身份 Agent 讨论一个哲学话题并互相质询”，审查多 Agent 讨论与 synthesis | runtime fixture shows role-specific Agents, multi-round messages, attribution-preserving synthesis and evidence chain |
| US-V9-08 | V9-3 / V9-6 | 用户输入一个视频点子，系统制定创作 workflow 并生成分镜图与创作包 | workflow spec, storyboard, image artifacts, provider/model refs, redaction result and dashboard are visible |
| US-V9-09 | V9-6 | 用户用自然语言要求优化已有工作流，审查系统是否只生成 Diff proposal 并等待确认 | WorkflowDiff proposal is visible; no durable mutation happens before user confirmation or valid human authorization |

## 3.1 Concrete Key Scenario Thresholds

### KS-V9-A Local Technical Design Review With Multiple Agents

User story:

```text
作为技术负责人，
我输入“请让多个 Agent 评审 docs/design/V9.x 的 V9-3 多 Agent 编排方案，分别从架构、风险、验收证据三个角度提出意见，并合成一份结论”，
我期望系统展示每个 station 上的 Agent、它们的角色、并行分支状态、各自产物、冲突点、合成结论和证据链。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
至少 3 个 station-bound Agents: architecture reviewer, risk reviewer, evidence reviewer.
用户能看到 fan-out: 同一设计材料分发给 3 个并行分支。
用户能看到 fan-in: synthesis station 引用 3 个分支产物并保留 attribution_refs。
每个产物有 producer_agent_id 和 producer_attempt_id。
失败或超时分支必须保留 old attempt，并展示 recovery attempt。
最终 dashboard 展示 serial/parallel/fan-in/fan-out、attempt history、artifact lineage 和 Evidence Chain。
缺任一项则 US-V9-02 不得 PASS。
```

### KS-V9-B Controlled Coding Change Proposal

User story:

```text
作为开发者，
我输入“请分析一个小型代码修改任务，生成实现计划、diff proposal、测试计划和 review 结论”，
我期望 Agent 能给出可审查的代码变更建议，但不能自动 apply patch、commit、push 或 deploy。
```

Acceptance threshold:

```text
user_entry=Mission TUI, Workflow Studio or controlled coding dashboard.
用户能看到 PlanningAgent / ImplementationAgent / TestAgent / ReviewAgent / FixAgent 的分工。
diff output 必须是 proposal，不是已应用 patch。
sandboxed test result 必须记录命令、退出码、日志引用和 redaction status。
review summary 不能被当作 approval。
fix-loop 必须生成新 proposal，不得静默修改已有产物。
必须有 no auto commit / no auto push / no auto deploy evidence。
缺任一项则 US-V9-03 不得 PASS。
```

### KS-V9-C Governed Terminal Worker Sandbox Review

User story:

```text
作为审计者，
我要求 Agent 在 workspace 内执行只读检查或受控测试命令，
我期望看到命令分级、workspace 边界、transcript、diff capture，以及越权命令被拒绝的证据。
```

Acceptance threshold:

```text
user_entry=Terminal Worker review dashboard or Studio evidence panel.
dashboard 显示 workspace_root、command_tier、allowed command、denied command。
workspace escape、symlink escape、secret-read、git push、production deploy 默认拒绝。
transcript_ref 和 diff_capture_ref 可打开。
任何 write action 必须有 user_confirmed=true 或 valid human_authorization_ref。
缺 sandbox denial evidence 则 US-V9-04 不得 PASS。
```

### KS-V9-D Workflow Studio Evidence Review

User story:

```text
作为产品使用者，
我在 Studio 打开一个已运行工作流，
我期望看到 workflow graph、每个 station 的 Agent profile、runtime status、artifact lineage、Runtime Report 和 Evidence Chain，并能确认哪些动作只是 ready for review。
```

Acceptance threshold:

```text
user_entry=Workflow Studio.
UI 通过 BFF / DTO 获取数据。
browser network log 不得出现 direct internal runtime route。
Runtime Report 和 Evidence Chain 只读。
页面不得出现自动执行、自动发布、Agent 已直接执行 durable mutation 的暗示文案。
用户能从 UI 打开每个关键 evidence_ref。
缺 BFF/browser/read-only 证据则 US-V9-05 不得 PASS。
```

### KS-V9-E Final V9 User Acceptance Dashboard

User story:

```text
作为最终验收人，
我打开 V9 final dashboard，
我期望一眼看到每个阶段和每个用户场景是 PASS、PARTIAL、FAIL 还是 BLOCKED，并知道哪些能力仍不得声明完成。
```

Acceptance threshold:

```text
dashboard 汇总 V9-0..V9-7 evidence summary。
dashboard 汇总 US-V9-01..US-V9-09 scenario status。
无 FAIL / BLOCKED。
PARTIAL 必须有 human proceed decision。
No False Green scan PASS。
Redaction scan PASS。
Drawio XML valid。
Forbidden claims 只出现在 forbidden/no-false-green context。
缺任一项则 US-V9-06 和 V9-8 不得 PASS。
```

### KS-V9-F Roman Forum Multi-Agent Debate

User story:

```text
作为知识工作者，
我输入“罗马广场：请让哲学家、工程师、历史学家、伦理学家讨论‘技术进步是否会削弱人的自由’，互相质询并总结共识和分歧”，
我期望系统展示不同身份 Agent 的多轮发言、互相引用、分歧点、综合结论和证据链。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
至少 4 个 role-specific station-bound Agents: philosopher, engineer, historian, ethicist。
至少 1 个 Moderator 或 Synthesizer Agent。
至少 2 轮 discussion turns。
每条 message 必须记录 producer_agent_id、attempt_id、input_refs、output_refs。
Agent 之间的引用或反驳必须有 message_ref 或 attribution_ref。
Synthesizer output 必须保留 attribution_refs，不能生成无来源总结。
dashboard 展示多 Agent 讨论路径、角色身份、message graph、fan-in synthesis 和 Evidence Chain。
缺任一项则 US-V9-07 不得 PASS。
```

### KS-V9-G Video Creation Storyboard Workflow

User story:

```text
作为创作者，
我输入“我想做一个 60 秒短视频，主题是一个程序员在深夜发现 AI 工作流自己学会了开会”，
我期望系统自动制定创作工作流，生成 brief、脚本、镜头清单、每个分镜 prompt、分镜图和创作审查报告。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
workflow 必须包含 Idea Analyst、Script Agent、Storyboard Agent、Prompt Agent、Image Generation Agent、Review Agent。
产物至少包含 creative_brief.json、script.md、shot_list.json、storyboard_prompts.json、image artifact refs、visual_consistency_report.json、runtime_report.html、evidence_chain.json。
至少 4 个 storyboard shots。
每个 shot 必须有 shot_id、scene_description、prompt_template_ref、image_artifact_ref。
Image Generation Agent 必须通过受控 provider adapter 或明确的 host capability 生成 image artifact refs。
provider invocation evidence 必须记录 provider、model_ref、input_artifact_refs、output_artifact_refs、redaction_status。
如果 MiniMax 或 host image capability 不可用，场景只能 BLOCKED 或 fallback_demo_only，不得 PASS。
placeholder image 或 deterministic image 不能写成 real image generation。
不得泄露 raw prompt、API key、raw provider payload、raw artifact content。
缺任一项则 US-V9-08 不得 PASS。
```

### KS-V9-H Natural Language Workflow Optimization

User story:

```text
作为工作流编辑者，
我输入“把这个视频创作工作流优化一下：减少到 5 个 station，把风格改成黑色幽默，并增加安全审查 Agent”，
我期望系统生成可审查的 WorkflowDiff proposal，而不是直接修改运行时。
```

Acceptance threshold:

```text
user_entry=Mission TUI or Workflow Studio.
系统必须读取 existing WorkflowSpec / Blueprint refs。
系统必须输出 WorkflowDiff proposal，列出 added / removed / modified stations、Agent role / goal / tool / model changes、risk_delta 和 affected_runtime_refs。
用户确认前不得 durable mutation。
source=agent 不得直接写 WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun / Artifact。
durable mutation 必须 user_confirmed=true 或 valid human_authorization_ref。
优化后的 Blueprint / Runtime Report / Evidence Chain 必须可重新链接。
如果只是 transcript-only，不得标记 runtime_backed PASS。
缺任一项则 US-V9-09 不得 PASS。
```

## 4. Scenario-Specific Gates

### US-V9-01 Controlled Runtime Evidence Review

Required evidence:

```text
docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/index.html
docs/design/V9.x/evidence/v9-2-controlled-executor-runtime/acceptance-data.json
```

PASS requires:

```text
allowed_operations exactly four.
excluded_operations are visible.
source_agent_durable_mutation_allowed=false.
runtime_backed=true.
evidence_scope=real_runtime_fixture.
claim guard explains this is not controlled executor ready.
```

### US-V9-02 Multi-Agent Orchestration User Path

PASS requires:

```text
user can see station-bound Agents.
user can see serial dependency and parallel branch states.
user can see fan-out dispatch and fan-in join attribution.
user can see failed attempt, retained old attempt and recovery attempt.
user can see artifact lineage with producer_agent_id and producer_attempt_id.
user can open the evidence dashboard.
```

### US-V9-03 Coding Workflow User Path

PASS requires:

```text
user can see original goal, plan, diff proposal, sandboxed test result, review summary and fix-loop proposal.
diff proposal is not patch apply.
review summary is not approval.
automated tooling does not commit, push, deploy or mark review as approval.
```

### US-V9-04 Terminal Worker User Path

PASS requires:

```text
user can see workspace root, command tier, transcript ref and diff capture.
workspace escape attempts are denied.
secret-read attempts are denied and redacted.
write actions require approval or valid human authorization according to the stage gate.
```

### US-V9-05 Studio User Path

PASS requires:

```text
user can inspect workflow graph, station Agent profile, artifact lineage, runtime report and evidence chain.
Studio panels use BFF / DTO boundary.
browser does not call internal runtime routes directly.
Evidence Review and Runtime Report remain read-only.
```

### US-V9-06 Final User Review Path

PASS requires:

```text
V9-0..V9-7 evidence packages exist.
US-V9-01..US-V9-09 have PASS or explicitly accepted PARTIAL with human decision.
No FAIL / BLOCKED scenario remains.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
```

### US-V9-07 Roman Forum Debate Path

PASS requires:

```text
user can see role-specific Agents with distinct identities.
user can see at least two discussion turns.
user can see message refs or attribution refs between Agents.
user can see synthesis output with preserved attribution_refs.
user can open the discussion dashboard and Evidence Chain.
```

### US-V9-08 Video Creation Storyboard Path

PASS requires:

```text
user can see idea brief, script, shot list, storyboard prompts and image artifact refs.
at least four storyboard shots exist.
image generation is provider-backed or clearly marked fallback_demo_only / placeholder.
provider / model / input_artifact_refs / output_artifact_refs are visible without raw prompt or token leakage.
user can open runtime report and evidence chain.
```

### US-V9-09 Natural Language Workflow Optimization Path

PASS requires:

```text
user can see WorkflowDiff proposal before any mutation.
user can see added / removed / modified stations and Agent profile changes.
user can approve, reject or keep proposal as draft.
source=agent direct runtime mutation remains denied.
optimized Blueprint, Runtime Report and Evidence Chain links are updated only after user confirmation or valid human authorization.
```

## 5. Stop Conditions

```text
User scenario evidence is missing but the stage is marked PASS.
Planning docs are counted as runtime-backed user evidence.
User cannot open the dashboard or report for a claimed scenario.
Stage dashboard hides denied operations or missing evidence.
V9 final acceptance runs before US-V9-01..US-V9-09 are reviewed.
Any user-facing text implies production ready, Agent executor ready, full orchestration ready or complete Studio ready.
Roman Forum discussion is counted as full multi-Agent orchestration readiness.
Video storyboard planning or placeholder images are counted as provider-backed image generation.
Natural language optimization directly mutates WorkflowDraft / WorkflowVersion / WorkflowInstance before user confirmation.
```

## 6. Minimum Dashboard Fields

Every scenario dashboard or report must display:

```text
scenario_id
status
evidence_scope
runtime_backed
user_goal
user_visible_outputs
evidence_refs
missing_evidence
claim_risk
false_green_risk
redaction_status
next_gate
```
