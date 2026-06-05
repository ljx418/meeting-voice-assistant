# V8 Agent Explainability TUI Contract

文档状态：V8-0 P0 UI contract / V8-8 entry input。

## 1. Purpose

V8 TUI must let the user inspect:

```text
which Agent is on each station
what the Agent can do
what the Agent cannot do
what context the Agent received
what model / skill / MCP / tool was used
what artifact the Agent produced
what evidence supports the result
```

## 2. Required TUI Panels

```text
Workflow Agent Map
Station Agent Detail
Agent Capability Panel
Agent Context Panel
Agent Memory Panel
Agent Invocation Panel
Agent Evidence Links
Forbidden Action Reason Panel
Terminal Worker Handoff Panel
WorkflowExplainerAgent Summary Panel
```

## 3. Read-Only Boundaries

```text
TUI is workflow head and read model.
TUI does not construct runtime truth.
TUI does not execute durable mutation before user confirmation.
TUI cannot let source=agent directly mutate runtime.
Evidence and Runtime Report panels are read-only.
```

## 4. Minimum Screen Layout

```text
Left: workflow station list and Agent identity.
Center: current station Agent detail, status, context and output.
Right: capability decisions, forbidden reasons, evidence links.
Bottom: state timeline, terminal transcript or handoff status if relevant.
```

## 5. Acceptance Tests

```text
tui_shows_agent_for_each_station
tui_shows_workflow_explainer_agent
tui_shows_agent_role_goal_model
tui_shows_skill_mcp_tool_policy
tui_shows_forbidden_action_reason
tui_links_runtime_report_evidence_blueprint
tui_no_hidden_mutation_form
tui_no_auto_apply_auto_run_copy
tui_does_not_construct_runtime_truth
```

