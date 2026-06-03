# V4.x WorkflowSpec Registry

文档状态：V4-U5A/U6 审计输入。本文定义 WorkflowSpec Registry read model，不替代 runtime truth。

## Purpose

WorkflowSpec Registry 用于记录 WorkflowSpec 的来源、hash、schema version 和可选 runtime refs，帮助 Mission Console、Workflow Blueprint、HTML Report、TUI 和 Thin Web Console 引用同一份 spec。

## Required Fields

```text
spec_id
spec_hash
schema_version
source
created_by
validated_at
linked_workflow_draft_id
linked_workflow_version_id
linked_workflow_instance_id
runtime_truth_boundary
```

## Runtime Truth Boundary

```text
WorkflowSpec Registry 不能替代 WorkflowDraft / WorkflowVersion。
WorkflowSpec Registry 不能直接写 WorkflowDraft / WorkflowVersion / WorkflowInstance / StationRun。
Drawio 不能构造 runtime truth。
HTML Report 不能构造 runtime truth。
EventBridge payload 不能构造 runtime truth。
Report Schema 是 read model。
Interaction Orchestrator 不直接写 runtime。
Experience State Machine 是 UX read model。
```

## Allowed Use

```text
Mission Console 可以创建 WorkflowSpec draft。
Workflow Blueprint 可以读取 WorkflowSpec 生成 Drawio。
HTML Report 可以引用 WorkflowSpec 和 runtime DTO 生成只读报告。
Evidence Chain 可以引用 spec_id 和 spec_hash 做审计。
V4-U5E 可以把真实 LLM 本地技术文档工作流结果链接到 linked_workflow_instance_id，但该链接仍是 read model 引用。
```

## Forbidden Use

```text
不得从 Drawio 反向写 WorkflowDraft。
不得从 HTML Report hidden form 写 runtime。
不得从 EventBridge payload 构造 workflow / station / patch / evidence truth。
不得让 source=agent 通过 spec registry 执行 apply / publish / run / rerun / approval.respond / context.update。
```
