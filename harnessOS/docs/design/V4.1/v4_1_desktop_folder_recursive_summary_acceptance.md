# V4.1 Desktop Folder Recursive Summary Workflow Acceptance

Status: V4.1 target acceptance standard.

This document defines the ChromeCLI / browser automation acceptance standard for the `Desktop/技术分享` recursive folder summary workflow. It is not a completion note and does not claim that the current project already supports this end-to-end experience.

Allowed completion claim after this acceptance passes:

```text
V4.1 desktop folder recursive summary workflow acceptance passed for dev/local validation.
```

Forbidden claims:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
autonomous workflow editing ready
```

## Goal

The user opens Workflow Console, types one natural-language request into the Agent assistant, and the system creates a workflow draft. After explicit user confirmation, the workflow is applied, published, and run. The workflow recursively scans `Desktop/技术分享`, parses all Markdown files, generates one summary per child folder, and generates a final overview summary.

The target user request is:

```text
帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。
```

## Preconditions

1. Start workflow-console build preview.
2. Start the dev/local BFF/runtime fixture.
3. Set `VITE_HARNESSOS_DEMO_MODE=false`.
4. Browser traffic may access only static assets and `/bff/*`.
5. Browser traffic must not access `/v1/rpc`.
6. Browser traffic must not access `/v1/events/subscribe`.
7. If the real `Desktop/技术分享` folder is unavailable, create an equivalent fixture:

```text
tests/fixtures/desktop/技术分享/
  AgentOS/01-架构.md
  AgentOS/02-工作流.md
  前端低代码/画布设计.md
  前端低代码/节点库.md
  项目复盘/周报.md
  未支持/test.pdf
  空文件夹/
```

## Evidence Output

The automation runner must save evidence under:

```text
docs/design/V4.1/acceptance-evidence/desktop-folder-summary/
```

Required evidence files:

```text
screenshots/
network-log.json
console-errors.json
result-summary.md
```

Every test case must record:

```text
case_id
status: PASS | PARTIAL | FAIL | BLOCKED
screenshots
network_assertions
console_errors
notes
```

## Case 1: Agent Generates Workflow Draft

Steps:

1. Open Workflow Console.
2. Open Agent assistant.
3. Enter the target user request.
4. Send the request.

PASS:

1. Agent creates a workflow draft proposal.
2. Canvas shows pending or ghost workflow nodes.
3. No file scan starts before user confirmation.
4. No mutation is automatically executed.

PARTIAL:

1. Agent creates a proposal, but the draft is incomplete or not shown clearly on canvas.
2. No unsafe mutation occurs.

FAIL:

1. Agent directly executes scan, apply, publish, or run.
2. Browser sends direct `/v1/rpc` or `/v1/events/subscribe`.
3. Sensitive fields appear in DOM or network logs.

BLOCKED:

1. Console cannot load.
2. Agent assistant cannot be opened.
3. BFF fixture is unavailable.

Required screenshots:

```text
01-open-console.png
02-agent-request-entered.png
03-agent-workflow-draft-proposal.png
04-canvas-ghost-nodes.png
```

## Case 2: Apply Workflow Draft

Steps:

1. Click View Diff.
2. Click Apply to Draft.
3. Confirm the browser or UI confirmation prompt.

PASS:

1. Apply request contains `user_confirmed=true`.
2. Apply request `source` is not `agent`.
3. Official workflow nodes appear on canvas after apply.
4. Draft revision increases.

PARTIAL:

1. Draft applies and nodes appear, but draft revision is not visible in UI.
2. Network log still proves a refreshed draft was fetched from BFF.

FAIL:

1. Apply runs with `source=agent`.
2. Apply runs without explicit user confirmation.
3. Canvas changes before apply.

BLOCKED:

1. Diff cannot be opened.
2. Apply control is missing.

Required screenshots:

```text
05-workflow-diff-before-apply.png
06-user-confirm-apply.png
07-canvas-after-apply.png
```

## Case 3: Configure Local Folder Input

Steps:

1. Select the folder input node.
2. In Inspector, enter `Desktop/技术分享`, or select the fixture path.
3. Click Authorize Read.
4. Click Debug Scan.

PASS:

1. UI displays a folder tree.
2. UI displays total file count.
3. UI displays Markdown file count.
4. UI displays child folder count.
5. UI displays unsupported file count.
6. No summaries are generated during debug scan.

PARTIAL:

1. Scan summary appears but folder tree is incomplete.
2. Unsupported files are counted but not listed.

FAIL:

1. Debug scan generates summaries.
2. Browser reads local files directly instead of going through BFF.
3. Raw file content is leaked into DOM.

BLOCKED:

1. Folder input node cannot be selected.
2. Local folder permission cannot be granted in the fixture environment.

Required screenshots:

```text
08-folder-input-inspector.png
09-folder-read-authorized.png
10-debug-scan-result.png
```

## Case 4: Publish and Run

Steps:

1. Click Publish Version.
2. Confirm publish.
3. Click Run Workflow.

PASS:

1. A new WorkflowInstance is created.
2. Pipeline Board displays 9 nodes.
3. Node states change over time.
4. Run action is user-confirmed and not performed by Agent.

PARTIAL:

1. Workflow runs with fewer visible nodes, but the missing nodes are explained by collapsed grouping.
2. Runtime events still prove the 9 expected logical steps.

FAIL:

1. Publish or run is triggered by Agent without user confirmation.
2. WorkflowInstance is not created.
3. Board remains static with no state transitions.

BLOCKED:

1. Publish is unavailable.
2. Run button is unavailable.
3. Runtime fixture cannot start a workflow instance.

Required screenshots:

```text
11-publish-confirmation.png
12-run-workflow-started.png
13-pipeline-board-9-nodes.png
14-node-state-transition.png
```

Expected logical nodes:

```text
folder_input
folder_scan
markdown_filter
markdown_parse
folder_group
per_folder_summary
overview_summary
quality_check
artifact_publish
```

## Case 5: Per-Folder Summaries

Steps:

1. Wait until the workflow completes or enters quality check.
2. Open Artifacts panel.
3. Open every generated summary artifact.

PASS:

The Artifacts panel contains:

```text
AgentOS_总结.md
前端低代码_总结.md
项目复盘_总结.md
总览总结.md
quality_report.json
```

Every summary Markdown file contains:

```text
内容概览
核心主题
关键知识点
重要文件列表
引用文件
```

PARTIAL:

1. All expected artifacts exist, but one summary misses a non-critical section.
2. Overview summary exists but has weak structure.

FAIL:

1. Any required child folder summary is missing.
2. Summary content is unrelated to input Markdown files.
3. Raw unsupported file content is included.

BLOCKED:

1. Workflow never reaches artifact generation.
2. Artifact panel cannot be opened.

Required screenshots:

```text
15-artifacts-list.png
16-agentos-summary.png
17-lowcode-summary.png
18-retrospective-summary.png
19-overview-summary.png
20-quality-report-artifact.png
```

## Case 6: Quality Check

Steps:

1. Open Quality Panel.
2. Review coverage and warnings.

PASS:

1. Quality Panel displays summary coverage.
2. Unsupported file `未支持/test.pdf` is recorded.
3. Empty folder `空文件夹/` is recorded.
4. If any child folder summary is missing, status is not `passed`.

PARTIAL:

1. Coverage is visible, but detailed missing-folder diagnostics are incomplete.

FAIL:

1. Missing summaries still produce `passed`.
2. Unsupported file is ignored silently.
3. Empty folder is ignored silently.

BLOCKED:

1. Quality Panel cannot be opened.
2. Quality result DTO is unavailable.

Required screenshots:

```text
21-quality-panel-coverage.png
22-quality-panel-unsupported-file.png
23-quality-panel-empty-folder.png
```

## Case 7: Long-Running Recovery

Steps:

1. Refresh the browser while the workflow is running.
2. Re-select the same WorkflowInstance.
3. Inspect board and artifact state.

PASS:

1. Running state is restored from BFF truth.
2. Completed nodes remain completed.
3. Generated artifacts remain visible.
4. UI does not use event payload as truth.

PARTIAL:

1. State restores after manual instance re-selection.
2. Artifacts appear only after a manual refresh.

FAIL:

1. Refresh loses the running instance.
2. Completed nodes reset without rerun.
3. Event payload mutates board truth directly.

BLOCKED:

1. Long-running fixture cannot be held in running state.

Required screenshots:

```text
24-running-before-refresh.png
25-after-refresh-same-instance.png
26-restored-artifacts.png
```

## Case 8: Failure Rerun

Steps:

1. Use a corrupted Markdown file or enable a simulated parse failure.
2. Wait for the parse node to fail.
3. Click rerun current node.
4. Confirm rerun.

PASS:

1. Failed node displays `error`.
2. Rerun requires explicit user confirmation.
3. A new StationRun attempt is created.
4. Old attempt and old error remain visible.

PARTIAL:

1. Rerun works, but old attempt is visible only in evidence or trace panel.

FAIL:

1. Rerun starts without user confirmation.
2. Old error is overwritten.
3. Agent triggers rerun directly.

BLOCKED:

1. Failure fixture cannot be enabled.
2. Rerun UI is not available.

Required screenshots:

```text
27-parse-node-error.png
28-rerun-confirmation.png
29-new-stationrun-attempt.png
30-old-error-preserved.png
```

## Case 9: Agent Debugging

Steps:

1. Ask Agent: `为什么这个文件夹没有生成总结？`
2. Verify read-only explanation.
3. Ask Agent: `帮我修复，让空文件夹也生成一份无内容总结。`
4. Verify Patch Proposal.
5. Apply only after user confirmation.

PASS:

1. The first Agent response is read-only.
2. The second Agent response creates a Patch Proposal.
3. Agent does not auto apply.
4. User confirmation is required before the fix is applied.

PARTIAL:

1. Agent produces a correct patch proposal but explanation is too generic.

FAIL:

1. Agent directly changes workflow state.
2. Agent applies patch automatically.
3. Explanation exposes raw file content or secrets.

BLOCKED:

1. Agent assistant is unavailable during or after the run.

Required screenshots:

```text
31-agent-readonly-debug-explanation.png
32-agent-empty-folder-fix-proposal.png
33-fix-patch-before-apply.png
34-fix-applied-after-user-confirmation.png
```

## Case 10: Governance Evidence

Steps:

1. Open Governance Evidence panel.
2. Inspect proposal, handoff, user confirmation, and runtime result records.

PASS:

1. Evidence chain includes `proposal -> handoff -> user_confirmed -> runtime result`.
2. Evidence includes `operation_type`.
3. Evidence includes `runtime_result_ref`.
4. Evidence includes `risk_flags`.
5. Evidence includes `policy_decision`.
6. Panel is read-only.
7. Panel does not show Apply, Publish, Approve, Reject, Execute, or Run controls.

PARTIAL:

1. Evidence chain is present but one optional reference is only available in network evidence.

FAIL:

1. Evidence chain is missing.
2. Governance panel exposes executable controls.
3. Agent action lacks user confirmation evidence.

BLOCKED:

1. Governance Evidence panel cannot be opened.

Required screenshots:

```text
35-governance-evidence-chain.png
36-governance-evidence-detail.png
37-governance-readonly-panel.png
```

## Global Assertions

Every case must enforce these assertions:

1. Browser network does not contain `/v1/rpc`.
2. Browser network does not contain `/v1/events/subscribe`.
3. DOM and `page.content()` do not contain:

```text
capability_token
subscription_token
Authorization
Bearer
secret
raw_trace_payload
raw_artifact_content
raw_connector_payload
raw prompt
upstream signed URL
```

4. UI does not contain:

```text
自动应用
自动发布
Agent 已执行
Agent 已发布
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
```

## Automation Result Summary Format

The automation runner must write `result-summary.md` with this structure:

```text
# V4.1 Desktop Folder Recursive Summary Acceptance Result

Date:
Browser:
BFF URL:
Console URL:
Fixture Source:

Case Results:
- Case 1:
- Case 2:
- Case 3:
- Case 4:
- Case 5:
- Case 6:
- Case 7:
- Case 8:
- Case 9:
- Case 10:

Totals:
- PASS:
- PARTIAL:
- FAIL:
- BLOCKED:

Global Assertions:
- no /v1/rpc:
- no /v1/events/subscribe:
- DOM redaction:
- UI false-green copy:

Current Project Completion:
- Not supported | Prototype only | Partial MVP | MVP acceptance ready

Blocking Issues:

Recommended Next Fixes:
```

## Completion Level Rules

Use these rules for the final completion assessment:

```text
Not supported
```

Use when Case 1 or Case 2 is BLOCKED or FAIL.

```text
Prototype only
```

Use when Agent can generate a proposal, but publish/run or folder scanning is missing.

```text
Partial MVP
```

Use when publish/run and folder scanning work, but per-folder artifacts, rerun, recovery, or governance evidence is incomplete.

```text
MVP acceptance ready
```

Use only when all 10 cases are PASS and all global assertions pass.

## No False Green

Passing this V4.1 acceptance proves only the dev/local `Desktop/技术分享` recursive Markdown summary workflow scenario.

It does not prove:

1. complete Workflow Studio ready.
2. complete AgentTalkWindow ready.
3. Agent executor ready.
4. controlled executor ready.
5. production-ready external app support.
6. autonomous workflow editing ready.
7. enterprise auth ready.
8. multi-tenant control plane ready.
