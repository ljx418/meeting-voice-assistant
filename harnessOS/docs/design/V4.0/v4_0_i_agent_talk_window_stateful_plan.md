# V4.0-I AgentTalkWindow Stateful Assistant Plan

文档状态：V4.0-I implementation baseline。

## Positioning

V4.0-I upgrades the V4.0-C AgentTalk preparation shell into a governed, stateful Agent assistant baseline for dev/local Workflow Console.

It is not a full AgentTalkWindow and not an autonomous workflow editor.

## Preconditions

V4.0-I can only start after:

```text
V4.0-G complete: governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console.
V4.0-H complete: canvas-to-runtime patch bridge ready for dev/local Workflow Console.
```

Both prerequisites are complete.

## Scope

Agent state is a V4.0 BFF/UI layer concern:

- `AgentTalkSession`
- `AgentMessage`
- `AgentSuggestion`
- `AgentActionIntent`

These objects do not enter the V3.6 Workflow Runtime Contract and do not write:

- `WorkflowTemplate`
- `WorkflowDraft`
- `WorkflowVersion`
- `StationRun`

If persisted, Agent state must include:

- scope
- workflow_instance_id
- workflow_template_id
- created_by
- redaction_status

## Allowed Action Intents

```text
explain_workflow
summarize_events
suggest_patch
show_patch_diff
show_approval_notice
show_context_summary
navigate_to_editing_panel
```

## Forbidden Action Intents

```text
apply_patch
reject_patch
publish_version
respond_approval
update_context
emit_business_event
start_workflow
rerun_station
```

## Runtime Boundary

V4.0-I does not call:

- external LLM
- external MCP
- connector executor
- workflow runtime store directly

Assistant responses are deterministic / rule-based / fixture-backed.

## BFF Routes

```text
GET  /bff/instances/{instance_id}/agent/session
POST /bff/instances/{instance_id}/agent/messages
GET  /bff/instances/{instance_id}/agent/suggestions
POST /bff/instances/{instance_id}/agent/suggestions/{suggestion_id}/dismiss
```

Capability profile:

```text
agent_talk.read
agent_talk.write
agent_suggestions.read
agent_suggestions.write
```

Agent read paths may also consume existing read DTOs:

```text
workflows.read
board.read
stations.read
artifacts.read
quality.read
approvals.read
workflow_context.read
workflow_patches.read
events
```

Agent routes do not require or hold:

```text
workflow_patches.write
workflow_versions.publish
approvals
workflow_context.write
business_events.write
workflows.execute
```

## Patch Governance

`source=agent` may propose a patch.

`source=agent` cannot:

- apply patch
- reject patch
- publish version

High-risk patch suggestions preserve `risk_flags` and `requires_approval`.

The user must enter the Editing Panel and use:

```text
user_confirmed=true
source=editing_panel
```

to apply or publish.

## Event Refresh

Agent timeline may display live events. Events only trigger refresh.

The assistant must reload board/status/context/patch DTO and must not use event payload as truth.

## Tests

```text
tests/test_v4_0_agent_talk_stateful_bff.py
tests/test_v4_0_agent_talk_stateful_scope.py
tests/test_v4_0_agent_talk_stateful_redaction.py
tests/test_v4_0_agent_talk_patch_governance.py
apps/workflow-console/src/__tests__/agentTalkStateful.test.tsx
apps/workflow-console/e2e/workflow-agent-talk-smoke.spec.ts
```

## Allowed Claim

```text
V4.0-I complete: governed stateful Agent assistant baseline ready for dev/local Workflow Console.
```

## Forbidden Claims

```text
complete AgentTalkWindow ready
complete Workflow Studio ready
production-ready external app support
autonomous workflow editing ready
enterprise auth/OAuth/SSO ready
```
