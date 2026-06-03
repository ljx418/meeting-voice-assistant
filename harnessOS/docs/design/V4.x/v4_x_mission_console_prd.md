# V4.x Mission Console PRD

文档状态：V4-U4 Mission Console 体验合同。

## 1. 定位

Mission Console 是 V4.x 的主体验入口。它可以落地为 TUI、Command Palette 或 Thin Web Console 中的命令面板。

它不等于 Agent executor，也不直接执行 mutation。

## 2. 主命令

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

## 3. Canonical Transcript

```text
User: 帮我创建一个工作流，递归总结 Desktop/技术分享 下的 Markdown 文件。
Mission Console: 已捕获目标，状态 IntentCaptured。
Mission Console: 已生成 WorkflowSpec，状态 SpecDrafted。
Mission Console: Schema 验证通过，状态 SchemaValidated。
Mission Console: Diff 已生成，状态 DiffReady。应用草稿需要用户确认。
User: /confirm apply
Mission Console: user_confirmed=true，source=mission_console，已 handoff 到 governed BFF。
Mission Console: 已生成 Workflow Blueprint，可查看 workflow.drawio。
User: /publish
Mission Console: 发布版本需要用户确认。
User: /run
Mission Console: 运行工作流需要用户确认。
Mission Console: Runtime Report 已生成，可查看 workflow_board.html、artifacts.html、quality.html、evidence.html。
User: /show evidence
Mission Console: Evidence Chain 只读展示 proposal、handoff、user_confirmed、runtime_result 和 policy_decision。
```

## 4. Agent Boundary

Agent 可以：

```text
propose
explain
handoff
navigate
```

Agent 不能：

```text
auto apply
auto publish
auto run
auto rerun
approval.respond
context.update
business.event.emit
```

## 5. 验收

1. transcript 中每个 durable mutation 都必须显示用户确认。
2. transcript 中 `source=agent` 不得执行 mutation。
3. Mission Console 必须引用 Experience State Machine 的状态。
4. Mission Console 输出必须能链接到 Blueprint、Runtime Report 和 Evidence Chain。

