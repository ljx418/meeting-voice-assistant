# V4.1 / V4.x Stage-Gate Development Plan / 阶段门禁开发计划

Status: active follow-up development outline.

This document is the controlling outline for post V4.1-A development. Every development stage must use bilingual naming, must validate the previous stage before moving on, and must record both spec drift and false-green risk. If either risk is HIGH, development stops for user decision.

## 1. Global Stage Gate / 全局阶段门禁

Every stage must follow this order:

1. Stage Implementation / 阶段实现
2. Focused Validation / 聚焦验证
3. Regression Validation / 回归验证
4. Browser Evidence / 浏览器证据
5. Completion Note / 完成记录
6. Spec Drift Evaluation / 规格漂移评估
7. False Green Evaluation / 虚假验收评估
8. Next Stage Audit / 下一阶段审计
9. Proceed Decision / 是否继续推进决策

Allowed proceed decisions:

```text
proceed
proceed_with_caution
stop_for_user_decision
```

Stop conditions:

1. Spec drift risk is HIGH.
2. False-green risk is HIGH.
3. Current stage core acceptance is FAIL.
4. Current stage core acceptance is BLOCKED and blocks the next stage.
5. Completion note does not match actual validation results.
6. The next step requires changing the V4.0 governance boundary.
7. The next step requires Agent executor, controlled executor, production auth, production filesystem access, or full multi-Agent runtime outside the approved stage scope.

## 2. Naming Rule / 命名规则

Each stage must use bilingual naming:

```text
V4.1-B Browser Evidence Hardening / 浏览器验收证据加固
```

Rules:

1. English stage names are used for file names, tests, DTOs, API identifiers, and machine-readable records.
2. Chinese stage names are used for communication, documentation titles, and manual audit clarity.
3. Completion notes and audit reports must include both names.
4. Stage claims remain English to keep claim guard stable.

## 3. V4.1 Local Knowledge Workflow MVP / 本地知识工作流 MVP

### V4.1-A Local Folder Summary Runtime Slice / 本地文件夹总结运行时切片

Status: focused implementation completed.

Allowed claim:

```text
V4.1-A complete: local Markdown folder summary runtime slice ready for focused browser validation.
```

Role in roadmap:

1. Establishes the dev/local Markdown folder summary vertical slice.
2. Proves proposal-first Agent workflow creation, folder authorization, debug scan, deterministic summary generation, artifact visibility, and quality report.
3. Does not prove full V4.1 MVP, generic rerun, full browser evidence, or governance evidence chain completeness.

### V4.1-B Browser Evidence Hardening / 浏览器验收证据加固

Status: completed for review.

Goal:

Complete browser evidence for the `Desktop/技术分享` recursive Markdown summary workflow beyond the focused smoke.

Implementation outline:

1. Expand browser automation for the 10 acceptance cases in `v4_1_desktop_folder_recursive_summary_acceptance.md`.
2. Save screenshots, network log, console errors, and result summary under the existing V4.1 evidence directory.
3. Mark every case as PASS, PARTIAL, FAIL, or BLOCKED.
4. Verify no browser direct `/v1/rpc` and no `/v1/events/subscribe`.
5. Verify DOM and network redaction for token, secret, raw payload, raw prompt, and signed URL strings.

Allowed claim:

```text
V4.1-B complete: browser evidence hardening for local folder summary workflow ready for review.
```

Spec drift checks:

1. Do not add PDF, DOCX, or PPTX parsing.
2. Do not add production filesystem permissions.
3. Do not convert focused smoke evidence into a full platform readiness claim.

False-green checks:

1. Browser evidence must prove the current build and current BFF were used.
2. PARTIAL and BLOCKED cases must not be written as PASS.
3. Demo fallback must not substitute for real BFF routes.

### V4.1-C Failure Rerun And Recovery Slice / 失败重跑与刷新恢复切片

Status: completed for local folder summary workflow validation.

Goal:

Add observable failure, user-confirmed local rerun, attempt history, and refresh recovery for the local Markdown workflow.

Implementation outline:

1. Add deterministic failure fixture or simulated parse failure.
2. Show failed node error state.
3. Require `user_confirmed=true` and non-agent source for rerun.
4. Create a new attempt while preserving old attempt and old error.
5. Restore workflow instance status, node status, artifacts, and quality report after refresh.
6. Keep the implementation scoped to V4.1 local knowledge workflow and do not introduce generic executor semantics.

Allowed claim:

```text
V4.1-C complete: failure rerun and recovery slice ready for local folder summary workflow validation.
```

Spec drift checks:

1. Do not implement generic `station.rerun` executor.
2. Do not allow `source=agent` rerun.
3. Do not claim controlled executor readiness.

False-green checks:

1. Tests must prove old attempt retention.
2. Browser validation must prove refresh recovery.
3. Network assertions must prove user-confirmed rerun.

### V4.1-D Governance Evidence Chain Slice / 治理证据链切片

Status: completed for review.

Goal:

Add V4.1-specific governance evidence chain for local knowledge workflow operations.

Implementation outline:

1. Record proposal to handoff to user confirmation to runtime result evidence.
2. Include operation type, runtime result ref, risk flags, policy decision, correlation ID, and redaction status.
3. Keep governance review panel read-only.
4. Ensure Agent debug remains read-only explanation or patch proposal only.
5. Ensure evidence review does not expose Apply, Publish, Approve, Reject, Execute, or Run controls.

Allowed claim:

```text
V4.1-D complete: governance evidence chain for local knowledge workflow ready for review.
```

Spec drift checks:

1. Do not add executor evidence runtime.
2. Do not add approval flow implementation.
3. Do not turn evidence review into an operation surface.

False-green checks:

1. Evidence must be created by actual operations.
2. Static fixtures must not be counted as full governance chain proof.
3. Browser evidence must show governance review is read-only.

### V4.1-E Local Knowledge Workflow MVP Consolidation Gate / 本地知识工作流 MVP 收口门禁

Status: completed for dev/local validation.

Goal:

Close V4.1 by proving the local recursive Markdown summary workflow MVP is ready for dev/local validation.

Implementation outline:

1. Consolidate V4.1-A through V4.1-D completion notes.
2. Run V4.1 focused tests, V4.0 regression, Workflow Console tests, build, and e2e.
3. Consolidate screenshots, network logs, console errors, artifact list, and quality report evidence.
4. Update V4.1 roadmap and audit summary.
5. Audit whether V4.2 prerequisites are met.

Allowed claim:

```text
V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation.
```

Spec drift checks:

1. Do not claim V4.2 controlled execution runtime.
2. Do not claim multi-Agent orchestration.
3. Do not claim complete Workflow Studio.

False-green checks:

1. All core acceptance cases must have evidence.
2. BLOCKED items must remain visible.
3. Focused smoke must not replace the V4.1 consolidation gate.

## 4. V4.2 Headless Interaction And Controlled Runtime / Headless 交互与受控运行时

V4.2 is split into a Headless Interaction Pivot first and a controlled runtime implementation second. This prevents the project from continuing as full Web low-code Studio first.

### V4.2-A Headless Interaction Pivot / Headless 交互转向

Goal: prove the V4.1 local workflow can be represented and reviewed through WorkflowSpec, TUI / Command Palette, Drawio visualization, HTML reports, and Thin Web Console.

Required evidence plan:

```text
tui-transcript.txt
workflow.yaml
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
workflow_board.html
artifacts.html
quality.html
evidence.html
result-summary.md
```

Allowed claim:

```text
V4.2-A complete: headless interaction baseline ready for local workflow validation.
```

Spec drift checks:

1. Do not implement controlled execution runtime in V4.2-A.
2. Do not make full Web Studio a prerequisite.
3. Do not treat Drawio or HTML reports as runtime truth.
4. Do not allow Agent to execute mutation.

False-green checks:

1. TUI transcript must not replace real runtime evidence in later implementation.
2. Drawio and HTML reports must be generated from source DTOs/specs, not hand-waved as runtime completion.
3. V4.2-A must not claim controlled executor ready.

### V4.2-B Controlled Runtime Design Gate / 受控运行时设计门禁

Goal: define the runtime implementation gate, acceptance standard, and audit requirements before any generic controlled runtime implementation.

Allowed claim:

```text
V4.2-B complete: controlled runtime design gate ready for implementation review.
```

### V4.2-C Controlled Runtime MVP / 受控运行时 MVP

Goal: implement generic user-confirmed workflow start, station rerun, attempt history, downstream stale propagation, runtime evidence, timeout baseline, and kill switch baseline.

Allowed claim:

```text
V4.2-C complete: controlled runtime MVP ready for dev/local validation.
```

### V4.2-D Controlled Runtime Consolidation Gate / 受控运行时收口门禁

Goal: prove V4.2 is sufficient for V4.3, V4.4, and V4.5 runtime needs after V4.2-C implementation evidence passes.

Allowed claim:

```text
V4.2 complete: controlled execution runtime MVP ready for dev/local validation.
```

Spec drift checks for V4.2:

1. Do not create Agent executor.
2. Do not create production executor.
3. Do not bypass user confirmation.
4. Do not trust event payload as truth.

False-green checks for V4.2:

1. Must include real start and rerun browser evidence.
2. Must include policy-deny tests.
3. Must prove `source=agent` cannot execute.

## 5. V4.3 Serial Multi-Agent Video Workflow MVP / 串行多 Agent 视频工作流 MVP

Stages:

1. V4.3-A Video Workflow Template And Agent Descriptor / 视频工作流模板与 Agent 描述符
2. V4.3-B Serial Video Runtime Execution / 串行视频运行时执行
3. V4.3-C Middle Station Rerun And Downstream Continuation / 中间工位重跑与下游续跑
4. V4.3-D Serial Multi-Agent Video Workflow Consolidation Gate / 串行多 Agent 视频工作流收口门禁

Allowed final V4.3 claim:

```text
V4.3 complete: serial multi-Agent video workflow MVP ready for dev/local validation.
```

Spec drift checks for V4.3:

1. Do not implement parallel deliberation.
2. Do not claim a complete video production platform.
3. Do not claim production media pipeline readiness.

False-green checks for V4.3:

1. Every station must produce or reference visible artifacts.
2. Rerun must preserve attempt history.
3. UI-only station cards must not count as runtime proof.

## 6. V4.4 Parallel Multi-Agent Deliberation Workflow MVP / 并行多 Agent 讨论工作流 MVP

Stages:

1. V4.4-A Roman Forum Template And Persona Descriptor / 罗马广场模板与人格描述符
2. V4.4-B Parallel Persona Runtime / 并行人格 Agent 运行时
3. V4.4-C Cross-Inspiration And Attributed Synthesis / 交叉启发与归因汇总
4. V4.4-D Parallel Multi-Agent Deliberation Consolidation Gate / 并行多 Agent 讨论收口门禁

Allowed final V4.4 claim:

```text
V4.4 complete: parallel multi-Agent deliberation workflow MVP ready for dev/local validation.
```

Spec drift checks for V4.4:

1. Do not implement unbounded Agent group chat.
2. Do not implement autonomous debate executor.
3. Cross-inspiration must be explicit and cannot rely on hidden raw context sharing.

False-green checks for V4.4:

1. Parallel branch execution must be proven.
2. Persona artifacts must be independently visible.
3. Synthesis must cite persona outputs.

## 7. V4.5 Long-Running Engineering Workflow MVP / 长时工程工作流 MVP

Stages:

1. V4.5-A Engineering Workflow Stage Model / 工程工作流阶段模型
2. V4.5-B Durable Task Board And Artifact Lineage / 持久任务看板与产物血缘
3. V4.5-C Quality Gates And Manual Checkpoints / 质量门禁与人工确认点
4. V4.5-D Long-Running Rerun And Recovery / 长时任务重跑与恢复
5. V4.5-E Long-Running Engineering Workflow Consolidation Gate / 长时工程工作流收口门禁

Allowed final V4.5 claim:

```text
V4.5 complete: long-running engineering workflow MVP ready for dev/local validation.
```

Spec drift checks for V4.5:

1. Do not claim autonomous coding workflow readiness.
2. Do not let Agent automatically mutate code.
3. Do not claim production job platform readiness.

False-green checks for V4.5:

1. Refresh recovery must be proven.
2. Human confirmation blocking must be proven.
3. Stage artifacts and evidence must be visible.

## 8. V4.6 Agent Workflow Builder UX / Agent 工作流搭建体验

Stages:

1. V4.6-A Clarifying Chat And Draft Planning / 澄清式对话与草案规划
2. V4.6-B Multi-Node Governed Draft Generation / 多节点受治理草案生成
3. V4.6-C Explain Before Apply And Repair Proposal / 应用前解释与修复提案
4. V4.6-D Cross-Scenario Builder Validation / 跨场景搭建器验证
5. V4.6-E Agent Workflow Builder UX Consolidation Gate / Agent 工作流搭建体验收口门禁

Allowed final V4.6 claim:

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

Spec drift checks for V4.6:

1. Agent must not automatically apply, publish, run, or rerun.
2. Do not claim complete AgentTalkWindow readiness.
3. Do not claim autonomous workflow editing readiness.

False-green checks for V4.6:

1. Chat transcript, patch diff, and network assertions must be saved.
2. Durable changes must require user confirmation.
3. Forbidden UI copy must be absent.

## 9. Required Completion Note Template / 必需完成记录模板

Every stage completion note must include:

```text
Stage Name / 阶段名称
Allowed Claim / 允许声明
Forbidden Claims / 禁止声明
Implementation Evidence / 实现证据
Validation Commands / 验证命令
Browser Evidence / 浏览器证据
Spec Drift Evaluation / 规格漂移评估
False Green Evaluation / 虚假验收评估
Next Stage Audit / 下一阶段审计
Proceed Decision / 是否继续推进决策
No False Green Statement / 非虚假完成声明
```

Required evaluation fields:

```text
Spec Drift Evaluation / 规格漂移评估
- risk_level: LOW | MEDIUM | HIGH
- evidence:
- out_of_scope_items_detected:
- decision:

False Green Evaluation / 虚假验收评估
- risk_level: LOW | MEDIUM | HIGH
- evidence:
- unverified_items:
- decision:

Next Stage Audit / 下一阶段审计
- next_stage_name:
- prerequisites_met:
- blocked_items:
- plan_revision_required:
- proceed_decision: proceed | proceed_with_caution | stop_for_user_decision
```

## 10. Current Proceed Decision / 当前推进决策

Current baseline stage:

```text
V4.1-E Local Knowledge Workflow MVP Consolidation Gate / 本地知识工作流 MVP 收口门禁
```

Current recommendation:

```text
proceed
```

Reason:

V4.1-E has consolidated V4.1-A through V4.1-D into the local recursive Markdown summary workflow MVP baseline. The current baseline is V4.1 complete: local recursive Markdown summary workflow MVP ready for dev/local validation. The next stage should proceed to V4.2-A Headless Interaction Pivot / Headless 交互转向, with WorkflowSpec, TUI transcript, Drawio, HTML reports, Thin Web Console observation, and evidence package outputs. V4.2-A must not implement generic controlled execution runtime, Agent executor, production-ready external app support, or full multi-Agent orchestration.
